#!/bin/bash

if [ "$1" == "" ]; then
  echo "First argument required to get indicator, for example: localhost:5530->DataProcessorData->drceDataStorageProperties->countSyncTasks"
  echo "Second argument is user name to get path"
  echo "Third argument is bool 1 - means renew data file"
  exit
fi

if [ "$2" == "" ]; then
  USER="$USER"
else
  USER="$2"
fi

if [ "$4" == "" ]; then
  DELIMITER="->"
else
  DELIMITER="$4"
fi

OUT_FILE="${0##*/}.log"

cd /home/$USER/hce-node-bundle/api/python/manage

if [ "$3" == "1" ]; then
  #Refresh properties json log
  ./dtm-daemon_status.sh
  if [ -s "../../python/log/dtm-daemon_status.sh.log" ]
  then
    cp "../../python/log/dtm-daemon_status.sh.log" "../../python/log/$OUT_FILE"
  fi
fi

#Replace some prefixes
KEY="$1"
ITEM=0
namesSrc=( "AdminInterfaceServer" "TasksDataManager" "ResourcesManager" "ResourcesStateMonitor" "Scheduler" "TasksManager" "ExecutionEnvironmentManager" "TasksExecutor" "TasksStateUpdateService" "ClientInterfaceService" )
for name in ${namesSrc[*]}
do
  if [[ "$1" == *"$name$DELIMITER"* ]]
    then
    KEY=${KEY/$name/0\%$ITEM\%0\%fields}
    #echo "It's there!"
    #echo "$KEY"
    break
  fi
  ((ITEM++))
done
#exit

#Fetch requestsTotal property of Admin handler from node localhost:5541
cd /home/$USER/hce-node-bundle/api/php/bin
./zabbix_fetch_indicator.php --p="$KEY" --l="../../python/log/$OUT_FILE" --d="$DELIMITER"
