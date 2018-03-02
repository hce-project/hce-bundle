#!/bin/bash

. ./dc_test_japan_sites_cfg.sh

for SITE_NAME in "${SITES_LIST[@]}"
  do
    echo "Site:$SITE_NAME" >> ../log/$0.log 2>&1
    echo "Check site status before update" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file="$DATA_DIR""dcc_site_status_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

    echo "Update site by $DATA_DIR""site_update_""$SITE_NAME"".json" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE --file="$DATA_DIR""dcc_site_update_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

    echo "Check site status after update" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file="$DATA_DIR""dcc_site_status_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

  done