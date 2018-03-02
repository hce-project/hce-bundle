#!/bin/bash

. ../cfg/current_cfg.sh

#Check is instance already started
if [ $(./status.sh s) -gt 0 ]; then
  echo "Cluster [$NODE_APP_LOG_PREFIX] already started!"
  exit
fi

echo "Starting the $NODE_APP_LOG_PREFIX..."

#router node
. start_router.sh

#rmanager/smanager node
. start_shard_manager.sh

#Start manage replicas
. start_replicas_manage.sh

#Start pool replicas (searchers)
. start_replicas_pool.sh

sleep 1

echo "Started, schema:"
. schema_chart.sh s

#grep "READY" "$LOG_DIR"n000.log | wc -l
#grep "READY" "$LOG_DIR"n010.log | wc -l
