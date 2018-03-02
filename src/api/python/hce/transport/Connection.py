'''
Created on Feb 4, 2014

@author: igor, bgv
'''


import json

from collections import namedtuple
import zmq

import Consts as consts
from Response import Response
import logging
import app.Consts as APP_CONSTS
from app.Utils import varDump

# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


# #Class is used to inform about expiration of operation timeout
#
class ConnectionTimeout(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)


# #Exception which express some critical errors in the network engine
#
# At the moment critical errors are zmq.ZMQError, zmq.Again
class TransportInternalErr(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)


# #Structure which describes all data need to establish connection
#
# @todo - add a protocol param as independent part
ConnectionParams = namedtuple("ConnectionParams", "host port")


# #Main class of the transport layer.
#
# The class has two main methods - send, recv which are used to
# exchange messages
class Connection(object):
  '''
  Transport class
  '''

  RECV_DEFAULT_TIMEOUT = 5000

  # #constructor
  #
  # @param zmq_socket an instance of zmq.socket object
  # @param zmq_poller an instance of zmq.poller object
  # @param socket_type type of socket(seerver or client side)
  def __init__(self, zmq_socket, zmq_poller, socket_type=consts.CLIENT_CONNECT):
    self.zmq_socket = zmq_socket
    self.zmq_poller = zmq_poller
    self.socket_type = socket_type
    # @todo remove poller
    # self.zmq_poller.register(self.zmq_socket, zmq.POLLIN)



  # #send request
  #
  # @param request an instance of Request object
  # @param rid request id for logging only
  # @return None or throw TransportInternalErr
  def send(self, request, rid=-1):
    try:
      if self.socket_type == consts.CLIENT_CONNECT:
        snd_data = request.get_body()
      else:
        # snd_data = list(request.eventObj.get_body())
        # snd_data.insert(0, request.connect_identity)
        # return self.zmq_socket.send_multipart(snd_data)
        snd_data = [request.connect_identity] + request.eventObj.get_body()

      try:
        if request.route is not None:
          request.route = json.loads(request.route)
          request.route['task_type'] = request.task_type
          request.route = json.dumps(request.route)
          snd_data.append(request.route)
        else:
          if request.task_type > 0:
            snd_data.append(json.dumps({'task_type':request.task_type}))

      except Exception as err:
        logger.debug("Error add task_type in to the route data: %s", str(err))

      logger.debug("send_multipart() socket_type: " + str(self.socket_type) + ", id:" + str(rid) + \
                   " snd_data: " + varDump(snd_data))
      r = self.zmq_socket.send_multipart(snd_data)
      logger.debug("Data sent with the zmq_socket.send_multipart()")
      return r
    except zmq.ZMQError as err:  # pylint: disable-msg=E1101
      logger.error("ZMQ error: " + str(err))
      raise TransportInternalErr(str(err))
    except Exception as err:
      raise TransportInternalErr('General error: ' + str(err))



  # #recieve data from connection
  #
  # @param timeout timeout in msec, default RECV_DEFAULT_TIMEOUT msec
  # @param rid request id for logging only
  # @return Response or throw ConnectionTimeout, TransportInternalErr
  def recv(self, timeout=RECV_DEFAULT_TIMEOUT, rid=-1):
    try:
      events = self.zmq_socket.poll(int(timeout), zmq.POLLIN)  # pylint: disable=E0602,E1101
      if  events == zmq.POLLIN:  # pylint: disable-msg=E1101
        if self.socket_type == consts.CLIENT_CONNECT:
          return Response(self.zmq_socket.recv_multipart())
        else:
          data = self.zmq_socket.recv_multipart()
          identity = data[:1]
          return Response(data[1:], identity[0])
      else:
        raise ConnectionTimeout('Connection.recv() timeout: ' + str(timeout) + ', request id: ' + str(rid))
    except (zmq.ZMQError, zmq.Again) as err:  # pylint: disable-msg=E1101
      logger.error("ZMQ error: " + str(err))
      raise TransportInternalErr(str(err))
    except Exception as err:
      logger.error("General error: " + str(err))
      raise TransportInternalErr(str(err))
    # finally:
#      self.zmq_poller.unregister(self.zmq_socket)


  # close zqm.socket
  #
  # @return None
  def close(self):
    # self.zmq_poller.unregister(self.zmq_socket) #is right place??
    self.zmq_socket.close()


  # #check status of zqm.socket
  #
  # @return bool
  def is_closed(self):
    return self.zmq_socket.closed


  # Destroys the object, close connection
  #
  # @return None
def __del__(self):
  try:
    self.close()
  except Exception:
    pass

