#!/bin/bash

PROCESS=dtm-daemon.py
MANAGE=dtm-client.py
JSON_ORIGINAL='../data/manage/dtm-daemon_tasks.json'
JSON_ORIGINAL_FULL='../data/manage/dtm-daemon_tasks_full.json'
SIZE_QUEUE=0
unset QUEUE
unset FIELD

SCRIPT_NAME=$(basename $0)

for ARG in $@
do
    case $ARG in
    'help'|'-help'|'--help')
        echo "Usage: $SCRIPT_NAME "
        echo " [help or -help or --help: this help]"
        echo " [size or -size or --size] - print number of queue to stdout"
        echo " [queue=X] [field='path'] - print value of field queue to stdout"
        echo " [ini='path' or -ini='path' or --ini='path': full path to ini file]"
        echo " [log='stdout' or 'file' or -log='stdout' or 'file' or --log='stdout' or 'file': log in stdout or file]"
        echo " [json='{\"fetchNum\":1000,\"fetchAdditionalFields\":1}' or -json='{\"fetchNum\":1000,\"fetchAdditionalFields\":1}' or --json='{\"fetchNum\":1000,\"fetchAdditionalFields\":1}': json (base64 encoded) for dtm-daemon]"
        exit 1;;
    'size'|'-size'|'--size') SIZE_QUEUE=1;;
    'queue='*|'-queue='*|'--queue='*) QUEUE=$(echo $ARG | sed 's/^queue=\|-queue=\|--queue=*\s*//');;
    'field='*|'-field='*|'--field='*) FIELD=$(echo $ARG | sed 's/^field=\|-field=\|--field=*\s*//');;
    'ini='*|'-ini='*|'--ini='*) INI_FILE=$(echo $ARG | sed 's/^ini=\|-ini=\|--ini=*\s*//');;
    'log='*|'-log='*|'--log='*) LOG_OUT=$(echo $ARG | sed 's/^log=\|-log=\|--log=*\s*//');;
    'json='*|'-json='*|'--json='*) JSON_CONFIG=$(echo $ARG | sed 's/^json=\|-json=\|--json=*\s*//' | base64 -d);;
    esac
done

if [[ ! $INI_FILE ]]
then
    INI_FILE='../ini/dtm-client.ini'
else
    if [[ ! -f $INI_FILE ]]
    then
        echo "Ini file $INI_FILE not found. Exit"
        exit 1
    fi
fi
if [[ ! $LOG_OUT || $LOG_OUT != 'stdout' ]]
then
    LOG_OUT='file'
else
    LOG_OUT='stdout'
fi

LOGDIR='../log/'
LOG=$SCRIPT_NAME.log
LOG_TMP="/tmp/$SCRIPT_NAME.log.tmp"

TEMPFILE=`mktemp /tmp/dtm-daemon_tasks.XXXXXX`
JSON_TMP=`mktemp /tmp/dtm-daemon_tasks_json.XXXXXX`
trap "rm -f $TEMPFILE $JSON_TMP" 0 1 2 5 15

function check() {
    # $1 - path to json
    while read LINE
    do
        if [[ $LINE =~ '"ids": [],' ]]
        then
            echo 0
            exit 1
        fi
        if [[ $LINE =~ "ids" ]]
        then
            COUNT_IDS=-2
            CHECK_IDS="TRUE"
        fi
        COUNT_IDS=$((COUNT_IDS+1))
        if [[ $LINE =~ "]" ]]
        then
            break
        fi
    done < $1
    if [[ $CHECK_IDS == "TRUE" ]]
    then
        echo $COUNT_IDS
    else
        echo 0
    fi
}

function find() {
    # $1 - id of queue
    # $2 - field of queue
    # $3 - path to json
    readarray JSON < $3
    for ((LINE=1;LINE<=${#JSON[@]]};++LINE))
    do
        if [[ ${JSON[$LINE]} =~ '"id": '$1 ]]
        then
            for ((INLINE=$LINE;INLINE<=${#JSON[@]]};++INLINE))
            do
                if [[ ${JSON[$INLINE]} =~ "$2" ]]
                then
                    echo ${JSON[$INLINE]} | awk -F\"$2\"\: '{print $2}' | sed 's/\"\|\,//g'
                    exit 1
                fi
                if [[ ${JSON[$INLINE]} =~ "}" ]]
                then
                    break
                fi
            done
            for ((INLINE=$LINE;INLINE>=0;--INLINE))
            do
                if [[ ${JSON[$INLINE]} =~ "$2" ]]
                then
                    echo ${JSON[$INLINE]} | awk -F\"$2\"\: '{print $2}' | sed 's/\"\|\,//g'
                    exit 1
                fi
                if [[ ${JSON[$INLINE]} =~ "{" ]]
                then
                    break
                fi
            done
        fi
    done
    echo 'Field not found'
}

if [[ $JSON_CONFIG ]]
then
    echo $JSON_CONFIG > $JSON_TMP
    #echo $JSON_CONFIG > "/tmp/dtm-daemon_tasks_last_request.json"
    JSON_DTM=$JSON_TMP
    JSON_DTM_FULL=$JSON_TMP
else
    JSON_DTM=$JSON_ORIGINAL_FULL
    JSON_DTM_FULL=$JSON_ORIGINAL
fi

PID=$(pgrep $PROCESS)

if [ $PID ]
then
    if [[ "$SIZE_QUEUE" == 1 ]]
    then
        ARG='--config='$INI_FILE' -t GET_TASKS --file='$JSON_DTM
        cd  ../bin && ./$MANAGE $ARG > $TEMPFILE
        SIZE=$(check $TEMPFILE)
        echo $SIZE
        exit 1
    elif [[ "$QUEUE" && "$FIELD" ]]
    then
        ARG='--config='$INI_FILE' -t GET_TASKS --file='$JSON_DTM_FULL
        cd  ../bin && ./$MANAGE $ARG > $TEMPFILE
        FIND=$(find "$QUEUE" "$FIELD" $TEMPFILE)
        echo $FIND
        exit 1
    else
        ARG='--config='$INI_FILE' -t GET_TASKS --file='$JSON_DTM_FULL
        if [[ $LOG_OUT == "stdout" ]]
        then
            cd  ../bin && ./$MANAGE $ARG > $LOG_TMP
            echo >> $LOG_TMP
            cat $LOG_TMP
        else
            echo "Service running, pid="$PID
            echo "Checking statistics..."
            cd  ../bin && ./$MANAGE $ARG > $LOG_TMP
            echo >> $LOG_TMP
            mv $LOG_TMP $LOGDIR$LOG
            echo "Saved in $LOGDIR$LOG"
        fi
    fi
else
    echo "Process [$PROCESS] stopped..."
fi

exit 0
