#!/bin/bash

. ../cfg/current_cfg.sh

if [ "$1" = "" ]; then
  COMMAND="NODE_MPMGET"
  MODE=""
else
  COMMAND="NODE_MPMSET"
  MODE="--purge=$1"
fi

$BIN_DIR$MANAGER_COMMAND --command=$COMMAND --host=$HOST --port=$SHARD_MANAGER_ADMIN_PORT $MODE --timeout=$SMALL_TIMEOUT

if [ "$1" != "" ]; then
  echo "new value:"
  . $0 ""
fi
