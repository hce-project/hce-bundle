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
  echo "List of allowed arguments:"
  echo "[outFile=<output file name>] - write output to the specified file."
  echo "If arguments omitted output file is $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log by default."
  exit 1
fi

REALTIME="--realtime=\"{\\\"realtime\\\":1}\""

COMMAND_GO="$BIN_DIR$MANAGER_COMMAND --command=STRUCTURE_CHECK $REALTIME --host=\"$CMD_HOSTS_CSV\" --port=\"$CMD_PORTS_CSV\" --log=0 --timeout=$SMALL_TIMEOUT --name=\"$NODE_APP_LOG_PREFIX\""

if [ "$outFile" == "" ]; then
  eval $COMMAND_GO > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
else
  eval $COMMAND_GO > $outFile
fi
