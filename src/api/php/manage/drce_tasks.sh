#!/bin/bash

. ../cfg/current_cfg.sh

LOG_OUT="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.log"

$BIN_DIR$MANAGER_COMMAND --command=DRCE_GET_TASKS --host=$HOST --port=$REPLICA_ADMIN_PORTS_CSV --timeout=$SMALL_TIMEOUT > $LOG_OUT 2>&1
