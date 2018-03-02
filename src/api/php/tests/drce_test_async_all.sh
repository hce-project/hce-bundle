#!/bin/bash

. ../cfg/current_cfg.sh

TEST_COMMAND="./drce_test_async.sh"

REQUEST_ID="5000"
REQUESTS_SET=("00" "01" "02" "03")
REQUESTS_CHECK=("00" "01")
REQUESTS_GET=("00" "01")
REQUESTS_DEL=("00")
REQUESTS_TERM=("00" "01" "02" "03")

## Sample of usage: ./drce_test_async.sh 5001 01 00 00 00 00

RED='\e[0;31m'
GREEN='\e[0;32m'
BLUE='\e[0;34m'
NC='\e[0m' # No Color

printMsg()
## $1 - string message 
{
	echo -e "${3}$1${NC} $2"
}

printMessage()
## $1 - status of message as string
## $2 - string description of message
{
	printMsg "$1" "$2" "$GREEN"
}

printOK()
## $1 - string description of message
{
	printMsg "[       OK ]" "$1" "$GREEN"
}

printFail()
## $1 - string description of message
{
	printMsg "[     FAIL ]" "$1" "$RED"
}

cleanup()
## $1 - extention of file for remove in log folders 
{
	for filename in $LOG_DIR*$1
		do
			if [ -e $filename ]
			then
				rm -f "$filename"
				echo "rm -f $filename"
			fi
		done
}
#######################
## Main process block
#######################
echo "Please, be patient while test in progress..."
cleanup ".json"

printMessage "[==========]"
passed=0
a=0
for REQUEST_TERM in "${REQUESTS_TERM[@]}"
	do
		for REQUEST_DEL in "${REQUESTS_DEL[@]}"
			do
				for REQUEST_GET in "${REQUESTS_GET[@]}"
					do
						for REQUEST_CHECK in "${REQUESTS_CHECK[@]}"
							do
								for REQUEST_SET in "${REQUESTS_SET[@]}"
									do
										printMessage "[ RUN      ]" "TEST $(($a+1)) started -----------------------------------"
										printMessage "[          ]" "TASK ID: $REQUEST_ID PARAMETERS: $REQUEST_SET $REQUEST_TERM $REQUEST_CHECK $REQUEST_GET $REQUEST_DEL"	

										$TEST_COMMAND "$REQUEST_ID" "$REQUEST_SET" "$REQUEST_TERM" "$REQUEST_CHECK" "$REQUEST_GET" "$REQUEST_DEL"
										if [ "$?" == "0" ] 
										then
											passed=$((passed+1))
											printOK "TEST $(($a+1)) finished ----------------------------------"
										else
											printFail "TEST $(($a+1)) finished ----------------------------------"
										fi

										REQUEST_ID=$(($REQUEST_ID+1))
										a=$(($a+1))
									done
							done
					done
			done
	done
printMessage "[==========]"
printMessage "[  PASSED  ]" "$passed/$a tests success"

exit 0

