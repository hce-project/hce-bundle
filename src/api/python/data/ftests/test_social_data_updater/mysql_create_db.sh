#!/bin/bash

set -e

source ./mysql_create_cfg

echo "Creating all databases..."

mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ./create.sql

echo "Databases creation finished."
echo "Creating test tables ..."

mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ./timeline_graph_data_24h.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ./titles_cache.sql
mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS < ./social_data_cache.sql

echo "Test tables successfully created"
