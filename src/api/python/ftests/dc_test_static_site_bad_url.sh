#!/bin/bash

if [[ $USER == 'root' ]]
then
  echo "You run script from root or sudo. Run from user. Exit"
  exit 1
fi

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

BUNDLE_DIR=$HOME'/hce-node-bundle'
JSONDIR=$BUNDLE_DIR'/api/python/data/ftests/dc_test_static_site_bad_url'

JSON_FIELD=$BUNDLE_DIR'/api/python/bin/json-field.py'
INI_FILE='../ini/dc-client.ini'

NETWORK_COMMUNICATION_TIMEOUT_PATH='error_code'
ERROR_MASK_PATH='itemsList:0:itemObject:0:dbFields:ErrorMask'
HTTP_CODE_PATH='itemsList:0:itemObject:0:dbFields:HttpCode'

JSONS_FAIL=0
JSONS_SUCCESS=0

IP_ADDRESS=$(/sbin/ifconfig  | grep 'inet addr:'| grep -v '127.0.0.' | cut -d: -f2 | awk '{ print $1}')

if [[ ! -d $JSONDIR ]]
then
    echo -e $RED"Directory "$JSONDIR" not found. Exit"$DEF
    exit 1
fi

TEMPFILE=$(mktemp /tmp/$(basename $0).XXXXX)
trap "rm -f $TEMPFILE" 0 1 2 5 15

function replaceJsonIp(){
    # $1 - json file with full path
    local URL_LINE=$(cat $1 | grep '"url":')
    local CHECK_LOCAL=$(echo $URL_LINE | grep '127.0.0.1')
    if [[ $CHECK_LOCAL ]]
    then
        local URL_LINK_OLD=$(echo $URL_LINE | awk '{print $2}' | sed 's/"//g')
        local URL_IP=$(echo $URL_LINK_OLD | awk -F'\/' '{print $3}' | sed 's/\\//g')
        local URL_LINK_NEW=$(echo $URL_LINK_OLD | sed 's/'$URL_IP'/'$IP_ADDRESS'/')
        local URL_LINK_NEW_NORMAL=$(echo $URL_LINK_NEW | sed 's/\\\//\//g')
        local MD5_NEW=$(echo -n $URL_LINK_NEW_NORMAL | md5sum | awk '{print $1}')
        local MD5_LINE=$(cat $1 | grep '"urlId":')
        local MD5_OLD=$(echo $MD5_LINE | awk '{print $2}' | sed 's/"//g')
        sed -i 's/'$URL_IP'/'$IP_ADDRESS'/g' $1
        sed -i 's/'$MD5_OLD'/'$MD5_NEW'/g' $1
    fi
}


function checkOut(){
    # $1 - json directory
#    ./dc-client.py --config=$INI_FILE --command=BATCH --file=$1/$JSONFILE > $1/$JSONFILE.out
    ./dc-client.py --config=$INI_FILE --command=BATCH --file=$1/$JSONFILE > $TEMPFILE

    # CHECK "Network communicate timeout"
    local CHECK_NETWORK_TIMEOUT=$($JSON_FIELD --field=$NETWORK_COMMUNICATION_TIMEOUT_PATH < $TEMPFILE)
    local CHECK_PROXY_FILE=$(echo $JSONFILE | grep PROXY_FAIL)
    if [[ $CHECK_NETWORK_TIMEOUT != 1 && -z $CHECK_PROXY_FILE ]]
    then
        local HTTP_CODE_CURRENT_NUMBER=$($JSON_FIELD --field=$HTTP_CODE_PATH < $TEMPFILE)
        local HTTP_CODE_REFERENCE_NUMBER=$($JSON_FIELD --field=$HTTP_CODE_PATH < $1/$JSONFILE.out)

        local ERROR_MASK_CURRENT_NUMBER=$($JSON_FIELD --field=$ERROR_MASK_PATH < $TEMPFILE)
        if [[ $ERROR_MASK_CURRENT_NUMBER -eq 0 ]]
        then
            ERROR_MASK_CURRENT=$ERROR_MASK_CURRENT_NUMBER
        else
            ERROR_MASK_CURRENT=$($JSON_FIELD --field=errors <<< $(./error-mask-info.py $ERROR_MASK_CURRENT_NUMBER))
        fi

        local ERROR_MASK_REFERENCE_NUMBER=$($JSON_FIELD --field=$ERROR_MASK_PATH < $1/$JSONFILE.out)
        if [[ $ERROR_MASK_REFERENCE_NUMBER -eq 0 ]]
        then
            ERROR_MASK_REFERENCE=$ERROR_MASK_REFERENCE_NUMBER
        else
            ERROR_MASK_REFERENCE=$($JSON_FIELD --field=errors <<< $(./error-mask-info.py $ERROR_MASK_REFERENCE_NUMBER))
        fi

        local FAIL=0
        if [[ $ERROR_MASK_CURRENT_NUMBER != $ERROR_MASK_REFERENCE_NUMBER ]]
        then
            echo -e $RED"Failed: "$DEF"ErrorMaskTest="$ERROR_MASK_CURRENT", ErrorMaskReference="$ERROR_MASK_REFERENCE", type="$JSONS_TYPE", json="$JSONFILE
            local FAIL=1
        fi
        if [[ $HTTP_CODE_CURRENT_NUMBER != $HTTP_CODE_REFERENCE_NUMBER ]]
        then
            echo -e $RED"Failed: "$DEF"HttpCodeTest="$HTTP_CODE_CURRENT_NUMBER", HttpCodeReference="$HTTP_CODE_REFERENCE_NUMBER", type="$JSONS_TYPE", json="$JSONFILE
            local FAIL=1
        fi

        if [[ $FAIL -eq 1 ]]
        then
            JSONS_FAIL=$(($JSONS_FAIL+1))
        else
            JSONS_SUCCESS=$(($JSONS_SUCCESS+1))
        fi
    fi
}

cd $BUNDLE_DIR/api/python/bin

chmod +x error-mask-info.py

JSONS_TYPE='static'
JSONS_ALL=$(ls $JSONDIR/$JSONS_TYPE | grep '.json.out' | grep $IP_ADDRESS | wc -l)
for OUT in $(ls $JSONDIR/$JSONS_TYPE | grep '.json.out' | grep $IP_ADDRESS)
do
    JSONFILE=${OUT%.out}
    checkOut $JSONDIR/$JSONS_TYPE
done

JSONS_TYPE='dynamic'
JSONS_ALL=$(($JSONS_ALL+$(ls $JSONDIR/$JSONS_TYPE | grep '.json.out' | grep $IP_ADDRESS | wc -l)))
for OUT in $(ls $JSONDIR/$JSONS_TYPE | grep '.json.out' | grep $IP_ADDRESS)
do
    JSONFILE=${OUT%.out}
    checkOut $JSONDIR/$JSONS_TYPE
done

if [[ $JSONS_FAIL -gt 0 ]]
then
    echo -e $RED"Number of fails: "$JSONS_FAIL" from "$JSONS_ALL $DEF
    echo -e $RED"Test Failed"$DEF
    exit 1
fi

echo -e $BLUE"Number of success: "$JSONS_SUCCESS" from "$JSONS_ALL $DEF
echo -e $BLUE"Test Success"$DEF
exit 0
