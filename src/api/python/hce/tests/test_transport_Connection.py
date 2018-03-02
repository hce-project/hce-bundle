'''
Created on Feb 4, 2014

@author: igor
'''
import unittest
import zmq
from transport.Connection import Connection
from transport.Connection import ConnectionTimeout
#from transport.Connection import ConnectionParams 
from transport.Request import Request


class TestConnection(unittest.TestCase):


    def setUp(self):        
        self.context = zmq.Context()
        self.connect_pair = self.create_bound_pair()
        self.poller = zmq.Poller()
        self.connection = Connection(self.connect_pair[0], self.poller)


    def test_send(self):
        request = Request("1")
        request.add_data("Hello people!")
        expect_msg = [b"1", b"Hello people!"]
        
        self.connection.send(request)
        recv_message = self.connect_pair[1].recv_multipart()
                
        self.assertEqual(expect_msg, recv_message, "connection send doesn't work")


    def test_recv_message(self):
        message = ["sock_identity", "232", "New message"]
        self.connect_pair[1].send_multipart(message)
        response = self.connection.recv(1000)
                        
        self.assertEqual(message[0], response.get_uid(), "connection recv is failed")
        self.assertEqual(message[1], response.get_body(), "connection recv is failed")
        
                        
    def test_recv_message_timeout_exception(self):
        with self.assertRaises(ConnectionTimeout):
            list(self.connection.recv(250))


    def test_alive_socket_check(self):
        self.assertTrue(self.connection.is_closed() == False, "sock must be valid")

    
    def test_disconnect(self):
        self.connection.close()
        self.assertTrue(self.connection.is_closed() == True, "close doesn't work")


    def create_bound_pair(self, type1=zmq.PAIR, type2=zmq.PAIR, interface='tcp://127.0.0.1'):
        """Create a bound socket pair using a random port."""
        s1 = self.context.socket(type1)
        s1.setsockopt(zmq.LINGER, 0)
        port = s1.bind_to_random_port(interface)
        s2 = self.context.socket(type2)
        s2.setsockopt(zmq.LINGER, 0)
        s2.connect('%s:%s' % (interface, port))
        return s2, s1