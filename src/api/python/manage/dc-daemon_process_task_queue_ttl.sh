#!/bin/bash

#Manage max process crawling tasks in queue

CLASSES="BatchTasksManagerProcess"
CONFIGVAR="BatchQueueTaskTTL"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONFIGVAR" --classes="$CLASSES" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONFIGVAR:$1" --classes="$CLASSES" > ../log/$0.log
fi
