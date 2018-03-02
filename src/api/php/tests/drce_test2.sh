#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=4
#1000 min timeout
TIMEOUT="60000000"

if [ "$1" = "" ]; then
  TEST_FILE="binarytrees.gcc-7.c.00.txt"
else
  TEST_FILE="$1"
fi

DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR2/$TEST_FILE"

$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$TIMEOUT --l=$LOG_LEVEL --json="$DRCE_TEST_JSON_FILE" > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
