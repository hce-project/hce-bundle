'''
Created on Feb 25, 2014

@author: igor
'''


import zmq
from Connection import Connection


##It's a wrapper for building server side endpoint
#
class ServerConnectionBuilder(object):
  '''
  classdocs
  '''

  ##constructor
  #init global variable
  #
  def __init__(self):
    self.zmq_context = zmq.Context()  # pylint: disable-msg=E1101
    self.zmq_poller = zmq.Poller()  # pylint: disable-msg=E1101


  ##build a server side connection
  #may raise  zmq.ZMQBindError
  #
  #@param connect_params an instance of  ConnectionParams
  #@param socket_type type of zmq socket(zmq.REP, ..)
  #@return Connection
  def build(self, connect_params, socket_type=zmq.REP):  # pylint: disable-msg=E1101,E0602
    sock = self.zmq_context.socket(socket_type)
    sock.bind(connect_params.host + ":" + str(connect_params.port))
    return Connection(sock, self.zmq_poller)
