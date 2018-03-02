#!/bin/bash

for (( i=1; i<=CLIENTS; i++ ))
  do
    nohup $BIN_DIR$SEARCH_COMMAND --q="$QUERY_STRING" --l=$LOG_LEVEL --host=$ROUTER --port=$ROUTER_CLIENT_PORT --r=$RESULTS --f=\"$FILTERS\" --n=$QUERIES --t=$TIMEOUT > "$LOG_DIR$LOG_FILE_TEMPLATE$i"."$NODE_APP_LOG_PREFIX".log &
    sleep 2
  done

echo $CLIENTS started each $QUERIES per $RESULTS

sleep 1

top