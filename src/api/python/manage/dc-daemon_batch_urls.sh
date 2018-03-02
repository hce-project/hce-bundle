#!/bin/bash

#Manage the batch urls number, value multiplied on nodes number in m-type cluster

CLASSES="BatchTasksManager"
CONFIGVAR="BatchDefaultMaxURLs"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONFIGVAR" --classes="$CLASSES" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONFIGVAR:$1" --classes="$CLASSES" > ../log/$0.log
fi
