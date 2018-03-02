#!/bin/sh

#execute common script
. ../cfg/all_cfg.sh

#export PYTHONPATH=$(pwd)/../hce/
#rm ../data/dtm.db

#rm ../log/dtm-daemon.log

PROCESS=dtm-daemon.py
ARG='--c=../ini/dtm-daemon.ini'

### Check process (worked or not) ###
if [ $(pgrep $PROCESS) ]
then
  echo 'Service ['$PROCESS'] already started!'
  exit 1
fi
### Start process ###
cd  ../bin && ./$PROCESS $ARG &
sleep 1
### Check process (started or not) ###
if [ $(pgrep $PROCESS) ]
then
  echo 'Service ['$PROCESS'] started!'
  exit 1
fi
### If process not start ###
echo 'Service ['$PROCESS'] not started!'

exit 0
