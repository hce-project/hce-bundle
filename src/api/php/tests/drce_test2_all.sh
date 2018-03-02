#!/bin/bash

. ../cfg/current_cfg.sh

REQUESTS=1
LOG_LEVEL=4
TIMEOUT="60000000"

DRCE_TEST2_FILE_PATTERN="^.*\.txt$"

echo "Please, be patient while test in progress..."

#collect list of request files in to the array
DRCE_TESTS_FILES=($(find "$DATA_DIR$DRCE_DATA_DIR2" -type f -regex "$DRCE_TEST2_FILE_PATTERN"))

echo "" > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
for TEST_FILE in "${DRCE_TESTS_FILES[@]}"
  do
    echo "TEST $TEST_FILE started -----------------------------------" >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    $BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$TIMEOUT --l=$LOG_LEVEL --json=$TEST_FILE >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    echo "TEST $TEST_FILE finished ----------------------------------" >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    echo "" >> $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
  done
