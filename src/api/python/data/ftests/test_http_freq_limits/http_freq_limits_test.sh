#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


if [ "$1" == "" ]; then
  echo "Tests started" # > $LOG
  #Good news scraping static fetcher for http freq limits test 1
  #wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/http_freq_limits_test1.json" $HTTP_URL >> $LOG
  #sleep 1
  #Good news scraping static fetcher for http freq limits test 2
  #wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/http_freq_limits_test2.json" $HTTP_URL >> $LOG  
  #sleep 1
  #Good news scraping static fetcher for http freq limits test 3
  #wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/http_freq_limits_test3.json" $HTTP_URL >> $LOG

	a=0
	while [ $a -lt 10 ]
		do
			a=$(($a+1))
			echo "$a) execution test..."
			wget -S -o "$DOWNLOAD_LOG_DIR/$0_$a.log" -O "$RESPONSE_JSON_DIR/$0_$a.result.json" --post-file "$REQUESTS_JSON_DIR/http_freq_limits_test1.json" $HTTP_URL >> $LOG
  		sleep 1
		done 

  echo "Tests finished" # >> $LOG
else
	wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi
