#!/bin/bash

. ../cfg/current_cfg.sh

TASK_ID=33
TEST_HOST="127.0.0.1"
TEST_PORT="8080"

if [ "$1" == "" ]; then
  TASK_ID=33335
else
  TASK_ID="$1"
fi

LOG_FILE="$LOG_DIR$0.$TASK_ID.$NODE_APP_LOG_PREFIX.log"
TMP_FILE="/tmp/$0.tmp"

JSON_FIELD_COMMAND="json-field.php"

RED='\e[0;31m'
GREEN='\e[0;32m'
##BLUE='\e[0;34m'
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
## $1 - message string about success
{
	local length=$(($LENGTH-${#1}))
	
	echo -n "$1:"
	printSpace "$length"
	echo -e "[ ${GREEN}SUCCESS${NC} ]"
}

printFail()
## $1 - message string about failure
{
	local length=$(($LENGTH-${#1}))
	echo -n "$1:"
	printSpace "$length"

	echo -e "[ ${RED}FAIL${NC} ]"
}

removeFile()
## $1 - file name
{
	if [ -e "$1" ]
	then
		rm -f $1
	fi
}

testExecution()
## $1 - title message string 
## $2 - host value string
## $3 - port value
## $4 - drce command name
## $5 - right value
{
	printf "\n$1\n" >> $LOG_FILE
	local result=`$BIN_DIR$MANAGER_COMMAND --host="$2" --port="$3" --command="$4" --id=$TASK_ID --timeout=$SMALL_TIMEOUT --log=0 2>&1`
	echo $result >> $LOG_FILE
	echo -n $result > $TMP_FILE

	local value=`$BIN_DIR$JSON_FIELD_COMMAND --field="$2%3A$3":0:DataProcessorData < $TMP_FILE`

	if [[ $value =~ "$5" ]]
	then
		printSuccess "$1"
	else
		printFail "$1"
	fi
}

## Remove file if it is exist
removeFile $LOG_FILE 

## Get old host value
testExecution "Get host value '$HOST'" "$HOST" "$PORT" "DRCE_GET_HOST" "$HOST"

## Set new host value instead old host 
testExecution "Set host value '$TEST_HOST' instead '$HOST'" "$TEST_HOST" "$PORT" "DRCE_SET_HOST" "$HOST"

## Get new host value
testExecution "Get host value: '$TEST_HOST'" "$HOST" "$PORT" "DRCE_GET_HOST" "$TEST_HOST"

## Set old host value instead new host value
testExecution "Set host value: '$HOST' instead '$TEST_HOST'" "$HOST" "$PORT" "DRCE_SET_HOST" "$TEST_HOST"

## Get old host value
testExecution "Get host value: '$HOST'" "$HOST" "$PORT" "DRCE_GET_HOST" "$HOST"

if [ "${#REPLICAS_POOL_ADMIN_PORTS[@]}" -ge "2" ]  
then
	for ADMIN_PORT in "${REPLICAS_POOL_ADMIN_PORTS[@]}"
		do
			if [ "$ADMIN_PORT" -ne "$PORT" ]
			then
				TEST_PORT=$ADMIN_PORT
				
				## Get old port value
				testExecution "Get port value '$PORT'" "$HOST" "$PORT" "DRCE_GET_PORT" "$PORT"

				## Set new port value instead old port 
				testExecution "Set port value '$TEST_PORT' instead '$PORT'" "$HOST" "$TEST_PORT" "DRCE_SET_PORT" "$TEST_PORT"

				## Get new port value
				testExecution "Get port value: '$TEST_PORT'" "$HOST" "$PORT" "DRCE_GET_PORT" "$PORT"

				## Set old port value instead new port value
				testExecution "Set port value: '$PORT' instead '$TEST_PORT'" "$HOST" "$PORT" "DRCE_SET_PORT" "$PORT"

				## Get old port value
				testExecution "Get port value: '$PORT'" "$HOST" "$PORT" "DRCE_GET_PORT" "$PORT"
			fi
		done
else
	## Get old port value
	testExecution "Get port value '$PORT'" "$HOST" "$PORT" "DRCE_GET_PORT" "$PORT"

	## Try set new port value instead old port and return error as result 
	testExecution "Try set port value '$TEST_PORT' instead '$PORT' return error" "$HOST" "$TEST_PORT" "DRCE_SET_PORT" "E"

	## Try get old port value
	testExecution "Try get port value '$TEST_PORT' return error" "$HOST" "$TEST_PORT" "DRCE_GET_PORT" "E"
fi

## Cleanup temporary file after tests
removeFile $TMP_FILE

