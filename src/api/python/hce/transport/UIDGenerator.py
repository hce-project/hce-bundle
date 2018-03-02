'''
Created on Feb 11, 2014

@author: igor, bgv
'''


import time
import binascii
from transport.IDGenerator import IDGenerator

##UIDGenerator is used to generate unique message id
#
class UIDGenerator(object):


  ##constructor
  #
  def __init__(self):
    '''
    Constructor
    '''
    #@var _start
    #a member variable, holds generator internal state
    self._start = 0


  ##get_uid
  #
  #@return uid as string
  def get_uid(self, idType=0):
    self._start = self._start + 1
    if idType == 0:
      idGenerator = IDGenerator()
      #return str(binascii.crc32(idGenerator.get_connection_uid() + str(self._start)))
      return "%d" % binascii.crc32(idGenerator.get_connection_uid() + str(self._start), int(time.time()))
    else:
      return str(self._start)

