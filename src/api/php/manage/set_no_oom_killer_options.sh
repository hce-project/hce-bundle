#!/bin/bash

. ../cfg/current_cfg.sh

printUsage()
{
  echo "Usage: $0 process=<process_name> debug=<debug_value>"
  echo "<process_name> - process name for block OOM-Killer,"
  echo "                 'hce-node' will be use as default if not set"
  echo "<debug_value>  - numeric value for allowed debug mode,"
  echo "                 value more than 0 is debug mode"
  echo ""
  exit 1
}


parseOptions "$@"

if [ "$ARG_HELP" == "1" ]
then
  printUsage
fi

#echo "process: $process"

if [ "$process" == "" ]
then
  PROCESS_NAME="hce-node"
else
  PROCESS_NAME="$process"
fi

#echo "debug: $debug"

if [[ $debug -gt 0 ]]
then
  DEBUG="1"
else
  DEBUG="0"
fi

#echo "DEBUG: $DEBUG"

echo -n "Blocking OOM-Killer for process names: '$PROCESS_NAME' "

pids=(`ps -A -o pid,cmd|grep $PROCESS_NAME | grep -v grep | awk '{print $1}'`)

if [ $DEBUG == "1" ]
then
  echo " Current pid: $$"
  echo "list of pids: ${pids[@]}"
else
  echo ""
fi

for pid in "${pids[@]}"
  do
    FILE="/proc/$pid/oom_score_adj"
    if [ -f $FILE ]
    then 
      if [ $pid != $$ ]
      then
        sudo echo -17 > $FILE && echo "$pid - Success" || echo "$pid - Fail"  
      else
        if [ $DEBUG == "1" ]
        then  
          echo "$pid - Skipped, because it's current process '$0'."
        fi
      fi
    else
      if [ $DEBUG == "1" ]
      then 
        echo "$pid - Skipped, because file $FILE alredy not exist."  
      fi
    fi
  done

echo "Finished."
