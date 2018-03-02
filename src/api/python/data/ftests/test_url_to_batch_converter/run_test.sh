#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEMPLATES=~/hce-node-bundle/api/python/data/ftests/templates
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_url_to_batch_converter
HCE_BIN=~/hce-node-bundle/api/php/bin


## start cluster
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

#add site
cd $BIN
cat $TEST_DIR/url_fetch.json | ./url_fetch_json_to_db-task_convertor.py -c ../ini/url_fetch_json_to_db_task_convertor.ini | ./urls-to-batch-task.py -c ../ini/urls-to-batch-task.ini  | ./processor-task.py --config=../ini/processor-task.ini
