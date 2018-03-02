#!/bin/bash

echo "This cleanup all DB data and structures! Continue? y/[N]"
read -rs -n1 KEY

case "$KEY" in
    'y'|'Y')
        :
        ;;
    *)
        echo "Canceled"
        exit 0
        ;;
esac

source mysql_create_cfg

echo "Remove all databases..."

# GET SCRIPTS WITH CREATE DBS #
CREATE_FILES=($(grep mysql_create mysql_create_db.sh | awk -F\/ '{print $2}'))

# GET INI FILES WITH DB AND SQLITE DB #
for FILE in "${CREATE_FILES[@]}"
do
  INI_FILES=("${INI_FILES[@]}" $(grep -E 'mysql.*ini' $FILE | awk -F\< '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'))
  DB_FILES=("${DB_FILES[@]}" $(grep -E 'cp.*\.db' $FILE | awk '{print $3}' | sed 's/^[ \t]*//;s/[ \t]*$//'))
done

# REMOVE SQLITE DB IF EXIST #
if [ ${#DB_FILES[@]} -ne 0 ]
then
    for SQLITE_DB in "${DB_FILES[@]}"
    do
        if [ -f "$SQLITE_DB" ]
        then
            rm -f "$SQLITE_DB"
        fi
    done
fi

# GET MYSQL DATABASES #
if [ ${#INI_FILES[@]} -ne 0 ]
then
    for MYSQL_DBS in "${INI_FILES[@]}"
    do
        if [ -f "$MYSQL_DBS" ]
        then
            MYSQL_DB=("${MYSQL_DB[@]}" $(grep -i 'create database' $MYSQL_DBS | awk -F\` '{print $2}'))
        fi
    done
fi

# DELETE MYSQL DATABASES #
if [ ${#MYSQL_DB[@]} -ne 0 ]
then
    for DATABASE in "${MYSQL_DB[@]}"
    do
        # DELETE #
        mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS -e "DROP DATABASE IF EXISTS $DATABASE"
        # CHECK #
        DBEXISTS=$(mysql -h 127.0.0.1 -u $APP_USER -p$APP_PASS -Bs -e "SHOW DATABASES LIKE '$DATABASE'" | grep "$DATABASE" > /dev/null; echo "$?")
        if [ $DBEXISTS -eq 0 ]
        then
            echo "Database $DATABASE not removed"
        fi
        unset DBEXISTS
    done
fi

echo "Done"

exit 0
