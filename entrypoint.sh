#!/usr/bin/env bash
cp /app/config/db.sqlite3 /app/config/db.sqlite3.bak
cp /app/config/sentences.txt /app/config/sentences.txt.bak
uwsgi --ini uwsgi.ini --enable-threads
