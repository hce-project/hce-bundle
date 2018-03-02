#!/bin/bash

INTERFACE=$1
RESTORE_TIME=$2

if [ "$INTERFACE" == "" ]
then
	INTERFACE="eth0"
fi

if [ "$RESTORE_TIME" == "" ]
then
	RESTORE_TIME=60
fi

#######################
## Main process block
#######################

## down network interface
ifdown "$INTERFACE"

## wait timeout
a=0
while [ $a -lt $RESTORE_TIME ]
do
  a=$(($a+1))
	sleep 1
done

## up network interface
ifup "$INTERFACE"

exit 0

