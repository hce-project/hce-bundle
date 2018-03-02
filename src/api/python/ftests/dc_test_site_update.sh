#!/bin/bash

. ./dc_test_site_update_cfg.sh

for SITE_NAME in "${SITES_LIST[@]}"
  do
    echo "Site:$SITE_NAME" >> ../log/$0.log 2>&1
    echo "Check site status before update" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file="$DATA_DIR""site_status_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

    echo "Update site by $DATA_DIR""site_update_""$SITE_NAME"".json" >> ../log/$0.log 2>&1
    #../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE --file="$DATA_DIR""site_update_""$SITE_NAME"".json" --fields='{"updateType":2,"state":3,"properties":{"PROCESS_CTYPES":"text/html,text/xml","STORE_HTTP_REQUEST":"0","STORE_HTTP_HEADERS":"0","template":"file://../data/ftests/test_10_site_snatz/templates/afpbb.txt"}}' >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE --fields='{"id": "afe3b4bc8af61fa95d67f62122d55d04","updateType":2,"state":2,"properties":{"PROCESS_CTYPES":"text/html,text/xml","STORE_HTTP_REQUEST":"0","STORE_HTTP_HEADERS":"0","template":"file://../data/ftests/test_10_site_snatz/templates/afpbb.txt"}}' >> ../log/$0.log 2>&1

    echo "Check site status after update" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file="$DATA_DIR""site_status_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

  done
