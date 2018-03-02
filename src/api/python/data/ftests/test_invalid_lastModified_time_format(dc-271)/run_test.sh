#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_invalid_lastModified_time_format\(dc-271\)
HCE_BIN=~/hce-node-bundle/api/php/bin


# stop cluster
cd $MANAGE
./dtm-daemon_stop.sh 
./dc-daemon_stop.sh

sleep 5

# clear cluster
#cd $HCE_BIN
#cp $HCE_BIN/../cfg/current_cfg.sh ../cfg/current_cfg.sh.save

#echo #!/bin/bash > $HCE_BIN/../cfg/current_cfg.sh
#echo . ../cfg/c112_localhost_m0_cfg.sh >> $HCE_BIN/../cfg/current_cfg.sh

#./drce.php --request=SET --host=localhost --port=5656 --n=1 --t=2000 --l=4 --json=$TEST_DIR/test.txt

#cp $HCE_BIN/../cfg/current_cfg.sh.save ../cfg/current_cfg.sh
#rm $HCE_BIN/../cfg/current_cfg.sh.save

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

NEW_SITE_FILES=$TEST_DIR/site_new*.json

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
