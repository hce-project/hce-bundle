#!/bin/bash

. ../cfg/current_cfg.sh

#Check is instance already started
if [ $(./status.sh s) -lt 1 ]; then
  echo "Cluster [$NODE_APP_LOG_PREFIX] not started!"
  exit
fi

LOG_OUT="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.log"

#echo "cleanup all tests"
#. ft01_cleanup.sh
#. ft02_cleanup.sh

echo "Trying to stop nodes of $NODE_APP_LOG_PREFIX..."

echo "[" > $LOG_OUT 2>&1

#Stop replicas
. stop_replicas.sh >> $LOG_OUT 2>&1

echo "," >> $LOG_OUT 2>&1

#Stop rmanager
. stop_shard_manager.sh >> $LOG_OUT 2>&1

echo "," >> $LOG_OUT 2>&1

#Stop router
. stop_router.sh >> $LOG_OUT 2>&1

echo "]" >> $LOG_OUT 2>&1

echo "Finished."

#echo "status:"
#. status.sh
