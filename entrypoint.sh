#!/usr/bin/env bash
mkdir -p /app/config/backups/
cp /app/config/*db.sqlite3 /app/config/backups/
uwsgi --ini uwsgi.ini --enable-threads --socket /tmp/scemo-pezzente-api/scemo-pezzente-1.sock
