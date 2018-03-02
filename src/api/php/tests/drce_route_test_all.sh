#!/bin/bash

. ../cfg/current_cfg.sh

TMP_DIR="/tmp/"
OUT_FILE="$TMP_DIR$0.log.tmp"
JSON_FIELD_COMMAND="json-field.php"

../manage/properties.sh outFile="$OUT_FILE"

remoteHost=$(echo $CMD_HOSTS_CSV | tr "," "\n")

NODE_NAMES=()
a=0
for hostName in ${remoteHost[@]}
	do
		for portName in ${REPLICAS_POOL_ADMIN_PORTS[@]}
			do  
				nodeName=`$BIN_DIR$JSON_FIELD_COMMAND --field="$hostName%3A$portName":DataProcessorData:nodeName < $OUT_FILE`
				NODE_NAMES[$a]=$nodeName
				a=$(($a+1))
			done
	done

SZ=${#NODE_NAMES[@]}

NODES=()
NODES[0]="\"${NODE_NAMES[0]}\""
a=0
for NODE_NAME in "${NODE_NAMES[@]}"
	do
		str="$str\"$NODE_NAME\""		
   	a=$(($a+1))
		if [ "$a" -lt "$SZ" ]
		then
			str="$str,"
		fi
	done

NODES[1]=$str
NODES[2]="$str,\"n013_data\""
NODES[3]="\"\""

rm -f "$OUT_FILE"

TEST_COMMAND="./drce_route_test.sh"

TESTS_NUMBERS=("00" "01")
MODES=("Sync" "Async")
#NODES=("\"n011_data\"" "\"n011_data\",\"n012_data\"" "\"n011_data\",\"n012_data\",\"n013_data\"" "\"\"")
ROUTES=()

ROLE_MIN=-1
ROLE_MAX=7

##for sample route JSON: "{\"role\":5,\"nodes\":[\"n011_data\",\"n012_data\",\"n013_data\"]}"

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color

printMsg()
{
	echo -e "${3}$1${NC} $2"
}

printMessage()
{
	printMsg "$1" "$2" "$GREEN"
}

printOK()
{
	printMsg "[       OK ]" "$1" "$GREEN"
}

printFail()
{
	printMsg "[     FAIL ]" "$1" "$RED"
}

#######################
## Main process block
#######################
role=$ROLE_MIN

while [ $role -lt $ROLE_MAX ]
do
##	echo "$role"
	for route in ${NODES[@]}
		do			
			JSON="{\"role\":$role,\"nodes\":[$route]}"		
##			echo "JSON: $JSON"	

			ROUTES=("${ROUTES[@]}" "$JSON")
		done

	role=$(($role+1))
done

echo "Please, be patient while test in progress..."
printMessage "[==========]"

passed=0
a=0
for TEST_NUMBER in "${TESTS_NUMBERS[@]}"
  do
		for ROUTE in "${ROUTES[@]}"
			do
    		printMessage "[ RUN      ]" "TEST $(($a+1)) started -----------------------------------"
				printMessage "[          ]" "TASK ID: 5$TEST_NUMBER$a  MODE: ${MODES[$TEST_NUMBER]}"		
    		printMessage "[          ]" "ROUTE: $ROUTE"		

				$TEST_COMMAND "$ROUTE" "5$TEST_NUMBER$a" "$TEST_NUMBER" 
				if [ "$?" == "0" ] 
				then
					passed=$((passed+1))
					printOK "TEST $(($a+1)) finished ----------------------------------"
				else
					printFail "TEST $(($a+1)) finished ----------------------------------"
				fi
				a=$(($a+1))
			done
  done

for TEST_NUMBER in "${TESTS_NUMBERS[@]}"
  do
		printMessage "[ RUN      ]" "TEST $(($a+1)) started -----------------------------------"
		printMessage "[          ]" "TASK ID: 5$TEST_NUMBER$a  MODE: ${MODES[$TEST_NUMBER]}"		
		printMessage "[          ]" "ROUTE: ''"		

		$TEST_COMMAND "" "5$TEST_NUMBER$a" "$TEST_NUMBER" 
		if [ "$?" == "0" ] 
		then
			passed=$((passed+1))
			printOK "TEST $(($a+1)) finished ----------------------------------"
		else
			printFail "TEST $(($a+1)) finished ----------------------------------"
		fi
		a=$(($a+1))
  done
printMessage "[==========]"
printMessage "[  PASSED  ]" "$passed/$a tests success"

exit 0

