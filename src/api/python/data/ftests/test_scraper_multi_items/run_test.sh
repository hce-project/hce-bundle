#!/bin/bash

STOP="no"

if [ "$1" != "" ]
then
	STOP="yes"
fi

SLEEP=2
EXIT_CODE=1

BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_scraper_multi_items

DAEMON_PROCESSES=("dc-daemon.py" "dtm-daemon.py")

cleanup()
{
	cd $BIN
	echo "Cleanup log files"
	rm -f ../log/*
}

isExistProcess()
# $1 - process name
# return 1 if exist or 0 othewise
{
	PID=$(pgrep $1)

	if [ $PID ]
	then
		return 1
	else
		return 0
	fi
}

processes=0
for p in ${DAEMON_PROCESSES[@]}
	do
		isExistProcess "$p"
		isExist=$?

		if [ $isExist -eq 1 ]
		then
			processes=$(($processes+1))
		fi
	done

if [ $processes -eq 0 ]
then
	cleanup
fi


# start cluster
cd $MANAGE
./dtm-daemon_start.sh 
./dc-daemon_start.sh

sleep $SLEEP

#change file permissions
sudo chmod a+w -R /tmp/
sudo chmod a+w -R ../

cd $BIN

NEW_SITE_FILES=$TEST_DIR/site_new*.json
for f in $NEW_SITE_FILES
do
  echo "Create new site"
  echo $f > ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

NEW_URL_FILES=$TEST_DIR/url_new*.json
for f in $NEW_URL_FILES
do
  echo "Create new url"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

BATCHES=$TEST_DIR/input_batch*.json

for f in $BATCHES
do
  echo "Send BATCH to scraping multi items"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py -v 1 --config=../ini/dc-client.ini --command=BATCH --file=$f >> ../log/$0.log 2>&1
	EXIT_CODE="$?"
done

sleep $SLEEP

DELETE_URL_FILES=$TEST_DIR/url_delete*.json
for f in $DELETE_URL_FILES
do
  echo "Delete url"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=URL_DELETE --file=$f >> ../log/$0.log 2>&1
done

sleep $SLEEP

DELETE_SITE_FILES=$TEST_DIR/site_delete*.json
for f in $DELETE_SITE_FILES
do
	echo "Delete site"
  echo $f >> ../log/$0.log 2>&1
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_DELETE --file=$f >> ../log/$0.log 2>&1
done

# stop cluster if necessary
if [ "$STOP" == "yes" ]
then
	cd $MANAGE
	./dc-daemon_stop.sh
	./dtm-daemon_stop.sh 
fi

exit $EXIT_CODE

