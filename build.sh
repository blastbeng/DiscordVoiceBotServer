#!/bin/sh
docker build . -f ./Dockerfile.api  -t scemo-pezzente-api:latest
docker build . -f ./Dockerfile.balancer  -t scemo-pezzente-api-balancer:latest
