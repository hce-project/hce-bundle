#!/bin/bash

cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=../data/ftests/test_tidy/dcc_site_new_ok.json
echo ">>> Sleep for a few minutes"
sleep $1
cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=URL_CONTENT --file=../data/ftests/test_tidy/dcc_url_content_ok.json > ../data/ftests/test_tidy/temp1.json
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:rawContents:0:buffer" -b 1 < ../data/ftests/test_tidy/temp1.json > ../data/ftests/test_tidy/temp2.json
var1="$(cd ../data/ftests/test_tidy && grep "heading1" -A 1 ./temp2.json | grep "</h1>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"heading1\" tidy NOT FIXED"
else
    echo ">>> OK \"heading1\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "</b> <i>bold?</i>" ./temp2.json | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"bold?\" tidy NOT FIXED"
else
    echo ">>> OK \"bold?\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "heading3</i>" -A 1 ./temp2.json | grep "</h1>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"heading3\" tidy NOT FIXED"
else
    echo ">>> OK \"heading3\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "heading4</i>" -A 1 ./temp2.json | grep "</h1>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"heading4\" tidy NOT FIXED"
else
    echo ">>> OK \"heading4\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "bold text</b>" -A 1 ./temp2.json | grep "</p>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"bold text\" tidy NOT FIXED"
else
    echo ">>> OK \"bold text\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "heading5" -A 1 ./temp2.json | grep "</h1>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"heading5\" tidy NOT FIXED"
else
    echo ">>> OK \"heading5\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "<b>sub</b>" -A 1 ./temp2.json | grep "</h2>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"sub\" tidy NOT FIXED"
else
    echo ">>> OK \"sub\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "heading6" -A 1 ./temp2.json | grep "</h2>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"heading6\" tidy NOT FIXED"
else
    echo ">>> OK \"heading6\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "1st list item</b>" -A 1 ./temp2.json | grep "</li>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"1st list item\" tidy NOT FIXED"
else
    echo ">>> OK \"1st list item\" tidy FIXED"
fi

var1="$(cd ../data/ftests/test_tidy && grep "2nd list item</b>" -A 1 ./temp2.json | grep "</li>" | wc -l)"
if [ $var1 = "0" ]
then
    echo ">>> ERROR \"2nd list item</b>\" tidy NOT FIXED"
else
    echo ">>> OK \"2nd list item</b>\" tidy FIXED"
fi