#!/bin/bash

PROCESS=dtm-daemon.py
MANAGE=dtm-admin.py
STOP='--config=../ini/dtm-admin.ini --cmd=STOP'
STATUS='--config=../ini/dtm-admin.ini --cmd=STAT'
LOGDIR='../log/'
LOG=$(basename $0).log
COUNTER=0

RED='\e[1;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

DELAY=5
MAXITERATION=300

function checkQueue() {
    # $1 - param
    CHECKQUEUE=$(./dtm-daemon_tasks.sh "$1")
    if [[ $CHECKQUEUE == 0 ]]
    then
        echo "FINISHED"
    else
        echo $CHECKQUEUE
    fi
}

function check() {
    ### Check, stopped or not ###
    sleep 1
    if [ $(pgrep $PROCESS) ]
    then
        echo  -e $RED'Service ['$PROCESS'] not stopped!'$DEF
        exit 1
    else
        echo  -e $BLUE'Service ['$PROCESS'] stopped!'$DEF
        exit 0
    fi
}

function civilizedStop(){
    echo "Max iteration "$MAXITERATION", delay between iteration "$DELAY" seconds, estimated time for run script about "$(($MAXITERATION*$DELAY))" seconds, or "$(($MAXITERATION*$DELAY/60))" minutes"
    while :
    do
        echo -e $BLUE'Start iteration '$COUNTER $DEF
        # CHECK COUNT < 300 ITERATION #
        if [[ $COUNTER -ge $MAXITERATION ]]
        then
            echo -e $RED'End iteration '$COUNTER': maximum iteration'$DEF
            echo -e $RED'Service ['$PROCESS'] not stopped, bacause queues not empty'$DEF
            return 1
        fi
        # CHECK STATUS #
        #echo -e $BLUE"Check dtm-daemon queue"$DEF
        CHECK=$(checkQueue "size")
        if [[ $CHECK == "FINISHED" ]]
        then
            echo -e $RED'End iteration '$COUNTER': all queues empty'$DEF
            break
        else
            echo -e $RED'Iteration '$COUNTER' - not empty, queue for end: '$CHECK $DEF
        fi
        sleep $DELAY
        echo -e $BLUE'End iteration '$COUNTER $DEF
        ((COUNTER++))
    done
    return 0
}


for ARG in $*
do
    case $ARG in
    'force'|'-force'|'--force')
        FORCE="TRUE";;
    'kill'|'-kill'|'--kill')
        KILL="TRUE";;
    *)
        echo "Usage $0 [force or kill] [help]"
        exit 0;;
    esac
done

if [[ $FORCE && $KILL ]]
then
    echo "Usage $0 [force or kill] [help]"
    exit 0
fi


### Check process (worked or not) and stop, if worked ###
if [ $(pgrep $PROCESS) ]
then
    if [[ $KILL ]]
    then
        #civilizedStop
        #if [[ $? -eq 0 ]]
        #then
        #    ./dtm-daemon_status.sh
        #    echo 'Stop log of ['$PROCESS']:' > $LOGDIR$LOG
        #    cd ../bin
        #    ./$MANAGE $STOP >> $LOGDIR$LOG
        #else
        #    ./dtm-daemon_status.sh
        #    echo 'Killing ['$PROCESS']'
        #    killall -9 $PROCESS
        #fi
        killall -9 $PROCESS
        check
    elif [[ -z $FORCE ]]
    then
        civilizedStop
        if [[ $? -eq 1 ]]
        then
            check
        fi
    fi
    ./dtm-daemon_status.sh
    echo 'Stop log of ['$PROCESS']:' > $LOGDIR$LOG
    cd ../bin
    ./$MANAGE $STOP >> $LOGDIR$LOG
    check
else
    echo -e $RED'Service ['$PROCESS'] not started!'$DEF
    exit 1
fi

exit 0
