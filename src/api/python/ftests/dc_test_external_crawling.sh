#!/bin/bash

cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_external_crawling_dc_297/site_new_$2.json
#cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=../data/ftests/test_external_crawling_dc_297/site_delete_$2.json
echo ">>> Sleep for a 20 minutes"
sleep $1
cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=URL_CONTENT --file=../data/ftests/test_external_crawling_dc_297/site_content_$2.json > ../data/ftests/test_external_crawling_dc_297/save1.json
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../data/ftests/test_external_crawling_dc_297/save1.json > ../data/ftests/test_external_crawling_dc_297/save2.json
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:rawContents:0:buffer" -b 1 < ../data/ftests/test_external_crawling_dc_297/save1.json > ../data/ftests/test_external_crawling_dc_297/save3.json
