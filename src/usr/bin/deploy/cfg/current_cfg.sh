#! /bin/bash
#
#

# Linux distribution we are using
# (deb/rpm)
PKGEXT="deb"
# PKGEXT="rpm"

# path to different hce-node
# package versions, for reinstall test
#packages=~

# packages path (probably, apt cache)
packages="/var/cache/apt/archives"

# architecture
arch=`uname -m`

if [ "${arch}" = "x86_64" ]; then
  arch=amd64
fi

CFG_DIR=../cfg
LOG_DIR=../log
