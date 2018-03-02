#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=200000
BIG_TIMEOUT=300000
STEP_FILE=""
REPEAT_LIMIT=10

TASK_ID="123"
TEST_NUMBER_SET="$1"

if [ "$TEST_NUMBER_SET" == "" ]
then
  TEST_NUMBER_SET="00"
fi

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"
TASK_DATA_FILE="$TASK_DATA_DIR$TASK_ID.data"
TASK_REQVEST_FILE="$TASK_DATA_DIR$TASK_ID.req"
TASK_STATUS_FILE="$TASK_STATUS_DIR$TASK_ID"

DRCE_TEST_JSON_FILE_SET="$DATA_DIR$SELENIUM_CHROME_DIR/c112_localhost_selenium_json_set$TEST_NUMBER_SET.txt"

JSON_FIELD_COMMAND="json-field.php"

makeStepName()
## $1 - step number
{
	STEP_FILE=$LOG_DIR$TASK_ID.$NODE_APP_LOG_PREFIX"_test_selenuim"$1".json"
}


executionRequestSet()
{
	$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE_SET --id=$TASK_ID --cover=0 > $STEP_FILE

	if [ "$?" -ne "0" ]
	then
		printFail "SET NEW TASK"
	fi

	ID=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:id < $STEP_FILE`
	HOST=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:host < $STEP_FILE`
	PORT=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:port < $STEP_FILE`
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $STEP_FILE`
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_message < $STEP_FILE`
	EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:exit_status < $STEP_FILE`
	TYPE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:type < $STEP_FILE`
	STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stderror < $STEP_FILE`
	STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stdout < $STEP_FILE` 

	if [ "$ERROR_CODE" == "" ]
	then
		echo "Problem execution test... Possible param 'SMALL_TIMEOUT=$SMALL_TIMEOUT' need to increase..."
		exit 1
	fi

	if [ "$HOST" == "" ]
	then
		echo "Problem execution test... Possible setting of HCE cluster need to check..."
		exit 2
	fi
}

#######################
## Main process block
#######################
## cleanup data and status files

## below test of request SET NEW TASK
makeStepName 1
executionRequestSet 

exit 0

