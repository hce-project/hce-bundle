#!/bin/bash

. ../cfg/current_cfg.sh

if [ "$1" = "" ]; then
  COMMAND="NODE_MRCSGET"
  COLLECTED_SIZE=""
else
  COMMAND="NODE_MRCSSET"
  COLLECTED_SIZE="--csize=$1"
fi

$BIN_DIR$MANAGER_COMMAND --command=$COMMAND --host=$HOST --port="$ROUTER_ADMIN_PORT,$SHARD_MANAGER_ADMIN_PORT" $COLLECTED_SIZE --timeout=$SMALL_TIMEOUT

if [ "$1" != "" ]; then
  echo "new value:"
  . $0 ""
fi

