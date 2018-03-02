"""
HCE project,  Python bindings, Distributed Tasks Manager application.
RTCFinalizer Class content main functional for finalize realtime crawling.

@package: dc_crawler
@file RTCFinalizer.py
@author Oleksii <developers.hce@gmail.com>, bgv, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import sys
import pickle
import logging.config
import ConfigParser
from cement.core import foundation
import app.Consts as APP_CONSTS
import app.Utils as Utils
from app.Utils import varDump
from app.ContentCheck import ContentCheck
import dc.EventObjects as dc_event
import dc.Constants as DC_CONSTS
from dc_db.TasksManager import TasksManager as DBTasksManager
import dc_crawler.Constants as DC_CRAWLER_CONSTS
from dc_crawler.Fetcher import BaseFetcher


# # RTCFinalizer Class content main functional for finalize realtime crawling,
# class inherits from foundation.CementApp
#
class RTCFinalizer(foundation.CementApp):

  # # Constants error messages used in class
  MSG_ERROR_PARSE_CMD_PARAMS = "Error parse command line parameters."
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."
  MSG_ERROR_READ_DB_TASK_CONFIG = "Error read db-task config file."

  # #Constans log messages
  MSG_ERROR_DELETE_URL = "Delete url has failed"
  MSG_DELETE_URL_OK = "URL was deleted"

  # #Constans used options from config file
  FINALIZER_OPTION_LOG = "log"
  FINALIZER_OPTION_DB_TASK_INI = "db_task_ini"

  # Mandatory
  class Meta(object):
    label = DC_CRAWLER_CONSTS.RTC_FINALIZER_APP_NAME
    def __init__(self):
      pass

  # #constructor
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)

    self.logger = None
    self.batch = None
    self.items = None
    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.urlContentResponse = None
    self.rb = None
    self.rc = None
    self.dbTask = None


  # # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)


  # # run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # call initialization application
    self.__initApp()

    # call internal processing
    self.process()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # #initialize application from config files
  #
  # @param - None
  # @return - None
  def __initApp(self):
    if self.pargs.config:
      confLogFileName, confDBTaskName = self.__loadAppConfig(self.pargs.config)
      self.__loadLogConfig(confLogFileName)
      self.dbTask = DBTasksManager(self.__loadDBTaskConfig(confDBTaskName))
    else:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG)
    self.rb = self.pargs.rb
    self.rc = int(self.pargs.rc) if self.pargs.rc is not None else None


  # #load application config file
  #
  # @param configName - name of application config file
  # @return - log config file name and db-task config file name
  def __loadAppConfig(self, configName):
    # variable for result
    confLogFileName = ""
    confDBTaskName = ""

    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        confLogFileName = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, self.FINALIZER_OPTION_LOG))
        confDBTaskName = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, \
                                        self.FINALIZER_OPTION_DB_TASK_INI))

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return confLogFileName, confDBTaskName


  # #load log config file
  #
  # @param configName - name of log rtc-finalizer config file
  # @return - None
  def __loadLogConfig(self, configName):
    try:
      if isinstance(configName, str) and len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)

      # call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  # #load db-task config file
  #
  # @param configName - name of log rtc-finalizer config file
  # @return - config parser instance
  def __loadDBTaskConfig(self, configName):
    # return config parser
    config = None
    if isinstance(configName, str) and len(configName) > 0:
      try:
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.read(configName)

      except Exception, err:
        raise Exception(self.MSG_ERROR_READ_DB_TASK_CONFIG + ' ' + str(err))

    return config


  def getBatchFromInput(self):
    try:
      # read pickled batch object from stdin and unpickle it
      input_pickled_object = sys.stdin.read()
      # self.logger.debug("input_pickled_object: %s", varDump(input_pickled_object))

      # print input_pickled_object
      input_data = (pickle.loads(input_pickled_object))
      # self.logger.debug("input_data: %s", varDump(input_data))

      # print("Batch item: siteId: %s, urlId: %s" %(input_data.siteId, input_data.urlId))
      self.batch = input_data
      self.items = self.batch.items
#       self.logger.debug("Batch: %s", varDump(self.batch, stringifyType=0, maxDepth=10))
    except Exception, err:
      raise Exception('getBatchFromInput error: ' + str(err))


  def getURLContent(self):
    urlContentRequest = []
    num_of_items = len(self.items)
    self.logger.debug("Num of items in batch: <<%s>>" % (num_of_items))
    item_no = 1
    for item in self.items:
      if not item:
        urlContentRequest.append(None)
        self.logger.debug("Item is None.")
      else:
        siteId = item.siteId
        url = item.urlObj.url
        urlId = item.urlId
        self.logger.debug("Item #%s: siteId: <<%s>>, urlId: <<%s>>, url: <<%s>>" % (item_no, siteId, urlId, url))
        _urlContentRequest = dc_event.URLContentRequest(siteId, url)
        _urlContentRequest.dbFieldsList = ["Status", "Crawled", "Processed", "ContentType", "Charset", "ErrorMask", \
                                           "CrawlingTime", "ProcessingTime", "HTTPCode", "Size", "LinksI", "LinksE", \
                                           "RawContentMd5", "LastModified", "CDate", "UDate", "TagsMask", "TagsCount", \
                                           "PDate", "ContentURLMd5", "Batch_Id"]
        urlContentRequest.append(_urlContentRequest)
      item_no = item_no + 1
    self.dbTask.dbTaskMode = self.batch.dbMode
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_CONTENT, urlContentRequest)
    responseDRCESyncTasksCover = self.dbTask.process(drceSyncTasksCoverObj)
    self.urlContentResponse = responseDRCESyncTasksCover.eventObject
    self.logger.debug("urlContentResponse: %s", varDump(obj=self.urlContentResponse, strTypeMaxLen=5000))


  def sendURLContent(self):
    print pickle.dumps(self.urlContentResponse)
    sys.stdout.flush()


  def saveBatchToFile(self):
    if self.rb is not None:
      self.logger.debug("batchSaveFile is = " + str(self.rb))
      urlCleanupList = []
      contentCheck = ContentCheck()
      for item in self.items:
        if item.siteObj is not None and item.siteObj.fetchType == BaseFetcher.TYP_AUTO:
          if item.urlPutObj is not None and contentCheck.lookMetricsinContent(item.urlPutObj):
            self.logger.debug(">>> start checkUrlPutObj")
            metricsApplying = self.selectSiteProperty(item, "FINALIZER_METRICS")
            toRecrawl = contentCheck.checkUrlPutObj(item.urlPutObj, contentCheck.CHECK_TYPE_SIMPLE, metricsApplying)
          else:
            self.logger.debug(">>> start urlObj")
            toRecrawl = contentCheck.checkUrlObj(item.urlObj)
          if not toRecrawl:
            urlCleanup = dc_event.URLCleanup(item.urlObj.siteId, item.urlObj.url)
            urlCleanup.urlType = dc_event.URLStatus.URL_TYPE_MD5
            urlCleanup.url = item.urlObj.urlMd5
            urlCleanupList.append(urlCleanup)
            item.siteObj.fetchType = BaseFetcher.TYP_DYNAMIC
            item.urlObj.status = dc_event.URL.STATUS_SELECTED_CRAWLING
            item.urlObj.crawled = 0
            item.urlObj.urlPut = None
            item.urlPutObj = None
            if self.rc is not None:
              self.exitCode = self.rc
      if len(urlCleanupList) > 0:
        drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_CLEANUP, urlCleanupList)
        self.dbTask.process(drceSyncTasksCoverObj)
      fd = open(self.rb, "w")
      if fd is not None:
        pickleObj = pickle.dumps(self.batch)
        fd.write(pickleObj)
        fd.close()


  def getURLContentFromBatch(self):
    self.urlContentResponse = []
    attributes = []
    for item in self.items:
      url = item.urlObj.url
      if item.urlPutObj is not None:
        # self.logger.debug("item.urlPutObj.putDict.data: %s", varDump(item.urlPutObj.putDict["data"]))
        try:
          if len(item.urlObj.attributes) > 0:
            self.logger.debug("item.urlPutObj.attributes: %s", varDump(item.urlObj.attributes))
            attributes = item.urlObj.attributes
        except Exception, err:
          self.logger.error("load attributes failed: %s", str(err))

        if item.urlPutObj.putDict["cDate"] is not None:
          contents = [dc_event.Content(item.urlPutObj.putDict["data"], item.urlPutObj.putDict["cDate"],
                                       dc_event.Content.CONTENT_PROCESSOR_CONTENT)]
        else:
          contents = [dc_event.Content(item.urlPutObj.putDict["data"],
                                       typeId=dc_event.Content.CONTENT_PROCESSOR_CONTENT)]
      else:
        contents = []
      rawContents = None
      isFetchRawContent = self.selectSiteProperty(item, "FETCH_RAW_CONTENT")
      if item.urlObj.urlPut is not None and isFetchRawContent is not None and int(isFetchRawContent) == 1:
        rawContents = [dc_event.Content(item.urlObj.urlPut.putDict["data"], item.urlObj.urlPut.putDict["cDate"],
                                        dc_event.Content.CONTENT_RAW_CONTENT)]
      urlContentResponse = dc_event.URLContentResponse(url, rawContents, processedContents=contents)
      urlContentResponse.status = 7
      urlContentResponse.urlMd5 = item.urlObj.urlMd5
      urlContentResponse.siteId = item.siteId
      urlContentResponse.contentURLMd5 = item.urlObj.contentURLMd5
      urlContentResponse.rawContentMd5 = item.urlObj.rawContentMd5
      urlContentResponse.attributes = attributes
      urlContentResponse.dbFields = {"Status":item.urlObj.status,
                                     "Crawled":item.urlObj.crawled,
                                     "Processed":item.urlObj.processed,
                                     "ContentType":item.urlObj.contentType,
                                     "Charset":item.urlObj.charset,
                                     "ErrorMask":item.urlObj.errorMask,
                                     "CrawlingTime":item.urlObj.crawlingTime,
                                     "ProcessingTime":item.urlObj.processingTime,
                                     "HttpCode":item.urlObj.httpCode,
                                     "Size":item.urlObj.size,
                                     "LinksI":item.urlObj.linksI,
                                     "LinksE":item.urlObj.linksE,
                                     "RawContentMd5":item.urlObj.rawContentMd5,
                                     "LastModified":item.urlObj.lastModified,
                                     "CDate":item.urlObj.CDate,
                                     "UDate":item.urlObj.UDate,
                                     "TagsMask":item.urlObj.tagsMask,
                                     "TagsCount":item.urlObj.tagsCount,
                                     "PDate":item.urlObj.pDate,
                                     "ContentURLMd5":item.urlObj.contentURLMd5,
                                     "BatchId":item.urlObj.batchId}

      if item.urlPutObj is not None and "properties" in item.urlPutObj.putDict:
        urlContentResponse.itemProperties = item.urlPutObj.putDict["properties"]

      self.urlContentResponse.append(urlContentResponse)
    self.logger.debug("urlContentResponse: %s", varDump(obj=self.urlContentResponse, strTypeMaxLen=5000))


  def process(self):
    self.getBatchFromInput()
    # Check is Real-Time crawling
    if self.batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
      self.logger.debug("Real-Time crawling batch")
      self.getURLContentFromBatch()
      self.deleteURLContent()
    else:
      self.logger.debug("Regular crawling batch")
      self.getURLContent()
    self.saveBatchToFile()
    if self.exitCode != self.rc:
      self.sendURLContent()


  def deleteURLContent(self):
    items = self.batch.items
    urlDeleteRequest = []
    num_of_items = len(items)
    self.logger.debug("Num of items to delete in batch: <<%s>>" % (num_of_items))
    item_no = 1
    for item in self.items:
      if item is None:
        continue
      siteId = item.siteId
      url = item.urlObj.url
      urlId = item.urlId
      self.logger.debug("Delete item #%s: siteId: <<%s>>, urlId: <<%s>>, url: <<%s>>" % (item_no, siteId, urlId, url))
      urlDeleteRequest.append(dc_event.URLDelete(siteId, url, reason=dc_event.URLDelete.REASON_RT_FINALIZER))
      item_no = item_no + 1
    self.dbTask.dbTaskMode = self.batch.dbMode
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_DELETE, urlDeleteRequest)
    responseDRCESyncTasksCover = self.dbTask.process(drceSyncTasksCoverObj)
    urlDeleteResponse = responseDRCESyncTasksCover.eventObject
    self.logger.debug("urlDeleteResponse: %s", varDump(urlDeleteResponse))
    for status in urlDeleteResponse.statuses:
      if status:
        self.logger.debug(self.MSG_DELETE_URL_OK)
      else:
        self.exitCode = APP_CONSTS.EXIT_FAILURE
        self.logger.debug(self.MSG_ERROR_DELETE_URL)


  # #selectSiteProperty method reads and returns specific siteProperty specified in propName
  #
  # @param batchItem incoming batchItem
  # @param propName name of returned property
  # @return specific siteProperty's value
  def selectSiteProperty(self, batchItem, propName):
    ret = None
    if batchItem.properties is not None and propName in batchItem.properties:
      ret = batchItem.properties[propName]
    elif batchItem.siteObj is not None and batchItem.siteObj.properties is not None:
      for elem in batchItem.siteObj.properties:
        if elem["name"] == propName:
          ret = elem["value"]
          break
    return ret
