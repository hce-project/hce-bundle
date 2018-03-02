'''
HCE project, Python bindings, Distributed Tasks Manager application.
TasksStateUpdateService object functional tests.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ConfigParser
import time
import unittest
import logging
from dtm.TasksStateUpdateService import TasksStateUpdateService
from app.BaseServerManager import BaseServerManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.ConnectionBuilder import ConnectionBuilder
from transport.IDGenerator import IDGenerator
from transport.Connection import ConnectionParams
from transport.Request import Request
from transport.Event import EventBuilder
import transport.Consts as TRANSPORT_CONSTS
from drce.CommandConvertor import CommandConvertor
import zmq
from dtm import Constants as DTM_CONSTS
from dtm.EventObjects import UpdateTaskFields, AvailableTaskIds, CheckTaskState

FORMAT = '%(asctime)s - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

class TestTasksStateUpdateService(unittest.TestCase):

  #Test TasksStateUpdateService instantiation
  CONFIG_SECTION = "TasksStateUpdateService"
  SERVICE_BIND_IP = "127.0.0.1"
  SERVICE_BIND_PORT = "5500"

  def __init__(self, *args, **kvargs):
    unittest.TestCase.__init__(self, *args, **kvargs)
    self.eventBuilder = EventBuilder()

  def setUp(self):
    if not hasattr(self, "inited"):
      self.inited = True

      config = ConfigParser.RawConfigParser()
      config.add_section(self.CONFIG_SECTION)
      config.set(self.CONFIG_SECTION, "clientTasksManager", "TasksManager")
      config.set(self.CONFIG_SECTION, "clientExecutionEnvironmentManager","EEManager")
      config.set(self.CONFIG_SECTION, "serverHost", self.SERVICE_BIND_IP)
      config.set(self.CONFIG_SECTION, "serverPort", self.SERVICE_BIND_PORT)
      
      #Dependent objects creation
      idGenerator = IDGenerator()
      connectionBuilderLight = ConnectionBuilderLight()
      connectionBuilder = ConnectionBuilder(idGenerator)
      #create AdminServer 
      self.adminServer = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)
      self.taskManagerConnServer = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "TasksManager")
      self.eeManagerServer = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "EEManager")
      # time.sleep(1)
      self.tsus = TasksStateUpdateService(config)
      self.tsus.pollTimeout = 100
      # start the threaded server
      self.tsus.start()
      self.hceNode = connectionBuilder.build(TRANSPORT_CONSTS.DATA_CONNECT_TYPE, ConnectionParams(self.SERVICE_BIND_IP, self.SERVICE_BIND_PORT), TRANSPORT_CONSTS.CLIENT_CONNECT)
      self.drceCommandConvertor = CommandConvertor()

  def tearDown(self):
    self.hceNode.close()
    self.adminServer.close()
    self.eeManagerServer.close()
    self.tsus.exit_flag = True
    time.sleep(0.3)
    self.taskManagerConnServer.close()
    time.sleep(0.2)
    for conn in self.tsus.connections.itervalues():
      conn.close()

  def testUpdateStateNomal(self):
    req = Request("1")
    req.add_data('''[{
      "error_code": 0, 
      "error_message": "", 
      "id": "123", 
      "type": 0,
      "host": "", 
      "port": 0, 
      "state": 0, 
      "pid": 1186, 
      "stdout": "",
      "stderror": "",
      "exit_status": 0, 
      "files": [], 
      "node":"node for test",
      "time": 0
    }]
    ''')
    self.hceNode.send(req)
    time.sleep(0.3)
    #TasksStateUpdateService send UpdateTaskFields message to TaskManager
    pollResult = self.taskManagerConnServer.poll()
    self.assertEqual(zmq.POLLIN, pollResult & zmq.POLLIN)
    event = self.taskManagerConnServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.UPDATE_TASK_FIELDS)
    self.assertTrue(isinstance(event.eventObj, UpdateTaskFields))
    self.assertEqual(event.eventObj.id, "123")
    self.assertEqual(event.eventObj.fields["state"], 0)
    self.assertEqual(event.eventObj.fields["pId"], 1186)
    self.assertEqual(event.eventObj.fields["nodeName"], "node for test")

  def testUpdateStateError(self):
    req = Request("1")
    req.add_data('''[{
      "error_code": 3, 
      "error_message": "error message for test", 
      "id": "1", 
      "type": 0,
      "host": "", 
      "port": 0, 
      "state": 0, 
      "pid": 1186, 
      "stdout": "",
      "stderror": "",
      "exit_status": 0, 
      "files": [], 
      "node":"node for test",
      "time": 0
    }]
    ''')
    self.hceNode.send(req)
    time.sleep(0.3)
    pollResult = self.taskManagerConnServer.poll()
    #TasksStateService don't send message to TaskManager
    if pollResult & zmq.POLLIN == zmq.POLLIN:
      event = self.taskManagerConnServer.recv()
      self.assertNotEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.UPDATE_TASK_FIELDS)
    
  def testCheckState(self):
    allAvailableTaskIds = ["1","2"]
    TasksStateUpdateService.FETCH_TASKS_IDS_INTERVAL = 1

    #test send CheckTaskState
    time.sleep(TasksStateUpdateService.FETCH_TASKS_IDS_INTERVAL)
    pollResult = self.taskManagerConnServer.poll(0.1)
    self.assertEqual(zmq.POLLIN, zmq.POLLIN & pollResult)
    event = self.taskManagerConnServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS)
    res = AvailableTaskIds(allAvailableTaskIds)
    responseEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.AVAILABLE_TASK_IDS_RESPONSE, res)
    responseEvent.connect_identity = event.connect_identity
    self.taskManagerConnServer.send(responseEvent)
    time.sleep(0.1)

    #check the EEManager received the CheckTaskState
    pollResult = self.eeManagerServer.poll(0.1)
    self.assertEqual(zmq.POLLIN, zmq.POLLIN & pollResult)
    event = self.eeManagerServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE)
    self.assertTrue(isinstance(event.eventObj, CheckTaskState))
    firstId = event.eventObj.id
    self.assertIn(firstId, allAvailableTaskIds)

    #test send CheckTaskState again
    time.sleep(TasksStateUpdateService.FETCH_TASKS_IDS_INTERVAL)
    pollResult = self.taskManagerConnServer.poll(0.1)
    self.assertEqual(zmq.POLLIN, zmq.POLLIN & pollResult)
    event = self.taskManagerConnServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS)
    res = AvailableTaskIds(allAvailableTaskIds)
    responseEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.AVAILABLE_TASK_IDS_RESPONSE, res)
    responseEvent.connect_identity = event.connect_identity
    self.taskManagerConnServer.send(responseEvent)
    time.sleep(0.1)

    pollResult = self.eeManagerServer.poll(0.1)
    self.assertEqual(zmq.POLLIN, zmq.POLLIN & pollResult)
    event = self.eeManagerServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE)
    self.assertTrue(isinstance(event.eventObj, CheckTaskState))
    secondId = event.eventObj.id
    self.assertIn(secondId, allAvailableTaskIds)
    #test the duplicate task avoiding
    self.assertNotEqual(firstId, secondId)

    #test send CheckTaskState again, all task sent, then it clear the sent records
    time.sleep(TasksStateUpdateService.FETCH_TASKS_IDS_INTERVAL)
    pollResult = self.taskManagerConnServer.poll(0.1)
    self.assertEqual(zmq.POLLIN, zmq.POLLIN & pollResult)
    event = self.taskManagerConnServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS)
    res = AvailableTaskIds(allAvailableTaskIds)
    responseEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.AVAILABLE_TASK_IDS_RESPONSE, res)
    responseEvent.connect_identity = event.connect_identity
    self.taskManagerConnServer.send(responseEvent)
    time.sleep(0.1)

    #check the EEManager received the CheckTaskState
    pollResult = self.eeManagerServer.poll(0.1)
    self.assertEqual(zmq.POLLIN, zmq.POLLIN & pollResult)
    event = self.eeManagerServer.recv()
    self.assertEqual(event.eventType, DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE)
    self.assertTrue(isinstance(event.eventObj, CheckTaskState))
    self.assertIn(event.eventObj.id, allAvailableTaskIds)

if __name__ == "__main__":
  unittest.main()
  
