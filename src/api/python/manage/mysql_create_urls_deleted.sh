#!/bin/bash
set -e

source mysql_create_cfg

echo "Creating url deleted database..."

mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_urls_deleted.sql

echo "Urls deleted databases successfully created"
