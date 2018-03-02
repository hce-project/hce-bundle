#! /bin/sh
#
# A poor man debootstrap for an RPM-based Linux distros :)
# usage:
# >
# > bootstrap-centos.sh <distro> <rel> <minor>
#
# (c) Valery 'valerius' Sedletski,
# Feb 2014
#

ARCH="x86_64"

CWD=`pwd`
MINOR=""

if [ "${3}" ]; then
    ROOT="${CWD}/${1}-${2}.${3}"
else
    ROOT="${CWD}/${1}-${2}"
fi

case ${1} in
fedora)
    # Fedora
    REV=${2}
    REP="${1}-${REV}"
    MIRROR="http://fedora.inode.at/fedora/linux/releases/${REV}/Everything/${ARCH}/os/"
    YUMCFGDIR="${ROOT}/etc/yum.repos.d"
    ;;
centos)
    # CentOS
    REV=${2}
    [ ${3} ] && MINOR=".${3}"
    REP="${1}-${REV}${MINOR}"
    MIRROR="http://mirror.centos.org/centos/${REV}${MINOR}/os/${ARCH}/"
    YUMCFGDIR="${ROOT}/etc/yum.repos.d"
    ;;
suse|opensuse)
    # SuSe
    REV=${2}
    if [ -z "${3}" ]; then
	echo No minor version specified!
	exit 2
    fi
    MINOR=".${3}"
    REP="${1}-${REV}${MINOR}"
    MIRROR="http://download.opensuse.org/distribution/${REV}${MINOR}/repo/oss/suse/"
    YUMCFGDIR="${ROOT}/etc/yum/repos.d"
    ;;
*)
    echo Unknown distro!
    exit 1
esac

REPOFILE="/tmp/new.repo"

mkdir -p ${YUMCFGDIR}
mkdir -p ${ROOT}/var/lib/rpm

rpm --root=${ROOT} --rebuilddb

# create temporary repo file
echo "#
#
#
[main]
multilib_policy=best
keepcache=1
gpgcheck=0
plugins=0
tolerant=1
assumeyes=1
cachedir=/var/cache/yum/

[base]
name=Base repo ${REP}
baseurl=${MIRROR}

###
" >${REPOFILE}

# bootstrap a full system as yum dependencies
yum -c ${REPOFILE} --installroot=${ROOT} --disablerepo=* \
    --enablerepo=base install yum  # rpm-build

mv ${REPOFILE} ${YUMCFGDIR}
