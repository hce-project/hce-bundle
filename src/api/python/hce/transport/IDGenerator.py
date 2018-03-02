'''
Created on Feb 4, 2014

@author: igor, bgv
'''


import socket
import time
import uuid
from transport.Singelon import Singleton

##IDGenerator is used to generate unique id for connections
#
class IDGenerator(object):
  '''
  The class is used to generate unique ID for connections
  '''
  __metaclass__ = Singleton

  def __init__(self):
    '''
    Constructor
    '''
    #@var _connection_uid
    #a member variable, holds generator internal state
    self._connection_uid = 0


  """
  Generate unique connection id
  """
  ##generate unique connection id
  #
  #@return unique id as string
  def get_connection_uid(self, idType=0):
    ret = None

    self._connection_uid = self._connection_uid + 1
    if idType == 0:
      ret = socket.gethostname() + "-" + str(time.time()) + "-" + uuid.uuid1().hex + "-" + str(self._connection_uid)
    else:
      ret = str(self._connection_uid)

    return ret

