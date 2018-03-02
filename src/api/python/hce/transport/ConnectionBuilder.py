'''
Created on Feb 4, 2014

@author: igor
'''


import zmq
from Connection import Connection
import Consts as consts
import logging
import app.Consts as APP_CONSTS


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


##The builder is used to encapsulation routine of creation
#various type of connections
class ConnectionBuilder(object):
  '''
  Factory is used to create various connection objects
  '''

  ##constructor
  #
  #Init global variable
  #@param id_generator an instance of IDGenerator object
  def __init__(self, id_generator):
    '''
    Init global variable
    '''
    self.zmq_context = zmq.Context()  # pylint: disable=E1101
    self.zmq_poller = zmq.Poller()  # pylint: disable-msg=E1101
    self.id_generator = id_generator
    self.builders = dict({consts.ADMIN_CONNECT_TYPE : self.__admin_connection,
                     consts.DATA_CONNECT_TYPE : self.__data_connection})


  ##build a connection
  #
  #@param connect_type  type of connection(DATA_CONNECT_TYPE
  #or ADMIN_CONNECT_TYPE)
  #@param connect_params an instance of  ConnectionParams
  #@param endpointType type of endpoint (client or server)
  #@return Connection
  def build(self, connect_type, connect_params, endPointType=consts.CLIENT_CONNECT):
    sock = self.builders[connect_type](connect_params, endPointType)
    return Connection(sock, self.zmq_poller, endPointType)


  ##helper function
  #
  #is used for create admin connection type
  #@param connect_params an instance of  ConnectionParams
  #@param endpointType type of endpoint (client or server)
  #return zmq.Socket
  def __admin_connection(self, connect_params, endPointType):
    sock = self.__data_connection(connect_params, endPointType)
    #@todo need set extra params
    return sock


  ##helper function
  #
  #is used for create data connection type
  #@param connect_params an instance of  ConnectionParams
  #@param endpointType type of endpoint (client or server)
  #return zmq.Socket
  def __data_connection(self, connect_params, endPointType):
    sock = None
    addr = "tcp://" + connect_params.host + ":" + str(connect_params.port)
    if endPointType == consts.CLIENT_CONNECT:
      sock = self.zmq_context.socket(zmq.DEALER)  # pylint: disable=E0602,E1101
      sock.setsockopt(zmq.IDENTITY, self.id_generator.get_connection_uid())  # pylint: disable=E0602,E1101
      sock.connect(addr)

    if endPointType == consts.SERVER_CONNECT:
      sock = self.zmq_context.socket(zmq.ROUTER)  # pylint: disable=E0602,E1101
      sock.bind(addr)

    return sock
