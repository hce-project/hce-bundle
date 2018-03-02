#!/bin/bash

echo "Site find" > ../log/$0.log 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_rnd.json >> ../log/$0.log
