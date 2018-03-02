#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file
REQUESTS_JSON_DIR="./" ##"../data/ftests/test_content_hash_algorithms"
RESPONSE_JSON_DIR="../../../log"
DOWNLOAD_LOG_DIR="../../../log"
LOG="../../../log/$0.log"

BIN=~/hce-node-bundle/api/python/bin
HCE_BIN=~/hce-node-bundle/api/php/bin
TMP_DIR="/tmp"
TMP_VALUE_FILE="$TMP_DIR/result.value.tmp"

GOOD_PROXIES_FILE="proxies.200.OK.list"
LENGTH=25

RED='\e[0;31m'
GREEN='\e[0;32m'
NC='\e[0m' # No Color

apiToken=$1

if [ "$apiToken" == "" ]
then
	apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"
	#apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQnnl7uGpgeZxcXv0x%2FL1VqR1Z%2BYsCFfoWA%3D%3D"
fi

#HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api?apiToken=$apiToken"
HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=$apiToken"
#HTTP_URL="http://demo.dc5.hce-project.com/TagsReaperUI/api?apiToken=$apiToken"

printSpace() 
## $1 - print space length
{ 
	for i in $(seq $1)
		do 
			echo -n ' '
	done 
}

checkErrors()
## $1 - temporary result file name
## Return 1 - if check is fail, or 0 - othewise
{
	$BIN/json-field.py -f "errorCode" -b 0 < "$1" > "$TMP_VALUE_FILE"
	ERROR_CODE=`cat "$TMP_VALUE_FILE"`

	$BIN/json-field.py -f "errorMessage" -b 0 < "$1" > "$TMP_VALUE_FILE"
	ERROR_MESSAGE=`cat "$TMP_VALUE_FILE"`

	if [ "$ERROR_CODE" == "0" ] && [ "$ERROR_MESSAGE" == "" ]
	then
		$BIN/json-field.py -f "itemsList:0:errorCode" -b 0 < "$1" > "$TMP_VALUE_FILE"
		ERROR_CODE=`cat "$TMP_VALUE_FILE"`

		$BIN/json-field.py -f "itemsList:0:errorMessage" -b 0 < "$1" > "$TMP_VALUE_FILE"
		ERROR_MESSAGE=`cat "$TMP_VALUE_FILE"`

		local isGood=0
		if [ "$ERROR_CODE" == "0" ] && [ "$ERROR_MESSAGE" == "" ] 
		then
			isGood=1
		elif [ "$ERROR_CODE" == "0" ] && [ "$ERROR_MESSAGE" == "OK" ]
		then
			isGood=1
		fi
		
		if [ $isGood -eq 1 ]
		then
			$BIN/json-field.py -f "itemsList:0:itemObject:0:dbFields:ErrorMask" -b 0 < "$1" > "$TMP_VALUE_FILE"
			ErrorMask=`cat "$TMP_VALUE_FILE"`

			#echo "ErrorMask: $ErrorMask"

			$BIN/json-field.py -f "itemsList:0:itemObject:0:dbFields:HttpCode" -b 0 < "$1" > "$TMP_VALUE_FILE"
			HttpCode=`cat "$TMP_VALUE_FILE"`

			#echo "HttpCode: $HttpCode"

			ip=`echo ${f%.*}`
			ip=`echo ${ip#*/}`

			if [ $ErrorMask -eq 0 ] && [ $HttpCode -eq 200 ]
			then
				echo "$ip" >> "$RESPONSE_JSON_DIR/$GOOD_PROXIES_FILE"	

				local length=$(($LENGTH-${#ip}))
				echo -n "$ip"
				printSpace "$length"
				echo -ne " - [ ${GREEN}GOOD${NC} ]"	
			else
				local length=$(($LENGTH-${#ip}))
				echo -n "$ip"
				printSpace "$length"
			  echo -ne " - [ ${RED}FAIL${NC} ]  HttpCode: $HttpCode  ErrorMask: $ErrorMask"
			fi			
			echo ""
		fi
		rm -f "$TMP_VALUE_FILE"
		return $isGood
	fi	
}




echo "Tests started" > $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_0.log" -O "$RESPONSE_JSON_DIR/$0_0.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test0.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_1.log" -O "$RESPONSE_JSON_DIR/$0_1.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test1.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_2.log" -O "$RESPONSE_JSON_DIR/$0_2.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test2.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_3.log" -O "$RESPONSE_JSON_DIR/$0_3.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test3.json" $HTTP_URL >> $LOG

#Good news scraping static fetcher for test proxies without usage host and port
#wget -S -o "$DOWNLOAD_LOG_DIR/$0_4.log" -O "$RESPONSE_JSON_DIR/$0_4.result.json" --post-file "$REQUESTS_JSON_DIR/proxies_test4.json" $HTTP_URL >> $LOG

#exit 0

#Create input json for test from file with proxies list
./proxies.py --listFile='proxies.list' --jsonFile='proxies_test.json'

INPUT_JSON_FILES=$REQUESTS_JSON_DIR*.in
for f in $INPUT_JSON_FILES
	do
		#echo "wget '$f'"
		#Good news scraping static fetcher for test proxies list
		wget -S -o "$DOWNLOAD_LOG_DIR/$f.log" -O "$RESPONSE_JSON_DIR/$f.result.json" --post-file "$REQUESTS_JSON_DIR/$f" $HTTP_URL >> $LOG

		checkErrors "$RESPONSE_JSON_DIR/$f.result.json"		
		#Remove input file
		rm -f "$REQUESTS_JSON_DIR/$f"
	done	
  
echo "Tests finished" >> $LOG

