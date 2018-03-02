#!/bin/bash

DIALOG=${DIALOG=dialog}
BACKTITLE='Install Dependencies for dev HCE project components: hce-node, DTM and DC'
HCE_DEV_FILE='/etc/hce-dev'


RED='\e[0;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

HCE_USER=hce
MYSQL_USER=hce
MYSQL_PWD=hce12345
WWW_USER='www-data'

SCRIPT_NAME=$(basename $0)

TEMPFILE_DEV=`mktemp /tmp/$SCRIPT_NAME.XXXXX`
TMPDIR_DEV=`mktemp -d /tmp/$SCRIPT_NAME.XXXXXX`
trap "rm -f $TEMPFILE_DEV; rm -rf $TMPDIR_DEV" 0 1 2 5 15

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

function start_dev() {
    $DIALOG --backtitle "$BACKTITLE" --title "$1" \
            --checklist "Check install components" 20 80 3 \
                                                0 "HCE-project dependencies" on \
                                                1 "The phpmyadmin" on \
                                                2 "The phpliteadmin" on  2> $TEMPFILE_DEV
    case $? in
        0)
            CHECK_DEV=$(cat $TEMPFILE_DEV);;
        1)
            infoDialog "Select components" "Cancel. Exit" && clear && exit 1;;
        255)
            infoDialog "Select components" "Cancel. Exit" && clear && exit 1;;
    esac
}

function phpmyadmin() {
    (
        COUNT=10
        echo "XXX"
        echo $COUNT
        echo "run apt-get update and install php5-mysqlnd..."
        echo "XXX"
        apt-get update
        apt-get install -y php5-mysqlnd
        COUNT=30
        echo "XXX"
        echo $COUNT
        echo "download phpmyadmin latest..."
        echo "XXX"
        cd $TMPDIR_DEV
        wget -q https://files.phpmyadmin.net/phpMyAdmin/4.4.11/phpMyAdmin-4.4.11-english.zip -O $TMPDIR_DEV/phpmyadmin-latest.zip
        if [[ -z $(file $TMPDIR_DEV/phpmyadmin-latest.zip | grep empty) ]]
        then
            COUNT=60
            echo "XXX"
            echo $COUNT
            echo "unzip phpmyadmin..."
            echo "XXX"
            unzip -q phpmyadmin-latest.zip > $TEMPFILE_DEV
            rm -f phpmyadmin-latest.zip >> $TEMPFILE_DEV
            COUNT=90
            echo "XXX"
            echo $COUNT
            echo "install phpmyadmin..."
            echo "XXX"
            echo '' >> $TEMPFILE_DEV
            PHPMYADMINDIR=$(ls)
            if [[ -d $PMA_DIR ]]
            then
                rm -rf $PMA_DIR
            fi
            mkdir $PMA_DIR
            mv $TMPDIR_DEV/$PHPMYADMINDIR/* $PMA_DIR/ 2>>$TEMPFILE_DEV
            mv $TMPDIR_DEV/$PHPMYADMINDIR/.[!.]* $PMA_DIR/ 2>>$TEMPFILE_DEV
            cp $PMA_DIR/config.sample.inc.php $PMA_DIR/config.inc.php 2>>$TEMPFILE_DEV
            if [[ -z $(grep "LogiDEFookieValidity" $PMA_DIR/config.inc.php) ]]
            then
                sed -i "s/?>/\$cfg['LogiDEFookieValidity'] = '86400'\;\n?>/" $PMA_DIR/config.inc.php
            fi
            cd $TMPDIR_DEV
            chown -R $WWW_USER:$WWW_USER $PMA_DIR
        else
            echo "phpmyadmin was not downloaded and was not installed" > $TEMPFILE_DEV
        fi
        echo '' >> $TEMPFILE_DEV
        echo 'Done' >> $TEMPFILE_DEV
     ) | indicatorDialog "Install phpmyadmin..." ""
    textDialog "Install phpmyadmin..." "$TEMPFILE_DEV" && clear
}

function phpliteadmin(){
    (
        COUNT=30
        echo "XXX"
        echo $COUNT
        echo "download phpmyadmin latest..."
        echo "XXX"
        cd $TMPDIR_DEV
        wget -q https://bitbucket.org/phpliteadmin/public/downloads/phpLiteAdmin_v1-9-6.zip -O $TMPDIR_DEV/phpliteadmin-latest.zip
        if [[ -z $(file $TMPDIR_DEV/phpliteadmin-latest.zip | grep empty) ]]
        then
            COUNT=60
            echo "XXX"
            echo $COUNT
            echo "unzip phpmyadmin..."
            echo "XXX"
            unzip -q phpliteadmin-latest.zip phpliteadmin.php > $TEMPFILE_DEV
            rm -f phpliteadmin-latest.zip >> $TEMPFILE_DEV
            COUNT=90
            echo "XXX"
            echo $COUNT
            echo "install phpliteadmin..."
            echo "XXX"
            echo '' >> $TEMPFILE_DEV
            mv $TMPDIR_DEV/phpliteadmin.php $WWW_DIR/ 2>>$TEMPFILE_DEV
            if [[ $(grep "\$directory = '.';" $WWW_DIR/phpliteadmin.php) ]]
            then
                sed -i "s/\$directory = '.'\;/\$directory = '\/home\/${HCE_USER}\/hce-node-bundle\/api\/python\/data'\;/" $WWW_DIR/phpliteadmin.php
            fi
            if [[ $(grep "$subdirectories = false;" $WWW_DIR/phpliteadmin.php) ]]
            then
                sed -i "s/\$subdirectories = false\;/\$subdirectories = true\;/" $WWW_DIR/phpliteadmin.php
            fi
            chown $WWW_USER:$WWW_USER $WWW_DIR/phpliteadmin.php
        else
            echo "phpliteadmin was not downloaded and was not installed" > $TEMPFILE_DEV
        fi
        echo '' >> $TEMPFILE_DEV
        echo 'Done' >> $TEMPFILE_DEV
     ) | indicatorDialog "Install phpliteadmin..." ""
    textDialog "Install phpliteadmin..." "$TEMPFILE_DEV" && clear
}

function force() {
    source ./install_dependencies.sh force
    # PHPMYADMIN #
    apt-get install -y php5-mysqlnd
    cd $TMPDIR_DEV
    wget -q https://files.phpmyadmin.net/phpMyAdmin/4.4.11/phpMyAdmin-4.4.11-english.zip -O $TMPDIR_DEV/phpmyadmin-latest.zip
    if [[ -z $(file $TMPDIR_DEV/phpmyadmin-latest.zip | grep empty) ]]
    then
        unzip -q phpmyadmin-latest.zip
        rm -f phpmyadmin-latest.zip
        PHPMYADMINDIR=$(ls)
        if [[ -d $PMA_DIR ]]
        then
            rm -rf $PMA_DIR
        fi
        mkdir $PMA_DIR
        mv $TMPDIR_DEV/$PHPMYADMINDIR/* $PMA_DIR/
        mv $TMPDIR_DEV/$PHPMYADMINDIR/.[!.]* $PMA_DIR/
        cp $PMA_DIR/config.sample.inc.php $PMA_DIR/config.inc.php
        if [[ -z $(grep "LogiDEFookieValidity" $PMA_DIR/config.inc.php) ]]
        then
            sed -i "s/?>/\$cfg['LogiDEFookieValidity'] = '86400'\;\n?>/" $PMA_DIR/config.inc.php
        fi
        cd /$TMPDIR_DEV
        chown -R $WWW_USER:$WWW_USER $PMA_DIR
    else
        echo "phpmyadmin was not downloaded and was not installed"
    fi
    # PHPLITEADMIN #
    cd $TMPDIR_DEV
    wget -q https://bitbucket.org/phpliteadmin/public/downloads/phpLiteAdmin_v1-9-6.zip -O $TMPDIR_DEV/phpliteadmin-latest.zip
    if [[ -z $(file $TMPDIR_DEV/phpliteadmin-latest.zip | grep empty) ]]
    then
        unzip -q phpliteadmin-latest.zip phpliteadmin.php
        rm -f phpliteadmin-latest.zip
        mv $TMPDIR_DEV/phpliteadmin.php $WWW_DIR/
        if [[ $(grep "\$directory = '.';" $WWW_DIR/phpliteadmin.php) ]]
        then
            sed -i "s/\$directory = '.'\;/\$directory = '\/home\/${HCE_USER}\/hce-node-bundle\/api\/python\/data'\;/" $WWW_DIR/phpliteadmin.php
        fi
        if [[ $(grep "$subdirectories = false;" $WWW_DIR/phpliteadmin.php) ]]
        then
            sed -i "s/\$subdirectories = false\;/\$subdirectories = true\;/" $WWW_DIR/phpliteadmin.php
        fi
        chown $WWW_USER:$WWW_USER $WWW_DIR/phpliteadmin.php
    else
        echo "phpliteadmin was not downloaded and was not installed"
    fi
    echo "Done"
    exit 0
}

# END OF FUNCTIONS #

# START #

for ARG in $*
do
    case $ARG in
    'force'|'-force'|'--force')
        force
        exit 0;;
    'username='*|'-username='*|'--username='*)
        echo 'blah'
        USER_NAME="username=$(echo $ARG | awk -F\= '{print $2}')";;
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

case $DEBIAN_VERSION_NUM in
    8)
        WWW_DIR='/var/www/html'
        PMA_DIR='/var/www/html/pma'
        start_dev "Select components";;
    *)
        WWW_DIR='/var/www'
        PMA_DIR='/var/www/pma'
        start_dev "Select components";;
esac

for CHOISE_DEV in ${CHECK_DEV[@]}
do
    case $CHOISE_DEV in
        0)
            source ./install_dependencies.sh $USER_NAME;;
        '"0"')
            source ./install_dependencies.sh $USER_NAME;;
        1)
            phpmyadmin;;
        '"1"')
            phpmyadmin;;
        2)
            phpliteadmin;;
        '"2"')
            phpliteadmin;;
    esac
done

infoDialog "Finish" "All selected dependencies installed" && clear

exit 0
