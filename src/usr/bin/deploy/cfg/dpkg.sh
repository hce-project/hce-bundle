#! /bin/bash
#
# dpkg-related functions
#

# is the package installed, according to
# the package manager database
function chk_sys_pkg_installed() {
  say "Checking for ${1} to be installed... " >&2
  dpkg -S ${1} 2>/dev/null | awk -v pkg=${1} 'BEGIN {
    cnt=0
  }
  {
    if (index($0, pkg) == 1) {
      cnt++
    }
  }
  END {
    if (cnt == 0) {
      print "no"
    }
    else {
      print "yes"
    }
  }'
#  dpkg -s ${1} 2>/dev/null | awk -v pkg=${1} 'BEGIN {
#    cnt=0
#  }
#  {
#    if ($1 ~ /^Package\:/) {
#      if ($2 == pkg) {
#        cnt++
#      }
#    }
#    else if ($1 ~ /^Status\:/) {
#      if ($3 == "ok" && cnt > 0) {
#        if ($2 == "install")
#          print "yes"
#        else
#          print "no"
#
#        cnt++
#      }
#    }
#    else {
#      next
#    }
#  }
#  END {
#    if (cnt == 0) {
#      print "no"
#    }
#  }'
}

# get binaries list from the given package
function get_sys_pkg_binaries() {
  # compare package contents
  # with unpacked files
  say "Checking ${1} contents for binaries: \n" >&2
  dpkg -S ${1} 2>/dev/null | awk '{
#    cmd1  = "file " $2
#    cmd2  = "md5sum " $2
#    cmd1  | getline type
#    close(cmd1)
#    if (type ~ /\ directory$/) next
#    cmd2  | getline md5 file
#    close(cmd2)
#    printf "%s  %s\n", md5, file
    if ($2 ~ /\/.+bin\//) {
      print $2
    }
  }'
}


function chk_sys_pkg_version() {
  # get an installed package version
  say "Checking ${1} version: " >&2
  dpkg -s ${1} 2>/dev/null | awk 'BEGIN {
    cnt = 0
  }
  {
    if ($1 ~ /^Version\:/) {
      print $2
      cnt++
    }
    next
  }
  END {
    if (cnt == 0) {
      print "none"
    }
  }'
}

function chk_sys_pkg_md5() {
  # check the md5 sums to be
  # equal on disk and in the last package
  say "Checking ${1} for md5 sums correctness: " >&2
  deb=${1}
  vers=`chk_sys_pkg_version ${deb} 2>/dev/null`
  if [ "`echo ${deb} | grep '\.deb$'`" = "" ]; then
    # if it is a not full package name,
    # without version, '.deb' extension etc.
    deb="${packages}/${1}_${vers}_${arch}.deb"
    # echo "deb=${deb}"
  fi
  debsums ${deb} 2>&1 | awk 'BEGIN {
    cnt = 1
  }
  {
    if ($2 != "OK") cnt = 0
  }
  END {
    if (cnt == 1)
      print "yes"
    else
      print "no"
  }'
  if [ "$?" != "0" ]; then
    say "\nmd5 sums check failed (the files on the disk"
    say "and in the package don't the same)!\n"
    exit 1
  fi
}

# get package dependencies, according to the package manager
function get_sys_pkg_deps() {
  dpkg -s ${1} 2>/dev/null | awk -F: '/^Depends\:\ /{print substr($0, 10)}' | awk -v RS=, '
  { print $1 }'
}

function sys_pkg_init() {
  # install a program for checking the correspondence of
  # md5 sums of files on disk and in the package
  rc=`chk_sys_pkg_installed "debsums"`

  if [ "${rc}" = "yes" -o "${rc}" = "no" ]; then
    echo "${rc}"
  fi

  # debsums utility checks installed packages
  # md5 checksums
  if [ "${rc}" != "yes" ]; then
    apt-get update
    apt-get install debsums
  fi
}
