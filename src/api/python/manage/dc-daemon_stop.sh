#!/bin/bash

PROCESS=dc-daemon.py
MANAGE=dtm-admin.py
STOP='--config=../ini/dc-admin.ini --cmd=STOP'
STATUS='--config=../ini/dc-admin.ini --cmd=STAT'
LOGDIR='../log/'
LOG=$(basename $0).log
DC_DAEMON_STATUS_LOG='../log/dc-daemon_status.sh.log'
COUNTER=0

DELITEMER=":"
ZERO=0
FIELDS="fields"

RED='\e[1;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

HCE_USER="$USER"

DELAY=5
MAXITERATION=300

NAMESRC=("AdminInterfaceServer" "ClientInterfaceService" "BatchTasksManager" "BatchTasksManagerRealTime" "BatchTasksManagerProcess" "SitesManager")
CLASSES=("BatchTasksManager:batches_crawl_queue" "BatchTasksManager:purge_batches" "BatchTasksManager:age_batches" "BatchTasksManagerProcess:batches_process_queue" "SitesManager:recrawl_sites_queue")

function checkQueueOld() {
    # $1 - class
    # $2 - field
    CHECKQUEUE=$(./dc-daemon_zabbix_fetch_indicator.sh "$1%$2" $HCE_USER 0 '%')
    if [[ $CHECKQUEUE == 0 ]]
    then
        echo "FINISHED"
    else
        echo $CHECKQUEUE
    fi
}

function checkQueue() {
    # $1 - class
    # $2 - field
    ITEM=0
    for NAME in ${NAMESRC[@]}
    do
        if [[ "$1" == "$NAME" ]]
        then
            KEY=${1/$NAME/$ITEM$DELITEMER$ZERO$DELITEMER$FIELDS$DELITEMER$2}
            break
        fi
    ((ITEM++))
    done
    CHECKQUEUE=$(../bin/json-field.py -f "$KEY" < $DC_DAEMON_STATUS_LOG)
    if [[ $CHECKQUEUE -eq 0 ]]
    then
        echo "FINISHED"
    else
        echo $CHECKQUEUE
    fi
}

function check() {
    ### Check, stopped or not ###
    echo -e $BLUE'Checked dc-daemon (stopped or not)'$DEF
    sleep 1
    if [ $(pgrep $PROCESS) ]
    then
        echo -e $RED'Service ['$PROCESS'] not stopped!'$DEF
        exit 1
    else
        echo -e $BLUE'Service ['$PROCESS'] stopped!'$DEF
        exit 0
    fi
}

function civilizedStop(){
    echo "Max iteration "$MAXITERATION", delay between iteration "$DELAY" seconds, estimated time for run script about "$(($MAXITERATION*$DELAY))" seconds, or "$(($MAXITERATION*$DELAY/60))" minutes"
    #Stop all periodic tasks processing
    echo -e $BLUE"Stop all periodic tasks processing"$DEF
    ./dc-daemon_modes.sh all 0
    while :
    do
        echo -e $BLUE'Start iteration '$COUNTER $DEF
        # CHECK ARRAY EMPTY OR NOT #
        if [[ ${#CLASSES[@]} -eq 0 ]]
        then
            echo -e $RED'End iteration '$COUNTER': all queues empty'$DEF
            break
        fi
        # CHECK COUNT < 300 ITERATION #
        if [[ $COUNTER -ge $MAXITERATION ]]
        then
            echo -e $RED'End iteration '$COUNTER': maximum iteration'$DEF
            echo -e $RED'Service ['$PROCESS'] not stopped, bacause queues not empty'$DEF
            return 1
        fi
        # CHECK #
        if [[ ${#CLASSES[@]} -gt 0 ]]
        then
            # CHECK STATUS #
            echo -e $BLUE"Check dc-daemon status"$DEF
            ./dc-daemon_status.sh > /dev/null
            for LINE in ${CLASSES[@]}
            do
                CLASSTMP=($(echo $LINE | tr ':' ' '))
                CLASS=${CLASSTMP[0]}
                QUEUE=${CLASSTMP[1]}
                CHECK=$(checkQueue $CLASS $QUEUE)
                if [[ $CHECK == "FINISHED" ]]
                then
                    CLASSES=(${CLASSES[@]/$LINE})
                elif [[ $CHECK =~ "ERROR" ]]
                then
                    CLASSES=(${CLASSES[@]/$LINE})
                    echo -e $RED $CLASS'.'$QUEUE': '$CHECK $DEF
                else
                    echo -e $RED'Iteration '$COUNTER $CLASS'.'$QUEUE' - not empty, queue for end: '$CHECK $DEF
                fi
            done
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
        #    ./dc-daemon_status.sh
        #    echo 'Stop log of ['$PROCESS']:' > $LOGDIR$LOG
        #    cd ../bin
        #    ./$MANAGE $STOP >> $LOGDIR$LOG
        #else
        #    ./dc-daemon_status.sh
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
    ./dc-daemon_status.sh
    echo 'Stop log of ['$PROCESS']:' > $LOGDIR$LOG
    cd ../bin
    ./$MANAGE $STOP >> $LOGDIR$LOG
    check
else
    echo -e $RED'Service ['$PROCESS'] not started!'$DEF
    exit 1
fi

exit 0
