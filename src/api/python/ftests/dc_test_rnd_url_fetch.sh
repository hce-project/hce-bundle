#!/bin/bash

echo "URL Fetch" > ../log/$0.log 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=URL_FETCH --file=../data/ftests/dcc_url_fetch_rnd.json >> ../log/$0.log
