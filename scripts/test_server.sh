#!/bin/bash

cd "$(dirname "$0")"
uwsgi --socket 0.0.0.0:8000 --protocol=http -w main:app
cd -
