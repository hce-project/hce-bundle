#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=200000
BIG_TIMEOUT=300000
STEP_FILE=""
REPEAT_LIMIT=10
WAIT_PAUSE=8

STATE=0
ERROR_CODE=0
SUB_STATE=0
SUB_ERROR_CODE=0
CLEANUP_FLAG=0

TEST_NUMBER="$1"
TASK_ID="$2"
SUB_TEST_NUMBER="$3"
ROUTE="$4"

if [ "$TEST_NUMBER" == "" ]
then
  TEST_NUMBER="00"
fi

if [ "$TASK_ID" == "" ]
then
  TASK_ID=33334
fi

if [ "$SUB_TEST_NUMBER" == "" ]
then
	SUB_TEST_NUMBER="0"
fi

#echo "TEST_NUMBER: $TEST_NUMBER"
#echo "TASK_ID: $TASK_ID"
#echo "SUB_TEST_NUMBER: $SUB_TEST_NUMBER"
#echo "ROUTE: $ROUTE"

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"
TASK_DATA_FILE="$TASK_DATA_DIR$TASK_ID.data"
TASK_STATUS_FILE="$TASK_STATUS_DIR$TASK_ID"

DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json$TEST_NUMBER.txt"
SUBTASKS_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json"$TEST_NUMBER"_subtasks.txt"
SUBTASKS_JSON_DATA_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json"$TEST_NUMBER"_sub1_data.txt"

JSON_FIELD_COMMAND="json-field.php"

TASK_STATES=( "FINISHED" "IN_PROGRESS" "SET_AS_NEW" "NOT_FOUND" "TERMINATED" "CRASHED" "NOT_SET_AS_NEW" "UNDEFINED" "QUEUED_TO_RUN" "DELETED" "TERMINATED_AS_EXPIRED")

TMP_DIR="/tmp/"
TMP_FILE=""

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
	## cleanup data and status files
	removeFile $TASK_DATA_FILE
	removeFile $TASK_STATUS_FILE
	exit 1
}

printSubtaskStates()
{
	echo -e "$1 TASK: ${BLUE}${TASK_STATES[$STATE]}${NC}  SUBTASKS: ${BLUE}${TASK_STATES[$SUB_STATE]}${NC}"	
}

printState()
{
	echo "STATE: $STATE ( ${TASK_STATES[$STATE]} )"
	echo "ERROR_CODE: $ERROR_CODE"	
	echo "SUB_STATE: $SUB_STATE ( ${TASK_STATES[$SUB_STATE]} )"
	echo "SUB_ERROR_CODE: $SUB_ERROR_CODE"
	echo "CLEANUP_FLAG: $CLEANUP_FLAG"

	if [ -e $TASK_DATA_FILE ] 
	then
		echo "File: '$TASK_DATA_FILE' exist"
	else
		echo "File: '$TASK_DATA_FILE' not exist"
	fi

	if [ -e $TASK_STATUS_FILE ] 
	then
		echo "File: '$TASK_STATUS_FILE' exist"
	else
		echo "File: '$TASK_STATUS_FILE' not exist"
	fi
}

makeStepName()
{
	STEP_FILE=$LOG_DIR$TASK_ID.$NODE_APP_LOG_PREFIX"_test_subtasks"$TEST_NUMBER"_step"$1".json"
}

makeTempFileName()
{
	TMP_FILE="$TMP_DIR$1.tmp"
}

removeFile()
{
	if [ -e "$1" ]
	then
		rm -f $1
	fi
}

checkSubtasks()
{
	local tmp_file=$TMP_FILE
	removeFile $tmp_file
	
	echo -n $@ > $tmp_file

	local ids=()
	local tasks=()
	local a=0
	while [ true ]
		do
			local id=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:id < $tmp_file`
			local subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:subtasks < $tmp_file`
				
			if [ "$id" == "$subtasks" ]
			then 
				break
			fi
#			echo "id: $id"
#			echo "subtasks: $subtasks"
			ids[$a]=$id
			tasks[$a]=$subtasks

			local state=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:state < $tmp_file`
			local error_code=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:error_code < $tmp_file`

			SUB_STATE=$state
			SUB_ERROR_CODE=$error_code
		
			a=$(($a+1))
		done

	a=0
	for task in "${tasks[@]}"
		do
#			echo "ids: ${ids[$a]}"
			makeTempFileName ${ids[$a]}			
			a=$(($a+1))		

			checkSubtasks $task					
		done

	removeFile $tmp_file
}

checkTestStatus()
{
	if [ "$STATE" == "0" ] && [ "$ERROR_CODE" == "0" ] && [ "$SUB_STATE" == "0" ] && [ "$SUB_ERROR_CODE" == "0" ]
	then
		printSuccess "CHECK STATE"
	else
		if [ "$STATE" == "3" ] && [ "$ERROR_CODE" == "107" ]
		then
			printSuccess "CHECK STATE"
		elif [ "$CLEANUP_FLAG" == "0" ] && [ -e $TASK_DATA_FILE ] && [ -e $TASK_STATUS_FILE ] && [ "$STATE" == "0" ] && [ "$ERROR_CODE" == "0" ] && [ "$SUB_STATE" == "0" ] && [ "$SUB_ERROR_CODE" == "0" ]
		then		
			printSuccess "CHECK STATE"
		elif [ "$STATE" == "11" ] && [ "$ERROR_CODE" == "116" ] && [ "$SUB_STATE" == "11" ] && [ "$SUB_ERROR_CODE" == "117" ]
		then		
			printSuccess "CHECK STATE"
		elif [ "$STATE" == "11" ] && [ "$ERROR_CODE" == "116" ] && [ "$SUB_STATE" == "8" ] && [ "$SUB_ERROR_CODE" == "0" ]
		then		
			printSuccess "CHECK STATE"
		else
			printState
			printFail "CHECK STATE 2"			
		fi
	fi
}

checkGetDataSubtasks()
{
	local ret=0
	local tmp_file=$TMP_FILE
	removeFile $tmp_file
	
	echo -n $@ > $tmp_file

	local ids=()
	local tasks=()
	local a=0
	while [ true ]
		do
			local id=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:id < $tmp_file`
			local subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:subtasks < $tmp_file`
				
			if [ "$id" == "$subtasks" ]
			then 
				break
			fi

			local state=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:state < $tmp_file`
			local error_code=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:error_code < $tmp_file`
			local error_message=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:error_message < $tmp_file`
			local type=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:type < $tmp_file`
			local host=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:host < $tmp_file`
			local port=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:port < $tmp_file`
			local pid=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:pid < $tmp_file`
			local stdout_stream=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:stdout < $tmp_file`
			local stderr_stream=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:stderr < $tmp_file`
			local exit_status=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:exit_status < $tmp_file`
			local node=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:node < $tmp_file`
			local files=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:files < $tmp_file`
			local fields=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:fields < $tmp_file`

			ret=1
			if [ -z $state ] && [ -z $error_code ] && [ -z $type ] && [ -z $pid ] && [ -z $exit_status ] && [ -z $files ] && [ -z $fields ] && [ -z $subtasks ] && [ -z $id ]
			then
				ret=0
			fi
#			echo "id: $id"
#			echo "state: $state"
#			echo "error_code: $error_code"
#			echo "error_message: $error_message" 
#			echo "type: $type"
#			echo "host: $host"
#			echo "port: $port"
#			echo "pid: $pid"
#			echo "stdout_stream: $stdout_stream"
#			echo "stderr_stream: $stderr_stream"
#			echo "exit_status: $exit_status"
#			echo "node: $node"
#			echo "files: $files"
#			echo "fields: $fields"

#			echo "subtasks: $subtasks"
			ids[$a]=$id
			tasks[$a]=$subtasks
			a=$(($a+1))
		done

	a=0
	for task in "${tasks[@]}"
		do
			makeTempFileName ${ids[$a]}
			a=$(($a+1))
			checkGetDataSubtasks $task		
			
			if [ "$?" == "0" ]
			then
				ret=0
			fi
		done

	removeFile $tmp_file

	return $ret
}

checkDeleteTasks()
{
	local ret=0
	local tmp_file=$TMP_FILE
	removeFile $tmp_file
	
	echo -n $@ > $tmp_file

	local ids=()
	local tasks=()
	local a=0
	while [ true ]
		do
			local id=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:id < $tmp_file`
			local subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:subtasks < $tmp_file`
				
			if [ "$id" == "$subtasks" ]
			then 
				break
			fi

			local state=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:state < $tmp_file`
			local error_code=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:error_code < $tmp_file`
			local type=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:type < $tmp_file`

			local task_data_file="$HOME_DIR$DATA_DIR$id.data"
			local task_status_file="$HOME_DIR$LOG_DIR$id"

			ret=1
			if [ "$state" == "9" ] && [ "$error_code" == "0" ] && [ "$type" == "4" ] && [ -z $id ] && [ ! -e $task_data_file ] && [ ! -e $task_status_file ]
			then
				ret=0
			fi
#			echo "id: $id"
#			echo "state: $state"
#			echo "error_code: $error_code"
#			echo "type: $type"

			ids[$a]=$id
			tasks[$a]=$subtasks
			a=$(($a+1))
		done

	a=0
	for task in "${tasks[@]}"
		do
			makeTempFileName ${ids[$a]}
			a=$(($a+1))
			checkDeleteTasks $task		
			
			if [ "$?" == "0" ]
			then
				ret=0
			fi
		done

	removeFile $tmp_file

	return $ret
}

checkTerminateTasks()
{
	local ret=0
	local tmp_file=$TMP_FILE
	removeFile $tmp_file
	
	echo -n $@ > $tmp_file

	local ids=()
	local tasks=()
	local a=0
	while [ true ]
		do
			local id=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:id < $tmp_file`
			local subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:subtasks < $tmp_file`
				
			if [ "$id" == "$subtasks" ]
			then 
				break
			fi

			local state=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:state < $tmp_file`
			local error_code=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:error_code < $tmp_file`
			local type=`$BIN_DIR$JSON_FIELD_COMMAND --field=$a:type < $tmp_file`

			local task_data_file="$HOME_DIR$DATA_DIR$id.data"
			local task_status_file="$HOME_DIR$LOG_DIR$id"

			if [ "$state" == "4" ] && [ "$error_code" == "0" ] && [ "$type" == "2" ] && [ -z $id ] && [ ! -e $task_data_file ] && [ ! -e $task_status_file ] $$ [ "$CLEANUP_FLAG" == "1" ]
			then
				ret=0
			elif [ "$state" == "4" ] && [ "$error_code" == "0" ] && [ "$type" == "2" ] && [ -z $id ] && [ -e $task_data_file ] && [ -e $task_status_file ] $$ [ "$CLEANUP_FLAG" == "0" ]
			then
				ret=0
			elif [ "$state" == "3" ] && [ "$error_code" == "0" ] && [ "$type" == "2" ] && [ -z $id ] && [ ! -e $task_data_file ] && [ ! -e $task_status_file ] $$ [ "$CLEANUP_FLAG" == "1" ]
			then
				ret=0
			elif [ "$state" == "3" ] && [ "$error_code" == "0" ] && [ "$type" == "2" ] && [ -z $id ] && [ -e $task_data_file ] && [ -e $task_status_file ] $$ [ "$CLEANUP_FLAG" == "0" ]
			then
				ret=0
			elif [ "$state" == "5" ] && [ "$error_code" == "112" ] && [ "$type" == "2" ] && [ -z $id ]
			then
				ret=0
			else
				ret=1
			fi
#			echo "id: $id"
#			echo "state: $state"
#			echo "error_code: $error_code"
#			echo "type: $type"

			ids[$a]=$id
			tasks[$a]=$subtasks
			a=$(($a+1))
		done

	a=0
	for task in "${tasks[@]}"
		do
			makeTempFileName ${ids[$a]}
			a=$(($a+1))
			checkTerminateTasks $task		
			
			if [ "$?" == "0" ]
			then
				ret=0
			fi
		done

	removeFile $tmp_file

	return $ret
}
#######################
## Main process block
#######################
makeStepName 1
removeFile $STEP_FILE

$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE --id=$TASK_ID --subtasks=$SUBTASKS_JSON_FILE --route=$ROUTE --cover=0 > $STEP_FILE

if [ "$?" -ne "0" ]
then
	printFail "SET NEW TASK"
fi

CLEANUP_FLAG=`$BIN_DIR$JSON_FIELD_COMMAND --field=session:cleanup < $DRCE_TEST_JSON_FILE`
HOST=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:host < $STEP_FILE`
PORT=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:port < $STEP_FILE`
STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:state < $STEP_FILE`
ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $STEP_FILE`

if [ "$ERROR_CODE" == "" ]
then
	echo "Problem execution test... Possible param 'SMALL_TIMEOUT' need to increase..."
	exit 1
fi

if [ "$HOST" == "" ]
then
	echo "Problem execution test... Possible setting of HCE cluster need to check..."
	exit 2
fi

if [[ "$ERROR_CODE" == "0" || "$ERROR_CODE" == "116" ]] 
then
	printSuccess "SET NEW TASK"
else
	printFail "SET NEW TASK"
fi

## below test of request CHECK STATE
DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json_check0$SUB_TEST_NUMBER.txt"
makeStepName 2

a=0
while [ true ]
do
  a=$(($a+1))

	removeFile $STEP_FILE
	sleep 1
		
	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=CHECK --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE --timeout=$BIG_TIMEOUT --log=0 2>&1 > $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "CHECK STATE EXIT"
	fi

	sleep $WAIT_PAUSE

	subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:subtasks < $STEP_FILE`
	id=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`
	
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 

	makeTempFileName $id
	checkSubtasks $subtasks 	

#	echo "STATE: $STATE"
#	echo "ERROR_CODE: $ERROR_CODE"	
#	echo "SUB STATE: $SUB_STATE"
#	echo "SUB ERROR_CODE: $SUB_ERROR_CODE"

	if [[ "$STATE" == "0" && "$SUB_STATE" == "0" ]] || [ "$ERROR_CODE" != "0" ] || [ "$SUB_ERROR_CODE" != "0" ] || [[ "$STATE" == "0" && "$SUB_STATE" == "4" ]]
	then
		break
	fi	

#	echo "$a) CHECK STATE TASK: ${TASK_STATES[$STATE]}  SUBTASKS: ${TASK_STATES[$SUB_STATE]}"	
	printSubtaskStates "$a) CHECK STATE"	
done

checkTestStatus


## below test of request GET DATA
DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json_get0$SUB_TEST_NUMBER.txt"
makeStepName 3

removeFile $STEP_FILE

$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=GET --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

if [ $? -ne 0 ]
then
	printFail "GET DATA"
fi

sleep $WAIT_PAUSE

subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:subtasks < $STEP_FILE`
id=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`

STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 

if [ "$CLEANUP_FLAG" == "0" ] 
then
	makeTempFileName $id
	checkGetDataSubtasks $subtasks 

#	echo "RET: $?"

	if [ "$?" == "0" ]
	then
		printSuccess "GET DATA"
	else
		printState
		printFail "GET DATA 1"		
	fi
elif [ "$CLEANUP_FLAG" == "1" ] 
then
	printSuccess "GET DATA"
else
	printState
	printFail "GET DATA 2"	
fi

## below test of request DELETE TASK
DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json_del00.txt"
makeStepName 4

removeFile $STEP_FILE

$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=DELETE --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

if [ $? -ne 0 ]
then
	printFail "DELETE TASK"
fi

subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:subtasks < $STEP_FILE`
id=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`

STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 

if [ "$CLEANUP_FLAG" == "0" ] 
then
	makeTempFileName $id
	checkDeleteTasks $subtasks 

#	echo "RET: $?"

	if [ "$?" == "0" ]
	then
		printSuccess "DELETE TASK"
	else
		printState
		printFail "DELETE TASK 1"		
	fi
elif [ "$CLEANUP_FLAG" == "1" ] 
then
	printSuccess "DELETE TASK"
else
	printState
	printFail "DELETE TASK 2"	
fi

## below test of request TERMINATE TASK
DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR_SUBTASKS/c112_localhost_drce_json_term0$SUB_TEST_NUMBER.txt"
makeStepName 5

removeFile $STEP_FILE

$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=TERMINATE --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

if [ $? -ne 0 ]
then
	printFail "TERMINATE TASK"
fi

subtasks=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:subtasks < $STEP_FILE`
id=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`

STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 

makeTempFileName $id
checkTerminateTasks $subtasks 

#echo "RET: $?"

if [ "$?" == "0" ]
then
	printSuccess "TERMINATE TASK"
else
	printState
	printFail "TERMINATE TASK"	
fi

## cleanup data after chain of tests if necessary
removeFile "$TASK_DATA_DIR*.*"
removeFile "$TASK_STATUS_DIR*"
#echo "CLEANUP_FLAG: $CLEANUP_FLAG"

