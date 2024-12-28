#!/bin/sh
set -e

# Read the VERSION file and store its content in a variable
VERSION=$(head -n 1 /app/VERSION)

# Display the version information when the container starts
echo "safe-proxy-docker version $VERSION"

# secret を作成（初回起動時のみ）
python /usr/local/bin/encrypt_key.py DUMMY > /dev/null

# config.yaml をDBに設定
python /usr/local/bin/db_setup.py

# Nginxを起動
exec nginx -g "daemon off;"
