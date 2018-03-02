#! /bin/sh
#
#

. ./cfg/php_cfg.sh

function chk_php_file_exist() {
  say "Checking for ${1} presence... "

  if [ -f "${INC}/${1}" ]; then
    rc="yes"
  else
    rc="no"
  fi

  echo -ne "${rc}\n"

  if [ "${rc}" == "no" ]; then
    say "\nAn include file missing: ${scr}!\n"
    exit 1
    # status="fail"
  fi
}

function chk_php_class_exist {
  say "Checking for class ${2} in file ${1}... "

  rc=`./php/php_symbol_test.php ${1} class ${2}`

  echo -ne "${rc}\n"

  if [ "${rc}" == "no" ]; then
    say "\nA class ${2} is missing!\n"
    exit 1
    # status="fail"
  fi
}

function chk_php_func_exist {
  say "Checking for function ${2}... "

  rc=`./php/php_symbol_test.php ${1} func ${2}`

  echo -ne "${rc}\n"

  if [ "${rc}" == "no" ]; then
    say "\nA function ${2} is missing!\n"
    exit 1
    # status="fail"
  fi
}

function chk_php_apis {
  # include file name
  inc_file=${1}
  # shift args array left, 
  # to get rid of 1st element
  shift

  echo "Checking for ${inc_file} API's... "
  while [ "$1" != "" ]; do
    api=$1; shift

    chk_php_func_exist "$inc_file" ${api}

    if [ "${status}" = "fail" ]; then
      say "\nCheck failed!\n"
      #say "The file ${inc_file} is missing ${api} function!\n"
      exit 1;
    fi
  done
}

function chk_php_module {
  mod=${1}
  # check for PHP module available
  say "Checking for ${mod} PHP module... "
  if [ "`${PHP} -m | grep ${mod} | uniq`" = "${mod}" ]; then
    rc="yes"
  else
    rc="no"
  fi

  echo -ne "${rc}\n"

  if [ "${rc}" == "no" ]; then
    say "\nA function ${2} is missing!\n"
    exit 1
    # status="fail"
  fi
}

function chk_php_includes {
  for scr in $*; do
    chk_php_file_exist ${scr}

    if [ "${status}" = "fail" ]; then
      say "\nCheck failed!\n"
      say "The include file ${scr} is missingn!\n"
      exit 1;
    fi
  done
}

function chk_php_api_groups {
  for group in $*; do
    file="${group}.inc.php"
    chk_php_apis ${file} ${!group}
  done
}


