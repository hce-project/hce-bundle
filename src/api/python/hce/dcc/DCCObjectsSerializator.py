'''
Created on Apr 11, 2014

@package: dc
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import hashlib
import types
import dc.EventObjects
import dbi.EventObjects
from app.Utils import SQLExpression
import app.Exceptions as Exceptions
from app.Utils import UrlNormalizator
# from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #DTMCObjectsSerializator Class contents serialize/deserialize methods for incoming "DTMC" commands
#
class DCCObjectsSerializator(object):

  def __init__(self):
    pass


  # #timeExtractor method, extracts time in various format
  def timeExtractor(self, timeField):
    ret = None
    if timeField is not None:
      if type(timeField) in types.StringTypes:
      # if type(timeField) == type("") or type(timeField) == type(unicode("")):
        ret = SQLExpression(str(timeField))
      elif type(timeField) is types.DictType:
      # elif type(timeField) == type({}):
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
    if filters is not None:
      ret = []
      for localFilter in filters:
        if "siteId" in localFilter and localFilter["siteId"] is not None:
          siteId = str(localFilter["siteId"])
        else:
          siteId = sid
        if "pattern" not in localFilter or localFilter["pattern"] is None:
          raise Exceptions.DeserilizeException(".filters pattern not found or None")
        if "type" not in localFilter:
          siteFilter = dc.EventObjects.SiteFilter(siteId, str(localFilter["pattern"]))
        else:
          siteFilter = dc.EventObjects.SiteFilter(siteId, str(localFilter["pattern"]), int(localFilter["type"]))
        if "subject" in localFilter and localFilter["subject"] is not None:
          siteFilter.subject = str(localFilter["subject"])
        if "opCode" in localFilter and localFilter["opCode"] is not None:
          siteFilter.opCode = int(localFilter["opCode"])
        if "stage" in localFilter and localFilter["stage"] is not None:
          siteFilter.stage = int(localFilter["stage"])
        if "action" in localFilter and localFilter["action"] is not None:
          siteFilter.action = int(localFilter["action"])
        if "mode" in localFilter and localFilter["mode"] is not None:
          siteFilter.mode = int(localFilter["mode"])
        if "state" in localFilter and localFilter["state"] is not None:
          siteFilter.state = int(localFilter["state"])
        if "uDate" in localFilter:
          siteFilter.uDate = self.timeExtractor(localFilter["uDate"])
        if "groupId" in localFilter:
          siteFilter.groupId = int(localFilter["groupId"])
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
      if ret is not None:
        ret = type(_type)(ret)
    else:
      if i is None:
        raise Exceptions.DeserilizeException("%s json-field not found" % excepStr)
      else:
        raise Exceptions.DeserilizeException("%s json-field not found in [%s] elem" % (excepStr, str(i)))
    return ret


  # #fillSiteURLs method, fills dc.EventObjects.SiteURL object
  # jsonData - json container
  # siteId - site's id value
  # returns dc.EventObjects.SiteURL object
  def fillSiteURLs(self, jsonData, siteId, userId=None, urlNormalizeMask=UrlNormalizator.NORM_NONE):
    ret = None
    if "url" in jsonData and jsonData["url"] is not None:
      ret = dc.EventObjects.SiteURL(siteId, jsonData["url"], normalizeMask=urlNormalizeMask)
      ret.userId = userId
      for key in jsonData:
        if hasattr(ret, key) and jsonData[key] is not None and key != "url":
          setattr(ret, key, jsonData[key])
    else:
      logger.error(">>> Some URL-dict elem doesn't content url field")
    return ret


  # #readBatchItems method, reads and returns bathitem list
  # jsonData - json container
  # returns batcjItem list
  def readBatchItems(self, jsonData):
    ret = []
    i = 0
    if hasattr(jsonData, '__iter__'):
      for elem in jsonData:
        localSiteId = self.simpleValueExtractor("siteId", elem, str(), "BatchItem.siteId", i)
        localUrlId = self.simpleValueExtractor("urlId", elem, str(), "BatchItem.urlId", i)
        if "urlObj" in elem and elem["urlObj"] is not None:
          localUrlObj = dc.EventObjects.URL(0, "")
          self.URLNewElementDeserialize(localUrlObj, elem["urlObj"], i)
        else:
          raise Exceptions.DeserilizeException("BatchItem.urlObj json-field not found in {0} elem".format(i))

        localBatchItem = dc.EventObjects.BatchItem(localSiteId, localUrlId, localUrlObj)
        if "properties" in elem and elem["properties"] is not None and type(elem["properties"]) is types.DictType:
          localBatchItem.properties = elem["properties"]
        if "siteObj" in elem and elem["siteObj"] is not None:
          localBatchItem.siteObj = self.siteNewDeserialize(elem["siteObj"])
        if "depth" in elem:
          localBatchItem.depth = self.simpleValueExtractor("depth", elem, int(), "BatchItem.depth", i)
        ret.append(localBatchItem)
        i = i + 1

    return ret


  # #siteNewDeserialize method, deserializes incoming jsonData to the Site object
  # jsonData - incoming json string
  def siteNewDeserialize(self, jsonData):
    siteObject = None
    try:
      if "id" in jsonData and jsonData["id"] is not None:
        siteObject = dc.EventObjects.Site("")
        siteObject.id = str(jsonData["id"])
      else:
        if "urls" in jsonData and hasattr(jsonData["urls"], '____') and \
          len(jsonData["urls"]) > 0 and jsonData["urls"][0] is not None:
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
      siteObject.userId = self.simpleValueExtractor("userId", jsonData, int(), "Site.userId")

      if "urls" in jsonData:
        if jsonData["urls"] is None:
          siteObject.urls = None
        elif not isinstance(jsonData["urls"], list):
          raise Exceptions.DeserilizeException("Site.urls not list type")
        else:
          for jsonUrl in jsonData["urls"]:
            localRet = None
            if isinstance(jsonUrl, dict):
              localRet = self.fillSiteURLs(jsonUrl, siteObject.id, siteObject.userId,
                                           int(jsonUrl["_normalizeMask"]) if "_normalizeMask" in jsonUrl else \
                                           UrlNormalizator.NORM_NONE)
            elif type(jsonUrl) in types.StringTypes:
              localRet = dc.EventObjects.SiteURL(siteId=siteObject.id, url=jsonUrl,
                                                 normalizeMask=int(jsonData["_urlNormalizeMask"])\
                                                 if "_urlNormalizeMask" in jsonData else UrlNormalizator.NORM_NONE)
              localRet.userId = siteObject.userId
            if localRet is not None:
              if siteObject.urls is None:
                siteObject.urls = []
              siteObject.urls.append(localRet)
      else:
        raise Exceptions.DeserilizeException("Site.urls json-field not found")

      if "filters" in jsonData:
        if jsonData["filters"] is not None and type(jsonData["filters"]) is not types.ListType:
          raise Exceptions.DeserilizeException("Site.filters not list type")
        siteObject.filters = self.checkFilters(jsonData["filters"], siteObject.id)
      else:
        raise Exceptions.DeserilizeException("Site.filters json-field not found")
      if "properties" in jsonData:
        if jsonData["properties"] is not None and type(jsonData["properties"]) is not types.DictType and \
        type(jsonData["properties"]) is not types.ListType:
          raise Exceptions.DeserilizeException("Site.properties not dict/list type")
        if type(jsonData["properties"]) is not types.ListType:
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
      siteObject.httpTimeout = self.simpleValueExtractor("httpTimeout", jsonData, float(), "Site.httpTimeout")
      siteObject.errorMask = self.simpleValueExtractor("errorMask", jsonData, int(), "Site.errorMask")
      siteObject.errors = self.simpleValueExtractor("errors", jsonData, int(), "Site.errors")
      siteObject.urlType = self.simpleValueExtractor("urlType", jsonData, int(), "Site.urlType")
      siteObject.contents = self.simpleValueExtractor("contents", jsonData, int(), "Site.contents")
      siteObject.processingDelay = self.simpleValueExtractor("processingDelay", jsonData, int(), "Site.processingDelay")
      siteObject.size = self.simpleValueExtractor("size", jsonData, int(), "Site.size")
      siteObject.avgSpeed = self.simpleValueExtractor("avgSpeed", jsonData, int(), "Site.avgSpeed")
      siteObject.avgSpeedCounter = self.simpleValueExtractor("avgSpeedCounter", jsonData, int(), "Site.avgSpeedCounter")
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
      if "newURLs" in jsonData:
        siteObject.newURLs = self.simpleValueExtractor("newURLs", jsonData, int(), "Site.newURLs")
      if "deletedURLs" in jsonData:
        siteObject.deletedURLs = self.simpleValueExtractor("deletedURLs", jsonData, int(), "Site.deletedURLs")
      if "moveURLs" in jsonData and jsonData["moveURLs"] is not None:
        siteObject.moveURLs = self.simpleValueExtractor("moveURLs", jsonData, int(), "Site.moveURLs")
        siteObject.moveURLs = bool(siteObject.moveURLs)
      if "tcDateProcess" in jsonData:
        siteObject.tcDateProcess = self.timeExtractor(jsonData["tcDateProcess"])
      if "categoryId" in jsonData:
        siteObject.categoryId = self.simpleValueExtractor("categoryId", jsonData, int(), "Site.categoryId")
    except Exceptions.DeserilizeException, e:
      raise e
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("siteNewDeserialize, some field has invalid type")
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
      siteUpdateObject.userId = self.simpleValueExtractor("userId", jsonData, int(), "SiteUpdate.userId")

      if "urls" in jsonData:
        if jsonData["urls"] is None:
          siteUpdateObject.urls = None
        elif not isinstance(jsonData["urls"], list):
          raise Exceptions.DeserilizeException("SiteUpdate.urls not list type")
        else:
          siteUpdateObject.urls = []
          for jsonUrl in jsonData["urls"]:
            localRet = None
            if isinstance(jsonUrl, dict):
              localRet = self.fillSiteURLs(jsonUrl, siteUpdateObject.id, siteUpdateObject.userId,
                                           int(jsonUrl["_normalizeMask"]) if "_normalizeMask" in jsonUrl else \
                                           UrlNormalizator.NORM_NONE)
            elif isinstance(jsonUrl, basestring):
              localRet = dc.EventObjects.SiteURL(siteId=siteUpdateObject.id, url=jsonUrl,
                                                 normalizeMask=int(jsonData["_urlNormalizeMask"])\
                                                 if "_urlNormalizeMask" in jsonData else UrlNormalizator.NORM_NONE)
              localRet.userId = siteUpdateObject.userId
            if localRet is not None:
              siteUpdateObject.urls.append(localRet)
        # TODO remove it in feauture
        if siteUpdateObject.urls is not None:
          for url in siteUpdateObject.urls:
            url.status = dc.EventObjects.URL.STATUS_PROCESSED
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.urls json-field not found")

      if "filters" in jsonData:
        if jsonData["filters"] is not None and type(jsonData["filters"]) is not types.ListType:
          raise Exceptions.DeserilizeException("SiteUpdate.filters not list type")
        siteUpdateObject.filters = self.checkFilters(jsonData["filters"], siteUpdateObject.id)
      else:
        raise Exceptions.DeserilizeException("SiteUpdate.filters json-field not found")
      if "properties" in jsonData:
        if jsonData["properties"] is not None and type(jsonData["properties"]) is not types.DictType and \
        type(jsonData["properties"]) is not types.ListType:
          raise Exceptions.DeserilizeException("SiteUpdate.properties not dict type")
        if type(jsonData["properties"]) is types.DictType:
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
      siteUpdateObject.httpTimeout = self.simpleValueExtractor("httpTimeout", jsonData, float(), "SiteUpdate.httpTimeout")
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
      siteUpdateObject.recrawlPeriod = self.simpleValueExtractor("recrawlPeriod", jsonData, int(), \
                                                                 "siteUpdateObject.recrawlPeriod")
      siteUpdateObject.maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", jsonData, int(), \
                                                                   "siteUpdateObject.maxURLsFromPage")
      if "recrawlDate" in jsonData:
        siteUpdateObject.recrawlDate = self.timeExtractor(jsonData["recrawlDate"])
      else:
        raise Exceptions.DeserilizeException("siteUpdateObject.recrawlDate json-field not found")

      if "criterions" in jsonData and jsonData["criterions"] is not None:
        if type(jsonData["criterions"]) is not types.DictType:
          raise Exceptions.DeserilizeException("URLCleanup.criterions json-field type")
        if hasattr(siteUpdateObject.criterions, '__iter__'):
          siteUpdateObject.criterions.update(jsonData["criterions"])
        else:
          siteUpdateObject.criterions = jsonData["criterions"]
      siteUpdateObject.collectedURLs = self.simpleValueExtractor("collectedURLs",
                                                                 jsonData, int(), "siteUpdateObject.collectedURLs")
      siteUpdateObject.fetchType = self.simpleValueExtractor("fetchType", jsonData, int(), "siteUpdateObject.fetchType")
      if "newURLs" in jsonData:
        siteUpdateObject.newURLs = self.simpleValueExtractor("newURLs", jsonData, int(), "siteUpdateObject.newURLs")
      if "deletedURLs" in jsonData:
        siteUpdateObject.deletedURLs = self.simpleValueExtractor("deletedURLs", jsonData, int(),
                                                                 "siteUpdateObject.deletedURLs")
      if "tcDateProcess" in jsonData:
        siteUpdateObject.tcDateProcess = self.timeExtractor(jsonData["tcDateProcess"])
      if "categoryId" in jsonData:
        siteUpdateObject.categoryId = self.simpleValueExtractor("categoryId", jsonData, int(),
                                                                "siteUpdateObject.categoryId")
    except Exceptions.DeserilizeException:
      raise
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("siteUpdateDeserialize, some field has invalid type")
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
      if "criterions" in jsonData and jsonData["criterions"] is not None:
        if type(jsonData["criterions"]) is not types.DictType:
          raise Exceptions.DeserilizeException("URLFetch.sitesCriterions json-field type not dict")
        siteFindObject.criterions.update(jsonData["criterions"])
      if "excludeList" in jsonData and type(jsonData["excludeList"]) is types.ListType:
        siteFindObject.excludeList = jsonData["excludeList"]
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("siteFindDeserialize, some field has invalid type")
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
        siteStatusObject.deleteTaskId = jsonData["deleteTaskId"]
      else:
        raise Exceptions.DeserilizeException("SiteStatus.deleteTaskId json-field not found")
      if "excludeList" in jsonData and type(jsonData["excludeList"]) is types.ListType:
        siteStatusObject.excludeList = jsonData["excludeList"]
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("siteStatusDeserialize, some field has invalid type")
    return siteStatusObject


  # #siteDeleteDeserialize method, deserializes incoming jsonData to the SiteDelete object
  # jsonData - incoming json string
  def siteDeleteDeserialize(self, jsonData):
    if type(jsonData) is types.ListType:
      siteDeleteObject = []
      jsonDataElems = jsonData
    else:
      siteDeleteObject = dc.EventObjects.SiteDelete()
      jsonDataElems = [jsonData]

    for elem in jsonDataElems:
      try:
        localSiteDeleteObject = dc.EventObjects.SiteDelete()
        if "id" in elem:
          localSiteDeleteObject.id = elem["id"]
        if "taskType" in elem:
          localSiteDeleteObject.taskType = int(elem["taskType"])
        else:
          raise Exceptions.DeserilizeException("SiteDelete.taskType json-field not found")
        if "delayedType" in elem and elem["delayedType"] is not None:
          localSiteDeleteObject.delayedType = int(elem["delayedType"])
        if "criterions" in elem:
          if type(elem["criterions"]) is not types.DictType:
            raise Exceptions.DeserilizeException("SiteDelete.criterions not dict type")
          if hasattr(localSiteDeleteObject.criterions, '__iter__'):
            localSiteDeleteObject.criterions.update(elem["criterions"])
          else:
            localSiteDeleteObject.criterions = elem["criterions"]
      except ValueError:
        raise Exceptions.DeserilizeException("siteDeleteDeserialize, some field has invalid type")
      if type(jsonData) is types.ListType:
        siteDeleteObject.append(localSiteDeleteObject)
      else:
        siteDeleteObject = localSiteDeleteObject
    return siteDeleteObject


  # #siteCleanupDeserialize method, deserializes incoming jsonData to the SiteCleanup object
  # jsonData - incoming json string
  def siteCleanupDeserialize(self, jsonData):
    if type(jsonData) is types.ListType:
      siteCleanupObject = []
      jsonDataElems = jsonData
    else:
      siteCleanupObject = dc.EventObjects.SiteCleanup("")
      jsonDataElems = [jsonData]

    for elem in jsonDataElems:
      localSiteCleanupObject = dc.EventObjects.SiteCleanup("")
      try:
        if "id" in elem:
          localSiteCleanupObject.id = elem["id"]
        else:
          raise Exceptions.DeserilizeException("SiteCleanup.id json-field not found")
        if "taskType" in elem:
          localSiteCleanupObject.taskType = int(elem["taskType"])
        else:
          raise Exceptions.DeserilizeException("SiteCleanup.taskType json-field not found")
        if "delayedType" in elem and elem["delayedType"] is not None:
          localSiteCleanupObject.delayedType = int(elem["delayedType"])
        if "moveURLs" in elem and elem["moveURLs"] is not None:
          localSiteCleanupObject.moveURLs = self.simpleValueExtractor("moveURLs", elem, int(), "Site.moveURLs")
          localSiteCleanupObject.moveURLs = bool(localSiteCleanupObject.moveURLs)
        if "saveRootURLs" in elem and elem["saveRootURLs"] is not None:
          localSiteCleanupObject.saveRootUrls = self.simpleValueExtractor("saveRootURLs", elem, int(),
                                                                     "Site.saveRootURLs")
          localSiteCleanupObject.saveRootUrls = bool(localSiteCleanupObject.saveRootUrls)
        if "state" in elem and elem["state"] is not None:
          localSiteCleanupObject.state = int(elem["state"])
        if "historyCleanUp" in elem and elem["historyCleanUp"] is not None:
          localSiteCleanupObject.historyCleanUp = int(elem["historyCleanUp"])
      except (ValueError, TypeError):
        raise Exceptions.DeserilizeException("siteCleanupDeserialize, some field has invalid type")
      if type(jsonData) is types.ListType:
        siteCleanupObject.append(localSiteCleanupObject)
      else:
        siteCleanupObject = localSiteCleanupObject
    return siteCleanupObject


  # #URLNewElementDeserialize method, fills data in one URLNew elemet
  #
  def URLNewElementDeserialize(self, urlNewObject, jsonData, i):
    urlNewObject.siteId = self.simpleValueExtractor("siteId", jsonData, str(), "URLNew.siteId", i)
    if "url" in jsonData:
      urlNewObject.url = str(jsonData["url"])
    else:
      raise Exceptions.DeserilizeException("URLNew.url json-field not found in {0} jsonData".format(i))
    urlNewObject.type = self.simpleValueExtractor("type", jsonData, int(), "URLNew.type", i)
    urlNewObject.state = self.simpleValueExtractor("state", jsonData, int(), "URLNew.state", i)
    urlNewObject.status = self.simpleValueExtractor("status", jsonData, int(), "URLNew.status", i)
    urlNewObject.siteSelect = self.simpleValueExtractor("siteSelect", jsonData, int(), "URLNew.siteSelect", i)
    urlNewObject.crawled = self.simpleValueExtractor("crawled", jsonData, int(), "URLNew.crawled", i)
    urlNewObject.processed = self.simpleValueExtractor("processed", jsonData, int(), "URLNew.processed", i)
    urlNewObject.urlMd5 = self.simpleValueExtractor("urlMd5", jsonData, str(), "URLNew.urlMd5", i)
    if urlNewObject.urlMd5 is None:
      urlNewObject.fillMD5 = hashlib.md5(urlNewObject.url).hexdigest()
    urlNewObject.contentType = self.simpleValueExtractor("contentType", jsonData, str(), "URLNew.contentType", i)
    urlNewObject.requestDelay = self.simpleValueExtractor("requestDelay", jsonData, int(), \
                                                             "URLNew.requestDelay", i)
    urlNewObject.processingDelay = self.simpleValueExtractor("processingDelay", jsonData, int(), \
                                                             "URLNew.processingDelay", i)
    urlNewObject.httpTimeout = self.simpleValueExtractor("httpTimeout", jsonData, float(), "URLNew.httpTimeout", i)
    urlNewObject.charset = self.simpleValueExtractor("charset", jsonData, str(), "URLNew.charset", i)
    urlNewObject.batchId = self.simpleValueExtractor("batchId", jsonData, int(), "URLNew.batchId", i)
    urlNewObject.errorMask = self.simpleValueExtractor("errorMask", jsonData, int(), "URLNew.errorMask", i)
    urlNewObject.crawlingTime = self.simpleValueExtractor("crawlingTime", jsonData, int(), \
                                                             "URLNew.crawlingTime", i)
    urlNewObject.processingTime = self.simpleValueExtractor("processingTime", jsonData, int(), \
                                                               "URLNew.processingTime", i)
    urlNewObject.totalTime = self.simpleValueExtractor("totalTime", jsonData, int(), "URLNew.totalTime", i)
    urlNewObject.httpCode = self.simpleValueExtractor("httpCode", jsonData, int(), "URLNew.httpCode", i)
    if "UDate" in jsonData:
      urlNewObject.UDate = self.timeExtractor(jsonData["UDate"])
    else:
      raise Exceptions.DeserilizeException("URLNew.UDate json-field not found in {0} jsonData".format(i))
    if "CDate" in jsonData:
      urlNewObject.CDate = self.timeExtractor(jsonData["CDate"])
    else:
      raise Exceptions.DeserilizeException("URLNew.CDate json-field not found in {0} jsonData".format(i))
    urlNewObject.httpMethod = self.simpleValueExtractor("httpMethod", jsonData, str(), "URLNew.httpMethod", i)
    urlNewObject.size = self.simpleValueExtractor("size", jsonData, int(), "URLNew.size", i)
    urlNewObject.linksI = self.simpleValueExtractor("linksI", jsonData, int(), "URLNew.linksI", i)
    urlNewObject.linksE = self.simpleValueExtractor("linksE", jsonData, int(), "URLNew.linksE", i)
    urlNewObject.freq = self.simpleValueExtractor("freq", jsonData, int(), "URLNew.freq", i)
    urlNewObject.depth = self.simpleValueExtractor("depth", jsonData, int(), "URLNew.depth", i)
    urlNewObject.rawContentMd5 = self.simpleValueExtractor("rawContentMd5", jsonData, str(), \
                                                              "URLNew.rawContentMd5", i)
    urlNewObject.parentMd5 = self.simpleValueExtractor("parentMd5", jsonData, str(), "URLNew.parentMd5", i)
    if "lastModified" in jsonData:
      urlNewObject.lastModified = self.timeExtractor(jsonData["lastModified"])
    else:
      raise Exceptions.DeserilizeException("URLNew.lastModified json-field not found in {0} jsonData".format(i))
    urlNewObject.eTag = self.simpleValueExtractor("eTag", jsonData, str(), "URLNew.eTag", i)
    urlNewObject.mRate = self.simpleValueExtractor("mRate", jsonData, int(), "URLNew.mRate", i)
    urlNewObject.mRateCounter = self.simpleValueExtractor("mRateCounter", jsonData, int(), "URLNew.mRateCounter", i)
    urlNewObject.maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", jsonData, int(), \
                                                             "URLNew.maxURLsFromPage", i)
    if "tcDate" in jsonData:
      urlNewObject.tcDate = self.timeExtractor(jsonData["tcDate"])
    else:
      raise Exceptions.DeserilizeException("URLNew.tcDate json-field not found in {0} jsonData".format(i))
    urlNewObject.tagsMask = self.simpleValueExtractor("tagsMask", jsonData, int(), "URLNew.tagsMask", i)
    urlNewObject.tagsCount = self.simpleValueExtractor("tagsCount", jsonData, int(), "URLNew.tagsCount", i)
    if "pDate" in jsonData:
      urlNewObject.pDate = self.timeExtractor(jsonData["pDate"])
    else:
      raise Exceptions.DeserilizeException("URLNew.pDate json-field not found in {0} jsonData".format(i))
    urlNewObject.contentURLMd5 = self.simpleValueExtractor("contentURLMd5", jsonData, str(), "URLNew.contentURLMd5", i)
    urlNewObject.priority = self.simpleValueExtractor("priority", jsonData, int(), "URLNew.priority", i)
    if "urlUpdate" in jsonData and jsonData["urlUpdate"] is not None:
      urlNewObject.urlUpdate = self.URLUpdateDeserializeOneElem(jsonData["urlUpdate"], 0)
    if "urlPut" in jsonData and jsonData["urlPut"] is not None:
      urlNewObject.urlPut = self.URLPutDeserializeOneElement(jsonData["urlPut"], 0)
    if "chainId" in jsonData:
      urlNewObject.chainId = self.simpleValueExtractor("chainId", jsonData, int(), "URLNew.chainId", i)
    if "classifierMask" in jsonData:
      urlNewObject.classifierMask = self.simpleValueExtractor("classifierMask", jsonData, int(),
                                                              "URLNew.classifierMask", i)
    if "attributes" in jsonData:
      urlNewObject.attributes = []
      for attribute in jsonData["attributes"]:
        if type(attribute) is types.DictType and len(attribute) == 1:
          attrObj = dc.EventObjects.Attribute(urlNewObject.siteId, attribute.keys()[0])
          attrObj.urlMd5 = urlNewObject.urlMd5
          attrObj.value = attribute[attribute.keys()[0]]
          urlNewObject.attributes.append(attrObj)


  # #URLNewDeserialize method, deserializes incoming jsonData to the URL object
  # jsonData - incoming json string
  def URLNewDeserialize(self, jsonData):
    URLNewObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLNewObject.append(dc.EventObjects.URL(0, ""))
          self.URLNewElementDeserialize(URLNewObject[i], elem, i)
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLNew not list type")
    except (ValueError, TypeError) as excp:
      raise Exceptions.DeserilizeException("URLNewDeserialize, some field has invalid type; =" + str(excp))
    return URLNewObject


  # #URLStatusDeserialize method, deserializes incoming jsonData to the [URLStatus] object
  # jsonData - incoming json string
  def URLStatusDeserialize(self, jsonData):
    URLStatusObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
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
      raise Exceptions.DeserilizeException("URLStatusDeserialize, some field has invalid type")
    return URLStatusObject


  # #URLUpdateDeserializeOneElem method, deserializes incoming jsonData to the URLUpdate object
  # jsonData - incoming json string
  def URLUpdateDeserializeOneElem(self, elem, i):
    localObject = dc.EventObjects.URLUpdate(0, "")
    if "siteId" in elem:
      localObject.siteId = str(elem["siteId"])
    else:
      raise Exceptions.DeserilizeException("URLUpdate.siteId json-field not found in {0} elem".format(i))
    localObject.url = self.simpleValueExtractor("url", elem, str(), "URLUpdate.url", i)
    localObject.type = self.simpleValueExtractor("type", elem, int(), "URLUpdate.type", i)
    if "urlMd5" in elem:
      localObject.urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "URLUpdate.urlMd5", i)
    if localObject.urlMd5 is None:
      localObject.fillMD5(localObject.url, localObject.type)
    localObject.state = self.simpleValueExtractor("state", elem, int(), "URLUpdate.state", i)
    localObject.status = self.simpleValueExtractor("status", elem, int(), "URLUpdate.status", i)
    localObject.siteSelect = self.simpleValueExtractor("siteSelect", elem, int(), \
                                                              "URLUpdate.siteSelect", i)
    localObject.crawled = self.simpleValueExtractor("crawled", elem, int(), "URLUpdate.crawled", i)
    localObject.processed = self.simpleValueExtractor("processed", elem, int(), "URLUpdate.processed", i)
    localObject.contentType = self.simpleValueExtractor("contentType", elem, str(), \
                                                               "URLUpdate.contentType", i)
    localObject.requestDelay = self.simpleValueExtractor("requestDelay", elem, int(), \
                                                                "URLUpdate.requestDelay", i)
    localObject.processingDelay = self.simpleValueExtractor("processingDelay", elem, int(), \
                                                             "URLUpdateObject.processingDelay", i)
    localObject.httpTimeout = self.simpleValueExtractor("httpTimeout", elem, float(), \
                                                               "URLUpdate.httpTimeout", i)
    localObject.charset = self.simpleValueExtractor("charset", elem, str(), "URLUpdate.charset", i)
    localObject.batchId = self.simpleValueExtractor("batchId", elem, int(), "URLUpdate.batchId", i)
    localObject.errorMask = self.simpleValueExtractor("errorMask", elem, int(), "URLUpdate.errorMask", i)
    localObject.crawlingTime = self.simpleValueExtractor("crawlingTime", elem, int(), \
                                                                "URLUpdate.crawlingTime", i)
    localObject.processingTime = self.simpleValueExtractor("processingTime", elem, int(), \
                                                                "URLUpdate.processingTime", i)
    localObject.totalTime = self.simpleValueExtractor("totalTime", elem, int(), "URLUpdate.totalTime", i)
    localObject.httpCode = self.simpleValueExtractor("httpCode", elem, int(), "URLUpdate.httpCode", i)

    if "UDate" in elem:
      localObject.UDate = self.timeExtractor(elem["UDate"])
    else:
      raise Exceptions.DeserilizeException("URLNew.UDate json-field not found in {0} elem".format(i))
    if "CDate" in elem:
      localObject.CDate = self.timeExtractor(elem["CDate"])
    else:
      raise Exceptions.DeserilizeException("URLNew.CDate json-field not found in {0} elem".format(i))
    localObject.httpMethod = self.simpleValueExtractor("httpMethod", elem, str(), \
                                                               "URLUpdateObject.httpMethod", i)
    localObject.size = self.simpleValueExtractor("size", elem, int(), "URLUpdateObject.size", i)
    localObject.linksI = self.simpleValueExtractor("linksI", elem, int(), "URLUpdateObject.linksI", i)
    localObject.linksE = self.simpleValueExtractor("linksE", elem, int(), "URLUpdateObject.linksE", i)
    localObject.freq = self.simpleValueExtractor("freq", elem, int(), "URLUpdateObject.freq", i)
    localObject.depth = self.simpleValueExtractor("depth", elem, int(), "URLUpdateObject.depth", i)
    localObject.rawContentMd5 = self.simpleValueExtractor("rawContentMd5", elem, str(), "URLNew.rawContentMd5", i)
    localObject.parentMd5 = self.simpleValueExtractor("parentMd5", elem, str(), "URLUpdateObject.parentMd5", i)
    if "lastModified" in elem:
      localObject.lastModified = self.timeExtractor(elem["lastModified"])
    else:
      raise Exceptions.DeserilizeException("URLUpdateObject.lastModified " +
                                           "json-field not found in {0} elem".format(i))
    localObject.eTag = self.simpleValueExtractor("eTag", elem, str(), "URLUpdateObject.eTag", i)
    localObject.mRate = self.simpleValueExtractor("mRate", elem, int(), "URLUpdateObject.mRate", i)
    localObject.mRateCounter = self.simpleValueExtractor("mRateCounter", elem, int(), \
                                                             "URLUpdateObject.mRateCounter", i)
    localObject.maxURLsFromPage = self.simpleValueExtractor("maxURLsFromPage", elem, int(), \
                                                             "URLUpdateObject.maxURLsFromPage", i)
    if "tcDate" in elem:
      localObject.tcDate = self.timeExtractor(elem["tcDate"])
    else:
      raise Exceptions.DeserilizeException("URLUpdateObject.tcDate json-field not found in {0} elem".format(i))
    localObject.tagsMask = self.simpleValueExtractor("tagsMask", elem, int(), "URLUpdateObject.tagsMask", i)
    localObject.tagsCount = self.simpleValueExtractor("tagsCount", elem, int(), "URLUpdateObject.tagsCount", i)
    if "pDate" in elem:
      localObject.pDate = self.timeExtractor(elem["pDate"])
    else:
      raise Exceptions.DeserilizeException("URLUpdateObject.pDate json-field not found in {0} jsonData".format(i))
    localObject.contentURLMd5 = self.simpleValueExtractor("contentURLMd5", elem, str(),
                                                              "URLUpdateObject.contentURLMd5", i)
    localObject.priority = self.simpleValueExtractor("priority", elem, int(), "URLUpdateObject.priority", i)
    if "urlPut" in elem and elem["urlPut"] is not None:
      localObject.urlPut = self.URLPutDeserializeOneElement(elem["urlPut"], 0)
    if "chainId" in elem:
      localObject.chainId = self.simpleValueExtractor("chainId", elem, int(), "URLUpdateObject.chainId", i)
    if "classifierMask" in elem:
      localObject.classifierMask = self.simpleValueExtractor("classifierMask", elem, int(),
                                                              "URLUpdateObject.classifierMask", i)
    if "attributes" in elem:
      localObject.attributes = []
      for attribute in elem["attributes"]:
        if type(attribute) is types.DictType and len(attribute) == 1:
          attrObj = dc.EventObjects.Attribute(localObject.siteId, attribute.keys()[0])
          attrObj.urlMd5 = localObject.urlMd5
          attrObj.value = attribute[attribute.keys()[0]]
          localObject.attributes.append(attrObj)
    return localObject


  # #URLUpdateDeserialize method, deserializes incoming jsonData to the [URLUpdate] object
  # jsonData - incoming json string
  def URLUpdateDeserialize(self, jsonData):
    URLUpdateObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLUpdateObject.append(self.URLUpdateDeserializeOneElem(elem, i))
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLUpdate not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLUpdateDeserialize, some field has invalid type")
    return URLUpdateObject


  # #URLFetchDeserialize method, deserializes incoming jsonData to the URLFetch object
  # jsonData - incoming json string
  def URLFetchDeserializeOneElem(self, elem, i):
    localObject = dc.EventObjects.URLFetch()
    if "sitesList" in elem:
      if type(elem["sitesList"]) is not types.ListType:
        raise Exceptions.DeserilizeException("URLFetch.sitesList json-field type not list in {0} elem".format(i))
      localObject.sitesList = elem["sitesList"]
    else:
      raise Exceptions.DeserilizeException("URLFetch.sitesList json-field not found in {0} elem".format(i))

    if "sitesCriterions" in elem and elem["sitesCriterions"] is not None:
      if type(elem["sitesCriterions"]) is not types.DictType:
        raise Exceptions.DeserilizeException(("URLFetch.sitesCriterions json-field type" +
                                              " not dict in {0} elem").format(i))
      if hasattr(localObject.sitesCriterions, '__iter__'):
        localObject.sitesCriterions.update(elem["sitesCriterions"])
      else:
        localObject.sitesCriterions = elem["sitesCriterions"]

    if "urlsCriterions" in elem and elem["urlsCriterions"] is not None:
      if type(elem["urlsCriterions"]) is not types.DictType:
        raise Exceptions.DeserilizeException(("URLFetch.urlsCriterions json-field type" +
                                              " not dict in {0} elem").format(i))
      if hasattr(localObject.urlsCriterions, '__iter__'):
        localObject.urlsCriterions.update(elem["urlsCriterions"])
      else:
        localObject.urlsCriterions = elem["urlsCriterions"]

    localObject.maxURLs = self.simpleValueExtractor("maxURLs", elem, int(), "URLFetch.maxURLs", i)
    if localObject.maxURLs is None:
      localObject.maxURLs = dc.EventObjects.URLFetch.DEFAULT_LIMIT

    localObject.algorithm = self.simpleValueExtractor("algorithm", elem, int(), "URLFetch.algorithm", i)

    if localObject.algorithm is None:
      localObject.algorithm = dc.EventObjects.URLFetch.DEFAULT_ALGORITHM

    if "isLocking" in elem and elem["isLocking"] is not None:
      localObject.isLocking = bool(self.simpleValueExtractor("isLocking", elem, int(), "URLFetch.isLocking", i))

    if "lockIterationTimeout" in elem and elem["lockIterationTimeout"] is not None:
      localObject.lockIterationTimeout = self.simpleValueExtractor("lockIterationTimeout", elem, int(),
                                                                   "URLFetch.lockIterationTimeout", i)
    if "siteUpdate" in elem and elem["siteUpdate"] is not None:
      localObject.siteUpdate = self.siteNewDeserialize(elem["siteUpdate"])

    if "attributeNames" in elem:
      if not isinstance(elem["attributeNames"], list):
        raise Exceptions.DeserilizeException("URLFetch.attributeNames json-field type not list in {0} elem".format(i))
      localObject.attributeNames = elem["attributeNames"]

    return localObject


  # #URLFetchDeserialize method, deserializes incoming jsonData to the list of URLFetch objects
  # jsonData - incoming json string
  def URLFetchDeserialize(self, jsonData):
    URLFetchObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLFetchObject.append(self.URLFetchDeserializeOneElem(elem, i))
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLFetchDeserialize's root element must be an list")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLFetchDeserialize's some field has invalid type")
    return URLFetchObject


  # #URLDeleteDeserialize method, deserializes incoming jsonData to the [URLDelete] object
  # jsonData - incoming json string
  def URLDeleteDeserialize(self, jsonData):
    URLDeleteObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLDeleteObject.append(dc.EventObjects.URLDelete(0, ""))
          if "siteId" in elem:
            URLDeleteObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLDelete.siteId json-field not found in {0} elem".format(i))
          URLDeleteObject[i].url = self.simpleValueExtractor("url", elem, str(), "URLDeleteObject.url", i)
          if "urlType" in elem:
            URLDeleteObject[i].urlType = int(elem["urlType"])
          else:
            raise Exceptions.DeserilizeException("URLDelete.urlType json-field not found in {0} elem".format(i))
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("URLDelete.criterions json-field type" +
                                                    " not dict in {0} elem").format(i))
            if hasattr(URLDeleteObject[i].criterions, '__iter__'):
              URLDeleteObject[i].criterions.update(elem["criterions"])
            else:
              URLDeleteObject[i].criterions = elem["criterions"]
          if "delayedType" in elem and elem["delayedType"] is not None:
            URLDeleteObject[i].delayedType = int(elem["delayedType"])
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLDelete not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLDeleteDeserialize, some field has invalid type")
    return URLDeleteObject


  # #URLCleanupDeserialize method, deserializes incoming jsonData to the [URLCleanup] object
  # jsonData - incoming json string
  def URLCleanupDeserialize(self, jsonData):
    URLCleanupObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLCleanupObject.append(dc.EventObjects.URLCleanup(0, ""))
          if "siteId" in elem:
            URLCleanupObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLCleanupObject.siteId json-field not found in {0} elem".format(i))
          URLCleanupObject[i].url = self.simpleValueExtractor("url", elem, str(), "URLCleanupObject.url", i)
          if "urlType" in elem:
            URLCleanupObject[i].urlType = int(elem["urlType"])
          else:
            raise Exceptions.DeserilizeException("URLCleanup.urlType json-field not found in {0} elem".format(i))
          if "state" in elem:
            URLCleanupObject[i].state = int(elem["state"])
          else:
            raise Exceptions.DeserilizeException("URLCleanup.state json-field not found in {0} elem".format(i))
          if "status" in elem:
            URLCleanupObject[i].status = int(elem["status"])
          else:
            raise Exceptions.DeserilizeException("URLCleanup.status json-field not found in {0} elem".format(i))
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("URLCleanup.criterions json-field type" +
                                                    " not dict in {0} elem").format(i))
            if hasattr(URLCleanupObject[i].criterions, '__iter__'):
              URLCleanupObject[i].criterions.update(elem["criterions"])
            else:
              URLCleanupObject[i].criterions = elem["criterions"]
          if "delayedType" in elem and elem["delayedType"] is not None:
            URLCleanupObject[i].delayedType = int(elem["delayedType"])
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLDelete not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLCleanupDeserialize, some field has invalid type")
    return URLCleanupObject


  # #URLContentDeserialize method, deserializes incoming jsonData to the [URLContentRequest] object
  # jsonData - incoming json string
  def URLContentDeserialize(self, jsonData):
    URLContentObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
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

          if "urlFetch" in elem and elem["urlFetch"] is not None:
            URLContentObject[i].urlFetch = self.URLFetchDeserializeOneElem(elem["urlFetch"], 0)

            if (dc.EventObjects.URLFetch.CRITERION_WHERE not in URLContentObject[i].urlFetch.sitesCriterions or \
            URLContentObject[i].urlFetch.sitesCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] is None) and \
            URLContentObject[i].siteId not in URLContentObject[i].urlFetch.sitesList:
              URLContentObject[i].urlFetch.sitesList.append(URLContentObject[i].siteId)

          if "attributeNames" in elem:
            if not isinstance(elem["attributeNames"], list):
              raise Exceptions.DeserilizeException("URLContentRequest.attributeNames json-field type not list in \
              {0} elem".format(i))
            URLContentObject[i].attributeNames = elem["attributeNames"]

          if "dbFieldsList" in elem:
          # and elem["dbFieldsList"] is not None:
          # TODO: fixed by bgv cause overrides default constructor's initialization if omitted
            if type(elem["dbFieldsList"]) is types.ListType:
              URLContentObject[i].dbFieldsList = elem["dbFieldsList"]
            # else:
              # URLContentObject[i].dbFieldsList = None
            # TODO: fixed by bgv cause overrides default constructor's initialization if omitted
          # else:
          #  URLContentObject[i].dbFieldsList = None
          # TODO: fixed by bgv cause overrides default constructor's initialization if omitted
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLContentObject not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLContentDeserialize, some field has invalid type")
    return URLContentObject


  # #SQLCustomDeserialize method, deserializes incoming jsonData to the [SQLCustomRequest] object
  # jsonData - incoming json string
  def SQLCustomDeserialize(self, jsonData):
    rid = None
    query = None
    dbName = None
    if "rid" in jsonData and jsonData["rid"] is not None:
      rid = self.simpleValueExtractor("rid", jsonData, int(), "SQLCustom.rid")
    else:
      raise Exceptions.DeserilizeException("mandatory SQLCustom.rid absent or None")
    if "query" in jsonData and jsonData["query"] is not None:
      query = self.simpleValueExtractor("query", jsonData, str(), "SQLCustom.query")
    else:
      raise Exceptions.DeserilizeException("mandatory SQLCustom.query absent or None")
    if "dbName" in jsonData and jsonData["dbName"] is not None:
      dbName = self.simpleValueExtractor("dbName", jsonData, str(), "SQLCustom.dbName")
    else:
      raise Exceptions.DeserilizeException("mandatory SQLCustom.query dbName or None")
    sqlCustomObject = dbi.EventObjects.CustomRequest(rid, query, dbName)
    if "includeFieldsNames" in jsonData and jsonData["includeFieldsNames"] is not None:
      sqlCustomObject.includeFieldsNames = self.simpleValueExtractor("includeFieldsNames", jsonData, int(),
                                                     "SQLCustom.includeFieldsNames")
    return sqlCustomObject


  # #BatchDeserialize method, deserializes incoming jsonData to the [Batch] object
  # jsonData - incoming json string
  def BatchDeserialize(self, jsonData):

    batchObject = dc.EventObjects.Batch(0)
    batchObject.id = self.simpleValueExtractor("id", jsonData, int(), "Batch.id")
    batchObject.crawlerType = self.simpleValueExtractor("crawlerType", jsonData, int(), "Batch.crawlerType")
    if "items" in jsonData and jsonData["items"] is not None:
      batchObject.items = self.readBatchItems(jsonData["items"])
    if "errorMask" in jsonData:
      batchObject.errorMask = self.simpleValueExtractor("errorMask", jsonData, int(), "Batch.errorMask")
    if "dbMode" in jsonData:
      batchObject.dbMode = self.simpleValueExtractor("dbMode", jsonData, int(), "Batch.dbMode")
    if "maxIterations" in jsonData:
      batchObject.maxIterations = self.simpleValueExtractor("maxIterations", jsonData, int(), "Batch.maxIterations")
    if "maxItems" in jsonData:
      batchObject.maxItems = self.simpleValueExtractor("maxItems", jsonData, int(), "Batch.maxItems")
    if "maxExecutionTime" in jsonData:
      batchObject.maxExecutionTime = self.simpleValueExtractor("maxExecutionTime", jsonData, int(),
                                                               "Batch.maxExecutionTime")
    if "removeUnprocessedItems" in jsonData:
      batchObject.removeUnprocessedItems = bool(self.simpleValueExtractor("removeUnprocessedItems", jsonData, int(),
                                                                          "Batch.removeUnprocessedItems"))

    return batchObject


  # #URLPurgeDeserialize method, deserializes incoming jsonData to the [URLPurge] object
  # jsonData - incoming json string
  def URLPurgeDeserialize(self, jsonData):
    URLPurgeObject = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLPurgeObject.append(dc.EventObjects.URLPurge(0, ""))
          if "siteId" in elem:
            if elem["siteId"] is None:
              URLPurgeObject[i].siteId = elem["siteId"]
            else:
              URLPurgeObject[i].siteId = str(elem["siteId"])
          else:
            raise Exceptions.DeserilizeException("URLPurge.siteId json-field not found in {0} elem".format(i))
          URLPurgeObject[i].url = self.simpleValueExtractor("url", elem, str(), "URLPurgeObject.url", i)
          if "urlType" in elem:
            URLPurgeObject[i].urlType = int(elem["urlType"])
          else:
            raise Exceptions.DeserilizeException("URLPurge.urlType json-field not found in {0} elem".format(i))
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("URLPurge.criterions json-field type" +
                                                    " not dict in {0} elem").format(i))
            if hasattr(URLPurgeObject[i].criterions, '__iter__'):
              URLPurgeObject[i].criterions.update(elem["criterions"])
            else:
              URLPurgeObject[i].criterions = elem["criterions"]
          if "siteLimits" in elem and elem["siteLimits"] is not None:
            URLPurgeObject[i].siteLimits = elem["siteLimits"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLPurge not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLPurgeDeserialize, some field has invalid type")
    return URLPurgeObject


  # #FieldRecalculatorDeserialize method, deserializes incoming jsonData to the [FieldRecalculatorObj] object
  # jsonData - incoming json string
  def FieldRecalculatorDeserialize(self, jsonData):
    fieldRecalculatorObj = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          fieldRecalculatorObj.append(dc.EventObjects.FieldRecalculatorObj(""))
          fieldRecalculatorObj[i].recalcType = \
                      self.simpleValueExtractor("recalcType", elem, int(), "FieldRecalculator.recalcType", i)
          fieldRecalculatorObj[i].siteId = \
                      self.simpleValueExtractor("siteId", elem, str(), "FieldRecalculator.siteId", i)
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException("fieldRecalculatorObj.criterions not found in {0} elem".format(i))
            if hasattr(fieldRecalculatorObj[i].criterions, '__iter__'):
              fieldRecalculatorObj[i].criterions.update(elem["criterions"])
            else:
              fieldRecalculatorObj[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLPurge not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("FieldRecalculatorDeserialize, some field has invalid type")
    return fieldRecalculatorObj


  # #URLVerifyDeserialize method, deserializes incoming jsonData to the [URLVerifyDeserialize] object
  # jsonData - incoming json string
  def URLVerifyDeserialize(self, jsonData):
    URLVerifyObj = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLVerifyObj.append(dc.EventObjects.URLVerify("", "", ""))
          URLVerifyObj[i].siteId = \
                      self.simpleValueExtractor("siteId", elem, str(), "URLVErify.siteId", i)
          URLVerifyObj[i].urlType = self.simpleValueExtractor("urlType", elem, int(), "URLVErify.urlType", i)
          URLVerifyObj[i].url = self.simpleValueExtractor("url", elem, str(), "URLVErify.url", i)
          URLVerifyObj[i].dbName = self.simpleValueExtractor("dbName", elem, str(), "URLVErify.dbName", i)
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException("URLVErify.criterions not found in {0} elem".format(i))
            if hasattr(URLVerifyObj[i].criterions, '__iter__'):
              URLVerifyObj[i].criterions.update(elem["criterions"])
            else:
              URLVerifyObj[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLVErify not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLVerifyDeserialize, some field has invalid type")
    return URLVerifyObj


  # #URLAgeDeserialize method, deserializes incoming jsonData to the [URLAge] object
  # jsonData - incoming json string
  def URLAgeDeserialize(self, jsonData):
    URLAgeObj = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLAgeObj.append(dc.EventObjects.URLAge(None, None))
          if "urlsCriterions" in elem and elem["urlsCriterions"] is not None:
            if type(elem["urlsCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException("URLAgeObj.urlsCriterions not found in {0} elem".format(i))
            if hasattr(URLAgeObj[i].urlsCriterions, '__iter__'):
              URLAgeObj[i].urlsCriterions.update(elem["urlsCriterions"])
            else:
              URLAgeObj[i].urlsCriterions = elem["urlsCriterions"]
          if "sitesCriterions" in elem and elem["sitesCriterions"] is not None:
            if type(elem["sitesCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException("URLAgeObj.sitesCriterions not found in {0} elem".format(i))
            if hasattr(URLAgeObj[i].sitesCriterions, '__iter__'):
              URLAgeObj[i].sitesCriterions.update(elem["sitesCriterions"])
            else:
              URLAgeObj[i].sitesCriterions = elem["sitesCriterions"]
          localMaxURLs = self.simpleValueExtractor("maxURLs", elem, int(), "URLAgeObj.maxURLs", i)
          if localMaxURLs is not None:
            URLAgeObj[i].maxURLs = localMaxURLs
          localDelayedType = self.simpleValueExtractor("delayedType", elem, int(), "URLAgeObj.delayedType", i)
          if localDelayedType is not None:
            URLAgeObj[i].delayedType = localDelayedType
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLAge not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLAgeDeserialize, some field has invalid type")
    return URLAgeObj


  def URLPutDeserializeOneElement(self, jsonData, i):
    ret = dc.EventObjects.URLPut(None, None, None)
    ret.siteId = self.simpleValueExtractor("siteId", jsonData, str(), "URLPutObj.siteId", i)
    ret.urlMd5 = self.simpleValueExtractor("urlMd5", jsonData, str(), "URLPutObj.urlMd5", i)
    if "putDict" in jsonData and type(jsonData["putDict"]) is types.DictType:
      ret.putDict = jsonData["putDict"]
      if "cDate" in ret.putDict and ret.putDict["cDate"] is not None:
        ret.putDict["cDate"] = self.timeExtractor(ret.putDict["cDate"])
    else:
      raise Exceptions.DeserilizeException("Absent mandatory putDict field or it's not dict type")

    if "criterions" in jsonData and jsonData["criterions"] is not None:
      if type(jsonData["criterions"]) is not types.DictType:
        raise Exceptions.DeserilizeException("URLPutObj.criterions not found in {0} elem".format(i))
      if hasattr(ret.criterions, '__iter__'):
        ret.criterions.update(jsonData["criterions"])
      else:
        ret.criterions = jsonData["criterions"]
    ret.contentType = self.simpleValueExtractor("contentType", jsonData, int(), "URLPutObj.contentType", i)
    if "fileStorageSuffix" in jsonData and jsonData["fileStorageSuffix"] is not None:
      ret.fileStorageSuffix = self.simpleValueExtractor("fileStorageSuffix", jsonData, str(),
                                                                 "URLPutObj.fileStorageSuffix", i)
    return ret


  # #URLPutDeserialize method, deserializes incoming jsonData to the [URLPut] object
  # jsonData - incoming json string
  def URLPutDeserialize(self, jsonData):
    URLPutObjs = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          URLPutObjs.append(self.URLPutDeserializeOneElement(elem, i))
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLPut not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLPutDeserialize, some field has invalid type")
    return URLPutObjs


  # #URLHistoryDeserialize method, deserializes incoming jsonData to the [URLHistoryRequest] object
  # jsonData - incoming json string
  def URLHistoryDeserialize(self, jsonData):
    URLHistoryRequestObjs = []
    i = 0
    logger.error(">>> Start URLHistoryDeserialize")
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ret = dc.EventObjects.URLHistoryRequest(None)
          ret.siteId = self.simpleValueExtractor("siteId", elem, str(), "URLHistoryRequest.siteId", i)
          ret.urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "URLHistoryRequest.urlMd5", i)
          if "urlCriterions" in elem and elem["urlCriterions"] is not None:
            if type(elem["urlCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException\
              ("URLHistoryRequestObjs.urlCriterions not found in {0} elem".format(i))
            if hasattr(ret.urlCriterions, '__iter__'):
              ret.urlCriterions.update(elem["urlCriterions"])
            else:
              ret.urlCriterions = elem["urlCriterions"]
          if "logCriterions" in elem and elem["logCriterions"] is not None:
            if type(elem["logCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException\
              ("URLHistoryRequestObjs.logCriterions not found in {0} elem".format(i))
            if hasattr(ret.logCriterions, '__iter__'):
              ret.logCriterions.update(elem["logCriterions"])
            else:
              ret.logCriterions = elem["logCriterions"]
          URLHistoryRequestObjs.append(ret)
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLHistoryDeserialize not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLHistoryDeserialize, some field has invalid type")
    return URLHistoryRequestObjs


  # #URLStatsDeserialize method, deserializes incoming jsonData to the [URLStatsRequest] object
  # jsonData - incoming json string
  def URLStatsDeserialize(self, jsonData):
    URLStatsRequestObjs = []
    i = 0
    logger.error(">>> Start URLStatsRequestObjs")
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ret = dc.EventObjects.URLStatsRequest(None)
          ret.siteId = self.simpleValueExtractor("siteId", elem, str(), "URLHistoryRequest.siteId", i)
          ret.urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "URLHistoryRequest.urlMd5", i)
          if "urlCriterions" in elem and elem["urlCriterions"] is not None:
            if type(elem["urlCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException("URLStatsRequestObjs.urlCriterions not found in {0} elem".format(i))
            if hasattr(ret.urlCriterions, '__iter__'):
              ret.urlCriterions.update(elem["urlCriterions"])
            else:
              ret.urlCriterions = elem["urlCriterions"]
          if "statsCriterions" in elem and elem["statsCriterions"] is not None:
            if type(elem["statsCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException\
              ("URLStatsRequestObjs.statsCriterions not found in {0} elem".format(i))
            if hasattr(ret.statsCriterions, '__iter__'):
              ret.statsCriterions.update(elem["statsCriterions"])
            else:
              ret.statsCriterions = elem["statsCriterions"]
          URLStatsRequestObjs.append(ret)
          i += 1
      else:
        raise Exceptions.DeserilizeException("URLStatsRequestObjs not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("URLStatsDeserialize, some field has invalid type")
    return URLStatsRequestObjs


  # #ProxyNewElementDeserialize method, fills data in one ProxyNew elemet
  #
  # proxyNewObject - filled ProxyNew object
  # jsonData - incoming json string
  # i - index of current ProxyNew object
  def ProxyNewElementDeserialize(self, proxyNewObject, jsonData, i):
    proxyNewObject.siteId = self.simpleValueExtractor("siteId", jsonData, str(), "ProxyNew.siteId", i)
    proxyNewObject.host = self.simpleValueExtractor("host", jsonData, str(), "ProxyNew.host", i)
    if "id" in jsonData and hasattr(proxyNewObject, 'id'):
      proxyNewObject.Id = self.simpleValueExtractor("id", jsonData, int(), "ProxyNew.id", i)
    if "domains" in jsonData:
      proxyNewObject.domains = jsonData["domains"]
    if "priority" in jsonData:
      proxyNewObject.priority = self.simpleValueExtractor("priority", jsonData, int(), "ProxyNew.priority", i)
    if "state" in jsonData:
      proxyNewObject.state = self.simpleValueExtractor("state", jsonData, int(), "ProxyNew.state", i)
    if "countryCode" in jsonData:
      proxyNewObject.countryCode = self.simpleValueExtractor("countryCode", jsonData, str(), "ProxyNew.countryCode", i)
    if "countryName" in jsonData:
      proxyNewObject.countryName = self.simpleValueExtractor("countryName", jsonData, str(), "ProxyNew.countryName", i)
    if "regionCode" in jsonData:
      proxyNewObject.regionCode = self.simpleValueExtractor("regionCode", jsonData, int(), "ProxyNew.regionCode", i)
    if "regionName" in jsonData:
      proxyNewObject.regionName = self.simpleValueExtractor("regionName", jsonData, str(), "ProxyNew.regionName", i)
    if "cityName" in jsonData:
      proxyNewObject.cityName = self.simpleValueExtractor("cityName", jsonData, str(), "ProxyNew.cityName", i)
    if "zipCode" in jsonData:
      proxyNewObject.zipCode = self.simpleValueExtractor("zipCode", jsonData, str(), "ProxyNew.zipCode", i)
    if "timeZone" in jsonData:
      proxyNewObject.timeZone = self.simpleValueExtractor("timeZone", jsonData, str(), "ProxyNew.timeZone", i)
    if "latitude" in jsonData:
      proxyNewObject.latitude = self.simpleValueExtractor("latitude", jsonData, float(), "ProxyNew.latitude", i)
    if "longitude" in jsonData:
      proxyNewObject.longitude = self.simpleValueExtractor("longitude", jsonData, float(), "ProxyNew.longitude", i)
    if "metroCode" in jsonData:
      proxyNewObject.metroCode = self.simpleValueExtractor("metroCode", jsonData, int(), "ProxyNew.metroCode", i)
    if "faults" in jsonData:
      proxyNewObject.faults = self.simpleValueExtractor("faults", jsonData, int(), "ProxyNew.faults", i)
    if "faultsMax" in jsonData:
      proxyNewObject.faultsMax = self.simpleValueExtractor("faultsMax", jsonData, int(), "ProxyNew.faultsMax", i)
    if "categoryId" in jsonData:
      proxyNewObject.categoryId = self.simpleValueExtractor("categoryId", jsonData, int(), "ProxyNew.categoryId", i)
    if "limits" in jsonData:
      proxyNewObject.limits = jsonData["limits"]
    if "description" in jsonData:
      proxyNewObject.description = self.simpleValueExtractor("description", jsonData, str(), "ProxyNew.description", i)
    if "cDate" in jsonData:
      proxyNewObject.cDate = self.timeExtractor(jsonData["cDate"])
    if "uDate" in jsonData:
      proxyNewObject.uDate = self.timeExtractor(jsonData["uDate"])


  # #ProxyNewDeserialize method, serializes all ProxyNew elemets from incoming json
  #
  # jsonData - incoming json string
  def ProxyNewDeserialize(self, jsonData):
    ProxyNewObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ProxyNewObjects.append(dc.EventObjects.Proxy("", ""))
          self.ProxyNewElementDeserialize(ProxyNewObjects[i], elem, i)
          i += 1
      else:
        raise Exceptions.DeserilizeException("ProxyNew not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("ProxyNewDeserialize, some field has invalid type")
    return ProxyNewObjects


  # #ProxyUpdateDeserialize method, serializes all ProxyUpdate elemets from incoming json
  #
  # jsonData - incoming json string
  def ProxyUpdateDeserialize(self, jsonData, siteId='', host=''):
    ProxyUpdateObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ProxyUpdateObjects.append(dc.EventObjects.ProxyUpdate(siteId, host))
          self.ProxyNewElementDeserialize(ProxyUpdateObjects[i], elem, i)
          i += 1
      else:
        raise Exceptions.DeserilizeException("ProxyUpdate not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("ProxyUpdateDeserialize, some field has invalid type")
    return ProxyUpdateObjects


  # #ProxyUpdateDeserialize method, serializes all ProxyDelete elemets from incoming json
  #
  # jsonData - incoming json string
  def ProxyDeleteDeserialize(self, jsonData):
    ProxyDeleteObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ProxyDeleteObjects.append(dc.EventObjects.ProxyDelete())
          if "siteId" in elem:
            ProxyDeleteObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "ProxyDelete.siteId", i)
          if "host" in elem:
            ProxyDeleteObjects[i].host = self.simpleValueExtractor("host", elem, str(), "ProxyDelete.host", i)
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("ProxyDelete.criterions json-field type" +
                                              " not dict in {0} elem").format(i))
            if hasattr(ProxyDeleteObjects[i].criterions, '__iter__'):
              ProxyDeleteObjects[i].criterions.update(elem["criterions"])
            else:
              ProxyDeleteObjects[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("ProxyDelete not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("ProxyDeleteDeserialize, some field has invalid type")
    return ProxyDeleteObjects


  # #ProxyUpdateDeserialize method, serializes all ProxyStatus elemets from incoming json
  #
  # jsonData - incoming json string
  def ProxyStatusDeserialize(self, jsonData):
    ProxyStausObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ProxyStausObjects.append(dc.EventObjects.ProxyStatus())
          if "siteId" in elem:
            ProxyStausObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "ProxyStaus.siteId", i)
          if "host" in elem:
            ProxyStausObjects[i].host = self.simpleValueExtractor("host", elem, str(), "ProxyStaus.host", i)
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("ProxyDelete.criterions json-field type" +
                                              " not dict in {0} elem").format(i))
            if hasattr(ProxyStausObjects[i].criterions, '__iter__'):
              ProxyStausObjects[i].criterions.update(elem["criterions"])
            else:
              ProxyStausObjects[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("ProxyStatus not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("ProxyStatusDeserialize, some field has invalid type")
    return ProxyStausObjects


  # #ProxyUpdateDeserialize method, serializes all ProxyFind elemets from incoming json
  #
  # jsonData - incoming json string
  # return list of ProxyFind objects
  def ProxyFindDeserialize(self, jsonData):
    ProxyFindObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          ProxyFindObjects.append(dc.EventObjects.ProxyFind())
          if "siteId" in elem:
            ProxyFindObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "ProxyFind.siteId", i)
          if "siteCriterions" in elem and elem["siteCriterions"] is not None:
            if type(elem["siteCriterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("ProxyFind.siteCriterions json-field type" +
                                              " not dict in {0} elem").format(i))
            if hasattr(ProxyFindObjects[i].siteCriterions, '__iter__'):
              ProxyFindObjects[i].siteCriterions.update(elem["siteCriterions"])
            else:
              ProxyFindObjects[i].siteCriterions = elem["siteCriterions"]
          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("ProxyFind.criterions json-field type" +
                                              " not dict in {0} elem").format(i))
            if hasattr(ProxyFindObjects[i].criterions, '__iter__'):
              ProxyFindObjects[i].criterions.update(elem["criterions"])
            else:
              ProxyFindObjects[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("ProxyStatus not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("ProxyFindDeserialize, some field has invalid type")
    return ProxyFindObjects


  # #AttrSetDeserialize method, serializes all ProxyFind elemets from incoming json
  #
  # jsonData - incoming json string
  # return list of Attributes objects
  def AttrSetDeserialize(self, jsonData):
    attributesObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          attributesObjects.append(dc.EventObjects.Attribute('', ''))
          attributesObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "Attribute.siteId")
          attributesObjects[i].name = self.simpleValueExtractor("name", elem, str(), "Attribute.name")
          if "urlMd5" in elem:
            attributesObjects[i].urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "Attribute.urlMd5")
          if "value" in elem:
            attributesObjects[i].value = self.simpleValueExtractor("value", elem, str(), "Attribute.value")
          i += 1
      else:
        raise Exceptions.DeserilizeException("AttrSet not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("AttrSetDeserialize, some field has invalid type")
    return attributesObjects


  # #AttrUpdateDeserialize method, serializes all AttributeUpdate elemets from incoming json
  #
  # jsonData - incoming json string
  # return list of AttributeUpdate objects
  def AttrUpdateDeserialize(self, jsonData):
    attributesUpdateObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          attributesUpdateObjects.append(dc.EventObjects.AttributeUpdate('', ''))
          attributesUpdateObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "AttributeUpdate.siteId")
          attributesUpdateObjects[i].name = self.simpleValueExtractor("name", elem, str(), "AttributeUpdate.name")

          if "urlMd5" in elem:
            attributesUpdateObjects[i].urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "AttributeUpdate.urlMd5")

          if "value" in elem:
            attributesUpdateObjects[i].value = self.simpleValueExtractor("value", elem, str(), "AttributeUpdate.value")
          i += 1
      else:
        raise Exceptions.DeserilizeException("AttrUpdate not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("AttrUpdateDeserialize, some field has invalid type")
    return attributesUpdateObjects


  # #AttrDeleteDeserialize method, serializes all AttributeDelete elemets from incoming json
  #
  # jsonData - incoming json string
  # return list of AttributeDelete objects
  def AttrDeleteDeserialize(self, jsonData):
    attributesDeleteObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          attributesDeleteObjects.append(dc.EventObjects.AttributeDelete(''))
          attributesDeleteObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "AttributeDelete.siteId")
          if "name" in elem:
            attributesDeleteObjects[i].name = self.simpleValueExtractor("name", elem, str(), "AttributeDelete.name")

          if "urlMd5" in elem:
            attributesDeleteObjects[i].urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "AttributeDelete.urlMd5")

          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("ProxyFind.criterions json-field type" +
                                              " not dict in {0} elem").format(i))
            if hasattr(attributesDeleteObjects[i].criterions, '__iter__'):
              attributesDeleteObjects[i].criterions.update(elem["criterions"])
            else:
              attributesDeleteObjects[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("AttrDelete not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("AttrDeleteDeserialize, some field has invalid type")
    return attributesDeleteObjects


  # #AttrFetchDeserialize method, serializes all AttributeFetch elemets from incoming json
  #
  # jsonData - incoming json string
  # return list of AttributeFetch objects
  def AttrFetchDeserialize(self, jsonData):
    attributesFetchObjects = []
    i = 0
    try:
      if type(jsonData) is types.ListType:
        for elem in jsonData:
          attributesFetchObjects.append(dc.EventObjects.AttributeFetch(''))
          attributesFetchObjects[i].siteId = self.simpleValueExtractor("siteId", elem, str(), "AttrFetch.siteId")
          if "name" in elem:
            attributesFetchObjects[i].name = self.simpleValueExtractor("name", elem, str(), "AttrFetch.name")

          if "urlMd5" in elem:
            attributesFetchObjects[i].urlMd5 = self.simpleValueExtractor("urlMd5", elem, str(), "AttrFetch.urlMd5")

          if "criterions" in elem and elem["criterions"] is not None:
            if type(elem["criterions"]) is not types.DictType:
              raise Exceptions.DeserilizeException(("ProxyFind.criterions json-field type" +
                                              " not dict in {0} elem").format(i))
            if hasattr(attributesFetchObjects[i].criterions, '__iter__'):
              attributesFetchObjects[i].criterions.update(elem["criterions"])
            else:
              attributesFetchObjects[i].criterions = elem["criterions"]
          i += 1
      else:
        raise Exceptions.DeserilizeException("AttrFetch not list type")
    except (ValueError, TypeError):
      raise Exceptions.DeserilizeException("AttrFetchDeserialize, some field has invalid type")
    return attributesFetchObjects
