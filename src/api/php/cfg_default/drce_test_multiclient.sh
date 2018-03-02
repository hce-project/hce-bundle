#!/bin/bash

for (( i=1; i<=CLIENTS; i++ ))
  do
    nohup $BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$TIMEOUT --n=$QUERIES --l=$LOG_LEVEL --json=$DRCE_TEST_JSON_FILE > "$LOG_DIR$LOG_FILE_TEMPLATE$i"."$NODE_APP_LOG_PREFIX".log &
    sleep 2
  done

echo $CLIENTS started each $QUERIES per $RESULTS

sleep 1

top