#!/bin/bash

echo "URLs content store for viewer" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_static.json" >> ../log/dcc_url_content_static.result.json 2>&1
echo "Get content to view tags" >> ../log/$0.log 2>&1
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../log/dcc_url_content_static.result.json > ../log/dcc_url_content_static.result.json.value

echo "Test fetch content automation script" > ../log/$0.log 2>&1
cd ../ftests && ./dc-kvdb-resource.sh b85ab149a528bd0a024fa0f43e80b5fc b85ab149a528bd0a024fa0f43e80b5fc >> ../log/$0.log 2>&1
