#!/bin/bash

# Look for response like that

#{
#    "data":{
#        "resId":null,
#        "tagList":[]
#    },
#    "error_code":1,
#    "error_message":"Empty resource",
#    "time":"0.00111 sec."
#}

# if match then test has failed


BIN=~/hce-node-bundle/api/python/bin
MANAGE=~/hce-node-bundle/api/python/manage
TEST_DIR=~/hce-node-bundle/api/python/data/ftests/test_pubdate\(DC-302\)
HCE_BIN=~/hce-node-bundle/api/php/bin
DATA_FILE=$TEST_DIR/pubdates.csv
FLAG=1

cd $BIN


IFS=$'\n'
while read -r line
do
  #echo $line
  c=`echo $line | ./search_engine_parser.py | jq '.["error_code"]'`
  #echo $c
  if [ "$c" == "0" ]
  then
    echo -e "query: <<$line>> \e[92mOK\e[39m"
  else
    echo -e "query: <<$line>>  \e[91mBAD\e[39m"
    FLAG=-1
  fi
done

if [ $FLAG == 1 ]
then
  echo -e "\e[92mPASSED\e[39m"
  exit 0 
else
  echo -e "\e[91mFAILED\e[39m"
  exit -1 
fi