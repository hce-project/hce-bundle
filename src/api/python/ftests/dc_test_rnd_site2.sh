#!/bin/bash
#
#

echo ""
read -p "WARNING! This test completely removes all data from DC's DB, delete logs and all service's data! Enter 'yes' to continue?"
if [ "$REPLY" != "yes" ]; then
   echo "Test cancelled!"
   echo ""
   exit
fi

red='\e[0;31m'
nc='\e[0m'

JSON_PATH="../data/ftests"
INI="../ini/dc-client.ini"

#Remove log files
rm -f ../log/*
echo "" > ../log/$0.log 2>&1

say() {
  # write message in red
  echo -ne "${red}$*" >>/dev/stderr
  echo -ne "${nc}"    >>/dev/stderr
}

show_content() {
  # show base64-encoded page content
  cd ../bin && ./json-field.py -f "itemsList:0:itemObject:0:processedContents:0:buffer" -b 1 >../log/${file}.value 2>&1
}

do_test() {
  # intended result code
  #result="${1}"
  #shift

  # test description
  #desc="${1}"
  #shift

  expected=`echo $* | awk -F, '{gsub(/ +/, "", $1); print $1}'`
  cmd=`echo $* | awk -F, '{gsub(/ +/, "", $2); print $2}'`
  f=`echo $* | awk -F, '{gsub(/ +/, "", $3); print $3}'`
  desc=`echo $* | awk -F, '{p = index($0, $4); print substr($0, p)}'`

  if [ "`echo "$*" | awk '/^[^0-9]/{print 1}'`" = "1" ]; then
    # the line begins from a non-numeric char
    # this means that it is external command
    $* >> ../log/$0.log 2>&1
    return
  fi

  #cmd=`echo  ${1} | awk '{print $1}' | awk -F= '{print $2}'`
  #file=`echo ${1} | awk '{print $2}' | awk -F= '{print $2}' | awk -F/ '{print $4}'`

  # execute the test and get the output json
  json=`../bin/dc-client.py --config=${INI} --command=${cmd} --file=${JSON_PATH}/${f} 2>&1 | tee -a ../log/$0.log`

  # get error code
  rc=`cd ../bin && echo ${json} | ./json-field.py -f "itemsList:0:errorCode"`

  # current response json
  echo ${json} > ../log/${f}.result

  if [ "${desc}" != "" ]; then
    say "${desc}, "
    say "${cmd}, ${f}: "
  fi

  if [ "${rc}" = "${expected}" ];  then
      echo "success" >>/dev/stderr
  else
      #error_code=`cd ../bin && echo ${json} | ./json-field.py -f "itemsList:0:error_code"`
      #error_status=`cd ../bin && echo ${json} | ./json-field.py -f "itemsList:0:error_status"`
      #echo ${error_code}, ${error_status}
      #if [  ]; then
        #
      #fi
      # error message
      errmsg=`cd ../bin && echo ${json} | ./json-field.py -f "itemsList:0:errorMessage"`
      echo "fail, error code: \"${errmsg}\"" >>/dev/stderr
      echo "${json}"
  fi
}

# Restarting the previous running DTM/DC services
if [ `ps ax | grep -i 'dtm-daemon' | grep -v grep | wc -l` -ge 1 -o \
     `ps ax | grep -i 'dc-daemon'  | grep -v grep | wc -l` -ge 1 ]; then
  echo "DTM/DC daemons running. Shutting them down..."
  ./dc_tests_after.sh
  # clearing databases
  ./clear_for_crawler_test.sh hce hce12345
  rm -f  ../data/dc_dbdata/*
  rm -rf ../data/dc_rdata/*
fi

sleep 2

#Before actions
./dc_tests_before.sh

sleep 2

while read line; do
  # delete empty lines
  if [ "${line}" = "" ]; then
     continue
  fi

  # get 1st line character
  char=`echo ${line} | head -c1`

  # delete comments
  if [ "${char}" = "#" ]; then
    continue
  fi

  # start test
  do_test ${line}
done<<EOF
# Intended command status; command; parameters JSON; test description
# Delete sites
0, SITE_DELETE, dcc_site_delete_timeout.json, "Site delete with timeout"
0, SITE_DELETE, dcc_site_delete_ok.json, "Site delete with success"
0, SITE_DELETE, dcc_site_delete_rnd.json, "Site delete with random site generator"

# Create new site(s)
0, SITE_NEW, dcc_site_new_timeout.json, "Site create with timeout"
0, SITE_NEW, dcc_site_new_ok.json, "Site create with success"
0, SITE_NEW, dcc_site_new_ok_rnd.json, "Site create - success w/random site generator"
0, SITE_NEW, dcc_site_new_rnd.json, "Site create with random site generator"

# Check site status before crawling
0, SITE_STATUS, dcc_site_status_timeout.json, "Check site status with timeout"
0, SITE_STATUS, dcc_site_status_ok.json, "Check site status with success"
0, SITE_STATUS, dcc_site_status_rnd.json, "Check site status with random site generator"

# Set new URLs ### timeout, ok
0, URL_NEW, dcc_url_new_timeout.json, "New URL with timeout"
0, URL_NEW, dcc_url_new_ok.json, "New URL with success"
0, URL_NEW, dcc_url_new_rnd.json, "New URL with random site generator"

# Check URLs status before crawling
0, URL_STATUS, dcc_url_status_rnd.json, "Check URL status with random site generator"

# Delete sites
0, SITE_DELETE, dcc_site_delete_timeout.json, "Site delete with timeout"
0, SITE_DELETE, dcc_site_delete_ok.json, "Site delete with success"
0, SITE_DELETE, dcc_site_delete_rnd.json, "Site delete with random site generator"

# Create new site(s)
0, SITE_NEW, dcc_site_new_timeout.json, "Site create with timeout"
0, SITE_NEW, dcc_site_new_ok.json, "Site create with success"
0, SITE_NEW, dcc_site_new_ok_rnd.json, "Site create with random site generator/success"
0, SITE_NEW, dcc_site_new_rnd.json, "Site create with random site generator"

# Check site status before crawling
0, SITE_STATUS, dcc_site_status_timeout.json, "Check site status with timeout"
0, SITE_STATUS, dcc_site_status_ok.json, "Check site status with success"
0, SITE_STATUS, dcc_site_status_rnd.json, "Check site status with random site generator"

# Set new URLs
0, URL_NEW, dcc_url_new_timeout.json, "New URL with timeout"
0, URL_NEW, dcc_url_new_ok.json, "New URL with success"
0, URL_NEW, dcc_url_new_rnd.json, "New URL with random site generator"

# Check URLs status before crawling
0, URL_STATUS, dcc_url_status_rnd.json, "Check URL status with random site generator"

# Get data of URLs
0, URL_CONTENT, dcc_url_content_timeout.json, "Get URLs content with timeout"
0, URL_CONTENT, dcc_url_content_ok.json, "Get URLs content with success"
0, URL_CONTENT, dcc_url_content_rnd.json, "Get URLs content with random site generator"

# Check sites status after crawling
0, SITE_STATUS, dcc_site_status_timeout.json, "Get site status with timeout"
0, SITE_STATUS, dcc_site_status_ok.json, "Get site status with success"
0, SITE_STATUS, dcc_site_status_rnd.json, "Get site status with random site generator"

# Check URLs status after crawling
0, URL_STATUS, dcc_url_status_rnd.json, "Get URL status with random site generator"

# Cleanup sites data ###
0, SITE_CLEANUP, dcc_site_cleanup_timeout.json, "Cleanup sites data with timeout"
0, SITE_CLEANUP, dcc_site_cleanup_ok.json, "Cleanup sites data with success"
0, SITE_CLEANUP, dcc_site_cleanup_rnd.json, "Cleanup sites data, with randomizer"

# Update sites ###
0, SITE_UPDATE, dcc_site_update_timeout.json, "Update site with timeout"
0, SITE_UPDATE, dcc_site_update_ok.json, "Update site with success"
0, SITE_UPDATE, dcc_site_update_rnd.json, "Update site with randomizer"

# Check sites status after update ###
0, SITE_STATUS, dcc_site_status_timeout.json, "Check site status with timeout"
0, SITE_STATUS, dcc_site_status_ok.json, "Check site status with success"
0, SITE_STATUS, dcc_site_status_rnd.json, "Check site status with randomizer"

# Update URLs ###
0, URL_UPDATE, dcc_url_update_rnd.json, "Update URLs with randomizer"

###
echo "Crawling started 2 at:"
date

# Let site crawl after update with RESTART ###
sleep 60

###
echo "Crawling finished 2 at:"
date

# Check sites status after crawling ###
0, SITE_STATUS, dcc_site_status_timeout.json, "Check sites status with timeout"
0, SITE_STATUS, dcc_site_status_ok.json, "Check sites status with success"
0, SITE_STATUS, dcc_site_status_rnd.json, "Check sites status with randomizer"

# Delete sites ###
0, SITE_DELETE, dcc_site_delete_timeout.json, "Delete sites with timeout"
0, SITE_DELETE, dcc_site_delete_ok.json, "Delete sites with success"
0, SITE_DELETE, dcc_site_delete_rnd.json, "Delete sites with randomizer"

# Check sites status after delete ###
0, SITE_STATUS, dcc_site_status_timeout.json, "Checking sites status with timeout"
0, SITE_STATUS, dcc_site_status_ok.json,  "Checking sites status with success"
0, SITE_STATUS, dcc_site_status_rnd.json, "Checking sites status with randomizer"

# URLs content before delete
2, URL_CONTENT, dcc_url_content_rnd.json, "URLs content with randomizer"
# Delete URLs and resources crawled
0, URL_DELETE, dcc_url_delete_rnd.json, "Delete URLs and resources crawled"
# URLs content after delete
2, URL_CONTENT, dcc_url_content_rnd.json, "URLs content after delete with randomizer"

echo "Crawling started 1 at:"
date

#Let the site(s) to be crawled
sleep 360

echo "Crawling finished 1 at:"
date

# URLs content store for viewer
2, URL_CONTENT, dcc_url_content_rnd.json, "URLs content to screen"

echo ../log/${file}.result | show_content

# Test fetch content automation script
cd ../ftests && ./dc-kvdb-resource.sh 699fcf4591fc23e79b839d8819904293 699fcf4591fc23e79b839d8819904293
EOF

# After actions
./dc_tests_after.sh
