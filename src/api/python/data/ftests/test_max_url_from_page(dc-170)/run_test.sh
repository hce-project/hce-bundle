#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_max_url_from_page\(dc-170\)
HCE_BIN=~/hce-node-bundle/api/php/bin


#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN

NEW_SITE_FILES=$TEST_DIR/site_new*.json
for f in $NEW_SITE_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f
done

sleep 5

UPDATE_SITE_FILES=$TEST_DIR/site_update*.json
for f in $UPDATE_SITE_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE --file=$f
done

sleep 5

NEW_URL_FILES=$TEST_DIR/url_new*.json
for f in $NEW_URL_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=$f
done

sleep 5

UPDATE_URL_FILES=$TEST_DIR/url_update*.json
for f in $UPDATE_URL_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_UPDATE --file=$f
done
