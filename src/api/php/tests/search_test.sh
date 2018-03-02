#!/bin/bash

. ../cfg/current_cfg.sh

SEARCH_STRING="for"
REQUESTS=1000
RESULTS=10
LOG_LEVEL=0

if [ "$1" = "" ]; then
  QS="$SEARCH_STRING"
else
  QS="$1"
fi

echo "Please, be patient while test in progress..."

$BIN_DIR$SEARCH_COMMAND --host=$ROUTER --port=$ROUTER_CLIENT_PORT --q="$QS" --n=$REQUESTS --r=$RESULTS --t=$BIG_TIMEOUT --l=$LOG_LEVEL --sphinx_timeout=$SEARCH_SPHINX_TIMEOUT > $LOG_DIR$0."$NODE_APP_LOG_PREFIX".log
