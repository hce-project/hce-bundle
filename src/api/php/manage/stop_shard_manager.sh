#!/bin/bash

. ../cfg/current_cfg.sh

#Stop rmanager
$BIN_DIR$MANAGER_COMMAND --command=NODE_SHUTDOWN --host=$HOST --port=$SHARD_MANAGER_ADMIN_PORT --timeout=$SMALL_TIMEOUT
