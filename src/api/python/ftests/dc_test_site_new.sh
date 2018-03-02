#!/bin/bash

DIR=~/hce-node-bundle/api/python/

cd ${DIR}/bin
echo `pwd`

FILES=`pwd`/*.json

for f in $FILES
do
  ./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=$f
done