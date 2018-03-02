#!/bin/bash

OLD_DIR=`pwd`

mkdir /tmp/textstat; cd /tmp/textstat

wget https://pypi.python.org/packages/source/t/textstat/textstat-0.1.4.tar.gz#md5=18d26e6f1116784384158ec216157798

tar zxvf textstat-0.1.4.tar.gz; cd textstat-0.1.4

/usr/bin/python setup.py install

cd $OLD_DIR
rm -rf /tmp/textstat
