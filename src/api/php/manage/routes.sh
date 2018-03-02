#!/bin/bash

. ../cfg/current_cfg.sh

LOG_OUT="$LOG_DIR$0.$NODE_APP_LOG_PREFIX.log"

removeFile()
## $1 - file name
{
	if [ -f $1 ]
	then 
		rm -f "$1"
	fi
}

executeCommand()
## neither input parameters
{
	#Reload configurations variables
	. ../cfg/current_cfg.sh

	#Check is instance already started and execution
	if [ $(./status.sh s) -gt 0 ]
	then
		echo "Cluster [$NODE_APP_LOG_PREFIX] has values:" >> $LOG_OUT
		$BIN_DIR$MANAGER_COMMAND --command=NODE_ROUTES --host=$HOST --port=$ROUTER_ADMIN_PORT,$SHARD_MANAGER_ADMIN_PORT --timeout=$SMALL_TIMEOUT >> $LOG_OUT 2>&1
	else
		echo "Cluster [$NODE_APP_LOG_PREFIX] not started!" >> $LOG_OUT
	fi
}

################
## Main loop
################

removeFile "$LOG_OUT"

#Save old values used current cfg
CURRENT_CFG_OLD="$CURRENT_CFG"

#Change configuration name
./config.sh n s

executeCommand

#Change configuration name
./config.sh m s

executeCommand

#Change configuration name
./config.sh m1 s

executeCommand

#Change configuration name
./config.sh r s

executeCommand

#Restore old configuration name
./config.sh "$CURRENT_CFG_OLD" s

exit 0

