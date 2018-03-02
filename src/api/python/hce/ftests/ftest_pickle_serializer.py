#coding: utf-8
'''
HCE project, Python bindings, DRCE module
Event objects functional tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import json
from app.Utils import PickleSerializer


s = u"test チューリップで描 Japan test«Facebook»test"
print "original: " + s

p = PickleSerializer().serialize(s)
print "pickled: " + p

j = json.dumps(p)
print "jsoned: " + j

p = json.loads(j)
print "pickled: " + p

s = PickleSerializer().unserialize(p)
print "restored: " + s

