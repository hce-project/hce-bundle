#!/bin/bash

HCE=~/hce-node-bundle/api/php/tests

cd $HCE 

pwd=`pwd`
echo "pwd: $pwd"
. ../cfg/current_cfg.sh


parseOptions "$@"

echo "param: $param"

