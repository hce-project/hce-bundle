#!/bin/bash

echo "Update site state to suspended" > ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_UPDATE --file=../data/ftests/dcc_site_update_static_disabled.json" > ../log/$0.log 2>&1
