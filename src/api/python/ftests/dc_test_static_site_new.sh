#!/bin/bash

echo "Site find" >> ../log/$0.log 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_static.json >> ../log/$0.log

echo "Delete site" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_DELETE --file=../data/ftests/dcc_site_delete_static.json" >> ../log/$0.log 2>&1

echo "Create new site" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_NEW --file=../data/ftests/dcc_site_new_ok_static.json" >> ../log/$0.log 2>&1

echo "Site find" >> ../log/$0.log 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_static.json >> ../log/$0.log

echo "Check site status before crawling" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_static.json" >> ../log/$0.log 2>&1

echo "Finished..." >> ../log/$0.log 2>&1
