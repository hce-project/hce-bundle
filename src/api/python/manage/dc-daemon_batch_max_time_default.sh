#!/bin/bash

#Manage the batch max tasks in queue

CLASSES="BatchTasksManager"
CONFIGVAR="BatchDefaultMaxExecutionTime"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONFIGVAR" --classes="$CLASSES" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONFIGVAR:$1" --classes="$CLASSES" > ../log/$0.log
fi
