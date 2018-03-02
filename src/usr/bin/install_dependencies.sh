#!/bin/bash

DIALOG=${DIALOG=dialog}
BACKTITLE='Install Dependencies for HCE project components: hce-node, DTM and DC'
HCE_DEV_FILE='/etc/hce-dev'

RED='\e[0;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

HCE_USER=hce
MYSQL_USER=hce
MYSQL_PWD=hce12345
WWW_USER='www-data'

SCRIPT_NAME=$(basename $0)

TEMPFILE=`mktemp /tmp/$SCRIPT_NAME.XXXXX`
TMPDIR=`mktemp -d /tmp/$SCRIPT_NAME.XXXXXX`
trap "rm -f $TEMPFILE; rm -rf $TMPDIR" 0 1 2 5 15

# FUNCTIONS #

function infoDialog() {
    # $1 - title
    # $2 - info messages
    # $3 - height
    if [[ -z $3 ]]
    then
        HEIGHT=5
    else
        HEIGHT=$3
    fi
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --colors --msgbox "$2" $HEIGHT 80
}

function infoBox() {
    # $1 - title
    # $2 - info messages
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
    --infobox "$2" 20 80
}

function yesNo() {
    # $1 - title
    # $2 - info messages
    $DIALOG --backtitle "$BACKTITLE" --title "$1" --defaultno \
            --yesno "$2" 20 80
    case $? in
        0)
            CHECK="YES";;
        1)
            CHECK="NO";;
        255)
            infoDialog "$1" "Cancel. Exit" && clear && exit 1;;
    esac
}

function textDialog() {
    # $1 - title
    # $2 - info messages
    $DIALOG --backtitle "$BACKTITLE" --title "$1" --exit-label "NEXT"\
            --textbox "$2" 20 80
}



function indicatorDialog() {
    # $1 - info messages
    # $2 - info %%
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --gauge "$1" 20 80 "$2"

}

function checkSudo() {
    if [[ $(whoami) != root ]]
    then
        infoDialog "Error" "Run script with root permissions or sudo: sudo $0 \"USERNAME\""
        clear
        exit 1
    fi
}

function checkOs() {
    if [[ ! -f '/etc/debian_version' ]]
    then
        infoDialog "Error" "This script is only for the Debian system! Cancelled."
        clear
        exit 1
    fi
}
function checkDebianVersion() {
    DEBIAN_VERSION_NUM=$(cat /etc/debian_version | awk -F\. '{print $1}')
}

function checkHomeDir() {
    # $1 = hce user
    if [[ ! -d /home/$1 ]]
    then
        infoDialog "Error" "Home dir (/home/${HCE_USER}) for user ${HCE_USER} not exists! Cancelled."
        clear
        exit 1
    fi
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

function start7() {
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --checklist "Check HCE-project dependencies to install" 20 80 9 \
                                                0 "The en_US.UTF-8 locale (if not present)" on \
                                                1 "Install mysql-server" $MYSQL_CHECKBOX \
                                                2 "PHP language API and management tools" on \
                                                3 "DC service" on \
                                                4 "Python language API and management tools" on \
                                                5 "The pyzmq library with zmq version 4.0.3 from source" on \
                                                6 "Copy test site files to the apache virtual host DocumentRoot" on \
                                                7 "The mysql DB support for default site" on \
                                                8 "Dynamic pages fetcher support (only from local repository) " on 2> $TEMPFILE
    case $? in
        0)
            CHECK=$(cat $TEMPFILE);;
        1)
            infoDialog "Select components" "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Select components" "Cancel. Exit" && clear && exit 1;;
    esac
}

function start() {
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --checklist "Check HCE-project dependencies to install" 20 80 8 \
                                                0 "The en_US.UTF-8 locale (if not present)" on \
                                                1 "Install mysql-server" $MYSQL_CHECKBOX \
                                                2 "PHP language API and management tools" on \
                                                3 "DC service" on \
                                                4 "Python language API and management tools" on \
                                                5 "Copy test site files to the apache virtual host DocumentRoot" on \
                                                6 "The mysql DB support for default site" on \
                                                7 "Dynamic pages fetcher support " on 2> $TEMPFILE
    case $? in
        0)
            CHECK=$(cat $TEMPFILE);;
        1)
            infoDialog "Select components" "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Select components" "Cancel. Exit" && clear && exit 1;;
    esac
}

function mysqlPwd() {
    $DIALOG --backtitle "$BACKTITLE" --title "$TITLE" \
            --insecure \
            --passwordbox "New password for the MySQL \"root\" user:" 20 80 2> $TEMPFILE
    case $? in
        0)
            MYSQLPWD=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
    $DIALOG --backtitle "$BACKTITLE" --title "$TITLE" \
            --insecure \
            --passwordbox "Repeat password for the MySQL \"root\" user:" 20 80 2> $TEMPFILE
    case $? in
        0)
            MYSQLPWDCONFIRM=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
    if [[ $MYSQLPWD != $MYSQLPWDCONFIRM ]]
    then
        infoDialog "The two passwords you entered were not the same. Please try again." && clear
        mysqlPwd
    elif [[ ! $MYSQLPWD ]]
    then
        infoDialog "Passwork not be null. Please try again." && clear
        mysqlPwd
    else
        return
    fi
}

function svnPwd(){
    $DIALOG --backtitle "$BACKTITLE" --title "Svn username" \
            --inputbox "Enter SVN username" 20 80 2> $TEMPFILE
    case $? in
        0)
            SVN_USER=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
    $DIALOG --backtitle "$BACKTITLE" --title "Svn password" \
            --passwordbox "Enter SVN password" 20 80 2> $TEMPFILE
    case $? in
        0)
            SVN_PWD=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
}

function locales() {
    if [[ -z $(checkLocale) ]]
    then
        echo -e '#\nLANG=en_US.UTF-8\n' >> /etc/default/locale
        sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
        (
            COUNT=99
            echo "XXX"
            echo $COUNT
            echo "generate locales..."
            echo "XXX"
            locale-gen
        ) | indicatorDialog "Added locales" "Generate locales..."
        infoDialog "Added locales" "Locale en_US.UTF-8 added" && clear
    else
        infoDialog "Added locales" "Locale en_US.UTF-8 present" && clear
    fi
}

function mysql_server() {
    if [[ $MYSQL_SERVER ]]
    then
        yesNo "Mysql server installation" "Mysql server installed on you system. Reinstall (not recommended)?" && clear
        if [[ $CHECK == "YES" ]]
        then
            mysqlPwd
            infoBox "Mysql server installation" "Mysql server is installed..."
            apt-get update > $TEMPFILE 2>&1
            debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQLPWD"
            debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQLPWD"
            apt-get -y install mysql-server >> $TEMPFILE 2>&1
            textDialog "Mysql server installation..." "$TEMPFILE" && clear
        fi
    else
        mysqlPwd
        infoBox "Mysql server installation" "Mysql server is installed..."
        apt-get update > $TEMPFILE 2>&1
        debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQLPWD"
        debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQLPWD"
        apt-get -y install mysql-server >> $TEMPFILE 2>&1
        textDialog "Mysql server installation..." "$TEMPFILE" && clear
    fi
}

function dtse_php() {
    (
        COUNT=30
        echo "XXX"
        echo $COUNT
        echo "run apt-get update..."
        echo "XXX"
        apt-get update -qq
        COUNT=60
        echo "XXX"
        echo $COUNT
        echo "run apt-get install..."
        echo "XXX"
        apt-get install -y --force-yes bsdutils unzip libzmq3-dev apache2 php5 php5-dev php-pear php5-curl php5-gd php5-mcrypt pkg-config libpgm-dev sphinxsearch > $TEMPFILE 2>&1
        php5enmod mcrypt
        COUNT=80
        echo "XXX"
        echo $COUNT
        echo "run install zmq-beta..."
        echo "XXX"
        echo '' >> $TEMPFILE
        printf "\n" | pecl install zmq-beta >> $TEMPFILE 2>&1
        if [[ -z $(checkZmqSo) ]]
        then
            COUNT=90
            echo "XXX"
            echo $COUNT
            echo "add zmq module to php ini and reload apache"
            echo "XXX"
            echo -e "; configuration for php ZMQ module \n; priority=20 \nextension=zmq.so" > /etc/php5/cli/conf.d/20-zmq.ini
        fi
        service apache2 reload
        echo '' >> $TEMPFILE
        echo 'Done' >> $TEMPFILE 2>&1
    ) | indicatorDialog "Install PHP language API and management tools..." ""
    textDialog "Install PHP language API and management tools..." "$TEMPFILE" && clear
}

function dtse_dc() {
    (
        COUNT=50
        echo "XXX"
        echo $COUNT
        echo "run apt-get update..."
        echo "XXX"
        apt-get update -qq
        COUNT=100
        echo "XXX"
        echo $COUNT
        echo "run apt-get install..."
        echo "XXX"
        apt-get install -y bc openjdk-7-jdk ruby g++ > $TEMPFILE 2>&1
        echo '' >> $TEMPFILE
        echo 'Done' >> $TEMPFILE
    ) | indicatorDialog "Install DC service dependencies..." ""
    textDialog "Install DC service dependencies..." "$TEMPFILE" && clear
}

function dtse_python() {
    (
        COUNT=30
        echo "XXX"
        echo $COUNT
        echo "run apt-get update..."
        echo "XXX"
        apt-get update -qq
        COUNT=60
        echo "XXX"
        echo $COUNT
        echo "run apt-get install..."
        echo "XXX"
        apt-get install -y libpgm-dev python-pip python-dev python-flask python-flaskext.wtf libffi-dev libxml2-dev libxslt1-dev mysql-client libmysqlclient-dev python-mysqldb libicu-dev libgmp3-dev libtidy-dev libjpeg-dev > $TEMPFILE 2>&1
        case $DEBIAN_VERSION_NUM in
            8)
                COUNT=80
                echo "XXX"
                echo $COUNT
                echo "run pip install..."
                echo "XXX"
                echo '' >> $TEMPFILE
                easy_install --upgrade pip >> $TEMPFILE 2>&1
                pip install cement sqlalchemy Flask-SQLAlchemy scrapy gmpy mysql-python pyicu newspaper goose-extractor pytidylib uritools python-magic feedparser pillow beautifulsoup4 w3lib snowballstemmer soundex langdetect pycountry validators >> $TEMPFILE 2>&1
                pip install --no-cache-dir -I pillow
                COUNT=90
                echo "XXX"
                echo $COUNT
                echo "run pip install pyzmq"
                echo "XXX"
                echo '' >> $TEMPFILE
                pip install pyzmq >> $TEMPFILE 2>&1
                ;;
            *)
                COUNT=80
                echo "XXX"
                echo $COUNT
                echo "run pip install..."
                echo "XXX"
                echo '' >> $TEMPFILE
                pip install cement sqlalchemy Flask-SQLAlchemy scrapy gmpy mysql-python pyicu newspaper goose-extractor pytidylib uritools python-magic feedparser pillow beautifulsoup4 w3lib snowballstemmer soundex langdetect pycountry validators >> $TEMPFILE 2>&1
                pip install --no-cache-dir -I pillow
                COUNT=90
                echo "XXX"
                echo $COUNT
                echo "run pip install pyzmq (with option zmq=bundle)..."
                echo "XXX"
                echo '' >> $TEMPFILE
                pip install pyzmq --install-option="--zmq=bundled" >> $TEMPFILE 2>&1
                ;;
        esac
        #pip install -U newspaper==0.0.9.8
        pip install -U email dateutils
        pip install -U scrapy==0.24.4
        pip install -U psutil==4.1.0
        pip install -U goose-extractor==1.0.22
        #pip install -U requests[security]==2.7
        pip install -U newspaper
        #pip install -U scrapy
        #pip install -U goose-extractor==1.0.22
        pip install -U requests[security]==2.7
        COUNT=100
        echo "XXX"
        echo $COUNT
        echo "run pip install urlnorm..."
        echo "XXX"
        echo '' >> $TEMPFILE
        pip install -U urlnorm >> $TEMPFILE 2>&1
        echo '' >> $TEMPFILE
        echo 'Done' >> $TEMPFILE 2>&1
    ) | indicatorDialog "Install Python language API and management tools..." ""
    textDialog "Install Python language API and management tools..." "$TEMPFILE" && clear
}

function pyzmq() {
    (
        COUNT=20
        echo "XXX"
        echo $COUNT
        echo "download zeromq v 4.0.4..."
        echo "XXX"
        cd $TMPDIR
        wget -q https://archive.org/download/zeromq_4.0.4/zeromq-4.0.4.tar.gz
        COUNT=40
        echo "XXX"
        echo $COUNT
        echo "untar zeromq v 4.0.4..."
        echo "XXX"
        tar -xf zeromq-4.0.4.tar.gz > $TEMPFILE 2>&1
        cd zeromq-4.0.4 2>>$TEMPFILE
        COUNT=60
        echo "XXX"
        echo $COUNT
        echo "configure, make and make install zeromq..."
        echo "XXX"
        echo '' >> $TEMPFILE
        ./configure -q 2>>$TEMPFILE >> $TEMPFILE 2>&1 && make -s >> $TEMPFILE 2>&1 && make -s install >> $TEMPFILE 2>&1
        COUNT=90
        echo "XXX"
        echo $COUNT
        echo "install pyzmq with zmq version 4.0.3..."
        echo "XXX"
        echo '' >> $TEMPFILE
        ldconfig >> $TEMPFILE 2>&1
        echo '' >> $TEMPFILE
        pip install -q pyzmq --install-option="--zmq=4.0.3" >> $TEMPFILE 2>&1
        COUNT=100
        echo "XXX"
        echo $COUNT
        echo "remove tmp files..."
        echo "XXX"
        cd $TMPDIR
        rm -rf $TMPDIR/*
        echo '' >> $TEMPFILE
        echo 'Done' >> $TEMPFILE
     ) | indicatorDialog "Install pyzmq with zmq v4.0.3 from source..." ""
    textDialog "Install pyzmq with zmq v4.0.3 from source..." "$TEMPFILE" && clear
}

function dpfs(){
    # GET SVN USER #
    svnPwd
    (
        COUNT=20
        echo "XXX"
        echo $COUNT
        echo "run apt-get install..."
        echo "XXX"
        apt-get install -y libexif-dev xvfb libxss1 > $TEMPFILE 2>&1
        COUNT=40
        echo "XXX"
        echo $COUNT
        echo "install google-chrome..."
        echo "XXX"
        if [[ $DEBIAN_VERSION_NUM -eq 8 ]]
        then
            wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
            echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
            apt-get update -qq
            apt-get install -y google-chrome-stable
        else
            su - $HCE_USER -c "cd ~/;
            expect -c \"
            spawn svn co svn+ssh://$SVN_USER@192.168.253.1/hce/download/trunk/chrome;
            expect {
                \"password\" {
                    send \"$SVN_PWD\n\"
                    exp_continue
                }
                \"password\" {
                    send \"$SVN_PWD\n\"
                    exp_continue
                }
            }
            \""
            dpkg -i /home/$HCE_USER/chrome/google-chrome-stable_current_amd64.deb
        fi
        apt-get install -y -f
        COUNT=70
        echo "XXX"
        echo $COUNT
        echo "run apt-get update..."
        echo "XXX"
        apt-get update -qq
        COUNT=99
        echo "XXX"
        echo $COUNT
        echo "install the python Selenium package and create link to chromedriver64"
        echo "XXX"
        pip install -q -U selenium
        pushd /home/$HCE_USER/hce-node-bundle/api/python/bin/ > /dev/null
        ln -s chromedriver64_chrome49 chromedriver64
        popd > /dev/null
        COUNT=100
        echo "XXX"
        echo $COUNT
        echo "Add to ~/.bashrc file"
        echo "XXX"
        echo "export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
DISPLAY=:1.0
export DISPLAY" >> /home/${HCE_USER}/.bashrc
        echo '' >> $TEMPFILE
        echo 'Done' >> $TEMPFILE
    ) | indicatorDialog "Dynamic pages fetcher support..." ""
    textDialog "Dynamic pages fetcher support..." "$TEMPFILE" && clear
    echo "ATTENTION!!! After end of work script
Run the Xvfb for the resolution 1024x768x16:
Xvfb :1 -screen 0 1024x768x16 &> /tmp/xvfb.log &
or this way for OpenVZ container:
Xvfb +extension RANDR :1 -screen 0 1024x768x16 &> /tmp/xvfb.log &

And apply the configuration for the current user (run from target user session):
source ~/.bashrc" > $TEMPFILE
    textDialog "Dynamic pages fetcher support..." "$TEMPFILE" && clear
}

function mvTestSite() {
    cp -r /home/${HCE_USER}/hce-node-bundle/api/python/data/ftests/test_site/* $WWW_DIR 2>$TEMPFILE
    chown -R $WWW_USER:$WWW_USER $WWW_DIR
    chmod oug+w $WWW_DIR
    usermod -a -G $WWW_USER $HCE_USER
    infoDialog "Set up test web site pages" "Test web site copied and file permissions set\n$(<$TEMPFILE)" 8 && clear
}

function mysqlSetup() {
    if [[ $(pgrep mysql) ]]
    then
        cd /home/${HCE_USER}/hce-node-bundle/api/python/manage
        ./mysql_create_user.sh 2 > $TEMPFILE
        sed -i '47d' /etc/mysql/my.cnf
        ./mysql_create_db.sh 2 >> $TEMPFILE
        textDialog "Install mysql-server..." "$TEMPFILE"
        infoDialog "Setup mysql (user, permissions, databases)" "Databases successfully created" && clear
    else
        textDialog "Install mysql-server..." "$TEMPFILE"
        infoDialog "Setup mysql (user, permissions, databases)" "Mysql server is not worked. User and databases not created" && clear
    fi
}


function checkZmqSo() {
    if [[ $(php -m | grep zmq) ]]
    then
        echo 'Y'
    else
        exit 1
    fi
}

function checkLocale() {
    if [[ $(locale -a 2>/dev/null | grep 'en_US.utf8') ]]
    then
        echo 'OK'
    fi
    exit 1
}

function force() {
    if [[ $(whoami) != root ]]
    then
        echo "Error" "Run script with root permissions or sudo: sudo $0 \"USERNAME\""
        exit 1
    fi
    if [[ ! -f '/etc/debian_version' ]]
    then
        echo "Error" "This script is only for the Debian system! Cancelled."
        exit 1
    fi
    if [[ ! -d /home/$HCE_USER ]]
    then
        echo "Error" "Home dir (/home/${HCE_USER}) for user ${HCE_USER} not exists! Cancelled."
        exit 1
    fi
    # CHECK DEBIAN VERSION #
    DEBIAN_VERSION_NUM=$(cat /etc/debian_version | awk -F\. '{print $1}')
    case $DEBIAN_VERSION_NUM in
        8)
            WWW_DIR='/var/www/html'
            PMA_DIR='/var/www/html/pma';;
        *)
            WWW_DIR='/var/www'
            PMA_DIR='/var/www/pma';;
    esac
    # LOCALES #
    echo -e '#\nLANG=en_US.UTF-8\n' >> /etc/default/locale
    sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
    locale-gen
    # DTSE_PHP #
    apt-get update -qq
    apt-get install -y --force-yes bsdutils unzip libzmq3-dev apache2 php5 php5-curl php5-gd php5-mcrypt php5-dev php-pear pkg-config libpgm-dev sphinxsearch
    php5enmod mcrypt
    printf "\n" | pecl install zmq-beta
    if [[ -z $(checkZmqSo) ]]
    then
        echo -e "; configuration for php ZMQ module \n; priority=20 \nextension=zmq.so" > /etc/php5/cli/conf.d/20-zmq.ini
    fi
    service apache2 reload
    # DTSE_DC #
    #apt-get update -qq
    apt-get install -y bc openjdk-7-jdk ruby g++
    # DTSE_PYTHON #
    #apt-get update -qq
    debconf-set-selections <<< "mysql-server mysql-server/root_password password ''"
    debconf-set-selections <<< "mysql-server mysql-server/root_password_again password ''"
    apt-get install -y mysql-server
    apt-get install -y libpgm-dev python-pip python-dev python-flask python-flaskext.wtf libffi-dev libxml2-dev libxslt1-dev mysql-client libmysqlclient-dev python-mysqldb libicu-dev libgmp3-dev libtidy-dev libjpeg-dev
    easy_install --upgrade pip
    pip install cement sqlalchemy Flask-SQLAlchemy scrapy gmpy mysql-python pyicu newspaper goose-extractor pytidylib uritools python-magic feedparser pillow beautifulsoup4 w3lib snowballstemmer soundex langdetect pycountry psutil==4.1.0 email validators dateutils
    pip install --no-cache-dir -I pillow
    case $DEBIAN_VERSION_NUM in
        8)
            pip install pyzmq
            ;;
        *)
            #pip install pyzmq --install-option="--zmq=bundled"
            # PYZMQ #
            cd $TMPDIR
            wget -q https://archive.org/download/zeromq_4.0.4/zeromq-4.0.4.tar.gz
            tar -xf zeromq-4.0.4.tar.gz
            cd zeromq-4.0.4
            ./configure -q && make -s && make -s install
            ldconfig
            pip install -q pyzmq --install-option="--zmq=4.0.3"
            cd $TMPDIR
            rm -rf $TMPDIR/*
            ;;
    esac
    pip install -U urlnorm
    # DYNAMIC PAGE SUPPORT #
    apt-get install -y libexif-dev xvfb libxss1
    pushd /home/$HCE_USER/hce-node-bundle/api/python/bin/ > /dev/null
    ln -s chromedriver64_chrome49 chromedriver64
    popd > /dev/null
    # MYSQL SETUP #
    set -f
    if [[ $(pgrep mysql) ]]
    then
        cd /home/${HCE_USER}/hce-node-bundle/api/python/manage
        ./mysql_create_user.sh 2 > $TEMPFILE
        sed -i '47d' /etc/mysql/my.cnf
        ./mysql_create_db.sh 2 >> $TEMPFILE
        echo "Setup mysql (user, permissions, databases)" "Databases successfully created"
    else
        echo "Setup mysql (user, permissions, databases)" "Mysql server is not worked. User and databases not created"
    fi
    exit 0
}

# END OF FUNCTIONS #

# START #

# CHECK HCE-DEVELOPMENTS CONTAINER #
if [[ -f $HCE_DEV_FILE ]]
then
    echo "It's a container for hce-developments, template created at  $(awk -F= '{print $2}' /etc/hce-dev), all dependencies installed"
fi

for ARG in $*
do
    case $ARG in
    'force'|'-force'|'--force')
        force
        exit 0;;
    'username='*|'-username='*|'--username='*)
        HCE_USER=$(echo $ARG | awk -F\= '{print $2}');;
    'help'|'-help'|'--help')
        echo "Usage $0 [username=user] [force] [help]"
        exit 0;;
    *)
        echo "Usage $0 [username=user] [force] [help]"
        exit 0;;
    esac
done

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

checkSudo
checkOs
checkHomeDir ${HCE_USER}
checkDebianVersion

MYSQL_SERVER=$(checkInstalledPackage "mysql-server")
if [[ $MYSQL_SERVER ]]
then
    MYSQL_CHECKBOX='off'
else
    MYSQL_CHECKBOX='on'
fi

case $DEBIAN_VERSION_NUM in
    8)
        WWW_DIR='/var/www/html'
        PMA_DIR='/var/www/html/pma'
        start "Select components";;
    *)
        WWW_DIR='/var/www'
        PMA_DIR='/var/www/pma'
        start7 "Select components";;
esac

case $DEBIAN_VERSION_NUM in
    8)
        for CHOISE in ${CHECK[@]}
        do
            case $CHOISE in
                0)
                    locales;;
                1)
                    mysql_server;;
                2)
                    dtse_php;;
                3)
                    dtse_dc;;
                4)
                    dtse_python;;
                5)
                    mvTestSite;;
                6)
                    mysqlSetup;;
                7)
                    dpfs;;
            esac
        done
        ;;
    *)
        for CHOISE in ${CHECK[@]}
        do
            case $CHOISE in
                '"0"')
                    locales;;
                '"1"')
                    mysql_server;;
                '"2"')
                    dtse_php;;
                '"3"')
                    dtse_dc;;
                '"4"')
                    dtse_python;;
                '"5"')
                    pyzmq;;
                '"6"')
                    mvTestSite;;
                '"7"')
                    mysqlSetup;;
                '"8"')
                    dpfs;;
            esac
        done
        ;;
esac

infoDialog "Finish" "All selected dependencies installed" && clear
