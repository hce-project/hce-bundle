'''
Created on Mar 12, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ppath
from dtmc.DTMC import DTMC
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
    if hasattr(event.eventObj, "id"):
      self.id = event.eventObj.id
    else:
      self.id = None


  def poll(self, timeout):
    return 1


  def recv(self):
    eventObj = None
    retEventType = None
    retEvent = None
    eventBulder = transport.Event.EventBuilder()
    if self.eventType == EVENT_TYPES.NEW_TASK:
      retEventType = EVENT_TYPES.GENERAL_RESPONSE
      eventObj = dtm.EventObjects.GeneralResponse()
      eventObj.statuses.append("was_new")
    elif self.eventType == EVENT_TYPES.CHECK_TASK_STATE:
      retEventType = EVENT_TYPES.FETCH_EE_DATA_RESPONSE
      eventObj = dtm.EventObjects.EEResponseData(self.id)
    elif self.eventType == EVENT_TYPES.DELETE_TASK:
      retEventType = EVENT_TYPES.GENERAL_RESPONSE
      eventObj = dtm.EventObjects.GeneralResponse()
      eventObj.statuses.append("was_delete")
    elif self.eventType == EVENT_TYPES.FETCH_TASK_RESULTS:
      retEventType = EVENT_TYPES.FETCH_EE_DATA_RESPONSE
      eventObj = dtm.EventObjects.EEResponseData(self.id)
    retEvent = eventBulder.build(retEventType, eventObj)
    return retEvent


def connectionBuilderMockBuild(type, addr, networkType):
  return ConnectionStub()


# #Class TestDTMC, contains functional tests of DTMC module
#
class TestDTMC(unittest.TestCase):


  def setUp(self):
    self.dtmc = None
    self.connectionBuilderMock = MagicMock(spec=ConnectionBuilderLight)
    self.connectionBuilderMock.build.side_effect = connectionBuilderMockBuild


  def tearDown(self):
    pass


  def commonTestCode(self, args):
    self.dtmc = DTMC()
    self.dtmc.connectionBuilder = self.connectionBuilderMock
    DTMC.argv = args
    self.dtmc.setup()
    try:
      self.dtmc.run()
    except SystemExit as excp:
      print("\nEXIT CODE >>> " + str(excp.message))
    self.dtmc.close()


  def testFunctionalHELP(self):
    print("HELP TEST START >>> \n")
    self.commonTestCode(["-h"])


  def testFunctionalNEW(self):
    print("NEW TEST START >>> \n")
#    self.commonTestCode(["-t", "NEW", "-f", "./new_test.json", "--config", "./dtmc.ini"])
    self.commonTestCode(["-t", "NEW", "-f", "./jsons/dtmc_new_task_1_request.json", "--config", "./dtmc.ini"])


  def testFunctionalCHCECK(self):
    print("CHECK TEST START >>> \n")
#    self.commonTestCode(["-t", "CHECK", "-f", "./check_test.json", "--config", "./dtmc.ini"])
    self.commonTestCode(["-t", "CHECK", "-f", "./jsons/dtmc_check_1_request.json", "--config", "./dtmc.ini"])


  def testFunctionalTERMINATE(self):
    print("TERMINATE TEST START >>> \n")
#    self.commonTestCode(["-t", "TERMINATE", "-f", "./del_test.json", "--config", "./dtmc.ini"])
    self.commonTestCode(["-t", "TERMINATE", "-f", "./jsons/dtmc_delete_task_1_request.json",
                         "--config", "./dtmc.ini"])


  def testFunctionalGET(self):
    print("GET TEST START >>> \n")
#    self.commonTestCode(["-t", "GET", "-f", "./get_test.json", "--config", "./dtmc.ini"])
    self.commonTestCode(["-t", "GET", "-f", "./jsons/dtmc_fetch_task_1_request.json", "--config", "./dtmc.ini"])


  def testFunctionalSTATUS(self):
    print("STATUS TEST START >>> \n")
    self.commonTestCode(["-t", "STATUS", "-f", "./jsons/dtmc_status_ok.json", "--config", "./dtmc.ini"])


  def testFunctionalSTATUSBad(self):
    print("STATUSBad TEST START >>> \n")
    self.commonTestCode(["-t", "STATUS", "-f", "./jsons/dtmc_status_bad.json", "--config", "./dtmc.ini"])


  def testFunctionalCLEANUP(self):
    print("CLEANUP TEST START >>> \n")
    self.commonTestCode(["-t", "CLEANUP", "-f", "./jsons/dtmc_cleanup_ok.json", "--config", "./dtmc.ini"])


  def testFunctionalCLEANUPBad(self):
    print("CLEANUPBad TEST START >>> \n")
    self.commonTestCode(["-t", "CLEANUP", "-f", "./jsons/dtmc_cleanup_bad.json", "--config", "./dtmc.ini"])


if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']

  unittest.main()
