#!/bin/bash

#Remove log files
rm ../log/*

echo "Remove all SQL databases"
mysql -u hce -phce12345 -e "drop database if exists dc_urls"
mysql -u hce -phce12345 -e "drop database if exists dc_sites"
mysql -u hce -phce12345 -e "drop database if exists dc_urls_deleted"
mysql -u hce -phce12345 -e "drop database if exists dc_contents"
mysql -u hce -phce12345 -e "drop database if exists dc_co"
mysql -u hce -phce12345 -e "drop database if exists dc_processor"
mysql -u hce -phce12345 -e "drop database if exists dc_stat_freqs"
mysql -u hce -phce12345 -e "drop database if exists dc_stat_logs"
mysql -u hce -phce12345 -e "drop database if exists dc_statistic"
mysql -u hce -phce12345 -e "drop database if exists dc_api_statistics"
mysql -u hce -phce12345 -e "drop database if exists dc_stat_sites"

echo "Remove all DC files from raw data and key-value db directories"
rm -rf ../data/dc_dbdata/*.db
rm -rf ../data/dc_rdata/*

echo "Remove all DTM files from raw data and key-value db directories"
rm -rf ../data/dtm_dbdata/*.db
