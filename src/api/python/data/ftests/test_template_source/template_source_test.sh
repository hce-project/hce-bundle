#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"

BIN=~/hce-node-bundle/api/python/bin
TMP_DIR="/tmp"
TMP_FILE="$TMP_DIR/temp.value.tmp"

EXIT_CODE=0

##template source test 
test()
## $1 - test name for message
## $2 - test unique number
{
	#Good news scraping static fetcher for template source test 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_$2.log" -O "$RESPONSE_JSON_DIR/$0_$2.result.json" --post-file "$REQUESTS_JSON_DIR/template_source_test1.json" $HTTP_URL >> $LOG

	$BIN/json-field.py -f "itemsList:0" < "$RESPONSE_JSON_DIR/$0_$2.result.json" > "$TMP_FILE"
	itemsList=`cat "$TMP_FILE"`

	$BIN/json-field.py -f "errorCode" < "$RESPONSE_JSON_DIR/$0_$2.result.json" > "$TMP_FILE"
	errorCode=`cat "$TMP_FILE"`

	$BIN/json-field.py -f "errorMessage" < "$RESPONSE_JSON_DIR/$0_$2.result.json" > "$TMP_FILE"
	errorMessage=`cat "$TMP_FILE"`

	if [ $errorCode -eq 0 ] && [ -z "$errorMessage" ] && [ -n "$itemsList" ]
	then
		echo "$1 $2 - SUCCESS"
		return 0
	fi
  EXIT_CODE=1
	return 1
}


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
  
	test "template source test" "1"
	test "template source test" "2"
	test "template source test" "3"
	test "template source test" "4"
	test "template source test" "5"
	test "template source test" "6"
     
  echo "Tests finished" >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi

rm -f $TMP_FILE

exit $EXIT_CODE

