#!/bin/bash

CURDIR=`pwd`

INPUT_FILE="$CURDIR/input.pickle"
OUTPUT_FILE="$CURDIR/output.pickle"


cd ~/hce-node-bundle/api/python/bin

./postprocessor_task.py --config=../ini/postprocessor_task-rt.ini --inputFile=$INPUT_FILE > $OUTPUT_FILE &

./postprocessor_task.py --config=../ini/postprocessor_task-rt.ini --inputFile=$INPUT_FILE > $OUTPUT_FILE &

./postprocessor_task.py --config=../ini/postprocessor_task-rt.ini --inputFile=$INPUT_FILE > $OUTPUT_FILE &
