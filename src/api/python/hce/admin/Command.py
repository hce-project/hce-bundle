'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from Constants import ADMIN_HANDLER_TYPES as ADMIN_HANDLERS
import Constants as CONSTANTS


##Command class contents "commad" data and processing methods
class Command(object):
  def __init__(self, commandName=None, params=None, adminHandler=ADMIN_HANDLERS.ADMIN, requestTimeout=None):
    self.commandName = commandName
    if params == None:
      params = []
    self.params = params
    self.adminHandler = adminHandler
    self.requestTimeout = requestTimeout


  def setCommandName(self, commandName):
    self.commandName = commandName


  def setParams(self, params):
    self.params = params


  def setAdminHandler(self, adminHandler):
    self.adminHandler = adminHandler


  def setRequestTimeout(self, requestTimeout):
    self.requestTimeout = requestTimeout


  def getCommandName(self):
    return self.commandName


  def getParams(self):
    return self.params


  def getAdminHandler(self):
    return self.adminHandler


  def getRequestTimeout(self):
    return self.requestTimeout


##Main processing method, generate request body string, based on internal field - "param"
  def generateBody(self):
    resultStr = ""
    if self.commandName != None:
      resultStr += self.adminHandler
      resultStr += CONSTANTS.COMMAND_DELIM
      resultStr += self.commandName
      resultStr += CONSTANTS.COMMAND_DELIM
      for param in self.params:
        if type(param) == type(0):
          param = str(param)
        resultStr += param
        resultStr += CONSTANTS.PARAM_DELIM
      if resultStr[-1] == CONSTANTS.PARAM_DELIM:
        resultStr = resultStr[:-1]
        resultStr += CONSTANTS.COMMAND_DELIM
    return resultStr

