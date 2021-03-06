import requests
import argparse
import os
import json
import gzip
import base64

def _enumerate_remote_songs(host, port):
    uri = f'http://{host}:{port}/api/songs/list'
    r = requests.get(uri)
    if r.status_code != 200:
        print('GET Request failed with code {r.status_code}')
        exit(-1)

    return r.json()['songs']

def _find_sm_file(songdir):
    candidates = [f for f in os.listdir(songdir) if f.endswith('.sm') or f.endswith('.ssc')]
    if len(candidates) == 0:
        return None

    if len(candidates) > 1:
        # TODO: log levels
        # print(f'Warning: multiple candidate step files in {songdir}')
        pass

    # Just use the first one
    return os.path.join(songdir, candidates[0])

def _get_song_from_songdir(songdir):
    group_name = os.path.basename(os.path.dirname(songdir))
    song_name = os.path.basename(songdir)
    sm_file = _find_sm_file(songdir)
    if not sm_file:
        print(f'Could not get valid step file from {songdir}')
        return None

    artist = "Unknown"
    banner_encoded = None
    with open(sm_file, 'r', encoding="ISO-8859-1") as fr:
        for line in fr.readlines():
            if line[0] != '#':
                continue

            idx = line.find(':')
            if idx > 0 and idx < len(line) - 1:
                # Kill the trailing semicolon
                value = line.strip()[idx + 1:][:-1]

            if line.startswith("#BANNER") and len(value) > 0:
                banner_file = os.path.join(songdir, value)
                if not os.path.isfile(banner_file):
                    continue

                with open(banner_file, 'rb') as fr_banner:
                    banner_encoded = base64.b64encode(fr_banner.read()).decode('utf-8')

            elif line.startswith("#ARTIST") and len(value) > 0:
                artist = value

            if artist and banner_encoded:
                break

    return {
        'title' : song_name,
        'group' : group_name,
        'artist': artist,
        'banner_data' : banner_encoded,
    } if artist else None

def _enumerate_local_songs(stepmania_songs_dir):
    groups = [d for d in os.listdir(stepmania_songs_dir) \
            if os.path.isdir(os.path.join(stepmania_songs_dir, d))]

    local_songdirs = []
    for g in groups:
        group_dir = os.path.join(stepmania_songs_dir, g)
        group_song_dirs = [d for d in os.listdir(group_dir) \
                if os.path.isdir(os.path.join(group_dir, d))]

        for songdir in group_song_dirs:
            abs_songdir = os.path.join(stepmania_songs_dir, group_dir, songdir)
            song = _get_song_from_songdir(abs_songdir)
            if song:
                local_songdirs.append(song)

    return local_songdirs

def _server_add_songs(host, port, songs_to_send):
    headers = { 'Content-Type' : 'application/json' }
    uri = f'http://{host}:{port}/api/songs/add'

    songs_to_send_encoded = json.dumps(songs_to_send).encode('utf-8')
    gz_songs_to_send = gzip.compress(songs_to_send_encoded)
    r_post = requests.post(uri, data=gz_songs_to_send, headers=headers)
    if r_post.status_code != 200:
        print(f'Failed to send songs to server')
        print(f'Status code: {r_post.status_code}')
    else:
        print(f'Sent {len(songs_to_send)} songs to server')

def main(args):
    if args.songs_file and os.path.exists(args.songs_file) and os.path.isfile(args.songs_file):
        with open(args.songs_file, 'r') as fr:
            local_songs = json.loads(fr.read())
    else:
        if not os.path.exists(args.songs_dir):
            print(f'Song directory {args.songs_dir} does not exist')
            exit(-1)

        if not os.path.isdir(args.songs_dir):
            print(f'Not a directory: {args.songs_dir}')
            exit(-1)

        local_songs = _enumerate_local_songs(args.songs_dir)

    # Working around my crappy workflow. TODO: FIX.
    songs_to_send = [s for s in local_songs if len(s['artist']) > 0]
    if args.list_songs:
        # The dump is illegible with the banner data
        for s in songs_to_send:
            s['banner_data'] = 'Emptied'

        print(json.dumps(songs_to_send, indent=4))
        exit(0)
        
    if args.dump_songs:
        MAX_DUMP_SONGS = 100
        songs_to_dump = songs_to_send if len(songs_to_send) < MAX_DUMP_SONGS \
            else songs_to_send[:MAX_DUMP_SONGS]
        print(json.dumps(songs_to_dump))
    else:
        _server_add_songs(args.server_host, args.server_port, songs_to_send)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    # Must choose one of these two options
    parser.add_argument('--songs-dir', type=str)
    parser.add_argument('--songs-file', type=str)

    parser.add_argument('--server-host', type=str, required=True)
    parser.add_argument('--server-port', type=int, required=True)
    parser.add_argument('--dump-songs', action='store_true')
    parser.add_argument('--list-songs', action='store_true')

    main(parser.parse_args())
