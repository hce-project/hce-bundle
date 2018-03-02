'''
Created on Feb 26, 2014

@author: igor
'''
import unittest
from mock import MagicMock, ANY
import sys
import zmq

from app.BaseServerManager import BaseServerManager
from app.PollerManager import PollerManager
from transport.Event import EventBuilder
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.ConnectionLight import ConnectionLight
from transport.Connection import ConnectionTimeout
from transport.Connection import TransportInternalErr
from transport.Response import Response
from transport.Connection import Connection
import transport.Consts as transport_const
from dtm.Constants import EVENT_TYPES 
from dtm.EventObjects import AdminState, AdminStatData

import logging
FORMAT = '%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT) #basic logging configuration

class Matcher(object):
    
    def __init__(self, compare, some_obj):
        self.compare = compare
        self.some_obj = some_obj
    
    def __eq__(self, other):
        return self.compare(self.some_obj, other)


def matchEvents(first, second):
    return first.uid == second.uid and first.eventType == second.eventType and\
        first.eventObj == second.eventObj 
        
        
def matchStatEvents(first, second):
    print first.eventObj.fields
    print second.eventObj.fields
    return first.uid == second.uid and first.eventType == second.eventType and\
        first.eventObj.fields == second.eventObj.fields


def match_tcp_raw_events(first, second):
    return first.eventType == second.eventType and first.eventObj.__dict__ == second.eventObj.__dict__


class TestBaseServerManager(unittest.TestCase):


    def setUp(self):
        self.connectionBuilderLight = ConnectionBuilderLight()
        self.adminServerFake = self.connectionBuilderLight.build(transport_const.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)
        
        self.sock_mock = MagicMock(spec = zmq.Socket)
        self.poller_mock = MagicMock(spec = zmq.Poller)
        self.poller_manager_mock = MagicMock(spec = PollerManager)
        self.connect_mock = MagicMock(spec = ConnectionLight) 
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=self.connectionBuilderLight)
        self.event_builder = EventBuilder()
        self.event = self.event_builder.build(EVENT_TYPES.NEW_TASK, "eventObj")                 
        self.connect_name = "Admin"
        self.event.connect_name = self.connect_name        
        self.adminState = AdminState("BaseServerManager", AdminState.STATE_SHUTDOWN)
        
        
    def tearDown(self):
        self.adminServerFake.close()


    def test_correct_add_new_connection(self):
        connect = ConnectionLight(self.sock_mock, transport_const.CLIENT_CONNECT)        
        self.base_server_manager.addConnection(self.connect_name, connect)        
                
        self.assertEqual(self.base_server_manager.connections[self.connect_name], connect, "")
        
        
    def test_set__event_handler(self):        
        handler_mock = MagicMock()        
        self.base_server_manager.setEventHandler(EVENT_TYPES.NEW_TASK, handler_mock)
        
        self.base_server_manager.process(self.event)
        
        handler_mock.assert_called_once_with(self.event)
        

    def test_call_unhandled_event_handler(self):
        unhandled_mock = MagicMock()
        self.base_server_manager.on_unhandled_event = unhandled_mock
                                                                        
        self.base_server_manager.process(self.event)
        
        unhandled_mock.assert_called_once_with(self.event)


    def test_send_event(self):
        self.base_server_manager.addConnection(self.connect_name, self.connect_mock)        
        self.base_server_manager.send(self.connect_name,self. event)
        
        self.connect_mock.send.assert_called_once_with(self.event)
                

    def test_reply(self):
        self.base_server_manager.addConnection(self.connect_name, self.connect_mock)
        
        reply_event = self.event_builder.build(EVENT_TYPES.NEW_TASK, "new obj")            
        expect_event = reply_event
        expect_event.uid = self.event.uid
         
        match_event = Matcher(matchEvents, expect_event)
        self.base_server_manager.reply(self.event, reply_event)
        
        self.connect_mock.send.assert_called_once_with(match_event)
        
                    
    def test_run_one_loop(self):        
        self.poller_manager_mock.poll.return_value = [self.connect_name]
        self.connect_mock.recv.return_value = self.event

        handler_mock = MagicMock()        
        self.base_server_manager.setEventHandler(EVENT_TYPES.NEW_TASK, handler_mock)
        self.base_server_manager.addConnection(self.connect_name, self.connect_mock)
        
        self.base_server_manager.poll()
                
        handler_mock.assert_called_once_with(self.event)
        
        
    def test_call_on_timeout_callback(self):
        self.poller_manager_mock.poll.side_effect = ConnectionTimeout("boom")        
        on_timeout_mock = MagicMock()
        self.base_server_manager.on_poll_timeout = on_timeout_mock
        
        self.base_server_manager.poll()
        
        on_timeout_mock.assert_called_once_with()
        
                        
    def test_propagate_out_TransportInternalErr(self):
        self.poller_manager_mock.poll.return_value = [self.connect_name]
        self.connect_mock.recv.side_effect = TransportInternalErr("boom")
        
        self.base_server_manager.addConnection(self.connect_name, self.connect_mock)
        
        with self.assertRaises(TransportInternalErr):
            list(self.base_server_manager.poll())
            
            
            
    def test_process_response_tcp_raw(self):
        raw_server = "raw_server"
        response = Response(["sock_identity", "id", "body"])
        connect_mock = MagicMock(Connection)
        connect_mock.recv.return_value = response
        self.poller_manager_mock.poll.return_value = [raw_server]
        
        self.base_server_manager.addConnection(raw_server, connect_mock)
        event_processor_mock = MagicMock()
        
        expect_event = self.base_server_manager.eventBuilder.build(EVENT_TYPES.SERVER_TCP_RAW, response)
        match_event = Matcher(match_tcp_raw_events, expect_event)
        
        self.base_server_manager.setEventHandler(EVENT_TYPES.SERVER_TCP_RAW, event_processor_mock)
                        
        self.base_server_manager.poll()
        
        event_processor_mock.assert_called_once_with(match_event)
        
        
    def test_create_client_admin_connect(self):
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock)
        
        connectLightBuilder_mock.build.assert_called_once_with(ANY, ANY)
                
    
    def test_create_server_connect(self):
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        adminConnect_mock = MagicMock(ConnectionLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock,
                                                     admin_connection=adminConnect_mock)
        self.assertEqual(connectLightBuilder_mock.build.call_count, 0, "was called")
        
        
    def test_get_client_admin_event(self):
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock)
                        
        adminEvent = self.event_builder.build(EVENT_TYPES.ADMIN_STATE, self.adminState)        
        connect_mock = MagicMock(ConnectionLight)
        connect_mock.recv.return_value = adminEvent
        
        self.poller_manager_mock.poll.return_value = [self.base_server_manager.ADMIN_CONNECT_CLIENT]        
        self.base_server_manager.addConnection(self.base_server_manager.ADMIN_CONNECT_CLIENT, connect_mock)
        
        self.base_server_manager.poll()
        
        self.assertEqual(self.base_server_manager.exit_flag, True, "still running")
        connect_mock.send.assert_called_once_with(ANY)
        
                
    def test_admin_event_broken_command_type(self):
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock)
                        
        self.adminState.command = AdminState.STATE_NOP
        adminEvent = self.event_builder.build(EVENT_TYPES.ADMIN_STATE, self.adminState)        
        connect_mock = MagicMock(ConnectionLight)
        connect_mock.recv.return_value = adminEvent
        
        self.poller_manager_mock.poll.return_value = [self.base_server_manager.ADMIN_CONNECT_CLIENT]        
        self.base_server_manager.addConnection(self.base_server_manager.ADMIN_CONNECT_CLIENT, connect_mock)
        
        self.base_server_manager.poll()
        
        self.assertEqual(self.base_server_manager.exit_flag, False, "stopped")
        connect_mock.send.assert_called_once_with(ANY)
        
        
    def test_admin_event_broken_class_name(self):
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock)
                        
        self.adminState.className = "AdminState.STATE_NOP"
        adminEvent = self.event_builder.build(EVENT_TYPES.ADMIN_STATE, self.adminState)        
        connect_mock = MagicMock(ConnectionLight)
        connect_mock.recv.return_value = adminEvent
        
        self.poller_manager_mock.poll.return_value = [self.base_server_manager.ADMIN_CONNECT_CLIENT]        
        self.base_server_manager.addConnection(self.base_server_manager.ADMIN_CONNECT_CLIENT, connect_mock)
        
        self.base_server_manager.poll()
        
        self.assertEqual(self.base_server_manager.exit_flag, False, "stopped")
        connect_mock.send.assert_called_once_with(ANY)
        
        
    def test_init_stat_fields_admin_connect(self):
        className = self.base_server_manager.__class__.__name__
        ready = AdminState(className, AdminState.STATE_READY)
        readyEvent = self.base_server_manager.eventBuilder.build(EVENT_TYPES.ADMIN_STATE_RESPONSE, ready)

        admin_connect_name = BaseServerManager.ADMIN_CONNECT_CLIENT
        self.assertTrue(self.base_server_manager.statFields[admin_connect_name + "_send_cnt"] == 1, "")
        self.assertTrue(self.base_server_manager.statFields[admin_connect_name + "_recv_cnt"] == 0, "")
        self.assertTrue(self.base_server_manager.statFields[admin_connect_name + "_send_bytes"] == sys.getsizeof(readyEvent), "")
        self.assertTrue(self.base_server_manager.statFields[admin_connect_name + "_recv_bytes"] == 0, "")
    
    
    def test_init_user_connection(self):
        fake_user_connect = None
        connect_name = "user_connect"
        self.base_server_manager.addConnection(connect_name, fake_user_connect)
        
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_send_cnt"] == 0, "")
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_recv_cnt"] == 0, "")
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_send_bytes"] == 0, "")
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_recv_bytes"] == 0, "")
        

    def test_stats_recv_several_msg(self):
        msg_size = sys.getsizeof(self.event)
        fake_user_connect = None
        connect_name = "user_connect"
        self.event.connect_name = connect_name
        self.base_server_manager.addConnection(connect_name, fake_user_connect)
        
        self.base_server_manager.process(self.event)
        self.base_server_manager.process(self.event)

        self.assertTrue(self.base_server_manager.statFields[connect_name + "_send_cnt"] == 0, "")
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_recv_cnt"] == 2, "")
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_send_bytes"] == 0, "")
        self.assertTrue(self.base_server_manager.statFields[connect_name + "_recv_bytes"] == 2 * msg_size, "")
        
        
    def test_stats_update_invalid_stat_key(self):
        self.event.connect_name = "bad_stat_name"
                
        self.base_server_manager.process(self.event)
        
                
    def test__admin_fetch_stat_data_all(self):        
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock)
                        
        adminStatData = AdminStatData("BaseServerManager")        
        adminStatEvent = self.event_builder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA, adminStatData)        
        connect_mock = MagicMock(ConnectionLight)
        connect_mock.recv.return_value = adminStatEvent
        
        self.poller_manager_mock.poll.return_value = [self.base_server_manager.ADMIN_CONNECT_CLIENT]        
        self.base_server_manager.addConnection(self.base_server_manager.ADMIN_CONNECT_CLIENT, connect_mock)

        expectAdminStatData = AdminStatData("BaseServerManager", self.base_server_manager.statFields)
        expect_event = self.event_builder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, expectAdminStatData)
        expect_event.uid = adminStatEvent.uid                         
        match_event = Matcher(matchStatEvents, expect_event)
                
        self.base_server_manager.poll()
        
        connect_mock.send.assert_called_once_with(match_event)
                                
                
    def test__admin_fetch_stat_data_some_fields(self):        
        connectLightBuilder_mock = MagicMock(ConnectionBuilderLight)
        self.base_server_manager = BaseServerManager(self.poller_manager_mock, conectionLightBuilder=connectLightBuilder_mock)
                        
        adminStatData = AdminStatData("BaseServerManager", dict({"Admin_recv_cnt":0, "WrongName":0}))        
        adminStatEvent = self.event_builder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA, adminStatData)        
        connect_mock = MagicMock(ConnectionLight)
        connect_mock.recv.return_value = adminStatEvent
        
        self.poller_manager_mock.poll.return_value = [self.base_server_manager.ADMIN_CONNECT_CLIENT]
        ##broken initial statistics        
        self.base_server_manager.addConnection(self.base_server_manager.ADMIN_CONNECT_CLIENT, connect_mock)

        expectAdminStatData = AdminStatData("BaseServerManager", dict({"Admin_recv_cnt":1, "WrongName":0}))
        expect_event = self.event_builder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, expectAdminStatData)
        expect_event.uid = adminStatEvent.uid                         
        match_event = Matcher(matchStatEvents, expect_event)
                
        self.base_server_manager.poll()
        
        connect_mock.send.assert_called_once_with(match_event)
                                