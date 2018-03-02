'''
Created on Feb 14, 2014

@author: scorp
'''
##unit-tests of Node class 

import unittest
from Node import Node
import test_Constants
import time


class TestNode(unittest.TestCase):
    
  def setUp(self):
    self.node = None


  def tearDown(self):
    pass


  def testElapsedFromConsturctorTimeout(self):
    self.node = Node("localhost", 0, test_Constants.TEST_TIMEOUT)
    elapsed = self.node.getElapsedTime()
    self.assertTrue(elapsed >= 0, ">>> Elapsed 1 failed")    
    time.sleep(test_Constants.TEST_TIMEOUT / 1000)
        
    elapsed = self.node.getElapsedTime()
    self.assertTrue(elapsed >= test_Constants.TEST_TIMEOUT, ">>> Elapsed 2 failed")        
        
        
if __name__ == "__main__":
# import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
