#!/bin/bash

TESTS_PATH="../"
CUR_PATH=`pwd`

cd $TESTS_PATH
. ../cfg/current_cfg.sh
cd $CUR_PATH

TASK_ID=$1

if [ "$TASK_ID" == "" ]
then
  TASK_ID=5000
fi

#######################
## Main process block
#######################

./drce_test_mass_new_tasks.sh $TASK_ID "07"

exit 0
