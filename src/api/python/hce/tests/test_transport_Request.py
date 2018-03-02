'''
Created on Feb 5, 2014

@author: igor
'''
import unittest
from transport.Request import Request


class TestRequest(unittest.TestCase):


    def setUp(self):
        self.request = Request("1")

        
    def test_correct_accumulate_data(self):
        send_data = ["1", "part1", "part2"]
        self.request.add_data(send_data[1])
        self.request.add_data(send_data[2])
        
        self.assertEqual(self.request.get_body(), send_data, "accumulation is wrong")        