#!/bin/bash

MANAGE=dtm-admin.py

BINDIR='../bin'
LOGDIR='../log/'
LOG=$(basename $0).log


cd $BINDIR
./$MANAGE --config=../ini/dtm-admin.ini --cmd=SYSTEM --fields="{\"type\":0,\"data\":null}" > $LOGDIR$LOG

exit 0

