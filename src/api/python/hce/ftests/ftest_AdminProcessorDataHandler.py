'''
Created on Mar 10, 2014

@author: scorp
'''
from admin.Command import Command
from admin.Constants import ADMIN_HANDLER_TYPES as ADMIN_HANDLERS
from admin.Node import Node
from admin.NodeManager import NodeManager
from time import sleep
import admin.AdminExceptions as AdminExceptions
import unittest
import ftest_AdminConstants as F_CONSTANTS
import admin.Constants as CONSTANTS


class TestAdminProcessorDataHandler(unittest.TestCase):


  def setUp(self):
    self.nodeManager = NodeManager()


  def tearDown(self):
    pass

## Test method, creates request with 2 nodes and 4 commands
#  So really we have  8 requests/responses
  def testAdminProcessorDataHandler(self):
    nodes = [Node(F_CONSTANTS.TEST_LOCAL_HOST, 1120), Node(F_CONSTANTS.TEST_LOCAL_HOST, 2120)]
    commands = []
    params = ["param1", "param2"]
# Last param (10 value) is Command timeout, if it not specified, that we use timeout from Node    
    command = Command("PROPERTIES", params, ADMIN_HANDLERS.DATA_PROCESSOR_DATA)
    commands.append(command)    
    command = Command("ECHO", params, ADMIN_HANDLERS.ADMIN)
    commands.append(command)    
    command = Command("DRCE", params, ADMIN_HANDLERS.DATA_PROCESSOR_DATA)
    commands.append(command)
    command = Command("BAD_COMMAND", params, ADMIN_HANDLERS.ADMIN)
    commands.append(command)     

#    with self.assertRaises(AdminExceptions.AdminTimeoutException):
#      list(self.nodeManager.execute(commands, nodes))
      
    nodes = [Node(F_CONSTANTS.TEST_REAL_HOST), Node(F_CONSTANTS.TEST_REAL_HOST, 5530, 20)]
    self.nodeManager.execute(commands, nodes)
    print("Responses count = " + str(len(self.nodeManager.getResponses())))
    print("Responses Dict count = " + str(len(self.nodeManager.getResponsesDicts())))
    for response in self.nodeManager.getResponses():
      print(response[CONSTANTS.STRING_RESPONSE_MARKER].getBody())
      
    if len(self.nodeManager.getResponsesDicts()) >=5 and self.nodeManager.getResponsesDicts()[4] != None:
      localDict = self.nodeManager.getResponsesDicts()[4]
      print(localDict[CONSTANTS.RESPONSE_FIELDS_NAME])
      if localDict[CONSTANTS.RESPONSE_CODE_NAME] == "OK":
        print("fields count = " + str(len(localDict[CONSTANTS.RESPONSE_FIELDS_NAME])))
        print("\"name\" field value = " + localDict[CONSTANTS.RESPONSE_FIELDS_NAME]["name"])
    sleep(1)
    '''
    try:
      raise AdminExceptions.AdminTimeoutException("WWWWWW")
    except Exception, e:
      print(e.__doc__ + ":")
    '''

if __name__ == "__main__":
#import sys;sys.argv = ['', 'Test.testName']
  unittest.main()