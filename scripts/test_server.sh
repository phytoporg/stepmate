#!/bin/bash

cd "$(dirname "$0")/../server"
uwsgi --socket :8000 --protocol=http --http-websockets -w main:app
cd -
