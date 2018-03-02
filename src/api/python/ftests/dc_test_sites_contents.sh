#!/bin/bash
#Fetching contents of sites and create set of files for visual verification
#Arguments:
#         $1 - max items number, zero means all returned by json query definitions, if omitted - first item for each site used
#         $2 - the destination directory can be omitted, "DATETIME" or full path, if omitted - the "../python/log/" directory used
#         $3 - int, if set and is 1 - tar archive of the directory will be created, if 2 - only in case of not empty list of articles
#         $4 - bool, original destination directory will be deleted after tar archive created
#         $5 - target directory to move tar archive

TOTAL_ITEMS=0

#Init max items per site, zero means all
if [ "$1" = "" ]; then
  ITEMS_MAX=1
else
  ITEMS_MAX="$1"
fi

#Init destination dir, empty means ~<DTS>/api/python/log/
if [ "$2" = "" ]; then
  DESTINATION_DIR="../log"
  DESTINATION_DIR_PHP="../../python/log"
else
  DESTINATION_DIR="$2"
  if [ "$DESTINATION_DIR" = "DATETIME" ]; then
    DESTINATION_DIR="../log/"$(date +"%Y%m%d%H%M")
    DESTINATION_TAR="$DESTINATION_DIR"
    DESTINATION_DIR_PHP="../../python/log"
  else
    DESTINATION_TAR="$DESTINATION_DIR${1##*/}"
    DESTINATION_DIR_PHP=""
  fi
  #Create destination dir
  if [ ! "$3" = "" ]; then
    if [ ! -d "$DESTINATION_DIR" ]; then
      mkdir "$DESTINATION_DIR"
      chmod 777 "$DESTINATION_DIR"
    fi
  fi
fi

LOG="$DESTINATION_DIR/${0##*/}.log"

echo "$(date +"%Y-%m-%d %H:%M:%S") Started..." > $LOG
echo "" >> $LOG

SITE_INDEX=0
for SITE_NAME in "${SITES_LIST[@]}"
  do
    SITE_ID="${SITES_LIST_ID[$SITE_INDEX]}"
    echo "Site:$SITE_NAME id:$SITE_ID" >> $LOG

    REQUEST_JSON="$DATA_DIR""url_content_""$SITE_NAME""_multi.json"
    RESULTS_JSON="$DESTINATION_DIR/$INSTALLATION_NAME${0##*/}""_""$SITE_NAME""_""$SITE_ID"".result"

    echo "Suspend crawling site $SITE_NAME:$SITE_ID" >> $LOG
    eval "./dc_test_sites_suspend.sh $SITE_ID"
    #sleep 60

    echo "URLs contents with date range condition" >> $LOG
    ../bin/dc-client.py -v 1 --config=../ini/dc-client.ini --command=URL_CONTENT --file=$REQUEST_JSON > $RESULTS_JSON.json 2>>$LOG

    echo "Activate site $SITE_NAME:$SITE_ID" >> $LOG
    eval "./dc_test_sites_active.sh $SITE_ID"

    echo "Check number of items in itemObject" >> $LOG
    cd ../bin
    ITEMS=$(./json-field.py -f "itemsList:0:itemObject:__LEN__" < $RESULTS_JSON.json 2>>$LOG)
    cd ../ftests
    echo "Items number $ITEMS" >> $LOG

    if [[ $ITEMS -gt 0 ]]; then
      TOTAL_ITEMS=$((TOTAL_ITEMS + ITEMS))

      #if [[ ("$CONTENTS_TO_SEPARATE_FILES" = "1") && ("$SITE_ID" != "2f105d68146db820c23aa3fc6010888d") && ("$SITE_ID" != "c241444dcd1b03bf04549448830c8942") ]]; then
      if [ "$CONTENTS_TO_SEPARATE_FILES" = "1" ]; then
        ((ITEMS--))
        START=0
        if [[ $ITEMS_MAX -gt 0 ]]; then
          if [[ $ITEMS_MAX -gt $ITEMS ]]; then
            END="$ITEMS"
          else
            END="$ITEMS_MAX"
            ((END--))
          fi
        else
          END="$ITEMS"
        fi

        for ITEM in $(eval echo "{$START..$END}")
        do
          echo "Get item #$ITEM Id" >> $LOG
          urlMd5=$(cd ../bin && ./json-field.py -f "itemsList:0:itemObject:$ITEM:urlMd5" < $RESULTS_JSON.json && cd ../ftests)

          if [ "$2" = "" ]; then
            RESULTS_JSON1="$RESULTS_JSON.$urlMd5"
          else
            RESULTS_JSON1="$DESTINATION_DIR/$SITE_NAME"_"$urlMd5"
          fi

          if [ "$PARENT_ID_IN_FILENAME" = "1" ]; then
            ParentMd5=$(cd ../bin && ./json-field.py -f "itemsList:0:itemObject:$ITEM:dbFields:ParentMd5" < $RESULTS_JSON.json && cd ../ftests)
            if [ ! "$ParentMd5" = "" ]; then
              RESULTS_JSON1="$RESULTS_JSON1.$ParentMd5"
            fi
          fi

          echo "Get content Id=$urlMd5 tags" >> $LOG
          cd ../bin && ./json-field.py -f "itemsList:0:itemObject:$ITEM:processedContents:0:buffer" -b 1 < $RESULTS_JSON.json > $RESULTS_JSON1.$ITEM.json && cd ../ftests

          if [ "$IMPORT_XML" = "1" ]; then
            echo "Convert content Id=$urlMd5json to xml" >> $LOG
            cd ../../php/bin && ./json-field.php --field=@ --xml=1 < $DESTINATION_DIR_PHP/$RESULTS_JSON1.$ITEM.json > $DESTINATION_DIR_PHP/$RESULTS_JSON1.$ITEM.xml && cd ../../python/ftests
          fi
        done
      fi
    fi

    echo "" >> $LOG

    ((SITE_INDEX++))
  done

  echo "$(date +"%Y-%m-%d %H:%M:%S") Finished." >> $LOG

  #Create archive
  if [ ! "$3" = "" ]; then
    if [[ ( $3 -eq 2 && (( $TOTAL_ITEMS > 0 )) ) || $3 -eq 1 ]]; then
      tar -czf $DESTINATION_TAR.tgz -C $DESTINATION_DIR .
    fi
    if [ ! "$4" = "" ]; then
      rm -R "$DESTINATION_DIR"
    fi
  fi

  if [ ! "$5" = "" ]; then
    if [ -f "$DESTINATION_TAR.tgz" ]; then
      mv $DESTINATION_TAR.tgz $5
    fi
  fi
