#!/bin/bash

RED='\e[1;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

# CHECK FILE WITH LOG #
if [[ -z $1 ]]
then
    echo -e "Usage $RED$0 [log file]$DEF"
    exit 1
fi
if [[ ! -f $1 ]]
then
    echo -e "File $RED$1$DEF not found"
fi
# END OF CHECK FILE WITH LOG #

# FUNCTIONS #
function fatalError() {
    # $1 - check line
    if [[ $1 =~ "#-#FATAL" ]]
    then
        echo $1 | awk -F: '{print "Fatal error: " $2}'
    fi
    exit 1
}
function errors() {
    # $1 - line with error
    # $2 - error
    if [[ $1 =~ "$2" ]]
    then
        CHECK=($(echo $1 | awk -F\: '{print $2}' | sed 's/ \|,\|\"//g' | tr ';' '\n'))
        for TMPLINE in "${CHECK[@]}"
        do
            if [[ $TMPLINE != 0 ]]
            then
                echo $1
                exit 1
            fi
        done
    fi
}
function searchStart() {
    # $1 - line with error
    if [[ $1 == '#-#' ]]
    then
        echo 'FOUND'
    fi
}
# END OF FUNCTIONS #

# FILE TO ARRAY #
readarray LOG < $1
# END OF FILE TO ARRAY #

# START CHECK #
for ((LINE=1;LINE<=${#LOG[@]]};++LINE))
do
    CHECKFATAL=$(fatalError ${LOG[$LINE]})
    if [[ $CHECKFATAL ]]
    then
        echo $CHECKFATAL
        exit 1
    fi
    CHECKERROR=$(errors "${LOG[$LINE]}" "errors")
    if [[ $CHECKERROR ]]
    then
        #echo $CHECKERROR
        for ((LINEBACK=$LINE;LINEBACK>=0;--LINEBACK))
        do
            SEARCHSTART=$(searchStart ${LOG[$LINEBACK]})
            if [[ $SEARCHSTART ]]
            then
                echo -e "$RED Error in block: $DEF\""${LOG[$LINEBACK+1]}\"$RED" in line "$LINE $DEF
                break
            fi
        done
    fi
    CHECKERROR=$(errors "${LOG[$LINE]}" "errorCode")
    if [[ $CHECKERROR ]]
    then
        #echo $CHECKERROR
        for ((LINEBACK=$LINE;LINEBACK>=0;--LINEBACK))
        do
            SEARCHSTART=$(searchStart ${LOG[$LINEBACK]})
            if [[ $SEARCHSTART ]]
            then
                echo -e "$RED Error in block: $DEF\""${LOG[$LINEBACK+1]}\"$RED" in line: "$LINE $DEF" "${LOG[$LINE]}", "$RED${LOG[$LINE+1]} $DEF
                break
            fi
        done
    fi
done
# END OF CHECK #

echo -e "$BLUE DONE $DEF"
exit 0