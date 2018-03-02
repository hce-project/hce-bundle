#!/bin/bash

. ../cfg/current_cfg.sh

CMD1="echo \`ps ax | awk '/${NODE_BIN_NAME//\//\\/}(.*)$NODE_APP_LOG_PREFIX/ { print \$1 }'\`"
PIDS="$(eval $CMD1)"
PIDSARR=(${PIDS// / })
PIDSCNT="${#PIDSARR[@]}"
SLASHES_CNT="${NODE_BIN_NAME//[^\/]}"

if [ ${#SLASHES_CNT} -lt 1 ]; then
  ((PIDSCNT--))
fi

if [ "$1" == "s" ]; then
  echo "$PIDSCNT"
  exit
fi

if [ $PIDSCNT -lt 1 ]; then
  echo "No '$NODE_BIN_NAME' processes found for cluster [$NODE_APP_LOG_PREFIX]!"
  exit
fi

LOG_OUT="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.log"
LOG_OUT_P="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.processes.log"

echo "Trying to get status of $NODE_APP_LOG_PREFIX..."

echo "[" > $LOG_OUT 2>&1

$BIN_DIR$MANAGER_COMMAND --command=NODE_PROPERTIES --t=$BIG_TIMEOUT --host=$HOST --port="$REPLICA_ADMIN_PORTS_CSV,$ROUTER_ADMIN_PORT,$SHARD_MANAGER_ADMIN_PORT" --handler=Admin --timeout=$SMALL_TIMEOUT --tformat="Y-m-d H:i:s" >> $LOG_OUT 2>&1

echo "]" >> $LOG_OUT 2>&1

echo "Finished."

cat $LOG_OUT

echo "Processes:"

ps xau | grep $NODE_BIN_NAME > $LOG_OUT_P 2>&1
ps xau | grep searchd >> $LOG_OUT_P 2>&1

cat $LOG_OUT_P

read -p "Press [ENTER] to continue..."
