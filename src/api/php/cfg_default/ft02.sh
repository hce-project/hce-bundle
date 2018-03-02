#!/bin/bash

echo "" > $LOG_FILE

#Create indexes at all nodes
INDEX_NUMBER="$INDEX_START_NUMBER"
for NODE_ADMIN_PORT in "${REPLICAS_MANAGE_ADMIN_PORTS[@]}"
  do
    INDEX_NAME="$INDEX_NAME_TEMPLATE$INDEX_NUMBER"

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT create index $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_CREATE --name=$INDEX_NAME --timeout=$SMALL_TIMEOUT >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check index $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_CHECK --name=$INDEX_NAME >> $LOG_FILE 2>&1

    echo "------------ $NODE_HOST:$NODE_ADMIN_PORT store schema file $SCHEMA_FILE $INDEX_NAME:" >> $LOG_FILE
    $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STORE_SCHEMA_FILE --name=$INDEX_NAME --data=$SCHEMA_FILE --timeout=$SMALL_TIMEOUT >> $LOG_FILE 2>&1

    echo "" >> $LOG_FILE

    ((INDEX_NUMBER++))
  done

#collect list of xml-source files in to the array
xml_source_files=($(find "$DATA_DIR" -type f -regex "$DATA_FILE_PATTERN"))

#Store branches files in the indexes, rebuild branches and merge index
if [[ ( "$MANAGER_MODE" = "rmanager" ) || ( "$MANAGER_MODE" = "rmanager-rnd" ) || ( "$MANAGER_MODE" = "rmanager-round-robin" ) ]]
then
  #In replica manner (total copy of data on all nodes to get balanced max of productivity)
  INDEX_NUMBER="$INDEX_START_NUMBER"
  BRANCHES_LIST=""
  for NODE_ADMIN_PORT in "${REPLICAS_MANAGE_ADMIN_PORTS[@]}"
    do
      BRANCHES_LIST=""
      INDEX_NAME="$INDEX_NAME_TEMPLATE$INDEX_NUMBER"
      for branch_file in ${xml_source_files[*]}
        do
          DATA_FILE="${branch_file##*/}"
          DATA_BRANCH="${DATA_FILE%%.*}"

          echo "------------ $NODE_HOST:$NODE_ADMIN_PORT store data file $DATA_FILE in index $INDEX_NAME as branch $DATA_BRANCH:" >> $LOG_FILE
          $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STORE_DATA_FILE --name=$INDEX_NAME --branch=$DATA_BRANCH --data=$branch_file --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

          echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rebuild $INDEX_NAME branch $DATA_BRANCH" >> $LOG_FILE 2>&1
          $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REBUILD --name=$INDEX_NAME --branches=$DATA_BRANCH --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

          BRANCHES_LIST="$BRANCHES_LIST,$DATA_BRANCH"
        done

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index get MAX_DOC_ID $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MAX_DOC_ID --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check data files list of index  $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DATA_LIST --name=$INDEX_NAME >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index merge $INDEX_NAME branches 0$BRANCHES_LIST:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MERGE --name=$INDEX_NAME --branches=0$BRANCHES_LIST --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      . "$MANAGE_DIR"icd_replicas_pool.sh $INDEX_NAME INDEX_CONNECT

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index search "$SEARCH_STRING" $INDEX_NAME:" >> $LOG_FILE
      $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

      echo "" >> $LOG_FILE

      ((INDEX_NUMBER++))
    done
else
  #In shard manner (sequential proportional storage file by file)
  echo "" >> $LOG_FILE  

  INDEX_NUMBER="$INDEX_START_NUMBER"
  NODE_NUMBER=0

  for branch_file in ${xml_source_files[*]}
    do
      #Each branch data file
      DATA_FILE="${branch_file##*/}"
      DATA_BRANCH="${DATA_FILE%%.*}"

      #For all nodes and indexes
      NODE_ADMIN_PORT="${REPLICAS_MANAGE_ADMIN_PORTS[${NODE_NUMBER}]}"
      INDEX_NAME="$INDEX_NAME_TEMPLATE$INDEX_NUMBER"

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT store data file $DATA_FILE in index $INDEX_NAME as branch $DATA_BRANCH:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STORE_DATA_FILE --name=$INDEX_NAME --branch=$DATA_BRANCH --data=$branch_file --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index rebuild $INDEX_NAME branch $DATA_BRANCH" >> $LOG_FILE 2>&1
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_REBUILD --name=$INDEX_NAME --branches=$DATA_BRANCH --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      ((INDEX_NUMBER++))
      ((NODE_NUMBER++))

      if [ "$NODE_NUMBER" = "${#REPLICAS_MANAGE_ADMIN_PORTS[@]}" ]; then
        INDEX_NUMBER="$INDEX_START_NUMBER"
        NODE_NUMBER=0
      fi

      echo "" >> $LOG_FILE
    done

  echo "" >> $LOG_FILE
  echo "" >> $LOG_FILE

  INDEX_NUMBER="$INDEX_START_NUMBER"
  REPLICA_POOL_NODE_NUMBER=0
  for NODE_ADMIN_PORT in "${REPLICAS_MANAGE_ADMIN_PORTS[@]}"
    do
      INDEX_NAME="$INDEX_NAME_TEMPLATE$INDEX_NUMBER"
      REPLICA_NODE_ADMIN_PORT="${REPLICAS_POOL_ADMIN_PORTS[${REPLICA_POOL_NODE_NUMBER}]}"

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index get MAX_DOC_ID $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MAX_DOC_ID --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT check data files list of index  $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_DATA_LIST --name=$INDEX_NAME >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index merge $INDEX_NAME all branches *:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_MERGE --name=$INDEX_NAME --branches=* --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index start $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_START --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status $INDEX_NAME:" >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS --name=$INDEX_NAME >> $LOG_FILE 2>&1

      echo "------------ $NODE_HOST:$NODE_ADMIN_PORT index status searchd $INDEX_NAME": >> $LOG_FILE
      $BIN_DIR$MANAGER_COMMAND --host=$NODE_HOST --port=$NODE_ADMIN_PORT --command=INDEX_STATUS_SEARCHD --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

#      . ./icd_replicas_pool.sh $INDEX_NAME INDEX_CONNECT

      echo "------------ $NODE_HOST:$REPLICA_NODE_ADMIN_PORT INDEX_CONNECT to index $INDEX_NAME": >> $LOG_FILE 2>&1
      $BIN_DIR$MANAGER_COMMAND --host=$HOST --port=$REPLICA_NODE_ADMIN_PORT --command=INDEX_CONNECT --name=$INDEX_NAME --timeout=$BIG_TIMEOUT >> $LOG_FILE 2>&1

      echo "------------ search $SEARCH_STRING" >> $LOG_FILE
      $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1

      ((INDEX_NUMBER++))
      ((REPLICA_POOL_NODE_NUMBER++))

      echo "" >> $LOG_FILE
    done

    echo "------------ search $SEARCH_STRING" >> $LOG_FILE
    $SEARCH_TEST_NAME$SEARCH_STRING >> $LOG_FILE 2>&1
fi
