#!/bin/bash

#Actions that will be performed after all tests finished

#Stop DC
echo "Stop DC" >> ../log/$0.log 2>&1
cd ../manage && ./dc-daemon_stop.sh >> ../log/$0.log 2>&1 && cd ../ftests
sleep 1
cd ../manage && ./dc-daemon_status.sh >> ../log/$0.log 2>&1 && cd ../ftests

#Stop DTMD
echo "Stop DTM" >> ../log/$0.log 2>&1
cd ../manage && ./dtm-daemon_stop.sh >> ../log/$0.log 2>&1 && cd ../ftests
sleep 1
cd ../manage && ./dtm-daemon_status.sh >> ../log/$0.log 2>&1 && cd ../ftests
