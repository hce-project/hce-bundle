#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_find_site
HCE_BIN=~/hce-node-bundle/api/php/bin


# start cluster
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

sleep 5

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN

echo "TEST FIND TEST" > ../log/$0.log 2>&1

NEW_SITE_FILES=$TEST_DIR/site_new*.json

for f in $NEW_SITE_FILES
do
	echo "New site: $f"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f >> ../log/$0.log 2>&1
done

FIND_SITE_FILES=$TEST_DIR/site_find*.json

for f in $FIND_SITE_FILES
do
	echo "Find site: $f"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=$f >> ../log/$0.log 2>&1
done

STATUS_SITE_FILES=$TEST_DIR/site_status*.json

for f in $STATUS_SITE_FILES
do
	echo "Status site: $f"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file=$f >> ../log/$0.log 2>&1
done

DELETE_SITE_FILES=$TEST_DIR/site_delete*.json
for f in $DELETE_SITE_FILES
do
	echo "Delete site: $f"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$f >> ../log/$0.log 2>&1
done
