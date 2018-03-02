#!/bin/bash

PERMISSIONS_FILE='hce-node-permissions.sh'

GOOSEDIR='/tmp/goose'

if [[ ! -d ${GOOSEDIR} ]]
then
    mkdir ${GOOSEDIR}
fi

while read LINE
do
    SRC_PATH=$(echo $LINE | grep chmod | awk -F'777' '{print $2}' | sed "s%~%$HOME%")
    if [[ $SRC_PATH ]]
    then
        for FILE in $SRC_PATH
        do
            PERM=$(stat -c "%a" ${FILE})
            if [[ ${PERM} != '777' && ${PERM} != '755' ]]
            then
                echo "Error: "$FILE" have permission "$PERM
            fi
        done
    fi
done < $PERMISSIONS_FILE
