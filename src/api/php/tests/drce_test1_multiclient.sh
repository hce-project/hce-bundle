#!/bin/bash

. ../cfg/current_cfg.sh

QUERIES=1000
CLIENTS=4
TIMEOUT=5000
LOG_LEVEL=0

if [ "$1" = "" ]; then
  TEST_NUMBER="00"
else
  TEST_NUMBER="$1"
fi

DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR1/c112_localhost_drce_json$TEST_NUMBER.txt"

LOG_FILE_TEMPLATE="drce_test1_client."

killall $DRCE_COMMAND

rm "$LOG_DIR$LOG_FILE_TEMPLATE"*.log

. ../cfg/drce_test_multiclient.sh
