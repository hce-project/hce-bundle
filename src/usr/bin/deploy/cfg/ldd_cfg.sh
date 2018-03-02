#! /bin/sh
#
#

function chk_sys_missing_libs() {
  say "Checking for missing ${1} executable dependent libraries... " >&2
  deps=`ldd ${1} | awk -F '=>' '{
    if ($2 ~ /not found/)
    {
      print $1
    }
  }' | uniq`

  if [ -z "${deps}" ]; then
    echo "none"
  else
    echo ${deps}
  fi
}


