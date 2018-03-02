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
JSONDIR=$BUNDLE_DIR'/api/python/data/ftests/dc_test_static_site_check_proxy'

JSON_FIELD=$BUNDLE_DIR'/api/python/bin/json-field.py'
INI_FILE='../ini/dc-client.ini'

ERROR_MASK_PATH='itemsList:0:itemObject:0:dbFields:ErrorMask'
HTTP_CODE_PATH='itemsList:0:itemObject:0:dbFields:HttpCode'

FIELD_PATH='itemsList:0:itemObject:0:processedContents:0:buffer'
CHECK_TAGS=('0:title' '0:link' '0:body' '0:image')

PROXY_TMP_FILE='/tmp/0.json'

RAW_PATH='itemsList:0:itemObject:0:rawContents:0:buffer'
ERRORS_FOR_DEAD=('ERROR_FATAL' 'ERROR_GENERAL' 'ERROR_CONTENT_OR_COOKIE' 'ERROR_NAME_NOT_RESOLVED' 'ERROR_TOO_MANY_REDIRECTS' 'ERROR_MACRO_RETURN_VALUE' 'ERROR_PROXY_CONNECTION_FAILED' 'ERROR_CONNECTION_TIMED_OUT' 'ERROR_TUNNEL_CONNECTION_FAILED' 'ERROR_SERVICE_UNAVAILABLE' 'ERROR_CONFLICT' 'ERROR_EMPTY_RESPONSE')

JSONS_FAIL=0

IP_ADDRESS=$(/sbin/ifconfig  | grep 'inet addr:'| grep -v '127.0.0.' | cut -d: -f2 | awk '{ print $1}')

if [[ ! -d $JSONDIR ]]
then
    echo -e $RED"Directory "$JSONDIR" not found. Exit"$DEF
    exit 1
fi

TEMPFILE=$(mktemp /tmp/$(basename $0).XXXXX)
trap "rm -f $TEMPFILE" 0 1 2 5 15

function checkIgnored() {
    # $1 - input to check
    echo -n > $TEMPFILE
    echo "$1" | while read LINE
    do
        for I in "${IGNORED_FIELDS[@]}"
        do
            if [[ ! "$LINE" =~ "$I" ]]
            then
                echo -e $JSONFILE" -$RED fail, $LINE"$DEF >> $TEMPFILE
            fi
        done
    done
}

function checkDeadErrors(){
    CONTENT=$($JSON_FIELD --base64=1 --field=$RAW_PATH < $TEMPFILE)
    for ERROR in "${ERRORS_FOR_DEAD[@]}"
    do
        local CHECK_CONTENT=$(echo $CONTENT | grep $ERROR)
        if [[ $CHECK_CONTENT ]]
        then
            return 0
        fi
    done
    echo -e $RED"Failed: "$DEF"HttpCodeTest="$HTTP_CODE_CURRENT_NUMBER", HttpCodeReference="$HTTP_CODE_REFERENCE_NUMBER", type="$JSONS_TYPE", json="$JSONFILE
    FAIL=1
}

function checkOut(){
    # $1 - json directory
#    ./dc-client.py --config=$INI_FILE --command=BATCH --file=$1/$JSONFILE > $1/$JSONFILE.out
#    ./dc-client.py --config=$INI_FILE --command=BATCH --file=1/$JSONFILE
    rm -f $PROXY_TMP_FILE
    ./dc-client.py --config=$INI_FILE --command=BATCH --file=$1/$JSONFILE > $TEMPFILE
    ERROR_MASK_CURRENT_NUMBER=$($JSON_FIELD --field=$ERROR_MASK_PATH < $TEMPFILE)
    HTTP_CODE_CURRENT_NUMBER=$($JSON_FIELD --field=$HTTP_CODE_PATH < $TEMPFILE)

    echo -e $BLUE"Info: "$DEF"httpCode="$HTTP_CODE_CURRENT_NUMBER", errorMask="$ERROR_MASK_CURRENT_NUMBER", type="$JSONS_TYPE", json="$JSONFILE

    if [[ $ERROR_MASK_CURRENT_NUMBER -eq 0 ]]
    then
        ERROR_MASK_CURRENT=$ERROR_MASK_CURRENT_NUMBER
    else
        ERROR_MASK_CURRENT=$($JSON_FIELD --field=errors <<< $(./error-mask-info.py $ERROR_MASK_CURRENT_NUMBER))
    fi
    #HTTP_CODE_CURRENT=$($JSON_FIELD --field=errors <<< $(./error-mask-info.py $HTTP_CODE_CURRENT_NUMBER))

    ERROR_MASK_REFERENCE_NUMBER=$($JSON_FIELD --field=$ERROR_MASK_PATH < $1/$JSONFILE.out)
    HTTP_CODE_REFERENCE_NUMBER=$($JSON_FIELD --field=$HTTP_CODE_PATH < $1/$JSONFILE.out)
    if [[ $ERROR_MASK_REFERENCE_NUMBER -eq 0 ]]
    then
        ERROR_MASK_REFERENCE=$ERROR_MASK_REFERENCE_NUMBER
    else
        ERROR_MASK_REFERENCE=$($JSON_FIELD --field=errors <<< $(./error-mask-info.py $ERROR_MASK_REFERENCE_NUMBER))
    fi
    #HTTP_CODE_REFERENCE=$($JSON_FIELD --field=errors <<< $(./error-mask-info.py $HTTP_CODE_REFERENCE_NUMBER))

    FAIL=0

    CHECK_DEAD=$(echo $JSONFILE | grep DEAD_DEAD)
    if [[ $CHECK_DEAD ]]
    then
        if [[ $HTTP_CODE_CURRENT_NUMBER -ne $HTTP_CODE_REFERENCE_NUMBER ]]
        then
            if [[ $HTTP_CODE_CURRENT_NUMBER -eq 200 ]]
            then
                checkDeadErrors
            else
                echo -e $RED"Failed: "$DEF"HttpCodeTest="$HTTP_CODE_CURRENT_NUMBER", HttpCodeReference="$HTTP_CODE_REFERENCE_NUMBER", type="$JSONS_TYPE", json="$JSONFILE
                FAIL=1
            fi
        fi
        if [[ $ERROR_MASK_CURRENT_NUMBER -eq 0 ]]
        then
            echo -e $RED"Failed: "$DEF"ErrorMaskTest="$ERROR_MASK_CURRENT" (need not 0), type="$JSONS_TYPE", json="$JSONFILE
            FAIL=1
        fi
    else
        if [[ $HTTP_CODE_CURRENT_NUMBER -ne 200 ]]
        then
            echo -e $RED"Failed: "$DEF"HttpCodeTest="$HTTP_CODE_CURRENT_NUMBER" (need 200), type="$JSONS_TYPE", json="$JSONFILE
            FAIL=1
        fi
        if [[ $ERROR_MASK_CURRENT_NUMBER -ne 0 ]]
        then
            echo -e $RED"Failed: "$DEF"ErrorMaskTest="$ERROR_MASK_CURRENT" (need 0), type="$JSONS_TYPE", json="$JSONFILE
            FAIL=1
        fi

        if [[ $FAIL -eq 0 ]]
        then
            BUFFER=$($JSON_FIELD --base64=1 --field=$FIELD_PATH < $TEMPFILE)

            for TAG in "${CHECK_TAGS[@]}"
            do
                CHECK=$($JSON_FIELD --field="$TAG" <<< $BUFFER)
                if [[ ${CHECK:0:1} == "%" && ${CHECK: -1} == "%" ]]
                then
                    echo -e $RED"Failed: "$DEF", type="$JSONS_TYPE", json="$JSONFILE
                    FAIL=1
                fi
            done

        fi
    fi
    if [[ $FAIL -eq 1 ]]
    then
        JSONS_FAIL=$(($JSONS_FAIL+1))
    fi
}

rm -f $PROXY_TMP_FILE
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
