#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The crc32 collisions research tests.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ctypes
import zlib
import socket
import time
import uuid
import binascii

_connection_uid = 'AAA'
print socket.gethostname() + "-" + str(time.time()) + "-" + uuid.uuid1().hex + "-" + str(_connection_uid)

h = {}
t = time.time()
s1 = socket.gethostname() + "-"
s2 = "-" + uuid.uuid1().hex + "-" + str(_connection_uid)
i = 1
j = 0
maxItr = 10000000
while True :
  ts = str(t)
  #ts = s1 + str(t) + s2
  ts = str(ctypes.c_uint32(zlib.crc32(ts, int(time.time()))).value)
  #ts = str(ctypes.c_uint32(binascii.crc32(ts)).value)
  if ts in h:
    h[ts] += 1
    j += 1
    #print str(t) + "\n"
  else:
    h[ts] = 1
  t -= 1
  i += 1
  if t < 0 or i > maxItr:
    break

print "Finished: " + str(i) + " iterations, " + str(j) + " collisions, hash len: " + str(len(h))

