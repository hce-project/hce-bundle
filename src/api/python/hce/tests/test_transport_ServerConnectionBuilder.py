'''
Created on Feb 25, 2014

@author: igor
'''

import unittest
from mock import MagicMock, call
import zmq
from transport.ServerConnectionBuilder import ServerConnectionBuilder
from transport.Connection import ConnectionParams


class TestServerConnectionBuilder(unittest.TestCase):


    def test_build_correct_connection(self):
        ctx_mock = MagicMock(spec=zmq.Context)
        socket_mock = MagicMock(spec=zmq.Socket)
        
        ctx_mock_cfg = {"socket.return_value":socket_mock}
        ctx_mock.configure_mock(**ctx_mock_cfg)
        
        socket_expect_calls = [call.bind("tcp://10.0.0.1:1024")]
                                             
        connect_params = ConnectionParams("tcp://10.0.0.1", 1024)
        server_connect_builder = ServerConnectionBuilder()
        
        server_connect_builder.zmq_context = ctx_mock
        
        server_connect = server_connect_builder.build(connect_params) 
        
        self.assertIn(socket_expect_calls, socket_mock.mock_calls, 
                                                             "server connect is wrong initialized")