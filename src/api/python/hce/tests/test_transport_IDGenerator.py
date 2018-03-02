'''
Created on Feb 4, 2014

@author: igor
'''
import unittest
from transport.IDGenerator import IDGenerator
 
class TestIDGenerator(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.idGenerator = IDGenerator()
       
        
    def test_generate_correct_connection_id(self):
        expect_id = ["1", "2", "3", "4"]
        result = list()
        for _  in xrange(0, 4):
            result.append(self.idGenerator.get_connection_uid(type=1))
            
        self.assertEqual(expect_id, result, "generation connection ids is broken")