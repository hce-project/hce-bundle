'''
Created on Feb 28, 2014

@author: igor
'''
import unittest
from mock import MagicMock, call
import zmq
from transport.ConnectionBuilderLight import ConnectionBuilderLight
import transport.Consts as consts


class TestConnectionBuilderLight(unittest.TestCase):


    def setUp(self):
        self.zmq_context_mock = MagicMock(spec = zmq.Context)
        self.zmq_sock_mock = MagicMock(spec = zmq.Socket)
        self.zmq_context_mock.socket.return_value = self.zmq_sock_mock
        self.connect_builder = ConnectionBuilderLight()
        self.original_zmq_context = self.connect_builder.zmq_context
        self.connect_builder.zmq_context = self.zmq_context_mock
        
        
    def tearDown(self): 
        self.connect_builder.zmq_context = self.original_zmq_context 
    

    def test_create_client_connect(self):
        connect_endpoint = "server"
        expect_calls = [call.connect("inproc://server")]
        
        self.connect_builder.build(consts.CLIENT_CONNECT, connect_endpoint)
                                
        self.assertEqual(self.zmq_sock_mock.mock_calls, expect_calls, "")


    def test_create_server_connect(self):
        connect_endpoint = "server"
        expect_calls = [call.bind("inproc://server")]
        
        self.connect_builder.build(consts.SERVER_CONNECT, connect_endpoint)
                                
        self.assertEqual(self.zmq_sock_mock.mock_calls, expect_calls, "")
        
        
    def test_create_tcp_server_connect(self):
        connect_endpoint = "10.10.1.1:1234"
        expect_calls = [call.bind("tcp://10.10.1.1:1234")]
        
        self.connect_builder.build(consts.SERVER_CONNECT, connect_endpoint, consts.TCP_TYPE)
        
        self.assertEqual(self.zmq_sock_mock.mock_calls, expect_calls, "")

