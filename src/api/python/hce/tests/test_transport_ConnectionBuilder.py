'''
Created on Feb 4, 2014

@author: igor
'''

import unittest
import zmq

from mock import Mock
from mock import MagicMock, ANY
from mock import call

from transport.ConnectionBuilder import ConnectionBuilder 
from transport.IDGenerator import IDGenerator
from transport.Connection import ConnectionParams
from transport.Consts import ADMIN_CONNECT_TYPE


class TestConnectionBuilder(unittest.TestCase):


    def setUp(self):
        self.connect_params = ConnectionParams("10.0.0.1", 1024)
        self.id_generator = IDGenerator()
        
        
    def test_correct_init_admin_connection(self):
        ctx_mock = Mock(spec=zmq.Context)
        socket_mock = MagicMock(spec=zmq.Socket)
        
        ctx_mock_cfg = {"socket.return_value":socket_mock}
        ctx_mock.configure_mock(**ctx_mock_cfg)
        
        socket_expect_calls = [call.setsockopt(zmq.IDENTITY, ANY),
                                             call.connect("tcp://10.0.0.1:1024")]
                                                     
        connection_factory = ConnectionBuilder(self.id_generator)
        connection_factory.zmq_context = ctx_mock
        
        admin_connection = connection_factory.build(ADMIN_CONNECT_TYPE, self.connect_params) 
        
        self.assertIn(socket_expect_calls, socket_mock.mock_calls, 
                                                                  "admin connect is wrong initialized")