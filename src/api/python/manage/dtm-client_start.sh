#!/bin/bash

#execute common script
. ../cfg/all_cfg.sh

LOG_FILE="../log/dtm-client.log"
if [ -f $LOG_FILE ];
then
  rm $LOG_FILE
fi

cd ../bin && ./dtm-client.py --config=../ini/dtm-client.ini $1
