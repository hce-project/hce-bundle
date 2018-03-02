#!/bin/sh
#First argument is the config file name, for example ../ini/dtm-admin.ini

if [ "$1" = "" ]; then
  CONFIG="../ini/dtm-admin.ini"
else
  CONFIG="$1"
fi

PROCESS=dtm-daemon.py
MANAGE=dtm-admin.py
ARG="--config=$CONFIG --cmd=STAT"
LOGDIR='../log/'
LOG=$0.log
LOG_TMP="$0.log.tmp"

PID=$(pgrep $PROCESS)

if [ $PID ]
then
  if [ "$1" = "" ]; then
    echo "Service running, pid="$PID
    echo "Checking statistics..."
    cd ../bin && ./$MANAGE $ARG > $LOGDIR$LOG_TMP
    mv $LOGDIR$LOG_TMP $LOGDIR$LOG
    echo "Saved in $LOGDIR$LOG"
  else
    cd ../bin && ./$MANAGE $ARG
  fi
else
  if [ "$1" = "" ]; then
    echo "Process [$PROCESS] stopped..."
  fi
fi

exit 0