#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" ##"../data/ftests/test_content_hash_algorithms"
RESPONSE_JSON_DIR="../../../log"
HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
#HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
  #Good news scraping static fetcher for scraper hash algorithm number 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_algorithm1.log" -O "$RESPONSE_JSON_DIR/$0_algorithm1.result.json" --post-file "$REQUESTS_JSON_DIR/content_hash_test_algorithm1.json" $HTTP_URL >> $LOG
  #Good news scraping static fetcher for scraper hash algorithm number 2
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_algorithm2.log" -O "$RESPONSE_JSON_DIR/$0_algorithm2.result.json" --post-file "$REQUESTS_JSON_DIR/content_hash_test_algorithm2.json" $HTTP_URL >> $LOG
  #Good news scraping static fetcher for scraper hash algorithm number 3
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_algorithm3.log" -O "$RESPONSE_JSON_DIR/$0_algorithm3.result.json" --post-file "$REQUESTS_JSON_DIR/content_hash_test_algorithm3.json" $HTTP_URL >> $LOG
  #Good news scraping static fetcher for scraper hash algorithm number 4
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_algorithm4.log" -O "$RESPONSE_JSON_DIR/$0_algorithm4.result.json" --post-file "$REQUESTS_JSON_DIR/content_hash_test_algorithm4.json" $HTTP_URL >> $LOG
  
  echo "Tests finished" >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi
