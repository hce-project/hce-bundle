#!/bin/bash

TESTS_PATH="../"
CUR_PATH=`pwd`

cd $TESTS_PATH
. ../cfg/current_cfg.sh
cd $CUR_PATH

TASK_ID=$1
REQUESTS_COUNT=$2
FILE_STDOUT="$3"

if [ "$TASK_ID" == "" ]
then
  TASK_ID=5000
fi

if [ "$REQUESTS_COUNT" == "" ]
then
  REQUESTS_COUNT=1
fi

if [ "$FILE_STDOUT" == "" ]
then
  FILE_STDOUT="$TESTS_PATH$LOG_DIR""big_size.data"
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

cleanupJSON()
## $1 - extention of file for remove in log folders 
{
	cd $TESTS_PATH
	for filename in $LOG_DIR*$1
		do
			removeFile $filename
		done
	cd $CUR_PATH
}

printData()
## $1 - full data file name
{
	cd $TESTS_PATH
	local stdout=`$BIN_DIR$JSON_FIELD_COMMAND --field=0:stdout < $1` 
	echo "Data file has value: { `echo $stdout|base64 -d` }"	
	cd $CUR_PATH
}

#######################
## Main process block
#######################
cleanupJSON ".json"
cleanupData 

a=0
while [ $a -lt $REQUESTS_COUNT ]
do
  a=$(($a+1))
	./drce_test_mass_new_tasks.sh $TASK_ID "05" $a"_1"
	./drce_test_check_task_state.sh $TASK_ID $a"_2" "$FILE_STDOUT"
done

##removeFile "$FILE_STDOUT" 

exit 0

