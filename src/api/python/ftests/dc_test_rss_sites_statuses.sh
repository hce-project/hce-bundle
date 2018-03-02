#!/bin/bash

. ./dc_test_rss_sites_cfg_snatz.sh

for SITE_NAME in "${SITES_LIST[@]}"
  do
    echo "Site:$SITE_NAME" >> ../log/$0.log 2>&1
    echo "Check site status" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file="$DATA_DIR""dcc_site_status_""$SITE_NAME"".json" >> ../log/$0.log 2>&1
  done
