#!/bin/bash

if [ $# -lt 2 ]
  then
    echo "No Site_Id and URL_Id specified by first and second arguments!"
    exit
fi

REQUEST_JSON="../log/dcc_url_content_$1_$2.result.json"

#Make URL_CONTENT request json
echo "[{\"contentTypeMask\": 3, \"siteId\": \"$1\", \"url\": \"\", \"urlMd5\": \"$2\"}]" > "$REQUEST_JSON"

#URLs content store for viewer
../manage/dc-client_start.sh "--command=URL_CONTENT --file=$REQUEST_JSON" > "$REQUEST_JSON.result.json" 2>&1

#Get content to view tags
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < "$REQUEST_JSON.result.json" >  "$REQUEST_JSON.result.json.value.buffer"
cd ../bin && ./json-field.py -f "default" < "$REQUEST_JSON.result.json.value.buffer" >  "$REQUEST_JSON.result.json.value"
