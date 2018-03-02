'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import Constants as CONSTANTS

##NodeManagerResponse class that represents admin modules response
class NodeManagerResponse(object):
  def __init__(self, errorCode=CONSTANTS.ERROR_NO, body=None):
    self.errorCode = errorCode
    self.body = body


  def getErrorCode(self):
    return self.errorCode


  def getBody(self):
    return self.body
