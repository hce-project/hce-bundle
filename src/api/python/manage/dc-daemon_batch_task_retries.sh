#!/bin/bash

#Manage max batch crawling tasks in queue

CLASSES="BatchTasksManager"
CONFIGVAR="BatchTask_RETRY"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONFIGVAR" --classes="$CLASSES" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONFIGVAR:$1" --classes="$CLASSES" > ../log/$0.log
fi
