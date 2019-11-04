#!/bin/bash
set -e

APP="note-service"
VERSION="0.1.0"

rm -f app/*.pyc
docker build -t $APP .
bash -c "docker stop $APP; exit 0"
docker run --rm -p 5000:5000 --name $APP $APP
