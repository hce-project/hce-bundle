#!/bin/bash

. ../cfg/current_cfg.sh

QUERIES=10
CLIENTS=4
TIMEOUT=60000000
LOG_LEVEL=0

if [ "$1" = "" ]; then
  TEST_FILE="binarytrees.gcc-7.c.00.txt"
else
  TEST_FILE="$1"
fi

DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR2/$TEST_FILE"

LOG_FILE_TEMPLATE="drce_test2_client."

killall $DRCE_COMMAND

rm "$LOG_DIR$LOG_FILE_TEMPLATE"*.log

. ../cfg/drce_test_multiclient.sh
