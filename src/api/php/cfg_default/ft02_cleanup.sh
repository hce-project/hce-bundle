#!/bin/bash

echo "" > $LOG_FILE

#Remove indexes at all nodes and start default_index usage
INDEX_NUMBER="$INDEX_START_NUMBER"
NODE_NUMBER=1
for NODE_ADMIN_PORT in "${REPLICAS_MANAGE_ADMIN_PORTS[@]}"
  do
    INDEX_NAME="$INDEX_NAME_TEMPLATE$INDEX_NUMBER"

    . "$MANAGE_DIR"icd_replicas_pool.sh $INDEX_NAME INDEX_DISCONNECT

    #New index stop
    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index stop $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STOP --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    #Remove index
    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT remove index $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REMOVE --name=$INDEX_NAME >> $LOG_FILE 2>&1

    echo "" >> $LOG_FILE

    ((INDEX_NUMBER++))
    ((NODE_NUMBER++))
  done
