#!/bin/bash

SCRIPTNAME=$0
if [ $# == 0 ]
then
    read -a NAMES
    for PROCESS in ${NAMES[*]}
    do
        PIDS=$(ps ax | grep $PROCESS | grep -v grep | grep -v $SCRIPTNAME | awk '{print $1}')
        if [[ $PIDS ]]
        then
            COUNT=0
            for PID in $PIDS
            do
                COUNT=$[COUNT+1]
                kill -9 $PID
            done
            echo $PROCESS killed $COUNT times
        fi
    done
else
    for PROCESS in $(echo $@ | tr " " "\n")
    do
        PIDS=$(ps ax | grep $PROCESS | grep -v grep | grep -v $SCRIPTNAME | awk '{print $1}')
        if [[ $PIDS ]]
        then
            COUNT=0
            for PID in $PIDS
            do
                COUNT=$[COUNT+1]
                kill -9 $PID
            done
            echo $PROCESS killed $COUNT times
        fi
    done
fi