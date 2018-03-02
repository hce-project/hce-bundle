#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
  #Good news scraping static fetcher for test pdate timezones 1
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test1.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 2
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test2.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 3
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test3.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 4
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_4.log" -O "$RESPONSE_JSON_DIR/$0_4.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test4.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 5
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_5.log" -O "$RESPONSE_JSON_DIR/$0_5.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test5.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 6
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_6.log" -O "$RESPONSE_JSON_DIR/$0_6.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test6.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 7
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_7.log" -O "$RESPONSE_JSON_DIR/$0_7.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test7.json" $HTTP_URL >> $LOG
	#Good news scraping static fetcher for test pdate timezones 8
  wget -S -o "$DOWNLOAD_LOG_DIR/$0_8.log" -O "$RESPONSE_JSON_DIR/$0_8.result.json" --post-file "$REQUESTS_JSON_DIR/pdate_timezones_test8.json" $HTTP_URL >> $LOG
    
  echo "Tests finished" >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi
