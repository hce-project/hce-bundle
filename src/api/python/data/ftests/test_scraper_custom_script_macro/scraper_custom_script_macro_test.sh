#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"
#LOG="~/hce-node-bundle/api/python/log/$0.log"

BIN=~/hce-node-bundle/api/python/bin
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_scraper_custom_script_macro
HCE_BIN=~/hce-node-bundle/api/php/bin
TMP_DIR="/tmp"

SLEEP=2
WAIT_CONTENT=120
EXIT_CODE=0


apiToken=$1

if [ "$apiToken" == "" ]
then
	apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
fi

#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api?apiToken=$apiToken"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=$apiToken"


testRestAPI()
{
	echo "Test RestAPI started"
  #Good news scraping static fetcher for test google search 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/scraper_custom_script_macro_test1.json" $HTTP_URL >> $LOG

	TMP_VALUE_FILE="$TMP_DIR/content_value.json.tmp"
	VALUE_FILE="$TMP_DIR/value.json.tmp"

	$BIN/json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < "$RESPONSE_JSON_DIR/$0_1.result.json" > "$TMP_VALUE_FILE"
	#VALUE=`cat "$TMP_VALUE_FILE"`
	#echo "$VALUE"

	$BIN/json-field.py -f "0:title" -b 0 < "$TMP_VALUE_FILE" > "$VALUE_FILE"
	title=`cat "$VALUE_FILE"`
	#echo "$title"

	$BIN/json-field.py -f "0:author" -b 0 < "$TMP_VALUE_FILE" > "$VALUE_FILE"
	author=`cat "$VALUE_FILE"`
	#echo "$author"

	$BIN/json-field.py -f "0:pubdate" -b 0 < "$TMP_VALUE_FILE" > "$VALUE_FILE"
	pubdate=`cat "$VALUE_FILE"`
	#echo "$pubdate"

	$BIN/json-field.py -f "0:body" -b 0 < "$TMP_VALUE_FILE" > "$VALUE_FILE"
	body=`cat "$VALUE_FILE"`
	#echo "$body"

	$BIN/json-field.py -f "0:errors_mask" -b 0 < "$TMP_VALUE_FILE" > "$VALUE_FILE"
	errors_mask=`cat "$VALUE_FILE"`
	#echo "$errors_mask" 

	if [ "$title" != "%title%" ] && [ "$author" != "%author%" ] && [ "$pubdate" != "%pubdate%" ] && [ "$body" != "%body%" ] && [ "$errors_mask" = "0" ]
	then
		EXIT_CODE=0
	else
		EXIT_CODE=1
	fi
	rm -f $TMP_CONTENT_FILE
	rm -f $VALUE_FILE
	echo "Test RestAPI stopped"
}

testRegular()
{
	if [ $EXIT_CODE -eq 1 ] 
	then
		return 1
	fi

	echo "Test Regular crawling started"
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
	VALUE_FILE="$TMP_DIR/value.json.tmp"

	CONTENT_URL_FILES=$TEST_DIR/url_content*.json
	for f in $CONTENT_URL_FILES
	do
		echo $f >> ../log/$01.log 2>&1
		./dc-client.py --config=../ini/dc-client.ini --command=URL_CONTENT --file=$f > "$TMP_CONTENT_FILE" 2>&1
		cat "$TMP_CONTENT_FILE" >> ../log/$0.log 2>&1

		$BIN/json-field.py -f "errorCode" < "$TMP_CONTENT_FILE" > "$VALUE_FILE"
		errorCode=`cat "$VALUE_FILE"`

		$BIN/json-field.py -f "errorMessage" < "$TMP_CONTENT_FILE" > "$VALUE_FILE"
		errorMessage=`cat "$VALUE_FILE"`

		if [ "$errorCode" -eq 0 ] && [ "$errorMessage" == "" ]
		then
			EXIT_CODE=0
		else
			EXIT_CODE=1
		fi
	done

	sleep $SLEEP

	rm -f $TMP_CONTENT_FILE
	rm -f $VALUE_FILE

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
	echo "Test Regular crawling stopped"
}

testRestAPI
testRegular

exit $EXIT_CODE
