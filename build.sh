#!/bin/bash
set -e

APP="note-service"
VERSION="dev"

rm -f app/*.pyc
docker build -t sybex/$APP:$VERSION .
bash -c "docker stop $APP; exit 0"
docker run --rm -p 5000:5000 -e TELEGRAM_TOKEN=$TELEGRAM_TOKEN -e WEATHER_TOKEN=$WEATHER_TOKEN --name $APP sybex/$APP:$VERSION
