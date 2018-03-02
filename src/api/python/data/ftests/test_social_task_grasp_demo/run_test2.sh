#!/bin/bash

CUR_DIR=`pwd`

TEST_DATA_FILE="$CUR_DIR/testData.json"

TINFILE="/tmp/hce-starter-social-data_ja.test.tmp"
TSOCFILE="$CUR_DIR/hce-starter-social-data_ja.test.out"


cp $TEST_DATA_FILE $TINFILE

#cd /home/hce/hce-node-bundle/usr/bin && ./hce-starter-social-data.sh inputFile="$TINFILE" outputFile="$TSOCFILE" lang=ja networks='tw,fb' remote=1 top=1

cd /home/$USER/hce-node-bundle/api/python/bin && ./social_data_calculator.py -c=../ini/social_data_calculator_grasp.ini --inputFile="$TINFILE" --outputFile="$TSOCFILE" --lang=ja --networks='tw,fb' --remote=1 --top=5

rm -f $TINFILE
