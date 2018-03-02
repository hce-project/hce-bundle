#!/bin/bash

echo "Check site status before crawling" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_rnd.json" >> ../log/$0.log 2>&1
