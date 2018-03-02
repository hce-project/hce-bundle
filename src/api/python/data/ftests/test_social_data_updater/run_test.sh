#!/bin/bash

CUR_DIR=`pwd`

PYTHON_DIR=/home/$USER/hce-node-bundle/api/python
BIN_DIR="$PYTHON_DIR/bin"

cd $BIN_DIR	
./social_data_updater.py -c=../ini/social_data_updater.ini 
EXIT_CODE=$?
cd $CUR_DIR

echo "exit_code = $EXIT_CODE"

exit $EXIT_CODE

