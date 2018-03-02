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
  echo "realtime={0,1} - set flag for getting data used realtime algorithm"
  echo "cmd_host=<host_names> - set hosts list for execution request (comma separated)"
  echo "cmd_port=<port_numbers> - set ports list for execution request (comma separated)"
  echo "cmd_handler=<handler_names> - set handlers list for execution request (comma separated)"
  echo "If arguments omitted output file is $LOG_DIR$0.$NODE_APP_LOG_PREFIX.log by default."
  exit 1
fi

if [ "$realtime" == "" ]
then
	isRealtime="0"
else
	isRealtime="1"
fi

if [ "$isRealtime" == "1" ] 
then
  REALTIME="--realtime=\"{\\\"realtime\\\":$realtime}\""
  CMD_HOST="$CMD_HOSTS_CSV"
  CMD_PORT="$CMD_PORTS_CSV"
  CMD_HANDLER="*"
else

	if [ "$cmd_host" == "" ]
	then
		CMD_HOST="$CMD_HOSTS_CSV"
	else
		CMD_HOST="$cmd_host"
	fi

  if [ "$cmd_port" = "" ]
	then
    CMD_PORT="$CMD_PORTS_CSV"
  else
    CMD_PORT="$cmd_port"
  fi

  if [ "$cmd_handler" = "" ]
	then
    CMD_HANDLER="*"
  else
    CMD_HANDLER="$cmd_handler"
  fi

fi

COMMAND_GO="$BIN_DIR$MANAGER_COMMAND --command=NODE_PROPERTIES $REALTIME --host=$CMD_HOST --port=$CMD_PORT --handler=$CMD_HANDLER --timeout=$BIG_TIMEOUT --tformat=\"Y-m-d H:i:s\" --sphinx_properties_formatted=yes"

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

