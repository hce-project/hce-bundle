#!/bin/bash

if [ "$1" = "" ]; then
  SITE_ID="--fields={}"
  echo "Update all sites state to disabled" > ../log/$0.log 2>&1
else
  SITE_ID='--fields={"id": "'$1'"}'
  echo "Update sites $1 state to disabled" > ../log/$0.log 2>&1
fi

cd ../bin && ./dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE "$SITE_ID" --file=../data/ftests/dcc_sites_update_disabled.json >> ../log/$0.log 2>&1
