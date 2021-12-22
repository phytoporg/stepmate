#!/usr/bin/bash

# Keepin' arguments simple for now
SONGS_DIR="$1"
if [ -z "$SONGS_DIR" ]; then
    echo "Please supply a songs directory argument."
    exit -1
fi

SERVER_HOST="$2"
if [ -z "$SERVER_HOST" ]; then
    echo "No server host provided, defaulting to localhost"
    SERVER_HOST="localhost"
fi

SERVER_PORT="$3"
if [ -z "$SERVER_PORT" ]; then
    echo "No server port provided, defaulting to 8000"
    SERVER_PORT=8000
fi

cd "$(dirname "$0")/../client"
python client.py --songs-dir "$SONGS_DIR" --server-host "$SERVER_HOST" --server-port "$SERVER_PORT"
cd -
