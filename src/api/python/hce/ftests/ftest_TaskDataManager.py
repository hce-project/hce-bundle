from transport.Event import Event
from transport.Event import EventBuilder  
from dtm.TaskDataManager import TaskDataManager
from dtm.Constants import EVENT_TYPES as EVENT
import unittest
import dtm.EventObjects
import ConfigParser

globalEvent = None
globalReplyEvent = None

def localReply(event, reply_event):
  global globalEvent
  globalEvent = event
  global globalReplyEvent
  globalReplyEvent = reply_event

class TestTaskDataManager(unittest.TestCase):


  def setUp(self):
    self.config = ConfigParser.ConfigParser()
    self.config.read("./TDM.ini")
    self.taskDataManager = TaskDataManager(self.config)
    self.eventBuilder = EventBuilder()
    self.taskDataManager.reply = localReply
    self.event = None
    self.reply_event = None
    global globalEvent
    globalEvent = None
    global globalReplyEvent
    globalReplyEvent = None    


  def tearDown(self):
    pass


  def insert(self, taskId):
    newTask = dtm.EventObjects.NewTask("bash")
    newTask.id = taskId
    event = self.eventBuilder.build(EVENT.NEW_TASK, newTask)
    self.taskDataManager.onNewTask(event)    

  def testOnNewTask(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    self.insert(taskId)
    self.assertTrue(globalEvent != None, ">>> ret event is None")        
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")
    self.assertTrue(globalEvent.eventType == EVENT.NEW_TASK, ">>> ret event.eventType is wrong")
    self.assertTrue(globalReplyEvent.eventType == EVENT.NEW_TASK_RESPONSE, ">>> reply_event event.eventType is wrong")
    
  def testOnFetchTask(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    self.insert(taskId)
    taskId = 200
    fetchTask = dtm.EventObjects.FetchTaskData(taskId)
    event = self.eventBuilder.build(EVENT.FETCH_TASK_DATA, fetchTask)
    self.taskDataManager.onFetchTask(event)
    self.assertTrue(globalEvent != None, ">>> ret event is None")        
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")
    self.assertTrue(globalEvent.eventType == EVENT.FETCH_TASK_DATA, ">>> ret event.eventType is wrong")
    self.assertTrue(globalReplyEvent.eventType == EVENT.FETCH_TASK_DATA_RESPONSE, 
                    ">>> reply_event event.eventType is wrong")
    self.assertTrue(len(globalReplyEvent.eventObj) == 1, ">>> reply_event event.eventType not None")   
    self.assertTrue(globalReplyEvent.eventObj[0] == None, ">>> reply_event event.eventType not None")
    
    taskId = 335
    fetchTask = dtm.EventObjects.FetchTaskData(taskId)
    event = self.eventBuilder.build(EVENT.FETCH_TASK_DATA, fetchTask)
    self.taskDataManager.onFetchTask(event)
    self.assertTrue(len(globalReplyEvent.eventObj) == 1, ">>> reply_event event.eventType not None")   
    self.assertTrue(globalReplyEvent.eventObj[0] != None, ">>> reply_event event.eventType not None")    
    
    
  def testOnUpdateTask(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    self.insert(taskId)
    taskId = 200
    updateTask = dtm.EventObjects.UpdateTask(taskId)
    event = self.eventBuilder.build(EVENT.UPDATE_TASK, updateTask) 
    self.taskDataManager.onUpdateTask(event)
    self.assertTrue(globalEvent != None, ">>> ret event is None")
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")
    
    
  def testOnDeleteTask(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    self.insert(taskId)
    taskId = 335
    deleteTask = dtm.EventObjects.UpdateTask(taskId)
    event = self.eventBuilder.build(EVENT.DELETE_TASK, deleteTask)
    self.taskDataManager.onDeleteTask(event)
    self.assertTrue(globalEvent != None, ">>> ret event is None")
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")
  
  
  def testOnInsertEEResponse(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    insertEEResponse = dtm.EventObjects.EEResponseData(taskId)
    event = self.eventBuilder.build(EVENT.INSERT_EE_DATA, insertEEResponse) 
    self.taskDataManager.onInsertEEResponse(event)
    self.assertTrue(globalEvent != None, ">>> ret event is None")
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")      
    
    
  def testOnFetchEEResponse(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    fetchEEResponse = dtm.EventObjects.FetchEEResponseData(taskId)
    event = self.eventBuilder.build(EVENT.FETCH_EE_DATA, fetchEEResponse) 
    self.taskDataManager.onFetchEEResponse(event)
    self.assertTrue(globalEvent != None, ">>> ret event is None")
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")
    self.assertTrue(globalEvent.eventType == EVENT.FETCH_EE_DATA, ">>> ret event.eventType is wrong")
    self.assertTrue(globalReplyEvent.eventType == EVENT.FETCH_EE_DATA_RESPONSE, 
                    ">>> reply_event event.eventType is wrong")
  
  
  def testOnDeleteEEResponse(self):
    global globalEvent
    global globalReplyEvent  
    taskId = 335
    deleteEEResponse = dtm.EventObjects.DeleteEEResponseData(taskId)
    event = self.eventBuilder.build(EVENT.DELETE_EE_DATA, deleteEEResponse)
    self.taskDataManager.onDeleteEEResponse(event)
    self.assertTrue(globalEvent != None, ">>> ret event is None")
    self.assertTrue(globalReplyEvent != None, ">>> ret reply_event is None")
    self.assertTrue(globalEvent.eventType == EVENT.DELETE_EE_DATA, ">>> ret event.eventType is wrong")
    self.assertTrue(globalReplyEvent.eventType == EVENT.DELETE_EE_DATA_RESPONSE, 
                    ">>> reply_event event.eventType is wrong")
    
      
if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()