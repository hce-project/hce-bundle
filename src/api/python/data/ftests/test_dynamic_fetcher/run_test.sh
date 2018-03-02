#!/bin/bash

SLEEP=2
WAIT_CONTENT=120
EXIT_CODE=1

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_dynamic_fetcher
HCE_BIN=~/hce-node-bundle/api/php/bin

## check necessary cle
if [ "$1" == "cleanup" ]
then
	# stop cluster
	cd $MANAGE
	./dc-daemon_stop.sh --force
	./dtm-daemon_stop.sh --force

	sleep $SLEEP

	#../ftests/dc_tests_cleanup.sh
	#cd $MANAGE && ./mysql_create_db.sh

	sleep $SLEEP

	# start cluster
	cd $MANAGE
	./dtm-daemon_start.sh 
	./dc-daemon_start.sh

	sleep $SLEEP
fi

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
RAW_CONTENTS_FILE="$TMP_DIR/rawContents.json"

CONTENT_URL_FILES=$TEST_DIR/url_content*.json
for f in $CONTENT_URL_FILES
do
  echo $f >> ../log/$0.log 2>&1
	./dc-client.py --config=../ini/dc-client.ini --command=URL_CONTENT --file=$f > "$TMP_CONTENT_FILE" 2>&1
	cat "$TMP_CONTENT_FILE" >> ../log/$0.log 2>&1


	$BIN/json-field.py -f "itemsList:0:itemObject:0:rawContents:0:buffer" -b 1 < "$TMP_CONTENT_FILE" > "$RAW_CONTENTS_FILE"
	RAW_CONTENTS=`cat "$RAW_CONTENTS_FILE"`

	if [ -n "$RAW_CONTENTS" ]
	then
		echo "Raw content was got successfully"
		EXIT_CODE=0
	fi
done

rm -f $PROCESSED_CONTENTS_FILE
rm -f $RAW_CONTENTS_FILE
rm -f $TMP_CONTENT_FILE

sleep $SLEEP

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

