#!/bin/bash

CUR_DIR=`pwd`

PYTHON_DIR=/home/$USER/hce-node-bundle/api/python

LOG_DIR="$PYTHON_DIR/log"
BIN_DIR="$PYTHON_DIR/bin"

TINFILE="$CUR_DIR/inputData4.json"
TOUTFILE="$LOG_DIR/output_data.json"

echo "LOG_DIR: $LOG_DIR"
echo "BIN_DIR: $BIN_DIR"

if [[ $1 == "debug" || $1 == "d" ]]
then
	DEBUG_MODE="--debugMode=1"
else
	DEBUG_MODE=""
fi
		
cd $BIN_DIR	
./social_data_get_api.py -c=../ini/social_data_get_api.ini --inputFile=$TINFILE --outputFile=$TOUTFILE $DEBUG_MODE
EXIT_CODE=$?
cd $CUR_DIR

echo "EXIT_CODE = $EXIT_CODE"

exit $EXIT_CODE
