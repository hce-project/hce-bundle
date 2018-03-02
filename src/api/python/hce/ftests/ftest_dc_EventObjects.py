'''
HCE project, Python bindings, Distributed Crawler application.
Event objects functional tests.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import dc.EventObjects
import dtm.EventObjects
from app.Utils import SQLExpression
from datetime import datetime
#import MySQLdb
#import oursql
#import mysql


if __name__ == "__main__":
  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"


  #Test Site object
  #site = dc.EventObjects.Site("http://127.0.0.1/")
  site = dc.EventObjects.Site("http://127.0.0.1/_site_random_generator.php?wrong=url")
  site.filters = [dc.EventObjects.SiteFilter(site.id, "*")]
  print TEST_TITLE + site.__class__.__name__ + TEST_TITLE_OBJECT, vars(site)
  print site.toJSON()

  #Test SiteUpdate object with overwrite action
  su = dc.EventObjects.SiteUpdate("b85ab149a528bd0a024fa0f43e80b5fc",
                                          dc.EventObjects.SiteUpdate.UPDATE_TYPE_OVERWRITE)
  su.uDate = SQLExpression("NOW()")
  su.tcDate = SQLExpression("NOW()")
  #su.cDate = "2012-12-12 12:12:12"
  su.cDate = datetime.now()
  su.resources = 2
  su.iterations = 20
  su.description = "Test update"
  su.urls = ["http://localhost/"]
  su.filters = [dc.EventObjects.SiteFilter(su.id, "http://localhost/*")]
  su.properties = {"PROCESS_CTYPES":"text/plain", "STORE_HTTP_REQUEST":"1", "STORE_HTTP_HEADERS":"1"}
  su.state = dc.EventObjects.Site.STATE_DISABLED
  su.priority = 200
  su.maxURLs = 2000
  su.maxResources = 2000
  su.maxErrors = 20000
  su.maxResourceSize = 20000000
  su.requestDelay = 200000000
  su.httpTimeout = 2000000000
  su.errorMask = 20000000000
  su.errors = 200000000000
  su.urlType = 2
  print TEST_TITLE + su.__class__.__name__ + TEST_TITLE_OBJECT, vars(su)
  print su.toJSON()

  #Test SiteUpdate object with append action
  su = dc.EventObjects.SiteUpdate("699fcf4591fc23e79b839d8819904293",
                                          dc.EventObjects.SiteUpdate.UPDATE_TYPE_APPEND)
  su.uDate = SQLExpression("NOW()")
  su.tcDate = SQLExpression("NOW()")
  su.cDate = "2012-12-12 12:12:12"
  su.resources = 2
  su.iterations = 20
  su.description = "Test update"
  su.urls = ["http://localhost/"]
  su.filters = [dc.EventObjects.SiteFilter(su.id, "http://localhost/*")]
  su.properties = {"PROCESS_CTYPES":"text/plain", "STORE_HTTP_REQUEST":"1", "STORE_HTTP_HEADERS":"1"}
  su.state = dc.EventObjects.Site.STATE_DISABLED
  su.priority = 200
  su.maxURLs = 2000
  su.maxResources = 2000
  su.maxErrors = 20000
  su.maxResourceSize = 20000000
  su.requestDelay = 200000000
  su.httpTimeout = 2000000000
  su.errorMask = 20000000000
  su.errors = 200000000000
  su.urlType = 2
  print TEST_TITLE + su.__class__.__name__ + TEST_TITLE_OBJECT, vars(su)
  print su.toJSON()


  #Test SiteStatus object
  siteStatus = dc.EventObjects.SiteStatus("699fcf4591fc23e79b839d8819904293")
  print TEST_TITLE + siteStatus.__class__.__name__ + TEST_TITLE_OBJECT, vars(siteStatus)
  print siteStatus.toJSON()

  #Test SiteDelete object
  sd = dc.EventObjects.SiteDelete("699fcf4591fc23e79b839d8819904293")
  print TEST_TITLE + sd.__class__.__name__ + TEST_TITLE_OBJECT, vars(sd)
  print sd.toJSON()

  #Test SiteCleanup object
  sc = dc.EventObjects.SiteCleanup("b85ab149a528bd0a024fa0f43e80b5fc")
  print TEST_TITLE + sc.__class__.__name__ + TEST_TITLE_OBJECT, vars(sc)
  print sc.toJSON()

  #Test SiteFilter object
  sf = dc.EventObjects.SiteFilter("235325634634263", "*")
  print TEST_TITLE + sf.__class__.__name__ + TEST_TITLE_OBJECT, vars(sf)

  #Test URL object simple
  #url = dc.EventObjects.URL("b85ab149a528bd0a024fa0f43e80b5fc", "http://127.0.0.1/")
  url = dc.EventObjects.URL("b85ab149a528bd0a024fa0f43e80b5fc", "http://127.0.0.1/_site_random_generator.php?a=1")
  print TEST_TITLE + url.__class__.__name__ + TEST_TITLE_OBJECT, vars(url)
  print url.toJSON()

  #Test URLStatus object
  us = dc.EventObjects.URLStatus("b85ab149a528bd0a024fa0f43e80b5fc", "701ccc5c1c589041d31d13dae8dce90d")
  us.urlType = dc.EventObjects.URLStatus.URL_TYPE_MD5
  print TEST_TITLE + us.__class__.__name__ + TEST_TITLE_OBJECT, vars(us)
  print us.toJSON()

  #Test BatchItem object
  urlObj = dc.EventObjects.URL("235325634634263", "http://127.0.0.1/")
  bi1 = dc.EventObjects.BatchItem("235325634634263", "235325634634234", urlObj)
  print TEST_TITLE + bi1.__class__.__name__ + TEST_TITLE_OBJECT, vars(bi1)
  bi2 = dc.EventObjects.BatchItem("335325634634264", "335325634634235", urlObj)
  print bi1.toJSON()

  #Test Batch object
  b = dc.EventObjects.Batch([bi1, bi2])
  print TEST_TITLE + b.__class__.__name__ + TEST_TITLE_OBJECT, vars(b)
  print b.toJSON()

  #Test URLFetch object
  uf = dc.EventObjects.URLFetch()
  print TEST_TITLE + uf.__class__.__name__ + TEST_TITLE_OBJECT, vars(uf)
  print uf.toJSON()
  uf = dc.EventObjects.URLFetch(["235325634634263", "235325634634234"])
  print TEST_TITLE + uf.__class__.__name__ + TEST_TITLE_OBJECT, vars(uf)
  print uf.toJSON()
  uf = dc.EventObjects.URLFetch()
  uf.urlsCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] = \
            "Status=7 AND Crawled>0 AND Processed>0 AND CDate BETWEEN '2014-06-28 00:00:01' AND '2014-06-28 23:59:59'"
  print TEST_TITLE + uf.__class__.__name__ + TEST_TITLE_OBJECT, vars(uf)
  print uf.toJSON()

  #Test URLUpdate object
  uu = dc.EventObjects.URLUpdate("525326523434525", "http://127.0.0.1/", statusField=dc.EventObjects.URL.STATUS_NEW)
  print TEST_TITLE + uu.__class__.__name__ + TEST_TITLE_OBJECT, vars(uu)
  print uu.toJSON()
  uu = dc.EventObjects.URLUpdate("b85ab149a528bd0a024fa0f43e80b5fc", urlString="701ccc5c1c589041d31d13dae8dce90d",
                                 urlType=dc.EventObjects.URLStatus.URL_TYPE_MD5,
                                 stateField=dc.EventObjects.URL.STATE_ENABLED,
                                 statusField=dc.EventObjects.URL.STATUS_NEW)
  print TEST_TITLE + uu.__class__.__name__ + TEST_TITLE_OBJECT, vars(uu)
  print uu.toJSON()

  #Test URLDelete object
  ud = dc.EventObjects.URLDelete("233243243242423", urlString="http://127.0.0.1/")
  print TEST_TITLE + ud.__class__.__name__ + TEST_TITLE_OBJECT, vars(ud)
  print ud.toJSON()
  ud = dc.EventObjects.URLDelete("b85ab149a528bd0a024fa0f43e80b5fc", urlString="701ccc5c1c589041d31d13dae8dce90d",
                                  urlType=dc.EventObjects.URLStatus.URL_TYPE_MD5)
  print TEST_TITLE + ud.__class__.__name__ + TEST_TITLE_OBJECT, vars(ud)
  print ud.toJSON()

  #Test URLCleanup object
  uc = dc.EventObjects.URLCleanup("346436436436346", urlString="http://127.0.0.1/", statusField=dc.EventObjects.URL.STATUS_NEW)
  print TEST_TITLE + uc.__class__.__name__ + TEST_TITLE_OBJECT, vars(uc)
  print uc.toJSON()
  uc = dc.EventObjects.URLCleanup("3463463463463463", urlString="235325634634263", urlType=dc.EventObjects.URLStatus.URL_TYPE_MD5,
                                 stateField=dc.EventObjects.URL.STATE_DISABLED)
  print TEST_TITLE + uc.__class__.__name__ + TEST_TITLE_OBJECT, vars(uc)
  print uc.toJSON()

  #Test URLContentRequest object
  ucr = dc.EventObjects.URLContentRequest("325632523424234234", "http://127.0.0.1/")
  print TEST_TITLE + ucr.__class__.__name__ + TEST_TITLE_OBJECT, vars(ucr)
  print ucr.toJSON()
  ucr = dc.EventObjects.URLContentRequest("3464363464363634", "http://127.0.0.1/",
                                          dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED +
                                          dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_ALL)
  print TEST_TITLE + ucr.__class__.__name__ + TEST_TITLE_OBJECT, vars(ucr)
  print ucr.toJSON()
  ucr = dc.EventObjects.URLContentRequest("", "")
  uf = dc.EventObjects.URLFetch()
  uf.urlsCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] = \
            "Status=7 AND Crawled>0 AND Processed>0 AND CDate BETWEEN '2014-06-28 00:00:01' AND '2014-06-28 23:59:59'"
  uf.sitesCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] = \
            "State IN (1,2,3)"
  uf.algorithm = dc.EventObjects.URLFetch.PROPORTIONAL_ALGORITHM
  uf.maxURLs = 10
  ucr.urlFetch = uf
  print TEST_TITLE + ucr.__class__.__name__ + TEST_TITLE_OBJECT, vars(ucr)
  print ucr.toJSON()


  #Test URLContentResponse object
  ucr = dc.EventObjects.URLContentResponse("http://127.0.0.1/",
                                           dc.EventObjects.Content(["<html>test content 1</html>"], 124124354),
                                           dc.EventObjects.Content(["test content 1"]))
  print TEST_TITLE + ucr.__class__.__name__ + TEST_TITLE_OBJECT, vars(ucr)
  print ucr.toJSON()


  #Test ClientResponse object
  gr = dtm.EventObjects.GeneralResponse()
  cri = dc.EventObjects.ClientResponseItem(gr)
  cr = dc.EventObjects.ClientResponse([cri])
  print TEST_TITLE + cr.__class__.__name__ + TEST_TITLE_OBJECT, vars(cr)
  print cr.toJSON()

