#!/bin/bash

CURRENT_CFG_FILE="../cfg/current_cfg.txt"
CONFIGURATION_NAME_N="n"
CONFIGURATION_NAME_M="m"
CONFIGURATION_NAME_R="r"
CURRENT_CFG="$CONFIGURATION_NAME_N"

#Check curent configuration
if [ -f "$CURRENT_CFG_FILE" ]
then
  CURRENT_CFG=$(<$CURRENT_CFG_FILE)
else
  echo "$CURRENT_CFG" > "$CURRENT_CFG_FILE"
fi

#Load proper configuration
if [ "$CURRENT_CFG" == "$CONFIGURATION_NAME_N" ]; then
  #N configuration
  #Single-host configuration
  #. ../cfg/c112_localhost_n0_cfg.sh
  #Multi-host configuration for first host of two-hosts
  # . ../cfg/c112_localhost_n0_2h_cfg.sh
  #Multi-host configuration for second host of two-hosts
  #. ../cfg/n_cfg.sh
  echo > /dev/null
  #_CONFIGFILE_N_#
elif [ "$CURRENT_CFG" == "$CONFIGURATION_NAME_M" ]; then
  #M configuration
  #Single-host configuration
  #. ../cfg/c112_localhost_m0_cfg.sh
  #Multi-host configuration for first host of two-hosts
  # . ../cfg/c112_localhost_m0_2h_cfg.sh
  #Multi-host configuration for second host of two-hosts
  #. ../cfg/m_cfg.sh
  echo > /dev/null
  #_CONFIGFILE_M_#
else
  #R configuration
  #Single-host configuration
  #. ../cfg/c112_localhost_r0_cfg.sh
  #Multi-host configuration for first host of two-hosts
  #. ../cfg/c112_localhost_r0_2h_cfg.sh
  #Multi-host configuration for second host of two-hosts
  #. ../cfg/c112_localhost_r0_2h-data_cfg.sh
  echo > /dev/null
  #_CONFIGFILE_R_#
fi
