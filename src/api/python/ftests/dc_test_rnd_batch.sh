#!/bin/bash

echo "URLs content store for viewer" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_rnd.json" >> ../log/dcc_url_content_rnd.result.json 2>&1
../manage/dc-client_start.sh "--command=BATCH --file=../data/ftests/dcc_site_batch.json" >> ../log/dcc_site_batch.json.result.json 2>&1

echo "Get content to view tags" >> ../log/$0.log 2>&1
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../log/dcc_site_batch.json.result.json > ../log/dcc_site_batch.json.result.json.value
