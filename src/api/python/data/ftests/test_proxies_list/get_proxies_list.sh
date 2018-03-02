#!/bin/bash

## Script only for dc2

BIN=~/hce-node-bundle/api/python/bin
TEST_DIR=`pwd`


cd $BIN

CONTENT_URL_FILES=$TEST_DIR/proxies_list_url_content*.json
for f in $CONTENT_URL_FILES
do
	./dc-client.py --config=../ini/dc-client.ini --command="URL_CONTENT" --file="$f" > "$f.result" 2>&1
done
