#!/bin/sh
set -e

# secret を作成（初回起動時のみ）
python /usr/local/bin/encrypt_key.py DUMMY > /dev/null

# config.yaml をDBに設定
python /usr/local/bin/db_setup.py

# Nginxを起動
exec nginx -g "daemon off;"
