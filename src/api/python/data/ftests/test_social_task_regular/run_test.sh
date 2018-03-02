#!/bin/bash

SLEEP=1
CRAWLING_TIME=480 
EXIT_CODE=0

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_social_task_regular
HCE_BIN=~/hce-node-bundle/api/php/bin

TMP_DIR="/tmp"
TMP_RESULT_FILE="$TMP_DIR/result.json.tmp"
TMP_VALUE_FILE="$TMP_DIR/result.value.tmp"


RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color

LENGTH=50 # default length for format output

printSpace() 
## $1 - print space length
{ 
	for i in $(seq $1)
		do 
			echo -n ' '
	done 
}

printSuccess()
{
	local length=$(($LENGTH-${#1}))	
	echo -n "$1:"
	printSpace "$length"
	echo -e "[ ${GREEN}SUCCESS${NC} ]"
}

printFail()
{
	local length=$(($LENGTH-${#1}))
	echo -n "$1:"
	printSpace "$length"
	echo -e "[ ${RED}FAIL${NC} ]"
	EXIT_CODE=1
}

waitCrawling()
{
	echo "Waiting:"
	for tm in  $(seq $CRAWLING_TIME)
	do
		printSpace "10"
		echo -en "\r\r\r$tm sec."
		sleep 1
	done
	echo ""
}

executeCommand()
## $1 - input json file full name
## $2 - command name
## $3 - command description
{
	cd $BIN
	echo "$3 started"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command="$2" --file="$1" > "$TMP_RESULT_FILE" 2>&1
	cat "$TMP_RESULT_FILE" >> ../log/$0.log 2>&1

	checkErrors
	if [ $? -eq 0 ]
	then
		printSuccess "$3 finished"
	else
		printFail "$3 finished"
	fi
}

checkErrors()
## Return 1 - if check is fail, or 0 - othewise
{
	$BIN/json-field.py -f "errorCode" -b 0 < "$TMP_RESULT_FILE" > "$TMP_VALUE_FILE"
	ERROR_CODE=`cat "$TMP_VALUE_FILE"`

	$BIN/json-field.py -f "errorMessage" -b 0 < "$TMP_RESULT_FILE" > "$TMP_VALUE_FILE"
	ERROR_MESSAGE=`cat "$TMP_VALUE_FILE"`

	if [ "$ERROR_CODE" == "0" ] && [ "$ERROR_MESSAGE" == "" ]
	then
		$BIN/json-field.py -f "itemsList:0:errorCode" -b 0 < "$TMP_RESULT_FILE" > "$TMP_VALUE_FILE"
		ERROR_CODE=`cat "$TMP_VALUE_FILE"`

		$BIN/json-field.py -f "itemsList:0:errorMessage" -b 0 < "$TMP_RESULT_FILE" > "$TMP_VALUE_FILE"
		ERROR_MESSAGE=`cat "$TMP_VALUE_FILE"`

		if [ "$ERROR_CODE" == "0" ] && [ "$ERROR_MESSAGE" == "" ] 
		then
			return 0
		elif [ "$ERROR_CODE" == "0" ] && [ "$ERROR_MESSAGE" == "OK" ]
		then
			return 0	
		else
			return 1
		fi
	else
		return 1
	fi	
}

##############################
## Main loop
##############################
# start cluster if necessary
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN
echo "Start test..." > ../log/$0.log 2>&1

NEW_SITE_FILES=$TEST_DIR/site_new*.json
for f in $NEW_SITE_FILES
do
	executeCommand "$f" "SITE_NEW" "Create new site"
done

sleep $SLEEP

NEW_URL_FILES=$TEST_DIR/url_new*.json
for f in $NEW_URL_FILES
do
	executeCommand "$f" "URL_NEW" "Create new url"
done

waitCrawling
#sleep $SLEEP

CONTENT_URL_FILES=$TEST_DIR/url_content*.json
for f in $CONTENT_URL_FILES
do
	executeCommand "$f" "URL_CONTENT" "Content url"
done

sleep $SLEEP

## Tests usage of attributes
#

FETCH_ATTR_FILES=$TEST_DIR/attr_fetch*.json
for f in $FETCH_ATTR_FILES
do
	executeCommand "$f" "ATTRIBUTE_FETCH" "Fetch attribute"
done

sleep $SLEEP
#exit 0

## Remove test data
#
DELETE_URL_FILES=$TEST_DIR/url_delete*.json
for f in $DELETE_URL_FILES
do
	executeCommand "$f" "URL_DELETE" "Delete url"
done

sleep $SLEEP

DELETE_SITE_FILES=$TEST_DIR/site_delete*.json
for f in $DELETE_SITE_FILES
do
	executeCommand "$f" "SITE_DELETE" "Delete site"
done

rm -f "$TMP_VALUE_FILE"
rm -f "$TMP_RESULT_FILE"
echo "Test finished" >> ../log/$0.log 2>&1
exit $EXIT_CODE

