#!/bin/bash

. ../cfg/current_cfg.sh

checkAllowedValue()
## $1 - input for check value
{
	if [ "$1" -lt 5 ]
	then
		echo "Operation was cancelled."
		echo "Dump interval value was inputted is incorrect."
		echo "Allowed value must be greater than 5 sec."
		exit 1
	fi	
}

if [ "$1" = "" ]; then
  COMMAND="NODE_DUMP_INTERVAL_GET"
  DUMP_INTERVAL=""
else
	checkAllowedValue "$1"
  COMMAND="NODE_DUMP_INTERVAL_SET"
  DUMP_INTERVAL="--interval=$1"
fi

executeCommand()
## neither input parameters
{
	#Reload configurations variables
	. ../cfg/current_cfg.sh

	#Check is instance already started and execution
	if [ $(./status.sh s) -gt 0 ]
	then
		echo "Cluster [$NODE_APP_LOG_PREFIX] has values:"
    $BIN_DIR$MANAGER_COMMAND --command=$COMMAND --host=$CMD_HOSTS_CSV --port=$CMD_PORTS_CSV --handler="*" $DUMP_INTERVAL --timeout=$SMALL_TIMEOUT
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

