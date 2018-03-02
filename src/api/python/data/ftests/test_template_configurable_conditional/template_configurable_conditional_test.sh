#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" ##"../data/ftests/test_content_hash_algorithms"
RESPONSE_JSON_DIR="../../../log"
#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=BK93JFdBezMEQCZX1cu2HMRraexVKC7V"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
  #Good news scraping static fetcher for configurable conditional test 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/template_configurable_conditional_test1.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for configurable conditional test 2
	wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/template_configurable_conditional_test2.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for configurable conditional test 3
	wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/template_configurable_conditional_test3.json" $HTTP_URL >> $LOG
    
  echo "Tests finished" >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi