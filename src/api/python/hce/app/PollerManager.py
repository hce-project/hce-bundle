'''
Created on Feb 26, 2014

@author: igor, bgv
'''

import zmq

from transport.Connection import ConnectionTimeout
import app.Utils as Utils  # pylint: disable=F0401


# Logger initialization
logger = Utils.MPLogger().getLogger()


# #Class wraps all routine operation of working with zmq.Poller object
#
class PollerManager(object):


  def __init__(self, poller=None):
    if poller is None:
      self.zmq_poller = zmq.Poller()  # pylint: disable=E1101
    else:
      self.zmq_poller = poller
    self.connections = dict()

  def add(self, connection, name):
    if hasattr(connection, "zmq_socket"):
      self.zmq_poller.register(connection.zmq_socket, zmq.POLLIN)  # pylint: disable=E1101
      self.connections[connection.zmq_socket] = name


  def remove(self, connection):
    if hasattr(connection, "zmq_socket"):
      self.zmq_poller.unregister(connection.zmq_socket)
      del self.connections[connection.zmq_socket]


  # #poll the zmq_poller
  #
  # @return if timeout - raise ConnectionTimeout or
  # return list of ready connections(names)
  def poll(self, timeout):
    socks = dict(self.zmq_poller.poll(timeout))
    if len(socks) == 0:
      raise ConnectionTimeout("PollerManager")
    ready_connection_names = list()
    for sock in socks:
      ready_connection_names.append(self.connections[sock])
    return ready_connection_names
