'''
Created on Mar 5, 2014

@author: igor
'''
import unittest
from mock import MagicMock, call, ANY
import ConfigParser
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from app.BaseServerManager import BaseServerManager
from dtm.ClientInterfaceService import ClientInterfaceService, CONFIG_SECTION
import transport.Consts as tr_const
from dtm.Constants import EVENT_TYPES
from transport.Event import EventBuilder

import logging
logging.basicConfig() #basic logging configuration


class TestClientInterfaceService(unittest.TestCase):


    def setUp(self):
        self.config = ConfigParser.RawConfigParser() 
        self.eventBuilder = EventBuilder()
        addr = "127.0.0.1"
        port = 8899
        self.tcpAddr = "127.0.0.1:8899"
        self.config.add_section(CONFIG_SECTION)
        self.config.set(CONFIG_SECTION, "serverHost", addr)
        self.config.set(CONFIG_SECTION, "serverPort", port)
        self.config.set(CONFIG_SECTION, "clientTaskManager", "TaskManager")
        self.config.set(CONFIG_SECTION, "clientExecutionEnvironmentManager", "ExecutionEnvironmentManager")
        
        self.connectionBuilderLight = ConnectionBuilderLight()
        self.taskFakeServer = self.connectionBuilderLight.build(tr_const.SERVER_CONNECT, "TaskManager")
        self.eeFakeServer = self.connectionBuilderLight.build(tr_const.SERVER_CONNECT, "ExecutionEnvironmentManager")
        self.adminServerFake = self.connectionBuilderLight.build(tr_const.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)

        self.clientInterfaceService = None

    
    def tearDown(self):
        self.taskFakeServer.close()
        self.eeFakeServer.close()
        self.adminServerFake.close()
        self.clientInterfaceService.connections[self.clientInterfaceService.server].close()
    
    
    def test_reading_config_params(self):
        connectBuilder_mock = MagicMock(spec = ConnectionBuilderLight)
        
        self.clientInterfaceService = ClientInterfaceService(self.config, connectBuilder_mock)    
        expect_connect_calls = [call.build(tr_const.SERVER_CONNECT, self.tcpAddr, tr_const.TCP_TYPE),
                                                call.build(tr_const.CLIENT_CONNECT, 'TaskManager'),
                                                call.build(tr_const.CLIENT_CONNECT, 'ExecutionEnvironmentManager')]
                        
        self.assertEqual(expect_connect_calls, connectBuilder_mock.mock_calls, "config parsing is failed")
        
        
    def test_route_event_to_taskManager(self):
        taskManager_mock = MagicMock()
        
        transport_events = [EVENT_TYPES.NEW_TASK, EVENT_TYPES.UPDATE_TASK, EVENT_TYPES.GET_TASK_STATUS,
                                         EVENT_TYPES.FETCH_RESULTS_CACHE, EVENT_TYPES.DELETE_TASK]
        
        self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilderLight)
        
        #change handler
        for evntHandler in self.clientInterfaceService.event_handlers:
            if self.clientInterfaceService.event_handlers[evntHandler] == self.clientInterfaceService.onTaskManagerRoute:
                 self.clientInterfaceService.event_handlers[evntHandler] = taskManager_mock 
        
        for eventType in transport_events:
            event = self.eventBuilder.build(eventType, "data obj")            
            self.clientInterfaceService.process(event)
            
        self.assertEqual(len(transport_events), taskManager_mock.call_count, "")
        
        
        
    def test_route_event_to_eeManager(self):
        taskManager_mock = MagicMock()
        
        transport_events = [EVENT_TYPES.CHECK_TASK_STATE, EVENT_TYPES.FETCH_TASK_RESULTS]
                
        self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilderLight)
        
        #change handler
        for evntHandler in self.clientInterfaceService.event_handlers:
            if self.clientInterfaceService.event_handlers[evntHandler] == self.clientInterfaceService.onEEManagerRoute:
                 self.clientInterfaceService.event_handlers[evntHandler] = taskManager_mock 
        
        for eventType in transport_events:
            event = self.eventBuilder.build(eventType, "data obj")            
            self.clientInterfaceService.process(event)
            
        self.assertEqual(len(transport_events), taskManager_mock.call_count, "")



    def test_route_response_events(self):
        taskManager_mock = MagicMock()
        
        transport_events = [EVENT_TYPES.NEW_TASK_RESPONSE, EVENT_TYPES.UPDATE_TASK_RESPONSE,
                                         EVENT_TYPES.CHECK_TASK_STATE_RESPONSE, EVENT_TYPES.GET_TASK_STATUS_RESPONSE,
                                         EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE, EVENT_TYPES.DELETE_TASK_RESPONSE]
                                
        self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilderLight)
        
        #change handler
        for evntHandler in self.clientInterfaceService.event_handlers:
            if self.clientInterfaceService.event_handlers[evntHandler] == self.clientInterfaceService.onDTMClientRoute:
                 self.clientInterfaceService.event_handlers[evntHandler] = taskManager_mock 
        
        for eventType in transport_events:
            event = self.eventBuilder.build(eventType, "data obj")
            self.clientInterfaceService.process(event)
            
        self.assertEqual(len(transport_events), taskManager_mock.call_count, "")
        
        
        
    def test_add_process_event(self):
        self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilderLight)
        
        event = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, "data obj")
        event.connect_identity = "1234"
        event.connect_name = "testName"
        
        self.clientInterfaceService.process(event)
        
        self.assertEqual(len(self.clientInterfaceService.processEvents), 1, "")
        process_event = self.clientInterfaceService.processEvents[event.uid]
        self.assertEqual(process_event.connect_identity, "1234", "")
        self.assertEqual(process_event.connect_name, "testName", "")
        self.assertEqual(process_event.eventObj, None, "")
        
        
        
    def test_drop_process_event(self):
        self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilderLight)
        
        event = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, "data obj")        
        self.clientInterfaceService.process(event)
        self.clientInterfaceService.unregisteEvent(event)
        
        self.assertEqual(len(self.clientInterfaceService.processEvents), 0, "")
        
        
    def test_supress_keyerror_exception(self):
        self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilderLight)
        event = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, "data obj")
        
        self.clientInterfaceService.onDTMClientRoute(event)