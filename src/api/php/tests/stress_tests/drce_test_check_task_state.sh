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

REPEAT_LIMIT=300

TASK_ID=$1
STEP_NUMBER="$2"
FILE_STDOUT="$3"

if [ "$TASK_ID" == "" ]
then
  TASK_ID=5000
fi

HOME_DIR="$TESTS_PATH../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"

JSON_FIELD_COMMAND="json-field.php"

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

printState()
## $1 - string message 
## $2 - 'stdout' data for print 
{
	local val=""
	if [ -n "$2" ]
	then
		val="$2"
	fi
	echo -e "$1 TASK: ${BLUE}${TASK_STATES[$STATE]}${NC} $val"	
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
#		if [ $? -eq 0 ]
#		then
#			echo "rm -f $1"
#		fi
	fi	
}

executionRequestCheck()
## $1 - task ID
{
	a=0
	while [ $a -lt $REPEAT_LIMIT ]
	do
		a=$(($a+1))

#		removeFile $STEP_FILE

		cd $TESTS_PATH
		if [ -e $LOG_DIR$1"_host.txt" ]
		then
			EXECUTED_HOST=`cat $LOG_DIR$1"_host.txt"`
		fi		
		if [ "$EXECUTED_HOST" == "" ]
		then
			EXECUTED_HOST=$HOST
		fi
		
		if [ -e $LOG_DIR$1"_port.txt" ]
		then
			EXECUTED_PORT=`cat $LOG_DIR$1"_port.txt"`
		fi
		if [ "$EXECUTED_PORT" == "" ]
		then
			EXECUTED_PORT=$PORT
		fi

		$BIN_DIR$MANAGER_COMMAND --host=$EXECUTED_HOST --port=$EXECUTED_PORT --command=DRCE --request=CHECK --id=$1 --json=$DRCE_TEST_JSON_FILE_CHECK --timeout=$BIG_TIMEOUT --log=0 2>&1 > $STEP_FILE
		
		if [ $? -ne 0 ]
		then
			printFail "CHECK STATE EXIT"
		fi

		ID=`$BIN_DIR$JSON_FIELD_COMMAND --field="$EXECUTED_HOST%3A$EXECUTED_PORT":1:0:id < $STEP_FILE`	
		STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$EXECUTED_HOST%3A$EXECUTED_PORT":1:0:state < $STEP_FILE`
		ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$EXECUTED_HOST%3A$EXECUTED_PORT":1:0:error_code < $STEP_FILE` 
		STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field="$EXECUTED_HOST%3A$EXECUTED_PORT":1:0:stdout < $STEP_FILE` 
		STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field="$EXECUTED_HOST%3A$EXECUTED_PORT":1:0:stderror < $STEP_FILE` 
		EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field="$EXECUTED_HOST%3A$EXECUTED_PORT":1:0:exit_status < $STEP_FILE`
	
		cd $CUR_PATH
		
		if [ "$FILE_STDOUT" == ""	]
		then
			printState "CHECK STATE" "{ $STDOUT }"
		else
			printState "CHECK STATE" "$a sec."
		fi

		if [[ "$STATE" -eq 0 || "$STATE" -eq 4 || "$STATE" -eq 11 || "$ERROR_CODE" -ne 0 ]]
		then
			echo "STATE: $STATE  ERROR_CODE: $ERROR_CODE  EXIT_STATUS: $EXIT_STATUS  STDERR: $STDERR"	

			break
		fi	
		sleep 1
	done	

	if [ "$FILE_STDOUT" != ""	]
	then
		echo "$STDOUT" > $FILE_STDOUT

		if [ -e "$FILE_STDOUT" ]
		then
			printSuccess "CHECK STDOUT"
		else
			printFail "CHECK STDOUT"
		fi
	fi
}

#######################
## Main process block
#######################
makeStepName "$STEP_NUMBER"
removeFile $STEP_FILE

executionRequestCheck $TASK_ID	

exit 0

