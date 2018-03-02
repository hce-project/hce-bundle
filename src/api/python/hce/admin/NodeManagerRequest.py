'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from NodeManagerResponse import NodeManagerResponse
from transport.Connection import ConnectionTimeout
from transport.Connection import ConnectionParams
from transport.ConnectionBuilder import ConnectionBuilder
from transport.IDGenerator import IDGenerator
from transport.Request import Request
import Constants as CONSTANTS
import AdminExceptions
import transport.Consts


##NodeManagerRequest class contents all data needed for admin level's request sending
class NodeManagerRequest(object):
  def __init__(self, errorCode=CONSTANTS.ERROR_NO, connectionBuilder=None, connectionIdGenerator=None):
    self.errorCode = errorCode
    if connectionBuilder == None:
      if connectionIdGenerator == None:
        connectionIdGenerator = IDGenerator()
      self.connectionBuilder = ConnectionBuilder(connectionIdGenerator)
    else:
      self.connectionBuilder = connectionBuilder


  def getErrorCode(self):
    return self.errorCode


  def createNodeManagerResponse(self, response, message):
    errorCode = CONSTANTS.ERROR_NO
    if response.get_uid() != message[CONSTANTS.STRING_MSGID_NAME]:
      errorCode = CONSTANTS.ERROR_BAD_MSG_ID
    return NodeManagerResponse(errorCode, response.get_body())


##raiseAdminExceptions method generates exceptions based on analyze of exceptionString param's data
  def raiseAdminExceptions(self, exceptionString):
    if exceptionString != None:
      if exceptionString == CONSTANTS.STRING_EXCEPTION_WRONG_CONNECTION_KEY:
        raise AdminExceptions.AdminWrongConnectionKey(exceptionString)
      else:
        raise AdminExceptions.AdminTimeoutException(exceptionString)


##makeRequest main class method, it gets node and message params, interact with transport layer,
# makes NodeManagerResponse object, based on transport layer's return data, returns it.
  def makeRequest(self, node, message, commandTimeout=None):
    exceptionString = None
    respond = None
    adminConnection = None
    connectParams = ConnectionParams(node.getHost(), node.getPort())
    try:
      adminConnection = self.connectionBuilder.build(transport.Consts.ADMIN_CONNECT_TYPE, connectParams)
    except KeyError as exp:
      exceptionString = CONSTANTS.STRING_EXCEPTION_WRONG_CONNECTION_KEY

    if adminConnection != None:
      request = Request(message[CONSTANTS.STRING_MSGID_NAME])
      request.add_data(message[CONSTANTS.STRING_BODY_NAME])
      adminConnection.send(request)

      localTimeout = -1
      if commandTimeout == None:
        elapsedTime = node.getElapsedTime()
        if elapsedTime >= node.getTimeout():
          exceptionString = CONSTANTS.STRING_EXCEPTION_ADMIN_TIMEOUT
        else:
          localTimeout = node.getTimeout() - elapsedTime
      else:
        localTimeout = commandTimeout

      if localTimeout >= 0:
        try:
          respond = adminConnection.recv(localTimeout)
        except ConnectionTimeout as exp:
          exceptionString = exp.message
      adminConnection.close()
    self.raiseAdminExceptions(exceptionString)
    return self.createNodeManagerResponse(respond, message)
