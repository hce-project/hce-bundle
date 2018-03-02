'''
Created on Feb 5, 2014

@author: igor
'''


##Exception which inform about errors which appeared during
#the hce protocol parsing procedure
#
class ResponseFormatErr(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)


##It's a wrapper similar to zmsg.hpp in sense of encapsulation of hce
#response message structure
#
class Response(object):
  '''
  Wrapper over hce response protocol - so it can raise AttributeError:
  when construct from wrong protocol format
  '''


  ##constructor
  #parse data according to the protocol
  #
  #@param identity - zmq socket identity
  #@param data row data from zmq.socket
  #@return None or throw ResponseFormatErr
  def __init__(self, data, connect_identity=None):
    if len(data) < 2:
      raise ResponseFormatErr(data)
    self.connect_identity = connect_identity
    self.uid = data[0]
    self.body = data[1]


  ##get_uid
  #
  #@return response uid
  def get_uid(self):
    return self.uid


  ##get_body
  #
  #return response body
  def get_body(self):
    return self.body
