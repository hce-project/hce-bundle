#!/bin/bash

SQL_QUERIES='SELECT `id` FROM `task_log_scheme` LIMIT 10; SELECT CONCAT(AVG(`id`)) FROM `task_log_scheme`; SELECT COUNT(*) from `task_back_log_scheme`; SELECT AVG(`id`) FROM `task_log_scheme`; SELECT `id` FROM `task_back_log_scheme` LIMIT 10'
SQL_IGNORE_TABLE='task_back_log_scheme'

DTM_DAEMON='../bin/dtm-admin.py'
DTM_DAEMON_INI='-c ../ini/dtm-admin.ini'
DTM_DAEMON_CMD='--cmd SQL_CUSTOM'
ID=0

for ARG in $*
do
    case $ARG in
    'sql_base64='*|'-sql_base64='*|'--sql_base64='*)
        SQL_QUERIES=$(echo $ARG | sed 's/^sql_base64=\|-sql_base64=\|--sql_base64=*\s*//' | base64 -d);;
    'help'|'-help'|'--help'|*)
        echo "Usage: $0 "
        echo " without arguments - uses sql requests from this script"
        echo " [help or -help or --help: this help]"
        echo " [sql_base64='base64 of sql request' or -sql_base64='base64 of sql request' or --sql_base64='base64 of sql request', example of sql request: 'SELECT \`id\` FROM \`task_log_scheme\` LIMIT 10; SELECT CONCAT(AVG(\`id\`)) FROM \`task_log_scheme\`']"
     exit 1;;
    esac
done

SCRIPT_NAME=$(basename $0)
TEMPFILE=$(mktemp /tmp/$SCRIPT_NAME.XXXXX)

RED='\e[0;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

SQL_QUERIES=($(echo $SQL_QUERIES | sed 's/ /<=>/g' | sed 's/;/ /g'))

for SQL in ${SQL_QUERIES[@]}
do
    ((ID++))
    SQL="$(echo $SQL | sed 's/<=>/ /g')"
    DTM_FIELD='{"id": '$ID', "sql": "'$SQL'"}'
    $DTM_DAEMON $DTM_DAEMON_INI $DTM_DAEMON_CMD --fields "$DTM_FIELD" > $TEMPFILE
    if [[ $(echo $?) == 0 ]]
    then
        CHECK_RID=0
        CHECK_RESULT=0
        CHECK_TABLE=$(echo $SQL | grep $SQL_IGNORE_TABLE)
        while read LINE
        do
            # CHECK RID AND RESULT IN ANSWER #
            # CHECK RID #
            if [[ $LINE =~ '"rid":' ]]
            then
                ((CHECK_RID++))
                RID=$(echo $LINE | sed 's/"rid"://' | sed -e 's/^[[:space:]]*\|*[[:space:]]$//')
                if [[ $RID != $ID ]]
                then
                    echo -e $RED"Error. Request № "$ID", rid="$RID", need "$ID" in ("$SQL")" $DEF
                fi
            fi
            # CHECK RESULT #
            if [[ $LINE =~ '"result":' ]]
            then
                ((CHECK_RESULT++))
                RESULT=$(echo $LINE | sed 's/"result"://' | sed -e 's/^[[:space:]]*\|*[[:space:]]$//')
                if [[ ! $CHECK_TABLE ]]
                then
                    if [[ $RESULT =~ '[]' || $RESULT == 'null' ]]
                    then
                        echo -e $RED"Error. Request № "$ID", result is null ("$SQL")"$DEF
                    fi
                fi
            fi
        done < $TEMPFILE
        if [[ $CHECK_RID == 0 ]]
        then
            echo -e $RED"Error. Request № "$ID", key 'rid' not found in response ("$SQL")"$DEF
        fi
        if [[ $CHECK_RESULT == 0 ]]
        then
            echo -e $RED"Error. Request № "$ID", key 'result' not found in response ("$SQL")"$DEF
        fi
    else
        echo -e $RED"Error. Request № "$ID", dtm command error ("$SQL")"$DEF
    fi

done
