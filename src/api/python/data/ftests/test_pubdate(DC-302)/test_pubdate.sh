#!/bin/bash


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_pubdate\(DC-302\)
HCE_BIN=~/hce-node-bundle/api/php/bin
DATA_FILE=$TEST_DIR/pubdates.csv
FLAG=1

cd $BIN

IFS=","
while read a b
do
  c=`echo $a | ./test_pubdate.py 2>&1`
  if [ "$c" == "$b" ]
  then
    echo -e "init: <<$a>> converted: <<$c>> \e[92mOK\e[39m"
  else
    echo -e "init: <<$a>> converted: <<$c>> sample: <<$b>> \e[91mBAD\e[39m"
    FLAG=-1
  fi
done < $DATA_FILE

if [ $FLAG == 1 ]
then
  echo -e "\e[92mPASSED\e[39m"
else
  echo -e "\e[91mFAILED\e[39m"
fi