#!/bin/bash

SCRIPTS2KILL='crawler-task.py;db-task.py;processor-task.py;scraper.py'
OPTIONS='test'

PHPPATH=~/hce-node-bundle/api/php/manage/
PYTHONPATH=~/hce-node-bundle/api/python/manage/
BINPATH=~/hce-node-bundle/usr/bin/
JSONPATH=~/hce-node-bundle/api/php/data/manage/

KILLSCRIPT=kill-process-by-name.sh
JSONFILE=dc-daemon-task-kill.json

REQUESTS=1
LOG_LEVEL=3
LOG_FILE=$0
JSON_TMP_DIR='/tmp/'
JSON_TMP_FILE=$0'.tmp.json'

cd $PHPPATH
. ./config.sh m
. ./../cfg/current_cfg.sh

. ./kill-process-m.sh -o $OPTIONS -s $SCRIPTS2KILL

. ./config.sh n

rm -f $JSON_TMP_DIR$JSON_TMP_FILE

exit 0
