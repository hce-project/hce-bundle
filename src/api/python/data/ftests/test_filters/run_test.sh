#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
#HTTP_URL="http://demo.dc5.hce-project.com/TagsReaperUI/api?apiToken=bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQnnl7uGpgeZxcXv0x%2FL1VqR1Z%2BYsCFfoWA%3D%3D"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


BIN=~/hce-node-bundle/api/python/bin
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_filters
HCE_BIN=~/hce-node-bundle/api/php/bin
TMP_DIR="/tmp"
EXIT_CODE=1


echo "Tests started" > $LOG

#Good template scraping use static fetcher for test filters 1
wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test1.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 2
wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test2.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 3
wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test3.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 4
wget -S -o "$DOWNLOAD_LOG_DIR/$0_4.log" -O "$RESPONSE_JSON_DIR/$0_4.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test4.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 5
wget -S -o "$DOWNLOAD_LOG_DIR/$0_5.log" -O "$RESPONSE_JSON_DIR/$0_5.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test5.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 6
wget -S -o "$DOWNLOAD_LOG_DIR/$0_6.log" -O "$RESPONSE_JSON_DIR/$0_6.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test6.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 7
wget -S -o "$DOWNLOAD_LOG_DIR/$0_7.log" -O "$RESPONSE_JSON_DIR/$0_7.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test7.json" $HTTP_URL >> $LOG

#Good template scraping use static fetcher for test filters 8
wget -S -o "$DOWNLOAD_LOG_DIR/$0_8.log" -O "$RESPONSE_JSON_DIR/$0_8.result.json" --post-file "$REQUESTS_JSON_DIR/filters_test8.json" $HTTP_URL >> $LOG

exit 0


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
  
echo "Tests finished" >> $LOG

exit $EXIT_CODE

