#!/bin/bash

. ../cfg/current_cfg.sh

QUERIES=10000
RESULTS=10
CLIENTS=8
TIMEOUT=5000
LOG_LEVEL=0
SEARCH_STRING="for"


LOG_FILE_TEMPLATE="search_client."

if [ "$1" = "" ]; then
  QUERY_STRING="$SEARCH_STRING"
else
  QUERY_STRING="$1"
fi

#if [ "$2" = "" ]; then
#  FILTERS="0,mmedia,0,0;3,afflags0,4,16,0;3,afflags0ex,8,0"
#else
  FILTERS="$2"
#fi

killall $SEARCH_COMMAND

rm "$LOG_DIR$LOG_FILE_TEMPLATE"*.log

. ../cfg/search_test_multiclient.sh
