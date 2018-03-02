#!/bin/bash

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

APACHE_DIR='/etc/apache2'
VHOSTS_PATH=$APACHE_DIR'/sites-available'
PORTS_CONF=$APACHE_DIR'/ports.conf'
PORT=80
APACHE_USER=$(ps -ef | egrep 'apache|httpd' | grep -v $(whoami) | grep -v root | head -n1 | awk '{print $1}')

# FUNCTIONS #
function checkSudo() {
    if [[ $(whoami) != root ]]
    then
        echo -e $RED"Error. Run script with root permissions or sudo: sudo $0 \"USERNAME\""$DEF
        exit 1
    fi
}
# END OF FUNCTIONS #

checkSudo

while getopts ":d:p:h" OPT
do
    case $OPT in
        d) DOMAIN=$OPTARG;;
        p) PORT=$OPTARG;;
        h|*) echo -e "Usage: $0 arguments. List of existing arguments:\n -d domain_name\n -p [port, default $PORT]\n -h this help"
            exit 1;;
    esac
done

if [[ -z $DOMAIN ]]
then
    echo -e $RED"Need domain$DEF\n Usage: $0 arguments. List of existing arguments:\n -d domain_name\n -p [port, default $PORT]\n -h this help"
    exit 1
fi

# CHECK VIRTHOST AND GET CONFIG FILE #
VHOST_STR=$(apachectl -S | grep $DOMAIN | grep $PORT)
if [[ -z $(echo $VHOST_STR | awk '{print $2}' | grep ^$PORT$) ]]
then
    echo -e $TUR"Virtual host $DOMAIN on port $PORT not exist. Exit"$DEF
    exit 1
fi
VHOST_CONFIG=$(echo $VHOST_STR | awk '{print $5}' | awk -F\: '{print $1}' | sed 's/(//')

# FIND AND REMOVE (IF EXIST) NameVirtualhost AND Listen IN ports.conf #
NAME_VHOST_STR=$(cat $PORTS_CONF | grep -n "#_HCE_NAME_VIRTUALHOST_:$PORT:_#" | awk -F\: '{print $1}')
if [[ $NAME_VHOST_STR ]]
then
    sed -i "$NAME_VHOST_STR,$(($NAME_VHOST_STR+1))d" $PORTS_CONF
fi
LISTEN_VHOST_STR=$(cat $PORTS_CONF | grep -n "#_HCE_LISTEN_:$PORT:_#" | awk -F\: '{print $1}')
if [[ $LISTEN_VHOST_STR ]]
then
    sed -i "$LISTEN_VHOST_STR,$(($LISTEN_VHOST_STR+1))d" $PORTS_CONF
fi

# GET DOC_ROOT AND AUTH_FILE #
DOC_ROOT=$(cat $VHOST_CONFIG | awk '/DocumentRoot/ {print $2}')
AUTH_FILE=$(cat $VHOST_CONFIG | awk '/AuthUserFile/ {print $2}')

# DISABLE VHOST AND RELOAD APACHE #
a2dissite $DOMAIN.conf > /dev/null
service apache2 reload > /dev/null

# REMOVE AUTH_FILE IF EXIST #
if [[ $AUTH_FILE && -f $AUTH_FILE ]]
then
    rm -f $AUTH_FILE
fi

# REMOVE DOCUMENT ROOT #
if [[ -d $DOC_ROOT ]]
then
    rm -rf $DOC_ROOT
fi

# REMOVE VIRTUAL_HOST CONFIG FILE #
if [[ -f $(echo $VHOST_CONFIG | sed 's/enabled/available/') ]]
then
    rm -f $(echo $VHOST_CONFIG | sed 's/enabled/available/')
fi

echo -e $BLUE"Done"$DEF
