#!/bin/bash
# simple HCE project DRCE Functional Object starter for asynchronous tasks run
# Usage variables:
# $1 - command
# $2 - stdin

REMOVE_TMP_FILES=1

## pickle Section
#Enable store picles
#export ENV_SCRAPER_STORE_PATH="/tmp/"
#export ENV_PROCESSOR_STORE_PATH="/tmp/"
#export ENV_CRAWLER_STORE_PATH="/tmp/"

#Disable store picles
export ENV_SCRAPER_STORE_PATH=""
export ENV_PROCESSOR_STORE_PATH=""
export ENV_CRAWLER_STORE_PATH=""

## raw content Section
#raw content storage path suffix
#for TR service demo page
export CONTENT_STORE_PATH=$$
#export CONTENT_STORE_PATH=""

TINFILE="/tmp/$(basename $0).$$.in.tmp"
TOUTFILE="/tmp/$(basename $0).$$.out.tmp"

#cp $2 "/tmp/$(basename $0).$$.in0.tmp"

eval "$1 < $2" > $TINFILE

if [ $? -ne 0 ]
then
  if [ $REMOVE_TMP_FILES -ne 0 ]
  then
    rm $TINFILE
  fi
  exit 1
else
  ./processor-task.py --config=../ini/processor-task-rt.ini < $TINFILE > $TOUTFILE
  if [ $? -ne 0 ]
  then
    if [ $REMOVE_TMP_FILES -ne 0 ]
    then
      rm $TINFILE
      rm $TOUTFILE
    fi
    exit 1
  else
    ./rtc-finalizer.py -c=../ini/rtc-finalizer.ini < $TOUTFILE
  fi
  if [ $REMOVE_TMP_FILES -ne 0 ]
  then
    rm $TOUTFILE
  fi
fi

if [ $REMOVE_TMP_FILES -ne 0 ]
then
  rm $TINFILE
fi
