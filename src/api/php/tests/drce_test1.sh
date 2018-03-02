#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=3

if [ "$1" = "" ]; then
  TEST_NUMBER="00"
else
  TEST_NUMBER="$1"
fi

DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR1/c112_localhost_drce_json$TEST_NUMBER.txt"

$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE --cover=0 > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
