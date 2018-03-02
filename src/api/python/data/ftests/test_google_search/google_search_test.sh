#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


apiToken=$1

if [ "$apiToken" == "" ]
then
	apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
fi

#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api?apiToken=$apiToken"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=$apiToken"


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG

  #Good news scraping static fetcher for test google search 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/google_search_test1.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test google search 2
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/google_search_test2.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test google search 3
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/google_search_test3.json" $HTTP_URL >> $LOG

  echo "Tests finished" >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi
