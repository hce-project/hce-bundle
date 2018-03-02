#!/bin/bash

. ../cfg/current_cfg.sh

if [ "$REPLICA_ADMIN_PORTS_CSV" != " " ]; then
  $BIN_DIR$MANAGER_COMMAND --command=NODE_SHUTDOWN --host=$HOST --port="$REPLICA_ADMIN_PORTS_CSV" --timeout=$SMALL_TIMEOUT
fi
