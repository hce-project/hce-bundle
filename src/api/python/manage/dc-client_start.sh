#!/bin/bash

#execute common script
. ../cfg/all_cfg.sh

LOG_FILE="../log/dc-client.log"

if [ -f $LOG_FILE ];
then
  rm $LOG_FILE
fi


#echo " ./dc-client.py --config=../ini/dc-client.ini $1"
#for an_arg in "$@" ; do
#   echo "${an_arg}"
#done

cd ../bin && ./dc-client.py --config=../ini/dc-client.ini $1
