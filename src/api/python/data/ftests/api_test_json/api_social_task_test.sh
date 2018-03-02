#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" 
RESPONSE_JSON_DIR="../../../log"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"


apiToken=$1

if [ "$apiToken" == "" ]
then
	apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"	# 114
	#apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQnnl7uGpgeZxcXv0x%2FL1VqR1Z%2BYsCFfoWA%3D%3D"	# dc2
	#apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQnnl7uGpgeZxcXv0x%2FL1VqR1Z%2BYsCFfoWA%3D%3D"	# dc5
fi

#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api?apiToken=$apiToken"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=$apiToken"
#HTTP_URL="http://demo.dc2.hce-project.com/TagsReaperUI/api?apiToken=$apiToken"
#HTTP_URL="http://demo.dc5n.hce-project.com/TagsReaperUI/api?apiToken=$apiToken"


if [ "$1" == "" ]; then
  echo "Tests started" > $LOG

  #Good news scraping dynamic fetcher with social task usage
  wget -S -o "$0.good_news_dynamic_social_task00.log" -O "$0.result.good_news_dynamic_social_task00.json" --post-file "api_test.good_news_dynamic_social_task00.json" $HTTP_URL >> $LOG

  wget -S -o "$0.good_news_dynamic_social_task01.log" -O "$0.result.good_news_dynamic_social_task01.json" --post-file "api_test.good_news_dynamic_social_task01.json" $HTTP_URL >> $LOG

  echo "Tests finished" >> $LOG
else
  wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$REQUESTS_JSON_DIR/$1" $HTTP_URL >> $LOG
fi
