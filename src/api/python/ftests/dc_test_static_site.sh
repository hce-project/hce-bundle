#!/bin/bash

#Remove log files
rm ../log/*
echo "" > ../log/$0.log 2>&1

#Before actions
./dc_tests_before.sh

sleep 2

echo "Site find" >> ../log/$0.log 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_static.json >> ../log/$0.log

echo "Delete site" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_DELETE --file=../data/ftests/dcc_site_delete_static.json" >> ../log/$0.log 2>&1

echo "Create new site" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_NEW --file=../data/ftests/dcc_site_new_ok_static.json" >> ../log/$0.log 2>&1

echo "Site find" >> ../log/$0.log 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_static.json >> ../log/$0.log

echo "Check site status before crawling" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_static.json" >> ../log/$0.log 2>&1

echo "Add new URL" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_NEW --file=../data/ftests/dcc_url_new_static.json" >> ../log/$0.log 2>&1

echo "Check URLs status before crawling" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_STATUS --file=../data/ftests/dcc_url_status_static.json" >> ../log/$0.log 2>&1

echo "Crawling started at:" >> ../log/$0.log 2>&1
date >> ../log/$0.log 2>&1

echo "Sleep 80 sec" >> ../log/$0.log 2>&1
sleep 80

echo "Crawling finished 1 at:" >> ../log/$0.log 2>&1
date >> ../log/$0.log 2>&1

echo "Check sites status after crawling" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_static.json" >> ../log/$0.log 2>&1

echo "Check URLs status after crawling" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_STATUS --file=../data/ftests/dcc_url_status_static.json" >> ../log/$0.log 2>&1

echo "Get data of URL" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_static.json" >> ../log/$0.log 2>&1

#echo "Cleanup sites data" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=SITE_CLEANUP --file=../data/ftests/dcc_site_cleanup_static.json" >> ../log/$0.log 2>&1

#echo "Update site" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=SITE_UPDATE --file=../data/ftests/dcc_site_update_static.json" >> ../log/$0.log 2>&1

#echo "Check sites status after update" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_static.json" >> ../log/$0.log 2>&1

#echo "Update URL" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=URL_UPDATE --file=../data/ftests/dcc_url_update_static.json" >> ../log/$0.log 2>&1

#echo "Crawling started at:" >> ../log/$0.log 2>&1
#date >> ../log/$0.log 2>&1

#echo "Sleep 60 sec" >> ../log/$0.log 2>&1
#sleep 60

#echo "Crawling finished 2 at:" >> ../log/$0.log 2>&1
#date >> ../log/$0.log 2>&1

#echo "Check sites status after crawling" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_static.json" >> ../log/$0.log 2>&1

echo "Get URL content before delete" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_static.json" >> ../log/$0.log 2>&1

echo "Delete URLs and resources crawled" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_DELETE --file=../data/ftests/dcc_url_delete_static.json" >> ../log/$0.log 2>&1

echo "Get URL content after delete" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_static.json" >> ../log/$0.log 2>&1

echo "URLs content store for viewer" >> ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_static.json" >> ../log/dcc_url_content_static.result.json 2>&1
echo "Get content to view tags" >> ../log/$0.log 2>&1
cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < ../log/dcc_url_content_static.result.json > ../log/dcc_url_content_static.result.json.value

echo "Test fetch content automation script" >> ../log/$0.log 2>&1
#cd ../ftests && ./dc-kvdb-resource.sh 699fcf4591fc23e79b839d8819904293 699fcf4591fc23e79b839d8819904293 >> ../log/$0.log 2>&1
cd ../ftests && ./dc-kvdb-resource.sh b85ab149a528bd0a024fa0f43e80b5fc b85ab149a528bd0a024fa0f43e80b5fc >> ../log/$0.log 2>&1

#echo "Delete site" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=SITE_DELETE --file=../data/ftests/dcc_site_delete_static.json" >> ../log/$0.log 2>&1

#echo "Check sites status after delete" >> ../log/$0.log 2>&1
#../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_static.json" >> ../log/$0.log 2>&1


#echo "After tests cleaning..." >> ../log/$0.log 2>&1

#After actions
#./dc_tests_after.sh

echo "Finished..." >> ../log/$0.log 2>&1
