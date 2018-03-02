#!/bin/bash

cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_dynamic_java_script/dcc_site_new_ok.json
echo ">>> Sleep for a 20 minutes"
sleep $1
cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=URL_CONTENT --file=../data/ftests/test_dynamic_java_script/dcc_url_content_ok.json > ../data/ftests/test_dynamic_java_script/temp1.json
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:rawContents:0:buffer" -b 1 < ../data/ftests/test_dynamic_java_script/temp1.json > ../data/ftests/test_dynamic_java_script/temp2.json
var1="$(cd ../data/ftests/test_dynamic_java_script && grep -o "Sign In" /temp2.json | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> \"Sign In\" not found in dynamic content"
else
    echo ">>> \"Sign In\" found in dynamic content"
fi