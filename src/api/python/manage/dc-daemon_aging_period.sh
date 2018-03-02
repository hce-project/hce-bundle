#!/bin/bash

CONGIFVAR="AgingPeriod"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONGIFVAR" --classes="BatchTasksManager" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONGIFVAR:$1" --classes="BatchTasksManager" > ../log/$0.log
fi
