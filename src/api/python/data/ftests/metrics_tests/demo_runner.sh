#!/bin/bash

INPUT_FILE=""
OUTPUT_FILE=""
BUNDLE_DIR=""
VERBOSE_MODE="no"

# /demo_runner.sh -i input.json -o output.json -d /home/hce/hce-node-bundle

while getopts ":i:o:d:v:h:" opt; do
  case $opt in
    i)
      INPUT_FILE=$OPTARG
    ;;
    o)
      OUTPUT_FILE=$OPTARG
    ;;
    d)
      BUNDLE_DIR=$OPTARG
    ;;
    v)
      VERBOSE_MODE="yes"
    ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
    ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
    exit 1
    ;;
  esac
done


# Check command line arguments
if [[ $INPUT_FILE = '' ]]; then
  echo "-i <input file name>"
  exit 1
fi

if [[ $OUTPUT_FILE = '' ]]; then
  echo "-o <output file name>"
  exit 1
fi

if [[ $BUNDLE_DIR = '' ]]; then
  echo "-d <bundle dir>"
  exit 1
fi

# Check absolute / relative path
if [[ $INPUT_FILE != /* ]]; then
  INPUT_FILE=`pwd`/$INPUT_FILE
fi

if [[ $OUTPUT_FILE != /* ]]; then
  OUTPUT_FILE=`pwd`/$OUTPUT_FILE
fi


if [[ $VERBOSE_MODE = "yes" ]];  then
    echo "Input  json file is: " $INPUT_FILE
    echo "Output json file is: " $OUTPUT_FILE
    echo "Bundle root  dir is: " $BUNDLE_DIR
    echo "./dc-client.py --config=../ini/dc-client.ini --command=BATCH --file=$INPUT_FILE > $OUTPUT_FILE"
fi

cd $BUNDLE_DIR/api/python/bin

./dc-client.py --config=../ini/dc-client.ini --command=BATCH --file=$INPUT_FILE > $OUTPUT_FILE
echo "done"
exit 0


