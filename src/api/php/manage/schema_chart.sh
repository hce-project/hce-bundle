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
  echo "[s=N] - integer number delay and infinite cycle with stdout."
  echo "[s] - single start with stdout (old format deprecated)."
  echo "[N] - where N is number of second to delay between starts, Ctrl+c to stop (old format deprecated)."
  echo "If arguments omitted output file is $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log by default."
  exit 1
fi

REALTIME="--realtime=\"{\\\"realtime\\\":1}\""

COMMAND_GO="$BIN_DIR$MANAGER_COMMAND --command=STRUCTURE_CHECK --view=chart --fields=rhasc --host=\"$CMD_HOSTS_CSV\" --port=\"$CMD_PORTS_CSV\" --log=0 --timeout=$SMALL_TIMEOUT --name=$NODE_APP_LOG_PREFIX $REALTIME"

if [ "$outFile" == "" ]; then
  if [[ "$1" == "s" || "$s" == "0" ]]; then
    eval $COMMAND_GO
  else
    if [[ "$1" == "" && "$s" == "" ]]; then
      eval $COMMAND_GO > $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log
    else
      if [ "$1" != "" ]; then
         delay="$1"
      else
         delay="$s"
      fi
      while true
        do
          eval $COMMAND_GO
          sleep $(($delay+0))
          clear
        done
    fi
  fi
else
  eval $COMMAND_GO > $outFile
fi
