'''
Created on Feb 25, 2014

@author: igor
'''

from transport.UIDGenerator import UIDGenerator

##Wrapper for structures passed between
#components of dtm
#
#
class Event(object):


  def __init__(self, uid, eventType, eventObj):
    '''
    Constructor
    '''
    self.uid = uid
    self.connect_name = ""  #set later
    self.connect_identity = ""
    self.cookie = None
    self.eventType = eventType
    self.eventObj = eventObj



class EventBuilder(object):


  def __init__(self):
    self.uidGenerator = UIDGenerator()


  def build(self, eventType, eventObj):
    event_uid = self.uidGenerator.get_uid()
    return Event(event_uid, eventType, eventObj)
