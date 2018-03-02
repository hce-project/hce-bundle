#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=4

DRCE_TESTS_NUMBERS=( 00 01 03 04 05 06 07 08 09 10 )
DRCE_TEST_JSON_FILE="$DATA_DIR$DRCE_DATA_DIR1/c112_localhost_drce_json"

echo "Please, be patient while test in progress..."

echo "" > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
for TEST_NUMBER in "${DRCE_TESTS_NUMBERS[@]}"
  do
    echo "TEST $TEST_NUMBER started -----------------------------------" >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    $BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE$TEST_NUMBER.txt >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    echo "TEST $TEST_NUMBER finished ----------------------------------" >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    echo "" >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
  done


