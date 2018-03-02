#!/bin/bash

DIALOG=${DIALOG=dialog}
TEMPFILE=`mktemp /tmp/check.XXXXXX`
trap "rm -f $TEMPFILE" 0 1 2 5 15
TITLE='Check Script For HCE-NODE'

CHECKDEBIAN='/etc/debian_version'
CHECKCENTOS='/etc/redhat-release'

REQUESTS_NEED_MIN_VERSION="2.4.3"
REQUESTS_NEED_MAX_VERSION="2.7"

GOOSE_NEED_MIN_VERSION="1.0.22"
GOOSE_NEED_MAX_VERSION="1.0.22"

PSUTIL_NEED_MIN_VERSION="4.1.0"
PSUTIL_NEED_MAX_VERSION="4.1.0"

DEBIAN_PACKAGES_BUNDLE_PHP=( bsdutils unzip hce-node libzmq3-dev php5 php5-curl php5-gd php5-mcrypt php5-dev php-pear pkg-config libpgm-dev bc g++ )
DEBIAN_PACKAGES_BUNDLE_PYTHON=( libpgm-dev mysql-server python-pip python-dev python-flask python-flaskext.wtf libffi-dev libxml2-dev libxslt1-dev mysql-client libmysqlclient-dev python-mysqldb libicu-dev libgmp3-dev libtidy-dev libjpeg-dev email dateutils )
DEBIAN_PACKAGES_BUNDLE_PYTHON_7=( libpgm-dev mysql-server python-pip python-dev python-flask python-flaskext.wtf libffi-dev libxml2-dev libxslt1-dev mysql-client libmysqlclient-dev python-mysqldb libicu-dev libgmp3-dev libtidy-dev libjpeg8-dev email dateutils )
DEBIAN_PACKAGES_CRAWLER_PYTHON=( python-pip python-dev libffi-dev libxml2-dev libxslt1-dev )
DEBIAN_PYTHON_BUNDLE_PYTHON=( cement sqlalchemy flask flask_sqlalchemy scrapy gmpy zmq requests ndg.httpsclient pyasn1 OpenSSL urlnorm icu MySQLdb newspaper goose tidylib uritools magic feedparser PIL w3lib bs4 snowballstemmer soundex langdetect pycountry validators )
DEBIAN_APACHE=( apache2 )
DEBIAN_OPENJDK=( openjdk-7-jdk )
DEBIAN_RUBY=( ruby )
DEBIAN_DYNAMIC_PAGE_FETCH_SUPPORT=( libexif-dev xvfb libxss1 google-chrome-stable )
DEBIAN_DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON=( selenium psutil )

# NOT RELEVANT #
CENTOS_PACKAGES_BUNDLE_PHP=( hce-node libzmq3-dev php php-devel php-pear pkgconfig openpgm-devel zeromq3-devel sphinx sphinx-php bc )
CENTOS_PACKAGES_BUNDLE_PYTHON=( openpgm-devel mariadb-server mariadb python-pip python-devel python-flask python-flask-wtf libffi-devel libxml2-devel libxslt-devel mariadb-devel mysql-connector-python libicu-devel gmp-devel libtidy-devel python-dateutil )
CENTOS_PACKAGES_CRAWLER_PYTHON=( python-pip python-devel libffi-devel libxml2-devel libxslt-devel )
CENTOS_PYTHON_BUNDLE_PYTHON=( cement sqlalchemy Flask-SQLAlchemy scrapy gmpy pyzmq requests ndg.httpsclient pyasn1 OpenSSL urlnorm pyicu mysql-python newspaper goose-extractor pytidylib uritools python-magic feedparser w3lib beautifulsoup4 snowballstemmer soundex langdetect pycountry validators )
CENTOS_APACHE=( httpd )
CENTOS_OPENJDK=( java-1.7.0-openjdk )
CENTOS_RUBY=( ruby )
CENTOS_DYNAMIC_PAGE_FETCH_SUPPORT=( libexif-dev xvfb libxss1 google-chrome-stable)
CENTOS_DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON=( selenium psutil )
# END OF NOT RELEVANT #

RED='\e[0;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

FORCE=0

# FUNCTIONS #

function infoDialog() {
    if [[ -z $2 ]]
    then
        HEIGHT=5
    else
        HEIGHT=$2
    fi
    $DIALOG --title "$TITLE" \
            --colors --msgbox "$1" $HEIGHT 80
}

function textDialog() {
    $DIALOG --title "$TITLE" \
            --textbox "$1" 20 80
}

function checkSudo() {
    if [[ $SUDO_USER || $USER == 'root' ]]
    then
        [ $FORCE -eq 0 ] && (infoDialog "Script started with top permissions level, please use without sudo or root. Cancelled!"; clear) || echo "Script started with top permissions level, please use without sudo or root. Cancelled!"
        exit 1
    fi
}

function username() {
    $DIALOG --title "$TITLE" \
            --inputbox "Input mysql username" 20 80 $USER 2> $TEMPFILE
    case $? in
        0)
            HCE_USER=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
}

function start() {
    $DIALOG --title "$TITLE" \
            --checklist "Select checks" 20 80 11 0 "File executable permissions?" on \
                                                1 "Bundle environment for PHP language" on \
                                                2 "Python modules" on \
                                                3 "Bundle environment for Python language" on \
                                                4 "Mysql (daemon, databases, user, permissions)" on \
                                                5 "Apache" on \
                                                6 "Distributed Crawler client environment for Python language" on \
                                                7 "Java 7 for DRCE tests suit" on \
                                                8 "Ruby for DRCE tests suit" on \
                                                9 "Check availability of en_US.utf8 locale" on \
                                                10 "Dynamic pages fetcher support" on 2> $TEMPFILE
    case $? in
        0)
            CHECK=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
}

function checkOs() {
	if [[ -f $CHECKDEBIAN ]]
	then
		CHECKOS='debian'
	elif [[ -f $CHECKCENTOS ]]
    then
		echo 'centos'
	else
		exit 1
	fi
}

function checkPermissions() {
    if [[ -f /home/$HCE_USER/hce-node-bundle/usr/bin/check_permissions.sh ]]
    then
        cd /home/$HCE_USER/hce-node-bundle/usr/bin/
        chmod 777 /home/$HCE_USER/hce-node-bundle/usr/bin/check_permissions.sh
        if [[ $(./check_permissions.sh) =~ 'Error' ]]
        then
            echo 'FALSE'
        fi
    else
        echo 'FALSE'
    fi
}

function addPermissions() {
    $DIALOG --title "$TITLE" \
            --yesno "File permissions check failed. Change permissions?" 20 80
    case $? in
        0)
            if [[ -f /home/$HCE_USER/hce-node-bundle/usr/bin/hce-node-permissions.sh ]]
            then
                chmod 777 /home/$HCE_USER/hce-node-bundle/usr/bin/hce-node-permissions.sh
                /home/$HCE_USER/hce-node-bundle/usr/bin/hce-node-permissions.sh
            else
                ADDPERMISSIONS="FALSE"
            fi
    esac
}

function checkInstalledPackage() {
    # $1 - package name
    if [[ $(dpkg -s "$1" 2>/dev/null) ]]
    then
        if [[ ! $(dpkg -s "$1" 2>/dev/null | grep deinstall) =~ "deinstall" ]]
        then
            echo 'INSTALLED'
        fi
    else
        exit 1
    fi
}

function checkInstalledPythonModule() {
    # $1 - module name
    if [[ $(python -c "import $1" 2>/dev/null && echo "INSTALLED") ]]
    then
        #if [[ $1 == "requests" ]]
        #then
        #    REQUESTS_INSTALL_VERSION=$(python -c "import $1;print ($1.__version__)")
        #    if [[ $(versionCompareMore "$REQUESTS_INSTALL_VERSION" "$REQUESTS_NEED_MIN_VERSION") == "GOOD" && $(versionCompareLess "$REQUESTS_INSTALL_VERSION" "$REQUESTS_NEED_MAX_VERSION") == "GOOD" ]]
        #    then
        #        echo 'INSTALLED'
        #    fi
        #else
        #    echo 'INSTALLED'
        #fi
        if [[ $1 == "goose" ]]
        then
            GOOSE_INSTALL_VERSION=$(python -c "import $1;print ($1.__version__)")
            if [[ $(versionCompareMore "$GOOSE_INSTALL_VERSION" "$GOOSE_NEED_MIN_VERSION") == "GOOD" && $(versionCompareLess "$GOOSE_INSTALL_VERSION" "$GOOSE_NEED_MAX_VERSION") == "GOOD" ]]
            then
                echo 'INSTALLED'
            fi
        else
            echo 'INSTALLED'
        fi
        if [[ $1 == "psutil" ]]
        then
            PSUTIL_INSTALL_VERSION=$(python -c "import $1;print ($1.__version__)")
            if [[ $(versionCompareMore "$PSUTIL_INSTALL_VERSION" "$PSUTIL_NEED_MIN_VERSION") == "GOOD" && $(versionCompareLess "$PSUTIL_INSTALL_VERSION" "$PSUTIL_NEED_MAX_VERSION") == "GOOD" ]]
            then
                echo 'INSTALLED'
            fi
        else
            echo 'INSTALLED'
        fi
    else
        exit 1
    fi
}

function checkZmqSo() {
    #if [[ $(grep 'extension=zmq.so' /etc/php5/cli/php.ini) ]]
    if [[ $(php -m | grep zmq) ]]
    then
        echo 'Y'
    else
        exit 1
    fi
}

function checkPhpModule() {
    # $1 - module name
    if [[ $(php -m | grep $1) ]]
    then
        echo 'Y'
    else
        exit 1
    fi
}

function mysqlAccess() {
    [ -z $MYSQLUSER ] && MYSQLUSER='hce'
    [ -z $MYSQLPWD ] && MYSQLPWD='hce12345'
    $DIALOG --title "$TITLE" \
            --inputbox "Input mysql username" 20 80 $MYSQLUSER 2> $TEMPFILE
    case $? in
        0)
            MYSQLUSER=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
    $DIALOG --title "$TITLE" \
            --insecure \
            --passwordbox "Input mysql password" 20 80 $MYSQLPWD 2> $TEMPFILE
    case $? in
        0)
            MYSQLPWD=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
}

function mysqlConnect() {
    # $1 - command
    mysql -u $MYSQLUSER -p$MYSQLPWD  -e "$1" 2>/dev/null && echo "TRUE" || echo "FALSE"
}

function createDb() {
    $DIALOG --title "$TITLE" \
            --yesno "Databases not exist. Create?" 20 80
    case $? in
        0)
            cd /home/$HCE_USER/hce-node-bundle/api/python/manage/
            bash mysql_create_db.sh 2 > /dev/null
            MYSQL[0]="TRUE";;
    esac
}

function checkLocale() {
    if [[ $(locale -a 2>/dev/null | grep 'en_US.utf8') ]]
    then
        echo 'OK'
    fi
    exit 1
}

function versionCompareMore(){
    # $1 - installed version
    # $2 - need version
    unset CHECK
    VERS_INST_ARR=($(echo "$1" | tr '.' '\n'))
    VERS_NEED_ARR=($(echo "$2" | tr '.' '\n'))
    if [[ ${#VERS_INST_ARR[@]} -eq ${#VERS_NEED_ARR[@]} ]]
    then
        MAX=${#VERS_INST_ARR[@]}
    elif [[ ${#VERS_NEED_ARR[@]} -gt ${#VERS_INST_ARR[@]} ]]
    then
        MAX=${#VERS_NEED_ARR[@]}
    else
        MAX=${#VERS_INST_ARR[@]}
    fi
    for COUNT in $(seq 0 $MAX);
    do
        if [[ ${VERS_INST_ARR[$COUNT]} -gt ${VERS_NEED_ARR[$COUNT]} ]]
        then
            CHECK="GOOD"
            break
        fi
        if [[ ${VERS_INST_ARR[$COUNT]} -lt ${VERS_NEED_ARR[$COUNT]} ]]
        then
            CHECK="BAD"
            break
        fi
    done
    if [[ -z $CHECK ]]
    then
        CHECK="GOOD"
    fi
    echo "$CHECK"
}

function versionCompareLess(){
    # $1 - installed version
    # $2 - need version
    unset CHECK
    VERS_INST_ARR=($(echo "$1" | tr '.' '\n'))
    VERS_NEED_ARR=($(echo "$2" | tr '.' '\n'))
    if [[ ${#VERS_INST_ARR[@]} -eq ${#VERS_NEED_ARR[@]} ]]
    then
        MAX=${#VERS_INST_ARR[@]}
    elif [[ ${#VERS_NEED_ARR[@]} -gt ${#VERS_INST_ARR[@]} ]]
    then
        MAX=${#VERS_NEED_ARR[@]}
    else
        MAX=${#VERS_INST_ARR[@]}
    fi
    for COUNT in $(seq 0 $MAX);
    do
        if [[ ${VERS_INST_ARR[$COUNT]} -lt ${VERS_NEED_ARR[$COUNT]} ]]
        then
            CHECK="GOOD"
            break
        fi
        if [[ ${VERS_INST_ARR[$COUNT]} -gt ${VERS_NEED_ARR[$COUNT]} ]]
        then
            CHECK="BAD"
            break
        fi
    done
    if [[ -z $CHECK ]]
    then
        CHECK="GOOD"
    fi
    echo "$CHECK"
}

function mysqlGetDatabases(){
    # GET SCRIPTS WITH CREATE DBS #
    CURRENT_PATH=$(pwd)
    cd ../../api/python/manage
    CREATE_FILES=($(grep mysql_create mysql_create_db.sh | awk -F\/ '{print $2}'))

    # GET INI FILES WITH DB #
    for FILE in "${CREATE_FILES[@]}"
    do
      INI_FILES=("${INI_FILES[@]}" $(grep -E 'mysql.*ini' $FILE | awk -F\< '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//'))
    done
    # GET MYSQL DATABASES #
    if [ ${#INI_FILES[@]} -ne 0 ]
    then
        for MYSQL_DBS in "${INI_FILES[@]}"
        do
            if [ -f "$MYSQL_DBS" ]
            then
                MYSQL_DB=("${MYSQL_DB[@]}" $(grep -i 'create database' $MYSQL_DBS | awk -F\` '{print $2}'))
            fi
        done
    fi
    cd $CURRENT_PATH
}

# END OF FUNCTIONS #

# START #

if [[ -f '/etc/debian_version' ]]
then
    DEBIAN_VERSION_NUM=$(cat /etc/debian_version | awk -F\. '{print $1}')
    PACKAGES_BUNDLE_PHP=${DEBIAN_PACKAGES_BUNDLE_PHP[@]}
    if [[ $DEBIAN_VERSION_NUM -eq 8 ]]
    then
        PACKAGES_BUNDLE_PYTHON=${DEBIAN_PACKAGES_BUNDLE_PYTHON[@]}
    else
        PACKAGES_BUNDLE_PYTHON=${DEBIAN_PACKAGES_BUNDLE_PYTHON_7[@]}
    fi
    PACKAGES_CRAWLER_PYTHON=${DEBIAN_PACKAGES_CRAWLER_PYTHON[@]}
    PYTHON_BUNDLE_PYTHON=${DEBIAN_PYTHON_BUNDLE_PYTHON[@]}
    OPENJDK=${DEBIAN_OPENJDK[@]}
    RUBY=${DEBIAN_RUBY[@]}
    APACHE=${DEBIAN_APACHE[@]}
    DYNAMIC_PAGE_FETCH_SUPPORT=${DEBIAN_DYNAMIC_PAGE_FETCH_SUPPORT[@]}
    DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON=${DEBIAN_DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON[@]}
elif [[ -f '/etc/redhat-release' || -f '/etc/centos-release' ]]
then
    [ $FORCE -eq 0 ] && (infoDialog "Only for debian system. Cancel"; clear) || echo "Only for debian system. Cancel"
    exit 1
    PACKAGES_BUNDLE_PHP=${CENTOS_PACKAGES_BUNDLE_PHP[@]}
    PACKAGES_BUNDLE_PYTHON=${CENTOS_PACKAGES_BUNDLE_PYTHON[@]}
    PACKAGES_CRAWLER_PYTHON=${CENTOS_PACKAGES_CRAWLER_PYTHON[@]}
    PYTHON_BUNDLE_PYTHON=${CENTOS_PYTHON_BUNDLE_PYTHON[@]}
    OPENJDK=${CENTOS_OPENJDK[@]}
    RUBY=${CENTOS_RUBY[@]}
    APACHE=${CENTOS_APACHE[@]}
    DYNAMIC_PAGE_FETCH_SUPPORT=${CENTOS_DYNAMIC_PAGE_FETCH_SUPPORT[@]}
    DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON=${CENTOS_DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON[@]}
else
    [ $FORCE -eq 0 ] && (infoDialog "System not supported (not a centos or debian)!"; clear) || echo "System not supported (not a centos or debian)!"
    exit 1
fi

# CHECK ARGUMENTS #
for ARG in $*
do
    case $ARG in
    'force'|'-force'|'--force')
        FORCE=1;;
    'username='*|'-username='*|'--username='*)
        HCE_USER=$(echo $ARG | awk -F\= '{print $2}');;
    'mysqluser='*|'-mysqluser='*|'--username='*)
        MYSQLUSER=$(echo $ARG | awk -F\= '{print $2}');;
    'mysqlpassword='*|'-mysqlpassword='*|'--mysqlpassword='*)
        MYSQLPWD=$(echo $ARG | awk -F\= '{print $2}');;
    'help'|'-help'|'--help'|*)
        echo "Usage $0 [force] [username=USER, default hce] [mysqluser=MYSQL_USER, default hce] [mysqlpassword=MYSQL_PASSWORD, default hce12345] [help]"
        exit 0;;
    esac
done


function permissions(){
    if [[ $(checkPermissions) == "FALSE" ]]
    then
        CHECKPERMISSIONS='FALSE'
    fi
}
function mysqlCheck(){
    mysqlGetDatabases
    if [[ $(mysqlConnect ";") == 'TRUE' ]]
    then
        if [ ${#MYSQL_DB[@]} -ne 0 ]
        then
            for DATABASE in "${MYSQL_DB[@]}"
            do
                if [[ $(mysqlConnect "use $DATABASE") == "FALSE" ]]
                then
                    MYSQL_DATABASES=("${MYSQL_DATABASES[@]}" "$DATABASE")
                fi
            done
        fi
        if [[ ${#MYSQL_DATABASES[@]} -ne 0 ]]
        then
            createDb
        fi
    else
        if [[ -z $(pgrep mysql) ]]
        then
            MYSQL[3]="not started"
        else
            MYSQL[3]="connection error"
        fi
    fi
}
function localesCheck(){
    if [[ $(checkLocale) ]]
    then
        CHECKLOCALE='TRUE'
    fi
    if [[ -z $CHECKLOCALE ]]
    then
        OUT+=( "Locales en_US.utf8 not added, to add run\n\"dpkg-reconfigure locales\" and select en_US.utf8" )
    fi
}
function bundlePhp(){
    for PACKAGE in ${PACKAGES_BUNDLE_PHP[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_PACKAGES_BUNDLE_PHP_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $PACKAGES_BUNDLE_PHP_NOT_INSTALLED ]]
            then
                PACKAGES_BUNDLE_PHP_NOT_INSTALLED=$PACKAGE
            else
                PACKAGES_BUNDLE_PHP_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
    if [[ -z $(checkPhpModule "mcrypt") ]]
    then
        OUT+=( "mcrypt module not enabled into php, enabled it (\"sudo php5enmod mcrypt\") and reload apache" )
    fi
    if [[ -z $(checkZmqSo) ]]
    then
        OUT+=( "zmq module not added into php, add the \"extension=zmq.so\" to the \"/etc/php5/cli/conf.d/20-zmq.ini\" and reload apache" )
    fi
}
function bundlePython(){
    for PACKAGE in ${PACKAGES_BUNDLE_PYTHON[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED ]]
            then
                PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED=$PACKAGE
            else
                PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}
function crawlerPython(){
    for PACKAGE in ${PACKAGES_CRAWLER_PYTHON[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED ]]
            then
                PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED=$PACKAGE
            else
                PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}
function pythonModules(){
    for PACKAGE in ${PYTHON_BUNDLE_PYTHON[@]}
    do
        if [[ -z $(checkInstalledPythonModule $PACKAGE) ]]
        then
            if [[ $PACKAGE == 'bs4' ]]
            then
                PACKAGE='beautifulsoup4'
            fi
            if [[ $PACKAGE == 'OpenSSL' ]]
            then
                PACKAGE='pyOpenSSL'
            fi
            #if [[ $PACKAGE == 'requests' ]]
            #then
            #    PACKAGE='requests=='$REQUESTS_NEED_MAX_VERSION
            #fi
            if [[ $PACKAGE == 'goose' ]]
            then
                PACKAGE='goose=='$GOOSE_NEED_MAX_VERSION
            fi
            if [[ $PACKAGE == 'psutil' ]]
            then
                PACKAGE='psutil=='$PSUTIL_NEED_MAX_VERSION
            fi
            PIP_PYTHON_BUNDLE_PYTHON_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $PYTHON_BUNDLE_PYTHON_NOT_INSTALLED ]]
            then
                PYTHON_BUNDLE_PYTHON_NOT_INSTALLED=$PACKAGE
            else
                PYTHON_BUNDLE_PYTHON_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}
function checkOpenJdk(){
    for PACKAGE in ${OPENJDK[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_OPENJDK_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $OPENJDK_NOT_INSTALLED ]]
            then
                OPENJDK_NOT_INSTALLED=$PACKAGE
            else
                OPENJDK_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}
function checkRuby(){
    for PACKAGE in ${RUBY[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_RUBY_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $OPENJDK_NOT_INSTALLED ]]
            then
                RUBY_NOT_INSTALLED=$PACKAGE
            else
                RUBY_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}
function checkApache(){
    for PACKAGE in ${APACHE[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_APACHE_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $APACHE_NOT_INSTALLED ]]
            then
                APACHE_NOT_INSTALLED=$PACKAGE
            else
                APACHE_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}
function checkDynamicPageSupport(){
    for PACKAGE in ${DYNAMIC_PAGE_FETCH_SUPPORT[@]}
    do
        if [[ -z $(checkInstalledPackage $PACKAGE) ]]
        then
            APT_DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED ]]
            then
                DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED=$PACKAGE
            else
                DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
    for PACKAGE in ${DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON[@]}
    do
        if [[ -z $(checkInstalledPythonModule $PACKAGE) ]]
        then
            PIP_DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED+=( "$PACKAGE" )
            if [[ -z $DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED ]]
            then
                DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED=$PACKAGE
            else
                DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED+=', '$PACKAGE
            fi
        fi
    done
}

# FORCE #
if [ $FORCE -eq 1 ]
then
    # SUDO CHECK #
    checkSudo
    # HCE USER #
    [ -z $HCE_USER ] && HCE_USER=$USER
    [ -z $MYSQLUSER ] && MYSQLUSER='hce'
    [ -z $MYSQLPWD ] && MYSQLPWD='hce12345'
    # 0 #
    permissions
    # 1 #
    bundlePhp
    # 2 #
    pythonModules
    # 3 #
    bundlePython
    # 4 #
    mysqlCheck
    # 5 #
    checkApache
    # 6 #
    crawlerPython
    # 7 #
    checkOpenJdk
    # 8 #
    # checkRuby
    # 9 #
    localesCheck
    # 10 #
    checkDynamicPageSupport
else
    # CHECK DIALOG INSTALL #
    if [[ -z $(which $DIALOG) ]]
    then
        if [[ -f '/etc/debian_version' ]]
        then
            echo -e $RED"Dialog not installed, please install dialog using ("$BLUE"sudo apt-get install dialog"$RED") and run "$BLUE"$0"$RED" again"$DEF
            exit 1
        elif [[ -f '/etc/redhat-release' || '/etc/centos-release' ]]
        then
            echo -e $RED"Dialog not installed, please install dialog ("$BLUE"sudo yum install dialog"$RED") and run "$BLUE"$0"$RED" again"$DEF
            exit 1
        else
            echo -e $RED"Dialog not installed, please install dialog and run "$BLUE"$0"$RED" again"$DEF
            exit 1
        fi
    fi
    # START DIALOG #
    checkSudo
    username
    start


    case $DEBIAN_VERSION_NUM in
        8)
            for CHOISE in ${CHECK[@]}
            do
                case $CHOISE in
                    0)
                        permissions;;
                    1)
                        bundlePhp;;
                    2)
                        pythonModules;;
                    3)
                        bundlePython;;
                    4)
                        mysqlAccess
                        mysqlCheck;;
                    5)
                        checkApache;;
                    6)
                        crawlerPython;;
                    7)
                        checkOpenJdk;;
                    8)
                        checkRuby;;
                    9)
                        localesCheck;;
                    10)
                        checkDynamicPageSupport;;
                esac
            done
            ;;
        *)
            for CHOISE in ${CHECK[@]}
            do
                case $CHOISE in
                    '"0"')
                        permissions;;
                    '"1"')
                        bundlePhp;;
                    '"2"')
                        pythonModules;;
                    '"3"')
                        bundlePython;;
                    '"4"')
                        mysqlAccess
                        mysqlCheck;;
                    '"5"')
                        checkApache;;
                    '"6"')
                        crawlerPython;;
                    '"7"')
                        checkOpenJdk;;
                    '"8"')
                        checkRuby;;
                    '"9"')
                        localesCheck;;
                    '"10"')
                        checkDynamicPageSupport;;
                esac
            done
            ;;
    esac

fi


if [[ $CHECKPERMISSIONS == "FALSE" ]]
then
    [ $FORCE -eq 1 ] && ADDPERMISSIONS="FALSE" || addPermissions
fi
if [[ $ADDPERMISSIONS == "FALSE" ]]
then
    OUT+=( "Permissions not changed (may be not found file \"hce-node-permissions.sh\" in \"/home/$HCE_USER/hce-node-bundle/usr/bin/\")" )
fi
if [[ ${PACKAGES_BUNDLE_PHP_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_PACKAGES_BUNDLE_PHP_NOT_INSTALLED[@]}"
    OUT+=( "List not installed packages for Bundle Environment for PHP language: $PACKAGES_BUNDLE_PHP_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${PYTHON_BUNDLE_PYTHON_NOT_INSTALLED[@]} ]]
then
    INSTALL="${PIP_PYTHON_BUNDLE_PYTHON_NOT_INSTALLED[@]}"
    OUT+=( "List not installed python modules: $PYTHON_BUNDLE_PYTHON_NOT_INSTALLED, to install modules run\n\"sudo pip install $INSTALL\"" )
fi
if [[ ${PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED[@]}"
    OUT+=( "List not installed package for Bundle Environment for Python language: $PACKAGES_BUNDLE_PYTHON_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${APACHE_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_APACHE_NOT_INSTALLED[@]}"
    OUT+=( "Not installed: $APACHE_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED[@]}"
    OUT+=( "List not installed package for Distributed Crawler client Environment for Python language: $PACKAGES_CRAWLER_PYTHON_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${OPENJDK_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_OPENJDK_NOT_INSTALLED[@]}"
    OUT+=( "Not installed: $OPENJDK_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${RUBY_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_RUBY_NOT_INSTALLED[@]}"
    OUT+=( "Not installed: $RUBY_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED[@]} ]]
then
    INSTALL="${APT_DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED[@]}"
    OUT+=( "Not installed: $DYNAMIC_PAGE_FETCH_SUPPORT_NOT_INSTALLED, to install packages run\n\"sudo apt-get install $INSTALL\"" )
fi
if [[ ${DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED[@]} ]]
then
    INSTALL="${PIP_DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED[@]}"
    OUT+=( "List not installed python modules: $DYNAMIC_PAGE_FETCH_SUPPORT_PYTHON_NOT_INSTALLED, to install modules run\n\"sudo pip install $INSTALL\"" )
fi
if [[ ${MYSQL[1]} && -z ${MYSQL[0]} ]]
then
    OUT+=( "MySQL, database \"dc_urls\" not exists or user $MYSQLUSER does not have permissions to access the database" )
fi
if [[ ${MYSQL[2]} && -z ${MYSQL[0]} ]]
then
    OUT+=( "MySQL, database \"dc_sites\" not exists or user $MYSQLUSER does not have permissions to access the database" )
fi
if [[ ${MYSQL[4]} && -z ${MYSQL[0]} ]]
then
    OUT+=( "MySQL, database \"dc_urls_deleted\" not exists or user $MYSQLUSER does not have permissions to access the database" )
fi
if [[ ${MYSQL[3]} ]]
then
    OUT+=( "MySQL: ${MYSQL[3]}" )
fi

# PRINT RESULT #
if [[ "${OUT[@]}" ]]
then
    for I in "${OUT[@]}"
    do
        OUTDIALOG+="$I\n"
    done
    [ $FORCE -eq 0 ] && (infoDialog "$OUTDIALOG" 20; clear) || echo -e "$OUTDIALOG"
    exit 1
else
    [ $FORCE -eq 0 ] && (infoDialog "All dependencies satisfied."; clear) || echo -e "All dependencies satisfied."
fi

exit 0
