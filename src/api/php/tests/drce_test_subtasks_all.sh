#!/bin/bash

. ../cfg/current_cfg.sh

DRCE_TESTS_NUMBERS=( 00 01 02 03 04 05 06 07 08 09 10)
DRCE_TEST_COMMAND="./drce_test_subtasks.sh"

RED='\e[0;31m'
GREEN='\e[0;32m'
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

echo "Please, be patient while test in progress..."
printMessage "[==========]"

passed=0
a=0
for TEST_NUMBER in "${DRCE_TESTS_NUMBERS[@]}"
  do
    printMessage "[ RUN      ]" "TEST $TEST_NUMBER started -----------------------------------"
		let "SUB_TEST_NUMBER = $((a % 2))"
		$DRCE_TEST_COMMAND "$TEST_NUMBER" "50$TEST_NUMBER" "$SUB_TEST_NUMBER"
		if [ "$?" == "0" ] 
		then
			passed=$((passed+1))
			printOK "TEST $TEST_NUMBER finished ----------------------------------"
		else
			printFail "TEST $TEST_NUMBER finished ----------------------------------"
		fi
		a=$(($a+1))
  done
printMessage "[==========]"
printMessage "[  PASSED  ]" "$passed/$a tests success"

