import requests
import argparse
import os
import json

def _enumerate_remote_songs(host, port):
    uri = f'http://{host}:{port}/api/songs/list'
    r = requests.get(uri)
    if r.status_code != 200:
        print('GET Request failed with code {r.status_code}')
        exit(-1)

    return r.json()['songs']

def _get_song_from_songdir(songdir):
    group_name = os.path.basename(os.path.dirname(songdir))
    song_name = os.path.basename(songdir)
    sm_file = os.path.join(songdir, f'{song_name}.sm')
    assert os.path.exists(sm_file)

    artist = "Unknown"
    with open(sm_file, 'r', encoding="ISO-8859-1") as fr:
        for line in fr.readlines():
            if line.startswith("#ARTIST"):
                idx = line.find(':')
                if idx > 0 and idx < len(line) - 1:
					# Artist names have trailing semicolons
                    artist = line.strip()[idx + 1:][:-1]

                # TODO: Get more data
                break

    return {
        'title' : song_name,
        'group' : group_name,
        'artist': artist
    }

def _enumerate_local_songs(stepmania_songs_dir):
    groups = [d for d in os.listdir(stepmania_songs_dir) \
            if os.path.isdir(os.path.join(stepmania_songs_dir, d))]

    local_songdirs = []
    for g in groups:
        group_dir = os.path.join(stepmania_songs_dir, g)
        group_song_dirs = [d for d in os.listdir(group_dir) \
                if os.path.isdir(os.path.join(group_dir, d)) and \
                   os.path.exists(os.path.join(group_dir, d, f'{d}.sm'))]

        for songdir in group_song_dirs:
            abs_songdir = os.path.join(stepmania_songs_dir, group_dir, songdir)
            local_songdirs.append(_get_song_from_songdir(abs_songdir))

    return local_songdirs

def _server_add_songs(host, port, songs_to_send):
    headers = { 'Content-Type' : 'application/json' }
    uri = f'http://{host}:{port}/api/songs/add'

    for song in songs_to_send:
        r_post = requests.post(uri, json=song, headers=headers)
        title = song['title']
        if r_post.status_code != 200:
            print(f'Failed to send song: {title}')
            print(f'Status code: {r_post.status_code}')
        else:
            print(f'Sent {title}')

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

    # TODO: Only send what's missing on the server. Issue is, tough to check for duplicates right
    # now without further insights into what's actually in a song. Need stepmania file parsing
    # support.
    # remote_songs = _enumerate_remote_songs(args.server_host, args.server_port)

    songs_to_send = local_songs
    if args.dump_songs:
        print(json.dumps(songs_to_send))
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

    main(parser.parse_args())
