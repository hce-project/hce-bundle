#!/bin/bash

. ./dc_test_rss_sites_cfg.sh

for SITE_NAME in "${SITES_LIST[@]}"
  do
    echo "Site:$SITE_NAME" >> ../log/$0.log 2>&1
    echo "Site find:""$DATA_DIR""dcc_site_find_""$SITE_NAME"".json" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file="$DATA_DIR""dcc_site_find_""$SITE_NAME"".json" >> ../log/$0.log

    echo "Delete site" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file="$DATA_DIR""dcc_site_delete_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

    echo "Create new site" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file="$DATA_DIR""dcc_site_new_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

    echo "Site find" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file="$DATA_DIR""dcc_site_find_""$SITE_NAME"".json" >> ../log/$0.log

    echo "Check site status before crawling" >> ../log/$0.log 2>&1
    ../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_STATUS --file="$DATA_DIR""dcc_site_status_""$SITE_NAME"".json" >> ../log/$0.log 2>&1

  done
