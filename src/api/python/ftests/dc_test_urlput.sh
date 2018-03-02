#!/bin/bash

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

CUR_DIR=$(pwd)/
JSONPARSER='../bin/json-field.py'

JSON_SITEDELETE="../data/ftests/dcc_site_delete_rnd.json"
JSON_SITENEW="../data/ftests/dcc_site_new_ok_rnd.json"
JSON_URLNEW="../data/ftests/dcc_url_new_rnd.json"
JSON_URLPUT="../data/ftests/dcc_url_put_rnd.json"
JSON_URLCONTENT="../data/ftests/dcc_url_content_put.json"
JSON_URLDELETE="../data/ftests/dcc_url_delete_rnd.json"

ERROR_OPERATION="itemsList:0:errorCode"

FIELDS=8
FIELDS_START="itemsList:0:itemObject:"

FIELDS_RAW=(":rawContents:0:buffer" "url_put_check-RAW" ":rawContents:0:typeId" "0" "url_put_check-RAW")
FIELDS_TIDY=(":rawContents:0:buffer" "url_put_check-TIDY" ":rawContents:0:typeId" "1" "url_put_check-TIDY")
FIELDS_HEADERS=(":headers:0:buffer" "url_put_check-HEADERS" ":headers:0:typeId" "2" "url_put_check-HEADERS")
FIELDS_REQUESTS=(":requests:0:buffer" "url_put_check-REQUESTS" ":requests:0:typeId" "3" "url_put_check-REQUESTS")
FIELDS_META=(":meta:0:buffer" "url_put_check-META" ":meta:0:typeId" "4" "url_put_check-META")
FIELDS_COOKIES=(":cookies:0:buffer" "url_put_check-COOKIES" ":cookies:0:typeId" "5" "url_put_check-COOKIES")
FIELDS_DYNAMIC=(":rawContents:0:buffer" "url_put_check-DYNAMIC" ":rawContents:0:typeId" "9" "url_put_check-DYNAMIC")
FIELDS_PROCESSOR=(":processedContents:0:buffer" "url_put_check-PROCESSOR" ":processedContents:0:typeId" "10" "url_put_check-PROCESSOR")

GOOD=()
ERROR=()

checkOperationError() {
    # $1 - first value
    # $2 - second value
    # $3 - operation
    if [[ $1 -ne $2 ]]
    then
        echo "Error in $3 operation. Exit"
        exit 1
    fi
}

function check() {
    # $1 - first value
    # $2 - second value
    if [[ $1 == $2 ]]
    then
        echo 'TRUE'
    else
        echo 'FALSE'
    fi
}

function out() {
    # $1 - content
    # $2 - value
    if [[ $2 == 'FALSE' ]]
    then
        ERROR+=("$1")
    else
        GOOD+=("$1")
    fi
}

echo "This test will delete (if exist) site id b85ab149a528bd0a024fa0f43e80b5fc Continue? y/[N]"
read -rs -n1 KEY
case "$KEY" in
    'y'|'Y')
        echo -e $YEL"Started..."$DEF
        ;;
    *)
        echo "Canceled"
        exit 0
        ;;
esac

# DELETE SITE #
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# SITE_NEW #
#echo -e $YEL"SITE_NEW OPERATION"$DEF
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

# URL_NEW #
#echo -e $YEL"URL_NEW OPERATION"$DEF
URL_NEW=$(../manage/dc-client_start.sh "--command=URL_NEW --file=$JSON_URLNEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $URL_NEW)
checkOperationError $CHECK_OPERATION 0 "URL_NEW"

# URL_PUT #
#echo -e $YEL"URL_PUT OPERATION"$DEF
URL_PUT=$(../manage/dc-client_start.sh "--command=URL_PUT --file=$JSON_URLPUT")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $URL_PUT)
checkOperationError $CHECK_OPERATION 0 "URL_PUT"

# URL_CONTENT #
#echo -e $YEL"URL_CONTENT OPERATION"$DEF
URL_CONTENT=$(../manage/dc-client_start.sh "--command=URL_CONTENT --file=$JSON_URLCONTENT")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $URL_CONTENT)
checkOperationError $CHECK_OPERATION 0 "URL_CONTENT"

# URL_DELETE #
#echo -e $YEL"URL_DELETE OPERATION"$DEF
URL_DELETE=$(../manage/dc-client_start.sh "--command=URL_DELETE --file=$JSON_URLDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $URL_DELETE)
checkOperationError $CHECK_OPERATION 0 "URL_DELETE"

# CHECK #
for FIELD in $(seq 0 $(($FIELDS-1)) )
do
    # RAW #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_RAW[2]}" <<< $URL_CONTENT) -eq ${FIELDS_RAW[3]} ]]
    then
        RAW_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_RAW[0]}" <<< $URL_CONTENT)
        RAW=$(check "$(echo $RAW_CHECK | base64 -d)" "${FIELDS_RAW[4]}")
    fi
    # TIDY #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_TIDY[2]}" <<< $URL_CONTENT) -eq ${FIELDS_TIDY[3]} ]]
    then
        TIDY_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_TIDY[0]}" <<< $URL_CONTENT)
        TIDY=$(check "$(echo $TIDY_CHECK | base64 -d)" "${FIELDS_TIDY[4]}")
    fi
    # HEADERS #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_HEADERS[2]}" <<< $URL_CONTENT) -eq ${FIELDS_HEADERS[3]} ]]
    then
        HEADERS_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_HEADERS[0]}" <<< $URL_CONTENT)
        HEADERS=$(check "$(echo $HEADERS_CHECK | base64 -d)" "${FIELDS_HEADERS[4]}")
    fi
    # REQUESTS #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_REQUESTS[2]}" <<< $URL_CONTENT) -eq ${FIELDS_REQUESTS[3]} ]]
    then
        REQUESTS_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_REQUESTS[0]}" <<< $URL_CONTENT)
        REQUESTS=$(check "$(echo $REQUESTS_CHECK | base64 -d)" "${FIELDS_REQUESTS[4]}")
    fi
    # META #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_META[2]}" <<< $URL_CONTENT) -eq ${FIELDS_META[3]} ]]
    then
        META_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_META[0]}" <<< $URL_CONTENT)
        META=$(check "$(echo $META_CHECK | base64 -d)" "${FIELDS_META[4]}")
    fi
    # COOKIES #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_COOKIES[2]}" <<< $URL_CONTENT) -eq ${FIELDS_COOKIES[3]} ]]
    then
        COOKIES_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_COOKIES[0]}" <<< $URL_CONTENT)
        COOKIES=$(check "$(echo $COOKIES_CHECK | base64 -d)" "${FIELDS_COOKIES[4]}")
    fi
    # DYNAMIC #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_DYNAMIC[2]}" <<< $URL_CONTENT) -eq ${FIELDS_DYNAMIC[3]} ]]
    then
        DYNAMIC_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_DYNAMIC[0]}" <<< $URL_CONTENT)
        DYNAMIC=$(check "$(echo $DYNAMIC_CHECK | base64 -d)" "${FIELDS_DYNAMIC[4]}")
    fi
    # PROCESSOR #
    if [[ $($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_PROCESSOR[2]}" <<< $URL_CONTENT) -eq ${FIELDS_PROCESSOR[3]} ]]
    then
        PROCESSOR_CHECK=$($JSONPARSER -f "$FIELDS_START$FIELD${FIELDS_PROCESSOR[0]}" <<< $URL_CONTENT)
        PROCESSOR=$(check "$PROCESSOR_CHECK" "${FIELDS_PROCESSOR[4]}")
    fi
done

# DONE #
out "RAW" "$RAW"
out "TIDY" "$TIDY"
out "HEADERS" "$HEADERS"
out "REQUESTS" "$REQUESTS"
out "META" "$META"
out "COOKIES" "$COOKIES"
out "DYNAMIC" "$DYNAMIC"
out "PROCESSOR" "$PROCESSOR"

if [[ ${#GOOD[@]} -ne 0 ]]
then
    echo -e $BLUE"Good: ${GOOD[@]}"$DEF
fi
if [[ ${#ERROR[@]} -ne 0 ]]
then
    echo -e $RED"Error: ${ERROR[@]}"$DEF
    exit 1
fi

exit 0
