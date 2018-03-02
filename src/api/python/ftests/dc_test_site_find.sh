#!/bin/bash

#Create new site
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_find_site/dcc_site_new_jiji.json >> ../log/$0.log

#Let the site to be added
sleep 5

#Create new site
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_find_site/dcc_site_new_nikkei.json >> ../log/$0.log

#Let the site to be added
sleep 5

#Find site
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/test_find_site/dcc_site_find.json >> ../log/$0.log

