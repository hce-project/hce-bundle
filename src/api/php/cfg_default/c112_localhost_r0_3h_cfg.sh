#!/bin/bash

. ../cfg/general_cfg.sh

#smanager (sends to all connected)
#rmanager or or rmanager-round-robin (sends to one of several connected round-robin way)
#rmanager-rnd (sends to one of random client)
##MANAGER_MODE="rmanager-rnd"
MANAGER_MODE="rmanager-resources-usage"

#Valgring profiling: 0 - not used, 1 - used. If valgrind profiling used, operation time of any kind action, command, request and so on grow and can be twice or more longer.
USE_VALGRIND=0

#Local host host name
HOST="localhost"
#Data nodes host name
REPLICAS=( "localhost" )

#Management data nodes instances ports
#REPLICAS_MANAGE_ADMIN_PORTS=( 5740 5741 )
#REPLICAS_MANAGE_ADMIN_PORTS=( 5740 5741 5742 )

#Searchers data nodes instances ports
#REPLICAS_POOL_ADMIN_PORTS=( 5730 )
#REPLICAS_POOL_ADMIN_PORTS=( 5730 5731 )
#REPLICAS_POOL_ADMIN_PORTS=( 5730 5731 5732 )
#REPLICAS_POOL_ADMIN_PORTS=( 5730 5731 5732 5733 )
#REPLICAS_POOL_ADMIN_PORTS=( 5730 5731 5732 5733 5734 5735 5736 5737 5738 5739 )

#Router host name
ROUTER="$HOST"
#Router ports
ROUTER_SERVER_PORT="5757"
ROUTER_ADMIN_PORT="5746"
ROUTER_CLIENT_PORT="5756"

#Manager (shard or replica) host and ports
MANAGER="$HOST"
SHARD_MANAGER_ADMIN_PORT="5749"
SHARD_MANAGER_SERVER_PORT="5758"

#Remote hosts and ports csv lists with strict correspondence
REMOTE_HOSTS="10.0.0.2,10.0.0.2,10.0.0.2,10.0.0.2,10.0.0.3,10.0.0.3,10.0.0.3,10.0.0.3"
REMOTE_PORTS="5730,5731,5732,5733,5730,5731,5732,5733"

NODE_APP_LOG_PREFIX="r0-3h"

#Accumulate list of replica admin ports in the csv string
REPLICA_ADMIN_PORTS_CSV=" "
for PORT in "${REPLICAS_MANAGE_ADMIN_PORTS[@]}"
  do
    REPLICA_ADMIN_PORTS_CSV="$REPLICA_ADMIN_PORTS_CSV$PORT,"
  done
for PORT in "${REPLICAS_POOL_ADMIN_PORTS[@]}"
  do
    REPLICA_ADMIN_PORTS_CSV="$REPLICA_ADMIN_PORTS_CSV$PORT,"
  done

if [ "$REPLICA_ADMIN_PORTS_CSV" != " " ]; then
   REPLICA_ADMIN_PORTS_CSV="${REPLICA_ADMIN_PORTS_CSV:1:${#REPLICA_ADMIN_PORTS_CSV}-2}"
fi

INI_FILE_POOL="node_pool_r"

#CSV lists of hosts and ports for the manager commands like properties, schemas and so on
CMD_HOSTS_CSV="$HOST,$HOST"
CMD_PORTS_CSV="$ROUTER_ADMIN_PORT,$SHARD_MANAGER_ADMIN_PORT"
#Fill lists of remote nodes in case of remote hosts or ports is not empty
if [ "$REMOTE_HOSTS" != "" ]; then
  CMD_HOSTS_CSV="$CMD_HOSTS_CSV,$REMOTE_HOSTS"
fi
if [ "$REMOTE_PORTS" != "" ]; then
  CMD_PORTS_CSV="$CMD_PORTS_CSV,$REMOTE_PORTS"
fi
