#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=150000
STEP_FILE=""

TASK_ID="$1"
SHOW_ROUTE=$2

if [ "$TASK_ID" == "" ]
then
  TASK_ID="5000"
fi

if [[ "$SHOW_ROUTE" == "" || "$SHOW_ROUTE" -eq "0" ]]
then
  SHOW_ROUTE="0"
else
  SHOW_ROUTE="1"
fi

TEST_COMMAND="./drce_route_test.sh"
TESTS_NUMBERS=("00" "01")
REQUEST_MODES=("-" "SYNC" "ASYNC")

ALGORITHMS=("-1" "0" "1")
WEIGHTS=()
LIMITS=()
ROUTE=""
REQUEST_MODE=""

DRCE_TEST_JSON_FILE_SET=""
JSON_FIELD_COMMAND="json-field.php"

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color

LENGTH=30 # default length for format output
LINE_LENGTH=75
STATE=""
ERROR_CODE=""
ERROR_MESSAGE=""
PASSED=0

cleanup()
## $1 - extention of file for remove in log folders 
{
	for filename in $LOG_DIR*$1
		do
			if [ -e $filename ]
			then
				rm -f "$filename"
#				echo "rm -f $filename"
			fi
		done
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
## $2 - description as string message
{
	local length=$(($LENGTH-${#1}))	
	echo -n "$1: "
	printSpace "$length"
	echo -ne "[ ${GREEN}SUCCESS${NC} ]"
	if [ -n "$2" ]
	then
		echo -ne " : ${BLUE}$2${NC}"
	fi	
	echo ""
	PASSED=$((PASSED+1))
}

printFail()
## $1 - string message about status
## $2 - string message about reason
{
	local length=$(($LENGTH-${#1}))
	echo -n "$1: "
	printSpace "$length"
	echo -ne "[  ${RED}FAIL${NC}  ]" 
	if [ -n "$2" ]
	then
		echo " $2"
	fi
	echo ""
}

printLine()
## $1 - width of print line
{
	for i in $(seq $1)
		do 
			echo -ne "${GREEN}=${NC}"
	done 
	echo ""
}

printPassed()
## $1 - string message
## $2 - description as string message
{
	local length=$(($LENGTH-${#1}))	
	echo -n "$1: "
	printSpace "$length"
	echo -ne "[ ${GREEN}PASSED${NC} ]"
	if [ -n "$2" ]
	then
		echo -ne " : ${BLUE}$2${NC}"
	fi	
	echo ""
}

makeParameters()
## $1 - count times of repeat value
## $2 - index for insert to arrays
## $2 - one value of weight for repeat
## $3 - one value of limit for repeat
{
	WEIGHT=""
	LIMIT=""
	a=0
	while [ $a -lt $1 ]
		do
			if [ $a -ne 0 ]
			then
				WEIGHT="$WEIGHT,$3"
				LIMIT="$LIMIT,$4"
			else
				WEIGHT="$3"
				LIMIT="$4"
			fi
			a=$(($a+1))
		done
	WEIGHTS[$2]=$WEIGHT
	LIMITS[$2]=$LIMIT
}

makeRoute()
## $1 - algorithm number for calculate of load balancing
## $2 - algorithm weights string
## $3 - resources usage limits string
{
	ROUTE="{\"role\":5,\"nodes\":[],\"alg\":$1,\"alg_weight\":\"$2\",\"limits\":\"$3\"}"
}

makeStepName()
## $1 - task ID
## $2 - test number
{
	STEP_FILE=$LOG_DIR$1.$NODE_APP_LOG_PREFIX"_test_resources_usage_limits"$2".json"
}

makeJsonFileName()
## $1 - test number
{
	DRCE_TEST_JSON_FILE_SET="$DATA_DIR$DRCE_DATA_DIR_ROUTE/c112_localhost_drce_json$1.txt"
}

removeFile()
## $1 - file name
{
	if [ -e "$1" ]
	then
		rm -f $1
	fi
}

getRequestMode()
{
	REQUEST_MODE=`$BIN_DIR$JSON_FIELD_COMMAND --field=session:tmode < $DRCE_TEST_JSON_FILE_SET`
}

executeRequest()
## $1 - task ID
{
	$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE_SET --id=$1 --route=$ROUTE --cover=0 > $STEP_FILE

	if [ "$?" -ne "0" ]
	then
		printFail "REQUEST EXECUTION ${REQUEST_MODES[$REQUEST_MODE]} TASK"
	fi

	STATE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:state < $STEP_FILE`
	ERROR_CODE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $STEP_FILE`
	ERROR_MESSAGE=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_message < $STEP_FILE`

	if [ "$ERROR_CODE" == "" ]
	then
		echo "Problem execution test... Possible param 'SMALL_TIMEOUT' need to increase..."
		exit 1
	fi
}

checkRequest()
{
	if [[ $STATE -eq 0 || $STATE -eq 1 || $STATE -eq 2 ]] && [ $ERROR_CODE -eq 0 ] && [ -z $ERROR_MESSAGE ]
	then
		printSuccess "REQUEST EXECUTION ${REQUEST_MODES[$REQUEST_MODE]} TASK" "Allowed resources usage values"
	elif [[ $STATE -eq 6 && $ERROR_CODE -eq 5002 && -n $ERROR_MESSAGE ]]
	then
		printSuccess "REQUEST EXECUTION ${REQUEST_MODES[$REQUEST_MODE]} TASK" "Exceed resources usage limits"
	else
		local REASONS=""
		if [[ $STATE -ne 0 && $STATE -ne 6 ]]
		then
			REASONS="STATE: $STATE"
		fi

		if [[ $ERROR_CODE -ne 0 && $ERROR_CODE -ne 5002 ]]
		then
			if [ -n "$REASONS" ]
			then
				REASONS="$REASONS,"
			fi
			REASONS="$REASONS ERROR_CODE: $ERROR_CODE"
		fi

		if [ -n $ERROR_MESSAGE ]
		then
			if [ -n "$REASONS" ]
			then
				REASONS="$REASONS,"
			fi
			REASONS="$REASONS ERROR_MESSAGE: $ERROR_MESSAGE"
		fi
		printFail "REQUEST EXECUTION ${REQUEST_MODES[$REQUEST_MODE]} TASK" "$REASONS"
	fi
}

#######################
## Main process block
#######################
printLine "$LINE_LENGTH"
cleanup ".json"

makeParameters 8 0 0.0 0.0
makeParameters 8 1 1.0 1.0

a=0
for ALG in ${ALGORITHMS[@]}
	do
		for WEIGHT in ${WEIGHTS[@]}
			do
				for LIMIT in ${LIMITS[@]}
					do
						makeRoute "$ALG" "$WEIGHT" "$LIMIT"

						if [ "$SHOW_ROUTE" -eq "1" ]
						then
							echo "ROUTE: $ROUTE"
						fi

						for TEST_NUMBER in ${TESTS_NUMBERS[@]}
							do
								ID=$(($TASK_ID+$a+1))
								makeStepName "$ID" "$TEST_NUMBER"
								makeJsonFileName "$TEST_NUMBER"
								getRequestMode

								executeRequest "$ID"
								checkRequest
								a=$(($a+1))
							done
					done
			done
	done

printLine "$LINE_LENGTH"
printPassed "RESULT EXECUTION OF REQUESTS" "$PASSED/$a tests success"
printLine "$LINE_LENGTH"
exit 0

