#!/bin/bash

SLEEP=5

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_html_redirect
HCE_BIN=~/hce-node-bundle/api/php/bin


# start cluster
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

sleep $SLEEP

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN

NEW_SITE_FILES=$TEST_DIR/site_new*.json
for f in $NEW_SITE_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f 2>&1 
done

sleep $SLEEP

NEW_URL_FILES=$TEST_DIR/url_new*.json
for f in $NEW_URL_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=$f 2>&1 
done

sleep $SLEEP

URL_STATUS_FILES=$TEST_DIR/url_status*.json
for f in $URL_STATUS_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_STATUS --file=$f 2>&1
done


