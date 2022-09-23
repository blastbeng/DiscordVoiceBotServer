#!/bin/sh
curl -X POST http://192.168.1.160:5000/utils/upload/trainfile/txt/en -H "Content-Type: application/json" -d -F "trainfile=@$1"