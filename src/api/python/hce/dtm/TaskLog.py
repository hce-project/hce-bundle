'''
Created on Mar 6, 2014

@author: igor
'''


##Class describes structures of  task item used in TaskManager
#
class TaskLog(object):


  ##constructor
  #initialise all class variable of None
  #more information in DTM_application_architecture   
  def __init__(self):
    self.id = None
    self.pId = None
    self.nodeName = None
    self.cDate = None
    self.sDate = None
    self.rDate = None
    self.fDate = None
    self.pTime = None
    self.pTimeMax = None
    self.state = None
    self.uRRAM = None
    self.uVRAM = None
    self.uCPU = None
    self.uThreads = None
    self.tries = None
    self.host = None
    self.port = None
    self.deleteTaskId = None
    self.autoCleanupFields = None
    self.type = None
    self.name = None
    