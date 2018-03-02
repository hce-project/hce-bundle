#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" ##"../data/ftests/test_content_hash_algorithms"
RESPONSE_JSON_DIR="../../../log"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"
# https://jira.ioix.com.ua/browse/DC-1667

apiToken=$1

if [ "$apiToken" == "" ]
then
	#apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
	apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQnnl7uGpgeZxcXv0x%2FL1VqR1Z%2BYsCFfoWA%3D%3D"
fi

#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api?apiToken=$apiToken"
#HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=$apiToken"
HTTP_URL="http://demo.dc5.hce-project.com/TagsReaperUI/api?apiToken=$apiToken"

echo "Tests started" > $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_0.log" -O "$RESPONSE_JSON_DIR/$0_0.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test0.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test1.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test2.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test3.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_4.log" -O "$RESPONSE_JSON_DIR/$0_4.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test4.json" $HTTP_URL >> $LOG

exit 0

#Create input json for test from file with proxies list
./proxies.py --listFile='proxies.list' --jsonFile='proxies_test.json'

INPUT_JSON_FILES=$REQUESTS_JSON_DIR*.in
for f in $INPUT_JSON_FILES
	do
		echo "wget '$f'"
		#Good news scraping static fetcher for test proxies list
		wget -S -o "$DOWNLOAD_LOG_DIR/$f.log" -O "$RESPONSE_JSON_DIR/$f.result.json" --post-file "$REQUESTS_JSON_DIR/$f" $HTTP_URL >> $LOG
		#Remove input file
		#rm -f "$f"
	done	
  
echo "Tests finished" >> $LOG

