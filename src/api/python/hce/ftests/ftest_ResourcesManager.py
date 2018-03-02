'''
Created on Mar 17, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
from transport.Event import Event
from transport.Event import EventBuilder
from dtm.ResourcesManager import ResourcesManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dtm.Constants import EVENT_TYPES as EVENT
from app.BaseServerManager import BaseServerManager
import unittest
import ConfigParser
import dtm.EventObjects
import transport.Consts
import logging
import time


logging.basicConfig()
logger = logging.getLogger(__name__)
testResources = [{"id":1010, "cpu":10, "io":10, "ramR":10, "ramV":10, "swap":10, "disk":10, "uDate":55, 
                  "state":dtm.EventObjects.Resource.STATE_ACTIVE, "cpuCores":4, "threads":77, "processes":88},
                 {"id":1020, "cpu":20, "io":20, "ramR":20, "ramV":20, "swap":20, "disk":20, "uDate":55, 
                  "state":dtm.EventObjects.Resource.STATE_ACTIVE, "cpuCores":16, "threads":77, "processes":88},
                 {"id":1030, "cpu":30, "io":30, "ramR":30, "ramV":30, "swap":30, "disk":30, "uDate":95, 
                  "state":dtm.EventObjects.Resource.STATE_ACTIVE, "cpuCores":12, "threads":77, "processes":88},
                 {"id":1050, "cpu":50, "io":50, "ramR":50, "ramV":50, "swap":50, "disk":50, "uDate":145, 
                  "state":dtm.EventObjects.Resource.STATE_UNDEFINED, "cpuCores":4, "threads":77, "processes":88},
                 {"id":1010, "cpu":40, "io":40, "ramR":40, "ramV":40, "swap":40, "disk":40, "uDate":15, 
                  "state":dtm.EventObjects.Resource.STATE_ACTIVE, "cpuCores":6, "threads":77, "processes":88}]


class TestResoursesManager(unittest.TestCase):


  def setUp(self):
    self.config = ConfigParser.ConfigParser()
    self.servIndex = 1
    self.config.read("./dtmd.ini")
    self.connectionBuilder = ConnectionBuilderLight()
    self.adminServerConnection = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)    
    self.taskResourcesManager = ResourcesManager(self.config, self.connectionBuilder)
    self.moduleName = self.taskResourcesManager.__class__.__name__
    self.eventBuilder = EventBuilder()
    self.event = None
    self.reply_event = None 
    self.taskResourcesManager.start()
    self.connectionInit()
    self.recvEvent = None
    
    
  def fillLocalResources(self, localTestResources, idx):
    ret = dtm.EventObjects.Resource(localTestResources[idx]["id"])
    ret.cpu = localTestResources[idx]["cpu"]
    ret.io = localTestResources[idx]["io"]
    ret.ramR = localTestResources[idx]["ramR"]
    ret.ramV = localTestResources[idx]["ramV"]
    ret.swap = localTestResources[idx]["swap"]
    ret.disk = localTestResources[idx]["disk"]
    ret.uDate = localTestResources[idx]["uDate"]
    ret.state = localTestResources[idx]["state"]
    ret.cpuCores = localTestResources[idx]["cpuCores"]
    ret.threads = localTestResources[idx]["threads"]
    ret.processes = localTestResources[idx]["processes"]    
    

  def connectionInit(self):
    self.connectionBuilder = ConnectionBuilderLight()
    try:
      self.localConnection = self.taskResourcesManager.connectionBuilder.build(transport.Consts.CLIENT_CONNECT, \
              self.config.get(self.moduleName, ResourcesManager.RESOURCE_MANAGER_SERV_CONFIG_NAME))
      self.servIndex = self.servIndex + 1
    except ConfigParser.NoSectionError:
      logger.error(">>> TasksDataManager can't read config - Section Error")
    except ConfigParser.NoOptionError:
      logger.error(">>> TasksDataManager can't read config - Option Error")


  def tearDown(self):
    self.taskResourcesManager.exit_flag = True
    self.taskResourcesManager.join()
    for connection in self.taskResourcesManager.connections.values():
      connection.close()    
    self.adminServerConnection.close()
    time.sleep(1)    


  def testFunctional1(self):
    localResourcesList = []
    localResources = self.fillLocalResources(testResources, 0)
    localResourcesList.append(localResources)
    event = self.eventBuilder.build(EVENT.UPDATE_RESOURCES_DATA, localResourcesList)
    self.localConnection.send(event) 
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventObj != None, ">>> ret reply_event_obj is None")
    self.assertTrue(len(self.recvEvent.eventObj.statuses) == 1, ">>> ret reply_event_obj size is wrong")
    self.assertTrue(self.recvEvent.eventType == EVENT.UPDATE_RESOURCES_DATA_RESPONSE, 
                    ">>> reply_event event.eventType is wrong")   
    
    localResourcesList = []
    localResources = self.fillLocalResources(testResources, 1)   
    localResourcesList.append(localResources)
    localResources = self.fillLocalResources(testResources, 2)  
    localResourcesList.append(localResources)
    localResources = self.fillLocalResources(testResources, 3)    
    localResourcesList.append(localResources)   
    event = self.eventBuilder.build(EVENT.UPDATE_RESOURCES_DATA, localResourcesList)
    self.localConnection.send(event) 
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventObj != None, ">>> ret reply_event_obj is None")
    self.assertTrue(len(self.recvEvent.eventObj.statuses) == 3, ">>> ret reply_event_obj size is wrong")
    self.assertTrue(self.recvEvent.eventType == EVENT.UPDATE_RESOURCES_DATA_RESPONSE, 
                    ">>> reply_event event.eventType is wrong")     
    
    localResourcesList = []
    localResources = self.fillLocalResources(testResources, 4)   
    localResourcesList.append(localResources)
    event = self.eventBuilder.build(EVENT.UPDATE_RESOURCES_DATA, localResourcesList)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventObj != None, ">>> ret reply_event_obj is None")
    self.assertTrue(len(self.recvEvent.eventObj.statuses) == 1, ">>> ret reply_event_obj size is wrong")
    self.assertTrue(self.recvEvent.eventType == EVENT.UPDATE_RESOURCES_DATA_RESPONSE,
                    ">>> reply_event event.eventType is wrong")

    event = self.eventBuilder.build(EVENT.GET_AVG_RESOURCES, None)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventObj != None, ">>> ret reply_event_obj is None")
    self.assertTrue(self.recvEvent.eventType == EVENT.GET_AVG_RESOURCES_RESPONSE,
                    ">>> reply_event event.eventType is wrong")
    # only 1th, 2th and 4th elements are present and active on ResourceManager now
    compareVal = (testResources[1]["cpu"] + testResources[2]["cpu"] + testResources[4]["cpu"]) / 3
    self.assertTrue(self.recvEvent.eventObj.cpu == compareVal, ">>> cpuAVG wrong")
    compareVal = (testResources[1]["io"] + testResources[2]["io"] + testResources[4]["io"]) / 3
    self.assertTrue(self.recvEvent.eventObj.io == compareVal, ">>> ioAVG wrong")
    compareVal = (testResources[1]["ramR"] + testResources[2]["ramR"] + testResources[4]["ramR"]) / 3
    self.assertTrue(self.recvEvent.eventObj.ramR == compareVal, ">>> ramRAVG wrong")
    compareVal = (testResources[1]["ramV"] + testResources[2]["ramV"] + testResources[4]["ramV"]) / 3
    self.assertTrue(self.recvEvent.eventObj.ramV == compareVal, ">>> ramVAVG wrong")
    compareVal = (testResources[1]["swap"] + testResources[2]["swap"] + testResources[4]["swap"]) / 3
    self.assertTrue(self.recvEvent.eventObj.swap == compareVal, ">>> swapAVG wrong")
    compareVal = (testResources[1]["disk"] + testResources[2]["disk"] + testResources[4]["disk"]) / 3
    self.assertTrue(self.recvEvent.eventObj.disk == compareVal, ">>> diskAVG wrong")
    compareVal = (testResources[1]["cpuCores"] + testResources[2]["cpuCores"] + testResources[4]["cpuCores"]) / 3
    self.assertTrue(self.recvEvent.eventObj.cpuCores == compareVal, ">>> cpuCores wrong")
    compareVal = (testResources[1]["threads"] + testResources[2]["threads"] + testResources[4]["threads"]) / 3
    self.assertTrue(self.recvEvent.eventObj.threads == compareVal, ">>> threads wrong")
    compareVal = (testResources[1]["processes"] + testResources[2]["processes"] + testResources[4]["processes"]) / 3
    self.assertTrue(self.recvEvent.eventObj.processes == compareVal, ">>> processes wrong")    
    self.assertTrue(self.recvEvent.eventObj.uDate == testResources[4]["uDate"] , ">>> diskAVG wrong")
   
    
if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()