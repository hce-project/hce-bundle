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
  REQUESTS_COUNT=100
fi

HOME_DIR="$TESTS_PATH../../"
TASK_DATA_DIR="$HOME_DIR$DATA_DIR"
TASK_STATUS_DIR="$HOME_DIR$LOG_DIR"

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

#######################
## Main process block
#######################
cleanupLog ".json"
cleanupLog ".txt"
cleanupData 

a=0
while [ $a -lt $REQUESTS_COUNT ]
do
	TASK_ID=$(($TASK_ID+1))
  a=$(($a+1))

	./drce_test_mass_new_tasks.sh $TASK_ID "01"

	sleep 0.1
done

exit 0

