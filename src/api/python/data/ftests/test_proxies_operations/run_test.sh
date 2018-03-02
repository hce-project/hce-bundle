#!/bin/bash

SLEEP=1
EXIT_CODE=0

RED='\e[0;31m'
GREEN='\e[0;32m'
NC='\e[0m' # No Color

#HOST="127.0.0.1"
HOST="192.168.253.114"

PORT="5504"
TIMEOUT="90000"

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_proxies_operations
HCE_BIN=~/hce-node-bundle/api/php/bin

TMP_DIR="/tmp"
TMP_RESULT_FILE="$TMP_DIR/result.json.tmp"
TMP_VALUE_FILE="$TMP_DIR/result.value.tmp"

executeCommand()
## $1 - input json file full name
## $2 - command name
## $3 - command description
{
	cd $BIN
	echo "$3 started"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --dcc_clientHost=$HOST --dcc_clientPort=$PORT --dcc_timeout=$TIMEOUT --command="$2" --file="$1" > "$TMP_RESULT_FILE" 2>&1
	cat "$TMP_RESULT_FILE" >> ../log/$0.log 2>&1

	checkErrors
	if [ $? -eq 0 ]
	then
		#echo "$3 finished - Success"
		#echo -ne "${GREEN}Stats is allowed${NC}"
		echo -ne "$3 finished - [ ${GREEN}SUCCESS${NC} ]"
	else
		#echo "$3 finished - Fail"
		echo -ne "$3 finished - [ ${RED}FAIL${NC} ]"
		EXIT_CODE=1
	fi
	echo ""
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
echo "Start test..." 

NEW_SITE_FILES=$TEST_DIR/site_new*.json
for f in $NEW_SITE_FILES
do
	executeCommand "$f" "SITE_NEW" "Create new site"
	checkErrors
done

sleep $SLEEP

NEW_PROXIES_FILES=$TEST_DIR/proxy_new*.json
for f in $NEW_PROXIES_FILES
do
	executeCommand "$f" "PROXY_NEW" "Create new proxy"
	checkErrors
done

sleep $SLEEP

FIND_PROXIES_FILES=$TEST_DIR/proxy_find*.json
for f in $FIND_PROXIES_FILES
do
	executeCommand "$f" "PROXY_FIND" "Proxy find"
	checkErrors
done

sleep $SLEEP

UPDATE_PROXIES_FILES=$TEST_DIR/proxy_update*.json
for f in $UPDATE_PROXIES_FILES
do
	executeCommand "$f" "PROXY_UPDATE" "Proxy update"
	checkErrors
done

sleep $SLEEP

## Tests usage of attributes
#
STATUS_PROXIES_FILES=$TEST_DIR/proxy_status*.json
for f in $STATUS_PROXIES_FILES
do
	executeCommand "$f" "PROXY_STATUS" "Proxy status"
	checkErrors
done

sleep $SLEEP

DELETE_PROXIES_FILES=$TEST_DIR/proxy_delete*.json
for f in $DELETE_PROXIES_FILES
do
	executeCommand "$f" "PROXY_DELETE" "Proxy delete"
	checkErrors
done

sleep $SLEEP

DELETE_SITE_FILES=$TEST_DIR/site_delete*.json
for f in $DELETE_SITE_FILES
do
	executeCommand "$f" "SITE_DELETE" "Delete site"
	checkErrors
done

rm -f "$TMP_VALUE_FILE"
rm -f "$TMP_RESULT_FILE"
echo "Test finished" 
exit $EXIT_CODE

