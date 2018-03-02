#!/bin/bash

. ../cfg/current_cfg.sh

LOG_FILE=$LOG_DIR$0"."$NODE_APP_LOG_PREFIX".log"

BIG_TIMEOUT=20000000
SMALL_TIMEOUT=10000

INDEX_START_NUMBER=1
INDEX_NAME_TEMPLATE="c112_ft01_00"

echo "Please, be patient while action in progress..."

. ../cfg/ft01_cleanup.sh

echo "Finished."