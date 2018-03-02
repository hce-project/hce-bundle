#!/bin/bash

SLEEP=2
EXIT_CODE=1

RED='\e[0;31m'
GREEN='\e[0;32m'
NC='\e[0m' # No Color

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_url_stats_request
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
  echo "Create new site"
  echo $f > ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

UPDATE_SITE_FILES=$TEST_DIR/site_update*.json
for f in $UPDATE_SITE_FILES
do
	echo "Site update"
  echo $f > ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

NEW_URL_FILES=$TEST_DIR/url_new*.json
for f in $NEW_URL_FILES
do
  echo "Create new url"
	echo $f > ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

UPDATE_URL_FILES=$TEST_DIR/url_update*.json
for f in $UPDATE_URL_FILES
do
	echo "Url update"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_UPDATE --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

TMP_DIR="/tmp"
TMP_CONTENT_FILE="$TMP_DIR/content.json.tmp"
STATS_FILE="$TMP_DIR/stats.value.tmp"

STATS_URL_FILES=$TEST_DIR/url_stats*.json
for f in $STATS_URL_FILES
do
	echo "Url stats request"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_STATS --file=$f > "$TMP_CONTENT_FILE" 2>&1
	cat "$TMP_CONTENT_FILE" >> ../log/$0.log 2>&1

	$BIN/json-field.py -f "itemsList:0:itemObject:0:logRows:0:Object" < "$TMP_CONTENT_FILE" > "$STATS_FILE"
	STATS=`cat "$STATS_FILE"`

	if [[ -n $STATS ]]
	then
		echo -ne "${GREEN}Stats is allowed${NC}"
		EXIT_CODE=0
	else
		echo -ne "${RED}Stats is not allowed${NC}"
		EXIT_CODE=1
	fi
	echo ""
done

rm -f $TMP_CONTENT_FILE
rm -f $HISTORY_FILE

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

