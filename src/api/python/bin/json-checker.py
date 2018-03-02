#!/usr/bin/python


'''
Created on Apr 2, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ppath
from ppath import sys

from jchecker.JsonChecker import JsonChecker

jsonChecker = JsonChecker()


try:
  jsonChecker.setup()
  jsonChecker.run()
finally:
  jsonChecker.close()
