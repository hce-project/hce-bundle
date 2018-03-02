#!/bin/bash

PHPPATH=~/hce-node-bundle/api/php/manage/
PYTHONPATH=~/hce-node-bundle/api/python/ftests/
JSONPATH=~/hce-node-bundle/api/python/data/ftests/
LOGDIR=~/hce-node-bundle/api/python/log/

JSONFILE=dc_tests_init.json
JSON_TMP_FILE=$JSONFILE.tmp

SCRIPTNAME=$(basename $0)
COMMANDS[0]="cd api/python/ftests/; ./dc_tests_cleanup.sh > ../log/$SCRIPTNAME.log 2>&2"
COMMANDS[1]="echo 'Create SQL DB schema' >> api/python/log/$SCRIPTNAME.log 2>&1"
COMMANDS[2]="cd api/python/manage; ./mysql_create_db.sh >> ../log/$SCRIPTNAME.log 2>&2"

REQUESTS=1
LOG_LEVEL=3
LOG_FILE=$0
JSON_TMP_DIR='/tmp/'

function checkError {
    cat $1 | while read line
    do
        SEARCH=$(echo $line | grep stderror)
        if [[ $SEARCH ]]
        then
            ERROR=$(echo $line | awk -F\" '{print $4}' | sed -e 's/rn//g' | base64 --decode)
            if [[ $ERROR ]]
            then
                echo $ERROR
                break
            fi
        fi
        unset SEARCH
    done
}

### Start ###

cd $PHPPATH
. ./config.sh m
. ./../cfg/current_cfg.sh

### First ###

COMMAND=$(echo ${COMMANDS[0]} | sed -e 's/\//\\\//g' | sed -e 's/&/\\&/g')

cp $JSONPATH$JSONFILE $JSON_TMP_DIR$JSON_TMP_FILE.tmp
sed -e "s/COMMAND_REPLACE/$COMMAND/g" $JSON_TMP_DIR$JSON_TMP_FILE.tmp > $JSON_TMP_DIR$JSON_TMP_FILE
rm -f $JSON_TMP_DIR$JSON_TMP_FILE.tmp

cd $PHPPATH
$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$JSON_TMP_DIR$JSON_TMP_FILE --cover=0 > $LOGDIR$LOG_FILE.$NODE_APP_LOG_PREFIX.log

rm -f $JSON_TMP_DIR$JSON_TMP_FILE

ERR=$(checkError $LOGDIR$LOG_FILE.$NODE_APP_LOG_PREFIX.log)

if [[ $ERR ]]
then
    echo -en 'Table not cleaned. Error:\n'$ERR'.\n\033[37;1;45mExiting\033[0m\n'
    cd $PHPPATH
    . ./config.sh n
    exit 1
fi

### Second ###

COMMAND=$(echo ${COMMANDS[1]} | sed -e 's/\//\\\//g' | sed -e 's/&/\\&/g')

cp $JSONPATH$JSONFILE $JSON_TMP_DIR$JSON_TMP_FILE.tmp
sed -e "s/COMMAND_REPLACE/$COMMAND/g" $JSON_TMP_DIR$JSON_TMP_FILE.tmp > $JSON_TMP_DIR$JSON_TMP_FILE
rm -f $JSON_TMP_DIR$JSON_TMP_FILE.tmp

cd $PHPPATH
$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$JSON_TMP_DIR$JSON_TMP_FILE --cover=0 > $LOGDIR$LOG_FILE.$NODE_APP_LOG_PREFIX.log

rm -f $JSON_TMP_DIR$JSON_TMP_FILE

### Third ###

COMMAND=$(echo ${COMMANDS[2]} | sed -e 's/\//\\\//g' | sed -e 's/&/\\&/g')

cp $JSONPATH$JSONFILE $JSON_TMP_DIR$JSON_TMP_FILE.tmp
sed -e "s/COMMAND_REPLACE/$COMMAND/g" $JSON_TMP_DIR$JSON_TMP_FILE.tmp > $JSON_TMP_DIR$JSON_TMP_FILE
rm -f $JSON_TMP_DIR$JSON_TMP_FILE.tmp

cd $PHPPATH
$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$JSON_TMP_DIR$JSON_TMP_FILE --cover=0 > $LOGDIR$LOG_FILE.$NODE_APP_LOG_PREFIX.log

rm -f $JSON_TMP_DIR$JSON_TMP_FILE

ERR=$(checkError $LOGDIR$LOG_FILE.$NODE_APP_LOG_PREFIX.log)

if [[ $ERR ]]
then
    echo -en 'SQL DB schema not created. Error:\n'$ERR'.\n\033[37;1;45mExiting\033[0m\n'
    cd $PHPPATH
    . ./config.sh n
    exit 1
fi

### END ###

cd $PHPPATH
. ./config.sh n

echo -en '\033[37;1;44mSuccessful\033[0m\n'

exit 0
