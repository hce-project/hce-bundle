#! /bin/bash
#
# DTS prerequisite components
# availability test (check for PHP
# and Python modules/includes)
#

. ./cfg/screen_cfg.sh

. ./cfg/php.sh

. ./cfg/py.sh

# PHP includes list
inclist="zmsg.php"
for i in ${api_groups}; do
  inclist="${inclist} ${i}.inc.php"
done

# test include file presence on disk
echo "Checking for PHP includes... "
chk_php_includes ${inclist}

echo "Checking if PHP modules are available... "
chk_php_module "zmq"

# check for 'zmsg' class existence
echo "Checking if classes are available... "
chk_php_class_exist zmsg.php zmsg

# check for API groups (listed in ${api_groups})
echo "Checking if API functions are available... "
chk_php_api_groups ${api_groups}

echo "Checking Python modules that are installed (are in pip base)... "
for p in ${pypkgs}; do
  chk_py_module_installed "${p}"
done

echo "Checking Python modules that could be included... "
for m in ${pymodules}; do
  chk_py_module_inc "${m}"
done

echo -ne "All OK\n"
