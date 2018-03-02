#!/bin/bash

REPEAT=$1
COUNT=$2

if [ "$REPEAT" == "" ]
then
	REPEAT=20
fi


if [ "$COUNT" == "" ]
then
	COUNT=100
fi

CMD="dd if=/dev/zero of=tmp bs=1M count=$COUNT"

LOG_START="start.txt"
LOG_END="end.txt"

a=0
while [ $a -lt $REPEAT ]
  do

		cat /proc/stat | grep "cpu " > $LOG_START

##		echo "exec : $CMD"
		$CMD

		cat /proc/stat | grep "cpu " > $LOG_END

##		cat $LOG_START
##		cat $LOG_END

		USR1=`awk -F " " '{print $2}' $LOG_START`
		NICE1=`awk -F " " '{print $3}' $LOG_START`
		SYS1=`awk -F " " '{print $4}' $LOG_START`
		IDLE1=`awk -F " " '{print $5}' $LOG_START`
		IOWAIT1=`awk -F " " '{print $6}' $LOG_START`
		IRQ1=`awk -F " " '{print $7}' $LOG_START`
		SOFRIRQ1=`awk -F " " '{print $8}' $LOG_START`
		STEAL1=`awk -F " " '{print $9}' $LOG_START`
		GUEST1=`awk -F " " '{print $10}' $LOG_START`

		USR2=`awk -F " " '{print $2}' $LOG_END`
		NICE2=`awk -F " " '{print $3}' $LOG_END`
		SYS2=`awk -F " " '{print $4}' $LOG_END`
		IDLE2=`awk -F " " '{print $5}' $LOG_END`
		IOWAIT2=`awk -F " " '{print $6}' $LOG_END`
		IRQ2=`awk -F " " '{print $7}' $LOG_END`
		SOFRIRQ2=`awk -F " " '{print $8}' $LOG_END`
		STEAL2=`awk -F " " '{print $9}' $LOG_END`
		GUEST2=`awk -F " " '{print $10}' $LOG_END`

		SUM1=`expr $USR1 + $NICE1 + $SYS1 + $IDLE1 + $IOWAIT1 + $IRQ1 + $SOFRIRQ1 + $STEAL1 + $GUEST1`

		SUM2=`expr $USR2 + $NICE2 + $SYS2 + $IDLE2 + $IOWAIT2 + $IRQ2 + $SOFRIRQ2 + $STEAL2 + $GUEST2`

		IOWAIT_PERCENT=`expr \( $IOWAIT2 - $IOWAIT1 \) \* 100 / \( $SUM2 - $SUM1 \)`
		echo "IOWAIT : $IOWAIT_PERCENT%"

    sleep 1
    a=$(($a+1))
  done

	rm -f $LOG_START
	rm -f $LOG_END
exit 0


