#!/bin/bash

LOG=/home/$USER/hce-node-bundle/api/python/log/

if [ "$1" == "" ]
then
  INPUT_FILE="-i=./ftest_UrlNormalization.in.txt"
else
  INPUT_FILE="-i=$1"
fi

if [ "$2" == "" ]
then
  OUTPUT_FILE="-o=$LOG""ftest_UrlNormalization.output.log"
else
  OUTPUT_FILE="-o=$2"
fi

PYTHONPATH=/home/hce/hce-node-bundle/api/python/hce python ftest_UrlNormalization.py "$INPUT_FILE" "$OUTPUT_FILE"
 
