#!/bin/bash

DELIMITER="|||"

CRITERION=$1
OUT_FILE_NAME=$2

printUsageAndExit()
## $1 - error message string
{
	printf "\nBad command line param. $1\nUsage: %s <criterion> [<out_file_name>]\n" $0
	echo "     <criterion> - task ID for search or other value"
	echo "     <out_file_name> - out result file name in log directory"
	exit 1
}

if [ -z "$CRITERION" ]
then
	#printUsageAndExit "Mandatory must be first argument ID of task's for search."
  CRITERION=" ERROR "
  echo "Searching use default expression as parameter: '$CRITERION'"
fi

HOME_DIR="../../../"
SCRIPT_BIN_DIR="./usr/bin/"
SCRIPT_NAME="logview.sh"

COMMAND=$HOME_DIR$SCRIPT_BIN_DIR$SCRIPT_NAME
LOG_DIR="../log/"

if [ -z $OUT_FILE_NAME ]
then
	OUT_FILE="$LOG_DIR$0.log"
else
	OUT_FILE=$LOG_DIR$OUT_FILE_NAME
fi

$COMMAND "$CRITERION" "$LOG_DIR" "$OUT_FILE" "$DELIMITER"

exit 0
