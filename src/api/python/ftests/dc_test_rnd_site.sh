#!/bin/bash

SCRIPT_NAME=$(basename $0)
FORCE=0
IGNORE=0
GOOD_RESULT=()
ERROR_RESULT=()

for ARG in $*
do
    case $ARG in
    'force'|'-force'|'--force') FORCE=1;;
    'ignore'|'-ignore'|'--ignore') IGNORE=1;;
    'help'|'-help'|'--help'|*) echo "Usage: $0 [force or -force or --force: force start, without warning message] [ignore or -ignore or --ignore: ignore operation error] [help or -help or --help: this help]"
        exit 1;;
    esac
done

if [[ $FORCE -eq 0 ]]
then
    echo ""
    read -p "WARNING! This test completely removes all data from DC's DB, delete logs and all service's data! Enter 'yes' to continue? "
    if [[ "$REPLY" != "yes" ]]
    then
        echo "Test cancelled!"
        echo ""
        exit 1
    fi
fi

SCRIPT_NAME=$(basename $0)
LOG_PATH="../log"
LOG=$SCRIPT_NAME".log"

CRAWL_DELAY=120
DELETE_DELAY=90
COUNT_OPERATION=0
ERROR_PATH=("itemsList:0:errorCode" "itemsList:0:errorMessage" "itemsList:0:host" "itemsList:0:port" "itemsList:0:node")
NULL_CONTENT="itemsList:0:itemObject"
STATUS0=("itemsList:0:itemObject:0:status" "status" "itemsList:0:host" "itemsList:0:port" "itemsList:0:node")
STATUS1=("itemsList:0:itemObject:1:status" "status" "itemsList:0:host" "itemsList:0:port" "itemsList:0:node")
STATUS2=("itemsList:0:itemObject:2:status" "status" "itemsList:0:host" "itemsList:0:port" "itemsList:0:node")
TAGS_COUNT0=("itemsList:0:itemObject:0:dbFields:TagsCount" "tags_count" "itemsList:0:host" "itemsList:0:port" "itemsList:0:node")
TAGS_COUNT2=("itemsList:0:itemObject:2:dbFields:TagsCount" "tags_count" "itemsList:0:host" "itemsList:0:port" "itemsList:0:node")
RAW_CONTENTS1="itemsList:0:itemObject:1:rawContents"
PROCESSED_CONTENTS1="itemsList:0:itemObject:1:processedContents"
URL_MD52="itemsList:0:itemObject:2:urlMd5"

JSONPARSER='../bin/json-field.py'

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

TEMPFILE=`mktemp /tmp/dc_test_rnd_site.XXXXXX`
trap "rm -f $TEMPFILE" 0 1 2 5 15

function scriptExit(){
    [ ${#GOOD_RESULT[@]} -ne 0 ] && echo -e $BLUE"Passed tests:$DEF "$(echo ${GOOD_RESULT[@]} | sed 's/ /, /g')
    [ ${#ERROR_RESULT[@]} -ne 0 ] && echo -e $RED"Failed tests:$DEF "$(echo ${ERROR_RESULT[@]} | sed 's/ /, /g') && exit 1
    exit 0
}

function checkErrors(){
    # $1 - file with temp log
    # $2 - command
    # $3 - error number
    # $4 - error path
    # $5 - error message path
    # $6 - error host
    # $7 - error port
    # $8 - error node
    # CHECK FOR DC SERVICE ERROR #
    CHECK=$(awk -F \: '/error_message/ {print $2}' $1)
    if [[ $CHECK ]]
    then
        echo $2 "dc error: "$CHECK
        ERROR_RESULT+=("$2_$(($COUNT_OPERATION-1))")
        if [[ $IGNORE -eq 0 ]]
        then
            scriptExit
        fi
        return 1
    fi

    ERROR_CHECK=$($JSONPARSER  --field="$4" < $1)
    MESSAGES_CHECK=$($JSONPARSER  --field="$5" < $1)
    HOSTS_CHECK=$($JSONPARSER  --field="$6" < $1)
    PORTS_CHECK=$($JSONPARSER  --field="$7" < $1)
    NODES_CHECK=$($JSONPARSER  --field="$8" < $1)

    IFS_ORIGINAL=$IFS
    IFS=";"
    read -a ERRORS <<< "$ERROR_CHECK"
    read -a MESSAGES <<< "$MESSAGES_CHECK"
    read -a HOSTS <<< "$HOSTS_CHECK"
    read -a PORTS <<< "$PORTS_CHECK"
    read -a NODES <<< "$NODES_CHECK"
    IFS=$IFS_ORIGINAL

    ERROR_COUNT=0
    for ERROR in "${ERRORS[@]}"
    do
        if [[ $ERROR -ne $3 ]]
        then
            if [[ $5 == "status" ]]
            then
                MSG="Bad status code ($ERROR), need $3"
            elif [[ $5 == "tags_count" ]]
            then
                MSG="Bad tags_count code ($ERROR), need $3"
            else
                MSG=$($JSONPARSER  --field="$5" < $1)
            fi
            echo $2 "error number "$ERROR": "$MSG", ${HOSTS[$ERROR_COUNT]}:${PORTS[$ERROR_COUNT]}, ${NODES[$ERROR_COUNT]}"
            echo -e "\n#-#FATAL:"$2" error="$ERROR"-#" >> $LOG_PATH/$LOG
            ERROR_RESULT+=("$2_$(($COUNT_OPERATION-1))#${HOSTS[$ERROR_COUNT]}:${PORTS[$ERROR_COUNT]}#${NODES[$ERROR_COUNT]}")
            if [[ $IGNORE -eq 0 ]]
            then
                scriptExit
            fi
        else
            GOOD_RESULT+=("$2_$(($COUNT_OPERATION-1))")
        fi
    ERROR_COUNT=$((ERROR_COUNT+1))
    done
}

function checkReverseErrors(){
    # $1 - file with temp log
    # $2 - command
    # $3 - error number
    # $4 - error path
    # $5 - error message path
    # $6 - error host
    # $7 - error port
    # $8 - error node
    # CHECK FOR DC SERVICE ERROR #
    CHECK=$(awk -F \: '/error_message/ {print $2}' $1)
    if [[ $CHECK ]]
    then
        echo $2 "dc error: "$CHECK
        ERROR_RESULT+=("$2_$(($COUNT_OPERATION-1))")
        if [[ $IGNORE -eq 0 ]]
        then
            scriptExit
        fi
        return 1
    fi
    ERROR_CHECK=$($JSONPARSER  --field="$4" < $1)
    MESSAGES_CHECK=$($JSONPARSER  --field="$5" < $1)
    HOSTS_CHECK=$($JSONPARSER  --field="$6" < $1)
    PORTS_CHECK=$($JSONPARSER  --field="$7" < $1)
    NODES_CHECK=$($JSONPARSER  --field="$8" < $1)

    IFS_ORIGINAL=$IFS
    IFS=";"
    read -a ERRORS <<< "$ERROR_CHECK"
    read -a MESSAGES <<< "$MESSAGES_CHECK"
    read -a HOSTS <<< "$HOSTS_CHECK"
    read -a PORTS <<< "$PORTS_CHECK"
    read -a NODES <<< "$NODES_CHECK"
    IFS=$IFS_ORIGINAL

    ERROR_COUNT=0
    for ERROR in "${ERRORS[@]}"
    do
        if [[ $ERROR -eq $3 ]]
        then
            if [[ $5 == "status" ]]
            then
                MSG="Bad status code ($ERROR), need not $3"
            elif [[ $5 == "tags_count" ]]
            then
                MSG="Bad tags_count code ($ERROR), need not $3"
            else
                MSG=$($JSONPARSER  --field="$5" < $1)
            fi
            echo $2 "error number "$ERROR": "$MSG", ${HOSTS[$ERROR_COUNT]}:${PORTS[$ERROR_COUNT]}, ${NODES[$ERROR_COUNT]}"
            echo -e "\n#-#FATAL:"$2" error="$ERROR"-#" >> $LOG_PATH/$LOG
            ERROR_RESULT+=("$2_$(($COUNT_OPERATION-1))#${HOSTS[$ERROR_COUNT]}:${PORTS[$ERROR_COUNT]}#${NODES[$ERROR_COUNT]}")
            if [[ $IGNORE -eq 0 ]]
            then
                scriptExit
            fi
        else
            GOOD_RESULT+=("$2_$(($COUNT_OPERATION-1))")
        fi
    ERROR_COUNT=$((ERROR_COUNT+1))
    done
}

function checkNullContent(){
    # $1 - file with temp log
    # $2 - command
    CONTENT=$($JSONPARSER  --field="$NULL_CONTENT" < $1)
    if [[ $CONTENT == "[]" ]]
    then
        ERROR_RESULT+=("$2_$(($COUNT_OPERATION-1))#ZERO_ITEMS")
        if [[ $IGNORE -eq 0 ]]
        then
            scriptExit
        fi
        return 1
    else
        return 0
    fi
}

function checkStringErrors(){
    # $1 - file with temp log
    # $2 - command
    # $3 - error string
    # $4 - error path
    # $5 - error message
    ERROR=$($JSONPARSER  --field="$4" < $1)
    if [[ $ERROR != "$3" ]]
    then
        MSG="$5"
        echo $2 "error: "$MSG
        echo -e "\n#-#FATAL:"$2" error="$ERROR"-#" >> $LOG_PATH/$LOG
        ERROR_RESULT+=("$2_$(($COUNT_OPERATION-1))")
        if [[ $IGNORE -eq 0 ]]
        then
            scriptExit
        fi
    else
        GOOD_RESULT+=("$2_$(($COUNT_OPERATION-1))")
    fi
}

#Remove log files
if [[ -f $LOG_PATH/* ]]
then
    rm $LOG_PATH/*
fi
echo "" > $LOG_PATH/$LOG 2>&1

# ADD and Check Permissions #
cd ../../../usr/bin/
./hce-node-permissions.sh
CHECK_PERM=$(./check_permissions.sh)
cd ../../api/python/ftests/
if [[ $CHECK_PERM =~ 'Error' ]]
then
    echo 'Error: Permissions error'
    echo $CHECK_PERM >> $LOG_PATH/$LOG
    echo "#-#FATAL:PERMISSIONS_ERROR-#"  >> $LOG_PATH/$LOG
    scriptExit
fi

# OPERATION 0 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"Prepare"$DEF
#Before actions
source ./dc_tests_before.sh

sleep 2

# OPERATION 1 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"SITE_FIND"$DEF
echo -e "\n#-#\nSite find" >> $LOG_PATH/$LOG 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_rnd.json | tee -a $LOG_PATH/$LOG 2>&1 > $TEMPFILE
checkErrors $TEMPFILE SITE_FIND 0 ${ERROR_PATH[@]}

# OPERATION 2 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"SITE_DELETE"$DEF
echo -e "\n#-#\nDelete site" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=SITE_DELETE --file=../data/ftests/dcc_site_delete_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE SITE_DELETE 0 ${ERROR_PATH[@]}

# OPERATION 3 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"SITE_NEW"$DEF
echo -e "\n#-#\nCreate new site" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=SITE_NEW --file=../data/ftests/dcc_site_new_ok_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE SITE_NEW 0 ${ERROR_PATH[@]}

# OPERATION 4 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"SITE_FIND"$DEF
echo -e "\n#-#\nSite find" >> $LOG_PATH/$LOG 2>&1
../bin/dc-client.py --config=../ini/dc-client.ini --command=SITE_FIND --file=../data/ftests/dcc_site_find_rnd.json | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE SITE_FIND 0 ${ERROR_PATH[@]}

# OPERATION 5 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"SITE_STATUS"$DEF
echo -e "\n#-#\nCheck site status before crawling" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE SITE_STATUS 0 ${ERROR_PATH[@]}

# OPERATION 6 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_NEW"$DEF
echo -e "\n#-#\nAdd new URL" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_NEW --file=../data/ftests/dcc_url_new_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_NEW 0 ${ERROR_PATH[@]}

# OPERATION 7 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_STATUS"$DEF
echo -e "\n#-#\nCheck URLs status before crawling" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_STATUS --file=../data/ftests/dcc_url_status_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_STATUS 0 ${ERROR_PATH[@]}

echo -e "\n#-#\nCrawling started at:" >> $LOG_PATH/$LOG 2>&1
date >> $LOG_PATH/$LOG 2>&1

echo -e "\n#-#\nSleep $CRAWL_DELAY sec" >> $LOG_PATH/$LOG 2>&1
sleep $CRAWL_DELAY

echo -e "\n#-#\nCrawling finished 1 at:" >> $LOG_PATH/$LOG 2>&1
date >> $LOG_PATH/$LOG 2>&1

# OPERATION 8 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"SITE_STATUS"$DEF
echo -e "\n#-#\nCheck sites status after crawling" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE SITE_STATUS 0 ${ERROR_PATH[@]}

# OPERATION 9 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_STATUS"$DEF
echo -e "\n#-#\nCheck URLs status after crawling" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_STATUS --file=../data/ftests/dcc_url_status_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_STATUS 0 ${ERROR_PATH[@]}

# OPERATION 10 #
sleep $CRAWL_DELAY
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_CONTENT"$DEF
echo -e "\n#-#\nGet data of URL" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_CONTENT 0 ${ERROR_PATH[@]}

if $(checkNullContent $TEMPFILE "URL_CONTENT")
then
    checkErrors $TEMPFILE URL_CONTENT 4 ${STATUS0[@]}
    #checkErrors $TEMPFILE URL_CONTENT 7 ${STATUS0[@]}
    #checkReverseErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT0[@]}

    checkErrors $TEMPFILE URL_CONTENT 0 ${STATUS1[@]}
    checkStringErrors $TEMPFILE URL_CONTENT "[]" $RAW_CONTENTS1 "raw_contents_error"
    checkStringErrors $TEMPFILE URL_CONTENT "[]" $PROCESSED_CONTENTS1 "processed_contents_error"

    checkErrors $TEMPFILE URL_CONTENT 4 ${STATUS2[@]}
    #checkErrors $TEMPFILE URL_CONTENT 7 ${STATUS2[@]}
    #checkReverseErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT2[@]}
fi

#echo "Cleanup sites data" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=SITE_CLEANUP --file=../data/ftests/dcc_site_cleanup_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
#checkErrors $TEMPFILE SITE_CLEANUP

#echo "Update site" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=SITE_UPDATE --file=../data/ftests/dcc_site_update_rnd.json" >> $LOG_PATH/$LOG 2>&1

#echo "Check sites status after update" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_rnd.json" >> $LOG_PATH/$LOG 2>&1

# OPERATION 11 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_UPDATE"$DEF
echo "Update URL with put content" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_UPDATE --file=../data/ftests/dcc_url_update_rnd.json " | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_UPDATE 0 ${ERROR_PATH[@]}

#echo "Crawling started at:" >> $LOG_PATH/$LOG 2>&1
#date >> $LOG_PATH/$LOG 2>&1

#echo "Sleep 60 sec" >> $LOG_PATH/$LOG 2>&1
#sleep 60

#echo "Crawling finished 2 at:" >> $LOG_PATH/$LOG 2>&1
#date >> $LOG_PATH/$LOG 2>&1

#echo "Check sites status after crawling" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_rnd.json" >> $LOG_PATH/$LOG 2>&1

# OPERATION 12 #
sleep $CRAWL_DELAY
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_CONTENT"$DEF
echo "Get URL content before delete" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_CONTENT 0 ${ERROR_PATH[@]}

if [[ $(checkNullContent $TEMPFILE "URL_CONTENT") -eq 0 ]]
then
    checkErrors $TEMPFILE URL_CONTENT 4 ${STATUS0[@]}
    #checkErrors $TEMPFILE URL_CONTENT 7 ${STATUS0[@]}
    #checkReverseErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT0[@]}

    checkErrors $TEMPFILE URL_CONTENT 0 ${STATUS1[@]}
    checkStringErrors $TEMPFILE URL_CONTENT "[]" $RAW_CONTENTS1 "raw_contents_error"
    checkStringErrors $TEMPFILE URL_CONTENT "[]" $PROCESSED_CONTENTS1 "processed_contents_error"

    #checkReverseErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT2[@]}
fi

# OPERATION 13 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_DELETE"$DEF
echo "Delete URLs and resources crawled" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_DELETE --file=../data/ftests/dcc_url_delete_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_DELETE 0 ${ERROR_PATH[@]}

echo -e "\n#-#\nSleep $DELETE_DELAY sec" >> $LOG_PATH/$LOG 2>&1
#sleep $DELETE_DELAY

# OPERATION 14 #
sleep $CRAWL_DELAY
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_CONTENT"$DEF
echo "Get URL content after delete" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_CONTENT 0 ${ERROR_PATH[@]}

if [[ $(checkNullContent $TEMPFILE "URL_CONTENT") -eq 0 ]]
then
    checkErrors $TEMPFILE URL_CONTENT 4 ${STATUS0[@]}
    #checkErrors $TEMPFILE URL_CONTENT 7 ${STATUS0[@]}
    #checkReverseErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT0[@]}

    checkErrors $TEMPFILE URL_CONTENT 0 ${STATUS1[@]}
    checkStringErrors $TEMPFILE URL_CONTENT "[]" $RAW_CONTENTS1 "raw_contents_error"
    checkStringErrors $TEMPFILE URL_CONTENT "[]" $PROCESSED_CONTENTS1 "processed_contents_error"

    checkErrors $TEMPFILE URL_CONTENT 0 ${STATUS2[@]}
    checkStringErrors $TEMPFILE URL_CONTENT "None" $URL_MD52 "url_content_after_delete_not_null"
fi

# OPERATION 15 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_NEW"$DEF
echo "URL new with put content" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_NEW --file=../data/ftests/dcc_url_new_wpc_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_NEW 0 ${ERROR_PATH[@]}

# OPERATION 16 #
#sleep $CRAWL_DELAY
#echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_CONTENT"$DEF
#echo "URLs content store for viewer" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=URL_CONTENT --file=../data/ftests/dcc_url_content_rnd.json" | tee -a $LOG_PATH/dcc_url_content_rnd.result.json > $TEMPFILE 2>&1
#checkErrors $TEMPFILE URL_CONTENT 0 ${ERROR_PATH[@]}

#if [[ $(checkNullContent $TEMPFILE "URL_CONTENT") -eq 0 ]]
#then
#    checkErrors $TEMPFILE URL_CONTENT 7 ${STATUS0[@]}
#    checkReverseErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT0[@]}

#    checkErrors $TEMPFILE URL_CONTENT 0 ${STATUS1[@]}
#    checkStringErrors $TEMPFILE URL_CONTENT "[]" $RAW_CONTENTS1 "raw_contents_error"
#    checkStringErrors $TEMPFILE URL_CONTENT "[]" $PROCESSED_CONTENTS1 "processed_contents_error"

#    checkErrors $TEMPFILE URL_CONTENT 1 ${STATUS2[@]}
#    checkErrors $TEMPFILE URL_CONTENT 0 ${TAGS_COUNT2[@]}
#fi

# OPERATION 7 #
echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"URL_STATUS"$DEF
echo -e "\n#-#\nCheck URLs status before crawling" >> $LOG_PATH/$LOG 2>&1
../manage/dc-client_start.sh "--command=URL_STATUS --file=../data/ftests/dcc_url_status_rnd.json" | tee -a $LOG_PATH/$LOG > $TEMPFILE 2>&1
checkErrors $TEMPFILE URL_STATUS 0 ${ERROR_PATH[@]}



#echo "Get content to view tags" >> $LOG_PATH/$LOG 2>&1
#$JSONPARSER --field="itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 < $LOG_PATH/dcc_url_content_rnd.result.json > $LOG_PATH/dcc_url_content_rnd.result.json.value

#echo -e $YEL"OPERATION $((COUNT_OPERATION++)): "$TUR"Test fetch content automation script"$DEF
#echo "Test fetch content automation script" >> $LOG_PATH/$LOG 2>&1
#cd ../ftests && ./dc-kvdb-resource.sh 699fcf4591fc23e79b839d8819904293 699fcf4591fc23e79b839d8819904293 >> $LOG_PATH/$LOG 2>&1
#cd ../ftests && ./dc-kvdb-resource.sh b85ab149a528bd0a024fa0f43e80b5fc b85ab149a528bd0a024fa0f43e80b5fc >> $LOG_PATH/$LOG 2>&1

#echo "Delete site" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=SITE_DELETE --file=../data/ftests/dcc_site_delete_rnd.json" >> $LOG_PATH/$LOG 2>&1

#echo "Check sites status after delete" >> $LOG_PATH/$LOG 2>&1
#../manage/dc-client_start.sh "--command=SITE_STATUS --file=../data/ftests/dcc_site_status_rnd.json" >> $LOG_PATH/$LOG 2>&1


#echo "After tests cleaning..." >> $LOG_PATH/$LOG 2>&1

#After actions
./dc_tests_after.sh

echo "Finished..." >> $LOG_PATH/$LOG 2>&1

scriptExit
