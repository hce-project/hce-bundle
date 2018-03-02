#!/bin/bash

DIALOG=${DIALOG=dialog}
BACKTITLE='Uninstall Dependencies for HCE project components: hce-node, DTM and DC'
HCE_DEV_FILE='/etc/hce-dev'

RED='\e[0;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

HCE_USER=hce
MYSQL_USER=hce
MYSQL_PWD=hce12345

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

function msgDialog() {
    # $1 - title
    # $2 - info messages
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --infobox "$2" 20 80
}

function textDialog() {
    # $1 - title
    # $2 - info messages
    $DIALOG --backtitle "$BACKTITLE" --title "$1" --exit-label "OK"\
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

function checkHomeDir() {
    # $1 = hce user
    if [[ ! -d /home/$1 ]]
    then
        infoDialog "Error" "Home dir (/home/${HCE_USER}) for user ${HCE_USER} not exists! Cancelled."
        clear
        exit 1
    fi
}

function checkDir() {
    # $1 - check directory
    if [[ ! -d "$1" ]]
    then
        infoDialog "Error" "Directory $1 not exists! Cancelled."
        clear
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
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --checklist "Select uninstall components" 20 80 10 \
                                                0 "Uninstall the hce-node application package" on \
                                                1 "Remove databases and tables" on \
                                                2 "Remove bundle directory, all crawled data and all temporary files in the /tmp dir" on \
                                                3 "Remove PHP language API and management tools" off \
                                                4 "Remove DC service" off \
                                                5 "Remove Python language API and management tools" off \
                                                6 "Remove php and php-dev" off \
                                                7 "Remove apache2" off \
                                                8 "Remove mysql dependent packages" off \
                                                9 "Remove dynamic pages fetcher packages" off 2> $TEMPFILE
    case $? in
        0)
            CHECK=$(cat $TEMPFILE);;
        1)
            infoDialog "Select uninstall components" "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Select uninstall components" "Cancel. Exit" && clear && exit 1;;
    esac
}

function bundle_directory() {
    $DIALOG --backtitle "$BACKTITLE" --title "Locate bundel direcroty" \
            --inputbox "Input path to bundle directory" 20 80 "/home/${HCE_USER}/hce-node-bundle" 2> $TEMPFILE
    case $? in
        0)
            BUNDLE_DIRECTORY=$(cat $TEMPFILE);;
        1)
            infoDialog "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Cancel. Exit" && clear && exit 1;;
    esac
}

function hce_package() {
    cd $BUNDLE_DIRECTORY/api/python/manage
    ./dc-daemon_stop.sh >> $TEMPFILE 2>&1
    ./dtm-daemon_stop.sh >> $TEMPFILE 2>&1
    cd $BUNDLE_DIRECTORY/api/php/manage
    ./stop_r.sh >> $TEMPFILE 2>&1
    ./stop_nm.sh >> $TEMPFILE 2>&1
    rm -rf /tmp/hce-node/
    cd /
    apt-get -y remove hce-node >> $TEMPFILE 2>&1
}

function database_tables() {
    cd $BUNDLE_DIRECTORY >> $TEMPFILE 2>&1
    cd api/python/manage >> $TEMPFILE 2>&1
    printf "y" | ./mysql_remove_db.sh >> $TEMPFILE 2>&1
}

function dtse_php() {
    cd /
    msgDialog "Remove PHP language API and management tools" "removing, please wait"
    echo "Remove PHP language API and management tools:" >> $TEMPFILE 2>&1
    pecl uninstall zmq-beta >> $TEMPFILE 2>&1
    rm -rf /etc/php5/cli/conf.d/20-zmq.ini >> $TEMPFILE 2>&1
    apt-get -y remove unzip libzmq3-dev php-pear pkg-config libpgm-dev sphinxsearch >> $TEMPFILE 2>&1
    apt-get -y autoremove >> $TEMPFILE 2>&1
    service apache2 reload >> $TEMPFILE 2>&1
    clear
}

function dtse_dc(){
    cd /
    msgDialog "Remove DC service" "removing, please wait"
    echo "Remove DC service:" >> $TEMPFILE 2>&1
    apt-get -y remove bc openjdk-7-jdk ruby g++ >> $TEMPFILE 2>&1
    apt-get -y autoremove >> $TEMPFILE 2>&1
    clear
}

function dtse_python(){
    cd /
    msgDialog "Remove Python language API and management tools" "removing, please wait"
    echo "Remove Python language API and management tools:" >> $TEMPFILE 2>&1
    pip uninstall -y pyzmq cement sqlalchemy Flask-SQLAlchemy scrapy gmpy mysql-python pyicu newspaper goose-extractor pytidylib uritools python-magic feedparser Ghost.py pillow beautifulsoup4 snowballstemmer soundex pycountry langdetect w3lib urlnorm requests ndg.httpsclient pyasn1 OpenSSL email validators dateutils >> $TEMPFILE 2>&1
    apt-get -y remove libpgm-dev python-pip python-dev python-flask python-flaskext.wtf libffi-dev libxml2-dev libxslt1-dev mysql-client libmysqlclient-dev python-mysqldb libicu-dev libgmp3-dev libtidy-dev libjpeg-dev >> $TEMPFILE 2>&1
    apt-get -y autoremove >> $TEMPFILE 2>&1
    clear
}

function php_pkgs(){
    cd /
    msgDialog "Remove php" "removing, please wait"
    apt-get -y remove php5 php5-cli php5-common php5-dev php-pear >> $TEMPFILE 2>&1
    apt-get -y autoremove >> $TEMPFILE 2>&1
    clear
}

function apache_pkgs(){
    cd /
    msgDialog "Remove apache2" "removing, please wait"
    apt-get -y remove apache2 apache2.2-bin apache2.2-common apache2-doc apache2-mpm-prefork apache2-utils >> $TEMPFILE 2>&1
    apt-get -y autoremove >> $TEMPFILE 2>&1
    clear
}


function mysql_pkgs(){
    cd /
    msgDialog "Remove mysql-server" "removing, please wait"
    apt-get -y remove mysql-server mysql-common mysql-server-core-5.5 >> $TEMPFILE 2>&1
    apt-get -y autoremove >> $TEMPFILE 2>&1
    clear
}

function bundle_tmp(){
    cd /tmp/
    msgDialog "Remove bundle directory ($BUNDLE_DIRECTORY)" "removing, please wait"
    rm -rf $BUNDLE_DIRECTORY >> $TEMPFILE 2>&1
    rm -f dc-daemon* >> $TEMPFILE 2>&1
    rm -f dtm-daemon* >> $TEMPFILE 2>&1
    clear
}

function dpfs(){
    cd /
    apt-get -y remove libexif-dev xvfb libxss1 google-chrome-stable >> $TEMPFILE 2>&1
    pip uninstall -y selenium psutil >> $TEMPFILE 2>&1
}

# END OF FUNCTIONS #

# START #

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
bundle_directory
checkDir "$BUNDLE_DIRECTORY"

start "Select components"
echo > $TEMPFILE

for CHOISE in ${CHECK[@]}
    do
    case $(echo $CHOISE | sed 's/\"//g') in
        0)
            hce_package;;
        1)
            database_tables;;
        2)
            bundle_tmp;;
        3)
            dtse_php;;
        4)
            dtse_dc;;
        5)
            dtse_python;;
        6)
            php_pkgs;;
        7)
            apache_pkgs;;
        8)
            mysql_pkgs;;
        9)
            dpfs;;
    esac
done

textDialog "Uninstall log" "$TEMPFILE" && clear
infoDialog "Finish" "Done" && clear
