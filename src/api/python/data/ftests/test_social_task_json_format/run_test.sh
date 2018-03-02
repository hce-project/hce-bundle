#!/bin/bash

CUR_DIR=`pwd`

PYTHON_DIR=../../../
cd $PYTHON_DIR
PYTHON_DIR=`pwd`
cd $CUR_DIR

LOG_DIR="$PYTHON_DIR/log"
BIN_DIR="$PYTHON_DIR/bin"
TEST_DIR="$PYTHON_DIR/hce/ftests"

TINFILE="$CUR_DIR/inputBatch.json"
 
executeTest()
# $1 - convertorFormat
# $2 - socialFormat 
# $3 - testNumber
{
	if [ $1 = "" ]
	then
		format="PICKLE"
	else
		format="$1"
	fi 
	
	if [ "$2" == "" ]
	then
		testNumber="1"
	else
		testNumber="$2"
	fi 

	TSOCFILE="$LOG_DIR/output_social.data$testNumber"
	TINFILE_JSON="$LOG_DIR/input.data$testNumber"	
	TOUTFILE_JSON="$LOG_DIR/output.data$testNumber"

	echo "LOG_DIR: $LOG_DIR"
	echo "BIN_DIR: $BIN_DIR"
	echo "TEST_DIR: $TEST_DIR"

	#cd $HCE_DIR			
	/usr/bin/python $TEST_DIR/testDataConvertor.py --format $format --operation PACK < $TINFILE > $TINFILE_JSON
	#cd $CUR_DIR
	
	cd $BIN_DIR	
	./social_task.py --config=../ini/social_task-rt.ini --format=$format --inputFile=$TINFILE_JSON > $TOUTFILE_JSON
	cd $CUR_DIR
	
	#cd $HCE_DIR
	/usr/bin/python $TEST_DIR/testDataConvertor.py --format $format --operation UNPACK < $TOUTFILE_JSON > $TSOCFILE		
	#cd $CUR_DIR
}


#executeTest "PICKLE" "batch"
executeTest "JSON" 


