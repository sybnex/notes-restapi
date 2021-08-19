#!/bin/bash

APP="note-service"
VERSION="dev"

rm -f app/*.pyc
docker build -t sybex/$APP:$VERSION .
bash -c "docker stop $APP; exit 0"
docker run -d -p 5000:5000 -e TELEGRAM_TOKEN=$TELEGRAM_TOKEN -e WEATHER_TOKEN=$WEATHER_TOKEN --name $APP sybex/$APP:$VERSION

sleep 5
echo "INFO: start testing ..."
curl -X POST "http://localhost:5000/test?data=ok" -H "accept: application/json"
sleep 1
curl -X GET  "http://localhost:5000/test" -H "accept: application/json"
echo "INFO: end testing."

docker logs $APP
docker stop $APP
docker rm $APP

docker tag sybex/$APP:dev sybex/$APP
docker push sybex/$APP
