#!/bin/bash
# simple HCE project DRCE Functional Object starter for asynchronous tasks run
# Usage variables:
# $1 - command
# $2 - stdin

#Enable store picles
#export ENV_CRAWLER_STORE_PATH="/tmp/"

#Disable store picles
export ENV_CRAWLER_STORE_PATH=""

eval "$1 < $2"
