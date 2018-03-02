#!/bin/bash

CURRENT_CFG_FILE="../cfg/current_cfg.txt"
CONFIGURATION_NAME_N="n"
CONFIGURATION_NAME_M="m"
CONFIGURATION_NAME_M1="m1"
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
  . ../cfg/c112_localhost_n0_cfg.sh

  #Multi-host configuration for first host of dual hosts
  #. ../cfg/c112_localhost_n0_2h_cfg.sh
  #Multi-host configuration for second host of dual hosts
  #. ../cfg/c112_localhost_n0_2h-data_cfg.sh

  #Multi-host configuration for first host of triple hosts
  #. ../cfg/c112_localhost_n0_3h_cfg.sh
  #Multi-host configuration for second host of triple hosts
  #. ../cfg/c112_localhost_n0_3h-data_cfg.sh
  #Multi-host configuration for third host of triple hosts
  #. ../cfg/c112_localhost_n0_3h-data2_cfg.sh
else
  if [ "$CURRENT_CFG" == "$CONFIGURATION_NAME_M" ]; then
    #M configuration
    #Single-host configuration
    . ../cfg/c112_localhost_m0_cfg.sh

    #Multi-host configuration for first host of dual hosts
    #. ../cfg/c112_localhost_m0_2h_cfg.sh
    #Multi-host configuration for second host of dual hosts
    #. ../cfg/c112_localhost_m0_2h-data_cfg.sh

    #Multi-host configuration for first host of triple hosts
    #. ../cfg/c112_localhost_m0_3h_cfg.sh
    #Multi-host configuration for second host of triple hosts
    #. ../cfg/c112_localhost_m0_3h-data_cfg.sh
    #Multi-host configuration for third host of triple hosts
    #. ../cfg/c112_localhost_m0_3h-data2_cfg.sh
  else
    if [ "$CURRENT_CFG" == "$CONFIGURATION_NAME_M1" ]; then
      #M configuration
      #Single-host configuration
      . ../cfg/c112_localhost_m1_cfg.sh
  
      #Multi-host configuration for first host of dual hosts
      #. ../cfg/c112_localhost_m1_2h_cfg.sh
      #Multi-host configuration for second host of dual hosts
      #. ../cfg/c112_localhost_m1_2h-data_cfg.sh
  
      #Multi-host configuration for first host of triple hosts
      #. ../cfg/c112_localhost_m1_3h_cfg.sh
      #Multi-host configuration for second host of triple hosts
      #. ../cfg/c112_localhost_m1_3h-data_cfg.sh
      #Multi-host configuration for third host of triple hosts
      #. ../cfg/c112_localhost_m1_3h-data2_cfg.sh
    else
      #R configuration
      #Single-host configuration
      . ../cfg/c112_localhost_r0_cfg.sh
  
      #Multi-host configuration for first host of dual hosts
      #. ../cfg/c112_localhost_r0_2h_cfg.sh
      #Multi-host configuration for second host of dual hosts
      #. ../cfg/c112_localhost_r0_2h-data_cfg.sh
  
      #Multi-host configuration for first host of triple hosts
      #. ../cfg/c112_localhost_r0_3h_cfg.sh
      #Multi-host configuration for second host of triple hosts
      #. ../cfg/c112_localhost_r0_3h-data_cfg.sh
      #Multi-host configuration for third host of triple hosts
      #. ../cfg/c112_localhost_r0_3h-data2_cfg.sh
    fi
  fi
fi
