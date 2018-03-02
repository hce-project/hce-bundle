#!/bin/bash

../bin/dtm-admin.py -c ../ini/dtm-admin.ini --cmd GET --fields field101,field102 --classes TasksDataManager,Scheduler,TasksManager,TasksExecutor,ResourcesManager,ResorcesStateMonitor,ClientInterfaceService,ExecutionEnvironmentManager
sleep 5
../bin/dtm-admin.py -c ../ini/dtm-admin.ini --cmd SET --fields field101:val101 --classes TasksDataManager,Scheduler,TasksManager,TasksExecutor,ResourcesManager,ResorcesStateMonitor,ClientInterfaceService,ExecutionEnvironmentManager
sleep 5
../bin/dtm-admin.py -c ../ini/dtm-admin.ini --cmd GET --fields field101,field102 --classes TasksDataManager,Scheduler,TasksManager,TasksExecutor,ResourcesManager,ResorcesStateMonitor,ClientInterfaceService,ExecutionEnvironmentManager
sleep 5
../bin/dtm-admin.py -c ../ini/dtm-admin.ini --cmd SET --fields field102:val102 --classes TasksDataManager,Scheduler,TasksManager,TasksExecutor,ResourcesManager,ResorcesStateMonitor,ClientInterfaceService,ExecutionEnvironmentManager
sleep 5
../bin/dtm-admin.py -c ../ini/dtm-admin.ini --cmd GET --fields field101,field102 --classes TasksDataManager,Scheduler,TasksManager,TasksExecutor,ResourcesManager,ResorcesStateMonitor,ClientInterfaceService,ExecutionEnvironmentManager
