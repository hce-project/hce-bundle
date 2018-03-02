#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
  #Good news scraping static fetcher for test scraper metrics 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/scraper_metrics_test1.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test scraper metrics 2
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/scraper_metrics_test2.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test scraper metrics 3
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/scraper_metrics_test3.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test scraper metrics 4
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_4.log" -O "$RESPONSE_JSON_DIR/$0_4.result.json" --post-file "$REQUESTS_JSON_DIR/scraper_metrics_test4.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test scraper metrics 5
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_5.log" -O "$RESPONSE_JSON_DIR/$0_5.result.json" --post-file "$REQUESTS_JSON_DIR/scraper_metrics_test5.json" $HTTP_URL >> $LOG
    
  echo "Tests finished" >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi
