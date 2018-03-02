'''
Created on Mar 27, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dtma.DTMA import DTMA
from mock import MagicMock
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dtm.Constants import EVENT_TYPES as EVENT_TYPES
import unittest
import dtm.EventObjects
import transport.Event


class ConnectionStub(object):


  def __init__(self):
    self.eventType = None


  def send(self, event):
    self.eventType = event.eventType
    '''
    if event.eventType == EVENT_TYPES.ADMIN_FETCH_STAT_DATA:
      print("-----------------------------------")
      print(event.eventObj.className)
      print(event.eventObj.fields)
    '''


  def poll(self, timeout):
    return 1


  def recv(self):
    eventObj = None
    retEventType = None
    retEvent = None
    eventBulder = transport.Event.EventBuilder()
    if self.eventType == EVENT_TYPES.ADMIN_FETCH_STAT_DATA:
      retEventType = EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE
      eventObj = dtm.EventObjects.AdminStatData("")
    elif self.eventType == EVENT_TYPES.ADMIN_SET_CONFIG_VARS:
      retEventType = EVENT_TYPES.ADMIN_SET_CONFIG_VARS_RESPONSE
      eventObj = dtm.EventObjects.AdminConfigVars("")
    elif self.eventType == EVENT_TYPES.ADMIN_GET_CONFIG_VARS:
      retEventType = EVENT_TYPES.ADMIN_GET_CONFIG_VARS_RESPONSE
      eventObj = dtm.EventObjects.AdminConfigVars("")
    elif self.eventType == EVENT_TYPES.ADMIN_STATE:
      retEventType = EVENT_TYPES.ADMIN_STATE_RESPONSE
      eventObj = dtm.EventObjects.GeneralResponse()
    retEvent = eventBulder.build(retEventType, eventObj)
    return retEvent


def connectionBuilderMockBuild(type, addr, networkType):
  return ConnectionStub()


##Class TestDTMA, contains functional tests of DTMA module
#
class TestDTMA(unittest.TestCase):


  def __init__(self, methodName='runTest'):
    unittest.TestCase.__init__(self, methodName)
    self.dtmc = None
    self.connectionBuilderMock = None


  def setUp(self):
    self.dtmc = None
    self.connectionBuilderMock = MagicMock(spec=ConnectionBuilderLight)
    self.connectionBuilderMock.build.side_effect = connectionBuilderMockBuild


  def tearDown(self):
    pass


  def commonTestCode(self, args, isZerro):
    exitCode = None
    self.dtma = DTMA()
    self.dtma.connectionBuilder = self.connectionBuilderMock
    DTMA.argv = args
    self.dtma.setup()
    try:
      self.dtma.run()
    except SystemExit as excp:
      print("\nEXIT CODE >>> " + str(excp.message))
      exitCode = excp.message
    self.dtma.close()
    if isZerro:
      self.assertTrue(exitCode == 0, ">>> Error! Exit code != 0")
    else:
      self.assertTrue(exitCode != 0, ">>> Error! Exit code == 0")


  def testFunctionalHELP(self):
    print("HELP TEST START >>> \n")
    self.commonTestCode(["-h"], True)


  def testFunctionalSTATBadConfig(self):
    print("testFunctionalSTATBadConfig TEST START >>> \n")
    self.commonTestCode(["--cmd", "STAT", "--config", "./bad"], False)


  def testFunctionalSTATBad1(self):
    print("testFunctionalSTATBad1 TEST START >>> \n")
    self.commonTestCode(["--cmd", "STAT", "--config", "./dtma.ini"], False)


  def testFunctionalSTAT(self):
    print("testFunctionalSTAT TEST START >>> \n")
#    self.commonTestCode(["--cmd", "STAT", "--fields", "adda1", "--classes", "cl1,cl2", "--config", "./dtma.ini"])
#    "--fields", "Adm:,adm2:33,adm4",
    self.commonTestCode(["--cmd", "STAT", "--classes", 
                         "TasksManager,ExecutionEnvironmentManager ", "--config", "./dtma.ini"], True)


  def testFunctionalSETBad(self):
    print("testFunctionalSETBad TEST START >>> \n")
    self.commonTestCode(["--cmd", "SET", "--fields", "cl1,cl2","--classes", "cl1,cl2", "--config", "./dtma.ini"], False)


  def testFunctionalSET(self):
    print("testFunctionalSET TEST START >>> \n")
    self.commonTestCode(["--cmd", "SET", "--fields", "cl1:cl2,cl4:", "--classes", "cl1,cl2",
                         "--config", "./dtma.ini"], True)


  def testFunctionalGETBad(self):
    print("testFunctionalGETBad TEST START >>> \n")
    self.commonTestCode(["--cmd", "GET", "--fields", "", "--classes", "cl1,cl2", "--config", "./dtma.ini"], False)


  def testFunctionalGET(self):
    print("testFunctionalGET TEST START >>> \n")
    self.commonTestCode(["--cmd", "GET", "--fields", "any", "--classes", "cl1,cl2", "--config", "./dtma.ini"], True)


  def testFunctionalSTOPBad(self):
    print("testFunctionalSTOPBad TEST START >>> \n")
    self.commonTestCode(["--cmd", "STOP", "--classes", "", "--config", "./dtma.ini"], False)


  def testFunctionalSTOP(self):
    print("testFunctionalSTOP TEST START >>> \n")
    self.commonTestCode(["--cmd", "STOP","--classes", "cl1,cl2", "--config", "./dtma.ini"], True)
 

if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  
  unittest.main()