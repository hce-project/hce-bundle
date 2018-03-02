'''
Created on Apr 14, 2014

@package: dc
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import ppath

from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dc.Constants import EVENT_TYPES as EVENT_TYPES
from dcc.DCC import DCC
from mock import MagicMock
try:
  import cPickle as pickle
except ImportError:
  import pickle
import unittest
import dc.EventObjects
import transport.Event
import dc.Constants

fName = None

class ConnectionStub(object):


  def __init__(self):
    self.eventType = None
    self.id = 0
    self.event = None


  def send(self, event):
    global fName
    self.eventType = event.eventType
    self.event = event
    if hasattr(event.eventObj, "id"):
      self.id = event.eventObj.id
    else:
      self.id = None
    if fName != None:
      drceSave = dc.Constants.DRCESyncTasksCover(self.eventType, event.eventObj)
      pickleStr = pickle.dumps(drceSave)
      f = open(fName, "w")
      f.write(pickleStr)
      f.close()
      if event.cookie != None:
        print(">>> Event.cookie = %s" % event.cookie)


  def poll(self, timeout):
    return 1


  def recv(self):
    eventObj = None
    retEventType = None
    eventBulder = transport.Event.EventBuilder()
    if self.eventType >= EVENT_TYPES.SITE_NEW and self.eventType <= EVENT_TYPES.URL_PURGE:
      retEventType = self.eventType + (EVENT_TYPES.SITE_NEW_RESPONSE - EVENT_TYPES.SITE_NEW)
    eventObj = dc.EventObjects.ClientResponse([])
    eventObj.itemsList.append(dc.EventObjects.ClientResponseItem(None))
    eventObj.itemsList.append(dc.EventObjects.ClientResponseItem(None))
    eventObj.itemsList[0].host = "host1"
    eventObj.itemsList[1].host = "host2"
    return eventBulder.build(retEventType, eventObj)


def connectionBuilderMockBuild(type, addr, networkType):
  return ConnectionStub()


class TestDCC(unittest.TestCase):

  def setUp(self):
    self.dtmc = None
    self.connectionBuilderMock = MagicMock(spec=ConnectionBuilderLight)
    self.connectionBuilderMock.build.side_effect = connectionBuilderMockBuild


  def tearDown(self):
    pass


  def commonTestCode(self, args, isSave):
    self.dcc = DCC()
    self.dcc.connectionBuilder = self.connectionBuilderMock
    DCC.argv = args
    self.dcc.setup()
    try:
      self.dcc.run()
    except SystemExit as excp:
      print("\nEXIT CODE >>> " + str(excp.message))
    self.dcc.close()

  '''
  def testFunctionalHELP(self):
    global fName
    print("HELP TEST START >>> \n")
    self.commonTestCode(["-h"], False)


  def testFunctionalSiteNewBad1(self):
    global fName
    fName = "./save_pic/dcc_site_new_bad1.json"
    print("SITE NEW BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_bad1.json", "--config", "./dcc.ini"], False)


  def testFunctionalSiteNewBad2(self):
    global fName
    fName = "./save_pic/dcc_site_new_bad2.json"
    print("SITE NEW BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_bad2.json", "--config", "./dcc.ini"], False)


  def testFunctionalSiteNewBad3(self):
    global fName
    fName = "./save_pic/dcc_site_new_bad3.json"
    print("SITE NEW BAD3 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_bad3.json", "--config", "./dcc.ini"], False)
  '''

  def testFunctionalSiteNewOk(self):
    global fName
    fName = "./save_pic/dcc_site_new_ok.json"
    print("SITE NEW OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_ok.json", "--config", "./dcc.ini"], True)

  '''
  def testFunctionalSiteNewOk1(self):
    global fName
    fName = "./save_pic/dcc_site_new_ok_1.json"
    print("SITE NEW OK 1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_ok_1.json", "--config", "./dcc.ini"], True)
    

  def testFunctionalSiteNewOk2(self):
    global fName
    fName = "./save_pic/dcc_site_new_ok_2.json"
    print("SITE NEW OK 2 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_ok_2.json", "--config", "./dcc.ini"], True)


  def testFunctionalSiteNewOk3(self):
    global fName
    fName = "./save_pic/dcc_site_new_ok_3.json"
    print("SITE NEW OK 3 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_ok_3.json", "--config", "./dcc.ini"], True)


  def testFunctionalSiteUpdateBad1(self):
    global fName
    fName = "./save_pic/dcc_site_update_bad1.json"
    print("SITE UPDATE BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_UPDATE", "-f", "./jsons/dcc_site_update_bad1.json", "--config", "./dcc.ini"], 
                        False)
    
    
  def testFunctionalSiteUpdateBad2(self):
    global fName
    fName = "./save_pic/dcc_site_update_bad2.json"
    print("SITE UPDATE BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_UPDATE", "-f", "./jsons/dcc_site_update_bad2.json", "--config", "./dcc.ini"], 
                        False)

    
  def testFunctionalSiteUpdateBad3(self):
    global fName
    fName = "./save_pic/dcc_site_update_bad3.json"
    print("SITE UPDATE BAD3 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_UPDATE", "-f", "./jsons/dcc_site_update_bad3.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalSiteUpdateOk(self):
    global fName
    fName = "./save_pic/dcc_site_update_ok.json"
    print("SITE UPDATE OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_UPDATE", "-f", "./jsons/dcc_site_update_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalSiteUpdateOk1(self):
    global fName
    fName = "./save_pic/dcc_site_update_ok_1.json"
    print("SITE UPDATE OK1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_UPDATE", "-f", "./jsons/dcc_site_update_ok_1.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalSiteStatusBad1(self):
    global fName
    fName = "./save_pic/dcc_site_status_bad1.json"
    print("SITE STATUS BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_STATUS", "-f", "./jsons/dcc_site_status_bad1.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalSiteStatusBad2(self):
    global fName
    fName = "./save_pic/dcc_site_status_bad2.json"
    print("SITE STATUS BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_STATUS", "-f", "./jsons/dcc_site_status_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalSiteStatusOk(self):
    global fName
    fName = "./save_pic/dcc_site_status_ok.json"
    print("SITE STATUS OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_STATUS", "-f", "./jsons/dcc_site_status_ok.json", "--config", "./dcc.ini"], 
                        True)

  def testFunctionalSiteDeleteBad1(self):
    global fName
    fName = "./save_pic/dcc_site_delete_bad1.json"
    print("SITE DELETE BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_DELETE", "-f", "./jsons/dcc_site_delete_bad1.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalSiteDeleteBad2(self):
    global fName
    fName = "./save_pic/dcc_site_delete_bad2.json"
    print("SITE DELETE BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_DELETE", "-f", "./jsons/dcc_site_delete_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalSiteDeleteOk(self):
    global fName
    fName = "./save_pic/dcc_site_delete_ok.json"
    print("SITE DELETE OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_DELETE", "-f", "./jsons/dcc_site_delete_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalSiteCleanupBad1(self):
    global fName
    fName = "./save_pic/dcc_site_cleanup_bad1.json"
    print("SITE CLEANUP BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_CLEANUP", "-f", "./jsons/dcc_site_cleanup_bad1.json", "--config", "./dcc.ini"],
                         False)


  def testFunctionalSiteCleanupBad2(self):
    global fName
    fName = "./save_pic/dcc_site_cleanup_bad2.json"
    print("SITE CLEANUP BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "SITE_CLEANUP", "-f", "./jsons/dcc_site_cleanup_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalSiteCleanupOk(self):
    global fName
    fName = "./save_pic/dcc_site_cleanup_ok.json"
    print("SITE CLEANUP OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_CLEANUP", "-f", "./jsons/dcc_site_cleanup_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlNewBad1(self):
    global fName
    fName = "./save_pic/dcc_url_new_bad1.json"
    print("URL NEW BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_bad1.json", "--config", "./dcc.ini"], False)


  def testFunctionalUrlNewBad2(self):
    global fName
    fName = "./save_pic/dcc_url_new_bad2.json"
    print("URL NEW BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_bad2.json", "--config", "./dcc.ini"], False)


  def testFunctionalUrlNewOk(self):
    global fName
    fName = "./save_pic/dcc_url_new_ok.json"
    print("URL NEW OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlStatusBad1(self):
    global fName
    fName = "./save_pic/dcc_url_status_bad1.json"
    print("URL STATUS BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_STATUS", "-f", "./jsons/dcc_url_status_bad1.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlStatusBad2(self):
    global fName
    fName = "./save_pic/dcc_url_status_bad2.json"
    print("URL STATUS BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_STATUS", "-f", "./jsons/dcc_url_status_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlStatusOk(self):
    global fName
    fName = "./save_pic/dcc_url_status_ok.json"
    print("URL STATUS OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_STATUS", "-f", "./jsons/dcc_url_status_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlUpdateBad1(self):
    global fName
    fName = "./save_pic/dcc_url_update_bad1.json"
    print("URL UPDATE BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_UPDATE", "-f", "./jsons/dcc_url_update_bad1.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlUpdateBad2(self):
    global fName
    fName = "./save_pic/dcc_url_update_bad2.json"
    print("URL UPDATE BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_UPDATE", "-f", "./jsons/dcc_url_update_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlUpdateBad3(self):
    global fName
    fName = "./save_pic/dcc_url_update_bad3.json"
    print("URL UPDATE BAD3 START >>> \n")
    self.commonTestCode(["-cmd", "URL_UPDATE", "-f", "./jsons/dcc_url_update_bad3.json", "--config", "./dcc.ini"],
                         False)

  
  def testFunctionalUrlUpdateOk(self):
    global fName
    fName = "./save_pic/dcc_url_update_ok.json"
    print("URL UPDATE OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_UPDATE", "-f", "./jsons/dcc_url_update_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlFetchBad1(self):
    global fName
    fName = "./save_pic/dcc_url_fetch_bad1.json"
    print("URL FETCH BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_FETCH", "-f", "./jsons/dcc_url_fetch_bad1.json", "--config", "./dcc.ini"], False)


  def testFunctionalUrlFetchBad2(self):
    global fName
    fName = "./save_pic/dcc_url_fetch_bad2.json"
    print("URL FETCH BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_FETCH", "-f", "./jsons/dcc_url_fetch_bad2.json", "--config", "./dcc.ini"], False)


  def testFunctionalUrlFetchBad3(self):
    global fName
    fName = "./save_pic/dcc_url_fetch_bad3.json"
    print("URL FETCH BAD3 START >>> \n")
    self.commonTestCode(["-cmd", "URL_FETCH", "-f", "./jsons/dcc_url_fetch_bad3.json", "--config", "./dcc.ini"], False)

  
  def testFunctionalUrlFetchOk(self):
    global fName
    fName = "./save_pic/dcc_url_fetch_ok.json"
    print("URL FETCH OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_FETCH", "-f", "./jsons/dcc_url_fetch_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlDeleteBad1(self):
    global fName
    fName = "./save_pic/dcc_url_delete_bad1.json"
    print("URL DELETE BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_DELETE", "-f", "./jsons/dcc_url_delete_bad1.json", "--config", "./dcc.ini"],
                         False)


  def testFunctionalUrlDeleteBad2(self):
    global fName
    fName = "./save_pic/dcc_url_delete_bad2.json"
    print("URL DELETE BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_DELETE", "-f", "./jsons/dcc_url_delete_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlDeleteOk(self):
    global fName
    fName = "./save_pic/dcc_url_delete_ok.json"
    print("URL DELETE OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_DELETE", "-f", "./jsons/dcc_url_delete_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlCleanupBad1(self):
    global fName
    fName = "./save_pic/dcc_url_cleanup_bad1.json"
    print("URL CLEANUP BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_CLEANUP", "-f", "./jsons/dcc_url_cleanup_bad1.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlCleanupBad2(self):
    global fName
    fName = "./save_pic/dcc_url_cleanup_bad2.json"
    print("URL CLEANUP BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_CLEANUP", "-f", "./jsons/dcc_url_cleanup_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlCleanupBad3(self):
    global fName
    fName = "./save_pic/dcc_url_cleanup_bad3.json"
    print("URL CLEANUP BAD3 START >>> \n")
    self.commonTestCode(["-cmd", "URL_CLEANUP", "-f", "./jsons/dcc_url_cleanup_bad3.json", "--config", "./dcc.ini"], 
                        False)
    
    
  def testFunctionalUrlCleanupOk(self):
    global fName
    fName = "./save_pic/dcc_url_cleanup_ok.json"
    print("URL CLEANUP OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CLEANUP", "-f", "./jsons/dcc_url_cleanup_ok.json", "--config", "./dcc.ini"], 
                        True)
    
    
  def testFunctionalUrlContentBad1(self):
    global fName
    fName = "./save_pic/dcc_url_content_bad1.json"
    print("URL CONTENT BAD1 START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_bad1.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlContentBad2(self):
    global fName
    fName = "./save_pic/dcc_url_content_bad2.json"
    print("URL CONTENT BAD2 START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_bad2.json", "--config", "./dcc.ini"], 
                        False)


  def testFunctionalUrlContentBad3(self):
    global fName
    fName = "./save_pic/dcc_url_content_bad3.json"
    print("URL CONTENT BAD3 START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_bad3.json", "--config", "./dcc.ini"], 
                        False)

  
  def testFunctionalUrlContentOk(self):
    global fName
    fName = "./save_pic/dcc_url_content_ok.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentOk1(self):
    global fName
    fName = "./save_pic/DCC_url_content1-4.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/DCC_url_content1-4.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentOk2(self):
    global fName
    fName = "./save_pic/DCC_url_content5.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/DCC_url_content5.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentOk3(self):
    global fName
    fName = "./save_pic/DCC_url_content5_dyn.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/DCC_url_content5_dyn.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentOk4(self):
    global fName
    fName = "./save_pic/DCC_url_content5_ext.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/DCC_url_content5_ext.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentOk5(self):
    global fName
    fName = "./save_pic/DCC_url_content_dbfields.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/DCC_url_content_dbfields.json", "--config", "./dcc.ini"], 
                        True)        


  def testFunctionalInvalidJSON(self):
    global fName
    fName = "./save_pic/dcc_invalid_json.json"
    print("INVALID JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_invalid_json.json", "--config", "./dcc.ini"], False)


  def testFunctionalUrlContentTestJSON(self):
    global fName
    fName = "./save_pic/dcc_url_content_test1.json"
    print("CONTENT TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_test1.json", \
                         "--config", "./dcc.ini", "--merge", "1"], False)


  def testFunctionalCustomBad1JSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_bad1.json"
    print("CUSTOM BAD1 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_bad1.json", \
                         "--config", "./dcc.ini"], False)
    
    
  def testFunctionalCustomBad2JSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_bad2.json"
    print("CUSTOM BAD2 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_bad2.json", \
                         "--config", "./dcc.ini"], False)


  def testFunctionalCustomBad3JSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_bad3.json"
    print("CUSTOM BAD3 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_bad3.json", \
                         "--config", "./dcc.ini"], False)


  def testFunctionalCustomBad4JSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_bad4.json"
    print("CUSTOM BAD4 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_bad4.json", \
                         "--config", "./dcc.ini"], False)


  def testFunctionalCustomBad5JSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_bad5.json"
    print("CUSTOM BAD5 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_bad5.json", \
                         "--config", "./dcc.ini"], False)


  def testFunctionalCustomBad6JSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_bad6.json"
    print("CUSTOM BAD6 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_bad6.json", \
                         "--config", "./dcc.ini"], False)


  def testFunctionalCustomOkJSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_ok.json"
    print("CUSTOM OK TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_ok.json", "--config", "./dcc.ini"], False)

    
  def testFunctionalBatchOkJSON(self):
    global fName
    fName = "./save_pic/dcc_batch_ok.json"
    print("BATCH OK TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "BATCH", "-f", "./jsons/dcc_batch_ok.json", "--config", "./dcc.ini"], False)


  def testFunctionalBatchPropOkJSON(self):
    global fName
    fName = "./save_pic/dcc_batch_prop_ok.json"
    print("BATCH PROP OK TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "BATCH", "-f", "./jsons/dcc_batch_prop_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalSiteFindJSON(self):
    global fName
    fName = "./save_pic/dcc_site_find_ok.json"
    print("SITE FIND OK TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SITE_FIND", "-f", "./jsons/dcc_site_find_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlPurgeBad1JSON(self):
    global fName
    fName = "./save_pic/dcc_url_purge_bad1.json"
    print("URL PURGE BAD1 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_PURGE", "-f", "./jsons/dcc_url_purge_bad1.json", "--config", "./dcc.ini"], False)


  def testFunctionalUrlPurgeOkJSON(self):
    global fName
    fName = "./save_pic/dcc_url_purge_ok.json"
    print("URL PURGE OK TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_PURGE", "-f", "./jsons/dcc_url_purge_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlPurgeOk2JSON(self):
    global fName
    fName = "./save_pic/dcc_url_purge_ok2.json"
    print("URL PURGE OK2 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_PURGE", "-f", "./jsons/dcc_url_purge_ok2.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlPurgeOk3JSON(self):
    global fName
    fName = "./save_pic/dcc_url_purge_ok3.json"
    print("URL PURGE OK3 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_PURGE", "-f", "./jsons/dcc_url_purge_ok3.json", "--config", "./dcc.ini"], True)


  def testFunctionalUrlNewDtest1OkJSON(self):
    global fName
    fName = "./save_pic/dcc_url_new_dtest1_ok.json"
    print("URL DTEST1 OK2 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_dtest1_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalFieldRecalculatorOkJSON(self):
    global fName
    fName = "./save_pic/dcc_field_recalculator_ok.json"
    print("URL FIELD RECALCULATOR TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "F_RECALC", "-f", "./jsons/dcc_field_recalculator_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalURLNewVerify1JSON(self):
    global fName
    fName = "./save_pic/dcc_url_new_verify.json"
    print("URL NEW VERIFY TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_verify.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalURLNewVerify21JSON(self):
    global fName
    fName = "./save_pic/dcc_url_new_verify2.json"
    print("URL NEW VERIFY2 TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_verify2.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalURLVerify1JSON(self):
    global fName
    fName = "./save_pic/dcc_url_verify.json"
    print("URL VERIFY TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_VERIFY", "-f", "./jsons/dcc_url_verify.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalURLNewUpdate(self):
    global fName
    fName = "./save_pic/dcc_url_new_update_ok.json"
    print("URL NEW UPDATE TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_update_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalURLAge(self):
    global fName
    fName = "./save_pic/dcc_url_age_ok.json"
    print("URL AGE TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_AGE", "-f", "./jsons/dcc_url_age_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalSiteNewContentOk(self):
    global fName
    fName = "./save_pic/dcc_site_ok_current.json"
    print("SITE NEW CONTENT OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_ok_current.json", "--config", "./dcc.ini"], True)


  def testFunctionalCustomContentOkJSON(self):
    global fName
    fName = "./save_pic/dcc_sql_custom_content.json"
    print("CUSTOM CONTENT OK TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "SQL_CUSTOM", "-f", "./jsons/dcc_sql_custom_content.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentOkMySQLself(self):
    global fName
    fName = "./save_pic/dcc_url_content_mysql.json"
    print("URL CONTENT TEST1 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_mysql.json", "--config", "./dcc.ini"], 
                        True)   


  def testFunctionalSiteNewOkTest(self):
    global fName
    fName = "./save_pic/dcc_site_new_test.json"
    print("SITE NEW TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_test.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalUrlPutOkTest(self):
    global fName
    fName = "./save_pic/dcc_url_put.json"
    print("URL PUT TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_PUT", "-f", "./jsons/dcc_url_put.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalSiteNewOkTest(self):
    global fName
    fName = "./save_pic/dcc_site_new_move.json"
    print("SITE NEW MOVE OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_move_ok.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalSiteCleanupOkTest(self):
    global fName
    fName = "./save_pic/dcc_site_cleanup_move_ok.json"
    print("SITE CLEANUP MOVE OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_CLEANUP", "-f", "./jsons/dcc_site_cleanup_move_ok.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalUrlNewMoveOkTest(self):
    global fName
    fName = "./save_pic/dcc_url_new_move_ok.json"
    print("URL NEW MOVE OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_move_ok.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalSiteNewDefCriterionsOkTest(self):
    global fName
    fName = "./save_pic/dcc_site_new_def_recalc_ok.json"
    print("SITE NEW DEF CRITERIONS TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_def_recalc_ok.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalFieldRecalculatorDefOkJSON(self):
    global fName
    fName = "./save_pic/dcc_field_recalculator_def_ok.json"
    print("URL FIELD RECALCULATOR DEF TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "F_RECALC", "-f", "./jsons/dcc_field_recalculator_def_ok.json", 
                         "--config", "./dcc.ini"], True)


  def testFunctionalSiteNewOkTest(self):
    global fName
    fName = "./save_pic/dcc_site_new_filters.json"
    print("SITE NEW FILTERS TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/dcc_site_new_filters.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalUrlNewOkTest(self):
    global fName
    fName = "./save_pic/dcc_url_new_statistic_ok.json"
    print("URL NEW STATISTIC TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_statistic_ok.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalUrlUpdateOkTest(self):
    global fName
    fName = "./save_pic/dcc_url_update_statistic_ok.json"
    print("URL UPDATE STATISTIC TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_UPDATE", "-f", "./jsons/dcc_url_update_statistic_ok.json", "--config", 
                         "./dcc.ini"], True)


  def testFunctionalUrlDeleteOkTest(self):
    global fName
    fName = "./save_pic/dcc_url_delete_statistic_ok.json"
    print("URL DELETE STATISTIC TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_DELETE", "-f", "./jsons/dcc_url_delete_statistic_ok.json", "--config", 
                         "./dcc.ini"], True)
    

  def testFunctionalURLAge(self):
    global fName
    fName = "./save_pic/dcc_url_age_statistic_ok.json"
    print("URL AGE STATISTIC TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_AGE", "-f", "./jsons/dcc_url_age_statistic_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlPurge(self):
    global fName
    fName = "./save_pic/dcc_url_purge_statistic_ok.json"
    print("URL PURGE STATISTIC TEST JSON START >>> \n")
    self.commonTestCode(["-cmd", "URL_PURGE", "-f", "./jsons/dcc_url_purge_statistic_ok.json", "--config", 
                         "./dcc.ini"], True)

  def testFunctionalUrlNewPutOk(self):
    global fName
    fName = "./save_pic/dcc_url_new_put_ok.json"
    print("URL NEW PUT OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/dcc_url_new_put_ok.josn", "--config", "./dcc.ini"], True)


  def testFunctionalUrlUpdatePutOk(self):
    global fName
    fName = "./save_pic/dcc_url_update_put_ok.json"
    print("URL UPDATE PUT OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_UPDATE", "-f", "./jsons/dcc_url_update_put_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlContentTest2Ok(self):
    global fName
    fName = "./save_pic/dcc_url_content_test2.json"
    print("URL CONTENT TEST2 OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_CONTENT", "-f", "./jsons/dcc_url_content_test2.json", "--config", "./dcc.ini"], 
                        True)
  '''
  '''
  def testFunctionalSiteNewOkTest(self):
    global fName
    fName = "./save_pic/dcc_site_new_ok.json"
    print("SITE NEW OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_NEW", "-f", "./jsons/DC-770/dcc_site_new_ok.json", "--config", "./dcc.ini"],
                        True)


  def testFunctionalUrlNewOk(self):
    global fName
    fName = "./save_pic/dcc_url_new_ok.json"
    print("URL NEW OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_NEW", "-f", "./jsons/DC-766/dcc_url_new_ok.json", "--config", "./dcc.ini"], True)


  def testFunctionalSiteUpdateOk(self):
    global fName
    fName = "./save_pic/dcc_site_update_ok.json"
    print("SITE UPDATE OK START >>> \n")
    self.commonTestCode(["-cmd", "SITE_UPDATE", "-f", "./jsons/DC-770/dcc_site_update_ok.json", "--config", "./dcc.ini"], 
                        True)


  def testFunctionalUrlPutOkTest(self):
    global fName
    fName = "./save_pic/dcc_url_put_test.json"
    print("URL PUT TEST OK START >>> \n")
    self.commonTestCode(["-cmd", "URL_PUT", "-f", "./jsons/dcc_url_put_test.json", "--config", "./dcc.ini"],
                        True)
  '''

if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()