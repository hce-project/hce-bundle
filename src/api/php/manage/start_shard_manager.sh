#!/bin/bash

. ../cfg/current_cfg.sh

START_NODE_NUMBER="$1"

if [ "$START_NODE_NUMBER" == "" ]
then
  START_NODE_NUMBER="1"
fi

if [ "$USE_VALGRIND" = "0" ]; then
  VALGRIND=""
else
  VALGRIND="$VALGRIND_COMMAND --log-file="$LOG_DIR$NODE_APP_LOG_PREFIX"10_manager_val.log"
fi

INI_FILE="$INI_FILE_MANAGE$START_NODE_NUMBER.ini"

$VALGRIND $NODE_BIN_NAME --role=$MANAGER_MODE --admin=tcp://*:$SHARD_MANAGER_ADMIN_PORT --server=tcp://*:$SHARD_MANAGER_SERVER_PORT --client=tcp://$ROUTER:$ROUTER_SERVER_PORT --name="$NODE_APP_LOG_PREFIX"10_manager --mode=$DATA_MODE --ini=$INI_DIR$INI_FILE --log=$LOGGER_INI > "$LOG_DIR$NODE_APP_LOG_PREFIX"10_manager.out 2>&1 &
