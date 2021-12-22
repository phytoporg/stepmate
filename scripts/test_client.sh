#!/usr/bin/bash

cd "$(dirname "$0")"
python client.py --songs-file ../data/sample_songs.json --server-host localhost --server-port 8000
cd -
