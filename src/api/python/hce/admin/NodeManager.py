'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from NodeManagerRequest import NodeManagerRequest
from NodeManagerResponse import NodeManagerResponse
from transport.UIDGenerator import UIDGenerator
import AdminExceptions
import Constants as CONSTANTS

##NodeManager represents API for interraction with user-side (execute method)
class NodeManager(object):
  def __init__(self, errorCode=CONSTANTS.ERROR_NO):
    self.request = NodeManagerRequest()
    self.errorCode = errorCode
    self.responses = []
    self.responsesDicts = []
    self.msgUidGenerator = UIDGenerator()


  def getErrorCode(self):
    return self.errorCode


  def getResponses(self):
    return self.responses


  def getResponsesDicts(self):
    return self.responsesDicts


##responsesParsing method parses data from self.responses into specific stucture (self.responsesDicts)
  def responsesParsing(self):
    for responseElement in self.responses:
      responsesDict = None
      responseBody = responseElement[CONSTANTS.STRING_RESPONSE_MARKER].getBody()
      if type(responseBody) == type(""):
        fieldsList = responseBody.split(CONSTANTS.ITEM_DELIM)
        if len(fieldsList) > 1:
          if fieldsList[0] != CONSTANTS.ERROR_CODE_OK and fieldsList[0] != CONSTANTS.ERROR_CODE_ERROR:
            self.responsesDicts.append(responsesDict)
            continue
          responsesDict = {CONSTANTS.RESPONSE_CODE_NAME: "", CONSTANTS.RESPONSE_FIELDS_NAME: {}}
          responsesDict[CONSTANTS.RESPONSE_CODE_NAME] = fieldsList[0]
          for i in xrange(1, len(fieldsList)):
            field = fieldsList[i].split(CONSTANTS.FIELD_DELIM)
            fieldValue = ""
            if len(field) > 1:
              fieldValue = field[1]
            if len(field) > 0:
              responsesDict[CONSTANTS.RESPONSE_FIELDS_NAME][field[0]] = fieldValue
      self.responsesDicts.append(responsesDict)


##execute method execute incoming commands on nodes, keepts reult in responses and responsesDicts fields
  def execute(self, commands, nodes):
    self.responses = []
    self.responsesDicts = []
    message = {CONSTANTS.STRING_MSGID_NAME : "", CONSTANTS.STRING_BODY_NAME : ""}
    for node in nodes:
      for command in commands:
        responseElement = {CONSTANTS.STRING_NODE_MARKER : node, CONSTANTS.STRING_RESPONSE_MARKER : None}
        requestBody = command.generateBody()
        if requestBody != None:
          message[CONSTANTS.STRING_MSGID_NAME] = self.msgUidGenerator.get_uid()
          message[CONSTANTS.STRING_BODY_NAME] = requestBody
          try:
            response = self.request.makeRequest(node, message, command.getRequestTimeout())
          except AdminExceptions.AdminWrongConnectionKey:
            errorStr = "ERR_AdminWrongConnectionKey"
            response = NodeManagerResponse(errorStr)
          except AdminExceptions.AdminTimeoutException:
            errorStr = "ERR_AdminTimeoutException"
            response = NodeManagerResponse(errorStr)
        responseElement[CONSTANTS.STRING_RESPONSE_MARKER] = response
        self.responses.append(responseElement)

    self.responsesParsing()
