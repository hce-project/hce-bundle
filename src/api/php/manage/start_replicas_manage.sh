#!/bin/bash

. ../cfg/current_cfg.sh

REPLICAS_ADMIN_PORTS=( "${REPLICAS_MANAGE_ADMIN_PORTS[@]}" )
REPLICAS_TYPE="MANAGE"

. ./start_replicas.sh 1
