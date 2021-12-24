import asyncio
import audioread
import json
import os
import struct
import websockets
import numpy as np

MUSIC_LIBRARY='/tmp/songs'

def pcm2float(signal_buffer):
    # Audio Web API expects 32-bit floating precision normalized to [-1, 1]
    signal = np.frombuffer(signal_buffer, dtype=np.int16)

    i = np.iinfo(signal.dtype) # Should be signed 16-bit ints from audioread
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max

    return (signal.astype('float32') - offset) / abs_max

async def _send_song(websocket, song_name):
    songs_in_library = os.listdir(MUSIC_LIBRARY)

    # The "song name" is just the song with no file extension
    matching_songs = [s for s in songs_in_library if s.lower().startswith(song_name.lower())]
    if len(matching_songs) == 0:
        print(f'No matching song for "{song_name}"')
        return
    elif len(matching_songs) > 1:
        print(f'Warning: Multiple matching songs for "{song_name}"')

    match_path = os.path.join(MUSIC_LIBRARY, matching_songs[0])
    print(f'Reading {match_path}...')
    with audioread.audio_open(match_path) as fr:
        frequency = fr.samplerate
        duration_ms, duration = int(fr.duration * 1000), fr.duration
        channel_count = fr.channels

        # Kinda arbitrary? Just wanted some distinct identifiers.
        MSG_ID_HEADER = 0x1000FA01
        MSG_ID_CHUNK  = 0x1000FA02

        # Not string-encoding this. Too much data, so pack dat sheeeit. 

        # In native byte-order:
        # - Message ID (unsigned int) - I
        # - frequency (unsigned int) - I
        # - channel_count (unsigned char) - I
        # - duration_ms (milliseconds - unsigned int) - I
        bin_header = struct.pack('@IIIf', MSG_ID_HEADER, frequency, channel_count, duration_ms)
        print('sending header')
        await websocket.send(bin_header)
        print('sent!')

        for chunk in fr.read_data():
            buffer = bytearray(pcm2float(chunk))

            # In native byte-order:
            # - Message ID (unsigned int) - I
            # - chunk_size (unsigned int) - I
            # - chunk_data - (char[]) - p
            bin_msg = struct.pack('@II', MSG_ID_CHUNK, len(buffer)) + buffer
            print(f'sending message of size {len(bin_msg)}')
            await websocket.send(bin_msg)
            print('sent!')
    
async def process_message(websocket):
    async for message in websocket:
        print(message)
        try:
            message_dict = json.loads(message)
        except:
            continue

        if type(message_dict) is not dict:
            continue

        if message_dict['cmd'] == 'send_song':
            await _send_song(websocket, message_dict['song_name'])

async def main():
    async with websockets.serve(process_message, "localhost", 5001):
        await asyncio.Future()  # run forever

asyncio.run(main())
