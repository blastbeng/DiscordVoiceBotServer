#!/usr/bin/env bash
mkdir -p /app/config/backups/
cp /app/config/*db.sqlite3 /app/config/backups/
uwsgi --ini uwsgi.ini --enable-threads
