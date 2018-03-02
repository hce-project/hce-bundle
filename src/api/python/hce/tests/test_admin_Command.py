'''
Created on Feb 17, 2014

@author: scorp
'''
##unit-tests of Command class 

import unittest
from Command import Command

standartString = "ECHO\t22@55@44"


class TestCommand(unittest.TestCase):


  def setUp(self):
    self.command = None


  def tearDown(self):
    pass


  def testConstructorSettings(self):
    self.command = Command()
    self.assertEqual(type(self.command.getParams()), type([]), ">> param field type not list")    
    self.assertEqual(len(self.command.getParams()), 0, ">> param field size != 0")


  def testGenerateBody(self):
    params = ["22", 55, 44]
    commandName = "ECHO"
    self.command = Command(commandName, params)
    ret = self.command.generateBody()
    self.assertEqual(ret, standartString, ">> wrong ret")

        
if __name__ == "__main__":
# import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
