#!/bin/bash
#Indicators fetcher for Zabbix from counters for each site
#Parameters: <"U" updates counter jsons for all sites> | [<indicator_name> <site_id> <host_number>]

#HOSTS=( localhost )

REQUEST_JSON_FILE_TEMPLATE="../data/ftests/test_14_site_stanz_url_content/dcc_site_custom_sql_counters_snatz.json"
REQUEST_JSON_FILE_DIR="../log/sites_stats"
OUT_JSON_FILE_DIR="../log/sites_stats"

if [ ! -d "$REQUEST_JSON_FILE_DIR" ]; then
  mkdir $REQUEST_JSON_FILE_DIR
fi

if [ ! -d "$OUT_JSON_FILE_DIR" ]; then
  mkdir $OUT_JSON_FILE_DIR
fi

if [ "$1" = "U" ]; then
  . ./../ftests/dc_test_japan_sites_cfg_snatz_rss.sh
  SITE_INDEX=0
  for SITE_NAME in "${SITES_LIST[@]}"
    do
      export SITE_ID="${SITES_LIST_ID[$SITE_INDEX]}"
      #echo "Site:$SITE_NAME id:$SITE_ID"

      REQUEST_JSON=$(<$REQUEST_JSON_FILE_TEMPLATE)
      REQUEST_JSON="${REQUEST_JSON/CRITERION/Id=\\\"$SITE_ID\\\"}"
      export REQUEST_JSON_FILE="$REQUEST_JSON_FILE_DIR/$0_$SITE_ID.request.json"
      echo "$REQUEST_JSON" > $REQUEST_JSON_FILE
      export OUT_FILE="$OUT_JSON_FILE_DIR/$0_$SITE_ID.response.json"

      ./dc-daemon_zabbix_fetch_site_counters.sh U

      ((SITE_INDEX++))
    done
else
  export SITE_ID="$2"

  if [ "$SITE_ID" = "" ]; then
    REQUEST_JSON="${REQUEST_JSON/CRITERION/1=1}"
  else
    REQUEST_JSON="${REQUEST_JSON/CRITERION/Id=\\\"$SITE_ID\\\"}"
  fi
  export REQUEST_JSON_FILE="$REQUEST_JSON_FILE_DIR/$0_$SITE_ID.request.json"
  echo REQUEST_JSON > $REQUEST_JSON_FILE
  export OUT_FILE="$OUT_JSON_FILE_DIR/$0_$SITE_ID.response.json"

  ./dc-daemon_zabbix_fetch_site_counters.sh $1 $3
fi
