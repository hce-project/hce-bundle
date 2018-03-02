#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=150000
STEP_FILE=""
REPEAT_LIMIT=10

ROUTE="$1"
TASK_ID="$2"
TEST_NUMBER="$3"

if [ "$ROUTE" == " " ]
then
  ROUTE=""
fi

if [ "$TASK_ID" == "" ]
then
  TASK_ID="33334"
fi

if [ "$TEST_NUMBER" == "" ]
then
  TEST_NUMBER="00"
fi

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"

DRCE_TEST_JSON_FILE_SET="$DATA_DIR$DRCE_DATA_DIR_ROUTE/c112_localhost_drce_json$TEST_NUMBER.txt"
DRCE_TEST_JSON_FILE_CHECK="$DATA_DIR$DRCE_DATA_DIR_ROUTE/c112_localhost_drce_json_check.txt"
DRCE_TEST_JSON_FILE_GET="$DATA_DIR$DRCE_DATA_DIR_ROUTE/c112_localhost_drce_json_get.txt"

JSON_FIELD_COMMAND="json-field.php"

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color

LENGTH=20 # default length for format output
ERROR_MESSAGE=""

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
	echo -e "[  ${RED}FAIL${NC}  ]"
	## cleanup data and status files
	removeFile $TASK_DATA_FILE
	removeFile $TASK_STATUS_FILE
	exit 1
}

printAllowedError()
{
	local length=$(($LENGTH-${#1}))
	echo -n "$1:"
	printSpace "$length"
	echo -e "[  ${BLUE}FAIL${NC}  ] Reason: $ERROR_MESSAGE"
	removeFile $TASK_DATA_FILE
  removeFile $TASK_STATUS_FILE
  exit 0
}

makeStepName()
{
	STEP_FILE=$LOG_DIR$TASK_ID.$NODE_APP_LOG_PREFIX"_test_route"$TEST_NUMBER"_step"$1".json"
}

removeFile()
{
	if [ -e "$1" ]
	then
		rm -f $1
	fi
}

#######################
## Main process block
#######################
makeStepName 1
removeFile $STEP_FILE

$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE_SET --id=$TASK_ID --route=$ROUTE --cover=0 > $STEP_FILE

if [ "$?" -ne "0" ]
then
	printFail "SET NEW TASK"
fi

HOST=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:host < $STEP_FILE`
PORT=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:port < $STEP_FILE`
STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:state < $STEP_FILE`
ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $STEP_FILE`
ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_message < $STEP_FILE`

if [ "$ERROR_CODE" == "" ]
then
	echo "Problem execution test... Possible param 'SMALL_TIMEOUT' need to increase..."
	exit 1
fi

if [[ "$ERROR_CODE" == "0" || "$ERROR_CODE" == "115" ]] 
then
	printSuccess "SET NEW TASK"
else
	if [[ "$ERROR_CODE" == "5000" ]]
	then
		printAllowedError "SET NEW TASK" 
	else
		printFail "SET NEW TASK"
	fi
fi


## below test of request CHECK STATE
makeStepName 2

a=0
while [ $a -lt $REPEAT_LIMIT ]
do
  a=$(($a+1))

	removeFile $STEP_FILE
	sleep 1
		
	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=CHECK --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE_CHECK --timeout=$BIG_TIMEOUT --log=0 2>&1 > $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "CHECK STATE EXIT"
	fi

	id=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`
	
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 

	if [[ "$STATE" == "0" || "$ERROR_CODE" != "0" ]]
	then
		break
	fi	
done

if [[ "$ERROR_CODE" == "0" || "$ERROR_CODE" == "0" ]] 
then
	printSuccess "CHECK TASK"
else
	printFail "CHECK TASK"
fi

## below test of request GET DATA
makeStepName 3
a=0
while [ $a -lt $REPEAT_LIMIT ]
do
  a=$(($a+1))

	removeFile $STEP_FILE
	sleep 1

	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=GET --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE_GET --timeout=$BIG_TIMEOUT --log=0 2>&1 > $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "GET DATA"
	fi

	id=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`

	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE`

	STDERROR=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stderror < $STEP_FILE`
  STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stdout < $STEP_FILE` 

	if [[ "$STATE" == "0" || "$ERROR_CODE" != "0" || "$ERROR_CODE" == "5000" ]]
	then
		break
	fi	
done	

if [[ "$STATE" == "0" || "$ERROR_CODE" == "0" ]] 
then
	if [[ "$STDERROR" == "" && "$STDOUT" != "" ]] 
	then
		printSuccess "GET DATA"
	else
		printFail "GET DATA"
	fi
else if [[ "$ERROR_CODE" == "5000" ]]
	then
		printSuccess "GET DATA"
	else
		printFail "GET DATA"
	fi
fi

removeFile "$TASK_DATA_DIR*.*"
removeFile "$TASK_STATUS_DIR*"

exit 0

