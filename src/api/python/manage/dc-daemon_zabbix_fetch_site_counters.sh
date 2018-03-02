#!/bin/bash
#Indicators fetcher for Zabbix from counters
#Parameters: <"U" - update action or indicator name, for example "Size"> <if first the indicator name - data host number, if omitted - merged value from all hosts>

if [[ -z "$SITE_ID" ]]; then
  SITE_ID=""
fi

if [[ -z "$HOSTS" ]]; then
  #HOSTS=( localhost )
  HOSTS=( h2.dc3m.hce-project.com h3.dc3m.hce-project.com )
fi

if [[ -z "$REQUEST_JSON_FILE" ]]; then
  REQUEST_JSON_FILE="../data/ftests/dcc_site_custom_sql_counters.json"
fi

if [[ -z "$OUT_FILE" ]]; then
  OUT_FILE="../log/$0_$SITE_ID.json"
fi

INDICATORS=( 'AVGSpeed' 'CollectedURLs' 'Contents' 'Errors' 'Resources' 'Size' 'Iterations' 'NewURLs' 'DeletedURLs' )

if [ "$1" = "U" ]; then
  #Update counters
  ../manage/dc-client_start.sh "--command=SQL_CUSTOM --file=$REQUEST_JSON_FILE" > $OUT_FILE.tmp 2>&1
  mv $OUT_FILE.tmp $OUT_FILE
else
  #Check is a valid indicator name
  if [[ "${INDICATORS[*]}" =~ (^|[^[:alpha:]])$1([^[:alpha:]]|$) ]]; then
    cd ../bin
    #Get number of hosts
    ITEMS=$(./json-field.py -f "itemsList:__LEN__" < $OUT_FILE)
    if [ "$2" = "" ]; then
      #Merged value from all hosts
      if [[ $ITEMS -gt 0 ]]; then
        ((ITEMS--))
        START=0
        END="$ITEMS"
        VALUE=0
        for ITEM in $(eval echo "{$START..$END}")
        do
          t=$(./json-field.py -f "itemsList:$ITEM:itemObject:0:result:0:$1" < $OUT_FILE)
          t=${t%.*}
          VALUE=$((VALUE+t))
        done
        if [[ (( $ITEMS > 0 )) && ( "$1" = "AVGSpeed" || "$1" = "" ) ]]; then
          VALUE=$((VALUE/(ITEMS+1)))
        fi
        echo "$VALUE"
      fi
    else
      #Single value from one host
      #./json-field.py -f "itemsList:$2:itemObject:0:result:0:$1" < $OUT_FILE
      if [[ $ITEMS -gt 0 ]]; then
        ((ITEMS--))
        START=0
        END="$ITEMS"
        VALUE=0
        for ITEM in $(eval echo "{$START..$END}")
        do
          HOST=$(./json-field.py -f "itemsList:$ITEM:host" < $OUT_FILE)
          #echo "$HOST == ${HOSTS[$2]}"
          if [[ "$HOST" == "${HOSTS[$2]}" ]]; then
            t=$(./json-field.py -f "itemsList:$ITEM:itemObject:0:result:0:$1" < $OUT_FILE)
            #echo "t=$t"
            VALUE=${t%.*}
            break
          fi
        done
        echo "$VALUE"
      fi
    fi
  fi
fi
