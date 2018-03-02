#!/bin/bash

INDEX_NAME="$1"
OPERATION="$2"

. ../cfg/current_cfg.sh

if [ "$LOG_FILE" = "" ]; then
  LOG_FILE="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.log"
fi

if [ "$INDEX_NAME" = "" ]; then
  echo "Index name not specified!"
  exit 1
fi

if [ "$OPERATION" = "" ]; then
  echo "Operation not specified!"
  exit 1
fi

for NODE_ADMIN_PORT1 in "${REPLICAS_POOL_ADMIN_PORTS[@]}"
  do
      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT1 $OPERATION to index $INDEX_NAME": >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$NODE_ADMIN_PORT1 --command=$OPERATION --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1
  done
