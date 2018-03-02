'''
Created on Feb 21, 2014

@author: scorp
'''
##unit-tests of NodeManager class 

import unittest
from mock import MagicMock
from Node import Node
from NodeManager import NodeManager
from Command import Command
import Constants as CONSTANTS
from NodeManagerRequest import NodeManagerRequest

from test_admin_Constants import bodyString
from test_admin_Constants import requestString 
from test_admin_Constants import testResponseString1 
from test_admin_Constants import testResponseString2 
from test_admin_Constants import testResponseString3 
from test_admin_Constants import testResponseString4 
 

def generateBodyMock():
  return None


def generateBodyMock2():
  return bodyString


def makeRequestMock(node, requestBody):
  return requestString


class testNodeManager(unittest.TestCase):


  def setUp(self):
    self.nodeManager = NodeManager() 


  def tearDown(self):
    pass


  def testNodeManagerConstructor(self):
    self.assertTrue(self.nodeManager.getErrorCode() == CONSTANTS.ERROR_NO, ">>> wrong Error code")
    self.assertTrue(len(self.nodeManager.getResponses()) == 0, ">>> response list not empty")


  def testResponsesParsing(self):
    responses = []
    responses.append({CONSTANTS.STRING_NODE_MARKER : None, CONSTANTS.STRING_RESPONSE_MARKER : None})
    responses.append({CONSTANTS.STRING_NODE_MARKER : None, CONSTANTS.STRING_RESPONSE_MARKER : testResponseString1})
    responses.append({CONSTANTS.STRING_NODE_MARKER : None, CONSTANTS.STRING_RESPONSE_MARKER : testResponseString2})
    responses.append({CONSTANTS.STRING_NODE_MARKER : None, CONSTANTS.STRING_RESPONSE_MARKER : testResponseString3})
    responses.append({CONSTANTS.STRING_NODE_MARKER : None, CONSTANTS.STRING_RESPONSE_MARKER : testResponseString4})
    self.nodeManager.responses = responses
    self.nodeManager.responsesParsing()
    responsesDicts = self.nodeManager.getResponsesDicts()
    self.assertTrue(len(responsesDicts) == len(responses), ">>> Wrong responsesDicts Len")
    self.assertTrue(responsesDicts[0] == None, ">>> responsesDicts[0] not None")
    self.assertTrue(responsesDicts[1] == None, ">>> responsesDicts[1] not None")
    self.assertTrue(responsesDicts[2] == None, ">>> responsesDicts[2] not None")
    self.assertTrue(responsesDicts[3][CONSTANTS.RESPONSE_CODE_NAME] == CONSTANTS.ERROR_CODE_ERROR,
                    ">>> responsesDicts[3][CONSTANTS.RESPONSE_CODE_NAME] is wrong")
    self.assertTrue(len(responsesDicts[3][CONSTANTS.RESPONSE_FIELDS_NAME]) == 1,
                    ">>> responsesDicts[3][CONSTANTS.RESPONSE_FIELDS_NAME] bad len")        
    self.assertTrue(responsesDicts[4][CONSTANTS.RESPONSE_CODE_NAME] == CONSTANTS.ERROR_CODE_OK,
                    ">>> responsesDicts[4][CONSTANTS.RESPONSE_CODE_NAME] is wrong")
    self.assertTrue(len(responsesDicts[4][CONSTANTS.RESPONSE_FIELDS_NAME]) == 2,
                    ">>> responsesDicts[4][CONSTANTS.RESPONSE_FIELDS_NAME] bad len")   
    self.assertTrue(responsesDicts[4][CONSTANTS.RESPONSE_FIELDS_NAME]["param1"] == "val1",
                    ">>> responsesDicts[4][CONSTANTS.RESPONSE_FIELDS_NAME][\"param1\"] bad value")
    self.assertTrue(responsesDicts[4][CONSTANTS.RESPONSE_FIELDS_NAME]["param2"] == "val2",
                    ">>> responsesDicts[4][CONSTANTS.RESPONSE_FIELDS_NAME][\"param2\"] bad value")                    
        
        
  def testExecute1(self):
    nodes = []
    commandMock = MagicMock(spec=Command)
    requestMock = MagicMock(spce=NodeManagerRequest)
    self.nodeManager.request = requestMock
    self.nodeManager.execute(commandMock, nodes)
    self.assertTrue(commandMock.generateBody.called == False, ">>> commandMock.generateBody was call")
    self.assertTrue(requestMock.makeRequest.called == False, ">>> requestMock.makeRequest was call")           
    responses = self.nodeManager.getResponses()
    self.assertTrue(len(responses) == 0, ">>> responses list not empty")           


  def testExecute2(self):
    nodes = []
    nodes.append(Node())
    nodes.append(Node())
    nodes.append(Node())
    commandMock = MagicMock(spec=Command)
    commandMock.generateBody.side_effect = generateBodyMock
    commandList = [commandMock]
    requestMock = MagicMock(spce=NodeManagerRequest)
    self.nodeManager.request = requestMock
    self.nodeManager.execute(commandList, nodes)
    self.assertTrue(commandMock.generateBody.called, ">>> commandMock.generateBody wasn't call")
    self.assertTrue(requestMock.makeRequest.called == False, ">>> requestMock.makeRequest was call")
    responses = self.nodeManager.getResponses()
    self.assertTrue(len(responses) == 3, ">>> size of responses list not 3")
    self.assertTrue(responses[0][CONSTANTS.STRING_RESPONSE_MARKER] == None, "1 response not None")
    self.assertTrue(responses[1][CONSTANTS.STRING_RESPONSE_MARKER] == None, "2 response not None")
    self.assertTrue(responses[2][CONSTANTS.STRING_RESPONSE_MARKER] == None, "3 response not None")
        
        
  def testExecute3(self):
    nodes = []
    nodes.append(Node())
    nodes.append(Node())
    nodes.append(Node())
    commandMock = MagicMock(spec=Command)
    commandMock.generateBody.side_effect = generateBodyMock2
    commandList = [commandMock]        
    requestMock = MagicMock(spce=NodeManagerRequest)
    requestMock.makeRequest.side_effect = makeRequestMock
    self.nodeManager.request = requestMock
    self.nodeManager.execute(commandList, nodes)  
    self.assertTrue(commandMock.generateBody.called, ">>> commandMock.generateBody wasn't call")
    self.assertTrue(requestMock.makeRequest.called, ">>> requestMock.makeRequest was not call")
    self.assertTrue(requestMock.makeRequest.call_count == 3, ">>> requestMock.makeRequest wrong call count")
    responses = self.nodeManager.getResponses()
    self.assertTrue(len(responses) == 3, ">>> size of responses list not 3")
    self.assertTrue(responses[0][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "1 response wrong value")
    self.assertTrue(responses[1][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "2 response wrong value")
    self.assertTrue(responses[2][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "3 response wrong value")
        
        
  def testExecute4(self):
    nodes = []
    nodes.append(Node())
    nodes.append(Node())
    nodes.append(Node())
    commandMock = MagicMock(spec=Command)
    commandMock.generateBody.side_effect = generateBodyMock2
    commandMock1 = MagicMock(spec=Command)
    commandMock1.generateBody.side_effect = generateBodyMock2        
    commandList = [commandMock, commandMock1]
    requestMock = MagicMock(spce=NodeManagerRequest)
    requestMock.makeRequest.side_effect = makeRequestMock
    self.nodeManager.request = requestMock
    self.nodeManager.execute(commandList, nodes)  
    self.assertTrue(commandMock.generateBody.called, ">>> commandMock.generateBody wasn't call")
    self.assertTrue(commandMock.generateBody.call_count == 3, ">>> commandMock.generateBody wrong call count")        
    self.assertTrue(commandMock1.generateBody.called, ">>> commandMock1.generateBody wasn't call")
    self.assertTrue(commandMock.generateBody.call_count == 3, ">>> commandMock1.generateBody wrong call count")
    self.assertTrue(requestMock.makeRequest.called, ">>> requestMock.makeRequest was not call")
    self.assertTrue(requestMock.makeRequest.call_count == 6, ">>> requestMock.makeRequest wrong call count")
    responses = self.nodeManager.getResponses()
    self.assertTrue(len(responses) == 6, ">>> size of responses list not 3")
    self.assertTrue(responses[0][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "0 response wrong value")
    self.assertTrue(responses[1][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "1 response wrong value")
    self.assertTrue(responses[2][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "2 response wrong value")
    self.assertTrue(responses[3][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "3 response wrong value")
    self.assertTrue(responses[4][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "4 response wrong value")
    self.assertTrue(responses[5][CONSTANTS.STRING_RESPONSE_MARKER] == requestString, "5 response wrong value")
        
        
if __name__ == "__main__":
# import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
