#!/bin/bash

. ../cfg/current_cfg.sh

if [ -d "$DUMP_DIR" ]; then
  rm -R $DUMP_DIR/*
fi
