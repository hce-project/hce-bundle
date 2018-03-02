#!/bin/bash
# simple HCE project DRCE Functional Object starter for asynchronous tasks run
# Usage variables:
# $1 - command
# $2 - stdin

#eval "$1 < $2 | ./processor-task.py --config=../ini/processor-task.ini"

REMOVE_TMP_FILES=1

#Enable store picles
#export ENV_SCRAPER_STORE_PATH="/tmp/"
#export ENV_PROCESSOR_STORE_PATH="/tmp/"
#export ENV_CRAWLER_STORE_PATH="/tmp/"

#Disable store picles
export ENV_SCRAPER_STORE_PATH=""
export ENV_PROCESSOR_STORE_PATH=""
export ENV_CRAWLER_STORE_PATH=""

TFILE="/tmp/$(basename $0).$$.batch.tmp"

eval "$1 < $2" > $TFILE

if [ $? -ne 0 ]
then
  if [ $REMOVE_TMP_FILES -ne 0 ]
  then
    rm $TFILE
  fi
  exit 1
else
  ./processor-task.py --config=../ini/processor-task.ini < $TFILE
fi

if [ $REMOVE_TMP_FILES -ne 0 ]
then
  rm $TFILE
fi
