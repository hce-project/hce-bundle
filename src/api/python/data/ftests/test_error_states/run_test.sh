#!/bin/bash

BUNDLE_DIR="/home/alexander/hce-node-bundle"
TEST_DIR=`pwd`"/"
BIN_DIR="$BUNDLE_DIR/api/python/bin/"
LOG_DIR="$BUNDLE_DIR/api/python/log/"

TMP_DIR="/tmp"
ERROR_CODE="0"
EXIT_CODE=1

executeRequest()
# $1 - input file
# $2 - output file
{
	oldDir=`pwd`
	cd $BIN_DIR 
	./dc-client.py -v 1 --config=../ini/dc-client.ini --command=BATCH --file=$1 > $2
	cd $oldDir
}

extractErrorCode()
# $1 - input file
{
	TEMP_FILE="$TMP_DIR/error_code_value.tmp"
	oldDir=`pwd`
	cd $BIN_DIR 
	./json-field.py -f "itemsList:0:itemObject:0:dbFields:ErrorMask" < "$1" > "$TEMP_FILE"
	ERROR_CODE=`cat "$TEMP_FILE"`
	cd $oldDir
	rm -f $TEMP_FILE
}

#############
## Main loop
#############

FILES=( "index1_news_domain_name.json" "index1_news_robots.json" "index1_news_http_redirect.json" "index1_news_http_timeout.json" )  
ERRORS=( "67174400" "2048" "67108864" "536870912" ) 

index=0
failed=0
for f in ${FILES[@]}
	do
		outFile="$LOG_DIR$f.out"
		executeRequest "$TEST_DIR$f" "$outFile"
		extractErrorCode "$outFile"

		echo -en "$f [ $ERROR_CODE ]"
	
		if [ $ERROR_CODE -eq ${ERRORS[$index]} ]
		then
			echo " - SUCCESS"
		else
			echo " - FAILED"
			failed=$(($failed+1))
		fi	
		index=$(($index+1))
	done

if [ $failed -eq 0 ]
then
	EXIT_CODE=0
fi

echo "Finished with exit code: $EXIT_CODE"

exit $EXIT_CODE

