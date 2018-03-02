#! /bin/bash
#

arch="amd64"

red='\e[0;31m'
nc='\e[0m'

cache="/var/cache/apt/archives"

function say() {
  echo -ne "${red}$*"
  echo -ne "${nc}"
}

function chk_package_installed() {
  say "Checking for ${1} to be installed... " >&2
  dpkg -s ${1} 2>/dev/null | awk -v pkg=${1} 'BEGIN {
    cnt=0
  }
  {
    if ($1 ~ /^Package\:/) {
      if ($2 == pkg) {
        cnt++
      }
    }
    else if ($1 ~ /^Status\:/) {
      if ($2 == "install"   && $3 == "ok" && 
          $4 == "installed" && cnt > 0) {
        print "yes"
      }
    }
    else {
      next
    }
  }
  END {
    if (cnt == 0) {
      print "no"
    }
  }'
}

function chk_package_contents() {
  # compare package contents
  # with unpacked files
  say "Checking ${1} contents: \n" >&2
  dpkg -S ${1} 2>/dev/null | awk '{
    cmd1  = "file " $2
    cmd2  = "md5sum " $2
    cmd1  | getline type
    close(cmd1)
    if (type ~ /\ directory$/) next
    cmd2  | getline md5 file
    close(cmd2)
    printf "%s  %s\n", md5, file
  }'
}


function chk_package_version() {
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

function chk_package_md5() {
  # check the md5 sums to be
  # equal on disk and in the last package
  say "Checking ${1} for md5 sums correctness: " >&2
  deb=${1}
  if [ "grep '.deb$' ${deb}" = "" ]; then
    # if it is a not full package name,
    # without version, '.deb' extension etc.
    deb="${cache}/${1}_${vers}_${arch}.deb"
  fi
  vers=`chk_package_version ${1} 2>/dev/null`
  debsums ${deb} | awk 'BEGIN {
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
}

function chk_missing_libs() {
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

if [ "`chk_package_installed debsums`" = "no" ]; then
  apt-get update
  apt-get install debsums
fi

pkglist="libmsgpack3 libpocofoundation22 libpocoutil22 libpocoxml22 \
      libpocojson22 libzmq3 hce-node"

for pkg in $pkglist; do
  # check each package to be installed
  rc=`chk_package_installed ${pkg}`
  echo ${rc}
  if [ "$rc" = "no" ]; then
    say "Interrupted!"
    exit 1
  fi
done

# get missing dep libs list
rc=`chk_missing_libs '/usr/bin/hce-node'`
echo ${rc}

chk_package_contents 'hce-node'
chk_package_version  'hce-node'
chk_package_md5      'hce-node'

pkg1="${cache}/hce-node_1.1-5_amd64.deb"
pkg2="${cache}/hce-node_1.2-3_amd64.deb"

say "Installing the older version above the newer one: ${pkg1}"
dpkg -i ${pkg1} >/dev/null 2>&1
chk_package_version  'hce-node'
chk_package_md5      'hce-node'

say "Installing the newer version: ${pkg2}"
dpkg -i ${pkg2} >/dev/null 2>&1
chk_package_version  'hce-node'
chk_package_md5      'hce-node'
