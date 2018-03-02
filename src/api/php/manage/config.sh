#!/bin/bash

. ../cfg/current_cfg.sh

if [[ "$1" == "$CONFIGURATION_NAME_N" || "$1" == "$CONFIGURATION_NAME_M" || "$1" == "$CONFIGURATION_NAME_M1" || "$1" == "$CONFIGURATION_NAME_R" ]]; then
  echo "$1" > "$CURRENT_CFG_FILE"
  chmod 666 $CURRENT_CFG_FILE
  . ../cfg/current_cfg.sh
else
  echo "Unsupported configuration name $1"
fi

if [ "$2" != "s" ]; then
  echo "Current configuration is [$CURRENT_CFG]"
  echo "Cluster node name prefix [$NODE_APP_LOG_PREFIX]"
fi
