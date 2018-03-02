#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=200000
BIG_TIMEOUT=300000
RESULT_FILE=""
REPEAT_LIMIT=10
TASK_ID=""

TASKS_COUNT="$1"

if [ "$TASKS_COUNT" == "" ]
then
  TASKS_COUNT="50"
fi

HOME_DIR="../../"

DRCE_TEST_JSON_FILE_SET="$DATA_DIR$DRCE_DATA_DIR_MAX_COUNT_ASYNC/c112_localhost_drce_json_set_task.txt"
DRCE_TEST_JSON_FILE_CHECK="$DATA_DIR$DRCE_DATA_DIR_MAX_COUNT_ASYNC/c112_localhost_drce_json_check_task.txt"
DRCE_TEST_JSON_FILE_GET="$DATA_DIR$DRCE_DATA_DIR_MAX_COUNT_ASYNC/c112_localhost_drce_json_get_task.txt"

JSON_FIELD_COMMAND="json-field.php"

TASK_STATES=( "FINISHED" "IN_PROGRESS" "SET_AS_NEW" "NOT_FOUND" "TERMINATED" "CRASHED" "NOT_SET_AS_NEW" "UNDEFINED" "QUEUED_TO_RUN" "DELETED" "BUSY" "TERMINATED_AS_EXPIRED")

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color
LENGTH=20 # default length for format output

ID=""
HOST=""
PORT=""
STATE=""
ERROR_CODE=""
ERROR_MESSAGE=""
EXIT_STATUS=""
TYPE=""
STDERR=""
STDOUT=""
PID=""

makeResultFileName()
{
	RESULT_FILE=$LOG_DIR"result_file."$NODE_APP_LOG_PREFIX".json"
}

removeFile()
## $1 - file name
{
	if [ -e "$1" ]
	then
		rm -f $1
	fi
}

printSpace() 
## $1 - print space length
{ 
	for i in $(seq $1)
		do 
			echo -n ' '
	done 
}

printSuccess()
## $1 - string message
{
	local length=$(($LENGTH-${#1}))	
	echo -n "$1:"
	printSpace "$length"
	echo -e "[ ${GREEN}SUCCESS${NC} ]"
}

printFail()
## $1 - string message about status
## $2 - string message about reason
{
	local length=$(($LENGTH-${#1}))
	echo -n "$1:"
	printSpace "$length"
	echo -e "[  ${RED}FAIL${NC}  ]" 
	if [ -n "$2" ]
	then
		echo "Reasons: $2"
	fi
	exit 1
}

printState()
## $1 - string message 
## $2 - string description
{
  MSG=$1
  if [[ -z $MSG ]]
  then
    MSG='TASK STATE'
  fi
  DESCRIPTION=$2
	local length=$(($LENGTH-${#MSG}))
  echo -n "$MSG:"
  printSpace "$length"
	echo -e "[ ${BLUE}${TASK_STATES[$STATE]}${NC} ] $DESCRIPTION"	
}

killProcess()
## $1 - pid of process
{
  if [ "$1" != "" ]
  then
    echo "sudo kill -9 $1"
    sudo kill -9 "$1"
  fi
}

executionRequestSet()
# $1 - task Id
{
  TASK_ID=$1
	$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE_SET --id=$TASK_ID --cover=0 > $RESULT_FILE

	if [ "$?" -ne "0" ]
	then
		printFail "SET NEW TASK"
	fi

	ID=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:id < $RESULT_FILE`
	HOST=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:host < $RESULT_FILE`
	PORT=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:port < $RESULT_FILE`
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:state < $RESULT_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $RESULT_FILE`
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_message < $RESULT_FILE`
	EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:exit_status < $RESULT_FILE`
	TYPE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:type < $RESULT_FILE`
	STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stderror < $RESULT_FILE`
	STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stdout < $RESULT_FILE`

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

checkRequestSet()
{
	if [[ "$ID"=="$TASK_ID" && -n "$HOST" && -n "$PORT" && "$ERROR_CODE" -eq 0 && "$STATE" -eq 2 && "$ERROR_CODE" -eq 0 && -z "$ERROR_MESSAGE" && "$EXIT_STATUS"=="0" && "$TYPE" -eq 0 && -z "$STDERR" && -z "$STDOUT" ]] 
	then
		printSuccess "SET NEW TASK"
	else
		local reasons=""

		if [ "$ID" != "$TASK_ID" ]
		then
			reasons="'id': $ID != $TASK_ID"
		fi

		if [ -z "$HOST" ]
		then
			reasons="$reasons, 'host' is empty"
		fi

		if [ -z "$PORT" ]
		then
			reasons="$reasons, 'port' is empty"
		fi

		if [ "$ERROR_CODE" -ne 0 ]
		then
			reasons="$reasons, 'error_code'= $ERROR_CODE"
		fi

		if [ "$STATE" -ne 2 ]
		then
			reasons="$reasons, 'state' ($STATE): [${TASK_STATES[$STATE]}]"
		fi

		if [ "$ERROR_CODE" -ne 0 ]
		then
			reasons="$reasons, 'error_code'= $ERROR_CODE"
			if [ -z "$ERROR_MESSAGE" ]
			then
				reasons="$reasons and 'error_message' is empty"
			fi
		fi

		if [ -n "$ERROR_MESSAGE" ]
		then
			reasons="$reasons, 'error_message': $ERROR_MESSAGE"
		fi

		if [ "$EXIT_STATUS" -ne 0 ]
		then
			reasons="$reasons, 'exit_status'= $EXIT_STATUS"
		fi

		if [ "$TYPE" -ne 0 ]
		then
			reasons="$reasons, 'type'= $TYPE"
		fi

		if [ -n "$STDERR" ]
		then
			reasons="$reasons, 'stderror'= $STDERR"
		fi

		if [ -n "$STDOUT" ]
		then
			reasons="$reasons, 'stdout'= $STDOUT"
		fi

		printFail "SET NEW TASK" "$reasons"
	fi
}

#######################
## Main process block
#######################
makeResultFileName

a=0
while [ $a -lt $TASKS_COUNT ]
do
  a=$(($a+1))

  executionRequestSet "$a"
	printState "Task ID $a"	"[$ERROR_CODE] $ERROR_MESSAGE"
done

exit 0
