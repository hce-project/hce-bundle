#!/bin/bash
echo -e "\nCreating mysql user and grant permitions\n"

source mysql_create_cfg

exit_status=0
# read mysql superuser password from Debian specific configuration file
if [ -f /etc/mysql/debian.cnf ]; then
	ROOT_USER="debian-sys-maint"
	ROOT_PASS=$(cat /etc/mysql/debian.cnf |grep password|uniq|awk '{ print ($3)}')
fi

# ask mysql superuser login and password, if we didn't set it.
if [ -z "$ROOT_USER" ] || [ -z "$ROOT_PASS" ]; then
	read -p "MySQL superuser login: " ROOT_USER
	read -s -p "MySQL superuser password: " ROOT_PASS
fi

# create application user
mysql --user=${ROOT_USER} --password=${ROOT_PASS} -e "GRANT ALL PRIVILEGES ON *.* TO '$APP_USER'@'localhost' IDENTIFIED BY '$APP_PASS';"
exit_status=$(( ${exit_status} + $? ))

mysql --user=${ROOT_USER} --password=${ROOT_PASS} -e "GRANT ALL PRIVILEGES ON *.* TO '$APP_USER'@'%' IDENTIFIED BY '$APP_PASS';"
exit_status=$(( ${exit_status} + $? ))

if [ 0 -eq ${exit_status} ]; then
	echo "Success"
else
	echo "Error"
fi
