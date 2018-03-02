#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=200000
BIG_TIMEOUT=300000
STEP_FILE=""
REPEAT_LIMIT=10

TASK_ID="$1"
TEST_NUMBER_SET="$2"
TEST_NUMBER_TERM="$3"
TEST_NUMBER_CHECK="$4"
TEST_NUMBER_GET="$5"
TEST_NUMBER_DEL="$6"

if [ "$TASK_ID" == "" ]
then
  TASK_ID="33334"
fi

if [ "$TEST_NUMBER_SET" == "" ]
then
  TEST_NUMBER_SET="00"
fi

if [ "$TEST_NUMBER_TERM" == "" ]
then
  TEST_NUMBER_TERM="00"
fi

if [ "$TEST_NUMBER_CHECK" == "" ]
then
  TEST_NUMBER_CHECK="00"
fi

if [ "$TEST_NUMBER_GET" == "" ]
then
  TEST_NUMBER_GET="00"
fi

if [ "$TEST_NUMBER_DEL" == "" ]
then
  TEST_NUMBER_DEL="00"
fi

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"
TASK_DATA_FILE="$TASK_DATA_DIR$TASK_ID.data"
TASK_REQVEST_FILE="$TASK_DATA_DIR$TASK_ID.req"
TASK_STATUS_FILE="$TASK_STATUS_DIR$TASK_ID"

DRCE_TEST_JSON_FILE_SET="$DATA_DIR$DRCE_DATA_DIR_ASYNC/c112_localhost_drce_json_set$TEST_NUMBER_SET.txt"
DRCE_TEST_JSON_FILE_CHECK="$DATA_DIR$DRCE_DATA_DIR_ASYNC/c112_localhost_drce_json_check$TEST_NUMBER_CHECK.txt"
DRCE_TEST_JSON_FILE_GET="$DATA_DIR$DRCE_DATA_DIR_ASYNC/c112_localhost_drce_json_get$TEST_NUMBER_GET.txt"
DRCE_TEST_JSON_FILE_DEL="$DATA_DIR$DRCE_DATA_DIR_ASYNC/c112_localhost_drce_json_del$TEST_NUMBER_DEL.txt"
DRCE_TEST_JSON_FILE_TERM="$DATA_DIR$DRCE_DATA_DIR_ASYNC/c112_localhost_drce_json_term$TEST_NUMBER_TERM.txt"

JSON_FIELD_COMMAND="json-field.php"

TASK_STATES=( "FINISHED" "IN_PROGRESS" "SET_AS_NEW" "NOT_FOUND" "TERMINATED" "CRASHED" "NOT_SET_AS_NEW" "UNDEFINED" "QUEUED_TO_RUN" "DELETED" "BUSY" "TERMINATED_AS_EXPIRED")

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color
LENGTH=20 # default length for format output

CLEANUP_FLAG_SET=`$BIN_DIR$JSON_FIELD_COMMAND --field=session:cleanup < $DRCE_TEST_JSON_FILE_SET`
CLEANUP_FLAG_TERM=`$BIN_DIR$JSON_FIELD_COMMAND --field=cleanup < $DRCE_TEST_JSON_FILE_TERM`
TERM_SIGNAL=`$BIN_DIR$JSON_FIELD_COMMAND --field=signal < $DRCE_TEST_JSON_FILE_TERM`
TERM_ALG=`$BIN_DIR$JSON_FIELD_COMMAND --field=alg < $DRCE_TEST_JSON_FILE_TERM`
TYPE_CHECK=`$BIN_DIR$JSON_FIELD_COMMAND --field=type < $DRCE_TEST_JSON_FILE_CHECK`
TYPE_GET=`$BIN_DIR$JSON_FIELD_COMMAND --field=type < $DRCE_TEST_JSON_FILE_GET`
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
REASONS=""

IS_LOCAL_TASK=1
IPS=()

extractIPs()
{
	IPS=`/sbin/ifconfig | grep inet | awk '{ print $2 }' | awk -F: '{ print $2 }' | grep -v '^$'`
}

isExistIP()
## $1 - ip address for checking
{
	for IP in ${IPS[@]}
		do
			if [[ "$IP" == "$1" || "$IP" == "localhost" || "$IP" == "127.0.0.1" ]]
			then
				return 1
			fi
		done
	return 0
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

	## cleanup data and status files
	removeFile $TASK_DATA_FILE
	removeFile $TASK_STATUS_FILE
	removeFile $TASK_REQVEST_FILE
	exit 1
}

printAllowedError()
## $1 - string message
{
	local length=$(($LENGTH-${#1}))
	echo -n "$1:"
	printSpace "$length"
	echo -e "[  ${BLUE}FAIL${NC}  ] Reason: $ERROR_MESSAGE"
	removeFile $TASK_DATA_FILE
  removeFile $TASK_STATUS_FILE
	removeFile $TASK_REQVEST_FILE
  exit 0
}

makeStepName()
## $1 - step number
{
	STEP_FILE=$LOG_DIR$TASK_ID.$NODE_APP_LOG_PREFIX"_test_async_step"$1".json"
}

makeReasons()
{
	REASONS="'id': $ID"
	REASONS="$REASONS, 'host': $HOST"
	REASONS="$REASONS, 'port': $PORT"
	REASONS="$REASONS, 'state' ($STATE): [${TASK_STATES[$STATE]}]"
	REASONS="$REASONS, 'error_code'= $ERROR_CODE"
	REASONS="$REASONS, 'error_message': $ERROR_MESSAGE"
	REASONS="$REASONS, 'exit_status'= $EXIT_STATUS"
	REASONS="$REASONS, 'type'= $TYPE"
	REASONS="$REASONS, 'stderror': $STDERR"
	REASONS="$REASONS, 'stdout': $STDOUT"
}

dumpState()
{
	echo "TASK_ID: $TASK_ID"
	echo "'id': $ID"
	echo "'host': $HOST"
	echo "'port': $PORT"
	echo "'state' ($STATE): [${TASK_STATES[$STATE]}]"
	echo "'error_code'= $ERROR_CODE"
	echo "'error_message': $ERROR_MESSAGE"
	echo "'exit_status'= $EXIT_STATUS"
	echo "'type'= $TYPE"
	echo "'stderror': $STDERR"
	echo "'stdout': $STDOUT"
	echo "CLEANUP_FLAG_SET: $CLEANUP_FLAG_SET"
	echo "CLEANUP_FLAG_TERM: $CLEANUP_FLAG_TERM"
	echo "TYPE_CHECK: $TYPE_CHECK"
	echo "TYPE_GET: $TYPE_GET"

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

printState()
{
	echo -e "$1 TASK: ${BLUE}${TASK_STATES[$STATE]}${NC}"	
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

executionRequestCheck()
{
	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=CHECK --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE_CHECK --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "CHECK STATE EXIT"
	fi

	ID=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`	
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_message < $STEP_FILE`
	EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:exit_status < $STEP_FILE`
	TYPE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:type < $STEP_FILE`
	STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stderror < $STEP_FILE`
	STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stdout < $STEP_FILE`
}

checkRequestCheck()
{
	if [[ "$ID"=="$TASK_ID" && "$STATE" -eq 0 && "$ERROR_CODE" -eq 0 && "$TYPE" -eq 0 && -z "$STDERR" ]] 
	then
		printSuccess "CHECK STATE"
	else
		if [[ "$ID"=="$TASK_ID" && -z "$STDERR" && -z "$STDOUT" ]] 
		then
			if [ "$STATE" == "5" ] && [ "$ERROR_CODE" == "103" ] && [ "$TYPE" -eq 2 ]
			then
				printSuccess "CHECK STATE"
			elif [ "$STATE" == "5" ] && [ "$ERROR_CODE" == "109" ] && [ "$TYPE" -eq 3 ]
			then
				printSuccess "CHECK STATE"
			elif [ "$STATE" == "3" ] && [ "$ERROR_CODE" == "107" ] && [ "$TYPE" -eq 1 ] 
			then
				printSuccess "CHECK STATE"
			elif [ "$CLEANUP_FLAG_SET" -eq 0 ] && [ "$CLEANUP_FLAG_TERM" -eq 0 ] && [ "$TYPE_GET" -eq 2 ] && [ -e $TASK_DATA_FILE ] && [ -e $TASK_STATUS_FILE ] && [ "$STATE" -eq 0 ] && [ "$ERROR_CODE" -eq 0 ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 1 ]
			then	
				if [ "$TYPE_CHECK" -eq 1 ] && [ -z "$STDOUT" ] 
				then
					printSuccess "CHECK STATE"
				elif [ "$TYPE_CHECK" -eq 2 ] && [ -n "$STDOUT" ]
				then
					printSuccess "CHECK STATE"	
				else
					dumpState
					printFail "CHECK STATE 1" 
				fi
			elif [ "$STATE" -eq 0 ] && [ "$ERROR_CODE" -eq 0 ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 0 ]
			then	
				if [ "$TYPE_CHECK" -eq 1 ] && [ -z "$STDOUT" ] 
				then
					printSuccess "CHECK STATE"
				elif [ "$TYPE_CHECK" -eq 2 ] && [ -n "$STDOUT" ]
				then
					printSuccess "CHECK STATE"	
				else
					dumpState
					printFail "CHECK STATE 3" 
				fi
			elif [[ "$CLEANUP_FLAG_SET" -eq 1 || "$CLEANUP_FLAG_TERM" -eq 1 || "$TYPE_GET" -eq 1 ]] && [ ! -e $TASK_DATA_FILE ] && [ ! -e $TASK_STATUS_FILE ] && [ "$STATE" -eq 0 ] && [ "$ERROR_CODE" -eq 0 ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 1 ]
			then
				printSuccess "CHECK STATE"
			elif [ "$STATE" -eq 0 ] && [ "$ERROR_CODE" -eq 0 ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 0 ]
			then
				printSuccess "CHECK STATE"
			elif [ "$CLEANUP_FLAG_SET" -eq 0 ] && [ -e $TASK_DATA_FILE ] && [ -e $TASK_STATUS_FILE ] && [ "$STATE" == "11" ] && [ "$ERROR_CODE" == "116" ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 1 ]
			then		
				printSuccess "CHECK STATE"
			elif [ "$CLEANUP_FLAG_SET" -eq 1 ] && [ ! -e $TASK_DATA_FILE ] && [ ! -e $TASK_STATUS_FILE ] && [ "$STATE" == "11" ] && [ "$ERROR_CODE" == "116" ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 1 ]
			then		
				printSuccess "CHECK STATE"
			elif [ "$STATE" == "11" ] && [ "$ERROR_CODE" == "116" ] && [ "$TYPE" -eq 0 ] && [ "$IS_LOCAL_TASK" -eq 0 ]
			then		
				printSuccess "CHECK STATE"
			elif [ "$STATE" == "7" ] && [ "$ERROR_CODE" == "112" ] && [ "$TYPE" -eq 0 ]
			then		
				printSuccess "CHECK STATE"	
			elif [ "$STATE" -ne 0 ] && [ "$ERROR_CODE" -eq 0 ] 
			then		
				printSuccess "CHECK STATE"
			else
				dumpState
				makeReasons
				printFail "CHECK STATE 2"	"$REASONS"	
			fi
		else
			dumpState
			makeReasons
			printFail "CHECK STATE" "$REASONS"				
		fi
	fi
}

executeRequestGet()
{	
	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=GET --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE_GET --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "GET DATA"
	fi

	ID=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`	
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_message < $STEP_FILE`
	EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:exit_status < $STEP_FILE`
	TYPE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:type < $STEP_FILE`
	STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stderror < $STEP_FILE`
	STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stdout < $STEP_FILE`
}

checkRequestGet()
{
	if [ "$STATE" == "5" ] && [ "$ERROR_CODE" == "109" ] && [ "$TYPE" -eq 3 ]
	then
		printSuccess "GET DATA"
	elif [ "$STATE" == "5" ] && [ "$ERROR_CODE" == "103" ] && [ "$TYPE" -eq 2 ]
	then
		printSuccess "GET DATA"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 0 && "$ERROR_CODE" -eq 0 && -z "$ERROR_MESSAGE" && "$EXIT_STATUS" -eq 0 && "$TYPE" -eq 0 && -z "$STDERR" && -n "$STDOUT" ]] 
	then
		if [ "$TYPE_GET" -eq 2 ] && [ -e $TASK_DATA_FILE ] && [ -e $TASK_STATUS_FILE ] && [ "$IS_LOCAL_TASK" -eq 1 ]
		then
			printSuccess "GET DATA"
		elif [ "$TYPE_GET" -eq 1 ] && [ ! -e $TASK_DATA_FILE ] && [ ! -e $TASK_STATUS_FILE ] && [ "$IS_LOCAL_TASK" -eq 1 ]
		then
			printSuccess "GET DATA"
		elif [[ "$TYPE_GET" -eq 1 || "$TYPE_GET" -eq 2 ]]
		then
			printSuccess "GET DATA"
		else
			dumpState
			printFail "GET DATA"
		fi
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 4 && "$ERROR_CODE" -eq 0 && -z "$ERROR_MESSAGE" && "$EXIT_STATUS" -ne 0 && "$TYPE" -eq 0 && -z "$STDERR" && -z "$STDOUT" ]]
	then
		printSuccess "GET DATA"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 4 && "$ERROR_CODE" -eq 0 && -z "$ERROR_MESSAGE" && "$EXIT_STATUS" -ne 0 && "$TYPE" -eq 2 && -z "$STDERR" && -z "$STDOUT" ]]
	then
		printSuccess "GET DATA"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 11 && "$ERROR_CODE" -eq 116 && -n "$ERROR_MESSAGE" && "$EXIT_STATUS" -ne 0 && "$TYPE" -eq 0 && -z "$STDERR" && -z "$STDOUT" ]]
	then
		printSuccess "GET DATA"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 11 && "$ERROR_CODE" -eq 116 && -n "$ERROR_MESSAGE" && "$EXIT_STATUS" -ne 0 && "$TYPE" -eq 2 && -z "$STDERR" && -z "$STDOUT" ]]
	then
		printSuccess "GET DATA"
	elif [[ "$ID" -eq 0 && "$STATE" -eq 6 && "$ERROR_CODE" -eq 12 && -n "$ERROR_MESSAGE" && "$EXIT_STATUS" -ne 0 && "$TYPE" -eq 4 && -n "$STDERR" && -z "$STDOUT" ]]
	then
		printSuccess "GET DATA"
	else
		dumpState
		printFail "GET DATA"
	fi
}

executeRequestDel()
{
	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=DELETE --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE_DEL --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "DELETE TASK"
	fi

	ID=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`	
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_message < $STEP_FILE`
	EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:exit_status < $STEP_FILE`
	TYPE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:type < $STEP_FILE`
	STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stderror < $STEP_FILE`
	STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stdout < $STEP_FILE`
}

checkRequestDel()
{
	if [[ "$ID"=="$TASK_ID" && "$STATE" -eq 9 && "$ERROR_CODE" -eq 0 && -z "$ERROR_MESSAGE" && "$EXIT_STATUS" -eq 0 && "$TYPE" -eq 4 && -z "$STDERR" && -n "$STDOUT" ]] 
	then
		if [ ! -e $TASK_DATA_FILE ] && [ ! -e $TASK_STATUS_FILE ]
		then
			printSuccess "DELETE TASK"
		else
			dumpState
			printFail "DELETE TASK"
		fi
	elif [[ "$CLEANUP_FLAG_SET" -eq 1 || "$CLEANUP_FLAG_TERM" -eq 1 || "$TYPE_GET" -eq 1 ]] && [ ! -e $TASK_DATA_FILE ] && [ ! -e $TASK_STATUS_FILE ] && [ "$IS_LOCAL_TASK" -eq 1 ] 
	then
		printSuccess "DELETE TASK"
	elif [ "$ID" -eq 0 ] && [ "$CLEANUP_FLAG_SET" -eq 0 ] && [ "$STATE" -eq 6 ] && [ "$EXIT_STATUS" -eq 0 ] && [ "$TYPE" -eq 4 ]
	then
		printSuccess "DELETE TASK"
	elif [ "$ID" -eq 0 ] && [ "$CLEANUP_FLAG_TERM" -eq 0 ] && [ "$STATE" -eq 6 ] && [ "$EXIT_STATUS" -eq 0 ] && [ "$TYPE" -eq 4 ]
	then
		printSuccess "DELETE TASK"
	elif [ "$ID" -eq 0 ] && [ "$TYPE_GET" -eq 2 ] && [ "$STATE" -eq 6 ] && [ "$EXIT_STATUS" -eq 0 ] && [ "$TYPE" -eq 4 ]
	then
		printSuccess "DELETE TASK"
	elif [ "$IS_LOCAL_TASK" -eq 0 ]
	then
		printSuccess "DELETE TASK"
	else
		dumpState
		printFail "DELETE TASK"
	fi
}

executionRequestTerm()
{
	$BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$PORT --command=DRCE --request=TERMINATE --id=$TASK_ID --json=$DRCE_TEST_JSON_FILE_TERM --timeout=$BIG_TIMEOUT --log=0 2>&1 >> $STEP_FILE

	if [ $? -ne 0 ]
	then
		printFail "TERMINATE TASK"
	fi

	ID=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:id < $STEP_FILE`	
	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_code < $STEP_FILE` 
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:error_message < $STEP_FILE`
	EXIT_STATUS=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:exit_status < $STEP_FILE`
	TYPE=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:type < $STEP_FILE`
	STDERR=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stderror < $STEP_FILE`
	STDOUT=`$BIN_DIR$JSON_FIELD_COMMAND --field="$HOST%3A$PORT":1:0:stdout < $STEP_FILE`
}

checkRequestTerm()
{
	local sig_term=15
	local sig_kill=9

	if [[ "$TERM_ALG" -ne 1 && "$TERM_ALG" -ne 2 && "$STATE" -ne 3 ]]
	then
		printFail "TERMINATE TASK" "algoritm = $TERM_ALG"
	fi
	
	if [[ "$TERM_ALG" -eq 1 && "$EXIT_STATUS" -ne $(($sig_term+128)) && "$EXIT_STATUS" -ne $(($sig_kill+128)) && "$STATE" -ne 3 ]]
	then
		printFail "TERMINATE TASK" "exit_status = $EXIT_STATUS"
	fi

	if [[ "$TERM_ALG" -eq 2 && "$EXIT_STATUS" -ne $(($TERM_SIGNAL+128)) && "$STATE" -ne 3 ]]
	then
		printFail "TERMINATE TASK" "exit_status = $EXIT_STATUS"
	fi

	if [[ "$ID"=="$TASK_ID" && "$STATE" -eq 4 && "$ERROR_CODE" -eq 0 && -z "$ERROR_MESSAGE" && "$TYPE" -eq 0 && -z "$STDERR" && -z "$STDOUT" ]] 
	then
		printSuccess "TERMINATE TASK"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 11 && "$ERROR_CODE" -eq 116 && -n "$ERROR_MESSAGE" && "$TYPE" -eq 0 && -z "$STDERR" && -z "$STDOUT" ]] 
	then
		printSuccess "TERMINATE TASK"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 3 && "$ERROR_CODE" -eq 103 && -n "$ERROR_MESSAGE" && -z "$STDERR" && -z "$STDOUT" ]] 
	then
		printSuccess "TERMINATE TASK"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 3 && "$ERROR_CODE" -eq 113 && -n "$ERROR_MESSAGE" && -z "$STDERR" && -z "$STDOUT" ]] 
	then
		printSuccess "TERMINATE TASK"
	elif [[ "$ID"=="$TASK_ID" && "$STATE" -eq 3 && "$ERROR_CODE" -eq 0 && -n "$ERROR_MESSAGE" && "$TYPE" -eq 2 && -z "$STDERR" && -z "$STDOUT" ]] 
	then
		printSuccess "TERMINATE TASK"
	else
		dumpState
		printFail "TERMINATE TASK"
	fi
}

#######################
## Main process block
#######################
## cleanup data and status files
removeFile $TASK_DATA_FILE
removeFile $TASK_STATUS_FILE
removeFile $TASK_REQVEST_FILE

## extract exist IP list for next checking
extractIPs

## below test of request SET NEW TASK
makeStepName 1
removeFile $STEP_FILE

executionRequestSet 
checkRequestSet

isExistIP "$HOST"
IS_LOCAL_TASK=$?

#echo "IP: $HOST isLocalTask: $IS_LOCAL_TASK"

## below test of request CHECK STATE
makeStepName 2
a=0
while [ $a -lt $REPEAT_LIMIT ]
do
  a=$(($a+1))

	removeFile $STEP_FILE
	sleep 2

	executionRequestCheck
	printState "$a ) CHECK STATE"

	if [[ "$STATE" -eq 0 || "$STATE" -eq 4 || "$STATE" -eq 11 || "$ERROR_CODE" -ne 0 ]]
	then
		break
	fi	
done

checkRequestCheck

## below test of request GET DATA
makeStepName 3
removeFile $STEP_FILE

executeRequestGet
checkRequestGet

## below test of request DELETE TASK
makeStepName 4
removeFile $STEP_FILE

executeRequestDel
checkRequestDel

## below make request SET NEW TASK as operation prepare of request TERMITATE TASK and 
makeStepName 5
removeFile $STEP_FILE

executionRequestSet 
checkRequestSet

## below test of request TERMITATE TASK
makeStepName 6
removeFile $STEP_FILE

executionRequestTerm
checkRequestTerm
## below test of request CHECK STATE after TERMITATE operations
makeStepName 7
a=0
while [ $a -lt $REPEAT_LIMIT ]
do
  a=$(($a+1))

	removeFile $STEP_FILE
	sleep 1

	executionRequestCheck
	printState "$a ) CHECK STATE"

	if [[ "$STATE" -eq 0 || "$STATE" -eq 4 || "$STATE" -eq 11 || "$ERROR_CODE" -ne 0 ]]
	then
		break
	fi	
done
checkRequestCheck

## below test of request GET DATA after TERMITATE operations
makeStepName 8
removeFile $STEP_FILE

executeRequestGet
checkRequestGet

## below test of request DELETE TASK after TERMITATE operations
makeStepName 9
removeFile $STEP_FILE

executeRequestDel
checkRequestDel

## cleanup data and status files
removeFile $TASK_DATA_FILE
removeFile $TASK_STATUS_FILE
removeFile $TASK_REQVEST_FILE
## cleanup data after chain of tests if necessary
#removeFile "$TASK_DATA_DIR*.*"
#removeFile "$TASK_STATUS_DIR*"
exit 0

