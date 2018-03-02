"""
@package: dc
@file URLProcess.py
@author Scorp, Vybornyh, bgv <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import datetime
import hashlib
import types
import re
import time
import urllib
import urlparse
import json
import requests

from dc_crawler.Exceptions import SyncronizeException
from dc_crawler.CollectURLs import CollectURLs
import dc_crawler.Constants as CONSTS
import CrawlerTask as CrawlerTask  # pylint: disable=W0403

import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from app.Filters import Filters
from app.Utils import SQLExpression
from app.Utils import ExceptionLog
from app.Utils import UrlNormalizator
# from app.Utils import urlNormalization
from app.Utils import varDump
from app.DateTimeType import DateTimeType
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
from app.UrlNormalize import UrlNormalize
import dc.EventObjects
import dc.Constants as DC_CONSTS
import dc_processor.Constants as PCONSTS
import dc_db.Constants as DB_CONSTS

from dtm.EventObjects import GeneralResponse


logger = Utils.MPLogger().getLogger()


class URLProcess(object):

  DC_URLS_TABLE_PREFIX = "urls_"
  DETECT_MIME_TIMEOUT = 1
  PATTERN_WITH_PROTOCOL = re.compile('[a-zA-Z]+:(//)?')
  URL_TEMPLATE_CONST = "%URL%"
  PROTOCOL_PREFIX = "://"
  DEFAULT_PROTOCOLS = ["http", "https"]


  def __init__(self, protocols=None):
    self.isUpdateCollection = False
    self.urlObj = None
    self.url = None
    self.dbWrapper = None
    self.siteId = None
    self.site = None
    self.urlTable = None
    self.protocolsList = self.DEFAULT_PROTOCOLS
    self.siteProperties = None
    self.setProtocols(protocols)
    self.normMask = UrlNormalizator.NORM_DEFAULT


  # #setProtocols inits self.protocolsList field
  #
  def setProtocols(self, protocols=None):
    if protocols is not None:
      try:
        self.protocolsList = json.loads(protocols)
      except Exception:
        self.protocolsList = []
    logger.debug(">>> THAT PROTOCOLS = " + str(self.protocolsList))


  # #checkUrlByPath checks incoming url by protocol
  #
  def checkUrlByPath(self, url):
    ret = False
    position = url.find(self.PROTOCOL_PREFIX)
    if position > 0 and url.find('/') == (position + 1):
      ret = True
    return ret


  # #checkUrlByProtocol finds url's protocol in allowed protocols list
  #
  def checkUrlByProtocol(self, url):
    ret = False
    for elem in self.protocolsList:
      if url.lower().startswith(elem + self.PROTOCOL_PREFIX):
        ret = True
        break
    if not ret:
      logger.debug(">>> URL skiped by protocol = " + url)
    return ret


  # #checkFieldsIsNone method checks all class's mandatory fields
  #
  def checkFieldsIsNone(self, checkList):
    # for field in self.__dict__:
    #  if field in checkList and (not hasattr(self, field) or getattr(self, field) is None):
    #    raise Exception(">>> [CollectURLs] Mandatory field must be initialized, field Name = " + field)
    for name in checkList:
      if not hasattr(self, name) or getattr(self, name) is None:
        raise Exception("Some mandatory field `%s` must be initialized!", name)


  # #resolveTableName method resolve bd name by incoming siteId
  #
  def resolveTableName(self, localSiteId):
    self.urlTable = self.DC_URLS_TABLE_PREFIX + localSiteId
    return self.urlTable


  # #readCurrentCnt return urls cnt from db
  #
  def readCurrentCnt(self, maxURLs):
    currentCnt = 0
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "urlTable"])

      if maxURLs > 0:
        countsql = "SELECT COUNT(*) AS cnt FROM `%s` WHERE NOT (Status=4 AND Crawled=0 AND Processed=0)" % \
                    (self.urlTable,)
        result = self.dbWrapper.customRequest(countsql, CrawlerTask.DB_URLS)
        if result is not None and len(result) > 0 and len(result[0]) > 0:
          currentCnt = result[0][0]
        else:
          currentCnt = 0

    logger.debug("!!! maxURLs = %s, currentCnt = %s", str(maxURLs), str(currentCnt))

    return currentCnt


  def simpleURLCanonize(self, realUrl):
    self.checkFieldsIsNone(["url"])
    if not self.checkUrlByPath(self.url):
      self.url = urlparse.urljoin(realUrl, self.url)
      # normalization
    retUrl = Utils.UrlNormalizator.normalize(self.url, self.protocolsList, self.normMask)
    return retUrl


  # #processURL process incoming url and added it to the one of incoming lists [internalLinks or externalLinks]
  #
  # @param pubdate - date extracted on crawler
  def processURL(self, realUrl, internalLinks, externalLinks, filtersApply=None, siteFilters=None, baseUrl=None):
    self.checkFieldsIsNone(["urlObj", "siteId", "url"])
    retUrl = None
    retContinue = False

    logger.debug("URL: %s", self.url)

    if self.urlObj.type == dc.EventObjects.URL.TYPE_SINGLE or not self.url:
      logger.debug("URL type is TYPE_SINGLE - not collect urls. Skip url.")
      retContinue = True

    if not retContinue:
      retUrl = UrlNormalize.execute(siteProperties=self.siteProperties, base=baseUrl, url=self.url, supportProtocols=self.protocolsList, log=None)
      if retUrl is not None:
        localFilters = None
        protocolAllowed = True
        if filtersApply is not None:
          # Stage 'collect urls protocols' and operation code 'regular expression'
          logger.debug(">>> Filters() (3.1) siteFilters: " + str(siteFilters))
          localFilters = Filters(siteFilters, self.dbWrapper, self.siteId, 0, None, Filters.OC_RE, \
                                 Filters.STAGE_COLLECT_URLS_PROTOCOLS)

          if localFilters.isExistStage(Filters.STAGE_COLLECT_URLS_PROTOCOLS):
            resFilterApply = filtersApply(siteFilters, retUrl, 0, self.dbWrapper, self.siteId,
                                          None, Filters.OC_RE, Filters.STAGE_COLLECT_URLS_PROTOCOLS)
            logger.debug("Filter apply: " + str(resFilterApply))

        protocolAllowed = self.checkUrlByProtocol(retUrl)
        logger.debug("checkUrlByProtocol return: " + str(protocolAllowed))
        logger.debug("retUrl: " + str(retUrl))
        logger.debug("realUrl: " + str(realUrl))

        if protocolAllowed:
          if Utils.parseHost(retUrl) == Utils.parseHost(realUrl):
            internalLinks.append(retUrl)
            logger.debug("URL classified as internal")
          elif Utils.parseHost(retUrl):
            externalLinks.append(retUrl)
            logger.debug("URL classified as external")
          else:  # not valid url like http://
            retContinue = True
        else:
          retContinue = True
      else:
        logger.debug(">>> Bad url normalization, url = " + str(retUrl))
        retContinue = True
    return retUrl, retContinue


  # #isUrlExist slelect localUrl from dc_urls db if it exist
  #
  def isUrlExist(self, recrawlPeriod, urlMd5):
    # variable for result
    ret = False

    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["url", "dbWrapper", "siteId", "urlTable"])

      if "RECRAWL_URL_AGE_EXPRESSION" in self.siteProperties and self.siteProperties["RECRAWL_URL_AGE_EXPRESSION"] != "":
        ageExpr = self.siteProperties["RECRAWL_URL_AGE_EXPRESSION"].replace("%RECRAWL_PERIOD%", str(recrawlPeriod))
      else:
        ageExpr = "(DATE_ADD(UDate, INTERVAL %s MINUTE)-NOW())" % (str(recrawlPeriod))
      query = "SELECT COUNT(*), %s, `Type` FROM `%s` WHERE `URLMd5` = '%s'" % (ageExpr, self.urlTable, urlMd5)
      result = self.dbWrapper.customRequest(query, CrawlerTask.DB_URLS)
      if result is not None and len(result) > 0 and len(result[0]) > 0 and result[0][0] > 0:
        if recrawlPeriod == 0 or result[0][1] > 0 or result[0][2] == dc.EventObjects.URL.TYPE_FETCHED or \
        ("RECRAWL_NO_ROOT_URLS" in self.siteProperties and self.siteProperties["RECRAWL_NO_ROOT_URLS"] == "0"):
          logger.debug("URL skipped, exists and re-crawling not active, time not reached or URL Type is " +
                       "RSS feed (not to fetch)\n %s %s", self.url, urlMd5)
          ret = True
        else:
          self.updateURLFields(urlMd5, self.dbWrapper, self.siteId)
          logger.debug("URL state updated to NEW because re-crawling\n %s %s", self.url, urlMd5)
          ret = True
      else:
        logger.debug("URL %s treated as new\n %s", self.url, urlMd5)

    return ret


  # #update some fields in dc_urls
  #
  # urlMd5 param - urls md5
  # wrapper param - db_db wrapper
  # siteId param - site's id
  def updateURLFields(self, urlMd5, wrapper, siteId):
    urlUpdateObj = dc.EventObjects.URLUpdate(siteId, urlMd5, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                             normalizeMask=self.normMask)
    if self.siteProperties is None:
      self.siteProperties = {}

    logger.debug('!!!!!! updateURLFields !!! self.siteProperties: ' + str(self.siteProperties))
    # Status field
    if "RECRAWL_URL_UPDATE_STATUS" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE_STATUS"] != "-1":
      urlUpdateObj.status = int(self.siteProperties["RECRAWL_URL_UPDATE_STATUS"])
    else:
      if "RECRAWL_URL_UPDATE_STATUS" in self.siteProperties and \
      self.siteProperties["RECRAWL_URL_UPDATE_STATUS"] == "-1":
        urlUpdateObj.status = None
      else:
        urlUpdateObj.status = dc.EventObjects.URL.STATUS_NEW

    # TcDate field
    if "RECRAWL_URL_UPDATE_TCDATE" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE_TCDATE"] != "":
      urlUpdateObj.tcDate = self.siteProperties["RECRAWL_URL_UPDATE_TCDATE"]
    else:
      if "RECRAWL_URL_UPDATE_TCDATE" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE_TCDATE"] == "":
        urlUpdateObj.tcDate = None
      else:
        urlUpdateObj.tcDate = SQLExpression("NOW()")

    # CDate field
    if "RECRAWL_URL_UPDATE_CDATE" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE_CDATE"] != "":
      urlUpdateObj.CDate = self.siteProperties["RECRAWL_URL_UPDATE_CDATE"]

    # UDate field
    if "RECRAWL_URL_UPDATE_UDATE" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE_UDATE"] != "":
      urlUpdateObj.UDate = self.siteProperties["RECRAWL_URL_UPDATE_UDATE"]
    else:
      if "RECRAWL_URL_UPDATE_UDATE" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE_UDATE"] == "":
        urlUpdateObj.UDate = None
      else:
        urlUpdateObj.UDate = SQLExpression("NOW()")

    # Recrawl url update
    if "RECRAWL_URL_UPDATE" in self.siteProperties and self.siteProperties["RECRAWL_URL_UPDATE"] != "":
      self.recrawlUrlUpdateHandler(wrapper, self.siteProperties["RECRAWL_URL_UPDATE"], urlUpdateObj)

    if wrapper is not None:
      saveAffectDB = wrapper.affect_db
      wrapper.affect_db = True
      wrapper.urlUpdate(urlUpdateObj, "`State`=0")
      wrapper.affect_db = saveAffectDB


  # # Recrawl url update handler
  #
  # @param dbWrapper - DBTaskWrapper insstance
  # @param recrawlUrlUpdateProperty - input property as json string
  # @param urlUpdateObj - UrlUpdate instance
  # @return - None
  def recrawlUrlUpdateHandler(self, dbWrapper, recrawlUrlUpdateProperty, urlUpdateObj):
    if dbWrapper is not None:
      propertyStruct = None
      try:
        propertyStruct = json.loads(recrawlUrlUpdateProperty)
      except Exception, err:
        logger.error("Load property 'RECRAWL_URL_UPDATE' was failed, error: %s", str(err))

      # If load json was successfully
      if propertyStruct is not None:
        try:
          # list elements or one element?
          for pattern, rules in propertyStruct.items():
            if re.search(pattern, self.url) is not None:
              # Update data accord to parameters
              if "new" in rules and int(rules["new"]) > 0:
                saveAffectDB = dbWrapper.affect_db
                dbWrapper.affect_db = True
                dbWrapper.urlNew(self.urlObj)
                dbWrapper.affect_db = saveAffectDB

              if "fields" in rules and isinstance(rules["fields"], dict):
                for key, value in rules["fields"].items():
                  if key in DB_CONSTS.URLTableDict.values():
                    for urlUpdateObjName, DBSchemaName in DB_CONSTS.URLTableDict.items():
                      if key == DBSchemaName and hasattr(urlUpdateObj, urlUpdateObjName):
                        setattr(urlUpdateObj, urlUpdateObjName, value)
                        logger.debug("For '" + str(DBSchemaName) + "' found attribute 'UrlUpdate." + \
                                     str(urlUpdateObjName) + "' and set value: " + str(value) + \
                                     " type: " + str(type(value)))
                        break
                  else:
                    logger.debug("Wrong DB schema field name '" + str(key) + "' in property 'RECRAWL_URL_UPDATE'")

        except Exception, err:
          logger.error("Usage property 'RECRAWL_URL_UPDATE' was failed, error: %s", str(err))


  # # detect mime type for an URL using HEAD method
  #
  # @return mime_type detected mime type, empty string if failed
  def detectUrlMime(self, contentTypeMap=None, urlObj=None):
    del urlObj
    self.checkFieldsIsNone(["url"])
    ret = ''
    try:
      res = requests.head(self.url, timeout=self.DETECT_MIME_TIMEOUT)
      ret = res.headers.get('content-type', '').lower()
      if contentTypeMap is not None and ret in contentTypeMap:
        logger.debug(">>> Mime type replaced from %s to %s", ret, contentTypeMap[ret])
        ret = contentTypeMap[ret]
    except Exception:
      logger.warn("detect mime type for %s failed", self.url, exc_info=True)
    return ret


  # #getDepthFromUrl method
  #
  # urlMd5 - url's md5
  def getDepthFromUrl(self, urlMd5):
    ret = 0
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId"])

      urlStatusObj = dc.EventObjects.URLStatus(self.siteId, urlMd5)
      result = self.dbWrapper.urlStatus(urlStatusObj, True)
      if len(result) > 0 and isinstance(result[0], dc.EventObjects.URL):
        ret = result[0].depth

    return ret


  # #updateURLForFailed
  #
  # @param errorBit BitMask of error
  # @param batchItem incoming batchItem instance
  def updateURLForFailed(self, errorBit, batchItem, httpCode=CONSTS.HTTP_CODE_400,
                         status=dc.EventObjects.URL.STATUS_CRAWLED, updateUdate=True):
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId"])
      logger.debug("Set errorBit = " + str(errorBit) + ", httpCode = " + str(httpCode))
      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, batchItem.urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)

      batchItem.urlObj.errorMask = batchItem.urlObj.errorMask | errorBit
      urlUpdateObj.errorMask = SQLExpression("`ErrorMask` | " + str(errorBit))

      urlUpdateObj.status = batchItem.urlObj.status = status
      urlUpdateObj.tcDate = batchItem.urlObj.tcDate = SQLExpression("NOW()")
      if updateUdate:
        urlUpdateObj.UDate = batchItem.urlObj.UDate = SQLExpression("NOW()")

      if httpCode is not None:
        urlUpdateObj.httpCode = batchItem.urlObj.httpCode = httpCode
        self.urlObj.httpCode = httpCode  # #???

      if self.dbWrapper is not None:
        # Evaluate URL class values if neccessary
        changedFieldsDict = FieldsSQLExpressionEvaluator.execute(self.siteProperties, self.dbWrapper, None,
                                                                 batchItem.urlObj, logger,
                                                                 APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
        # Update URL values
        for name, value in changedFieldsDict.items():
          if hasattr(urlUpdateObj, name):
            setattr(urlUpdateObj, name, value)
        urlUpdateObj.errorMask = SQLExpression("`ErrorMask` | " + str(errorBit))

        # Update URL data in DB
        self.dbWrapper.urlUpdate(urlUpdateObj)


  # #getRealUrl
  #
  def getRealUrl(self):
    self.checkFieldsIsNone(["url"])
    if self.url.startswith("http%3A") or self.url.startswith("https%3A"):
      ret = urllib.unquote(self.url.url).decode('utf-8')
    else:
      ret = self.url.decode('utf8')
    return ret


  # #resolveHTTP method resolves http method, and fill headersDict["If-Modified-Since"] element
  #
  # @param postForms incoming post forms
  # @param headersDict incoming headersDict dict, where filled element with "If-Modified-Since" key
  # return None or filled postData
  def resolveHTTP(self, postForms, headersDict):
    self.checkFieldsIsNone(["urlObj"])
    logger.debug("headersDict: %s", str(headersDict))
    postData = None
    try:
      method = self.urlObj.httpMethod.lower()
    except Exception:
      method = "get"
    if method == "post":
      postData = postForms
      logger.debug("use post, post_data:%s", postData)
#    else:
#      logger.debug("last modified: <<%s>>", str((self.urlObj.lastModified)))
#      if str(self.urlObj.lastModified) != "None" and str(self.urlObj.lastModified) != "NULL":
#        logger.debug("If-Modified-Since: <<%s>>", self.urlObj.lastModified)
#        headersDict["If-Modified-Since"] = \
#        Utils.convertToHttpDateFmt(datetime.datetime.strptime(str(self.urlObj.lastModified), "%Y-%m-%d %H:%M:%S"))
    return postData


  # #updateCrwledURL
  #
  # @param site - site object
  def updateCrawledURL(self, crawledResource, batchItem, contentSize, status=dc.EventObjects.URL.STATUS_CRAWLED):

    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["urlObj", "dbWrapper", "siteId"])
      logger.debug(">>> Start urls update")

      updatedCount = self.urlObj.mRate * self.urlObj.mRateCounter
      if crawledResource.http_code != 304:
        updatedCount += 1
      mrate = updatedCount / (self.urlObj.mRateCounter + 1)


      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, batchItem.urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)

      urlUpdateObj.contentType = batchItem.urlObj.contentType
      urlUpdateObj.charset = batchItem.urlObj.charset
      urlUpdateObj.errorMask = batchItem.urlObj.errorMask
      urlUpdateObj.crawlingTime = batchItem.urlObj.crawlingTime
      urlUpdateObj.totalTime = batchItem.urlObj.crawlingTime
      urlUpdateObj.httpCode = batchItem.urlObj.httpCode

      urlUpdateObj.status = batchItem.urlObj.status = status
      urlUpdateObj.size = batchItem.urlObj.size = contentSize
      urlUpdateObj.mRate = batchItem.urlObj.mRate = mrate

      batchItem.urlObj.UDate = batchItem.urlObj.tcDate = str(datetime.datetime.now())
      urlUpdateObj.UDate = urlUpdateObj.tcDate = SQLExpression("NOW()")
      batchItem.urlObj.mRateCounter += 1
      urlUpdateObj.mRateCounter = SQLExpression("`MRateCounter` + 1")
      urlUpdateObj.lastModified = batchItem.urlObj.lastModified = crawledResource.last_modified
      urlUpdateObj.urlMd5 = batchItem.urlObj.urlMd5

      if APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER in self.siteProperties:
        # Evaluate URL class values if neccessary
        changedFieldsDict = FieldsSQLExpressionEvaluator.execute(self.siteProperties, self.dbWrapper, None,
                                                                 batchItem.urlObj, logger,
                                                                 APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
        # Update URL values
        if changedFieldsDict is not None:
          for name, value in changedFieldsDict.items():
            if hasattr(urlUpdateObj, name):
              setattr(urlUpdateObj, name, value)

      logger.debug("!!! Before self.dbWrapper.urlUpdate(urlUpdateObj, \"`Status` = 3\")")
      affectDB = self.dbWrapper.affect_db
      self.dbWrapper.affect_db = True
      updatedRowsCount = self.dbWrapper.urlUpdate(urlUpdateObj, "`Status` = 3")
      self.dbWrapper.affect_db = affectDB
      logger.debug("!!! updatedRowsCount = " + str(updatedRowsCount))


  # #updateURL
  #
  # @param batchItem - incoming batchItem
  # @param batchId - base batchId
  # @param status - value for status field updating
  def updateURL(self, batchItem, batchId, status=dc.EventObjects.URL.STATUS_CRAWLING):

    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["urlObj", "dbWrapper", "siteId"])
      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, batchItem.urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)
      urlUpdateObj.batchId = batchId
      if not self.urlObj.httpMethod:
        urlUpdateObj.httpMethod = batchItem.urlObj.httpMethod = "get"
      else:
        urlUpdateObj.httpMethod = batchItem.urlObj.httpMethod = self.urlObj.httpMethod

      urlUpdateObj.status = batchItem.urlObj.status = status
      batchItem.urlObj.crawled += 1
      urlUpdateObj.crawled = SQLExpression("`Crawled`+1")
      urlUpdateObj.tcDate = batchItem.urlObj.tcDate = SQLExpression("NOW()")
      urlUpdateObj.UDate = batchItem.urlObj.UDate = SQLExpression("NOW()")

      if status == dc.EventObjects.URL.STATUS_CRAWLING:
        #####urlUpdateObj.errorMask = batchItem.urlObj.errorMask = 0
        urlUpdateObj.contentType = batchItem.urlObj.contentType = dc.EventObjects.URL.CONTENT_TYPE_UNDEFINED
        #####urlUpdateObj.size = batchItem.urlObj.size = 0
        urlUpdateObj.httpCode = batchItem.urlObj.httpCode = 0

      updatedRowsCount = self.dbWrapper.urlUpdate(urlUpdateObj)
      logger.debug("!!! updatedRowsCount = " + str(updatedRowsCount))


  # #updateURLStatus
  #
  # @param urlId - urlId
  # @param status - value for status field updating
  def updateURLStatus(self, urlId, status=dc.EventObjects.URL.STATUS_CRAWLED):
    if status is not None and self.dbWrapper is not None:
      self.checkFieldsIsNone(["siteId"])
      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)
      urlUpdateObj.status = status
      updatedRowsCount = self.dbWrapper.urlUpdate(urlUpdateObj)
      logger.debug("!!! updatedRowsCount = " + str(updatedRowsCount))


  # #resetErrorMask reset url's errorMask, using db-task wrapper
  #
  # @param batchItem - incoming batchItem
  def resetErrorMask(self, batchItem):
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId"])
      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, batchItem.urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)
      urlUpdateObj.errorMask = batchItem.urlObj.errorMask = 0
      urlUpdateObj.tcDate = batchItem.urlObj.tcDate = SQLExpression("NOW()")
      urlUpdateObj.UDate = batchItem.urlObj.UDate = SQLExpression("NOW()")
      self.dbWrapper.urlUpdate(urlUpdateObj)


  # #addURLFromBatchToDB inserts new URL in to the db with auto-removing
  #
  # @param batchItem - incoming BatchItem object
  # @param crawlerType - url's crawlingType, we have used for internal checks
  # @param recrawlPeriod - url's recrawlPeriod, we have used for internal checks
  # @param autoRemoveProps - param send into URLProcess.autoRemoveURL method call
  def addURLFromBatchToDB(self, batchItem, crawlerType, recrawlPeriod, autoRemoveProps):
    # variable for result
    ret = True

    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId", "urlTable"])
      try:
        siteStatusObj = dc.EventObjects.SiteStatus(Utils.autoFillSiteId(self.siteId, logger))
        result = self.dbWrapper.siteStatus(siteStatusObj)
        if result is not None:
          maxURLs = result.maxURLs
          if ((crawlerType != dc.EventObjects.Batch.TYPE_REAL_TIME_CRAWLER) and \
          (result.state != dc.EventObjects.Site.STATE_ACTIVE)) or \
          ((crawlerType == dc.EventObjects.Batch.TYPE_REAL_TIME_CRAWLER) and \
          (result.state == dc.EventObjects.Site.STATE_DISABLED)):
            logger.debug("Warning: Batch CrawlerType: %s, site state is %s but not STATE_ACTIVE!", crawlerType,
                         str(result.state))
            raise SyncronizeException("Site state is not active, state=" + str(result.state))

          if (result.maxErrors > 0) and (result.errors > result.maxErrors):
            msg = "Site maxErrors limit " + str(result.maxErrors) + " reached " + str(result.errors)
            logger.debug(msg)
            raise SyncronizeException(msg)

          # Check the limit of the maxURLs for count of active URLs (not migrated with batches)
          if DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE_ACTIVE in autoRemoveProps:
            where = autoRemoveProps[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE_ACTIVE]
          else:
            where = "NOT (`Status`=4 AND `Crawled`=0 AND `Processed`=0)"
          query = "SELECT COUNT(*) FROM `%s` " % self.urlTable
          query += "WHERE " + where
          result = self.dbWrapper.customRequest(query, CrawlerTask.DB_URLS)
          if len(result) > 0 and len(result[0]) > 0:
            activeURLs = result[0][0]
            logger.debug("Active URLs count: " + str(activeURLs) + ", maxURLs: " + str(maxURLs))
            if (maxURLs > 0) and (activeURLs >= maxURLs):
              autoRemoved = URLProcess.autoRemoveURL(autoRemoveProps, recrawlPeriod, self.urlTable, self.dbWrapper)
              if autoRemoved < 1:
                msg = "Active URLs:" + str(activeURLs) + " > MaxURLs:" + str(maxURLs) + " and no one auto-removed!"
                logger.debug(msg)
                raise SyncronizeException(msg)
              else:
                logger.debug(str(autoRemoved) + " URLs auto-removed to insert new URL from batch")
          else:
            msg = "Error of query processing, no rows returned:\n" + query
            logger.debug(msg)
            raise SyncronizeException(msg)

          batchItem.urlObj.CDate = str(datetime.datetime.now())
          batchItem.urlObj.UDate = batchItem.urlObj.CDate
          batchItem.urlObj.tcDate = batchItem.urlObj.CDate
          batchItem.urlObj.batchId = 0  # self.batch.id
          result = self.dbWrapper.urlNew([batchItem.urlObj])
          logger.debug("rows_count: %s", result)
          self.isUpdateCollection = True
          # self.updateCollectedURLs()
        else:
          raise SyncronizeException("Execute last SQL query(SiteStatus), no rows returned:\n")
      except Exception as err:
        logger.debug('Error add new url from batch (another host source):' + str(err))
        ret = False
        raise err

    return ret


  # checkDictEmptyStrings method checks dict by keys list
  #
  # @param inDict - incoming dict
  # @param keys - incoming keys list
  # @return bool value of checking
  @staticmethod
  def checkDictEmptyStrings(inDict, keys):
    ret = False
    for key in keys:
      if key in inDict and inDict[key] != '':
        ret = True
      else:
        ret = False
        break
    return ret



  # #Auto remove resources
  # Removes resources in condition based on dc_sites.sites_properties items
  #
  # @param autoRemoveProps - list of autoremove properties
  # @param recrawlPeriod - used only for replacing in autoRemoveProps field
  # @param urlTable - currently table in dc_urls db
  # @param wrapper - db_task wrapper
  # @return number of URLs
  @staticmethod
  def autoRemoveURL(autoRemoveProps, recrawlPeriod, urlTable, wrapper):
    ret = 0
    if wrapper is not None:
      try:
        # logger.debug("Auto remove properties:\n%s", varDump(autoRemoveProps))
        # If defined auto remove properties and set in proper values
        if URLProcess.checkDictEmptyStrings(autoRemoveProps, [DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES,
                                                              DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE,
                                                              DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER]):
          # Select candidates to remove
          query = "SELECT Site_Id, URLMd5 FROM %s WHERE %s ORDER BY %s LIMIT %s" % \
                  (urlTable,
                   autoRemoveProps[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE].replace("%RecrawlPeriod%", str(recrawlPeriod)),
                   autoRemoveProps[DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER],
                   autoRemoveProps[DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES])
          logger.debug("SQL to select auto remove candidates: %s", query)
          result = wrapper.customRequest(query, CrawlerTask.DB_URLS)
          if len(result) > 0:
            urlsToDelete = []
            for row in result:
              # Create new URLDelete object
              urlDelete = dc.EventObjects.URLDelete(row[0], row[1], dc.EventObjects.URLStatus.URL_TYPE_MD5,
                                                    reason=dc.EventObjects.URLDelete.REASON_CRAWLER_AUTOREMOVE)
              urlsToDelete.append(urlDelete)
              logger.debug("URL added to auto remove URLMd5:[%s]", row[1])
            drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_DELETE, urlsToDelete)
            responseDRCESyncTasksCover = wrapper.process(drceSyncTasksCoverObj)
            logger.debug("Response from db-task module on URLDelete operation:\n%s", \
                              Utils.varDump(responseDRCESyncTasksCover))
            deleted = 0
            if isinstance(responseDRCESyncTasksCover, DC_CONSTS.DRCESyncTasksCover):
              generalResponse = responseDRCESyncTasksCover.eventObject
              if isinstance(generalResponse, GeneralResponse):
                deleted = sum([el for el in generalResponse.statuses if el])
            ret = deleted
          else:
            logger.debug("No auto remove candidates or SQL query error!")
        else:
          logger.debug("No mandatory auto remove properties in auto_remove_props:\n" + Utils.varDump(autoRemoveProps))
      except Exception as err:
        ExceptionLog.handler(logger, err, 'Error of auto remove operation:')

    return ret


  # #updateCollectTimeAndMime
  # add time cost of collect url to URL.CrawlingTime
  # and update Detected MIME type
  #
  # @param detectedMime - mine type from current page
  # @param batchItem - incoming batch item
  # @param crawledTime - datatime used for filling some fields
  # @param autoDetectMime - used for check detectedMime param before contentType field updating
  def updateCollectTimeAndMime(self, detectedMime, batchItem, crawledTime, autoDetectMime, httpHeaders=None,
                               strContent=None):
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId"])
      if crawledTime is not None:
        collectTime = int((time.time() - crawledTime) * 1000)
      else:
        collectTime = 0
      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, batchItem.urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)
      if strContent is not None:
        urlUpdateObj.rawContentMd5 = hashlib.md5(strContent).hexdigest()
      urlUpdateObj.crawlingTime = SQLExpression(("`CrawlingTime` + %s" % str(collectTime)))
      urlUpdateObj.totalTime = SQLExpression(("`TotalTime` + %s" % str(collectTime)))
      urlUpdateObj.tcDate = SQLExpression("NOW()")
      urlUpdateObj.UDate = SQLExpression("NOW()")
      logger.debug(">>> detectMime = " + str(detectedMime))
      if httpHeaders is not None:
        for header in httpHeaders:
          if header.lower() == "etag":
            # Simple get only first from several
            urlUpdateObj.eTag = httpHeaders[header].split(',')[0].strip("\"'")
      if detectedMime is not None and autoDetectMime is not None:
        urlUpdateObj.contentType = str(detectedMime)
      self.dbWrapper.urlUpdate(urlUpdateObj)


  # # urlDBSync synchronize url object with database
  #
  # @param batchItem - incoming batch item
  # @param crawlerType - url's crawlingType, we have used for internal checks
  # @param recrawlPeriod - url's recrawlPeriod, we have used for internal checks
  # @param autoRemoveProps - list of autoremove properties
  def urlDBSync(self, batchItem, crawlerType, recrawlPeriod, autoRemoveProps):
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId"])
      self.isUpdateCollection = False
      # Request for check exists url on here host
      sqlQuery = "SELECT COUNT(*) FROM `%s` WHERE `URLMd5` = '%s'" % \
                 (DB_CONSTS.DC_URLS_TABLE_NAME_TEMPLATE % self.siteId, batchItem.urlId)
      logger.debug("!!! urlDBSync sqlQuery: " + str(sqlQuery))

      result = self.dbWrapper.customRequest(sqlQuery, CrawlerTask.DB_URLS)
      logger.debug("!!! urlDBSync result: " + varDump(result))

      isExist = False
      if result is not None and len(result) > 0 and len(result[0]) > 0:
        logger.debug("!!! urlDBSync result[0][0]: " + str(result[0][0]) + " type: " + str(type(result[0][0])))
        isExist = bool(int(result[0][0]) > 0)

      try:
        if isExist:
          logger.debug("Url already exist in DB.")
        else:
          # When url come from another dc cluster's host it is not present in the db
          if self.addURLFromBatchToDB(batchItem, crawlerType, recrawlPeriod, autoRemoveProps):
            self.urlDBSync(batchItem, crawlerType, recrawlPeriod, autoRemoveProps)
          else:
            msg = "Can't add url from batch."
            logger.debug(msg)
            raise SyncronizeException(msg)
      except SyncronizeException, err:
        logger.debug("Can't synchronize url with db: " + str(err))
        raise err


  # #updateAdditionProps update some fields for URL (makes URLUpdate operation)
  #
  # @param internalLinksCount - count of internal links from page
  # @param externalLinksCount - count of enternal links from page
  # @param batchItem - incoming batch item
  # @param size - value for .size field update
  # @param freq - value for .freq field update
  # @param contentMd5 - value for .contentMd5 field update
  def updateAdditionProps(self, internalLinksCount, externalLinksCount, batchItem, size, freq, contentMd5):
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "siteId"])
      urlUpdateObj = dc.EventObjects.URLUpdate(self.siteId, batchItem.urlId, dc.EventObjects.URLStatus.URL_TYPE_MD5, \
                                               normalizeMask=self.normMask)
      urlUpdateObj.tcDate = SQLExpression("NOW()")
      urlUpdateObj.size = size
      urlUpdateObj.linksI = internalLinksCount
      urlUpdateObj.linksE = externalLinksCount
      urlUpdateObj.freq = freq
      urlUpdateObj.rawContentMd5 = contentMd5
      self.dbWrapper.urlUpdate(urlUpdateObj)


  # #createUrlObjForCollectURLs - creates and returns urlObj for collectedURL operation
  #
  # @param urlMd5 - url's md5
  # @param formMethods - formMethods post/get form data
  # @param urlId - parent URL md5
  # @param depth - url's depth in site structure
  # @param detectedMime -
  # @param maxURLsFromPage
  def createUrlObjForCollectURLs(self, urlMd5, formMethods, parentMd5, depth, detectedMime, maxURLsFromPage):
    self.checkFieldsIsNone(["url", "siteId", "urlObj"])
    ret = dc.EventObjects.URL(self.siteId, self.url, normalizeMask=self.normMask)
    ret.type = self.urlObj.type
    ret.urlMd5 = urlMd5
    ret.requestDelay = self.urlObj.requestDelay
    ret.httpTimeout = self.urlObj.httpTimeout
    ret.httpMethod = formMethods.get(self.url, "get")
    ret.parentMd5 = parentMd5
    ret.maxURLsFromPage = maxURLsFromPage
    ret.tcDate = SQLExpression("NOW()")
    ret.UDate = SQLExpression("NOW()")
    ret.depth = (depth + 1)
    ret.contentType = detectedMime
    ret.priority = self.urlObj.priority
    # TODO Additional URL init
    if self.siteProperties is not None and "URLS_FIELDS_INIT" in self.siteProperties:
      URLProcess.additionalUrlObjInit(ret, self.siteProperties["URLS_FIELDS_INIT"],
                                      {"site": self.site, "parent": self.urlObj})
    return ret


  # #createUrlObjForChain - creates and returns urlObj for collected chain URL operation, checks collected url
  # by pattern before
  #
  # @param pattern for check url canditae to chain urls
  # @param urlMd5 - url's md5
  # @param formMethods - formMethods post/get form data
  # @param urlId - parent URL md5
  # @param depth - url's depth in site structure
  # @param detectedMime - incoming value for detectedMime field
  # @param maxURLsFromPage - incoming value for maxURLsFromPage field
  def createUrlObjForChain(self, pattern, urlMd5, formMethods, parentMd5, depth, detectedMime, maxURLsFromPage):
    ret = None
    self.checkFieldsIsNone(["url"])
    # logger.debug(">>> chain patter is = " + str(pattern) + " url = " + self.url)
    if re.search(pattern, self.url) is not None:
      ret = self.createUrlObjForCollectURLs(urlMd5, formMethods, parentMd5, depth, detectedMime, maxURLsFromPage)
      ret.type = dc.EventObjects.URL.TYPE_CHAIN
    return ret


  # #updateTypeForURLObjects updates url type in DB
  #
  # @param urlObjects - list of url objects
  # @param typeArg - updated url type
  def updateTypeForURLObjects(self, urlObjects, typeArg=dc.EventObjects.URL.TYPE_CHAIN):
    if self.dbWrapper is not None:
      updateUrlObjects = []
      for urlObject in urlObjects:
        localUrlObject = dc.EventObjects.URLUpdate(urlObject.siteId, urlObject.url, normalizeMask=self.normMask)
        localUrlObject.urlMd5 = urlObject.urlMd5
        localUrlObject.type = typeArg
        updateUrlObjects.append(localUrlObject)
      if len(updateUrlObjects) > 0:
        self.dbWrapper.urlUpdate(updateUrlObjects)



  # #fillRssFieldInUrlObj - fills some fields, related with rss, in internal urlObj
  #
  # @param oldUrl - incoming previous ulr
  # @param objectUrlUlr - incoming url object
  # @param batchItem - incoming bachItem
  # @param processorName - processor name
  # @param feed - incoming source of rss data
  # @param rootFeed - bool param that specifyied use feed element from rss struture of entities element
  # @return dict with filled rss values
  def fillRssFieldInUrlObj(self, oldUrl, objectUrlUlr, batchItem, processorName, feed, rootFeed=False):
    # logger.debug("oldUrl=%s\nobjectUrlUlr=%s\nbatchItem=%s\nprocessorName=%s\nfeed=%s\n",
    #             Utils.varDump(oldUrl),
    #             Utils.varDump(objectUrlUlr),
    #             Utils.varDump(batchItem),
    #             Utils.varDump(processorName),
    #             str(feed))
    self.checkFieldsIsNone(["url", "siteId", "urlObj"])
    ret = None
    status = dc.EventObjects.URL.STATUS_CRAWLED
    crawled = 1
    localType = dc.EventObjects.URL.TYPE_FETCHED
    if processorName == PCONSTS.PROCESSOR_RSS:
      status = dc.EventObjects.URL.STATUS_NEW
      crawled = 0
      localType = dc.EventObjects.URL.TYPE_SINGLE
    if rootFeed:
      ret = self.fillRssFieldOneElem(feed.feed, objectUrlUlr, batchItem, status, crawled, localType)
    else:
      for entry in feed.entries:
        if hasattr(entry, 'link'):
#           logger.debug("entry.link=%s, oldUrl=%s", Utils.varDump(entry.link), Utils.varDump(oldUrl))
          if entry.link == oldUrl and ret is None:
            ret = self.fillRssFieldOneElem(entry, objectUrlUlr, batchItem, status, crawled, localType)
            if ret is None:
              logger.debug("Getting next candidate URL")
          elif ret is not None and "urlObj" in ret and ret["urlObj"] is None:
            ret = self.fillRssFieldOneElem(entry, objectUrlUlr, batchItem, status, crawled, localType)

    return ret


  # #fillRssFieldOneElem - fills one rss field element
  #
  # @param entry - one rss entry
  # @param urlObj objectUrlUlr - incoming url object
  # @param batchItem - incoming bachItem
  # @param status - calculated ststus for urlObj
  # @param crawled - calculated crawled value for urlObj
  # @param localType - calculated localType value for urlObj
  # @return one filled rss dict element
  def fillRssFieldOneElem(self, entry, urlObj, batchItem, status, crawled, localType):
    # variable for result
    ret = {}
    ret["entry"] = entry
    ret["urlObj"] = dc.EventObjects.URL(self.siteId, self.url, normalizeMask=self.normMask)
    ret["parent_rss_feed"] = urlObj
    ret["parent_rss_feed_urlMd5"] = batchItem.urlId
    # Getting pubdate from feed
    pubdate = None
    for date in CONSTS.pubdateFeedNames:
      if date in entry:
        try:
          dt = DateTimeType.parse(entry[date], True, logger, False)
          if dt is not None:
            logger.debug("Convert pubdate from: '%s' to '%s'", str(entry[date]), dt.isoformat(' '))
            pubdate = DateTimeType.toUTC(dt).strftime("%Y-%m-%d %H:%M:%S")
            logger.debug("pubdate converted to UTC: '%s'", str(pubdate))
            break
        except TypeError:
          logger.debug("Unsupported date format: '%s'", str(entry[date]))
        except Exception, err:
          logger.debug("Error: %s, data: '%s'", str(err), str(entry[date]))

    logger.debug("!!! Before apply 'SQLExpression' and 'STAGE_COLLECT_URLS' pubdate: " + str(pubdate))
    localFilters = Filters(None, self.dbWrapper, batchItem.siteId, 0, None, Filters.OC_SQLE, Filters.STAGE_COLLECT_URLS)
    isExistFilter = localFilters.isExist(Filters.STAGE_COLLECT_URLS, Filters.OC_SQLE)
    logger.debug("Filter is exists: " + str(bool(isExistFilter)))
    if isExistFilter and  pubdate is not None:
      collectURLs = CollectURLs()
      if collectURLs.filtersApply(None, '', batchItem.depth, self.dbWrapper, batchItem.siteId,
                                  {'PDATE':str(pubdate)}, Filters.OC_SQLE, Filters.STAGE_COLLECT_URLS, None, False):
        logger.debug("Candidate URL matched SQLExpression filter.")
      else:
        logger.debug("Candidate URL not matched SQLExpression filter, skipped.")
        # ret["urlObj"] = None
        ret = None
        return ret

    if len(entry.links) > 0 and hasattr(entry.links[0], 'type'):
      contentType = entry.links[0].type
    ret["urlObj"].status = status
    ret["urlObj"].crawled = crawled
    ret["urlObj"].contentType = contentType
    ret["urlObj"].pDate = pubdate
    ret["urlObj"].type = localType
    size = len(str(ret))
    ret["urlObj"].size = size
    ret["pubdate"] = pubdate
    # TODO Additional URL init
    if self.siteProperties is not None and "URLS_FIELDS_INIT" in self.siteProperties:
      URLProcess.additionalUrlObjInit(ret, self.siteProperties["URLS_FIELDS_INIT"],
                                      {"site": self.site, "parent": self.urlObj})

    # logger.debug(">>>> ret[\"urlObj\"].pDate = " + str(ret["urlObj"].pDate))

    return ret


  # #urlTemplateApply - method applies url's template for current url
  #
  # @param url - incoming url
  # @param crawlerType - crawler's type
  # @param urlTempalteRegular - url template, that applying in regularCrawl case
  # @param urlTempalteRealtime - url template, that applying in realTimeCrawl case
  # @param urlTempalteRegularEncode - make url enconing for regularCrawl or not
  # @param urlTempalteRealtimeEncode - make url enconing for realTimeCrawl or not
  # @return processed url, after url template applying
  def urlTemplateApply(self, url, crawlerType, urlTempalteRegular, urlTempalteRealtime, urlTempalteRegularEncode,
                       urlTempalteRealtimeEncode):
    ret = url
    if crawlerType == dc.EventObjects.Batch.TYPE_REAL_TIME_CRAWLER:
      if urlTempalteRealtime is not None:
        try:
          if urlTempalteRealtimeEncode is not None and bool(int(urlTempalteRealtimeEncode)):
            encodedUrl = urllib.quote(url)
          else:
            encodedUrl = url
        except ValueError:
          encodedUrl = url
        ret = urlTempalteRealtime.replace(self.URL_TEMPLATE_CONST, encodedUrl)
    else:
      if urlTempalteRegular is not None:
        try:
          if urlTempalteRegularEncode is not None and bool(int(urlTempalteRegularEncode)):
            encodedUrl = urllib.quote(url)
          else:
            encodedUrl = url
        except ValueError:
          encodedUrl = url
        ret = urlTempalteRegular.replace(self.URL_TEMPLATE_CONST, encodedUrl)
    if ret != url:
      logger.debug(">>> url was replaced ")
      logger.debug(">>> new url = " + ret)
    return ret


  # #conditionEvaluate - static method evaluates condition in condition param, uses conditionalData for it.
  #
  # @param condition - incoming condition string
  # @param conditionalData - additional condition comparing data
  # @param return bool value - result of condition evaluating
  @staticmethod
  def conditionEvaluate(condition, conditionalData):
    ret = False
    conditionElements = condition.split(' ', 2)
    if len(conditionElements) == 3:
      objectName = conditionElements[0]
      operationName = conditionElements[1]
      value = conditionElements[2]
      if len(value) > 0 and (value[0] == '"' or value[0] == '\''):
        value = value[1:]
      if len(value) > 0 and (value[-1] == '"' or value[-1] == '\''):
        value = value[0:-1]
      objectName = objectName.strip().split('.')
      if len(objectName) >= 2:
        fieldName = objectName[1]
        objectName = objectName[0]
        if objectName in conditionalData and hasattr(conditionalData[objectName], fieldName):
          if operationName == '=' or operationName == "==":
            if str(getattr(conditionalData[objectName], fieldName)) == value:
              ret = True
          elif operationName == "match":
            if re.compile(value).match(str(getattr(conditionalData[objectName], fieldName))) is not None:
              ret = True
          elif operationName == "search":
            if re.compile(value).search(str(getattr(conditionalData[objectName], fieldName))) is not None:
              ret = True
          elif operationName == "<>" or operationName == "!=":
            if str(getattr(conditionalData[objectName], fieldName)) != value:
              ret = True
          elif operationName == "is" and value == 'empty':
            if str(getattr(conditionalData[objectName], fieldName)) == '':
              ret = True

    return ret


  # #additionalUrlObjInit - static method makes additional urlObj fields init, applies conditions from urlInitParam
  #
  # @param urlObj - instance of initialized urlObj
  # @param urlInitParam - string with "URLS_FIELDS_INIT" siteParameter value
  # @param conditionalData - additional condition comparing data
  @staticmethod
  def additionalUrlObjInit(urlObj, urlInitParam, conditionalData):
    try:
      urlInit = json.loads(urlInitParam)
      for fieldName in urlInit:
        if hasattr(urlObj, fieldName):
          for condition in urlInit[fieldName]["conditions"]:
            if (isinstance(condition, types.BooleanType) and condition) or \
            (isinstance(condition, types.StringTypes) and URLProcess.conditionEvaluate(condition, conditionalData)):
              setattr(urlObj, fieldName, urlInit[fieldName]["value"])
              break
    except Exception as excp:
      logger.debug(">>> some error with URLS_FIELDS_INIT param processing; err=" + str(excp))
