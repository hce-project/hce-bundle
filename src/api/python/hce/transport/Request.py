'''
Created on Feb 5, 2014

@author: igor
'''


##It's a wrapper similar to zmsg.hpp in sense of encapsulation of hce
#message structure
#
class Request(object):
  '''
  It's a wrapper similar to zmsg.hpp in sense of encapsulation of hce
  message structure
  '''


  ##constructor
  #
  #according to the protocol message consist at least 2 part - uid and body
  #the first part is the uid
  #@param uid - unique message identificator
  def __init__(self, uid):
    self.uid = uid
    self.body = []
    self.body.append(uid)
    self.connect_identity = None
    self.route = None
    self.task_type = 0


  ##return uid of the message
  #
  #@return uid
  def get_uid(self):
    return self.uid


  ##add data to the message's body
  #
  #@param data append data
  #@return None
  def add_data(self, data):
    self.body.append(data)


  ##return body of the message
  #
  #@return message body(list)
  def get_body(self):
    return self.body
