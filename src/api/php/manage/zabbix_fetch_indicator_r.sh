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

cd /home/$USER/hce-node-bundle/api/php/manage

. ../cfg/c112_localhost_r0_cfg.sh

DATA_JSON="zabbix_fetch_indicator.sh.$NODE_APP_LOG_PREFIX.log"

if [ "$3" == "1" ]; then
  #Refresh properties json log
  ./properties.sh outFile="$LOG_DIR""$DATA_JSON".tmp cfgFile="../cfg/c112_localhost_r0_cfg.sh"
  #mv "$LOG_DIR"properties.sh."$NODE_APP_LOG_PREFIX".log "$LOG_DIR""$DATA_JSON"
  if [ -s "$LOG_DIR""$DATA_JSON".tmp ]
  then
    mv "$LOG_DIR""$DATA_JSON".tmp "$LOG_DIR""$DATA_JSON"
  fi
fi

#Fetch requestsTotal property of Admin handler from node localhost:5541
../bin/zabbix_fetch_indicator.php --p="0$DELIMITER$1" --l="$DATA_JSON" --d="$DELIMITER"
