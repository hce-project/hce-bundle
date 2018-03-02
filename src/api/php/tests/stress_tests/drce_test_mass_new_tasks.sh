#!/bin/bash

TESTS_PATH="../"
CUR_PATH=`pwd`

cd $TESTS_PATH
. ../cfg/current_cfg.sh
cd $CUR_PATH

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=200000
BIG_TIMEOUT=300000
STEP_FILE=""
HOST_EXEC=""

TASK_ID=$1
TEST_NUMBER_SET="$2"
STEP_NUMBER="$3"

if [ "$TASK_ID" == "" ]
then
  TASK_ID=5000
fi

if [ "$TEST_NUMBER_SET" == "" ]
then
  TEST_NUMBER_SET="00"
fi

HOME_DIR="$TESTS_PATH../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"

JSON_FIELD_COMMAND="json-field.php"
DRCE_TEST_JSON_FILE_SET="$DATA_DIR$DRCE_DATA_DIR_LOAD_STRESS_TESTS/c112_localhost_drce_json_set$TEST_NUMBER_SET.txt"
DRCE_TEST_JSON_FILE_CHECK="$DATA_DIR$DRCE_DATA_DIR_LOAD_STRESS_TESTS/c112_localhost_drce_json_check00.txt"

TASK_STATES=( "FINISHED" "IN_PROGRESS" "SET_AS_NEW" "NOT_FOUND" "TERMINATED" "CRASHED" "NOT_SET_AS_NEW" "UNDEFINED" "QUEUED_TO_RUN" "DELETED" "BUSY" "TERMINATED_AS_EXPIRED")

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color
LENGTH=20 # default length for format output

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
}

makeStepName()
## $1 - step name
{
	cd $TESTS_PATH
	STEP_FILE=$LOG_DIR$TASK_ID.$NODE_APP_LOG_PREFIX"_stress_test$1.json"
	cd $CUR_PATH
}

removeFile()
## $1 - file name
{
	if [ -e "$1" ]
	then
		rm -f $1
		if [ $? -eq 0 ]
		then
			echo "rm -f $1"
		fi
	fi	
}

executionRequestSet()
## $1 - task ID
{
	cd $TESTS_PATH
	$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE_SET --id=$1 --cover=0 > $STEP_FILE

	if [ "$?" -ne "0" ]
	then
		printFail "SET NEW TASK"
	fi

	local task_id=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:id < $STEP_FILE`
	local error_code=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $STEP_FILE`
	local exit_status=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:exit_status < $STEP_FILE`
	local host=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:host < $STEP_FILE`
	local port=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:port < $STEP_FILE`

	if [ "$error_code" == "" ]
	then
		echo "Problem execution test... Possible param 'SMALL_TIMEOUT=$SMALL_TIMEOUT' need to increase..."
		exit 1
	fi

	if [ "$host" == "" ]
	then
		echo "Problem execution test... Possible setting of HCE cluster need to check..."
		exit 2
	fi

	if [[ "$task_id" -eq "$1" && "$error_code" -eq "0" && "$exit_status" -eq "0" ]]
	then
		printSuccess "EXECUTE TASK $1" 
	else
		printFail "EXECUTE TASK $1" "taskID: $task_id errorCode: $error_code exitStatus: $exit_status"
	fi
	
	echo $host > $LOG_DIR$TASK_ID"_host.txt"
	echo $port > $LOG_DIR$TASK_ID"_port.txt"

	cd $CUR_PATH
}

#######################
## Main process block
#######################
makeStepName "$STEP_NUMBER"
removeFile $STEP_FILE

executionRequestSet $TASK_ID	

exit 0

