#!/bin/bash

./config.sh n s

./start_all.sh

./config.sh m s

./start_all.sh

./config.sh n s

## bloking oom killer for 'hce-node' optionaly
if [[ ("$1" = "--no-oom-killer") || ("$1" = "-n") ]]
then
  ./set_no_oom_killer_options.sh
fi