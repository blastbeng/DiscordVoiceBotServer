#!/usr/bin/env bash
/usr/sbin/nginx -t -q -g 'daemon on; master_process on;'
/usr/sbin/nginx -g 'daemon on; master_process on;'
