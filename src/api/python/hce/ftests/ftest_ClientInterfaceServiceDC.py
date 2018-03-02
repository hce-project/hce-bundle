'''
Created on Apr 9, 2014

@package: dc
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
from transport.Event import Event
from transport.Event import EventBuilder
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from app.BaseServerManager import BaseServerManager
from dc.ClientInterfaceService import ClientInterfaceService
from dc.Constants import EVENT_TYPES, LOGGER_NAME
import dc.EventObjects
import dtm.EventObjects
import ConfigParser
import transport.Consts
import unittest
import logging
import time


logger = logging.getLogger(__name__)

class TestClientInterfaceServiceDC(unittest.TestCase):


  def setUp(self):
    self.servIndex = 1
    self.connectionBuilder = ConnectionBuilderLight()
    self.localConnectionDCC = None
    self.localConnectionURLManager = None
    self.localConnectionSitesManager = None
    self.adminServerConnection = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)
    self.config = ConfigParser.ConfigParser()
    self.config.read("./dc.ini")
    self.connectionInitServers()
    self.clientInterfaceService = ClientInterfaceService(self.config, self.connectionBuilder)
    self.clientInterfaceService.start()
    self.eventBuilder = EventBuilder()
    self.recvEvent = None
    self.event = None
    self.reply_event = None
    self.connectionInitClients()


  def connectionInitClients(self):
    try:
      serverHost = self.config.get(ClientInterfaceService.CONFIG_SECTION, ClientInterfaceService.CONFIG_SERVER_HOST)
      serverPort = self.config.get(ClientInterfaceService.CONFIG_SECTION, ClientInterfaceService.CONFIG_SERVER_PORT)
      server = serverHost + ":" + str(serverPort)
      
      self.localConnectionDCC = self.connectionBuilder.build(transport.Consts.CLIENT_CONNECT, \
                                                             server, transport.Consts.TCP_TYPE)
      self.servIndex = self.servIndex + 1
    except ConfigParser.NoSectionError:
      logger.error(">>> TasksDataManager can't read config - Section Error")
    except ConfigParser.NoOptionError:
      logger.error(">>> TasksDataManager can't read config - Option Error")


  def connectionInitServers(self):
    try:
      URLManager = self.config.get(ClientInterfaceService.CONFIG_SECTION, ClientInterfaceService.CONFIG_URL_MANAGER)
      sitesManager = self.config.get(ClientInterfaceService.CONFIG_SECTION, ClientInterfaceService.CONFIG_SITES_MANAGER)
      
      self.localConnectionURLManager = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT, URLManager)
      self.localConnectionSitesManager = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT, sitesManager)
      self.servIndex = self.servIndex + 1
    except ConfigParser.NoSectionError:
      logger.error(">>> TasksDataManager can't read config - Section Error")
    except ConfigParser.NoOptionError:
      logger.error(">>> TasksDataManager can't read config - Option Error")


  def tearDown(self):
    self.clientInterfaceService.exit_flag = True
    self.clientInterfaceService.join()
    for connection in self.clientInterfaceService.connections.values():
      connection.close()    
    self.adminServerConnection.close()
    self.localConnectionDCC.close()
    self.localConnectionURLManager.close()
    self.localConnectionSitesManager.close()
    time.sleep(3)


  def commonTestTimeout(self, eventObj, eventType, excptStr):
    siteEvent = self.eventBuilder.build(eventType, eventObj)
    self.localConnectionDCC.send(siteEvent)
    if self.localConnectionDCC.poll(3000) == 0:
      self.assertTrue(True, ">>> " + excptStr + "Was timeout")
    else:
      self.localConnectionDCC.recv()    


  def commonTest(self, eventObject, eventObjectResponse, eventType, eventTypeResponse, excptStr):
    event = self.eventBuilder.build(eventType, eventObject)
    responseEvent = self.eventBuilder.build(eventTypeResponse, eventObjectResponse)
    responseEvent.uid = event.uid
    self.localConnectionDCC.send(event)
    time.sleep(1)
    self.clientInterfaceService.onDCClientRoute(responseEvent)
    if self.localConnectionDCC.poll(3000) == 0:
      self.assertTrue(False, ">>> " + excptStr + " Was timeout")
    else:
      ret = self.localConnectionDCC.recv()
      if ret.eventType != eventTypeResponse:
        self.assertTrue(False, ">>> " + excptStr + " Bad ret event type")


  def testNewSiteTimeout(self):
    newSiteObj = dc.EventObjects.Site("intel.com")
    self.commonTestTimeout(newSiteObj, EVENT_TYPES.SITE_NEW, "[testNewSiteTimeout]")


  def testUpdateSiteTimeout(self):
    updateSiteObj = dc.EventObjects.SiteUpdate(1000)
    self.commonTestTimeout(updateSiteObj, EVENT_TYPES.SITE_UPDATE, "[testUpdateSiteTimeout]")


  def testStatusSiteTimeout(self):
    statusSiteObj = dc.EventObjects.SiteStatus(1000)
    self.commonTestTimeout(statusSiteObj, EVENT_TYPES.SITE_STATUS, "[testStatusSiteTimeout]")


  def testDeleteSiteTimeout(self):
    deleteSiteObj = dc.EventObjects.SiteDelete(1000)
    self.commonTestTimeout(deleteSiteObj, EVENT_TYPES.SITE_DELETE, "[testDeleteSiteTimeout]")


  def testCleanupSiteTimeout(self):
    cleanupSiteObj = dc.EventObjects.SiteCleanup(1000)
    self.commonTestTimeout(cleanupSiteObj, EVENT_TYPES.SITE_CLEANUP, "[testCleanupSiteTimeout]")


  def testNewURLTimeout(self):
    newURLObj = dc.EventObjects.URL(1000, "intel.com")
    self.commonTestTimeout(newURLObj, EVENT_TYPES.URL_NEW, "[testNewURLTimeout]")


  def testUpdateURLTimeout(self):
    updateURLObj = []
    updateURLObj.append(dc.EventObjects.URLUpdate(0, "intel.com"))
    self.commonTestTimeout(updateURLObj, EVENT_TYPES.URL_UPDATE, "[testUpdateURLTimeout]")


  def testStatusURLTimeout(self):
    statusURLObj = []
    statusURLObj.append(dc.EventObjects.URLStatus(1000, "intel.com"))
    self.commonTestTimeout(statusURLObj, EVENT_TYPES.URL_STATUS, "[testStatusURLTimeout]")


  def testDeleteURLTimeout(self):
    deleteURLObj = []
    deleteURLObj.append(dc.EventObjects.URLDelete(1, "intel.com"))
    self.commonTestTimeout(deleteURLObj, EVENT_TYPES.URL_DELETE, "[testDeleteURLTimeout]")


  def testCleanupURLTimeout(self):
    cleanupURLObj = []
    cleanupURLObj.append(dc.EventObjects.URLCleanup(1, "intel.com"))
    self.commonTestTimeout(cleanupURLObj, EVENT_TYPES.URL_CLEANUP, "[testCleanupURLTimeout]")


  def testFetchURLTimeout(self):
    fetchURLObj = dc.EventObjects.URLFetch()
    self.commonTestTimeout(fetchURLObj, EVENT_TYPES.URL_FETCH, "[testFetchURLTimeout]")


  def testContentURLTimeout(self):
    contentURLObj = []
    contentURLObj.append(dc.EventObjects.URLContentRequest(1, "intel.com"))
    self.commonTestTimeout(contentURLObj, EVENT_TYPES.URL_CONTENT, "[testContentURLTimeout]")


  def testNewSite(self):
    newSiteObj = dc.EventObjects.Site("intel.com")
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(newSiteObj, generalResponse, EVENT_TYPES.SITE_NEW, EVENT_TYPES.SITE_NEW_RESPONSE, 
                    "[testNewSiteTimeout]")


  def testUpdateSite(self):
    updateSiteObj = dc.EventObjects.SiteUpdate(1000)
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(updateSiteObj, generalResponse, EVENT_TYPES.SITE_UPDATE, EVENT_TYPES.SITE_UPDATE_RESPONSE,
                    "[testUpdateSiteTimeout]")


  def testStatusSite(self):
    statusSiteObj = dc.EventObjects.SiteStatus(1000)
    siteResponse = dc.EventObjects.Site("ibmn.com")
    self.commonTest(statusSiteObj, siteResponse, EVENT_TYPES.SITE_STATUS, EVENT_TYPES.SITE_STATUS_RESPONSE,
                    "[testStatusSiteTimeout]")


  def testDeleteSite(self):
    deleteSiteObj = dc.EventObjects.SiteDelete(1000)
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(deleteSiteObj, generalResponse, EVENT_TYPES.SITE_DELETE, EVENT_TYPES.SITE_DELETE_RESPONSE,
                    "[testDeleteSiteTimeout]")


  def testCleanupSite(self):
    cleanupSiteObj = dc.EventObjects.SiteCleanup(1000)
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(cleanupSiteObj, generalResponse, EVENT_TYPES.SITE_CLEANUP, EVENT_TYPES.SITE_CLEANUP_RESPONSE,
                    "[testCleanupSiteTimeout]")


  def testNewURL(self):
    newURLObj = dc.EventObjects.URL(1000, "intel.com")
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(newURLObj, generalResponse, EVENT_TYPES.URL_NEW, EVENT_TYPES.URL_NEW_RESPONSE, 
                    "[testNewURLTimeout]")


  def testUpdateURL(self):
    updateURLObj = []
    updateURLObj.append(dc.EventObjects.URLUpdate(2, "intel.com"))
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(updateURLObj, generalResponse, EVENT_TYPES.URL_UPDATE, EVENT_TYPES.URL_UPDATE_RESPONSE,
                    "[testUpdateURLTimeout]")


  def testStatusURL(self):
    statusURLObj = []
    statusURLObj.append(dc.EventObjects.URLStatus(1000, "intel.com"))
    urlResponse = []
    urlResponse.append(dc.EventObjects.URL(1000, "intel.com"))
    self.commonTest(statusURLObj, urlResponse, EVENT_TYPES.URL_STATUS, EVENT_TYPES.URL_STATUS_RESPONSE,
                    "[testStatusURLTimeout]")


  def testDeleteURL(self):
    deleteURLObj = []
    deleteURLObj.append(dc.EventObjects.URLDelete(1, "intel.com"))
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(deleteURLObj, generalResponse, EVENT_TYPES.URL_DELETE, EVENT_TYPES.URL_DELETE_RESPONSE,
                    "[testDeleteURLTimeout]")


  def testCleanupURL(self):
    cleanupURLObj = []
    cleanupURLObj.append(dc.EventObjects.URLCleanup(1, "intel.com"))
    generalResponse = dtm.EventObjects.GeneralResponse()
    self.commonTest(cleanupURLObj, generalResponse, EVENT_TYPES.URL_CLEANUP, EVENT_TYPES.URL_CLEANUP_RESPONSE,
                    "[testCleanupURLTimeout]")


  def testFetchURL(self):
    fetchURLObj = dc.EventObjects.URLFetch()
    urlsResponse = []
    urlsResponse.append(dc.EventObjects.URL(1000, "intel.com"))
    self.commonTest(fetchURLObj, urlsResponse, EVENT_TYPES.URL_FETCH, EVENT_TYPES.URL_FETCH_RESPONSE,
                    "[testFetchURLTimeout]")


  def testContentURL(self):
    contentURLObj = []
    contentURLObj.append(dc.EventObjects.URLContentRequest(1, "intel.com"))
    contentResponse = []
    contentResponse.append(dc.EventObjects.URLContentResponse(1, "intel.com"))
    self.commonTest(contentURLObj, contentResponse, EVENT_TYPES.URL_CONTENT, EVENT_TYPES.URL_CONTENT_RESPONSE,
                    "[testContentURLTimeout]")


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()