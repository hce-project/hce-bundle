#!/bin/bash

while [[ $# > 1 ]]
do
key="$1"
shift

case $key in
    -o|--options)
    OPTIONS="$1"
    shift
    ;;
    -s|--scripts)
    SCRIPTS="$1"
    shift
    ;;
esac
done

if [ ! $SCRIPTS ]
then
    echo 'Usage: '$0' [-o <options>] -p <process_name_to_kill_0> [<process_name_to_kill_1>] [<process_name_to_kill_n>]'
    exit 1
fi

COMMAND=$(echo $BINPATH$KILLSCRIPT | sed -e 's/\//\\\//g')

for i in $(echo $SCRIPTS | tr ";" " ")
do
  INPUT=${INPUT}$i" "
done

cp $JSONPATH$JSONFILE $JSON_TMP_DIR$JSON_TMP_FILE

sed -e "s/COMMAND_REPLACE/$COMMAND/g" $JSON_TMP_DIR$JSON_TMP_FILE > $JSON_TMP_DIR$JSON_TMP_FILE.tmp
sed -e "s/PROCESS_REPLACE/$INPUT/g" $JSON_TMP_DIR$JSON_TMP_FILE.tmp > $JSON_TMP_DIR$JSON_TMP_FILE
rm -f $JSON_TMP_DIR$JSON_TMP_FILE.tmp

cd $PHPPATH
$BIN_DIR$DRCE_COMMAND --request=SET --host=$ROUTER --port=$ROUTER_CLIENT_PORT --n=$REQUESTS --t=$SMALL_TIMEOUT --l=$LOG_LEVEL --json=$JSON_TMP_DIR$JSON_TMP_FILE --cover=0 > $LOG_DIR$LOG_FILE.$NODE_APP_LOG_PREFIX.log
