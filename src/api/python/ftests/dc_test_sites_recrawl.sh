#!/bin/bash

echo "Update all sites state to recrawl now" > ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_UPDATE --file=../data/ftests/dcc_sites_update_recrawl_now.json" > ../log/$0.log 2>&1
