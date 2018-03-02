#!/bin/bash

CONGIFVAR="MaxThreads"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONGIFVAR" --classes="BatchTasksManagerRealTime" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONGIFVAR:$1" --classes="BatchTasksManagerRealTime" > ../log/$0.log
fi
