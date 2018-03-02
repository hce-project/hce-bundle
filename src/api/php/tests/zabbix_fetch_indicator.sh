#!/bin/bash

#Refresh properties json log
. ../manage/properties.sh

#Fetch requestsTotal property of Admin handler from node localhost:5541
../bin/zabbix_fetch_indicator.php --p="0->localhost:5530->DataProcessorData->drceDataStorageProperties->countSyncTasks" --l=zabbix_fetch_indicator.sh."$NODE_APP_LOG_PREFIX".log
echo ""
