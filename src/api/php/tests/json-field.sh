#!/bin/bash

. ../cfg/current_cfg.sh

LOG_FILE="$LOG_DIR$0.log"
DATADIR="$DATA_DIR/json-field/"

$BIN_DIR./json-field.php --field=0:id < "$DATADIR"1.json > "$LOG_FILE".2.json

$BIN_DIR./json-field.php --field=0:data:tagList:data:0:data:0 < "$DATADIR"1a.json > "$LOG_FILE".2a.json

$BIN_DIR./json-field.php --field=@ < "$DATADIR"1a.json > "$LOG_FILE".2b.json

$BIN_DIR./json-field.php --field=@ --xml=1 < "$DATADIR"1a.json > "$LOG_FILE".2b.xml
