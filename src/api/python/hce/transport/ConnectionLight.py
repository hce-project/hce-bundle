'''
Created on Feb 28, 2014

@author: igor, bgv
'''

# import pickle
try:
  import cPickle as pickle
except ImportError:
  import pickle

import logging
import zmq
from transport.Connection import TransportInternalErr
import transport.Consts as consts
import app.Consts as APP_CONSTS
from app.Utils import varDump


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)

# #Wrapper class on zmq.Socket that operate python objects
#
class ConnectionLight(object):

  POLL_DEFAULT_TIMEOUT = 5000

  def __init__(self, zmq_socket, socket_type, addr="", connected=True):
    '''
    Constructor
    '''
    self.zmq_socket = zmq_socket
    self.socket_type = socket_type
    self.connected = connected
    self.addr = addr

  # #send python object
  #
  # @param obj python object
  # @return None or throw TransportInternalErr
  def send(self, event_obj):
    try:
      logger.debug("event_obj: %s", varDump(event_obj))
      self.connect()
      if self.socket_type == consts.CLIENT_CONNECT:
        self.zmq_socket.send_pyobj(event_obj)
      else:
        pickle_event = pickle.dumps(event_obj)
        self.zmq_socket.send_multipart([event_obj.connect_identity, pickle_event])
    except zmq.ZMQError as err:  # pylint: disable-msg=E1101
      raise TransportInternalErr(err.message)
    except Exception, err:
      logger.error("Error `%s`", str(err))


  # #recieve python object from connection
  #
  # @return python object(event) or throw TransportInternalErr
  def recv(self):
    try:
      self.connect()
      if self.socket_type == consts.CLIENT_CONNECT:
        pyObj = self.zmq_socket.recv_pyobj()
        logger.debug("pyObj: %s", varDump(pyObj))
        return pyObj
      else:
        identity, pickle_event = self.zmq_socket.recv_multipart()
        event = pickle.loads(pickle_event)
        event.connect_identity = identity
        logger.debug("event: %s", varDump(event))
        return event
    except zmq.ZMQError, err:  # pylint: disable-msg=E1101
      raise TransportInternalErr(err)
    except Exception, err:
      logger.error("Error `%s`", str(err))


  # #poll the socket for events
  #
  # @param timeout the timeout (in milliseconds) to wait for an event
  # @param flags the event flags to poll for
  # @return The events that are ready and waiting.
  # Will be 0 if no events were ready by the time timeout was reached
  def poll(self, timeout=POLL_DEFAULT_TIMEOUT, flags=zmq.POLLIN):  # pylint: disable-msg=E1101
    self.connect()
    return self.zmq_socket.poll(int(timeout), flags)


  # close zqm.socket
  #
  # @return None
  def close(self):
    self.connect()
    self.zmq_socket.close()
    self.connected = False


  # #Really connect to listen socket with addr
  #
  #
  def connect(self):
    if self.connected is False:
      self.zmq_socket.connect(self.addr)
      self.connected = True
