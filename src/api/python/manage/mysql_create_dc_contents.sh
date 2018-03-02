#!/bin/bash
set -e

source mysql_create_cfg

echo "Creating dc_contents database..."

mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_contents.sql

echo "dc_contents databases successfully created"
