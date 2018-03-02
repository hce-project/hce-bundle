'''
Created on Feb 28, 2014

@author: igor
'''
import unittest
from mock import MagicMock 
import zmq
from transport.ConnectionLight import ConnectionLight, TransportInternalErr
from transport.ConnectionBuilderLight import ConnectionBuilderLight
import transport.Consts as consts 


class TestConnectionLight(unittest.TestCase):


    def setUp(self):
        self.zmq_sock_mock = MagicMock(spec = zmq.Socket)
        self.zmq_sock_mock.send_pyobj.side_effect = zmq.ZMQError("boom")        


    def test_raise_send_enternal_error(self):
        connection = ConnectionLight(self.zmq_sock_mock, consts.CLIENT_CONNECT)
        self.zmq_sock_mock.send_pyobj.side_effect = zmq.ZMQError("boom")
                
        with self.assertRaises(TransportInternalErr):
            list(connection.send("python object"))


    def test_raise_recv_enternal_error(self):
        connection = ConnectionLight(self.zmq_sock_mock, consts.CLIENT_CONNECT)
        self.zmq_sock_mock.recv_pyobj.side_effect = zmq.ZMQError("boom")
                
        with self.assertRaises(TransportInternalErr):
            list(connection.recv())
            
            
    def test_poll_no_event(self):
        connectionBuilder = ConnectionBuilderLight()
        
        client_connect = connectionBuilder.build(consts.CLIENT_CONNECT, "127.0.0.1:8292", consts.TCP_TYPE)
                        
        timeout=500
        ret_val = client_connect.poll(timeout)
                
        self.assertEqual(ret_val, 0, "There are events!!!!!!!")
        client_connect.close()
        