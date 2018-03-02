#!/bin/bash

echo "Execute batch" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=BATCH --file=../data/ftests/dcc_site_batch_rss.json" > ../log/dcc_site_batch_rss.json.result.json 2>&1

echo "Get content to view tags" >> ../log/$0.log 2>&1
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../log/dcc_site_batch_rss.json.result.json > ../log/dcc_site_batch_rss.json.result.json.value
