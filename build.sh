#!/bin/bash
set -e

APP="note-service"
VERSION="0.12"

rm -f app/*.pyc
docker build -t sybex/$APP:$VERSION .
bash -c "docker stop $APP; exit 0"
#docker push sybex/$APP:$VERSION
docker run --rm -p 5000:5000 -e TELEGRAM_TOKEN=$TOKEN --name $APP sybex/$APP:$VERSION
