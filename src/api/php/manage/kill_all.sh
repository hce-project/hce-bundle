#!/bin/bash

. ../cfg/current_cfg.sh

#Check is instance already started
if [ $(./status.sh s) -lt 1 ]; then
  echo "Cluster [$NODE_APP_LOG_PREFIX] not started!"
  exit
fi

LOG_OUT="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.log"

echo "Trying to kill nodes of '$NODE_APP_LOG_PREFIX'..."

CMD1="kill -9 \`ps ax | awk '/${NODE_BIN_NAME//\//\\/}(.*)$NODE_APP_LOG_PREFIX/ { print \$1 }'\`"
eval $CMD1 >> $LOG_OUT 2>&1

echo "Finished."
