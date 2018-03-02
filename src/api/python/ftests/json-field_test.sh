#!/bin/bash

cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../data/ftests/dcc_url_content_rnd.result.json > ../log/$0.value
