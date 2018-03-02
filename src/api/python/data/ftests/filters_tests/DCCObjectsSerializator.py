'''
Created on Apr 11, 2014

@package: dc
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from app.Utils import SQLExpression
import hashlib
import app.Exceptions as Exceptions
import dc.EventObjects
import app.Consts as APP_CONSTS
import logging

# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)



# #DTMCObjectsSerializator Class contents serialize/deserialize methods for incoming "DTMC" commands
#
class DCCObjectsSerializator(object):

  def __init__(self):
    pass


  # #timeExtractor method, extracts time in various format
  def timeExtractor(self, timeField):
    ret = None
    if timeField != None:
      if type(timeField) == type("") or type(timeField) == type(unicode("")):
        ret = SQLExpression(str(timeField))
      elif type(timeField) == type({}):
        ret = SQLExpression(str(timeField["str"]))
    return ret


  # #checkProperties method, validate incoming properties dict, rise excaption if properties contains bad values
  # properties - incoming properties dict
  def checkProperties(self, properties):
    for value in properties.values():
      if not isinstance(value, str) and not isinstance(value, unicode) and not isinstance(value, list):
        raise Exceptions.DeserilizeException("Properties field values can be string or list[] type")
      elif isinstance(value, list) and len(value) != 3:
        raise Exceptions.DeserilizeException("Properties field values with list[] type must be len() == 3")


  # #checkFilters method, gets filters list and return list of SiteFilter objects
  # filters - incoming filters list
  def checkFilters(self, filters, sid):
    ret = None
    siteId = None
    siteFilter = None
    if filters != None:
      ret = []
      for localFilter in filters:
        if "siteId" in localFilter and localFilter["siteId"] != None:
          siteId = str(localFilter["siteId"])
        else:
          siteId = sid
        if "pattern" not in localFilter:
          raise Exceptions.DeserilizeException(".filters pattern not found")
        if "type" not in localFilter:
          siteFilter = dc.EventObjects.SiteFilter(siteId, str(localFilter["pattern"]))
        else:
          siteFilter = dc.EventObjects.SiteFilter(siteId, str(localFilter["pattern"]), int(localFilter["type"]))
        if "mode" in localFilter and localFilter["mode"] != None:
          siteFilter.mode = int(localFilter["mode"])
        if "State" in localFilter and localFilter["State"] != None:
          siteFilter.state = int(localFilter["State"])
        if "stage" in localFilter and localFilter["stage"] != None:
          siteFilter.stage = int(localFilter["stage"])
        if "subject" in localFilter and localFilter["subject"] != None:
          siteFilter.subject = localFilter["subject"]
        if "action" in localFilter and localFilter["action"] != None:
          siteFilter.action = int(localFilter["action"])
        ret.append(siteFilter)
    return ret


  # #simpleValueExtractor method, extracts values for simple fields
  # fieldName - field name
  # jsonData - json container
  # _type - field type
  # excepStr - exception string
  # i - index value
  def simpleValueExtractor(self, fieldName, jsonData, _type, excepStr, i=None):
    ret = None
    if fieldName in jsonData:
      ret = jsonData[fieldName]
      if ret != None:
        ret = type(_type)(ret)
    else:
      if i == None:
        raise Exceptions.DeserilizeException("%s json-field not found" % excepStr)
      else:
        raise Exceptions.DeserilizeException("%s json-field not found in [%s] elem" % (excepStr, str(i)))
    return ret


  # #siteNewDeserialize method, deserializes incoming jsonData to the Site object
  # jsonData - incoming json string
  def siteNewDeserialize(self, jsonData):
    siteObject = None
    try:
      if "id" in jsonData and jsonData["id"] != None:
        siteObject = dc.EventObjects.Site("")
        siteObject.id = str(jsonData["id"])
      else:
        if "urls" in jsonData and hasattr(jsonData["urls"], '__iter__') and \
          len(jsonData["urls"]) > 0 and jsonData["urls"][0] != None:
          siteObject = dc.EventObjects.Site(jsonData["urls"][0])
        else:
          raise Exceptions.DeserilizeException("Site.id json-field not found and Site.urls[0] no found")
      if "uDate" in jsonData:
        siteObject.uDate = self.timeExtractor(jsonData["uDate"])
      else:
        raise Exceptions.DeserilizeException("Site.uDate json-field not found")
      if "tcDate" in jsonData:
        siteObject.tcDate = self.timeExtractor(jsonData["tcDate"])
      else:
        raise Exceptions.DeserilizeException("Site.tcDate json-field not found")
      if "cDate" in jsonData:
        siteObject.cDate = self.timeExtractor(jsonData["cDate"])
      else:
        raise Exceptions.DeserilizeException("Site.cDate json-field not found")
      siteObject.resources = self.simpleValueExtractor("resources", jsonData, int(), "Site.resources")
      siteObject.iterations = self.simpleValueExtractor("iterations", jsonData, int(), "Site.iterations")
      siteObject.description = self.simpleValueExtractor("description", jsonData, str(), "Site.description")
      if "urls" in jsonData:
        if jsonData["urls"] != None and type(jsonData["urls"]) != type([]):
          raise Exceptions.DeserilizeException("Site.urls not list type")
        siteObject.urls = jsonData["urls"]
      else:
        raise Exceptions.DeserilizeException("Site.urls json-field not found")
      if "filters" in jsonData:
        if jsonData["filters"] != None and type(jsonData["filters"]) != type([]):
          raise Exceptions.DeserilizeException("Site.filters not list type")
        siteObject.filters = self.checkFilters(jsonData["filters"], siteObject.id)
      else:
        raise Exceptions.DeserilizeException("Site.filters json-field not found")
      if "properties" in jsonData:
        if jsonData["properties"] != None and type(jsonData["properties"]) != type({}) and \
        type(jsonData["properties"]) != type([]):
          raise Exceptions.DeserilizeException("Site.properties not dict type")
        if type(jsonData["properties"]) != type([]):
          self.checkProperties(jsonData["properties"])
        siteObject.properties = jsonData["properties"]
      else:
        raise Exceptions.DeserilizeException("Site.properties json-field not found")
      siteObject.state = self.simpleValueExtractor("state", jsonData, int(), "Site.state")
      siteObject.priority = self.simpleValueExtractor("priority", jsonData, int(), "Site.priority")
      siteObject.maxURLs = self.simpleValueExtractor("maxURLs", jsonData, int(), "Site.maxURLs")
      siteObject.maxResources = self.simpleValueExtractor("maxResources", jsonData, int(), "Site.maxResources")
      siteObject.maxErrors = self.simpleValueExtractor("maxErrors", jsonData, int(), "Site.maxErrors")
      siteObject.maxResourceSize = self.simpleValueExtractor("maxResourceSize", jsonData, int(), "Site.maxResourceSize")
      siteObject.requestDelay = self.simpleValueExtractor("requestDelay", jsonData, int(), "Site.requestDelay")
      siteObject.httpTimeout = self.simpleValueExtractor("httpTimeout", jsonData, int(), "Site.httpTimeout")
      siteObject.errorMask = self.simpleValueExtractor("errorMask", jsonData, int(), "Site.errorMask")
      siteObject.errors = self.simpleValueExtractor("errors", jsonData, int(), "Site.errors")
      siteObject.urlType = self.simpleValueExtractor("urlType", jsonData, int(), "Site.urlType")
      siteObject.contents = self.simpleValueExtractor("contents", jsonData, int(), "Site.contents")
      siteObject.processingDelay = self.simpleValueExtractor("processingDelay", jsonData, int(), "Site.processingDelay")
      siteObject.size = self.simpleValueExtractor("size", jsonData, int(), "Site.size")
      siteObject.avgSpeed = self.simpleValueExtractor("avgSpeed", jsonData, int(), "Site.avgSpeed")
      siteObject.avgSpeedCounter = self.simpleValueExtractor("avgSpeedCounter", jsonData, int(), "Site.avgSpeedCounter")
      siteObject.userId = self.simpleValueExtractor("userId", jsonData, int(), "Site.userId")
      # update by Oleksii
      # add support maxURLsFromPage (dc-170)
      siteObject.maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", jsonData, int(), "Site.maxURLsFromPage")
      siteObject.recrawlPeriod = self.simpleValueExtractor("recrawlPeriod", jsonData, int(), "Site.recrawlPeriod")
      siteObject.maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", jsonData, int(), "Site.maxURLsFromPage")
      if "recrawlDate" in jsonData:
        siteObject.recrawlDate = self.timeExtractor(jsonData["recrawlDate"])
      else:
        raise Exceptions.DeserilizeException("Site.recrawlDate json-field not found")
      siteObject.collectedURLs = self.simpleValueExtractor("collectedURLs", jsonData, int(), "Site.collectedURLs")
      siteObject.fetchType = self.simpleValueExtractor("fetchType", jsonData, int(), "Site.fetchType")
    except Exceptions.DeserilizeException, e:
      raise e
    except (ValueError, TypeError):
      logger.warn("x", exc_info = True)
      raise Exceptions.DeserilizeException("some field has invalid type")
    return siteObject


  # #siteUpdateDeserialize method, deserializes incoming jsonData to the SiteUpdate object
  # jsonData - incoming json string
  def siteUpdateDeserialize(self, jsonData):
    siteUpdateObject = dc.EventObjects.SiteUpdate("")
    try:
      siteUpdateObject.updateType = self.simpleValueExtractor("updateType", jsonData, int(), "SiteUpdate.updateType")
      siteUpdateObject.id = self.simpleValueExtractor("id", jsonData, str(), "SiteUpdate.id")
      if "uDate" in jsonData:
        siteUpdateObject.uDate = self.timeExtractor(jsonData["uDate"])
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.uDate json-field not found")
      if "tcDate" in jsonData:
        siteUpdateObject.tcDate = self.timeExtractor(jsonData["tcDate"])
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.tcDate json-field not found")
      if "cDate" in jsonData:
        siteUpdateObject.cDate = self.timeExtractor(jsonData["cDate"])
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.cDate json-field not found")
      siteUpdateObject.resources = self.simpleValueExtractor("resources", jsonData, int(), "SiteUpdate.resources")
      siteUpdateObject.iterations = self.simpleValueExtractor("iterations", jsonData, int(), "SiteUpdate.iterations")
      siteUpdateObject.description = self.simpleValueExtractor("description", jsonData, str(), "SiteUpdate.description")
      if "urls" in jsonData:
        if jsonData["urls"] != None and type(jsonData["urls"]) != type([]):
          raise Exceptions.DeserilizeException("SiteUpdate.urls not list type")
        siteUpdateObject.urls = jsonData["urls"]
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.urls json-field not found")
      if "filters" in jsonData:
        if jsonData["filters"] != None and type(jsonData["filters"]) != type([]):
          raise Exceptions.DeserilizeException("SiteUpdate.filters not list type")
        siteUpdateObject.filters = self.checkFilters(jsonData["filters"], siteUpdateObject.id)
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.filters json-field not found")
      if "properties" in jsonData:
        if jsonData["properties"] != None and type(jsonData["properties"]) != type({}) and \
        type(jsonData["properties"]) != type([]):
          raise Exceptions.DeserilizeException("SiteUpdate.properties not dict type")
        if type(jsonData["properties"]) == type({}):
          self.checkProperties(jsonData["properties"])
        siteUpdateObject.properties = jsonData["properties"]
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.properties json-field not found")
      siteUpdateObject.state = self.simpleValueExtractor("state", jsonData, int(), "SiteUpdate.state")
      siteUpdateObject.priority = self.simpleValueExtractor("priority", jsonData, int(), "SiteUpdate.priority")
      siteUpdateObject.maxURLs = self.simpleValueExtractor("maxURLs", jsonData, int(), "SiteUpdate.maxURLs")
      siteUpdateObject.maxResources = self.simpleValueExtractor("maxResources", jsonData, int(), \
                                                                "SiteUpdate.maxResources")
      siteUpdateObject.maxErrors = self.simpleValueExtractor("maxErrors", jsonData, int(), "SiteUpdate.maxErrors")
      siteUpdateObject.maxResourceSize = self.simpleValueExtractor("maxResourceSize", jsonData, int(), \
                                                                   "SiteUpdate.maxResourceSize")
      siteUpdateObject.requestDelay = self.simpleValueExtractor("requestDelay", jsonData, int(), \
                                                                "SiteUpdate.requestDelay")
      siteUpdateObject.httpTimeout = self.simpleValueExtractor("httpTimeout", jsonData, int(), "SiteUpdate.httpTimeout")
      siteUpdateObject.errorMask = self.simpleValueExtractor("errorMask", jsonData, int(), "SiteUpdate.errorMask")
      siteUpdateObject.errors = self.simpleValueExtractor("errors", jsonData, int(), "SiteUpdate.errors")
      siteUpdateObject.urlType = self.simpleValueExtractor("urlType", jsonData, int(), "SiteUpdate.urlType")
      siteUpdateObject.contents = self.simpleValueExtractor("contents", jsonData, int(), "SiteUpdate.contents")
      siteUpdateObject.processingDelay = self.simpleValueExtractor("processingDelay", jsonData, int(), \
                                                                   "SiteUpdate.processingDelay")
      siteUpdateObject.size = self.simpleValueExtractor("size", jsonData, int(), "SiteUpdate.size")
      siteUpdateObject.avgSpeed = self.simpleValueExtractor("avgSpeed", jsonData, int(), "SiteUpdate.avgSpeed")
      siteUpdateObject.avgSpeedCounter = self.simpleValueExtractor("avgSpeedCounter", jsonData, int(), \
                                                                   "SiteUpdate.avgSpeedCounter")
      siteUpdateObject.userId = self.simpleValueExtractor("userId", jsonData, int(), "SiteUpdate.userId")
      siteUpdateObject.recrawlPeriod = self.simpleValueExtractor("recrawlPeriod", jsonData, int(), \
                                                                 "siteUpdateObject.recrawlPeriod")
      siteUpdateObject.maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", jsonData, int(), \
                                                                   "siteUpdateObject.maxURLsFromPage")
      if "recrawlDate" in jsonData:
        siteUpdateObject.recrawlDate = self.timeExtractor(jsonData["recrawlDate"])
      else:
        raise Exceptions.DeserilizeException("siteUpdateObject.recrawlDate json-field not found")
      
      if "criterions" in jsonData and jsonData["criterions"] != None:
        if type(jsonData["criterions"]) != type({}):
          raise Exceptions.DeserilizeException("URLCleanup.criterions json-field type")
        if hasattr(siteUpdateObject.criterions, '__iter__'):
          siteUpdateObject.criterions.update(jsonData["criterions"])
        else:
          siteUpdateObject.criterions = jsonData["criterions"]
    except (Exceptions.DeserilizeException):
      raise
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return siteUpdateObject


  # #siteUpdateDeserialize method, deserializes incoming jsonData to the SiteUpdate object
  # jsonData - incoming json string
  def siteFindDeserialize(self, jsonData):
    siteFindObject = dc.EventObjects.SiteFind("")
    try:
      if "url" in jsonData:
        # if jsonData["url"] is None or jsonData["url"] == "":
        #  raise Exceptions.DeserilizeException("SiteFind.url not exist or empty")
        siteFindObject.url = jsonData["url"]
      if "criterions" in jsonData and jsonData["criterions"] != None:
        if type(jsonData["criterions"]) != type({}):
          raise Exceptions.DeserilizeException("URLFetch.sitesCriterions json-field type not dict")
        siteFindObject.criterions.update(jsonData["criterions"])
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return siteFindObject


  # #siteStatusDeserialize method, deserializes incoming jsonData to the SiteStatus object
  # jsonData - incoming json string
  def siteStatusDeserialize(self, jsonData):
    siteStatusObject = dc.EventObjects.SiteStatus("")
    try:
      if "id" in jsonData:
        siteStatusObject.id = jsonData["id"]
      else:
        raise Exceptions.DeserilizeException("SiteStatus.id json-field not found")
      if "deleteTaskId" in jsonData:
        if jsonData["deleteTaskId"] == None:
          siteStatusObject.deleteTaskId = jsonData["deleteTaskId"]
        else:
          siteStatusObject.deleteTaskId = int(jsonData["deleteTaskId"])
      else:
        raise Exceptions.DeserilizeException("SiteStatus.deleteTaskId json-field not found")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return siteStatusObject


  # #siteDeleteDeserialize method, deserializes incoming jsonData to the SiteDelete object
  # jsonData - incoming json string
  def siteDeleteDeserialize(self, jsonData):
    siteDeleteObject = dc.EventObjects.SiteDelete("")
    try:
      if "id" in jsonData:
        siteDeleteObject.id = jsonData["id"]
      else:
        raise Exceptions.DeserilizeException("SiteDelete.id json-field not found")
      if "taskType" in jsonData:
        siteDeleteObject.taskType = int(jsonData["taskType"])
      else:
        raise Exceptions.DeserilizeException("SiteDelete.taskType json-field not found")
    except ValueError:
      raise Exceptions.DeserilizeException("some field has invalid type")
    return siteDeleteObject


  # #siteCleanupDeserialize method, deserializes incoming jsonData to the SiteCleanup object
  # jsonData - incoming json string
  def siteCleanupDeserialize(self, jsonData):
    siteCleanupObject = dc.EventObjects.SiteCleanup("")
    try:
      if "id" in jsonData:
        siteCleanupObject.id = jsonData["id"]
      else:
        raise Exceptions.DeserilizeException("SiteCleanup.id json-field not found")
      if "taskType" in jsonData:
        siteCleanupObject.taskType = int(jsonData["taskType"])
      else:
        raise Exceptions.DeserilizeException("SiteCleanup.taskType json-field not found")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return siteCleanupObject


  # #URLNewDeserialize method, deserializes incoming jsonData to the URL object
  # jsonData - incoming json string
  def URLNewDeserialize(self, jsonData):
    URLNewObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLNewObject.append(dc.EventObjects.URL(0, ""))
          URLNewObject[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "URLNew.siteId", i)
          if "url" in elem:
            URLNewObject[i].url = str(elem["url"])
          else:
            raise Exceptions.DeserilizeException("URLNew.url json-field not found in {0} elem".format(i))
          URLNewObject[i].type = self.simpleValueExtractor("type", elem, int(), "URLNew.type", i)
          URLNewObject[i].state = self.simpleValueExtractor("state", elem, int(), "URLNew.state", i)
          URLNewObject[i].status = self.simpleValueExtractor("status", elem, int(), "URLNew.status", i)
          URLNewObject[i].siteSelect = self.simpleValueExtractor("siteSelect", elem, int(), "URLNew.siteSelect", i)
          URLNewObject[i].crawled = self.simpleValueExtractor("crawled", elem, int(), "URLNew.crawled", i)
          URLNewObject[i].processed = self.simpleValueExtractor("processed", elem, int(), "URLNew.processed", i)
          URLNewObject[i].urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "URLNew.urlMd5", i)
          if URLNewObject[i].urlMd5 == None:
            URLNewObject[i].fillMD5 = hashlib.md5(URLNewObject[i].url).hexdigest()
          URLNewObject[i].contentType = self.simpleValueExtractor("contentType", elem, str(), "URLNew.contentType", i)
          URLNewObject[i].requestDelay = self.simpleValueExtractor("requestDelay", elem, int(), \
                                                                   "URLNew.requestDelay", i)
          URLNewObject[i].processingDelay = self.simpleValueExtractor("processingDelay", elem, int(), \
                                                                   "URLNew.processingDelay", i)
          URLNewObject[i].httpTimeout = self.simpleValueExtractor("httpTimeout", elem, int(), "URLNew.httpTimeout", i)
          URLNewObject[i].charset = self.simpleValueExtractor("charset", elem, str(), "URLNew.charset", i)
          URLNewObject[i].batchId = self.simpleValueExtractor("batchId", elem, int(), "URLNew.batchId", i)
          URLNewObject[i].errorMask = self.simpleValueExtractor("errorMask", elem, int(), "URLNew.errorMask", i)
          URLNewObject[i].crawlingTime = self.simpleValueExtractor("crawlingTime", elem, int(), \
                                                                   "URLNew.crawlingTime", i)
          URLNewObject[i].processingTime = self.simpleValueExtractor("processingTime", elem, int(), \
                                                                     "URLNew.processingTime", i)
          URLNewObject[i].totalTime = self.simpleValueExtractor("totalTime", elem, int(), "URLNew.totalTime", i)
          URLNewObject[i].httpCode = self.simpleValueExtractor("httpCode", elem, int(), "URLNew.httpCode", i)
          if "UDate" in elem:
            URLNewObject[i].UDate = self.timeExtractor(elem["UDate"])
          else:
            raise Exceptions.DeserilizeException("URLNew.UDate json-field not found in {0} elem".format(i))
          if "CDate" in elem:
            URLNewObject[i].CDate = self.timeExtractor(elem["CDate"])
          else:
            raise Exceptions.DeserilizeException("URLNew.CDate json-field not found in {0} elem".format(i))
          URLNewObject[i].httpMethod = self.simpleValueExtractor("httpMethod", elem, str(), "URLNew.httpMethod", i)
          URLNewObject[i].size = self.simpleValueExtractor("size", elem, int(), "URLNew.size", i)
          URLNewObject[i].linksI = self.simpleValueExtractor("linksI", elem, int(), "URLNew.linksI", i)
          URLNewObject[i].linksE = self.simpleValueExtractor("linksE", elem, int(), "URLNew.linksE", i)
          URLNewObject[i].freq = self.simpleValueExtractor("freq", elem, int(), "URLNew.freq", i)
          URLNewObject[i].depth = self.simpleValueExtractor("depth", elem, int(), "URLNew.depth", i)
          URLNewObject[i].rawContentMd5 = self.simpleValueExtractor("rawContentMd5", elem, str(), \
                                                                    "URLNew.rawContentMd5", i)
          URLNewObject[i].parentMd5 = self.simpleValueExtractor("parentMd5", elem, str(), \
                                                                    "URLNew.parentMd5", i)
          if "lastModified" in elem:
            URLNewObject[i].lastModified = self.timeExtractor(elem["lastModified"])
          else:
            raise Exceptions.DeserilizeException("URLNew.lastModified json-field not found in {0} elem".format(i))
          URLNewObject[i].eTag = self.simpleValueExtractor("eTag", elem, str(), "URLNew.eTag", i)
          URLNewObject[i].mRate = self.simpleValueExtractor("mRate", elem, int(), "URLNew.mRate", i)
          URLNewObject[i].mRateCounter = self.simpleValueExtractor("mRateCounter", elem, int(), \
                                                                   "URLNew.mRateCounter", i)
          URLNewObject[i].maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", elem, int(), \
                                                                   "URLNew.maxURLsFromPage", i)
          if "tcDate" in elem:
            URLNewObject[i].tcDate = self.timeExtractor(elem["tcDate"])
          else:
            raise Exceptions.DeserilizeException("URLNew.tcDate json-field not found in {0} elem".format(i))
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLNew not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLNewObject


  # #URLStatusDeserialize method, deserializes incoming jsonData to the [URLStatus] object
  # jsonData - incoming json string
  def URLStatusDeserialize(self, jsonData):
    URLStatusObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLStatusObject.append(dc.EventObjects.URLStatus(0, ""))
          if "siteId" in elem:
            URLStatusObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLStatus.siteId json-field not found in {0} elem".format(i))
          if "url" in elem:
            URLStatusObject[i].url = str(elem["url"])
          else:
            raise Exceptions.DeserilizeException("URLStatus.url json-field not found in {0} elem".format(i))
          if "urlType" in elem:
            URLStatusObject[i].urlType = int(elem["urlType"])
          else:
            raise Exceptions.DeserilizeException("URLStatus.urlType json-field not found in {0} elem".format(i))
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLStatus not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLStatusObject


  # #URLUpdateDeserialize method, deserializes incoming jsonData to the [URLUpdate] object
  # jsonData - incoming json string
  def URLUpdateDeserialize(self, jsonData):
    URLUpdateObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLUpdateObject.append(dc.EventObjects.URLUpdate(0, ""))
          if "siteId" in elem:
            URLUpdateObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLUpdate.siteId json-field not found in {0} elem".format(i))
          URLUpdateObject[i].url = self.simpleValueExtractor("url", elem, str(), "URLUpdate.url", i)
          URLUpdateObject[i].type = self.simpleValueExtractor("type", elem, int(), "URLUpdate.type", i)
          if "urlMd5" in elem:
            URLUpdateObject[i].urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "URLUpdate.urlMd5", i)
          else:
            URLUpdateObject[i].urlMd5 = None
          if URLUpdateObject[i].urlMd5 == None:
            URLUpdateObject[i].fillMD5(URLUpdateObject[i].url, URLUpdateObject[i].type)
          URLUpdateObject[i].state = self.simpleValueExtractor("state", elem, int(), "URLUpdate.state", i)
          URLUpdateObject[i].status = self.simpleValueExtractor("status", elem, int(), "URLUpdate.status", i)
          URLUpdateObject[i].siteSelect = self.simpleValueExtractor("siteSelect", elem, int(), \
                                                                    "URLUpdate.siteSelect", i)
          URLUpdateObject[i].crawled = self.simpleValueExtractor("crawled", elem, int(), "URLUpdate.crawled", i)
          URLUpdateObject[i].processed = self.simpleValueExtractor("processed", elem, int(), "URLUpdate.processed", i)
          URLUpdateObject[i].contentType = self.simpleValueExtractor("contentType", elem, str(), \
                                                                     "URLUpdate.contentType", i)
          URLUpdateObject[i].requestDelay = self.simpleValueExtractor("requestDelay", elem, int(), \
                                                                      "URLUpdate.requestDelay", i)
          URLUpdateObject[i].processingDelay = self.simpleValueExtractor("processingDelay", elem, int(), \
                                                                   "URLUpdateObject.processingDelay", i)
          URLUpdateObject[i].httpTimeout = self.simpleValueExtractor("httpTimeout", elem, int(), \
                                                                     "URLUpdate.httpTimeout", i)
          URLUpdateObject[i].charset = self.simpleValueExtractor("charset", elem, str(), "URLUpdate.charset", i)
          URLUpdateObject[i].batchId = self.simpleValueExtractor("batchId", elem, int(), "URLUpdate.batchId", i)
          URLUpdateObject[i].errorMask = self.simpleValueExtractor("errorMask", elem, int(), "URLUpdate.errorMask", i)
          URLUpdateObject[i].crawlingTime = self.simpleValueExtractor("crawlingTime", elem, int(), \
                                                                      "URLUpdate.crawlingTime", i)
          URLUpdateObject[i].processingTime = self.simpleValueExtractor("processingTime", elem, int(), \
                                                                      "URLUpdate.processingTime", i)
          URLUpdateObject[i].totalTime = self.simpleValueExtractor("totalTime", elem, int(), "URLUpdate.totalTime", i)
          URLUpdateObject[i].httpCode = self.simpleValueExtractor("httpCode", elem, int(), "URLUpdate.httpCode", i)

          if "UDate" in elem:
            URLUpdateObject[i].UDate = self.timeExtractor(elem["UDate"])
          else:
            raise Exceptions.DeserilizeException("URLNew.UDate json-field not found in {0} elem".format(i))
          if "CDate" in elem:
            URLUpdateObject[i].CDate = self.timeExtractor(elem["CDate"])
          else:
            raise Exceptions.DeserilizeException("URLNew.CDate json-field not found in {0} elem".format(i))
          URLUpdateObject[i].httpMethod = self.simpleValueExtractor("httpMethod", elem, str(), \
                                                                     "URLUpdateObject.httpMethod", i)
          URLUpdateObject[i].size = self.simpleValueExtractor("size", elem, int(), "URLUpdateObject.size", i)
          URLUpdateObject[i].linksI = self.simpleValueExtractor("linksI", elem, int(), "URLUpdateObject.linksI", i)
          URLUpdateObject[i].linksE = self.simpleValueExtractor("linksE", elem, int(), "URLUpdateObject.linksE", i)
          URLUpdateObject[i].freq = self.simpleValueExtractor("freq", elem, int(), "URLUpdateObject.freq", i)
          URLUpdateObject[i].depth = self.simpleValueExtractor("depth", elem, int(), "URLUpdateObject.depth", i)
          URLUpdateObject[i].rawContentMd5 = self.simpleValueExtractor("rawContentMd5", elem, str(), \
                                                                    "URLNew.rawContentMd5", i)
          URLUpdateObject[i].parentMd5 = self.simpleValueExtractor("parentMd5", elem, str(), \
                                                                    "URLUpdateObject.parentMd5", i)
          if "lastModified" in elem:
            URLUpdateObject[i].lastModified = self.timeExtractor(elem["lastModified"])
          else:
            raise Exceptions.DeserilizeException("URLUpdateObject.lastModified " +
                                                 "json-field not found in {0} elem".format(i))
          URLUpdateObject[i].eTag = self.simpleValueExtractor("eTag", elem, str(), "URLUpdateObject.eTag", i)
          URLUpdateObject[i].mRate = self.simpleValueExtractor("mRate", elem, int(), "URLUpdateObject.mRate", i)
          URLUpdateObject[i].mRateCounter = self.simpleValueExtractor("mRateCounter", elem, int(), \
                                                                   "URLUpdateObject.mRateCounter", i)
          URLUpdateObject[i].maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", elem, int(), \
                                                                   "URLUpdateObject.maxURLsFromPage", i)
          if "tcDate" in elem:
            URLUpdateObject[i].tcDate = self.timeExtractor(elem["tcDate"])
          else:
            raise Exceptions.DeserilizeException("URLUpdateObject.tcDate json-field not found in {0} elem".format(i))
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLUpdate not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLUpdateObject


  # #URLFetchDeserialize method, deserializes incoming jsonData to the URLFetch object
  # jsonData - incoming json string
  def URLFetchDeserializeOneElem(self, elem, i):
    localObject = dc.EventObjects.URLFetch()
    if "sitesList" in elem:
      if type(elem["sitesList"]) != type([]):
        raise Exceptions.DeserilizeException("URLFetch.sitesList json-field type not list in {0} elem".format(i))
      localObject.sitesList = elem["sitesList"]
    else:
      raise Exceptions.DeserilizeException("URLFetch.sitesList json-field not found in {0} elem".format(i))
    if "sitesCriterions" in elem and elem["sitesCriterions"] != None:
      if type(elem["sitesCriterions"]) != type({}):
        raise Exceptions.DeserilizeException(("URLFetch.sitesCriterions json-field type" +
                                              " not list in {0} elem").format(i))
      if hasattr(localObject.sitesCriterions, '__iter__'):
        localObject.sitesCriterions.update(elem["sitesCriterions"])
      else:
        localObject.sitesCriterions = elem["sitesCriterions"]
    if "urlsCriterions" in elem and elem["urlsCriterions"] != None:
      if type(elem["urlsCriterions"]) != type({}):
        raise Exceptions.DeserilizeException(("URLFetch.urlsCriterions json-field type" +
                                              " not list in {0} elem").format(i))
      if hasattr(localObject.urlsCriterions, '__iter__'):
        localObject.urlsCriterions.update(elem["urlsCriterions"])
      else:
        localObject.urlsCriterions = elem["urlsCriterions"]
    localObject.maxURLs = self.simpleValueExtractor("maxURLs", elem, int(), "URLFetch.maxURLs", i)
    if localObject.maxURLs == None:
      localObject.maxURLs = dc.EventObjects.URLFetch.DEFAULT_LIMIT
    localObject.algorithm = self.simpleValueExtractor("algorithm", elem, int(), "URLFetch.algorithm", i)
    if localObject.algorithm == None:
      localObject.algorithm = dc.EventObjects.URLFetch.DEFAULT_ALGORITHM
    return localObject


  # #URLFetchDeserialize method, deserializes incoming jsonData to the list of URLFetch objects
  # jsonData - incoming json string
  def URLFetchDeserialize(self, jsonData):
    URLFetchObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLFetchObject.append(self.URLFetchDeserializeOneElem(elem, i))
          i += 1
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLFetchObject


  # #URLDeleteDeserialize method, deserializes incoming jsonData to the [URLDelete] object
  # jsonData - incoming json string
  def URLDeleteDeserialize(self, jsonData):
    URLDeleteObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLDeleteObject.append(dc.EventObjects.URLDelete(0, ""))
          if "siteId" in elem:
            URLDeleteObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLDelete.siteId json-field not found in {0} elem".format(i))
          URLDeleteObject[i].url = self.simpleValueExtractor("url", elem, str(), "URLDeleteObject.url", i)
          if "urlType" in elem:
            URLDeleteObject[i].urlType = str(elem["urlType"])
          else:
            raise Exceptions.DeserilizeException("URLDelete.urlType json-field not found in {0} elem".format(i))
          if "criterions" in elem and elem["criterions"] != None:
            if type(elem["criterions"]) != type({}):
              raise Exceptions.DeserilizeException(("URLDelete.criterions json-field type" +
                                                    " not list in {0} elem").format(i))
            if hasattr(URLDeleteObject[i].criterions, '__iter__'):
              URLDeleteObject[i].criterions.update(elem["criterions"])
            else:
              URLDeleteObject[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLDelete not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLDeleteObject


  # #URLCleanupDeserialize method, deserializes incoming jsonData to the [URLCleanup] object
  # jsonData - incoming json string
  def URLCleanupDeserialize(self, jsonData):
    URLCleanupObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLCleanupObject.append(dc.EventObjects.URLCleanup(0, ""))
          if "siteId" in elem:
            URLCleanupObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLCleanupObject.siteId json-field not found in {0} elem".format(i))
          URLCleanupObject[i].url = self.simpleValueExtractor("url", elem, str(), "URLCleanupObject.url", i)
          if "urlType" in elem:
            URLCleanupObject[i].urlType = str(elem["urlType"])
          else:
            raise Exceptions.DeserilizeException("URLCleanup.urlType json-field not found in {0} elem".format(i))
          if "state" in elem:
            URLCleanupObject[i].state = str(elem["state"])
          else:
            raise Exceptions.DeserilizeException("URLCleanup.state json-field not found in {0} elem".format(i))
          if "status" in elem:
            URLCleanupObject[i].status = str(elem["status"])
          else:
            raise Exceptions.DeserilizeException("URLCleanup.status json-field not found in {0} elem".format(i))
          if "criterions" in elem and elem["criterions"] != None:
            if type(elem["criterions"]) != type({}):
              raise Exceptions.DeserilizeException(("URLCleanup.criterions json-field type" +
                                                    " not list in {0} elem").format(i))
            if hasattr(URLCleanupObject[i].criterions, '__iter__'):
              URLCleanupObject[i].criterions.update(elem["criterions"])
            else:
              URLCleanupObject[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLDelete not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLCleanupObject


  # #URLContentDeserialize method, deserializes incoming jsonData to the [URLContentRequest] object
  # jsonData - incoming json string
  def URLContentDeserialize(self, jsonData):
    URLContentObject = []
    i = 0
    try:
      if type(jsonData) == type([]):
        for elem in jsonData:
          URLContentObject.append(dc.EventObjects.URLContentRequest(0, ""))
          if "siteId" in elem:
            URLContentObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLContentObject.siteId json-field not found in {0} elem".format(i))
          if "url" in elem:
            URLContentObject[i].url = str(elem["url"])
          else:
            raise Exceptions.DeserilizeException("URLContentObject.url json-field not found in {0} elem".format(i))
          if "contentTypeMask" in elem:
            URLContentObject[i].contentTypeMask = int(elem["contentTypeMask"])
          else:
            raise Exceptions.DeserilizeException("URLContentObject.contentTypeMask json-field not found in {0} elem".\
                                              format(i))
          if "urlMd5" in elem:
            URLContentObject[i].urlMd5 = str(elem["urlMd5"])
          else:
            URLContentObject[i].fillMD5(URLContentObject[i].url)
          if "urlFetch" in elem and elem["urlFetch"] != None:
            URLContentObject[i].urlFetch = self.URLFetchDeserializeOneElem(elem["urlFetch"], 0)
          else:
            URLContentObject[i].urlFetch = None
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLContentObject not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("some field has invalid type")
    return URLContentObject
