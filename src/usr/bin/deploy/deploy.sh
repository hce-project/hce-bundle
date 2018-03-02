#! /bin/bash
#
# Deploy HCE-NODE with tests and API bindings
# Syntax: ./deploy <somedir>
#

# Locale
export LC_ALL=C LANG=en_US

# escape sequences
red='\e[0;31m'
nc='\e[0m'

# tests archive name
ARCH_FILE="hce-node-tests"
# tests archive path
FILE_PKG="/usr/share/hce-node/${ARCH_FILE}"

# Any Debian repo
main_repo="http://ftp.debian.org/debian"
# HCE project repo
hce_repo="http://packages.hierarchical-cluster-engine.com/debian"
# Linux release codename
suite="wheezy"
#suite="jessie"

# Say a string in RED color
say() {
  echo -e "${red}${1}"
  echo -e ${nc}
}

# Do a MySQL query
mysql() {
  say "MySQL: ${1}"
  # users database name
  DB="mysql"
  if [ "`${CHROOT} ${CHROOTDIR} ls /var/run/mysqld | grep sock`" != "mysqld.sock" ]; then
    say "No MySQL server socket, it may be not running!"
    ${CHROOT} ${CHROOTDIR} /etc/init.d/mysql restart
    sleep 3
  fi
  # mysql default maintenance password
  MYPW=`cat ${CHROOTDIR}/etc/mysql/debian.cnf | grep password | uniq | awk '{print $3}'`
  ${CHROOT} ${CHROOTDIR} /usr/bin/mysql -udebian-sys-maint -p${MYPW} ${DB} -e"${1}"
  if [ "$?" != "0" ]; then
     say "MySQL query failed!"
     exit 1
  fi
}

# bootstrap a minimal system
bootstrap() {
  if [ ! -f ${BOOTSTRAP_FLAG} ]; then
    if [ "${1}" ]; then
      say "Bootstrapping  a minimal system"
      debootstrap ${suite} ${1} ${main_repo}
    fi
    if [ "$?" = "0" ]; then 
      touch ${BOOTSTRAP_FLAG}
      say "Bootstrap successful."
    else
      say "Bootstrap failed! Some packages, or whole distribution, may be missing!"
      rm -f ${BOOTSTRAP_FLAG}
      exit 2
    fi
  fi
}

# install a HCE repo description
hce_repo_inst() {
  if [ -f ${BOOTSTRAP_FLAG} ]; then
    say "Adding HCE project repo into /etc/apt/sources.list.d"
    echo  "deb ${hce_repo} ${suite} main" > ${CHROOTDIR}/etc/apt/sources.list.d/hce.list
    ${CHROOT} ${CHROOTDIR} apt-get update
  fi
}

# Install a package in a chroot from repo
sys_inst() {
  say "Installing $*"
  ${CHROOT} ${CHROOTDIR} apt-get -y --force-yes install $*
  if [ "$?" != "0" ]; then
    say "One of these packages:  $*  (or their dependencies) may be missing, or wrong repo!"
    exit 3
  else
    say "Success."
  fi
}

# Install a PHP extension by PECL
pecl_inst() {
  say "Installing $*"
  for i in $*; do
    rc=`${CHROOT} ${CHROOTDIR} pecl info $i | awk '{if ($1 == "Name") print $2}'`
    if [ "$rc" != "$i" ]; then
      say "$i is not yet installed, proceeding with install..."
      ${CHROOT} ${CHROOTDIR} pecl install $*
      if [ $? -eq 0 ]; then
         say "Success."
      #else # PECL has strange logic -- it 
            # returns an non-zero error code
            # if the package is already installed!
            # (it must pass it over, like others)
         #say "Fail!"
      fi
    else
      say "$* already installed, skipping"
    fi
  done
}

# Install a Python extension by PIP
pip_inst() {
  say "Installing $*"
  ${CHROOT} ${CHROOTDIR} pip install $*
  if [ $? -ne 0 ]; then
    say "Installation of $* failed."
    say "Make sure all steps before succeeded!!"
    exit 5
  else
    say "Success."
  fi
}

# install zmq.so into PHP5 configs
zmq_conf_inst() {
  say "Installing zmq.so into php-cli"
  echo "extension=zmq.so" > "${CHROOTDIR}/etc/php5/mods-available/zmq.ini"
  ln -sf "${CHROOTDIR}/etc/php5/mods-available/zmq.ini" "${CHROOTDIR}/etc/php5/conf.d/20-zmq.ini" 
}

unpack() {
  if [ -f ${1} ]; then
    cd ${FILE_DEST}
    if [ -d ${TESTS_DIR} ]; then
      say "Directory with tests exists. Backing it up..."
      zip -r9q ${TESTS_DIR}-`date +%Y-%m-%d`-`date +%s`.zip ${TESTS_DIR}
      say "Removing it..."
      rm -rf ${TESTS_DIR}
    fi
    say "Unzipping the new tests archive..."
    unzip -oq ${1}
    say "Setting executable permissions for needed files"
    find ${TESTS_DIR} -type f -name '*.sh'  | xargs chmod 755
    find ${TESTS_DIR} -type f -name '*.php' | xargs chmod 755
    find ${TESTS_DIR} -type f -name '*.py'  | xargs chmod 755
    cd ${CWD}
  fi
}


if [ -z "${1}" ]; then
  say "No installation directory specified!"
  say "\"/\" means the host system, otherwise the chrooted one"
  exit 2
else
  if [ "${1}" = "/" ]; then
    CHROOT=""
  else
    CHROOT="chroot "
  fi
fi

# chroot dir
if [ -n "${CHROOT}" ]; then
  # current dir
  CWD=`pwd`
  CHROOTDIR="${CWD}/${1}"
else
  CHROOTDIR=""
fi

# destination
FILE_DEST=${CHROOTDIR}${HOME}
# 'bootstrap complete' flag
BOOTSTRAP_FLAG=${CHROOTDIR}/bootstrap.flg
# unpacked dir
TESTS_DIR="hce-node-tests"

# Create the main directory (if it doesn't exist)
if [ ! -d ${CHROOTDIR} ]; then
  mkdir -p ${CHROOTDIR}
fi

# Killing MySQL daemon (it will 
# be restarted when being installed)
killall mysqld

# Bootstrap a minimal system
bootstrap ${CHROOTDIR}

# Install info about HCE repo to /etc/apt
hce_repo_inst

# Install the main package (with deps)
sys_inst "hce-node"

# Install DTS (unpack an archive,
# with previous version backup)
unpack ${FILE_PKG}.zip

# Install PHP pre-reqs
sys_inst pkg-config g++ make libpgm-dev libzmq3-dev php5-cli php5-dev php5-mysql php-pear sphinxsearch

# Install PHP ZMQ module
pecl_inst zmq-beta

# Installing ZMQ module config into PHP5
zmq_conf_inst

# Add packages for PHP API tests
sys_inst bc php5-gmp ruby # openjdk-7-jdk ???

# Add packages for DTM
say "Installing the system packages fot DTM"
sys_inst mysql-server-5.5 mysql-client-5.5 python-pip python-dev python-flask \
  python-flaskext.wtf libffi-dev libxml2-dev libxslt1-dev python-mysqldb libicu-dev libgmp3-dev
say "Installing Python packages for DTM"
pip_inst cement sqlalchemy Flask-SQLAlchemy scrapy pyzmq lepl requests # gmpy

# Setup MySQL user and grant rights
if [ -z "`mysql 'SELECT user FROM user;' | grep 'hc-user'`" ]; then
  say   "No HCE user, creating it..."
  mysql 'CREATE USER "hc-user"@"localhost" IDENTIFIED BY "hc689";'
  mysql 'CREATE USER "hc-user"@"%" IDENTIFIED BY "hc689";'
  mysql 'GRANT ALL ON *.* TO "hc-user"@"localhost";'
  mysql 'GRANT ALL ON *.* TO "hc-user"@"%";'
else
  say "hc-user already exists."
fi

# All done
say 'Done.'
