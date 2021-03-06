'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

#Admin module's constants
PORT_DEFAULT = 5546
HOST_DEFAULT = "tcp://localhost"
NODE_TIMEOUT = 1000

ERROR_NO = 0
ERROR_BAD_MSG_ID = 1

ADMIN_CONNECT_TYPE = 0
DATA_CONNECT_TYPE = 1

STRING_MSGID_NAME = "msgId"
STRING_BODY_NAME = "body"

STRING_EXCEPTION_ADMIN_TIMEOUT = "Admin module timeout"
STRING_EXCEPTION_WRONG_CONNECTION_KEY = "Wrong Connection key"

STRING_NODE_MARKER = "node"
STRING_RESPONSE_MARKER = "response"

COMMAND_DELIM = '\t'
PARAM_DELIM = '@'
ITEM_DELIM = '\t'
FIELD_DELIM = '='

ERROR_CODE_OK = "OK"
ERROR_CODE_ERROR = "ERROR"
RESPONSE_CODE_NAME = "response_code"
RESPONSE_FIELDS_NAME = "fields"

#Admin handler types
class ADMIN_HANDLER_TYPES(object):

  DATA_CLIENT_PROXY = "DataClientProxy"
  DATA_CLIENT_DATA = "DataClientData"
  DATA_PROCESSOR_DATA = "DataProcessorData"
  ADMIN = "Admin"
  DATA_REDUCE_PROXY = "DataReducerProxy"
  DATA_SERVER_PROXY = "DataServerProxy"
  ROUTER_SERVER_PROXY = "RouterServerProxy"


  def __init__(self):
    pass


#Admin commands names
class COMMAND_NAMES(object):
  DRCE = "DRCE"
  SPHINX = "SPHINX"
  ECHO = "ECHO"
  REBUILD_SERVER_CONNECTION = "REBUILD_SERVER_CONNECTION"
  REBUILD_SERVER_CONNECTION = "REBUILD_SERVER_CONNECTION"
  DISCONNECT_SERVER_CONNECTION = "DISCONNECT_SERVER_CONNECTION"
  REBUILD_CLIENT_CONNECTION = "REBUILD_CLIENT_CONNECTION"
  DISCONNECT_CLIENT_CONNECTION = "DISCONNECT_CLIENT_CONNECTION"
  UPDATE_SCHEMA = "UPDATE_SCHEMA"
  REBUILD_CLIENT_CONNECTION = "REBUILD_CLIENT_CONNECTION"
  SHUTDOWN = "SHUTDOWN"
  LLGET = "LLGET"
  LLSET = "LLSET"
  MMGET = "MMGET"
  MMSET = "MMSET"
  TIME = "TIME"
  PROPERTIES = "PROPERTIES"
  DRCE_SET_HOST = "DRCE_SET_HOST"
  DRCE_GET_HOST = "DRCE_GET_HOST"
  DRCE_SET_PORT = "DRCE_SET_PORT"
  DRCE_GET_PORT = "DRCE_GET_PORT"


  def __init__(self):
    pass
