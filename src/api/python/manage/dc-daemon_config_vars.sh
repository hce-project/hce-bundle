#!/bin/bash

SCRIPT_NAME=$(basename $0)
LOG="../log/$SCRIPT_NAME.log"

TEMPFILE=`mktemp /tmp/$SCRIPT_NAME.XXXXX`

if [ "$1" = "" ]
then
  CONFIG="../ini/dc-admin.ini"
  OUT=1
else
  CONFIG="$1"
  OUT=0
fi

if [[ ! -f $CONFIG ]]
then
    echo "ini file not found, exit"
    exit 1
fi

../bin/dtm-admin.py --config=$CONFIG --cmd="GET" --fields="*" --classes="AdminInterfaceServer,BatchTasksManager,BatchTasksManagerProcess,BatchTasksManagerRealTime,SitesManager" > $TEMPFILE

if [[ $OUT -eq 1 ]]
then
    cp $TEMPFILE $LOG
else
    cat $TEMPFILE
fi
