#!/bin/bash

#echo "Site find" >> ../log/$0.log 2>&1
#../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_rnd.json >> ../log/$0.log

echo "Create new site Id not specified" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_NEW --file=../data/ftests/dcc_site_new_rnd_null_id.json" >> ../log/$0.log 2>&1

#echo "Site find" >> ../log/$0.log 2>&1
#../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_rnd.json >> ../log/$0.log

echo "Finished..." >> ../log/$0.log 2>&1
