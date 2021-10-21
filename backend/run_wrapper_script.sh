#!/bin/bash

# turn on bash's job control
set -m

mkdir -p /var/run/gunicorn
mkdir -p /var/log/gunicorn
mkdir -p /var/log/web

rm -rf /var/run/gunicorn/*
# Start the primary process and put it in the background
flask run --host=0.0.0.0 &
#/usr/local/bin/dotenv -f .web-variables.env run gunicorn -c gun.py --bind 0.0.0.0:8080 server:web &
# now we bring the primary process back into the foreground
# and leave it there
fg %1
