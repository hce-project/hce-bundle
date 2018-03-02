#!/bin/bash

echo "Creating all databases..."

./mysql_create_struct.sh
./mysql_create_dc_contents.sh
./mysql_create_statistic.sh
./mysql_create_urls_deleted.sh

echo "Databases creation finished."
