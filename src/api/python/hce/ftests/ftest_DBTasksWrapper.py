'''
Created on Oct 28, 2014

@author: scorp
'''
import unittest
import ppath  # pylint: disable=W0611
from ppath import sys
import logging.config
import ConfigParser
import dc_crawler.DBTasksWrapper as DBTasksWrapper
import dc.EventObjects
from app.Utils import SQLExpression


class Test(unittest.TestCase):

  CFG_NAME = "./db-task2.ini"


  def setUp(self):
    cfgParser = ConfigParser.ConfigParser()
    cfgParser.read(self.CFG_NAME)
    logging.config.fileConfig(cfgParser.get("TasksManager", "log_cfg"))
    self.wrapper = DBTasksWrapper.DBTasksWrapper(cfgParser)


  def tearDown(self):
    pass


  def urlNew(self, params):
    ret = 0
    if params is not None:
      if hasattr(params, '__iter__'):
        urlsList = []
        for param in params:
          urlObject = dc.EventObjects.URL(param[0], param[1])
          urlObject.type = param[2]
          urlObject.urlMd5 = param[3]
          urlObject.requestDelay = param[4]
          urlObject.httpTimeout = param[5]
          urlObject.httpMethod = param[6]
          urlObject.parentMd5 = param[7]
          urlObject.maxURLsFromPage = param[8]
          urlObject.tcDate = SQLExpression("NOW()")
          urlObject.UDate = SQLExpression("NOW()")
          urlObject.depth = param[9]
          urlObject.contentType = param[10]
          urlObject.priority = param[11]
          urlsList.append(urlObject)
        ret = self.wrapper.urlNew(urlsList)
    return ret


  def insertNewSiteProperties(self, siteId, params):
    if siteId is not None and hasattr(params, '__iter__') and len(params) > 0:
      localSiteUpdate = dc.EventObjects.SiteUpdate(siteId)
      for attr in localSiteUpdate.__dict__:
        if hasattr(localSiteUpdate, attr):
          setattr(localSiteUpdate, attr, None)
      localSiteUpdate.updateType=dc.EventObjects.SiteUpdate.UPDATE_TYPE_APPEND
      localSiteUpdate.id = siteId
      localSiteUpdate.properties = []
      for param in params:
        newPropElem = {}
        newPropElem["siteId"] = param[0]
        newPropElem["name"] = param[1]
        newPropElem["value"] = param[2]
        localSiteUpdate.properties.append(newPropElem)
      self.wrapper.siteNewOrUpdate(localSiteUpdate, stype=dc.EventObjects.SiteUpdate)


  def test_CustomRequest(self):
    newObject = dc.EventObjects.Site("http://ibm.com")
    self.wrapper.siteNewOrUpdate(newObject)
    selectStr ="SELECT COUNT(*) FROM urls_0b41d5052c7a52f5927ae7114cb288e9 " + \
    "WHERE NOT (Status=4 AND Crawled=0 AND Processed=0)"
    result = self.wrapper.customRequest(selectStr, "dc_urls")
    if len(result) > 0 and len(result[0]) > 0:
      print result[0][0]
    
    url_md5 = "0b41d5052c7a52f5927ae7114cb288e9"
    siteId = "0b41d5052c7a52f5927ae7114cb288e9"
    urlUpdateObj = dc.EventObjects.URLUpdate(siteId, url_md5, dc.EventObjects.URLStatus.URL_TYPE_MD5)
    urlUpdateObj.tcDate = SQLExpression("NOW()")
    urlUpdateObj.status = 2
    urlUpdateObj.depth = 32
    self.wrapper.urlUpdate(urlUpdateObj, "`State`=0")
    
    urlStatusObj = dc.EventObjects.URLStatus(siteId, url_md5)
    result = self.wrapper.urlStatus(urlStatusObj, True)
    if len(result) > 0 and type(result[0]) == dc.EventObjects.URL:
      print "Depth == " + str(result[0].depth)
      
    params = []
    params.append((siteId, "http://ibm1.com", 0, "32323232", 10, 10,
                   "GET", "0b41d5052c7a52f5927ae7114cb288e9", 1, 1, "test", 71))
    params.append((siteId, "http://ibm2.com", 0, "55656565", 10, 10,
                   "GET", "0b41d5052c7a52f5927ae7114cb288e9", 1, 1, "text/xml", 71))
    self.urlNew(params)
    
    props_params = []
    props_params.append(("0b41d5052c7a52f5927ae7114cb288e9", "HTTP_POST_FORM_AAA", "AAA"))
    props_params.append(("0b41d5052c7a52f5927ae7114cb288e9", "HTTP_POST_FORM_BBB", "BBB"))
    self.insertNewSiteProperties(siteId, props_params)

if __name__ == "__main__":
#import sys;sys.argv = ['', 'Test.testName']
  unittest.main()