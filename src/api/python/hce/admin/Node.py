'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import time
import Constants as CONSTANTS

#Node class contents data data for interraction (make connection) with transport layer
class Node(object):
  def __init__(self, host=CONSTANTS.HOST_DEFAULT, port=CONSTANTS.PORT_DEFAULT, timeout=CONSTANTS.NODE_TIMEOUT):
    self.host = host
    self.port = port
    self.timeout = timeout
    self.createTime = int(round(time.time() * 1000.0))


  def setHost(self, host):
    self.host = host


  def setPort(self, port):
    self.port = port


  def setTimeout(self, timeout):
    self.timeout = timeout


  def getHost(self):
    return self.host


  def getPort(self):
    return self.port


  def getTimeout(self):
    return self.timeout


  def getElapsedTime(self):
    return int(round(time.time() * 1000.0)) - self.createTime
