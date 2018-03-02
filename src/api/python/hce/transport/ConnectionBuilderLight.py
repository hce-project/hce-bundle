'''
Created on Feb 28, 2014

@author: igor, bgv
'''


import logging
import zmq
from ConnectionLight import ConnectionLight
from Singelon import Singleton
import Consts as consts
import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from app.Utils import ExceptionLog


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


##Class hides routines of bulding connection objects
#
class ConnectionBuilderLight(object):
  __metaclass__ = Singleton

  def __init__(self):
    '''
    Constructor
    '''
    try:
      self.zmq_context = zmq.Context()  # pylint: disable=E1101
      #for Poller object
      self.zmq_poller = zmq.Poller()  # pylint: disable=E1101
    except Exception as err:
      ExceptionLog.handler(logger, err, 'Error:')
    except:
      ExceptionLog.handler(logger, None, 'Unknown error:')


  ##build a connection
  #
  #@param connect_type  type of connection(CLIENT_CONNECT, SERVER_CONNECT)
  #@param connect_params an instance of  ConnectionParams
  #@return Connection
  def build(self, connect_type, connect_endpoint, protocol_type=consts.INPROC_TYPE, real_connect=True):
    try:
      sock = None
      if protocol_type == consts.TCP_TYPE:
        protocol = "tcp://"
      else:
        protocol = "inproc://"
      addr = protocol + connect_endpoint
      if connect_type == consts.CLIENT_CONNECT:
        sock = self.zmq_context.socket(zmq.DEALER)  # pylint: disable=E1101
        if real_connect:
          sock.connect(addr)
      if connect_type == consts.SERVER_CONNECT:
        sock = self.zmq_context.socket(zmq.ROUTER)  # pylint: disable=E1101
        sock.bind(addr)
      return ConnectionLight(sock, connect_type, addr, real_connect)
    except Exception as err:
       ExceptionLog.handler(logger, err, 'Error:')
    except:
      ExceptionLog.handler(logger, None, 'Unknown error:')

