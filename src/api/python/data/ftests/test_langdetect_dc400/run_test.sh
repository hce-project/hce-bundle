#!/bin/bash

BASEDIR=~/dts
BIN=${BASEDIR}/api/python/bin
MANAGE=${BASEDIR}/api/python/manage
TEST_DIR=${BASEDIR}/api/python/data/ftests/test_langdetect_dc400
HCE_BIN=${BASEDIR}/api/php/bin


# stop cluster
cd $MANAGE
#./dtm-daemon_stop.sh 
echo dtm-daemon stoped
#./dc-daemon_stop.sh
echo dc-daemon stoped

sleep 5

../ftests/clear_for_crawler_test.sh hc-user hc689

sleep 5

# start cluster
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

sleep 5

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN

NEW_SITE_FILES=$TEST_DIR/*.json

for f in $NEW_SITE_FILES
do
  echo $f
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f
done

#FIND_SITE_FILES=$TEST_DIR/site_find*.json

#for f in $FIND_SITE_FILES
#do
#  echo $f
#  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=$f
#done
