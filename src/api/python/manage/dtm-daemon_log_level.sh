#!/bin/bash

#Manage the logging level, values are: 10 - DEBUG, 20 - INFO, 30 - WARNING, 40 - ERROR, 50 - CRITICAL

CLASSES="AdminInterfaceServer,TasksDataManager,ResourcesManager,ResourcesStateMonitor,Scheduler,TasksManager,ExecutionEnvironmentManager,TasksExecutor,TasksStateUpdateService,ClientInterfaceService"
CONFIGVAR="LOG_LEVEL"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dtm-admin.ini --cmd="GET" --fields="$CONFIGVAR" --classes="$CLASSES" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dtm-admin.ini --cmd="SET" --fields="$CONFIGVAR:$1" --classes="$CLASSES" > ../log/$0.log
fi
