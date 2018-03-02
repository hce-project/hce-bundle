#!/bin/bash

CUR_DIR=`pwd`

TINFILE="./inputNewsFormat.json"
TSOCFILE="$TINFILE.out"
TINFILE_PICKLED="$CUR_DIR/input.pickle"
TOUTFILE_PICKLED="$CUR_DIR/output.pickle"

./dataPickle.py --operation PICKLE < $TINFILE > $TINFILE_PICKLED


cd /home/hce/hce-node-bundle/api/python/bin

./social_task.py --config=../ini/social_task.ini < $TINFILE_PICKLED > $TOUTFILE_PICKLED

cd $CUR_DIR

./dataPickle.py --operation UNPICKLE < $TOUTFILE_PICKLED > $TSOCFILE


