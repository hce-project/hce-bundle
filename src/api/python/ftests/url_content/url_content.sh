#!/bin/bash

cd ../ && ../manage/dc-client_start.sh "--command=URL_CONTENT --file=../ftests/url_content/url_content.json" > ../ftests/url_content/url_content.result.json
cd url_content
cd ../ && ../bin/json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../ftests/url_content/url_content.result.json > ../ftests/url_content/url_content.result.decoded.json
