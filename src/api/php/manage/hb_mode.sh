#!/bin/bash

. ../cfg/current_cfg.sh

MIN_ALLOWED_MODE="0"
MAX_ALLOWED_MODE="3"

checkAllowedMode()
## $1 - input mode value
{
	if [[ "$1" -lt "$MIN_ALLOWED_MODE" || "$1" -gt "$MAX_ALLOWED_MODE" ]]
	then
		echo "Operation was cancelled."
		echo "Inputed heartbeat mode value ($1) not supported."
		echo "Allowed range between $MIN_ALLOWED_MODE and $MAX_ALLOWED_MODE."
		exit 1
	fi	
}

if [ "$1" = "" ]; then
  COMMAND="NODE_HB_MODE_GET"
  HB_MODE=""
else
  COMMAND="NODE_HB_MODE_SET"
  HB_MODE="--hbmode=$1"
	checkAllowedMode "$1"
fi

CMD_HANDLER="DataServerProxy,DataClientData,DataClientProxy"

executeCommand()
## neither input parameters
{
	#Reload configurations variables
	. ../cfg/current_cfg.sh

	#Check is instance already started and execution
	if [ $(./status.sh s) -gt 0 ]
	then
		echo "Cluster [$NODE_APP_LOG_PREFIX] has values:"
		$BIN_DIR$MANAGER_COMMAND --command=$COMMAND --host=$CMD_HOSTS_CSV --port=$CMD_PORTS_CSV --handler=$CMD_HANDLER $HB_MODE --timeout=$SMALL_TIMEOUT
	else
		echo "Cluster [$NODE_APP_LOG_PREFIX] not started!"
	fi
}

################
## Main loop
################

#Save old values used current cfg
CURRENT_CFG_OLD="$CURRENT_CFG"

#Change configuration name
./config.sh n s

executeCommand

#Change configuration name
./config.sh m s

executeCommand

#Change configuration name
./config.sh r s

executeCommand

#Restore old configuration name
./config.sh "$CURRENT_CFG_OLD" s

if [ "$1" != "" ]; then
  echo "new value:"
  . $0 ""
fi

exit 0

