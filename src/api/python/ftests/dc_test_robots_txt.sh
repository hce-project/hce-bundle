#!/bin/bash

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

SILENT=0
HCE_PWD=''
MYSQL_USER='hce'
MYSQL_PWD='hce12345'

CUR_DIR=$(pwd)
JSONPARSER='../bin/json-field.py'

JSON_SITEDELETE="../data/ftests/dcc_site_delete_static.json"
JSON_SITENEW="../data/ftests/dcc_site_new_robots_static.json"

ERROR_OPERATION="itemsList:0:errorCode"

WWW_DIR="/var/www"
TEST_DIR="robots"
ROBOTSTXT="robots.txt"
SITE_MD5="699fcf4591fc23e79b839d8819904293"
URL_MD5_ROOT="90fec81f2cc0b58f6a7f95ee8b883728"
URL_MD5_CHECK_1="5abe815b1fe031060762b6696daaf03c"
URL_MD5_CHECK_2="6735566e28590d22f3d51fabb234cf8f"
URL_MD5_CHECK_3="51899e69aaa2a96f6c1d2d3a9a44b927"

DB_CONTENT="dc_contents"
TABLE_CONTENT="contents_$SITE_MD5"
DB_URLS="dc_urls"
TABLE_URLS="urls_$SITE_MD5"

CRAWL_DELAY=30

ERROR=0
GOOD=0
GOOD_PASSED=5

if [[ $(whoami) == "root" ]]
then
    trap "rm -rf $CUR_DIR/../log/*" 0 1 2 5 15
fi

function SLEEP() {
    # $1 - message
    # $2 - sleep time
    # $3 - timeout
    if [[ $SILENT -eq 1 ]]
    then
        sleep $2
    else
        echo -en $TUR"$1"
        for COUNT in $(seq 1 $(($2/$3)))
        do
            echo -n "."
            sleep $3
        done
        echo -e $DEF
    fi
}

checkOperationError() {
    # $1 - first value
    # $2 - second value
    # $3 - operation
    if [[ $1 -ne $2 ]]
    then
        if [[ $SILENT -eq 1 ]]
        then
            rm -f $WWW_DIR/$ROBOTSTXT
            exit 1
        else
            echo -e $RED"Error in $3 operation. Exit"$DEF
            rm -f $WWW_DIR/$ROBOTSTXT
            exit 1
        fi
    fi
}

checkError() {
    # $1 - first value
    # $2 - second value
    # $3 - message
    if [[ $1 -ne $2 ]]
    then
        if [[ $SILENT -eq 1 ]]
        then
            ERROR=$(($ERROR+1))
        else
            echo -e $RED"Error: $3."$DEF
            ERROR=$(($ERROR+1))
        fi
    fi
}

checkGood(){
    # $1 - first value
    # $2 - second value
    if [[ $1 -eq $2 ]]
    then
        GOOD=$(($GOOD+1))
        if [[ $SILENT -eq 0 ]]
        then
            echo -e $BLUE"Test passed"$DEF
        fi
    fi
}

function checkWWW(){
    if [ ! -w $WWW_DIR ]
    then
        if [[ $SILENT -eq 1 ]]
        then
            exit 1
        else
            echo -e $RED"Directory $WWW_DIR not writable (or missing) Add write permission for user $USER."$DEF
            exit 1
        fi
    fi
}

function checkRobotsDir(){
    if [ ! -w $WWW_DIR/$TEST_DIR ]
    then
        if [[ $SILENT -eq 1 ]]
        then
            exit 1
        else
            echo -e $RED"Directory $WWW_DIR/$ROBOTSTXT not writable (or missing). Copy her from test site"$DEF
            exit 1
        fi
    fi
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

function mysqlSelect() {
    # $1 - db.table
    # $2 - field 4 select
    # $3 - where
    if [[ "$3" ]]
    then
        echo $(mysql -u$MYSQL_USER -p$MYSQL_PWD -Bse "SELECT $2 FROM $1 WHERE $3")
    else
        echo $(mysql -u$MYSQL_USER -p$MYSQL_PWD -Bse "SELECT $2 FROM $1")
    fi
}

if [[ $1 == "silent" || $1 == "-silent" || $1 == "--silent" ]]
then
    SILENT=1
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

checkWWW
checkRobotsDir

# STAGE 1 #
if [[ $SILENT -ne 1 ]]
then
    echo -e $YEL"Stage 1. Dissalow all"$DEF
fi
# CREATE robots.txt WITH DISALLOW ALL #
echo "User-agent: *
Disallow: /" > $WWW_DIR/$ROBOTSTXT

# SITE_DELETE #
#../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE"
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# SITE_NEW #
#../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW"
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

SLEEP "Eat sunflower seeds, drink buratino" $CRAWL_DELAY 2

TMPCHECK_BEFORE=$ERROR

# CHECK TABLES #
CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT")
checkError "$CHECK" "0" "Robots.txt not work. Content table is not empty"

CHECK=$(mysqlRows "$DB_URLS.$TABLE_URLS")
checkError "$CHECK" "1" "Robots.txt not work. Urls crowley"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "4" "Robots.txt not work. Root url status != 4"

checkGood $TMPCHECK_BEFORE $ERROR

# STAGE 2 #
if [[ $SILENT -ne 1 ]]
then
    echo -e $YEL"Stage 2. Allow all"$DEF
fi
# CREATE robots.txt WITH DISALLOW ALL #
echo "User-agent: *
Allow: /" > $WWW_DIR/$ROBOTSTXT

# SITE_DELETE #
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# SITE_NEW #
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

SLEEP "Eat sunflower seeds, drink buratino" $(($CRAWL_DELAY*4)) 2

TMPCHECK_BEFORE=$ERROR

# CHECK TABLES #
CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT")
checkError "$CHECK" "4" "Robots.txt not work. Rows in content table != 4 ($CHECK row)"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_ROOT != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_1'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_CHECK_1 != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_CHECK_2 != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_3'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_CHECK_3 != 1"


CHECK=$(mysqlRows "$DB_URLS.$TABLE_URLS")
checkError "$CHECK" "4" "Robots.txt not work. Urls in urls table != 4"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_ROOT status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_1'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_CHECK_1 status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_CHECK_2 status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_3'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_CHECK_3 status != 7"

checkGood $TMPCHECK_BEFORE $ERROR

# STAGE 3 #
if [[ $SILENT -ne 1 ]]
then
    echo -e $YEL"Stage 3. Allow only from GoogleBot"$DEF
fi
# CREATE robots.txt WITH DISALLOW ALL #
echo "User-agent: Googlebot
Allow: /
User-agent: *
Disallow: /" > $WWW_DIR/$ROBOTSTXT

# SITE_DELETE #
#../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE"
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# SITE_NEW #
#../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW"
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

SLEEP "Eat sunflower seeds, drink buratino" $CRAWL_DELAY 2

TMPCHECK_BEFORE=$ERROR

# CHECK TABLES #
CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT")
checkError "$CHECK" "0" "Robots.txt not work. Content table is not empty"

CHECK=$(mysqlRows "$DB_URLS.$TABLE_URLS")
checkError "$CHECK" "1" "Robots.txt not work. Urls crowley"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "4" "Robots.txt not work. Root url status != 4"

checkGood $TMPCHECK_BEFORE $ERROR

# STAGE 4 #
if [[ $SILENT -ne 1 ]]
then
    echo -e $YEL"Stage 4. Disallow one directory"$DEF
fi
# CREATE robots.txt WITH DISALLOW ALL #
echo "User-agent: *
Disallow: /$TEST_DIR/
Allow: /" > $WWW_DIR/$ROBOTSTXT

# SITE_DELETE #
#../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE"
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# SITE_NEW #
#../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW"
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

SLEEP "Eat sunflower seeds, drink buratino" $(($CRAWL_DELAY*4)) 2

TMPCHECK_BEFORE=$ERROR

# CHECK TABLES #
CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT")
checkError "$CHECK" "2" "Robots.txt not work. Rows in content table != 2 ($CHECK row)"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_ROOT != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_1'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_CHECK_1 != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "0" "Robots.txt not work. Rows whith $URL_MD5_CHECK_2 != 0"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_3'")
checkError "$CHECK" "0" "Robots.txt not work. Rows whith $URL_MD5_CHECK_3 != 0"


CHECK=$(mysqlRows "$DB_URLS.$TABLE_URLS")
checkError "$CHECK" "3" "Robots.txt not work. Urls in urls table != 3"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_ROOT status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_1'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_CHECK_1 status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "4" "Robots.txt not work. $URL_MD5_CHECK_2 status != 4"

checkGood $TMPCHECK_BEFORE $ERROR

# STAGE 5 #
if [[ $SILENT -ne 1 ]]
then
    echo -e $YEL"Stage 5. Allow one directory, disallow all other"$DEF
fi
# CREATE robots.txt WITH DISALLOW ALL #
echo "User-agent: *
Allow: /robots.html
Allow: /$TEST_DIR/
Disallow: /" > $WWW_DIR/$ROBOTSTXT

# SITE_DELETE #
#../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE"
SITE_DELETE=$(../manage/dc-client_start.sh "--command=SITE_DELETE --file=$JSON_SITEDELETE")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_DELETE"

# SITE_NEW #
#../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW"
SITE_NEW=$(../manage/dc-client_start.sh "--command=SITE_NEW --file=$JSON_SITENEW")
CHECK_OPERATION=$($JSONPARSER -f "$ERROR_OPERATION" <<< $SITE_NEW)
checkOperationError $CHECK_OPERATION 0 "SITE_NEW"

SLEEP "Eat sunflower seeds, drink buratino" $(($CRAWL_DELAY*4)) 2

TMPCHECK_BEFORE=$ERROR

# CHECK TABLES #
CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT")
checkError "$CHECK" "3" "Robots.txt not work. Rows in content table != 3 ($CHECK row)"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_ROOT != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_1'")
checkError "$CHECK" "0" "Robots.txt not work. Rows whith $URL_MD5_CHECK_1 != 0"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_CHECK_2 != 1"

CHECK=$(mysqlRows "$DB_CONTENT.$TABLE_CONTENT" "id LIKE '$URL_MD5_CHECK_3'")
checkError "$CHECK" "1" "Robots.txt not work. Rows whith $URL_MD5_CHECK_3 != 1"


CHECK=$(mysqlRows "$DB_URLS.$TABLE_URLS")
checkError "$CHECK" "4" "Robots.txt not work. Urls in urls table != 4"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_ROOT'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_ROOT status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_1'")
checkError "$CHECK" "4" "Robots.txt not work. $URL_MD5_CHECK_1 status != 4"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_CHECK_2 status != 7"

CHECK=$(mysqlSelect "$DB_URLS.$TABLE_URLS" "Status" "URLMd5 LIKE '$URL_MD5_CHECK_2'")
checkError "$CHECK" "7" "Robots.txt not work. $URL_MD5_CHECK_2 status != 7"

checkGood $TMPCHECK_BEFORE $ERROR

rm -f $WWW_DIR/$ROBOTSTXT

if [[ $ERROR -ne 0 ]]
then
    exit 1
fi

if [[ $GOOD -eq $GOOD_PASSED && $SILENT -eq 0 ]]
then
    echo -e $BLUE"ALL tests passed successfully"$DEF
fi

exit 0
