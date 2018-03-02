#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEMPLATES=~/hce-node-bundle/api/python/data/ftests/templates
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_max_redirect
HCE_BIN=~/hce-node-bundle/api/php/bin


#add site
cd $BIN
./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_max_redirect/site_new.json
