#! /bin/sh
#
#

. ./cfg/py_cfg.sh

# check if the given module can be imported
function chk_py_module_inc() {
  say "Trying to include ${1} module... " >&2
  rc=`./python/py_module_test.py -m ${1}`

  if [ "${rc}" = "0" ]; then
    rc="yes"
  else
    rc="no"
  fi

  echo -ne "${rc}\n"

  if [ "${rc}" = "no" ]; then
    say "\nImport test failed for ${1}!\n"
    exit 1
  fi
}

function chk_py_module_installed() {
  # try check it in pip database
  say "Checking ${1} to be installed, according to pip base... " >&2
  rc=`pip freeze 2>/dev/null | grep -i ${1} | grep -v grep | \
         awk -F== -v name=${1} 'BEGIN {
    ret = "no"
  }
  {
    if (tolower(name) != tolower($1)) {next}

    ret = "yes"
  }
  END {
    print ret
  }'`

  if [ "${rc}" = "no" ]; then
    say "\nImport test failed for ${1}!\n"
    exit 1
  fi

  echo -ne "${rc}\n"
}
