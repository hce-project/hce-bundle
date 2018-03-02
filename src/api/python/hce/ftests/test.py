#!/usr/bin/python
'''
HCE project, Python bindings, DC dependencies
The join tools research tests.

@package: drce
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ppath
from ppath import sys

from app.Utils import varDump


testStr = u'首相動静（２月７日）'

print varDump(testStr, stringifyType=0)