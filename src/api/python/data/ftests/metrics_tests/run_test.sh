#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
FTESTS=~/hce-node-bundle/api/python/ftests
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/metrics_tests
HCE_BIN=~/hce-node-bundle/api/php/bin


# stop cluster
cd $MANAGE
./dc-daemon_stop.sh -force
./dc-daemon-tasks-kill.sh
./dtm-daemon_stop.sh

sleep 5

# clear cluster
cd $HCE_BIN
cp $HCE_BIN/../cfg/current_cfg.sh ../cfg/current_cfg.sh.save

../manage/config.sh  m

JSON=$TEST_DIR/command.json
$HCE_BIN/drce.php --request=SET --host=localhost --port=5656 --n=1 --t=5000 --l=4 --json=$JSON

sleep 5

# start cluster
cd $MANAGE
./dtm-daemon_start.sh
./dc-daemon_start.sh

sleep 5

#change file permissions
#sudo chmod a+w -R /tmp/
#sudo chmod a+w -R ../

cd $BIN


  # delete site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rss.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rss.json

  # delete site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rss_feed.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rss_feed.json

  # delete site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rss_metric.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rss_metric.json

  # delete site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_rnd.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/dcc_site_delete_rnd.json

  # delete site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_jiji.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_jiji.json

  # delete site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_real-time.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$TEST_DIR/site_delete_real-time.json



  # new site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_rss.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_rss.json

  # new site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_rss_feed.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_rss_feed.json

  # new site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_rss_metric.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_rss_metric.json

  # new site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/dcc_site_new_ok_rnd.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/dcc_site_new_ok_rnd.json

  # new site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_jiji.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_jiji.json

  # new site
  echo ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_real-time.json
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$TEST_DIR/site_new_real-time.json




  # Activate site
  cd $FTESTS; ./dc_test_sites_active.sh