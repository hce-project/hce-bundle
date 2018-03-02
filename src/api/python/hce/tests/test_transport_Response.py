'''
Created on Feb 5, 2014

@author: igor
'''
import unittest
from transport.Response import Response
from transport.Response import ResponseFormatErr

 

class TestResponse(unittest.TestCase):


    def test_raise_protocol_exception_when_no_data(self):
        bad_msg = list()
        with self.assertRaises(ResponseFormatErr):
            list(Response(bad_msg))
        

    def test_raise_protocol_exception_too_less_data(self):
        bad_msg = ["id"]
        with self.assertRaises(ResponseFormatErr):
            list(Response(bad_msg))
        
    
    def test_parse_valid_msg(self):
        msg = ["id", "body"]
        response = Response(msg)       
        self.assertEqual(response.get_uid(), "id", "doesn't correct parse uid")
        self.assertEqual(response.get_body(), "body", "doesn't correct parse body")
