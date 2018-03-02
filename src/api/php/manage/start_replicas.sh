#!/bin/bash

if [ "$1" = "" ]; then
  START_NODE_NUMBER=1
else
  START_NODE_NUMBER="$1"
fi

i="$START_NODE_NUMBER"
j=1
for NODE_ADMIN_PORT in "${REPLICAS_ADMIN_PORTS[@]}"
  do
    if [ "$USE_VALGRIND" = "0" ]; then
      VALGRIND=""
    else
      VALGRIND="$VALGRIND_COMMAND --log-file="$LOG_DIR$NODE_APP_LOG_PREFIX"1"$i"_data_val.log"
    fi

    if [ "$REPLICAS_TYPE" = "MANAGE" ]; then
      INI_FILE="$INI_FILE_MANAGE$i.ini"
      MANAGER_CONNECTION="0"
    else
      INI_FILE="$INI_FILE_POOL$j.ini"
      MANAGER_CONNECTION="tcp://$MANAGER:$SHARD_MANAGER_SERVER_PORT"
    fi

     $VALGRIND $NODE_BIN_NAME --role=replica --admin=tcp://*:$NODE_ADMIN_PORT --client=$MANAGER_CONNECTION --name="$NODE_APP_LOG_PREFIX"1"$i"_data --mode=$DATA_MODE --ini=$INI_DIR$INI_FILE --log=$LOGGER_INI > "$LOG_DIR$NODE_APP_LOG_PREFIX"1"$i"_data.out 2>&1 &

     sleep 1

    ((i++))
    ((j++))
 done
