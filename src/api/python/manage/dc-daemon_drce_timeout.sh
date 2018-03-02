#!/bin/bash

CONGIFVAR="DRCETimeout"

if [ "$1" = "" ]; then
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="$CONGIFVAR" --classes="SitesManager" > ../log/$0.log
else
  ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="$CONGIFVAR:$1" --classes="SitesManager" > ../log/$0.log
fi
