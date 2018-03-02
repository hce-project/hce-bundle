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

#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"

if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
        #Good news scraping dynamic fetcher for "Google Search", results concatinated with delimiter ";" in one field
	wget -S -o "$DOWNLOAD_LOG_DIR/$0.good_template_dynamic_google_search00.log" -O "$RESPONSE_JSON_DIR/$0.result.good_template_dynamic_google_search00.json" --post-file "$REQUESTS_JSON_DIR/api_test.good_template_dynamic_google_search00.json" $HTTP_URL >> $LOG

	#Good news scraping dynamic fetcher for "Google Search", results represented as multi-item set
	#wget -S -o "$DOWNLOAD_LOG_DIR/$0.good_template_dynamic_google_search01.log" -O "$RESPONSE_JSON_DIR/$0.result.good_template_dynamic_google_search01.json" --post-file "$REQUESTS_JSON_DIR/api_test.good_template_dynamic_google_search01.json" $HTTP_URL >> $LOG

	#Good news scraping dynamic fetcher for "Google Search", same as above, but uses URL schema and set of keywords
	#wget -S -o "$DOWNLOAD_LOG_DIR/$0.good_template_dynamic_google_search02.log" -O "$RESPONSE_JSON_DIR/$0.result.good_template_dynamic_google_search02.json" --post-file "$REQUESTS_JSON_DIR/api_test.good_template_dynamic_google_search02.json" $HTTP_URL >> $LOG

  echo "Tests finished" >> $LOG
else
  wget -S -o "$DOWNLOAD_LOG_DIR/$1.log" -O "$RESPONSE_JSON_DIR/$1.result.json" --post-file "$REQUESTS_JSON_DIR/$1" $HTTP_URL > $LOG
fi
