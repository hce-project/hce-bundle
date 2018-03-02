#!/bin/bash

. ../cfg/current_cfg.sh

DATA_DIR=$DATA_DIR"c112_localhost_ft02/"
DATA_FILE_PATTERN="^.*_branch.*\.xml$"

NODE_HOST="$HOST"

SCHEMA_FILE=$DATA_DIR"_schema.xml"
LOG_FILE=$LOG_DIR$0"."$NODE_APP_LOG_PREFIX".log"

SEARCH_STRING=""
SEARCH_TEST_NAME="$BIN_DIR$SEARCH_COMMAND --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=10 --l=0 --q="

INDEX_START_NUMBER=3
INDEX_NAME_TEMPLATE="c112_ft02_00"

BRANCH_TEMPLATE="b"
BRANCH_MIN_NUMBER=0

SMALL_TIMEOUT=10000
BIG_TIMEOUT=120000

echo "Please, be patient while test in progress..."

. ../cfg/ft02.sh
