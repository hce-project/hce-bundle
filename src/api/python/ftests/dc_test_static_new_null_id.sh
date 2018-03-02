#!/bin/bash

echo "Create new site Id not specified" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_NEW --file=../data/ftests/dcc_site_new_static_null_id.json" >> ../log/$0.log 2>&1

echo "Finished..." >> ../log/$0.log 2>&1
