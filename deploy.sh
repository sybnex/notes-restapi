#!/bin/bash

if [ -n "$TELEGRAM_TOKEN" ]; then
  kubectl -n tools delete secret telegram-secret
  kubectl -n tools create secret generic telegram-secret --from-literal=token=$TELEGRAM_TOKEN
fi

if [ -n "$WEATHER_TOKEN" ]; then
  kubectl -n tools create secret generic weather-secret --from-literal=token=$WEATHER_TOKEN
fi

kubectl create ns tools
kubectl apply -f deployment.yaml
