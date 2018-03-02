#!/bin/bash

. ../cfg/general_cfg.sh

parseOptions "$@"

if [ "$cfgFile" == "" ]
then
  . ../cfg/current_cfg.sh
else
  . $cfgFile
fi

if [ "$ARG_HELP" == "1" ]; then
  echo "Usage nothing arguments: $0"
  exit 1
fi

CMD_HANDLER="DataProcessorData"
CMD_HOST="$CMD_HOSTS_CSV"
CMD_PORT="$CMD_PORTS_CSV"

COMMAND_GO="$BIN_DIR$MANAGER_COMMAND --command=NODE_RESET_STAT_COUNTERS --handler=$CMD_HANDLER --host=$CMD_HOST --port=$CMD_PORT --handler=$CMD_HANDLER --timeout=$BIG_TIMEOUT"

if [ "$cmd_host" == "" ]
then
  if [ "$outFile" == "" ]
  then
    eval $COMMAND_GO > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
  else
    $COMMAND_GO > $outFile
  fi
else
  while true
    do
      $COMMAND_GO
      sleep $1
      clear
    done
fi

