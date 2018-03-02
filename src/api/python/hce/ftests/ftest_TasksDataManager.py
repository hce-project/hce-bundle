'''
Created on Mar 10, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
from transport.Event import Event
from transport.Event import EventBuilder  
from dtm.TasksDataManager import TasksDataManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dtm.Constants import EVENT_TYPES as EVENT
from app.BaseServerManager import BaseServerManager
import unittest
import dtm.EventObjects
import ConfigParser
import transport.Consts
import logging
import time

logger = logging.getLogger(__name__)

##Class TestTasksDataManager, contains functional tests of TasksDataManager module
#
class TestTasksDataManager(unittest.TestCase):


  def setUp(self):
    self.servIndex = 1
    self.connectionBuilder = ConnectionBuilderLight()
    self.localConnection = None
    self.adminServerConnection = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)
    self.config = ConfigParser.ConfigParser()
    self.config.read("./dtmd.ini")
    self.taskDataManager = TasksDataManager(self.config, self.connectionBuilder)
    self.taskDataManager.start()
    self.eventBuilder = EventBuilder()
    self.recvEvent = None
    self.event = None
    self.reply_event = None
    self.moduleName = self.taskDataManager.__class__.__name__
    self.connectionInit()


  def connectionInit(self):
    try:
      self.localConnection = self.connectionBuilder.build(transport.Consts.CLIENT_CONNECT, \
                        self.config.get(self.moduleName, self.taskDataManager.TASK_DATA_MANAGER_SERV_CONFIG_NAME))
      self.servIndex = self.servIndex + 1
    except ConfigParser.NoSectionError:
      logger.error(">>> TasksDataManager can't read config - Section Error")
    except ConfigParser.NoOptionError:
      logger.error(">>> TasksDataManager can't read config - Option Error")


  def tearDown(self):
    self.taskDataManager.exit_flag = True
    self.taskDataManager.join()
    for connection in self.taskDataManager.connections.values():
      connection.close()    
    self.adminServerConnection.close()
    self.localConnection.close()
    time.sleep(1)


  def insert(self, taskId):
    newTask = dtm.EventObjects.NewTask("bash", taskId)
    event = self.eventBuilder.build(EVENT.NEW_TASK, newTask)
    self.localConnection.send(event) 
    self.recvEvent = self.localConnection.recv()


  def testOnNewTask(self):
    taskId = 335
    self.insert(taskId)      
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventType == EVENT.NEW_TASK_RESPONSE, ">>> reply_event event.eventType is wrong")    


  def testOnFetchTask(self):
    taskId = 335
    self.insert(taskId)
    taskId = 200
    fetchTask = dtm.EventObjects.FetchTaskData(taskId)
    event = self.eventBuilder.build(EVENT.FETCH_TASK_DATA, fetchTask)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventType == EVENT.FETCH_TASK_DATA_RESPONSE,
                    ">>> reply_event event.eventType is wrong")
    self.assertTrue(self.recvEvent.eventObj != 1, ">>> reply.eventobject is None")
    taskId = 335
    fetchTask = dtm.EventObjects.FetchTaskData(taskId)
    event = self.eventBuilder.build(EVENT.FETCH_TASK_DATA, fetchTask)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent.eventObj != 1, ">>> reply.eventobject is None")


  def testOnUpdateTask(self): 
    taskId = 335
    self.insert(taskId)
    taskId = 200
    updateTask = dtm.EventObjects.UpdateTask(taskId)
    event = self.eventBuilder.build(EVENT.UPDATE_TASK, updateTask)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")


  def testOnDeleteTask(self):
    taskId = 335
    self.insert(taskId)
    taskId = 335
    deleteTask = dtm.EventObjects.UpdateTask(taskId)
    event = self.eventBuilder.build(EVENT.DELETE_TASK_DATA, deleteTask)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")  


  def testOnInsertEEResponse(self):
    taskId = 335
    insertEEResponse = dtm.EventObjects.EEResponseData(taskId)
    event = self.eventBuilder.build(EVENT.INSERT_EE_DATA, insertEEResponse)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent  != None, ">>> ret reply_event is None")


  def testOnFetchEEResponse(self):
    taskId = 335
    fetchEEResponse = dtm.EventObjects.FetchEEResponseData(taskId)
    event = self.eventBuilder.build(EVENT.FETCH_EE_DATA, fetchEEResponse)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventType == EVENT.FETCH_EE_DATA_RESPONSE,
                    ">>> reply_event event.eventType is wrong")


  def testOnDeleteEEResponse(self):
    taskId = 335
    deleteEEResponse = dtm.EventObjects.DeleteEEResponseData(taskId)
    event = self.eventBuilder.build(EVENT.DELETE_EE_DATA, deleteEEResponse)
    self.localConnection.send(event)
    self.recvEvent = self.localConnection.recv()
    self.assertTrue(self.recvEvent != None, ">>> ret reply_event is None")
    self.assertTrue(self.recvEvent.eventType == EVENT.DELETE_EE_DATA_RESPONSE,
                    ">>> reply_event event.eventType is wrong")


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()