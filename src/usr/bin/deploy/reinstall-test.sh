#! /bin/bash
#
# Different versions of hce-node reinstall one
# over another one
#

# a directory with different versions of a package
packages=~
# packages="/var/cache/apt/archives"
# a package name
pack="hce-node"

. ./cfg/sys.sh

. ./cfg/reinstall_cfg.sh

chk_sys_pkg_reinstall ${pack}
