#! /bin/bash
#
#
#
# system dependent settings
#

. ./cfg/current_cfg.sh

. ./cfg/screen_cfg.sh

case ${PKGEXT} in
  deb)
    . ./cfg/dpkg.sh
    ;;
  rpm)
    . ./cfg/rpm.sh
    ;;
  *)
    # not supported
esac

. ./cfg/ldd_cfg.sh


function chk_sys_pkgs_list() {
  # check if there are needed packages on disk
  find ${packages} -mindepth 1 -maxdepth 1 -type f -name "${1}_*_${arch}\.${PKGEXT}" | sort
}
