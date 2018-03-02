#!/bin/bash

. ../cfg/current_cfg.sh

#Stop router
$BIN_DIR$MANAGER_COMMAND --command=NODE_SHUTDOWN --host=$HOST --port=$ROUTER_ADMIN_PORT --timeout=$SMALL_TIMEOUT
