'''
Created on Apr 8, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
from transport.Event import Event
from transport.Event import EventBuilder  
from app.BaseServerManager import BaseServerManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dtm.Constants import EVENT_TYPES as EVENT, LOGGER_NAME 
import dtm.EventObjects
import unittest
import transport.Consts
import logging
import time

connectName = "TestBaseServerManagerConn"

FORMAT = '%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

class TestBaseServerManager(unittest.TestCase):

  '''
  def loggerInit(self):
    logHandler = logging.Handler()
    logging.setLoggerClass()
  '''   

  def setUp(self):
    self.servIndex = 1
    self.connectionBuilder = ConnectionBuilderLight()
    self.localConnectionClient = None
    self.localConnectionServer = None
    self.adminServerConnection = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)
    self.baseServerManager = BaseServerManager(conectionLightBuilder=self.connectionBuilder)
    self.localConnectionServer = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT, connectName)
    self.baseServerManager.addConnection(connectName, self.localConnectionServer)    
    self.baseServerManager.start()
    self.eventBuilder = EventBuilder()
    self.recvEvent = None
    self.event = None
    self.reply_event = None
    self.moduleName = self.baseServerManager.__class__.__name__
    self.localConnectionClient = self.connectionBuilder.build(transport.Consts.CLIENT_CONNECT, connectName)
    self.servIndex = self.servIndex + 1


  def tearDown(self):
    self.baseServerManager.exit_flag = True
    self.baseServerManager.join()
    for connection in self.baseServerManager.connections.values():
      connection.close()    
    self.adminServerConnection.close()
    self.localConnectionClient.close()
    time.sleep(1)


  def testOnAdminGetConfigVarsBad1(self):
    self.baseServerManager.configVars["var1"] = 100
    getConfigVars = dtm.EventObjects.AdminConfigVars("BadClassName")
    getConfigVars.fields["var1"] = None
    getConfigVars.fields["var2"] = None
    event = self.eventBuilder.build(EVENT.ADMIN_GET_CONFIG_VARS, getConfigVars)
    self.localConnectionClient.send(event)
    time.sleep(1)
    self.recvEvent = self.localConnectionClient.recv()
    self.assertTrue(len(self.recvEvent.eventObj.fields) == 2 , ">>> Bad fields len")
    self.assertTrue(self.recvEvent.eventObj.fields["var1"] == None, ">>> 1th elem not None")
    self.assertTrue(self.recvEvent.eventObj.fields["var2"] == None, ">>> 2th elem not None")
    
    
  def testOnAdminGetConfigVars(self):
    self.baseServerManager.configVars["var1"] = 100
    getConfigVars = dtm.EventObjects.AdminConfigVars(self.baseServerManager.__class__.__name__)
    getConfigVars.fields["var1"] = None
    getConfigVars.fields["var2"] = None
    event = self.eventBuilder.build(EVENT.ADMIN_GET_CONFIG_VARS, getConfigVars)
    self.localConnectionClient.send(event)
    time.sleep(1)
    self.recvEvent = self.localConnectionClient.recv()
    self.assertTrue(len(self.recvEvent.eventObj.fields) == 2 , ">>> Bad fields len")
    self.assertTrue(self.recvEvent.eventObj.fields["var1"] == 100, ">>> 1th elem not 100")
    self.assertTrue(self.recvEvent.eventObj.fields["var2"] == None, ">>> 2th elem not None")


  def testOnAdminSetConfigVarsBad1(self):
    self.baseServerManager.configVars["var1"] = 100
    getConfigVars = dtm.EventObjects.AdminConfigVars("BadClassName")
    getConfigVars.fields["var1"] = 55
    getConfigVars.fields["var2"] = 66
    event = self.eventBuilder.build(EVENT.ADMIN_SET_CONFIG_VARS, getConfigVars)
    self.localConnectionClient.send(event)
    time.sleep(1)
    self.recvEvent = self.localConnectionClient.recv()
    self.assertTrue(len(self.recvEvent.eventObj.fields) == 2 , ">>> Bad fields len")
    self.assertTrue(self.recvEvent.eventObj.fields["var1"] == 55, ">>> 1th elem not None")
    self.assertTrue(self.recvEvent.eventObj.fields["var2"] == 66, ">>> 2th elem not None")
    self.assertTrue(self.baseServerManager.configVars["var1"] == 100, ">>> var1 not change")



  def testOnAdminSetConfigVars(self):
    self.baseServerManager.configVars["var1"] = 100
    self.baseServerManager.configVars["var2"] = 100
    getConfigVars = dtm.EventObjects.AdminConfigVars(self.baseServerManager.__class__.__name__)
    getConfigVars.fields["var1"] = 55
    getConfigVars.fields["var2"] = "ASSA"
    getConfigVars.fields["var3"] = "DOOB"
    event = self.eventBuilder.build(EVENT.ADMIN_SET_CONFIG_VARS, getConfigVars)
    self.localConnectionClient.send(event)
    time.sleep(1)
    self.recvEvent = self.localConnectionClient.recv()
    self.assertTrue(len(self.recvEvent.eventObj.fields) == 3, ">>> Bad fields len")
    self.assertTrue(len(self.baseServerManager.configVars) == 3, ">>> Bad baseServerManager fields len")
    self.assertTrue(self.recvEvent.eventObj.fields["var1"] == 55, ">>> 1th elem not None")
    self.assertTrue(self.recvEvent.eventObj.fields["var2"] == None, ">>> 2th elem not None")
    self.assertTrue(self.recvEvent.eventObj.fields["var3"] == "DOOB", ">>> 2th elem not None")
    self.assertTrue(self.baseServerManager.configVars["var1"] == 55, ">>> var1 not change")
    self.assertTrue(self.baseServerManager.configVars["var2"] == 100, ">>> var1 not change")
    self.assertTrue(self.baseServerManager.configVars["var3"] == "DOOB", ">>> var1 not change")
    

if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()