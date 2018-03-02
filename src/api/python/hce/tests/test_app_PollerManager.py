'''
Created on Feb 26, 2014

@author: igor
'''
import unittest
import zmq
from mock import MagicMock
from transport.Connection import Connection, ConnectionTimeout
from app.PollerManager import PollerManager



class TestPollerManager(unittest.TestCase):


    def setUp(self):
        self.sock_mock = MagicMock(spec = zmq.Socket)
        self.poller_mock = MagicMock(spec = zmq.Poller)
        self.poller_manager = PollerManager(self.poller_mock)


    def test_add_conections(self):
        connection = Connection(self.sock_mock, self.poller_mock)
        self.poller_manager.add(connection, "sname")
        
        self.assertEqual(self.poller_manager.connections[self.sock_mock], "sname", "add is failed")
        
        
    def test_remove_conenction(self):
        connection = Connection(self.sock_mock, self.poller_mock)
        
        self.poller_manager.add(connection, "sname")
        self.poller_manager.remove(connection)

        with self.assertRaises(KeyError):
            list(self.poller_manager.connections[self.sock_mock])
            
    
    def test_timeout(self):
        poller_mock_cfg = {"poll.return_value": list()}
        self.poller_mock.configure_mock(**poller_mock_cfg)
        
        with self.assertRaises(ConnectionTimeout):
            list(self.poller_manager.poll(100))
            
            
    def test_return_names(self):         
        poller_mock_cfg = {"poll.return_value": [(self.sock_mock, zmq.POLLIN)]}
        self.poller_mock.configure_mock(**poller_mock_cfg)

        connection = Connection(self.sock_mock, self.poller_mock)        
        self.poller_manager.add(connection, "sname")
        
        expect_list = ["sname"]
        
        res = self.poller_manager.poll(100)
        
        self.assertEqual(expect_list, res, "poll is failed")


