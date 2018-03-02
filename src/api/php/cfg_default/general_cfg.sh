#!/bin/bash

#Relative directories path
LOG_DIR="../log/"
INI_DIR="../ini/"
CFG_DIR="../cfg/"
DATA_DIR="../data/"
BIN_DIR="../bin/"
TESTS_DIR="../tests/"
MANAGE_DIR="../manage/"
DUMP_DIR="/tmp/hce-node"

#Ini files for management data nodes
INI_FILE_MANAGE="node_manage"
#Ini file for search data nodes
INI_FILE_POOL="node_pool"

#Operation data mode: 0 - test only plain text random data values, 1 - regular handler-specific data used as default standard mode
DATA_MODE=1

#Utilities executable script names
MANAGER_COMMAND="manager.php"
SEARCH_COMMAND="search.php"
DRCE_COMMAND="drce.php"

#Valgrind command line to start and arguments
VALGRIND_COMMAND="valgrind --leak-check=full --track-origins=yes --read-var-info=yes --freelist-vol=100000000 -v"

LOGGER_INI=../ini/hce-node_log.ini

#Binary executable name
NODE_BIN_NAME="hce-node"

#Timeouts, msec
HUGE_TIMEOUT=90000
BIG_TIMEOUT=30000
SMALL_TIMEOUT=3000
SEARCH_SPHINX_TIMEOUT="2000"

#Test suit data directories names
DRCE_DATA_DIR1="c112_localhost_drce_ft01"
DRCE_DATA_DIR2="c112_localhost_drce_ft02"
DRCE_DATA_DIR_ASYNC="c112_localhost_drce_ft_async"
DRCE_DATA_DIR_KILL_ASYNC="c112_localhost_drce_ft_killed_async"
DRCE_DATA_DIR_MAX_COUNT_ASYNC="c112_localhost_drce_ft_max_count_async"
DRCE_DATA_DIR_SUBTASKS="c112_localhost_drce_ft_subtasks"
DRCE_DATA_DIR_ROUTE="c112_localhost_drce_ft_route"
DRCE_DATA_DIR_LOAD_BALANCE="c112_localhost_drce_ft_load_balance"
DRCE_DATA_DIR_LOAD_BALANCE_ASYNC="c112_localhost_drce_ft_load_balance_async"
DRCE_DATA_DIR_LOAD_STRESS_TESTS="c112_localhost_drce_stress_tests"
SELENIUM_CHROME_DIR="c112_localhost_selenium_tests"

parseOptions()
{
  args=("$@")
  for opt in "${args[@]}"; do
    if [[ ! "${opt}" =~ .*=.* ]]; then
      if [[ ("$1" = "-help") || ("$1" = "-h") || ("$1" = "--help") || ("$1" = "--h") ]]; then
        export ARG_HELP="1"
        return 0
      else
        echo "badly formatted option \"${opt}\" should be: option=value or [--help | -help | --h | -h] - for help"
        return 1
      fi
    fi
    local var="${opt%%=*}"
    local value="${opt#*=}"
    export ${var}="${value}"
  done
  return 0
}
