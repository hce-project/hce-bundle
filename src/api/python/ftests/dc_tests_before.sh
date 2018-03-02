#!/bin/bash

#Actions that will be performed before tests will be started

cd ../manage

#Stop DC
echo -e "\n#-#\nStop DC" >> ../log/$0.log 2>&1
./dc-daemon_stop.sh >> ../log/$0.log 2>&1

# Check status of DC #
CHECK=$(./dc-daemon_status.sh | grep 'Service running')
if [[ $CHECK ]]
then
    echo "DC service not stopped. Canseled"
    echo -e "\n#-FATAL:DC_stop-#" >> ../log/$0.log
    exit 1
fi

#Stop DTMD
echo -e "\n#-#Stop DTM" >> ../log/$0.log 2>&1
./dtm-daemon_stop.sh >> ../log/$0.log 2>&1

# Check status of DTMD #
CHECK=$(./dtm-daemon_status.sh | grep 'Service running')
if [[ $CHECK ]]
then
    echo "DTM service not stopped. Canseled"
    echo -e "\n#-#FATAL:DTM_stop-#" >> ../log/$0.log
    exit 1
fi

# Check running mysql-server #
if [[ -z $(pgrep mysql) ]]
then
    echo "MYSQL server not worked. Canseled"
    echo -e "\n#-#FATAL:MYSQL-#" >> ../log/$0.log
    exit 1
fi

cd ../ftests

# Cleanup all
./dc_tests_cleanup.sh >> ../log/$0.log 2>&1

cd ../manage
# Remove databases #
echo -e "\n#-#\nRemove SQL DB schema" >> ../log/$0.log 2>&1
printf "Y" | ./mysql_remove_db.sh >> ../log/$0.log 2>&1

# Create new schema structure
echo -e "\n#-#\nCreate SQL DB schema" >> ../log/$0.log 2>&1
./mysql_create_db.sh >> ../log/$0.log 2>&1

# Check mysql schema #
if [[ $(mysql -u hce -phce12345  -e "use dc_urls" 2>/dev/null && echo "TRUE" || echo "FALSE") == "FALSE" ]]
then
    echo "Not connect to database \"use dc_urls\". Canseled"
    echo -e "\n#-#FATAL:use dc_urls-#" >> ../log/$0.log
    exit 1
fi
if [[ $(mysql -u hce -phce12345  -e "use dc_sites" 2>/dev/null && echo "TRUE" || echo "FALSE") == "FALSE" ]]
then
    echo "Not connect to database \"use dc_sites\". Canseled"
    echo -e "\n#-#FATAL:use dc_sites-#" >> ../log/$0.log
    exit 1
fi
echo -e "\n#-#\nCreate SQL DB schema for deleted resources" >> ../log/$0.log 2>&1
./mysql_create_urls_deleted.sh hce hce12345 >> ../log/$0.log 2>&1

#Start DTMD
echo -e "\n#-#\nStart DTM" >> ../log/$0.log 2>&1
./dtm-daemon_start.sh >> ../log/$0.log 2>&1

# Check status of DTMD #
CHECK=$(./dtm-daemon_status.sh | grep stopped)
if [[ $CHECK ]]
then
    echo "DTM service not started. Canseled"
    echo -e "\n#-#FATAL:DTM_start-#" >> ../log/$0.log
    exit 1
fi

sleep 10

#Start DC
echo -e "\n#-#\nStart DC" >> ../log/$0.log 2>&1
./dc-daemon_start.sh >> ../log/$0.log 2>&1

# Check status of DC #
CHECK=$(./dc-daemon_status.sh | grep stopped)
if [[ $CHECK ]]
then
    echo "DC service not started. Canseled"
    echo -e "#-#FATAL:DC_start-#" >> ../log/$0.log
    exit 1
fi

sleep 5

cd ../ftests