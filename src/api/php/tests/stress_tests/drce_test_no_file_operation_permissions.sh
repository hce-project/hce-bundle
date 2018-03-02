#!/bin/bash

TESTS_PATH="../"
CUR_PATH=`pwd`

cd $TESTS_PATH
. ../cfg/current_cfg.sh
cd $CUR_PATH

TASK_ID=$1
REQUESTS_COUNT=$2

if [ "$TASK_ID" == "" ]
then
  TASK_ID=5000
fi

if [ "$REQUESTS_COUNT" == "" ]
then
  REQUESTS_COUNT=1
fi

HOME_DIR="../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"

JSON_FIELD_COMMAND="json-field.php"

removeFile()
## $1 - file name
{
	if [ -e "$1" ]
	then
		rm -f $1
		if [ $? -eq 0 ]
		then
			echo "rm -f $1"
		fi
	fi	
}

cleanupData()
{
	removeFile "$TASK_DATA_DIR*.data"
	removeFile "$TASK_DATA_DIR*.req"
	removeFile "$TASK_STATUS_DIR*"
}

cleanupLog()
## $1 - extention of file for remove in log folders 
{
	cd $TESTS_PATH
	for filename in $LOG_DIR*$1
		do
			removeFile $filename
		done
	cd $CUR_PATH
}

checkDataFileContent()
## $1 - full data file name
{
	cd $TESTS_PATH
	if [ -e $LOG_DIR$1"_host.txt" ]
	then 
		EXECUTED_HOST=`cat $LOG_DIR$1"_host.txt"`
		if [ "$EXECUTED_HOST" == "$HOST" ]
		then
			local stdout=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stdout < $1` 
			local stderr=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stderror < $1`
			local exit_status=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:exit_status < $1`

			if [ -z "$stdout" ] && [ -n "$stderr" ] && [ $exit_status -eq 126 ]
			then
				echo "Data file has valid content."
			else
				echo "Data file has bad content."
				echo "stdout: '$stdout'"	
				echo "stderr: '$stderr'"
				echo "exit_status: $exit_status"
			fi
		fi
	fi
	cd $CUR_PATH
}

#######################
## Main process block
#######################
cleanupLog ".json"
cleanupLog ".txt"
cleanupData 

a=0
while [ $a -lt $REQUESTS_COUNT ]
do
  a=$(($a+1))	
	./drce_test_mass_new_tasks.sh $TASK_ID "06" "$a"
	./drce_test_check_task_state.sh $TASK_ID "$a" ""

	sleep 1
	checkDataFileContent "$TASK_DATA_DIR$TASK_ID.data"

	TASK_ID=$(($TASK_ID+1))
done

exit 0

