#!/bin/bash
set -e

source mysql_create_cfg

echo "Creating main databases..."

mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_sites.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_urls.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_sites_default.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_sites_mutexes_api.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_processor.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_contents.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dc_stat_domains.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ../ini/dtm.sql


#Creating kv storage for default site...
cp ../ini/db-task_keyvalue_template.db ../data/dc_dbdata/0.db

echo "Main databases successfully created"
