#!/bin/bash

. ../cfg/current_cfg.sh

LOG_FILE="$LOG_DIR$0"."$NODE_APP_LOG_PREFIX".log

SCHEMA_FILE=$DATA_DIR"c112_ft01_schema.xml"
SCHEMA_FILE_BAD=$DATA_DIR"c112_ft01_schema_bad.xml"

SEARCH_STRING="post|website"
SEARCH_TEST_NAME="$BIN_DIR$SEARCH_COMMAND --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=100 --l=0 --q="

BIG_TIMEOUT=20000000
SMALL_TIMEOUT=10000

INDEX_START_NUMBER=1
INDEX_NAME_TEMPLATE="c112_ft01_00"

echo "Please, be patient while test in progress..."

. ../cfg/ft01.sh

echo "Finished."
