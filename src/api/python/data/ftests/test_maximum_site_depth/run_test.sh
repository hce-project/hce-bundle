#!/bin/bash

SLEEP=2
WAIT_CONTENT=60
EXIT_CODE=1

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_maximum_site_depth
HCE_BIN=~/hce-node-bundle/api/php/bin


#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN

NEW_SITE_FILES=$TEST_DIR/site_new*.json
for f in $NEW_SITE_FILES
do
	echo "Create new site"
  echo $f > ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

NEW_URL_FILES=$TEST_DIR/url_new*.json
for f in $NEW_URL_FILES
do
	echo "Create new url"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

echo "Wait for getting url content:"
a=0
while [ $a -lt $WAIT_CONTENT ]
	do
		sleep 10
		a=$(($a+10))
		echo "time: $a sec."
	done 

TMP_DIR="/tmp"
TMP_CONTENT_FILE="$TMP_DIR/content.json.tmp"

CONTENT_URL_FILES=$TEST_DIR/url_content*.json
for f in $CONTENT_URL_FILES
do
  echo $f >> ../log/$0.log 2>&1
	./dc-client.py --config=../ini/dc-client.ini --command=URL_CONTENT --file=$f > "$TMP_CONTENT_FILE" 2>&1
	cat "$TMP_CONTENT_FILE" >> ../log/$0.log 2>&1
done

sleep $SLEEP

DEPTH_FILE="$TMP_DIR/depth.value.tmp"

URL_STATUS_FILES=$TEST_DIR/url_status*.json
for f in $URL_STATUS_FILES
do
	echo "Get status url"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_STATUS --file=$f > "$TMP_CONTENT_FILE" 2>&1
	cat "$TMP_CONTENT_FILE" >> ../log/$0.log 2>&1
	
	$BIN/json-field.py -f "itemsList:0:itemObject:0:depth" < "$TMP_CONTENT_FILE" > "$DEPTH_FILE"
	DEPTH=`cat "$DEPTH_FILE"`

	if [ $DEPTH -lt 1 ]
	then
		echo "Depth value: $DEPTH is allowed"
		EXIT_CODE=0
	fi
done

rm -f $TMP_CONTENT_FILE
rm -f $DEPTH_FILE

DELETE_URL_FILES=$TEST_DIR/url_delete*.json
for f in $DELETE_URL_FILES
do
	echo "Delete url"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_DELETE --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

DELETE_SITE_FILES=$TEST_DIR/site_delete*.json
for f in $DELETE_SITE_FILES
do
	echo "Delete site"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$f >> ../log/$0.log 2>&1
done

exit $EXIT_CODE

