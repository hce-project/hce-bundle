#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/acceptance_tests/
HCE_BIN=~/hce-node-bundle/api/php/bin
WWW_DIR=$TEST_DIR/www/

# stop cluster
cd $MANAGE
./dc-daemon_stop.sh
./dtm-daemon_stop.sh 

sleep 5

# clear cluster
cd $HCE_BIN
cp $HCE_BIN/../cfg/current_cfg.sh ../cfg/current_cfg.sh.save

#echo #!/bin/bash > $HCE_BIN/../cfg/current_cfg.sh
#echo . ../cfg/c112_localhost_m0_cfg.sh >> $HCE_BIN/../cfg/current_cfg.sh
../manage/config.sh  m

JSON=$TEST_DIR/command.json
$HCE_BIN/drce.php --request=SET --host=localhost --port=5656 --n=1 --t=5000 --l=4 --json=$JSON

#cp $HCE_BIN/../cfg/current_cfg.sh.save ../cfg/current_cfg.sh
#rm $HCE_BIN/../cfg/current_cfg.sh.save

sleep 5

# start cluster
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

sleep 5

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../


#cd $WWW_DIR
#/usr/bin/python -m SimpleHTTPServer &

cd $BIN


NEW_SITE_FILES=$TEST_DIR/site_new_japan.json
for f in $NEW_SITE_FILES
do
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f
done