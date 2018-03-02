#!/bin/bash


RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

APACHE_DIR='/etc/apache2'
VHOSTS_PATH=$APACHE_DIR'/sites-available'
PORTS_CONF=$APACHE_DIR'/ports.conf'
DOMAIN='hce.loc'
PORT=80
DOC_ROOT='/var/www/hce'
AUTH=0
LOGIN='hce'
PASSWORD='hce'
APACHE_USER=$(ps -ef | egrep 'apache|httpd' | grep -v $(whoami) | grep -v root | head -n1 | awk '{print $1}')
HTPASSWD_FILE='/etc/apache2/hce.htpasswd'

# FUNCTIONS #
function checkSudo() {
    if [[ $(whoami) != root ]]
    then
        echo -e $RED"Error. Run script with root permissions or sudo: sudo $0 \"USERNAME\""$DEF
        exit 1
    fi
}

function createVhost(){
    echo "
<VirtualHost *:$PORT>
        ServerAdmin postmaster@$DOMAIN
        ServerName $DOMAIN
        DocumentRoot $DOC_ROOT/
        AddDefaultCharset UTF-8
        <Directory $DOC_ROOT/>
                DirectoryIndex index.php index.html
                AllowOverride All
                <IfVersion < 2.4>
		            Allow from all
		            Order deny,allow
                </IfVersion>
                <IfVersion >= 2.4>
                      Require all granted
                </IfVersion>
                Options Indexes FollowSymLinks
        </Directory>
        ErrorLog /var/log/apache2/$DOMAIN.error.log
        CustomLog /var/log/apache2/$DOMAIN.access.log combined
</VirtualHost>" > "$VHOSTS_PATH/$DOMAIN.conf"
}

function createVhostAuth(){
    echo "
<VirtualHost *:$PORT>
        ServerAdmin postmaster@$DOMAIN
        ServerName $DOMAIN
        DocumentRoot $DOC_ROOT/
        AddDefaultCharset UTF-8
        <Directory $DOC_ROOT/>
                DirectoryIndex index.php index.html
                AllowOverride All
                <IfVersion < 2.4>
		            Allow from all
		            Order deny,allow
                </IfVersion>
                <IfVersion >= 2.4>
                      Require all granted
                </IfVersion>
                Options Indexes FollowSymLinks
                AuthUserFile $HTPASSWD_FILE
                AuthName 'Log in to access'
                AuthType Basic
                Require valid-user
        </Directory>
        ErrorLog /var/log/apache2/$DOMAIN.error.log
        CustomLog /var/log/apache2/$DOMAIN.access.log combined
</VirtualHost>" > "$VHOSTS_PATH/$DOMAIN.conf"
}
# END OF FUNCTIONS #

checkSudo

while getopts ":d:p:r:al:P:h" OPT
do
    case $OPT in
        d) DOMAIN=$OPTARG;;
        p) PORT=$OPTARG;;
        r) DOC_ROOT=$OPTARG;;
        a) AUTH=1;;
        l) LOGIN=$OPTARG;;
        P) PASSWORD=$OPTARG;;
        h|*) echo -e "Usage: $0 arguments. List of existing arguments:\n -d [domain name, default $DOMAIN]\n -p [port, default $PORT]\n -r [document root for site, default $DOC_ROOT]\n -a (enable http autorization)\n -l [login for http authorization (if enabled), default $LOGIN]\n -P [password dor http authorization (if enabled), default $PASSWORD]\n -h this help"
            exit 1;;
    esac
done

# CREATE VIRTUAL HOST #
if [[ $AUTH -eq 1 ]]
then
    a2enmod auth_basic > /dev/null
    createVhostAuth
    htpasswd -bc $HTPASSWD_FILE $LOGIN $PASSWORD
else
    createVhost
fi
# CHECK PORTS #
if [[ $PORT -ne 80 ]]
then
    NAME_VHOST=$(grep NameVirtualHost $PORTS_CONF | grep $PORT | awk -F\: '{print $2}' | grep ^$PORT$)
    LISTEN_VHOST=$(grep Listen $PORTS_CONF | grep $PORT | awk '{print $2}' | grep ^$PORT$)
    if [[ -z $NAME_VHOST ]]
    then
        echo "#_HCE_NAME_VIRTUALHOST_:$PORT:_#" >> $PORTS_CONF
        echo "NameVirtualHost *:$PORT" >> $PORTS_CONF
    fi
    if [[ -z $LISTEN_VHOST ]]
    then
        echo "#_HCE_LISTEN_:$PORT:_#" >> $PORTS_CONF
        echo "Listen $PORT" >> $PORTS_CONF
    fi
fi

chown -R $APACHE_USER:$APACHE_USER $DOC_ROOT > /dev/null
# ENABLE VHOST #
a2ensite $DOMAIN.conf > /dev/null
service apache2 reload > /dev/null

echo -e $BLUE"Done"$DEF
