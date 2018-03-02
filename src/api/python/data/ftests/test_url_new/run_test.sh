#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEMPLATES=~/hce-node-bundle/api/python/data/ftests/templates
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_icremental_crawling
HCE_BIN=~/hce-node-bundle/api/php/bin


#add site
cd $BIN
./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_url_new/site_new.json
sleep 5
./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=../data/ftests/test_url_new/url_new.json
