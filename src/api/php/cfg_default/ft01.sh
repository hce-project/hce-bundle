#!/bin/bash

INDEX_NUMBER="$INDEX_START_NUMBER"
NODE_NUMBER=1

echo "" > $LOG_FILE

for NODE_HOST in "${REPLICAS[@]}"
  do

for NODE_ADMIN_PORT in "${REPLICAS_MANAGE_ADMIN_PORTS[@]}"
  do
    DATA_FILE_B1=$DATA_DIR"c112_ft01_doc"$NODE_NUMBER"1.xml"
    DATA_FILE_B2=$DATA_DIR"c112_ft01_doc"$NODE_NUMBER"2.xml"
    INDEX_NAME="$INDEX_NAME_TEMPLATE$INDEX_NUMBER"
    DATA_FILE_B1_APPEND=$DATA_DIR"c112_ft01_doc"$NODE_NUMBER"_append.xml"

##First phase
    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT create index $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_CREATE --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check index $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_CHECK --name=$INDEX_NAME >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT store data file $DATA_FILE_B1 $INDEX_NAME branch b0001:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STORE_DATA_FILE --name=$INDEX_NAME --branch=b0001 --data=$DATA_FILE_B1 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT store data file $DATA_FILE_B2 $INDEX_NAME branch b0002:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STORE_DATA_FILE --name=$INDEX_NAME --branch=b0002 --data=$DATA_FILE_B2 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT store schema file $SCHEMA_FILE $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STORE_SCHEMA_FILE --name=$INDEX_NAME --data=$SCHEMA_FILE >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rebuild $INDEX_NAME branches b0001,b0002:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REBUILD --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index get MAX_DOC_ID $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MAX_DOC_ID --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index merge $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MERGE --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    . "$MANAGE_DIR"icd_replicas_pool.sh $INDEX_NAME INDEX_CONNECT

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index search "$SEARCH_STRING" $INDEX_NAME:" >> $LOG_FILE
    $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

##Copy index
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index copy $INDEX_NAME to $INDEX_NAME"_copy: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_COPY --from=$INDEX_NAME --to="$INDEX_NAME"_copy --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index stop $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STOP --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME"_copy: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name="$INDEX_NAME"_copy --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME"_copy: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name="$INDEX_NAME"_copy --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME"_copy: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME"_copy --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index search "$SEARCH_STRING" $INDEX_NAME:" >> $LOG_FILE
#    $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

##Rename index, depends on Copy
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index stop $INDEX_NAME"_copy: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STOP --name="$INDEX_NAME"_copy --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rename $INDEX_NAME"_copy to "$INDEX_NAME"_copy1: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_RENAME --from="$INDEX_NAME"_copy --to="$INDEX_NAME"_copy1 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start" "$INDEX_NAME"_copy1: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name="$INDEX_NAME"_copy1 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index search "$SEARCH_STRING" $INDEX_NAME:" >> $LOG_FILE
#    $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME"_copy1: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name="$INDEX_NAME"_copy1 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME"_copy1: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME"_copy1 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

##Delete documents
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index $INDEX_NAME delete documents: 9245650963705457277,9270095736706771532,9234913788877831530" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DELETE_DOC --name=$INDEX_NAME --documents=9245650963705457277,9270095736706771532,9234913788877831530 --timeout=$SMALL_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index $INDEX_NAME delete docs number" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DELETE_DOC_NUMBER --name=$INDEX_NAME --timeout=$SMALL_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index $INDEX_NAME pack doc data:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_PACK_DOC_DATA --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index $INDEX_NAME delete docs number" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DELETE_DOC_NUMBER --name=$INDEX_NAME --timeout=$SMALL_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rebuild $INDEX_NAME branches b0001,b0002:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REBUILD --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index get MAX_DOC_ID $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MAX_DOC_ID --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index merge $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MERGE --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

##Append data files
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT append data file $DATA_FILE_B1_APPEND $INDEX_NAME branch b0002:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_APPEND_DATA_FILE --name=$INDEX_NAME --branch=b0001 --data=$DATA_FILE_B1_APPEND --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rebuild $INDEX_NAME branches b0001,b0002:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REBUILD --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index get MAX_DOC_ID $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MAX_DOC_ID --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index merge $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MERGE --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index search "$SEARCH_STRING" $INDEX_NAME:" >> $LOG_FILE
#    $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

##Delete branches
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT delete index $INDEX_NAME branch b0002:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DELETE_DATA_FILE --name=$INDEX_NAME --branches=b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

##    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT delete schema index $INDEX_NAME:" >> $LOG_FILE
##    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DELETE_SCHEMA_FILE --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rebuild $INDEX_NAME branches b0001,b0002:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REBUILD --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index get MAX_DOC_ID $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MAX_DOC_ID --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index merge $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MERGE --name=$INDEX_NAME --branches=b0001,b0002 --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME" --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index search "$SEARCH_STRING" $INDEX_NAME:" >> $LOG_FILE
#    $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME"_copy: >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name="$INDEX_NAME"_copy --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

##Check schema
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check good schema $SCHEMA_FILE $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_CHECK_SCHEMA --name=$INDEX_NAME --data=$SCHEMA_FILE >> $LOG_FILE 2>&1

#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check bad schema $SCHEMA_FILE_BAD $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_CHECK_SCHEMA --name=$INDEX_NAME --data=$SCHEMA_FILE_BAD >> $LOG_FILE 2>&1

##Check index data files
#    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check data files list of index  $INDEX_NAME:" >> $LOG_FILE
#    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DATA_LIST --name=$INDEX_NAME >> $LOG_FILE 2>&1

#    sleep 10

    echo "" >> $LOG_FILE

    ((INDEX_NUMBER++))
    ((NODE_NUMBER++))
  done
  done
