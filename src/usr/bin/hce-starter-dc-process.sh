#!/bin/bash
# simple HCE project DRCE Functional Object starter for asynchronous tasks run
# Usage variables:
# $1 - command
# $2 - stdin


REMOVE_TMP_FILES=1

#Enable store picles
#export ENV_SCRAPER_STORE_PATH="/tmp/"
#export ENV_PROCESSOR_STORE_PATH="/tmp/"

#Disable store picles
export ENV_SCRAPER_STORE_PATH=""
export ENV_PROCESSOR_STORE_PATH=""

TOUTFILE="/tmp/$(basename $0).$$.out.tmp"
TPOSTFILE="/tmp/$(basename $0).$$.post.tmp"
TFILE="/tmp/$(basename $0).$$.urlFetchOut.tmp"
eval "$1 < $2 > $TFILE"

if [ $? -ne 0 ]
then
  if [ $REMOVE_TMP_FILES -ne 0 ]
  then
    rm $TFILE
  fi
  exit 1
else
  TFILE2="/tmp/$(basename $0).$$.batchConvertorOut.tmp"
  ./urls-to-batch-task.py -c ../ini/urls-to-batch-task.ini < $TFILE > $TFILE2
  STATUS=$?
  if [ $STATUS -ne 0 ]
  then
    if [ $REMOVE_TMP_FILES -ne 0 ]
    then
      rm $TFILE $TFILE2
    fi
    if [ $STATUS -ne 2 ]
    then
      exit 1
    else
      #Exit with zero in case of the STATUS is 2 - means empty batch
      exit 0
    fi
  else
    ./processor-task.py --config=../ini/processor-task.ini < $TFILE2 > $TOUTFILE

    # postprocessing execution
    ./postprocessor_task.py --config=../ini/postprocessor_task.ini < $TOUTFILE > $TPOSTFILE   

    if [ $? -ne 0 ]
    then
      LOG_ERROR_REASONS="Starter has error: $LOG_ERROR_REASONS"
      ./content_updater.py --config=../ini/content_updater.ini --error="$LOG_ERROR_REASONS" < $TOUTFILE
    else
      ./content_updater.py --config=../ini/content_updater.ini < $TPOSTFILE
    fi

    if [ $REMOVE_TMP_FILES -ne 0 ]
    then
      rm -f $TFILE2
      rm -f $TOUTFILE
      if [ -f $TPOSTFILE ]
      then
        rm -f $TPOSTFILE
      fi
    fi
  fi
fi

if [ $REMOVE_TMP_FILES -ne 0 ]
then
  rm $TFILE
fi
