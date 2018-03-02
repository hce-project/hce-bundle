#!/bin/bash

#prepare dc for tests
#delete mysql databases and create empty ones
#delete data from filesistems

mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_contents"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_processor"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_sites"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_stat_freqs"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_stat_logs"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_statistic"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_urls"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_urls_deleted"
mysql -h 127.0.0.1 -u $1 -p$2  -e "drop database dc_co"

#cd ../manage && ./mysql_create_struct.sh hce hce12345

#mysql -u $1 -p$2 < ../ini/sites_properties.sql
#mysql -u $1 -p$2 < ../ini/sites_filters_media_url_filters.sql

rm -rf ../data/dc_dbdata/*
rm -rf ../data/dc_rdata/*
rm ../log/*

#find ../ -name "*.pyc" -delete

rm ../data/dtm_dbdata/*

#cd ../ftests && ./dc_tests.sh

#cd ../bin && find . -not -name "*.py" -a -type f -delete

cd ../manage && ./mysql_create_db.sh
