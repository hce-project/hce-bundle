#! /bin/bash
#
#

# reinstall test
function chk_sys_pkg_reinstall() {
  # get a list of package versions
  pack=${1}
  versions=`chk_sys_pkgs_list ${pack}`

  # find the last version (alphabetically)
  for ver in ${versions}; do
    lastver=${ver}
  done

  # install all versions over the last one, and vice versa
  for ver in ${versions}; do
    if [ "${ver}" != "${lastver}" ]; then
      say "Installing the older version over the newer one: ${ver}\n"
      dpkg -i ${ver} >/dev/null 2>&1
      # do version check
      chk_sys_pkg_version  ${pack}
      # do md5 check
      chk_sys_pkg_md5      ${pack}

      say "Installing the newest version: ${lastver} back\n"
      dpkg -i ${lastver} >/dev/null 2>&1
      # do version check
      chk_sys_pkg_version  ${pack}
      # do md5 check
      chk_sys_pkg_md5      ${pack}
    fi
  done
}


 