#!/bin/bash

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

MYSQL_USER='hce'
MYSQL_PWD='hce12345'

CUR_DIR=$(pwd)/
JSONPARSER='../bin/json-field.py'

JSON_SITEDELETE="../data/ftests/dcc_site_delete_static.json"
JSON_SITENEW="../data/ftests/dcc_site_new_stats.json"
JSON_SITESUSPEND="../data/ftests/dcc_site_update_static_suspended.json"
JSON_SITEACTIVE="../data/ftests/dcc_site_update_static_active.json"
JSON_URLCLEANUP="../data/ftests/dcc_url_cleanup_stats.json"
JSON_URLDELETE="../data/ftests/dcc_url_delete_stats.json"

ERROR_OPERATION="itemsList:0:errorCode"

SITE_MD5="699fcf4591fc23e79b839d8819904293"
URL_MD5_ROOT="5c81a2a6e74d3800a85a22167c369251"
URL_MD5_CHECK="e6d30550c5d1cc668c5a9bae8e35e030"
URL_MD5_CHECK_CLEANUP="0a45bcc1980bde1ae8cd016792901f4d"
URL_MD5_CHECK_DELETE="f66715663feeb315c254f9f1e848d136"

DB_URLS="dc_urls"
TABLE_URLS="urls_$SITE_MD5"
DB_FREQS="dc_stat_freqs"
TABLE_FREQ="freq_$SITE_MD5"
DB_LOGS="dc_stat_logs"
TABLE_LOG="log_$SITE_MD5"

CRAWL_DELAY=120

ERROR=0

function SLEEP() {
    # $1 - message
    # $2 - sleep time
    # $3 - timeout
    echo -en $TUR"$1"
    for COUNT in $(seq 1 $(($2/$3)))
    do
        echo -n "."
        sleep $3
    done
    echo -e $DEF
}

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

checkError() {
    # $1 - first value
    # $2 - second value
    # $3 - message
    if [[ $1 -ne $2 ]]
    then
        echo -e $RED"Error: $3."$DEF
        ERROR=$(($ERROR+1))
    fi
}

checkErrorWithZero() {
    # $1 - first value
    # $2 - second value
    # $3 - message
    if [[ $1 -ne 0 && $2 -ne 0 ]]
    then
        if [[ $1 -ne $2 ]]
        then
            echo -e $RED"Error: $3."$DEF
            ERROR=$(($ERROR+1))
        fi
    else
        echo -e $RED"Zero. Error: $3."$DEF
        ERROR=$(($ERROR+1))
    fi
}

function mysqlCheckTable () {
    # $1 - database
    # $2 - table
    CHECK=$(mysql -u$MYSQL_USER -p$MYSQL_PWD -e "USE '$1'; SHOW TABLES LIKE'$2';" 2>/dev/null && echo || echo "FALSE")
    if [[ -z $CHECK ]]
    then
        echo "FALSE"
    else
        echo "TRUE"
    fi
}

function mysqlSelectWhere() {
    # $1 - db.table
    # $2 - field 4 select
    # $3 - where
    VALUE=$(mysql -u$MYSQL_USER -p$MYSQL_PWD -Bse "SELECT $2 FROM $1 WHERE $3")
    echo $VALUE
}

function mysqlRows() {
    # $1 - db.table
    # $2 - where
    if [[ "$2" ]]
    then
        echo $(mysql -u$MYSQL_USER -p$MYSQL_PWD -Bse "SELECT COUNT(*) FROM $1 WHERE $2")
    else
        echo $(mysql -u$MYSQL_USER -p$MYSQL_PWD -Bse "SELECT COUNT(*) FROM $1")
    fi
}

if [[ $1 == "force" || $1 == "-force" || $1 == "--force" ]]
then
    :
else
    echo -e $TUR"This test will delete (if exist) site id $SITE_MD5 Continue? y/[N]"$DEF
    read -rs -n1 KEY
    case "$KEY" in
        'y'|'Y')
            echo -e $YEL"Started..."$DEF
            ;;
        *)
            echo -e $TUR"Canceled"$DEF
            exit 0
            ;;
    esac
fi

# SITE_DELETE #
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# CHECK FOR TABLES #
CHECK_TABLE_FREQ=$(mysqlCheckTable "$DB_FREQS" "$TABLE_FREQ")
CHECK_TABLE_LOG=$(mysqlCheckTable "$DB_LOGS" "$TABLE_LOG")

checkError "$CHECK_TABLE_FREQ" "FALSE" "$DB_FREQS.$TABLE_FREQ exist"
checkError "$CHECK_TABLE_LOG" "FALSE" "$DB_LOGS.$TABLE_LOG exist"
# END DELETE SITE #

# SITE_NEW #
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

# CHECK FOR TABLES #
CHECK_TABLE_FREQ=$(mysqlCheckTable "$DB_FREQS" "$TABLE_FREQ")
CHECK_TABLE_LOG=$(mysqlCheckTable "$DB_LOGS" "$TABLE_LOG")

checkError "$CHECK_TABLE_FREQ" "TRUE" "$DB_FREQS.$TABLE_FREQ not exist"
checkError "$CHECK_TABLE_LOG" "TRUE" "$DB_LOGS.$TABLE_LOG not exist"

SLEEP "Eat sunflower seeds, drink buratino (crawling)" $CRAWL_DELAY 2

# URL_CLEANUP #
URL_CLEANUP=$(../manage/dc-client_start.sh "--command=URL_CLEANUP --file=$JSON_URLCLEANUP")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $URL_CLEANUP)
checkOperationError $CHECK_OPERATION 0 "URL_CLEANUP"

# URL_DELETE #
URL_DELETE=$(../manage/dc-client_start.sh "--command=URL_DELETE --file=$JSON_URLDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $URL_DELETE)
checkOperationError $CHECK_OPERATION 0 "URL_DELETE"

# SUSPEND SITE #
SITE_SUSPEND=$(../manage/dc-client_start.sh "--command=SITE_UPDATE --file=$JSON_SITESUSPEND")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_SUSPEND)
checkOperationError $CHECK_OPERATION 0 "SITE_SUSPEND"

SLEEP "Eat sunflower seeds, drink buratino (suspend site)" $CRAWL_DELAY 2

# ACTIVATE SITE #
SITE_ACTIVE=$(../manage/dc-client_start.sh "--command=SITE_UPDATE --file=$JSON_SITEACTIVE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_ACTIVE)
checkOperationError $CHECK_OPERATION 0 "SITE_ACTIVE"

SLEEP "Eat sunflower seeds, drink buratino (unsuspending site)" $(($CRAWL_DELAY*2)) 2

# GET VALUES FROM dc_stat_freqs #
FIns=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FIns" "URLMd5 LIKE '$URL_MD5_CHECK'")
FDel=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FDel" "URLMd5 LIKE '$URL_MD5_CHECK_DELETE'")
FUpd=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FUpd" "URLMd5 LIKE '$URL_MD5_CHECK'")
FNew=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FNew" "URLMd5 LIKE '$URL_MD5_CHECK'")
FCrawled=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FCrawled" "URLMd5 LIKE '$URL_MD5_CHECK'")
FProcessed=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FProcessed" "URLMd5 LIKE '$URL_MD5_CHECK'")
FAged=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FAged" "URLMd5 LIKE '$URL_MD5_CHECK'")
FDeleted=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FDeleted" "URLMd5 LIKE '$URL_MD5_CHECK_DELETE'")
FPurged=$(mysqlSelectWhere "$DB_FREQS.$TABLE_FREQ" "FPurged" "URLMd5 LIKE '$URL_MD5_CHECK'")

# GET VALUES FROM dc_stat_logs #
INSERT=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=20")
DELETE=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK_DELETE' AND OpCode=21")
UPDATE=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=22")
CLEANUP=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK_CLEANUP' AND OpCode=23")
AGING=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=24")
CONTENT=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=25")

NEW=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=1")
SELTECTED2CRAWL=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=2")
CRAWLING=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=3")
CRAWLED=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=4")
SELTECTED2PROCESS=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=5")
PROCESSING=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=6")
PROCESSED=$(mysqlRows "$DB_LOGS.$TABLE_LOG" "URLMd5 LIKE '$URL_MD5_CHECK' AND OpCode=7")

# CHECK FREQS #
checkErrorWithZero "$FPurged" "1" "FPurged = $FPurged"

# CHECK FREQS WITH LOGS #
checkErrorWithZero "$FIns" "$INSERT" "FIns ($DB_FREQS.$TABLE_FREQ) != INSERT ($DB_LOGS.$TABLE_LOG) or zero"
checkErrorWithZero "$FDel" "$DELETE" "FDel ($DB_FREQS.$TABLE_FREQ) != DELETE ($DB_LOGS.$TABLE_LOG) or zero"
checkErrorWithZero "$FUpd" "$UPDATE" "FUpd ($DB_FREQS.$TABLE_FREQ) != UPDATE ($DB_LOGS.$TABLE_LOG) or zero"
checkErrorWithZero "$FNew" "$NEW" "FNew ($DB_FREQS.$TABLE_FREQ) != NEW ($DB_LOGS.$TABLE_LOG) or zero"
checkErrorWithZero "$FCrawled" "$CRAWLED" "FCrawled ($DB_FREQS.$TABLE_FREQ) != CRAWLED ($DB_LOGS.$TABLE_LOG) or zero"
checkErrorWithZero "$FProcessed" "$PROCESSED" "FProcessed ($DB_FREQS.$TABLE_FREQ) != PROCESSED ($DB_LOGS.$TABLE_LOG) or zero"
checkErrorWithZero "$FAged" "$AGING" "FAged ($DB_FREQS.$TABLE_FREQ) != AGING ($DB_LOGS.$TABLE_LOG) or zero"

# CHECK LOGS #
checkErrorWithZero "$CLEANUP" "1" "CLEANUP = $CLEANUP"
checkErrorWithZero "$CONTENT" "1" "CONTENT = $CONTENT"
checkErrorWithZero "$SELTECTED2CRAWL" "1" "SELTECTED2CRAWL = $SELTECTED2CRAWL"
checkErrorWithZero "$CRAWLING" "1" "CRAWLING = $CRAWLING"
checkErrorWithZero "$SELTECTED2PROCESS" "1" "SELTECTED2PROCESS = $SELTECTED2PROCESS"
checkErrorWithZero "$PROCESSING" "1" "PROCESSING = $PROCESSING"

NOT_RECRAWLING=$(mysqlRows "$DB_URLS.$TABLE_URLS")
checkErrorWithZero "$NOT_RECRAWLING" "1" "Recrawling work (not root urls in $DB_URLS.$TABLE_URLS created)"

if [[ $ERROR -ne 0 ]]
then
    echo -e $RED"Test failed"$DEF
    exit 1
else
    echo -e $BLUE"Test complete. Done"$DEF
    exit 0
fi

