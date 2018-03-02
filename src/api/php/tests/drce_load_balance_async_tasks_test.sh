#!/bin/bash

## Attention! Before start test necessary restart hce-node cluster!!!

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3
SMALL_TIMEOUT=150000
STEP_FILE=""
HOST=""
COUNT=30
SLEEP=1
LINE_WIDTH=45

NODE_NAMES=()

TASK_ID="5000"
OPTION=$1

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color

LENGTH=18 # default length for format output

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"
DRCE_TEST_JSON_FILE_SET=""

TMP_DIR="/tmp/"
OUT_FILE="$TMP_DIR$0.log.tmp"
JSON_FIELD_COMMAND="json-field.php"

declare -A hosts 
declare -A counts

printUsage()
{
	echo -ne "${RED}Attention! Before start test necessary restart hce-node cluster!!!${NC}"
	echo ""
	echo "Usage: $0 mode=<mode_name>"	
	echo "Allowed values of	mode_name:"  
	echo "			RR - round-robin"
	echo "			RU - resource usage"
	exit 1
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
		echo -ne " > ${BLUE}$2${NC}"
	fi	
	echo ""
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

printRow()
## $1 - value of first column
## $2 - value of second column
## $3 - value of third column
{
	local length=$(($LENGTH-${#1}))	
	echo -n "$1"
	printSpace "$length"

	if [ -n "$2" ]
	then
		length=$(($LENGTH-${#2}))	
		echo -n "$2"
		printSpace "$length"

		if [ -n "$3" ]
		then
			length=$(($LENGTH/2-${#3}))	
			echo -n "$3"
			printSpace "$length"
		fi
	fi
	echo ""
}

printTitle()
## $1 - name of first column
## $2 - name of second column
## $3 - name of third column
{
local length=$(($LENGTH-${#1}))	
	echo -ne "${GREEN}$1${NC}"
	printSpace "$length"

	if [ -n "$2" ]
	then
		length=$(($LENGTH-${#2}))	
		echo -ne "${GREEN}$2${NC}"
		printSpace "$length"

		if [ -n "$3" ]
		then
			length=$(($LENGTH/2-${#3}))	
			echo -ne "${GREEN}$3${NC}"
		fi
	fi
	echo ""
}

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

makeStepName()
## $1 - step number
{
	STEP_FILE=$LOG_DIR$TASK_ID.$NODE_APP_LOG_PREFIX"_test_load_balance_async_step"$1".json"
}

makeJsonFileName()
## $1 - test number
{
	DRCE_TEST_JSON_FILE_SET="$DATA_DIR$DRCE_DATA_DIR_LOAD_BALANCE_ASYNC/c112_localhost_drce_json_set0$1.txt"
}

executionRequestSet()
## $1 - task ID
## $2 - node name for route
## $3 - role number  
{
	if [ -n "$2" ] && [ -n "$3" ]
	then
		ROUTE="{\"role\":$3,\"nodes\":[$2]}"
	fi

	$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE_SET --id=$1 --route=$ROUTE --cover=0 > $STEP_FILE

	if [ "$?" -ne "0" ]
	then
		printFail "EXECUTE TASK $1"
	fi

	local task_id=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:id < $STEP_FILE`
	local error_code=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:error_code < $STEP_FILE`
	local exit_status=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:exit_status < $STEP_FILE`
	HOST=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:host < $STEP_FILE`

	if [ "$error_code" == "" ]
	then
		printFail "EXECUTE TASK $1" "Problem execution test... Possible param 'SMALL_TIMEOUT=$SMALL_TIMEOUT' need to increase..."
		exit 1
	fi

	if [ "$HOST" == "" ]
	then
		printFail "EXECUTE TASK $1" "Problem execution test... Possible setting of HCE cluster need to check..."
		exit 2
	fi

	if [[ "$task_id" -eq "$1" && "$error_code" -eq "0" && "$exit_status" -eq "0" && -n "$HOST" ]]
	then
		printSuccess "EXECUTE TASK $1" "$HOST"
	else
		printFail "EXECUTE TASK $1" "$task_id $error_code $exit_status $HOST"
	fi
}

executionTestCase()
## $1 - number of test case
## $2 - description of test case
## $3 - repeat count
## $4 - node name for route
## $5 - role number 
{
	makeStepName "$1"
	makeJsonFileName "$2"
	a=0
	while [ $a -lt $3 ]
		do
			executionRequestSet $TASK_ID "$4" "$5"
			if [ "$HOST" != "" ]
			then
				hosts["$HOST"]=$HOST
				counts["$HOST"]=$((${counts[$HOST]}+1)) 
				a=$(($a+1))
				TASK_ID=$(($TASK_ID+1))
				sleep $SLEEP
			fi
		done
}
#######################
## Main process block
#######################
if [ "$OPTION" == "" ]
then
	printUsage
fi

cleanup ".json"

../manage/properties.sh outFile="$OUT_FILE"

remoteHost=$(echo $CMD_HOSTS_CSV | tr "," "\n")

CMD_HOSTS=""
a=0
for hostName in ${remoteHost[@]}
	do
		for portName in ${REPLICAS_POOL_ADMIN_PORTS[@]}
			do  
				nodeName=`$BIN_DIR$JSON_FIELD_COMMAND --field="$hostName%3A$portName":DataProcessorData:nodeName < $OUT_FILE`
				NODE_NAMES[$a]=$nodeName
				a=$(($a+1))

				if [ $a -gt 1 ]
				then
					CMD_HOSTS="$CMD_HOSTS,"
				fi
				CMD_HOSTS="$CMD_HOSTS\"$nodeName\""
			done
	done
rm -f "$OUT_FILE"

parseOptions "$@"

if [[ "$mode" == "RR" || "$mode" == "round-robin" ]]
then
	printLine "$LINE_WIDTH"
	printRow "Start test use round-robin mode" " "
	printLine "$LINE_WIDTH"

	executionTestCase "1" "0" $COUNT "$CMD_HOSTS" "1"
	executionTestCase "2" "1" 10 "$CMD_HOSTS" "1"
	executionTestCase "3" "0" $COUNT "$CMD_HOSTS" "1"

elif [[ "$mode" == "RU" || "$mode" == "resource-usage" ]]
then
	printLine "$LINE_WIDTH"
	printRow "Start test use resource-usage mode" " "
	printLine "$LINE_WIDTH"

	executionTestCase "1" "0" $COUNT
	executionTestCase "2" "1" 10
	executionTestCase "3" "0" $COUNT

else
	printUsage  
fi

total=0
for count in ${counts[@]}
	do
		total=$(($total+$count))
	done

printLine "$LINE_WIDTH"
#echo "Total: $total"

printTitle "Host" "Count" "Percent"
printLine "$LINE_WIDTH"
for host in ${hosts[@]}
	do
#		echo "$host = ${counts[$host]}  ($((${counts[$host]}*100/$total)) %)"
		printRow "$host" "${counts[$host]}"  "$((${counts[$host]}*100/$total)) %"
	done
printLine "$LINE_WIDTH"
printRow "Total:" "$total"
printLine "$(($LENGTH/3+$LENGTH))"

exit 0

