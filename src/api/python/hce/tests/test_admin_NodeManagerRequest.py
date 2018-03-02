'''
Created on Feb 17, 2014

@author: scorp
'''
##unit-tests of NodeManagerRequest class 

import unittest
import Constants as CONSTANTS
import AdminExceptions
from NodeManagerRequest import NodeManagerRequest
from transport.Connection import ConnectionTimeout
from transport.IDGenerator import IDGenerator
from transport.Response import Response
from transport.Connection import Connection
from mock import MagicMock
from transport.ConnectionBuilder import ConnectionBuilder
from Node import Node
from time import sleep


def recvMockFunc(timeout):
  raise ConnectionTimeout(">>> recv timeout")


def sendMockFunc(request):
  sleep(2)


class TestNodeManagerRequest(unittest.TestCase):


  def setUp(self):
    self.nodeManagerRequest = NodeManagerRequest()


  def tearDown(self):
    pass


  def testNodeManagerRequestConstructor(self):
    self.assertTrue(self.nodeManagerRequest.connectionBuilder != None,
                    ">>> connectionBuilder field is None, after default consturctor")
    iDGenerator = IDGenerator()
    self.nodeManagerRequest = NodeManagerRequest(connectionIdGenerator=iDGenerator)
    self.assertTrue(self.nodeManagerRequest.connectionBuilder != None,
                    ">>> connectionBuilder field is None, after consturctor with IDGenerator")
        
        
  def testCreateNodeManagerResponse(self):
    testData = [123, "Body String"]
    response = Response(testData)
    message = {CONSTANTS.STRING_MSGID_NAME : 123, CONSTANTS.STRING_BODY_NAME : "Body String"}
    nodeManagerResponse = self.nodeManagerRequest.createNodeManagerResponse(response, message)
    self.assertEqual(nodeManagerResponse.getErrorCode(), CONSTANTS.ERROR_NO,
                     ">>> [1] id request and id response not equal")
        
    message = {CONSTANTS.STRING_MSGID_NAME : 124, CONSTANTS.STRING_BODY_NAME : "Body String"}
    nodeManagerResponse = self.nodeManagerRequest.createNodeManagerResponse(response, message)
    self.assertEqual(nodeManagerResponse.getErrorCode(), CONSTANTS.ERROR_BAD_MSG_ID,
                     ">>> [2] id request and id response are equal")
        
        
  def testRaiseAdminExceptions(self):
    exceptionString = None
    self.nodeManagerRequest.raiseAdminExceptions(exceptionString)
    exceptionString = CONSTANTS.STRING_EXCEPTION_WRONG_CONNECTION_KEY
    with self.assertRaises(AdminExceptions.AdminWrongConnectionKey):
      list(self.nodeManagerRequest.raiseAdminExceptions(exceptionString))
            
    exceptionString = CONSTANTS.STRING_EXCEPTION_ADMIN_TIMEOUT
    with self.assertRaises(AdminExceptions.AdminTimeoutException):
      list(self.nodeManagerRequest.raiseAdminExceptions(exceptionString))

    exceptionString = "---> Some String <---"
    with self.assertRaises(AdminExceptions.AdminTimeoutException):
      list(self.nodeManagerRequest.raiseAdminExceptions(exceptionString))
        
            
  def testMakeRequest1(self):
    mock = MagicMock(spec=ConnectionBuilder)
    mock.build.side_effect = KeyError("Wrong Key")
    self.nodeManagerRequest.connectionBuilder = mock
    localNode = Node()
    testMsg = {CONSTANTS.STRING_MSGID_NAME : 123, CONSTANTS.STRING_BODY_NAME : "Body String"}
    with self.assertRaises(AdminExceptions.AdminWrongConnectionKey):
      list(self.nodeManagerRequest.makeRequest(localNode, testMsg))
            
            
  def testMakeRequest2(self):
    mock = MagicMock(spec=ConnectionBuilder)
    self.nodeManagerRequest.connectionBuilder = mock
    localNode = Node()
    testMsg = {CONSTANTS.STRING_MSGID_NAME : 123, CONSTANTS.STRING_BODY_NAME : "Body String"}
    connectionMock = MagicMock(spec=Connection)
    mock_cfg = {"build.return_value":connectionMock}
    mock.configure_mock(**mock_cfg)
    self.nodeManagerRequest.connectionBuilder = mock
    self.nodeManagerRequest.makeRequest(localNode, testMsg)
    self.assertTrue(connectionMock.send.called, ">>> transport.Connection.send not call")
    self.assertTrue(connectionMock.recv.called, ">>> transport.Connection.recv not call")
    self.assertTrue(connectionMock.close.called, ">>> transport.Connection.close not call")        
        
        
  def testMakeRequest3(self): 
    mock = MagicMock(spec=ConnectionBuilder)
    localNode = Node()
    testMsg = {CONSTANTS.STRING_MSGID_NAME : 123, CONSTANTS.STRING_BODY_NAME : "Body String"}
    connectionMock = MagicMock(spec=Connection)
    mock_cfg = {"build.return_value":connectionMock}
    mock.configure_mock(**mock_cfg)      
    connectionMock.recv.side_effect = recvMockFunc
    createNodeManagerResponseMock = MagicMock()
    self.nodeManagerRequest.connectionBuilder = mock
    self.nodeManagerRequest.createNodeManagerResponse = createNodeManagerResponseMock
    with self.assertRaises(AdminExceptions.AdminTimeoutException):
      list(self.nodeManagerRequest.makeRequest(localNode, testMsg))
    self.assertTrue(createNodeManagerResponseMock.called == False,
                    ">>> transport.Connection.close not call")
        
        
  def testMakeRequest4(self):
    mock = MagicMock(spec=ConnectionBuilder)
    self.nodeManagerRequest.connectionBuilder = mock
    localNode = Node()
    testMsg = {CONSTANTS.STRING_MSGID_NAME : 123, CONSTANTS.STRING_BODY_NAME : "Body String"}      
    connectionMock = MagicMock(spec=Connection)
    connectionMock.send.side_effect = sendMockFunc
    mock_cfg = {"build.return_value":connectionMock}
    mock.configure_mock(**mock_cfg)
    self.nodeManagerRequest.connectionBuilder = mock
    with self.assertRaises(AdminExceptions.AdminTimeoutException):
      list(self.nodeManagerRequest.makeRequest(localNode, testMsg))
    self.assertTrue(connectionMock.send.called, ">>> transport.Connection.send wasn't call")
    self.assertTrue(connectionMock.recv.called == False, ">>> transport.Connection.recv was call")
    self.assertTrue(connectionMock.close.called, ">>> transport.Connection.close wasn't call")   
        

if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
