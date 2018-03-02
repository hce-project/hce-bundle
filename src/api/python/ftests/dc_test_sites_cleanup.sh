#!/bin/bash

if [[ -z "$@" ]]
then
    echo "Usage: $0 id=\"site_id\""
    exit 1
fi

JSONPARSER='../bin/json-field.py'

function parser(){
    # $1 - json file
    CHECK='itemsList:0:errorCode'
    ERROR='itemsList:0:errorMessage'
    CHECK_ERROR=$($JSONPARSER -f "$CHECK"< $1)
    if [[ $CHECK_ERROR -eq 0 ]]
    then
        echo "Cleared"
    else
        echo "Error:"
        $JSONPARSER -f "$ERROR"
    fi
}

# CHECK ARGUMENTS #
for ARG in "$@"
do
    case "$ARG" in
        id=*|-id=*|--id=*)
            ID=$(echo $ARG | awk -F= '{print $2}');;
        force|-force|--force)
            FORCE="TRUE";;
    esac
done

if [[ -z $ID ]]
then
    echo "Usage: $0 id=\"site_id\""
    exit 1
fi

# FORCE? #
if [[ -z $FORCE ]]
then
    echo "Clean site? If yes, print YES (in uppercase)"
    read READ
    if [[ $READ == "YES" ]]
    then
        :
    else
        echo "Canceled, exit"
        exit 1
    fi
fi

cd ../manage/
# CHECK STATUS OF DC #
echo "Check status of DC daemon. Please, wait..."
CHECK=$(./dc-daemon_status.sh | grep stopped)
if [[ $CHECK ]]
then
    echo "DC service not started. Canseled"
    exit 1
fi

# CHECK STATUS OF DTMD #
echo "Check status of DTM daemon. Please, wait..."
CHECK=$(./dtm-daemon_status.sh | grep stopped)
if [[ $CHECK ]]
then
    echo "DTM service not started. Canseled"
    exit 1
fi

#cd ../ftests/
# CREATE JSON #
#TEMPFILE=`mktemp /tmp/$(basename $0).XXXXXX`
#trap "rm -f $TEMPFILE" 0 1 2 5 15
#echo "{\"id\": \"$ID\", \"taskType\": 1, \"delayedType\": 1}" > $TEMPFILE

# CLEANUP #
#../manage/dc-client_start.sh "--command=SITE_CLEANUP --file=$TEMPFILE"

#LOG_FILE="../log/dc-client.log"
#if [ -f $LOG_FILE ];
#then
#  rm $LOG_FILE
#fi

TEMPFILE=`mktemp /tmp/$(basename $0).XXXXXX`
trap "rm -f $TEMPFILE" 0 1 2 5 15

FIELDS='{"id": "'$ID'", "taskType": 1, "delayedType": 1}'
cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=SITE_CLEANUP --fields="$FIELDS" > $TEMPFILE
cp $TEMPFILE /tmp/dc_test_sites_cleanup.log

parser $TEMPFILE

echo "Done"

exit 0