'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import glob
import os
import base64
from datetime import datetime

import dc.EventObjects
import dc.Constants as DC_CONSTANTS
import dc_db.Constants as Constants
from dc_db.URLFetchTask import URLFetchTask
from dc_db.StatisticLogManager import StatisticLogManager
from dc_db.ProcessedContentInternalStruct import ProcessedContentInternalStruct
from dc_db.AttrFetchTask import AttrFetchTask
from app.Utils import PathMaker
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process urlContent event
class URLContentTask(object):


  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  # @param dBDataTask instance of DBDataTask module
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask, dcSiteTemplate, keyValueDefaultFile, dcStatTemplate,
               dcLogTemplate):
    self.keyValueStorageDir = keyValueStorageDir
    self.rawDataDir = rawDataDir
    self.processedContents = []
    self.rawContents = []
    self.headers = []
    self.requests = []
    self.meta = []
    self.cookies = []
    self.contentMask = None
    self.dbDataTask = dBDataTask
    self.urlFetchTask = URLFetchTask(keyValueStorageDir, rawDataDir, dBDataTask, dcSiteTemplate,
                                     keyValueDefaultFile, dcStatTemplate, dcLogTemplate,
                                     Constants.DEFAULT_LOCK_TTL)


  # #method clears main contants
  def clearContents(self):
    self.processedContents = []
    self.rawContents = []
    self.headers = []
    self.requests = []
    self.meta = []
    self.cookies = []


  # #make all necessary actions to get urls content data from storages
  #
  # @param urlContentRequests list of URLContentRequest objects
  # @param queryCallback function for queries execution
  # @return list of URLContentResponse objects
  def process(self, urlContentRequests, queryCallback):  # pylint: disable=W0613
    urlContentResponses = []
    # @todo add more complex case, implemented only from rawDataDir
    for urlContentRequest in urlContentRequests:
      if urlContentRequest is None:
        urlContentResponses.append(None)
      elif hasattr(urlContentRequest, "urlFetch") and urlContentRequest.urlFetch is not None:
        urlFetches = []
        urlFetches.append(urlContentRequest.urlFetch)
        urls = self.urlFetchTask.process(urlFetches, queryCallback)
        for url in urls:
          urlContentRequest.urlMd5 = ""
          urlContentRequest.siteId = url.siteId
          urlContentRequest.url = url.url
          self.calcEmptyFields(urlContentRequest)
          StatisticLogManager.logUpdate(queryCallback, "LOG_URL_CONTENT", urlContentRequest, urlContentRequest.siteId,
                                        urlContentRequest.urlMd5)
          urlContentResponses.append(self.getURLContent(urlContentRequest, queryCallback))
      else:
        self.calcEmptyFields(urlContentRequest)
        StatisticLogManager.logUpdate(queryCallback, "LOG_URL_CONTENT", urlContentRequest, urlContentRequest.siteId,
                                      urlContentRequest.urlMd5)
        urlContentResponses.append(self.getURLContent(urlContentRequest, queryCallback))
      logger.debug(">>> urlContentResponses len = %s", str(len(urlContentResponses)))
      # logger.debug("!!! urlContentResponses: %s", Utils.varDump(urlContentResponses, stringifyType=0, strTypeMaxLen=5000))

    return urlContentResponses


  # #calcEmptyFields method calculate values of empty fields
  #
  # @param urlContentRequest object of  URLContentRequest type
  def calcEmptyFields(self, urlContentRequest):
    if urlContentRequest.siteId == "":
      urlContentRequest.siteId = "0"
    if urlContentRequest.urlMd5 is None or urlContentRequest.urlMd5 == "":
      urlContentRequest.urlMd5 = urlContentRequest.fillMD5(urlContentRequest.url)


  # #generates and returns dbFieldsDict
  #
  # @param dbFieldsList - list of db fields names
  # @param dbFieldsListDefaultValues - dict with default values for DB fields names
  # @param row db row, not None
  # @return just generated dbFieldsDict dict
  def genDBFields(self, dbFieldsList, dbFieldsListDefaultValues, row):
    ret = {}
    for fName in dbFieldsList:
      if fName in dbFieldsListDefaultValues:
        ret[fName] = dbFieldsListDefaultValues[fName]

    for fName in dbFieldsList:
      if fName is not None:
        if fName in row:
          if fName in ["UDate", "CDate", "LastModified", "TcDate", "PDate"]:
            ret[str(fName)] = str(row[fName])
          else:
            ret[str(fName)] = row[fName]
        else:
          ret[str(fName)] = None
    return ret


  # #read content from KVDB if CONTENT_TYPE_PROCESSED have setted
  #
  # @param urlContentRequest object of  URLContentRequest type
  # @param dataDir - contains file directory
  # @return list of Content objects
  def contentProcessed(self, dataDir, urlContentRequest, contentMask, queryCallback):  # pylint: disable=W0613
    ret = []
    dataFetchRequest = dc.EventObjects.DataFetchRequest(urlContentRequest.siteId, urlContentRequest.urlMd5)
    dataFetchResponse = self.dbDataTask.process(dataFetchRequest, queryCallback)
    if dataFetchResponse is not None and len(dataFetchResponse.resultDict) > 0:
      if ProcessedContentInternalStruct.DATA_FIELD in dataFetchResponse.resultDict and \
      dataFetchResponse.resultDict[ProcessedContentInternalStruct.DATA_FIELD] is not None and \
      ProcessedContentInternalStruct.CDATE_FIELD in dataFetchResponse.resultDict and \
      dataFetchResponse.resultDict[ProcessedContentInternalStruct.CDATE_FIELD] is not None:
        ret = ProcessedContentInternalStruct.parseProcessedBuf(\
              dataFetchResponse.resultDict[ProcessedContentInternalStruct.DATA_FIELD], \
              dataFetchResponse.resultDict[ProcessedContentInternalStruct.CDATE_FIELD], contentMask)
        logger.debug(">>> ret_content == " + str(ret))
    logger.debug(">>> UrlContent result = " + str(dataFetchResponse.__dict__))
    return ret


  # #extract url fields from Database
  #
  # @param siteId site Id
  # @param urlMD5 urls urlMD5
  # @return first row of SQL request
  def selectURLFromMySQL(self, siteId, urlMD5, queryCallback):
    row = None
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    SELECT_URL_QUERY = "SELECT * FROM %s WHERE `URLMd5` = '%s'"
    query = SELECT_URL_QUERY % (tableName, urlMD5)
    res = queryCallback(query, Constants.SECONDARY_DB_ID, Constants.EXEC_NAME)
    if hasattr(res, '__iter__') and len(res) >= 1:
      row = res[0]
    return row


  # #fillLists - fills incoming list of file's content
  #
  # @param filePath - path to the content file
  # @param elemList - incoming filled list
  def fillLists(self, filePath, elemList, typeId=dc.EventObjects.Content.CONTENT_RAW_CONTENT):
    if os.path.isfile(filePath):
      try:
        fd = open(filePath)
        raw_content = fd.read()
        localDate = datetime.fromtimestamp(os.path.getctime(filePath))
        elemList.append(dc.EventObjects.Content(base64.b64encode(raw_content.decode('utf-8')), localDate.isoformat(' '), typeId))
        fd.close()
      except IOError as err:
        elemList.append(None)
        logger.debug(">>> IOError with file = %s MSG = %s", str(filePath), str(err.message))
    else:
      elemList.append(None)
      logger.debug(">>> No file = %s", str(filePath))


  # #contentRaw - content reader
  #
  # @param fList - incoming file list
  # @param isBreak - break after firs element or not
  def contentRaw(self, fList, isBreak, contentTypeId, parseAdditionType):
    fd = None
    wasOpen = False
    for filePath in fList:
      if os.path.isfile(filePath):
        try:
          fd = open(filePath)
          raw_content = fd.read()
          localDate = datetime.fromtimestamp(os.path.getctime(filePath))
          self.rawContents.append(dc.EventObjects.Content(base64.b64encode(raw_content), localDate.isoformat(' '),
                                                          contentTypeId))
          wasOpen = True
          fd.close()
        except IOError as err:
          logger.debug(">>> IOError with file = %s MSG = %s", str(filePath), str(err.message))

        if wasOpen and parseAdditionType:
          filePath = filePath[0: len(DC_CONSTANTS.RAW_DATA_SUFF) * -1]
          filePath += DC_CONSTANTS.RAW_DATA_HEADERS_SUFF
          if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_HEADERS:
            self.fillLists(filePath, self.headers, dc.EventObjects.Content.CONTENT_HEADERS_CONTENT)
          filePath = filePath[0: len(DC_CONSTANTS.RAW_DATA_HEADERS_SUFF) * -1]
          filePath += DC_CONSTANTS.RAW_DATA_REQESTS_SUFF
          if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_REQUESTS:
            self.fillLists(filePath, self.requests, dc.EventObjects.Content.CONTENT_REQUESTS_CONTENT)
          filePath = filePath[0: len(DC_CONSTANTS.RAW_DATA_REQESTS_SUFF) * -1]
          filePath += DC_CONSTANTS.RAW_DATA_META_SUFF
          if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_META:
            self.fillLists(filePath, self.meta, dc.EventObjects.Content.CONTENT_META_CONTENT)
          filePath = filePath[0: len(DC_CONSTANTS.RAW_DATA_META_SUFF) * -1]
          filePath += DC_CONSTANTS.RAW_DATA_COOKIES_SUFF
          if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_COOKIES:
            self.fillLists(filePath, self.cookies, dc.EventObjects.Content.CONTENT_COOKIES_CONTENT)
      if isBreak:
        break


  # #contentRawCommon - common content reader
  #
  # @param dataDir - contains file directory
  # @param localReverse - file reverse sorting (boolean)
  # @param allFiles - all files read or not (boolean)
  def contentRawCommon(self, dataDir, localReverse=False, allFiles=False, rawDataSuff=DC_CONSTANTS.RAW_DATA_SUFF,
                       contentTypeId=dc.EventObjects.Content.CONTENT_RAW_CONTENT, parseAdditionType=True):
    fileMask = (dataDir + "/*" + rawDataSuff)
    logger.debug(">>> contentRaw fList = " + str(fileMask))
    fList = sorted(glob.glob(fileMask), key=os.path.getctime, reverse=localReverse)
    self.contentRaw(fList, (not allFiles), contentTypeId, parseAdditionType)


  # #fillAdditionContentTypes fills result with contents of addition raw content types.
  #
  # @param typeMask - typeMask of supported content type
  # @param typeId - content type id, needs for filling Content obj
  # @param suff - raw data file sufffix
  # @param dataDir - raw data file storage dir
  def fillAdditionContentTypes(self, typeMask, typeId, suff, dataDir):
    if self.contentMask & typeMask:
      if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_LAST:
        self.contentRawCommon(dataDir, True, False, suff, typeId, False)
      if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_FIRST:
        self.contentRawCommon(dataDir, False, False, suff, typeId, False)
      if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_ALL:
        self.contentRawCommon(dataDir, False, True, suff, typeId, False)


  # #extract url content from mandatory storage - implemented RAW!!
  #
  # @param urlContentRequest instance of URLContentRequest objects
  # @param queryCallback function for queries execution
  # @return list of URLContentResponse objects
  def getURLContent(self, urlContentRequest, queryCallback):
    dataDir = self.rawDataDir + "/" + urlContentRequest.siteId + "/" + PathMaker(urlContentRequest.urlMd5).getDir()
    self.clearContents()
    self.contentMask = urlContentRequest.contentTypeMask

    if self.contentMask & (dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED | \
                           dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_INTERNAL | \
                           dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_CUSTOM):
      self.processedContents.extend(self.contentProcessed(dataDir, urlContentRequest, self.contentMask, queryCallback))

    if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW:
      if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_LAST:
        self.contentRawCommon(dataDir, True, False)
      if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_FIRST:
        self.contentRawCommon(dataDir, False, False)
      if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_RAW_ALL:
        self.contentRawCommon(dataDir, False, True)

    self.fillAdditionContentTypes(dc.EventObjects.URLContentRequest.CONTENT_TYPE_TIDY,
                                  dc.EventObjects.Content.CONTENT_TIDY_CONTENT, DC_CONSTANTS.RAW_DATA_TIDY_SUFF,
                                  dataDir)

    self.fillAdditionContentTypes(dc.EventObjects.URLContentRequest.CONTENT_TYPE_DYNAMIC,
                                  dc.EventObjects.Content.CONTENT_DYNAMIC_CONTENT, DC_CONSTANTS.RAW_DATA_DYNAMIC_SUFF,
                                  dataDir)

    self.fillAdditionContentTypes(dc.EventObjects.URLContentRequest.CONTENT_TYPE_CHAIN,
                                  dc.EventObjects.Content.CONTENT_CHAIN_PARTS, DC_CONSTANTS.RAW_DATA_CHAIN_SUFF,
                                  dataDir)

    logger.debug("!!!!! self.processedContents: %s", Utils.varDump(self.processedContents, stringifyType=0, ensure_ascii=False, strTypeMaxLen=5000))

    ret = dc.EventObjects.URLContentResponse(urlContentRequest.url, self.rawContents, self.processedContents)
    ret.headers = self.headers
    ret.requests = self.requests
    ret.meta = self.meta
    ret.cookies = self.cookies
    row = self.selectURLFromMySQL(urlContentRequest.siteId, urlContentRequest.urlMd5, queryCallback)

    if row is not None:
      if "Status" in row:
        ret.status = row["Status"]
      if "URL" in row:
        ret.url = row["URL"]
      if "URLMd5" in row:
        ret.urlMd5 = row["URLMd5"]
      if "RawContentMd5" in row:
        ret.rawContentMd5 = row["RawContentMd5"]
      if "ContentURLMd5" in row:
        ret.contentURLMd5 = row["ContentURLMd5"]
      if "Site_Id" in row:
        ret.siteId = row["Site_Id"]
      if hasattr(urlContentRequest.dbFieldsList, '__iter__') and len(urlContentRequest.dbFieldsList) > 0:
        ret.dbFields = self.genDBFields(urlContentRequest.dbFieldsList, \
                                        urlContentRequest.dbFieldsListDefaultValues, \
                                        row)

    if self.contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_ATTRIBUTES:
      if ret.urlMd5 is not None and ret.urlMd5 != "" and ret.siteId is not None:
        ret.attributes = AttrFetchTask.fetchUrlsAttributesByNames(ret.siteId,
                                                                  ret.urlMd5,
                                                                  queryCallback,
                                                                  urlContentRequest.attributeNames)

    return ret
