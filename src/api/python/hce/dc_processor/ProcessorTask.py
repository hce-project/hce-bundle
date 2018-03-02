# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file ProcessorTask.py
@author Oleksii, bgv <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

try:
  import cPickle as pickle
except ImportError:
  import pickle

import sys
import time
import json
import signal
import hashlib
import re
import copy
import types
import base64
import datetime
import logging.config
import ConfigParser
from subprocess import Popen
from subprocess import PIPE
from collections import namedtuple
from cement.core import foundation
import icu

import app.Consts as APP_CONSTS
import app.Profiler
import app.Utils as Utils
from app.Utils import SQLExpression
from app.Utils import ExceptionLog
from app.Utils import varDump
from app.Filters import Filters
from app.Utils import UrlNormalizator
from app.DateTimeType import DateTimeType
from app.ContentHashCalculator import ContentHashCalculator
from app.Metrics import Metrics
from app.Exceptions import DatabaseException
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
from dc_crawler.DBTasksWrapper import DBTasksWrapper
import dc.Constants as DC_CONSTS
import dc.EventObjects as dc_event
from dc.EventObjects import Site
# from dc.EventObjects import Batch
import dc_processor.Constants as CONSTS
from dc_processor.SourceTemplateExtractor import SourceTemplateExtractor
from dc_processor.scraper_utils import encode
from dc_processor.ScraperInData import ScraperInData
from dc_processor.ProcessorException import ProcessorException
from dc_processor.ScraperLangDetector import ScraperLangDetector


APP_NAME = "processor-task"

DC_URLS_DB_NAME = "dc_urls"
DC_URLS_TABLE_PREFIX = "urls_"
DC_SITES_DB_NAME = "dc_sites"
DC_SITES_TABLE_NAME = "sites"
DC_URLS_TABLE_NAME = "urls"
DC_SITES_PROPERTIES_TABLE_NAME = "sites_properties"

MSG_ERROR_PROCESS_BATCH_ITEM = "Error process batch item "
MSG_ERROR_PROCESS_BATCH = "Error process batch. "
MSG_ERROR_LOAD_CONFIG = "Error loading config file."
MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Error loading logging config file. Exiting."
MSG_ERROR_LOAD_URL_DATA = "Can't load url data: "
MSG_ERROR_LOAD_SITE_DATA = "Error load site data: "
MSG_ERROR_READ_SITE_FROM_DB = "Error read site data from db"
MSG_ERROR_PROCESS_TASK = "Can't process task "
MSG_ERROR_SERIALISE_RESULT = "Error serialize result "
MSG_ERROR_GET_SITE_FILE_DB = "Error get site file db "
MSG_ERROR_UPDATE_RECORD = "Error update record "
MSG_ERROR_UPDATE_PROCESSED_URL = "Error update processed url "
MSG_ERROR_UPDATE_URL_CHARSET = "Error update url charset "
MSG_ERROR_GET_RAW_CONTENT_FROM_DB = "Error get raw content from disk "
MSG_ERROR_PROCESS = "Error process "
MSG_ERROR_LOAD_SITE_PROPERTIES = "Error load site properties "
MSG_ERROR_CHECK_SITE = "Site check is not passed. "
MSG_ERROR_LOAD_OPTIONS = "Error load options. "
MSG_ERROR_CONVERT_RAW_CONTENT_CHARSET = "Cannot convert raw content charset. "
MSG_ERROR_UPDATE_SITE_RESOURCES = "Error update site resources. "
MSG_ERROR_EMPTY_BATCH = "Error read input pickle from stdin."
MSG_ERROR_CHECK_CONTENT_HASH = "Fail to check content hash"
MSG_ERROR_CALC_CONTENT_HASH = "Fail to calc content hash"
MSG_ERROR_CHECK_CONTENT_HASH_DUPLICATE = "Can't check content hash duplicate"

MSG_INFO_PROCESSOR_CMD = "Processor cmd: "
MSG_INFO_LOAD_SITE_PROPERTIES = "Mismatch load site properties "
MSG_INFO_PROCESS_BATCH = "Skipped process batch. "
MSG_INFO_PROCESS_BATCH_ITEM = "Skipped process batch item "
MSG_INFO_PROCESSOR_EXIT_CODE = "Scraper exit_code: "
MSG_INFO_PROCESSOR_OUTPUT = "Scraper output: "
MSG_INFO_PROCESSOR_ERROR = "Scraper err: "

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ERROR_MASK_NO_ERRORS = 0
ERROR_MASK_SITE_OK = 0

URLS_OF_MEDIA_CONTENT = 1
ENV_PROCESSOR_STORE_PATH = "ENV_PROCESSOR_STORE_PATH"

SCRAPER_RESPONSE_ATTR_NAME = 'scraperResponse'
DEFSULT_CHAIN_DELIMITER = ' '

Results = namedtuple("Results", "exit_code, output, err, scraperResponse")
# scraper = None

# #The CrawlerTask class, is a interface for fetching content from the web
#
# This object is a run at once application
class ProcessorTask(foundation.CementApp):


  # Mandatory
  class Meta(object):
    label = APP_NAME
    def __init__(self):
      pass

  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.exit_code = EXIT_SUCCESS
    self.logger = None
    self.template = None
    self.raw_content = None
    self.DBConnector = None
    self.url = None
    self.process_time = None
    self.batchItem = None
    self.site_table = None
    self.raw_data_dir = None
    self.filters = None
    self.processorName = None
    self.batchSites = set()
    self.scraper_response = None
    self.input_batch = None
    self.db_task_ini = None
    self.wrapper = None
    self.htmlRecover = False
    self.objFilters = {}
    self.hashed_content = None
    self.algorithmsModel = APP_CONSTS.APP_USAGE_MODEL_PROCESS
    self.algorithmsModule = None
    self.algorithmsClass = None
    self.accumulatedBatchItems = []
    self.groupResponses = {}
    self.sourceTemplateExtractor = None
    self.accumulateProcessing = False
    self.localTemplate = None
    self.normMask = UrlNormalizator.NORM_NONE
    # for support max execution time
    self.maxExecutionTimeReached = False
    self.maxExecutionTimeValue = 0
    self.removeUnprocessedItems = False
    self.maxTimeCli = None


  # #setup
  # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)


  # #run
  # run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # config section
    self.loadConfig()

    # # load cli arguments
    self.loadAppParams()

    # load scraper
    # self.loadScraper()

    # load logger config file
    self.loadLogConfigFile()

    # load mandatory options
    self.loadOptions()

    # make processing
    self.processBatch()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # # Create multi items unique URL
  #
  # @param url - base url string
  # @param counter - unique numeric value
  # @return unique URL
  def createUniqueMultiItemsUrl(self, url, counter):
    return url + '#' + str(counter)


  # #getPropValueFromSiteProperties reads and returns property value from "site".properties
  #
  # @param batchItemDict - incoming bathitemDict
  # @param propName - property name
  # @return property value of None
  def getPropValueFromSiteProperties(self, batchItemDict, propName):
    ret = None
    if "site" in batchItemDict:
      for prop in batchItemDict["site"].properties:
        if prop["name"] == propName:
          ret = prop["value"]
          break
    return ret


  # #loadSiteProperties
  #
  # @param site - site object
  def loadSiteProperties(self, site, url, batchItem, batchItemDict):
    batchItemDict["template"] = ""
#     self.logger.debug("site.properties: " + str(site.properties))
    try:
      # Update site properties from batch item properties
      keys = [localProperty["name"] for localProperty in site.properties]
#       self.logger.debug("keys: %s" % str(keys))
      for key in batchItem.properties.keys():
        if key in keys:
          for localProperty in site.properties:
            if localProperty["name"] == key:
              self.logger.debug("%s exist in site properties. Rewrite property", key)
#               self.logger.debug("Old value: %s" % varDump(localProperty["value"]))
              localProperty["value"] = batchItem.properties[key]
#               self.logger.debug("New value: %s" % varDump(localProperty["value"]))
        else:
          self.logger.debug("%s don't exist in site properties. Add property", key)
          site.properties.append({"name": key, "value": batchItem.properties[key], "URLMd5": batchItem.urlId})
      # self.logger.debug("Updated site's properties: " + str(site.properties))


      for localProperty in site.properties:
        # self.logger.debug('>>> localProperty ' + str(localProperty["name"]) + ' => ' + str(localProperty["value"]))

        # PROCESS_CTYPES
        if localProperty["name"] == "PROCESS_CTYPES":
          batchItemDict["processCTypes"] = localProperty["value"]
          self.logger.debug("PROCESS_CTYPES: " + str(batchItemDict["processCTypes"]))

        # CONTENT_TYPE_MAP
        elif localProperty["name"] == "CONTENT_TYPE_MAP":
          batchItemDict["contentTypeMap"] = localProperty["value"]
          self.logger.debug("CONTENT_TYPE_MAP: " + str(batchItemDict["contentTypeMap"]))

        # TIMEZONE
        elif localProperty["name"] == "TIMEZONE":
          batchItemDict["timezone"] = localProperty["value"]
          self.logger.debug("TIMEZONE: " + str(batchItemDict["timezone"]))

        # REFINE_TAGS
        elif localProperty["name"] == "TEXT_STATS":
          batchItemDict["textStatus"] = int(localProperty["value"])
          self.logger.debug("TEXT_STATS: " + str(batchItemDict["textStatus"]))

        # TEMPLATE_SOURCE
        elif localProperty["name"] == "TEMPLATE_SOURCE":
          batchItemDict["TEMPLATE_SOURCE"] = localProperty["value"]
          self.logger.debug("TEMPLATE_SOURCE: " + str(batchItemDict["TEMPLATE_SOURCE"]))

        # PROCESSOR_PROPERTIES
        elif localProperty["name"] == "PROCESSOR_PROPERTIES":
          batchItemDict["processorProperties"] = localProperty["value"]
          self.logger.debug("PROCESSOR_PROPERTIES: " + str(batchItemDict["processorProperties"]))

        # CONTENT_HASH
        elif localProperty["name"] == "CONTENT_HASH":
          batchItemDict["contentHash"] = localProperty["value"]
          self.logger.debug("CONTENT_HASH: " + str(batchItemDict["contentHash"]))

        # HTML_RECOVER
        elif localProperty["name"] == "HTML_RECOVER":
          batchItemDict["htmlRecover"] = localProperty["value"]
          self.logger.debug("HTML_RECOVER: " + str(batchItemDict["htmlRecover"]))

        # URL_NORMALIZE_MASK_PROCESSOR
        elif localProperty["name"] == "URL_NORMALIZE_MASK_PROCESSOR":
          batchItemDict["urlNormalizeMaskProcessor"] = localProperty["value"]
          self.logger.debug("URL_NORMALIZE_MASK_PROCESSOR: " + str(batchItemDict["urlNormalizeMaskProcessor"]))

        # template
        elif localProperty["name"] == "template":
          batchItemDict["template"] = localProperty["value"]
          self.logger.debug("Template: " + varDump(batchItemDict["template"]))

        # PROCESSOR_NAME_REPLACE
        elif localProperty["name"] == "PROCESSOR_NAME_REPLACE":
          batchItemDict["PROCESSOR_NAME_REPLACE"] = localProperty["value"]
          self.logger.debug("PROCESSOR_NAME_REPLACE: " + str(batchItemDict["PROCESSOR_NAME_REPLACE"]))

        # PROCESSOR_NAME
        elif localProperty["name"] == "PROCESSOR_NAME":
          batchItemDict["processorName"] = localProperty["value"]
          self.logger.debug("PROCESSOR_NAME: " + str(batchItemDict["processorName"]))

        # HTTP_REDIRECT_LINK
        elif localProperty["name"] == "HTTP_REDIRECT_LINK":
          batchItemDict["HTTP_REDIRECT_LINK"] = localProperty["value"]
          self.logger.debug("HTTP_REDIRECT_LINK: " + str(batchItemDict["HTTP_REDIRECT_LINK"]))


      # debug info
      self.logger.debug("HASH: %s, URL: %s", str(hashlib.md5(app.Utils.UrlParser.generateDomainUrl(url.url)).hexdigest()), url.url)
      if "processorProperties" not in batchItemDict:
        batchItemDict["processorProperties"] = None
      if "processCTypes" in batchItemDict:
        self.logger.debug("PROCESS_CTYPES: " + str(batchItemDict["processCTypes"]))
      if "timezone" in batchItemDict:
        self.logger.debug("TIMEZONE: " + str(batchItemDict["timezone"]))
      else:
        batchItemDict["timezone"] = None
      if "textStatus" in batchItemDict:
        self.logger.debug("TEXT_STATS: " + str(batchItemDict["textStatus"]))

      if "processorName" in batchItemDict:
        self.logger.debug("PROCESSOR_NAME: " + str(batchItemDict["processorName"]))
      else:
        batchItemDict["processorName"] = None

      if "contentHash" in batchItemDict:
        self.logger.debug("CONTENT_HASH: " + str(batchItemDict["contentHash"]))
      else:
        batchItemDict["contentHash"] = None
      if "template" in batchItem.properties and self.accumulateProcessing:
        batchItemDict["template"] = batchItem.properties["template"]
        self.logger.debug(">>> Reproduce template for accumulate batchItem")
      if "template" in batchItemDict:
        batchItemDict["template"] = copy.deepcopy(batchItemDict["template"])
        # self.logger.debug("Template: " + varDump(batchItemDict["template"]))
    except ProcessorException, err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_LOAD_SITE_PROPERTIES)
      raise err
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_LOAD_SITE_PROPERTIES)
      raise err


  # #getProcessorCmd
  #
  def getProcessorCmd(self, processorName):
    if self.algorithmsModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # support PROCESSOR_NAME
      cmd = CONSTS.PYTHON_BINARY + " " + CONSTS.SCRAPER_BINARY + " " + CONSTS.SCRAPER_CFG
      if processorName is None or processorName == CONSTS.PROCESSOR_EMPTY:
        cmd = CONSTS.PYTHON_BINARY + " " + CONSTS.SCRAPER_BINARY + " " + CONSTS.SCRAPER_CFG
      elif processorName == CONSTS.PROCESSOR_STORE:
        cmd = CONSTS.PYTHON_BINARY + " " + CONSTS.STORE_PROCESSOR_BINARY + " " + CONSTS.STORE_PROCESSOR_CFG
      elif processorName == CONSTS.PROCESSOR_FEED_PARSER:
        # Use default scraper for rss_feed site
        cmd = CONSTS.PYTHON_BINARY + " " + CONSTS.PROCESSOR_FEED_PARSER_BINARY + " " + CONSTS.PROCESSOR_FEED_PARSER_CFG
      elif processorName == CONSTS.PROCESSOR_SCRAPER_MULTI_ITEMS:
        cmd = CONSTS.PYTHON_BINARY + " " + CONSTS.SCRAPER_MULTI_ITEMS_BINARY + " " + CONSTS.SCRAPER_MULTI_ITEMS_CFG
      elif processorName == CONSTS.PROCESSOR_SCRAPER_CUSTOM:
        cmd = CONSTS.PYTHON_BINARY + " " + CONSTS.SCRAPER_CUSTOM_BINARY + " " + CONSTS.SCRAPER_CUSTOM_CFG
      self.logger.debug(MSG_INFO_PROCESSOR_CMD + cmd)
    else:
      cmd = {}
      if processorName == CONSTS.PROCESSOR_STORE:
        cmd["AppClass"] = CONSTS.STORE_APP_CLASS_NAME
        cmd["AppConfig"] = CONSTS.STORE_APP_CLASS_CFG
      elif processorName == CONSTS.PROCESSOR_FEED_PARSER:
        cmd["AppClass"] = CONSTS.PROCESSOR_FEED_PARSER_CLASS_NAME
        cmd["AppConfig"] = CONSTS.PROCESSOR_FEED_PARSER_CLASS_CFG
      elif processorName == CONSTS.PROCESSOR_SCRAPER_MULTI_ITEMS:
        cmd["AppClass"] = CONSTS.SCRAPER_MULTI_ITEMS_APP_CLASS_NAME
        cmd["AppConfig"] = CONSTS.SCRAPER_MULTI_ITEMS_APP_CLASS_CFG
      elif processorName == CONSTS.PROCESSOR_SCRAPER_CUSTOM:
        cmd["AppClass"] = CONSTS.SCRAPER_CUSTOM_JSON_APP_CLASS_NAME
        cmd["AppConfig"] = CONSTS.SCRAPER_CUSTOM_JSON_APP_CLASS_CFG
      else:
        cmd["AppClass"] = CONSTS.SCRAPER_APP_CLASS_NAME
        cmd["AppConfig"] = CONSTS.SCRAPER_APP_CLASS_CFG

    return cmd


  # #
  #
  def getProcessedContent(self, template, scraperResponse, errorMask):
    if self.input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER and "response" in template:
      localResponse = self.mapResponseAdditionSubstitutes(template["response"][0], errorMask)
      ret = encode(localResponse)
    else:
      resultDict = {}
      if scraperResponse is not None and scraperResponse.processedContent is not None:
        if "data" in scraperResponse.processedContent["default"].data and \
        "tagList" in scraperResponse.processedContent["default"].data["data"] and \
        len(scraperResponse.processedContent["default"].data["data"]["tagList"]) > 0:
          tagList = scraperResponse.processedContent["default"].data["data"]["tagList"][0]
          # self.logger.debug("!!! tagList: %s, type: %s", varDump(tagList), str(type(tagList)))

          for index, tag in enumerate(tagList):
            # self.logger.debug("!!!tagList[%s]: %s", str(index), varDump(tag))
            if "name" in tag and tag["name"] == "content_encoded" and "data" in tag and \
            "output_format" in template and "name" in template["output_format"] and \
            template["output_format"]["name"] == 'json':
              for elem in tag["data"]:
                tagList[index]["data"] = str(elem)
                # self.logger.debug("!!! elem: %s", varDump(elem))

        scraperResponse.processedContent["default"].get()
        resultDict["default"] = scraperResponse.processedContent["default"].data
        resultDict["internal"] = []
        resultDict["custom"] = []
        buf = []
        for content in scraperResponse.processedContent["internal"]:
          content.get()
          buf.append(content.data)
        resultDict["internal"] = buf
        resultDict["custom"] = scraperResponse.processedContent["custom"]
      ret = encode(json.dumps(resultDict, ensure_ascii=False, encoding='utf-8'))
    return ret


  # # Check allowed site limits ret["site"]
  #
  # @param siteObj - incoming site object instance
  # @param accumulatedBatchItems - accumulated batch items list
  # @return True if allowed site limits or False otherwise
  def isAllowedSiteLimits(self, siteObj, accumulatedBatchItems):

    self.logger.debug("!!! siteObj.maxURLs = " + str(siteObj.maxURLs))
    self.logger.debug("!!! siteObj.maxResources = " + str(siteObj.maxResources))
    self.logger.debug("!!! siteObj.maxErrors = " + str(siteObj.maxErrors))
    self.logger.debug("!!! siteObj.maxResourceSize = " + str(siteObj.maxResourceSize))

    if siteObj.maxURLs > 0 and siteObj.maxURLs < len(accumulatedBatchItems):
      accumulatedBatchItems[-1].urlObj.errorMask |= APP_CONSTS.ERROR_MAX_ITEMS
      self.logger.debug("Max URLs is reached! Urls count= %s. Site maxURLs: %s ", len(accumulatedBatchItems),
                        siteObj.maxURLs)
      return False

    if siteObj.maxResources > 0 and siteObj.maxResources < len(accumulatedBatchItems):
      accumulatedBatchItems[-1].urlObj.errorMask |= APP_CONSTS.ERROR_MASK_SITE_MAX_RESOURCES_SIZE
      self.logger.debug("Max resources size is reached! resources count= %s. Site maxResources: %s ",
                        len(accumulatedBatchItems), siteObj.maxResources)
      return False

    errors = 0
    for batchItem in accumulatedBatchItems:
      self.logger.debug("!!! batchItem.urlObj.errorMask = " + str(batchItem.urlObj.errorMask))
      if batchItem.urlObj.errorMask != APP_CONSTS.ERROR_OK:
        errors += 1

      if 'data' in batchItem.urlObj.urlPut.putDict:
        resourcesSize = len(batchItem.urlObj.urlPut.putDict['data'])
        self.logger.debug("Resource size = " + str(resourcesSize))

        if siteObj.maxResourceSize > 0 and siteObj.maxResourceSize <= resourcesSize:
          accumulatedBatchItems[-1].urlObj.errorMask |= APP_CONSTS.ERROR_RESPONSE_SIZE_ERROR
          self.logger.debug("Max resource size is reached! resource size = %s. Site maxResourceSize: %s ",
                            resourcesSize, siteObj.maxResourceSize)
          return False


    if siteObj.maxErrors > 0 and siteObj.maxErrors <= errors:
      accumulatedBatchItems[-1].urlObj.errorMask |= APP_CONSTS.ERROR_SITE_MAX_ERRORS
      self.logger.debug("Max errors is reached! Errors count= %s. Site maxErrors: %s ",
                        errors, siteObj.maxErrors)
      return False

    return True


  # # read scraper response from output data
  #
  # @param batchItem - batch item structure for clone
  # @param scraperOutputData - output data from scraper module
  # @param siteObj - incoming site object
  # @return scraperResponse, accumulatedBatchItems - filled scraperResponse structure and accumulated BatchItems list
  def readScraperOutputData(self, batchItem, scraperOutputData, siteObj):
    # variables for result
    scraperResponse = None
    accumulatedBatchItems = []

    if isinstance(scraperOutputData, list):
      if len(scraperOutputData) > 0:
        scraperResponse = scraperOutputData[0]
      else:
        pass

      if len(scraperOutputData) > 1:
        for scraperOutputItem in scraperOutputData[1:]:

          localBatchItem = copy.deepcopy(batchItem)
          localBatchItem.urlContentResponse = dc_event.URLContentResponse(None, None, [scraperOutputItem])

          localBatchItem.urlObj.url = self.createUniqueMultiItemsUrl(localBatchItem.urlObj.url, \
                                                                     len(accumulatedBatchItems) + 1)

          localBatchItem.urlObj.urlMd5 = hashlib.md5(localBatchItem.urlObj.url).hexdigest()

          localBatchItem.urlObj.parentMd5 = batchItem.urlObj.urlMd5
          localBatchItem.urlObj.status = dc_event.URL.STATUS_PROCESSED
          localBatchItem.urlObj.crawled = 1
          localBatchItem.urlObj.processed += 1
          localBatchItem.urlObj.type = dc_event.URL.TYPE_SINGLE
          localBatchItem.urlObj.errorMask = scraperOutputItem.errorMask
          localBatchItem.urlObj.CDate = localBatchItem.urlObj.UDate = localBatchItem.urlObj.tcDate = \
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

          localBatchItem.urlId = localBatchItem.urlObj.urlMd5

          self.logger.debug('self.localTemplate: ' + varDump(self.localTemplate))
          self.logger.debug('localBatchItem.properties["template"]: ' + varDump(localBatchItem.properties["template"]))

          if self.localTemplate is not None and localBatchItem.properties is not None\
          and "template" in localBatchItem.properties and "templates" in localBatchItem.properties["template"]:
            localBatchItem.properties["template"] = {}
            localBatchItem.properties["template"]["templates"] = []
            localBatchItem.properties["template"]["templates"].append(self.localTemplate)
          elif self.localTemplate is not None and "template" in localBatchItem.properties:
            self.logger.debug('localBatchItem.properties["template"]: ' + \
                              varDump(localBatchItem.properties["template"]))

          accumulatedBatchItems.append(localBatchItem)
          # Check allowed site limits
          if not self.isAllowedSiteLimits(siteObj, accumulatedBatchItems):
            self.logger.debug("!!! Not allowed site limits. len(accumulatedBatchItems) = " + \
                              str(len(accumulatedBatchItems)))
            break

      self.logger.debug('---> 1 ----')

    else:
      scraperResponse = scraperOutputData
      self.logger.debug('---> 2 ----')

    # self.logger.debug("scraperResponse: %s", varDump(scraperResponse))

    return scraperResponse, accumulatedBatchItems


  # #process main class/module incoming point
  # @param scraperInputObject - instance of scraperInputObject class
  # @param batchItem - incoming batchItem object
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  # @return instance of Results or raises ProcessorException type exception
  def process(self, scraperInputObject, batchItem, batchItemDict):
    try:
      # sleep to reduce system load
      time.sleep(batchItemDict["url"].processingDelay / 1000.0)

      # self.logger.debug('batchItemDict: ' + varDump(batchItemDict))
      self.logger.debug('batchItemDict["processorName"]: ' + varDump(batchItemDict["processorName"]))

      cmd = self.getProcessorCmd(batchItemDict["processorName"])

      self.logger.debug('cmd: ' + varDump(cmd))

      err = ""
      scraperResponse = None
      if self.algorithmsModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        inputPickledObject = pickle.dumps(scraperInputObject)
        Utils.storePickleOnDisk(inputPickledObject, ENV_PROCESSOR_STORE_PATH, "processor.out." + batchItem.urlId)
        self.logger.debug("The process Popen() algorithms usage model")
        self.logger.debug("Popen: %s", str(cmd))
        process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True)
        self.logger.debug("process.communicate(), len(input_pickled_object)=" + str(len(inputPickledObject)))
        (output, err) = process.communicate(input=inputPickledObject)
        self.logger.debug("Process std_error=: %s", str(err))
        self.logger.debug("Process output len=:" + str(len(output)))
        exitCode = process.wait()
        self.logger.debug("Process response exitCode: %s", str(exitCode))
        if exitCode == EXIT_FAILURE:
          self.logger.error("Process has failed!")
          raise ProcessorException("Scraper has failed.")
        # self.scraper_response = pickle.loads(output)
        scraperOutputData = pickle.loads(output)
        self.logger.debug("scraperOutputData: %s", varDump(scraperOutputData))

        scraperResponse, accumulatedBatchItems = self.readScraperOutputData(batchItem, scraperOutputData,
                                                                            batchItemDict["site"])
        self.accumulatedBatchItems += accumulatedBatchItems
      else:
        self.logger.debug("The module import algorithms usage model")
        if self.algorithmsModule is None:
          self.logger.debug("Initialize algorithm module and class instantiate")
          import importlib
          self.logger.debug("importlib.import_module(dc_processor." + cmd["AppClass"] + ")")
          self.algorithmsModule = importlib.import_module("dc_processor." + cmd["AppClass"])
          self.logger.debug("Module dc_processor." + cmd["AppClass"] + " imported")
          # create the app
          try:
            self.algorithmsClass = getattr(self.algorithmsModule, cmd["AppClass"])(APP_CONSTS.APP_USAGE_MODEL_MODULE,
                                                                                   cmd["AppConfig"],
                                                                                   self.logger, scraperInputObject)
            self.algorithmsClass.setup()
          except Exception as err:
            raise ProcessorException("Module initialization failed: " + str(err) + "\n" + Utils.getTracebackInfo())
        else:
          # Use instance from previous call
          self.algorithmsClass.input_data = scraperInputObject
        try:
          self.algorithmsClass.run()
          exitCode = self.algorithmsClass.getExitCode()

          self.logger.debug('type(self.algorithmsClass.output_data): ' + str(type(self.algorithmsClass.output_data)))
          self.logger.debug('self.algorithmsClass.output_data: ' + str(self.algorithmsClass.output_data))

          scraperResponse, accumulatedBatchItems = self.readScraperOutputData(batchItem,
                                                                              self.algorithmsClass.output_data,
                                                                              batchItemDict["site"])
          self.accumulatedBatchItems += accumulatedBatchItems

          output = pickle.dumps(scraperResponse)
        except Exception as err:
          raise ProcessorException("Algorithm module has failed: " + str(err) + "\n" + Utils.getTracebackInfo())

      self.logger.info(MSG_INFO_PROCESSOR_EXIT_CODE + str(exitCode))

      if scraperResponse is not None:
        self.logger.debug("scraper_response: %s", varDump(scraperResponse))

        batchItemDict["errorMask"] |= scraperResponse.errorMask

    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS)
      raise ProcessorException(MSG_ERROR_PROCESS + " : " + str(err) + "\n" + Utils.getTracebackInfo())

    return Results(exitCode, output, err, scraperResponse)


  # #getRawContentFromFS method reads rawContent from FS
  # @param batchItem - incoming batchItem object
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  # @return raw content bufer
  def getRawContentFromFS(self, batchItem, batchItemDict):
    ret = None
    try:
      # Check if Real-Time crawling with ONLY_PROCESSING algorithm
      # if self.input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER and \
      # batchItem.urlObj.urlPut is not None:
      if batchItem.urlObj.urlPut is not None:
        ret = batchItem.urlObj.urlPut.putDict["data"]
        if batchItem.urlObj.urlPut.contentType == dc_event.Content.CONTENT_RAW_CONTENT:
          ret = base64.b64decode(ret)
      else:
        if "htmlRecover" in batchItemDict and batchItemDict["htmlRecover"] is not None and \
        batchItemDict["htmlRecover"] == "1":
          urlContentObj = dc_event.URLContentRequest(batchItem.siteId, batchItem.urlObj.url,
                                                     dc_event.URLContentRequest.CONTENT_TYPE_RAW_LAST + \
                                                     dc_event.URLContentRequest.CONTENT_TYPE_TIDY)
          urlContentObj.urlMd5 = batchItem.urlObj.urlMd5
          ret = self.wrapper.urlContent([urlContentObj])
          if len(ret[0].rawContents) > 0:
            self.logger.debug(">>> YES tidy on disk")
          else:
            self.logger.debug(">>> NO tidy on disk")
        else:
          urlContentObj = dc_event.URLContentRequest(batchItem.siteId, batchItem.urlObj.url,
                                                     dc_event.URLContentRequest.CONTENT_TYPE_RAW_LAST + \
                                                     dc_event.URLContentRequest.CONTENT_TYPE_RAW)
          urlContentObj.urlMd5 = batchItem.urlObj.urlMd5
          ret = self.wrapper.urlContent([urlContentObj])
        # Decode buffer
        if ret is not None and len(ret) > 0 and ret[0].rawContents is not None and len(ret[0].rawContents) > 0:
          putDict = {}
          putDict["id"] = batchItem.urlId
          putDict["data"] = ret[0].rawContents[0].buffer
          putDict["cDate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          batchItem.urlObj.urlPut = dc_event.URLPut(batchItem.siteId, batchItem.urlId,
                                                    dc_event.Content.CONTENT_RAW_CONTENT, putDict)
          ret = base64.b64decode(ret[0].rawContents[0].buffer)
          self.logger.debug("Some raw content size %s on disk", str(len(ret)))
        else:
          ret = None
          self.logger.debug("NO raw content on disk, raw_content: %s", str(ret))

    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_GET_RAW_CONTENT_FROM_DB, (err))
      batchItemDict["errorMask"] |= APP_CONSTS.ERROR_MASK_MISSED_RAW_CONTENT_ON_DISK
      raise ProcessorException(MSG_ERROR_GET_RAW_CONTENT_FROM_DB)
    return ret


  # #convertRawContentCharset method decode raw content bufer to the specified encoding
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  def convertRawContentCharset(self, batchItemDict):
    try:
      # self.logger.info("self.raw_content: %s" % str(self.raw_content))
      if 'charset' in batchItemDict:
        self.logger.debug("Charset incoming is: %s", batchItemDict["charset"])
      else:
        self.logger.debug("Charset not defined in batchItemDict!")
        batchItemDict["charset"] = icu.CharsetDetector(batchItemDict["rawContent"]).detect().getName() # pylint: disable=E1101
        self.logger.debug("Charset detected with icu is: %s", batchItemDict["charset"])
      if batchItemDict["charset"] != 'utf-8':
        self.logger.debug("Content charset decode ignore errors, incoming len: %s",
                          str(len(batchItemDict["rawContent"])))
        batchItemDict["rawContent"] = batchItemDict["rawContent"].decode('utf-8', 'ignore')
        self.logger.debug("Content after decoding len: %s", str(len(batchItemDict["rawContent"])))
    except Exception, err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_CONVERT_RAW_CONTENT_CHARSET, (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      batchItemDict["errorMask"] |= APP_CONSTS. ERROR_BAD_ENCODING
      # Crawler must set content encoding as UTF-8 or it is not changed if natural is
      batchItemDict["charset"] = 'utf-8'


  # #updateURLCharset method updates charset field in the storage of URL object
  # @param batchItem - incoming batchItem object
  # @param charset - incoming charset value
  def updateURLCharset(self, batchItem, charset):
    try:
      urlUpdateObj = dc_event.URLUpdate(batchItem.siteId, batchItem.urlId, dc_event.URLStatus.URL_TYPE_MD5, \
                                        normalizeMask=self.normMask)
      # urlUpdateObj.UDate = SQLExpression("NOW()")
      urlUpdateObj.charset = charset
      self.wrapper.urlUpdate(urlUpdateObj)
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_UPDATE_URL_CHARSET)
      raise err


  # readFilters read pattern from sites_filters
  # @param site - instance of site class
  def readFilters(self, site):
    self.filters = site.filters
    self.logger.debug("sites_filters: " + varDump(self.filters))


  # #updateProcessedURL method updates processed URL in the URL storage
  # @param batchItem - incoming batchItem object
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  def updateProcessedURL(self, batchItem, batchItemDict):
    # check url state
    state = dc_event.URL.STATE_ENABLED
    processedTime = int((time.time() - batchItemDict["processedTime"]) * 1000)
    if "contentURLMd5" not in batchItemDict:
      batchItemDict["contentURLMd5"] = ""

    if "scraperResponse" in batchItemDict and batchItemDict["scraperResponse"] is not None and \
    len(batchItemDict["scraperResponse"]) > 0 and batchItemDict["scraperResponse"][0] is not None:
      tagsMask = batchItemDict["scraperResponse"][0].tagsMask or 0
      tagsCount = batchItemDict["scraperResponse"][0].tagsCount or 0
      pubdate = batchItemDict["scraperResponse"][0].pubdate or None
      # Validate pubdate value from scraper response and return as None if value is incorrect
      self.logger.debug('pubdate from scraper response: ' + str(pubdate))
      if pubdate is not None and isinstance(pubdate, basestring):
        pubdate = DateTimeType.parse(pubdate)
        if pubdate is not None:
          pubdate = pubdate.strftime("%Y-%m-%d %H:%M:%S")
    else:
      tagsMask = 0
      tagsCount = 0
      pubdate = None

    self.logger.debug('>>> updateProcessedURL  pubdate = ' + str(pubdate) + ' type: ' + str(type(pubdate)))

    try:
      urlUpdateList = []
      batchItem.urlObj.status = dc_event.URL.STATUS_PROCESSED
      batchItem.urlObj.state = state
      batchItem.urlObj.errorMask = batchItemDict["errorMask"]
      batchItem.urlObj.tagsMask = tagsMask
      batchItem.urlObj.tagsCount = tagsCount
      batchItem.urlObj.totalTime += processedTime
      batchItem.urlObj.processingTime = processedTime
      batchItem.urlObj.pDate = pubdate
      batchItem.urlObj.UDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      batchItem.urlObj.tcDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      batchItem.urlObj.contentURLMd5 = batchItemDict["contentURLMd5"]
      batchItem.urlObj.processed += 1

      urlUpdateObj = dc_event.URLUpdate(batchItem.siteId, batchItem.urlId, dc_event.URLStatus.URL_TYPE_MD5, \
                                        normalizeMask=self.normMask)
      urlUpdateObj.status = batchItem.urlObj.status
      urlUpdateObj.state = batchItem.urlObj.state
      urlUpdateObj.errorMask = SQLExpression("`ErrorMask` + %s" % str(batchItem.urlObj.errorMask))
      urlUpdateObj.tagsMask = batchItem.urlObj.tagsMask
      urlUpdateObj.tagsCount = batchItem.urlObj.tagsCount
      urlUpdateObj.totalTime = SQLExpression(("`TotalTime` + %s" % str(batchItem.urlObj.processingTime)))
      urlUpdateObj.processingTime = batchItem.urlObj.processingTime
      urlUpdateObj.pDate = batchItem.urlObj.pDate
      urlUpdateObj.UDate = SQLExpression("NOW()")
      urlUpdateObj.tcDate = SQLExpression("NOW()")
      urlUpdateObj.contentURLMd5 = batchItem.urlObj.contentURLMd5
      urlUpdateObj.processed = SQLExpression("`Processed`+1")
      urlUpdateObj.crawled = batchItem.urlObj.crawled

      urlUpdateList.append(urlUpdateObj)
      self.logger.debug('>>>> urlUpdateList: ' + varDump(urlUpdateList))

      if ("processorName" in batchItemDict) and (batchItemDict["processorName"] == CONSTS.PROCESSOR_FEED_PARSER) and \
      (dc_event.BatchItem.PROP_FEED in batchItem.properties):
        for url, value in batchItem.properties[dc_event.BatchItem.PROP_FEED].items():
          del url
          urlUpdateObjLocal = copy.deepcopy(urlUpdateObj)
          urlUpdateObjLocal.urlMd5 = value["urlMd5"]
          urlUpdateObjLocal.errorMask = batchItemDict["errorMask"]
          urlUpdateList.append(urlUpdateObjLocal)

      # Evaluate 'URL' class values use sql expression if neccessary
      changedFieldsDict = FieldsSQLExpressionEvaluator.execute(batchItem.properties, self.wrapper, None,
                                                               batchItem.urlObj, self.logger,
                                                               APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR)
      # Update URL values
      if isinstance(changedFieldsDict, dict):
        for name, value in changedFieldsDict.items():
          if hasattr(urlUpdateObj, name):
            setattr(urlUpdateObj, name, value)

        result = self.wrapper.urlUpdate(urlUpdateList)
        del result
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_UPDATE_PROCESSED_URL)
      raise err


  # #processContentHash method calculates content hash for content from incoming batchItemDict dict
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  # @return just calculated content hash value
  def processContentHash(self, batchItemDict):
    ret = None
    try:
      if "contentHash" in batchItemDict and batchItemDict["contentHash"] is not None \
      and "scraperResponse" in batchItemDict and len(batchItemDict["scraperResponse"]) > 0:
        self.logger.debug(">>> Site has content hash rule: %s", str(batchItemDict["contentHash"]))
        localContentHash = json.loads(batchItemDict["contentHash"])
        # self.list_hashed_tags = self.contentHash["tags"].split(",")
        listHashedTags = localContentHash["tags"].split(",")
        batchItemDict["contentURLMd5Algorithm"] = localContentHash["algorithm"]
        self.logger.debug(">>> List hashed tags: %s", str(listHashedTags))
        localBuf = self.stickHashedContents(listHashedTags, batchItemDict["scraperResponse"][0])
        ret = ContentHashCalculator.hashCalculate(localBuf, int(batchItemDict["contentURLMd5Algorithm"]))
      else:
        self.logger.debug(">>> Site hasn't content hash rule")
    except ProcessorException as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_CALC_CONTENT_HASH, (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    return ret


  # #stickHashedContents method sticks hash calculated contents together
  # @param listHashedTags - incoming list of tag's names for hash calculated contents
  # @param scraperResponse - instance of scraperResponse with processed contents
  # @return just sticked content
  def stickHashedContents(self, listHashedTags, scraperResponse):
    ret = ""
    tagsList = []
    if len(scraperResponse.processedContent["default"].data["data"]["tagList"]) > 0:
      tagsList = scraperResponse.processedContent["default"].data["data"]["tagList"][0]
      for tag in tagsList:
        if tag["name"] in listHashedTags:
          self.logger.debug(">>> Tag name added to hash: %s", str(tag["name"]))
          # self.logger.debug(">>> Tag value added to hash: %s", str(tag["data"]))
          if isinstance(tag["data"], basestring):
            ret += tag["data"]
            ret += ' '
          elif isinstance(tag["data"], list):
            for elem in tag["data"]:
              ret += str(elem)
              ret += ' '
        else:
          self.logger.debug(">>> Tag: %s not added to hash", tag["name"])
    return ret


  # #extendProcessorProperties method extends processorProperties by some site.properties
  # @param batchItem - incoming batchItem object
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  def extendProcessorProperties(self, batchItemDict, siteProperties):
    if "processorProperties" in batchItemDict:
      try:
        localJson = json.loads(batchItemDict["processorProperties"])
        for elem in siteProperties:
          if elem["name"] == "HTTP_HEADERS" and "EXTRACTOR_USER_AGENT" not in localJson:
            try:
              localHeaders = json.loads(elem["value"])
              for key in localHeaders:
                if key.lower() == "useragent":
                  localJson["EXTRACTOR_USER_AGENT"] = localHeaders[key]
                  break
            except Exception:
              self.logger.debug(">>> Bad json value in the siteProperties[\"HTTP_HEADERS\"]")
          elif elem["name"] == "SCRAPER_METRICS" and "metrics" not in localJson:
            localJson["metrics"] = elem["value"]
          elif elem["name"] == "SCRAPER_SCRAPY_PRECONFIGURED" and "SCRAPER_SCRAPY_PRECONFIGURED" not in localJson:
            localJson["SCRAPER_SCRAPY_PRECONFIGURED"] = elem["value"]
        if "url" in batchItemDict and batchItemDict["url"] is not None and "parentMd5" not in localJson:
          localJson["parentMd5"] = batchItemDict["url"].parentMd5
        batchItemDict["processorProperties"] = json.dumps(localJson)
      except Exception as err:
        self.logger.debug(">>> Something wrong with processorProperties = " + str(err))


  # #extendTemplateFromSource method extends template list property by templates from external sources
  # @param templateSource - incoming external templateSource
  # @param template - incoming template structure from properties
  # @return sticked template list
  def extendTemplateFromSource(self, batchItemDict):
    ret = batchItemDict["template"]
    additionData = {}
    additionData["parentMD5"] = batchItemDict["url"].parentMd5
    self.sourceTemplateExtractor = SourceTemplateExtractor()
    additionTemplate = self.sourceTemplateExtractor.loadTemplateFromSource(batchItemDict["TEMPLATE_SOURCE"],
                                                                           None, batchItemDict["rawContent"],
                                                                           batchItemDict["url"].url)
    if "templates" in ret:
      for additionTemplateElem in additionTemplate:
        for templateElem in ret["templates"]:
          if hasattr(additionTemplateElem, "name") and hasattr(templateElem, "name") and \
          additionTemplateElem.name == templateElem.name:
            templateElem = copy.deepcopy(additionTemplateElem)
            additionTemplateElem = None
            break
        if additionTemplateElem is not None:
          ret["templates"].append(additionTemplateElem)
    return ret


  # #parseTemplate method parses json string with templates, converted (if needed) to new format and calls
  # templateSource extended method
  # @param batchItem - incoming batchItem object
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  def parseTemplate(self, batchItem, batchItemDict):
    # Parse templates
    # self.logger.debug("template: %s" % varDump(batchItemDict["template"]))
    # self.logger.debug("type of template is = " + str(type(batchItemDict["template"])))
    if isinstance(batchItemDict["template"], basestring) and batchItemDict["template"] != "":
      batchItemDict["template"] = json.loads(batchItemDict["template"])
    if "templates" in batchItemDict["template"]:
      # If new template format do nothing
      self.logger.debug("NEW template format")
      if "template" not in batchItem.properties:
        batchItem.properties["template"] = copy.deepcopy(batchItemDict["template"])
    else:
      # Conver old template format to new one
      self.logger.debug("OLD template format")
      self.convertTemplateFormat(batchItem, batchItemDict)
    if not self.accumulateProcessing:
      if "TEMPLATE_SOURCE" in batchItemDict:
        batchItemDict["template"] = self.extendTemplateFromSource(batchItemDict)
    batchItemDict["template"] = self.removeTemplateElementsByCondition(batchItemDict["template"], batchItemDict)


  # #removeTemplateElementsByCondition method looks templates conditions (if they are present) and remove that
  # not matches
  # @param template - incoming template structure from properties
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  def removeTemplateElementsByCondition(self, template, batchItemDict):
    ret = template
    if "templates" in ret:
      newTemplateList = []
      for templateElement in ret["templates"]:
        isAdded = True
        if "condition" in templateElement:
          isAdded = False
          if templateElement["condition"]["type"] == CONSTS.TEMPLATE_CONDITION_TYPE_URL:
            if "url" in batchItemDict:
              compareObj = batchItemDict["url"]
              if hasattr(compareObj, templateElement["condition"]["field"]):
                fieldValue = getattr(compareObj, templateElement["condition"]["field"], None)
                if fieldValue is not None:
                  try:
                    if re.compile(templateElement["condition"]["pattern"]).match(str(fieldValue)) is not None:
                      isAdded = True
                  except Exception as excp:
                    self.logger.debug(">>> Some wrong with RE. in ret condition; err = " + str(excp))
        if isAdded:
          newTemplateList.append(templateElement)
      ret["templates"] = newTemplateList
    return ret


  # #convertTemplateFormat method converts tempalte from old format ot new format
  # not matches
  # @param batchItem - incoming batchItem object
  # @param batchItemDict - incoming batchItemDict dict, dict of batchItem's properties
  def convertTemplateFormat(self, batchItem, batchItemDict):
    self.logger.debug("Template before convertion: %s", varDump(batchItemDict["template"]))
    template = copy.copy(batchItemDict["template"])
    batchItemDict["template"] = {"templates":[{"priority":100, "mandatory":1, "is_filled":0, "tags":template}]}
    batchItem.properties["template"] = batchItemDict["template"]
    self.logger.debug("Template after convertion: %s", varDump(batchItemDict["template"]))


  # # mapResponseProcessedContent
  #
  def mapResponseProcessedContent(self, template, processedContent, removeTrailingComma, entry, processorProperties):
    if len(template["tags"]) == 0:
      entries = []
      for data in processedContent.data["data"]["tagList"][0]:
        ei = re.sub("%tag_name%_%extractor_value%", "%" + data["name"] + "_extractor%", entry)
        ei = re.sub("%tag_value%", "%" + data["name"] + "%", ei)
        ei = re.sub("%tag_name%", data["name"], ei)

        if ei != "":
          entries.append(ei)

      if len(entries) > 0:
        if template["output_format"]["name"] == "json":
          itemDelimiter = ","
        else:
          itemDelimiter = " "

        # # make unique
        entries = list(set(entries))
        entry = itemDelimiter.join(entries)
        if removeTrailingComma and len(entry) > 0 and entry.endswith(","):
          entry = entry[:-1]
      else:
        entry = ""

    langTagsNames = []
    properties = {}
    try:
      properties = json.loads(processorProperties)
    except Exception, err:
      self.logger.error(str(err))

    if CONSTS.LANG_PROP_NAME in properties:
      langDetector = ScraperLangDetector(properties[CONSTS.LANG_PROP_NAME])
      langTagsNames = langDetector.getLangTagsNames()
      # self.logger.debug("langTagsNames: %s", str(langTagsNames))

    if entry != "":
      # self.logger.debug("Output processedContent.data.tagList: %s", varDump(processedContent.data["data"]["tagList"]))
      for data in processedContent.data["data"]["tagList"][0]:
        # self.logger.debug("Output processedContent.data: %s" % varDump(data))
        pattern = "%" + data["name"] + "%"
        # pattern = pattern.replace("\\", "\\\\")
        if entry.find(pattern) != -1:
          for item in data["data"]:
            if item is None or item == "":
              continue
            entry = entry.replace(pattern, item)

          if "extractor" in data and "name" in data:
            entry = entry.replace("%" + data["name"] + "_extractor" + "%", str(data["extractor"]))

          if "xpath" in data and "name" in data and data["data"] and len(data["data"]) > 0:
            xpathData = str(data["xpath"])
            if template["output_format"]["name"] == "json":
              # self.logger.debug('>>> ' + str(data["name"]) + ' xpathData: ' + str(xpathData))
              xpathData = json.dumps(xpathData, encoding='utf-8').strip('"')
#               xpathData = json.dumps(xpathData).strip('"')
              # self.logger.debug('>>> ' + str(data["name"]) + ' xpathData: ' + str(xpathData))
            entry = entry.replace("%" + data["name"] + "_xpath" + "%", xpathData)
          elif "xpath" in data and "name" in data:
            entry = entry.replace("%" + data["name"] + "_xpath" + "%", "%" + data["name"] + "_xpath" + "%")

          if "lang" in data and "lang_suffix" in data and "name" in data:
            entry = entry.replace("%" + data["name"] + data["lang_suffix"] + "%", str(data["lang"]))

          if "summary_lang" in data and "lang_suffix" in data:
            entry = entry.replace("%" + data["lang_suffix"] + "%", str(data["summary_lang"]))

          for langTagName in langTagsNames:
            if "lang" in data and "name" in data and data["name"] in langTagName:
              if "%" + langTagName + "%" in entry:
                entry = entry.replace("%" + langTagName + "%", str(data["lang"]))
              else:
                entry = self.addAdditionalValue(entry, str(langTagName), str(data["lang"]))

      if "time" in processedContent.data:
        entry = entry.replace("%scraper_time%", str(processedContent.data["time"]))
    else:
      entry = json.dumps({"default":processedContent.data}, ensure_ascii=False) # , encoding='utf-8')

    localMetrics = json.dumps(processedContent.metrics)
    if len(localMetrics) > 0 and localMetrics[0] == '"' or localMetrics[0] == '\'':
      localMetrics = localMetrics[1:]
    if len(localMetrics) > 0 and localMetrics[-1] == '"' or localMetrics[-1] == '\'':
      localMetrics = localMetrics[0:-1]
    entry = entry.replace("%metrics%", localMetrics)

    return entry


  # # mapResponse
  #
  def mapResponse(self, template, crawlingTime, scraperResponse, processorProperties):
    # I. TODO reduce phase
    # self.logger.debug("Output format: %s" % varDump(template["output_format"]))
    localProcessedContents = []
    if scraperResponse is not None:
      localProcessedContents.append(scraperResponse.processedContent["default"])
      localProcessedContents.extend(scraperResponse.processedContent["internal"])
    template["response"] = []

    # II. Fill header
    localResponse = template["output_format"]["header"]

    # III. Fill item
    localResponse = localResponse + template["output_format"]["items_header"]

    entry = template["output_format"]["item"]
    removeTrailingComma = entry.endswith(",")
    i = 0
    for localProcessedContent in localProcessedContents:
      internalEntry = copy.deepcopy(entry)
      internalLocalResponse = copy.deepcopy(localResponse)
      if localProcessedContent is not None:
        internalEntry = self.mapResponseProcessedContent(template, localProcessedContent, removeTrailingComma,
                                                         internalEntry, processorProperties)

      internalEntry = internalEntry.replace("%crawler_time%", str(crawlingTime / 1000.0))
      if removeTrailingComma and len(internalEntry) > 0 and internalEntry.endswith(","):
        internalEntry = internalEntry[:-1]

      entry = self.mapResponseAdditionSubstitutes(entry, scraperResponse.errorMask)
      internalLocalResponse = internalLocalResponse + internalEntry + template["output_format"]["items_footer"]
      # IV. Fill footer
      internalLocalResponse = internalLocalResponse + template["output_format"]["footer"]

      template["response"].append(internalLocalResponse)
      if i > 0:
        scraperResponse.processedContent["custom"].append(internalLocalResponse)
      i += 1

    if len(localProcessedContents) == 0:
      entry = entry.replace("%crawler_time%", str(crawlingTime / 1000.0))
      if removeTrailingComma and len(entry) > 0 and entry.endswith(","):
        entry = entry[:-1]

      if scraperResponse is not None:
        entry = self.mapResponseAdditionSubstitutes(entry, scraperResponse.errorMask)
      localResponse = localResponse + entry + template["output_format"]["items_footer"]
      # IV. Fill footer
      localResponse = localResponse + template["output_format"]["footer"]
      template["response"].append(localResponse)

#     self.logger.debug("Output response: %s" % varDump(template["response"]))


  # # mapResponseAdditionSubstitutes
  #
  def mapResponseAdditionSubstitutes(self, buf, errorMask):
    ret = buf
    substituteDict = {"%errors_mask%": str(errorMask)}
    for key in substituteDict:
      ret = re.sub(key, substituteDict[key], ret)

    return ret


  # # addAdditionalValue
  #
  # @param buf - string buffer
  # @name - name as string
  # @value - value as string
  # @return modified buffer
  def addAdditionalValue(self, buf, name, value):
    # variable for result
    ret = buf
    try:
      fieldsDict = json.loads(buf)
      
      if isinstance(fieldsDict, dict):
        fieldsDict[name] = value

      ret = json.dumps(fieldsDict) # , encoding='utf-8')

    except Exception, err:
      self.logger.error(str(err))
      self.logger.info(Utils.getTracebackInfo())

    return ret


  # # reduceResponse
  #
  def reduceResponse(self, processingTamplatesDict, templateSelectType, batchItemDict):
    maxVal = -1
    ret = None
    templeteElem = None
    for elem in processingTamplatesDict:
      templeteElem = elem[0]
      if "mandatory" in templeteElem and templeteElem["mandatory"] == 1 and "isEmpty" in templeteElem and \
      templeteElem["isEmpty"]:
        batchItemDict["errorMask"] |= APP_CONSTS.ERROR_MANDATORY_TEMPLATE
        ret = elem
        break
      if "contentsCount" in templeteElem and "contentsLen" in templeteElem:
        if templateSelectType == "first_nonempty":
          if templeteElem["contentsCount"] > maxVal:
            maxVal = templeteElem["contentsCount"]
            ret = elem
        elif templeteElem["contentsLen"] > maxVal:
          maxVal = templeteElem["contentsLen"]
          ret = elem
      else:
        ret = elem
    if ret is not None:
      batchItemDict["template"] = ret[0]
      batchItemDict["scraperResponse"] = []
      batchItemDict["scraperResponse"].append(ret[1])


  # #processTask
  #
  def processTask(self, batchItem, batchItemDict, withoutProcess=False):
    try:
      # If the processing algorithm is "raw-data" (bgv)
      if batchItemDict["processorProperties"] is not None:
        processorProperties = json.loads(batchItemDict["processorProperties"])
        if "algorithm" in processorProperties:
          algorithm = processorProperties["algorithm"]
          if "algorithm_name" in algorithm and algorithm["algorithm_name"] == "raw-data":
            self.logger.debug("raw-data algorithm defined!")
            batchItemDict["processedContent"] = encode(batchItemDict["rawContent"])
            self.putContent(batchItem, batchItemDict["processedContent"], batchItemDict)
            return
        self.extendProcessorProperties(batchItemDict, batchItemDict["site"].properties)
      # self.logger.debug("processorProperties = " + str(batchItemDict["processorProperties"]))
      if "charset" in batchItemDict:
        self.updateURLCharset(batchItem, batchItemDict["charset"])
      if "site" in batchItemDict:
        self.readFilters(batchItemDict["site"])

      # self.logger.debug("batchItemDict[\"template\"]) before: " + varDump(batchItemDict["template"]))
      # Parse templates
      # self.parseTemplate(batchItem, batchItemDict)

      # self.logger.debug("batchItemDict[\"template\"]) after: " + varDump(batchItemDict["template"]))

      # Step I: reorder templates order by priority
      # self.logger.debug("Template order before: %s" % varDump(self.template))
      checkPriority = True
      for elem in batchItemDict["template"]["templates"]:
        if "priority" not in elem:
          checkPriority = False
          break
      if checkPriority:
        batchItemDict["template"]["templates"] = sorted(batchItemDict["template"]["templates"],
                                                        key=lambda template: template["priority"], reverse=True)
      # self.logger.debug("Template order after: %s" % varDump(self.template))

      # Step II: process each template
      # processingTemplatesDict = []
      # templateSelectType = self.template["select"] if "select" in self.template else "first_nonempty"
      if "scraperResponse" not in batchItemDict:
        if batchItem.urlContentResponse is not None and batchItem.urlContentResponse.processedContents is not None:
          batchItemDict["scraperResponse"] = batchItem.urlContentResponse.processedContents
        else:
          batchItemDict["scraperResponse"] = []

          for self.localTemplate in batchItemDict["template"]["templates"]:
            # self.logger.debug(">>> Processing template %s" % varDump(self.localTemplate))
            if "state" in self.localTemplate and not bool(int(self.localTemplate["state"])):
              self.logger.debug(">>> Template disable")
              batchItemDict["scraperResponse"].append(None)
              continue
            # Anything can happen but
            # we don't bother what happeh - just go further
            if not withoutProcess:
              try:
                scraperInputObject = ScraperInData(batchItemDict["url"].url, batchItem.urlId, batchItem.siteId,
                                                   batchItemDict["rawContent"], self.localTemplate["tags"],
                                                   self.filters, batchItemDict["url"].lastModified,
                                                   batchItemDict["timezone"], self.input_batch.id,
                                                   self.input_batch.dbMode, batchItem,
                                                   batchItemDict["processorProperties"],
                                                   self.localTemplate["output_format"] if "output_format" in \
                                                   self.localTemplate else None)
                result = self.process(scraperInputObject, batchItem, batchItemDict)
                batchItemDict["scraperResponse"].append(result.scraperResponse)
              except Exception() as err:
                self.logger.error("Some error in template processing : " + str(err))
                batchItemDict["scraperResponse"].append(None)
          self.localTemplate = None
      else:
        self.logger.debug("'scraperResponse' found in batchItemDict!!!")
    except ProcessorException as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS_TASK)
      batchItemDict["errorMask"] |= APP_CONSTS.ERROR_MASK_SCRAPER_ERROR
      raise err
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS_TASK, (err))
      batchItemDict["errorMask"] |= APP_CONSTS.ERROR_MASK_SCRAPER_ERROR


  # # Put content to DB
  #
  def putContent(self, batchItem, processedContent, batchItemDict):

    # add to batchItem processed content for result output batch
    batchItem.urlContentResponse = dc_event.URLContentResponse(None, processedContents=[processedContent])

    # URLPut
    # Create new URLPut object
    putDict = {}
    putDict["id"] = batchItem.urlId
    putDict["data"] = processedContent
    putDict["cDate"] = SQLExpression("NOW()")  # # datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    urlPut = dc_event.URLPut(batchItem.siteId, batchItem.urlId, dc_event.Content.CONTENT_PROCESSOR_CONTENT, putDict)
    # Check if Real-Time crawling
    if self.input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER and \
    (self.input_batch.dbMode & dc_event.Batch.DB_MODE_W == 0) and batchItem.urlPutObj is None:

      if "TEMPLATE_SOURCE" in batchItemDict or self.accumulateProcessing:
        putDict["properties"] = copy.deepcopy(batchItem.properties)
        if "template" in batchItemDict:
          if isinstance(batchItemDict["template"]["templates"], types.DictType):
            putDict["properties"]["template"]["templates"] = [copy.deepcopy(batchItemDict["template"]["templates"])]
          elif isinstance(batchItemDict["template"]["templates"], types.ListType) and \
          len(batchItemDict["template"]["templates"]) > 0:
            putDict["properties"]["template"]["templates"] = [copy.deepcopy(batchItemDict["template"]["templates"][0])]
          if len(putDict["properties"]["template"]["templates"]) > 0:
            putDict["properties"]["template"]["templates"][0]["response"] = []

      batchItem.urlPutObj = urlPut

    else:
      drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_PUT, [urlPut])
      try:
        responseDRCESyncTasksCover = self.wrapper.process(drceSyncTasksCoverObj)
        if responseDRCESyncTasksCover.eventType == DC_CONSTS.EVENT_TYPES.URL_PUT_RESPONSE:
          for obj in responseDRCESyncTasksCover.eventObject:
            self.logger.debug("URL_PUT_RESPONSE: %s", varDump(obj))
        else:
          self.logger.error("URL_PUT_RESPONSE >>> Wrong response type")
      except DatabaseException, err:
        self.logger.error('PutContent error: ' + str(err))
        batchItemDict["errorMask"] |= APP_CONSTS.ERROR_DATABASE_ERROR


  # #updateURL
  #
  def updateURL(self, batchItem, errorMask=None):
    try:
      # updated by Oleksii
      # if insert into kv db wasn't successfully
      # not update Processed counter
      urlUpdateObj = dc_event.URLUpdate(batchItem.siteId, batchItem.urlId, dc_event.URLStatus.URL_TYPE_MD5, \
                                        normalizeMask=self.normMask)
      urlUpdateObj.tcDate = SQLExpression("NOW()")
      urlUpdateObj.status = dc_event.URL.STATUS_PROCESSING
      urlUpdateObj.batchId = self.input_batch.id
      if errorMask is not None:
        urlUpdateObj.errorMask = errorMask
      self.wrapper.urlUpdate(urlUpdateObj)
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_LOAD_SITE_DATA)
      raise err


  # # Check is disabled site
  #
  # @param site - site object
  # @return True - if site is disabled, otherwise False
  def isDisabledSite(self, site):
    return bool(site.state == Site.STATE_DISABLED)


  # # Check max resources limits for site
  #
  # @param site - site object
  # @param url - incoming url object
  # @return True - if max resouces has overlimit, otherwise False
  def isOverlimitMaxResources(self, site, url):
    # variable for result
    ret = False
    # pass checking if it is first processing, but not re-crawling
    if site.maxResources > 0 and site.contents > site.maxResources and url.processed == 0:
      self.logger.debug("Site maxResources number is reached! Site contents is: %s. Site maxResources: %s ",
                        str(site.contents), str(site.maxResources))
      ret = True

    return ret


  # #
  #
  def readSiteFromDB(self, batchItem):
    ret = None
    try:
      # Add support db-task Site
      siteStatus = dc_event.SiteStatus(batchItem.siteId)
      drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.SITE_STATUS, siteStatus)
      responseDRCESyncTasksCover = self.wrapper.process(drceSyncTasksCoverObj)
      site = responseDRCESyncTasksCover.eventObject
      ret = site

      # self.logger.debug('>>> readSiteFromDB  site: ' + varDump(site))
    except DatabaseException, err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_READ_SITE_FROM_DB)
      raise err
    except Exception, err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_READ_SITE_FROM_DB)
      raise err

    return ret


  # #
  #
  def loadSite(self, batchItem):
    ret = None
    try:
      if not len(batchItem.siteId):
        batchItem.siteId = "0"
      site = self.readSiteFromDB(batchItem)
      if site is not None and batchItem.siteObj is not None:
        site.rewriteFields(batchItem.siteObj)
      ret = site
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_LOAD_SITE_DATA)
      raise err

    return ret


  # #
  #
  #
  def loadURL(self, batchItem):
    ret = None
    urlStatus = dc_event.URLStatus(batchItem.siteId, batchItem.urlId)
    urlStatus.urlType = dc_event.URLStatus.URL_TYPE_MD5
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_STATUS, [urlStatus])
    responseDRCESyncTasksCover = self.wrapper.process(drceSyncTasksCoverObj)
    row = responseDRCESyncTasksCover.eventObject
    try:
      if len(row):
        ret = row[0]
      else:  # throw if url doesn't exists
        raise ProcessorException(">>> URLStatus return empty response, urlId=" + batchItem.urlId)
    except Exception, err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_LOAD_URL_DATA, (ret))
      raise err

    self.logger.debug(">>> Url object: " + varDump(ret))

    return ret


  # #extendBatchItemsWithChain method extent primary batchItems list with chin items
  # @param batchItems - incoming batchitems list
  # @return extended batchItems list
  def extendBatchItemsWithChain(self, batchItems):
    ret = []
    chainIndex = 0
    chainIncrement = 0
    for batchItem in batchItems:
      if batchItem.urlObj.chainId is not None and batchItem.urlObj.chainId > chainIndex:
        chainIndex = batchItem.urlObj.chainId + 1
    self.logger.debug(">>> Started chainId is = " + str(chainIndex))
    for batchItem in batchItems:
      chainIncrement = 0
      ret.append(batchItem)
      if batchItem.urlObj.chainId is None:
        urlContent = dc_event.URLContentRequest(batchItem.siteId, batchItem.urlObj.url)
        urlContent.contentTypeMask = dc_event.URLContentRequest.CONTENT_TYPE_CHAIN
        urlContent.contentTypeMask |= dc_event.URLContentRequest.CONTENT_TYPE_RAW_FIRST
        urlContent.urlMd5 = batchItem.urlObj.urlMd5
        drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_CONTENT, [urlContent])
        responseDRCESyncTasksCover = self.wrapper.process(drceSyncTasksCoverObj)
        row = responseDRCESyncTasksCover.eventObject
        if row is not None and len(row) > 0 and len(row[0].rawContents) > 0:
          self.logger.debug(">>> Started chainId , yes chain list")
          chainBuf = row[0].rawContents[0].buffer
          self.logger.debug(">>> buff = " + str(chainBuf))
          try:
            chainBuf = base64.b64decode(chainBuf)
          except Exception:
            self.logger.debug(">>> chain buf exception")
            chainBuf = None
          if chainBuf is not None:
            splitterList = chainBuf.split("\n")
            self.logger.debug(">>> Started chainId , yes chain list len is = " + str(len(splitterList)))
            for i in xrange(0, len(splitterList)):
              urlMd5 = splitterList[i].strip()
              self.logger.debug(">>> extract chain MD5 = " + urlMd5)
              urlObjEvent = dc_event.URLStatus(batchItem.siteId, urlMd5)
              urlObjEvent.urlType = dc_event.URLStatus.URL_TYPE_MD5
              drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_STATUS, [urlObjEvent])
              responseDRCESyncTasksCover = self.wrapper.process(drceSyncTasksCoverObj)
              row = responseDRCESyncTasksCover.eventObject
              if row is not None and len(row) > 0:
                chainIncrement = 1
                batchItem.urlObj.chainId = chainIndex
                newBatchitem = copy.deepcopy(batchItem)
                newBatchitem.urlId = urlMd5
                newBatchitem.urlObj = row[0]
                newBatchitem.urlObj.chainId = chainIndex
                newBatchitem.urlObj.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK
                ret.append(newBatchitem)
                self.logger.debug(">>> added new chain item, urlMd5 = " + str(urlMd5) + " ChainId = " + \
                                  str(newBatchitem.urlObj.chainId))
            chainIndex += chainIncrement
    return ret


  # #templateMetricsCalculate calculates some templates metrics
  # @param template - incoming batch templates
  # @param scraperResponse - incoming scraperResponse
  def templateMetricsCalculate(self, template, scraperResponse):
    template["contentsCount"] = 0
    template["contentsLen"] = 0
    template["isEmpty"] = True
    for data in scraperResponse.processedContent["default"].data["data"]["tagList"][0]:
      saveLen = template["contentsLen"]
      for item in data["data"]:
        if item is not None:
          template["contentsLen"] += len(item)
      if template["contentsLen"] > saveLen:
        template["contentsCount"] += 1
        template["isEmpty"] = False


  # #processBatchItemScrapyStep implements first step of batchitem processing (fetch scraper responce)
  # @param batchItem - incoming bathitem
  # @return bathitemDict with result data
  def processBatchItemScrapyStep(self, batchItem):
    self.logger.debug(">>> 1 step")
    ret = {}
    ret["errorMask"] = batchItem.urlObj.errorMask
    ret["processedTime"] = time.time()
    try:
      self.batchSites.update([batchItem.urlObj.siteId])
      ret["site"] = self.loadSite(batchItem)
      # Check if Real-Time crawling
      # if self.input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER and \
      # (self.input_batch.dbMode & dc_event.Batch.DB_MODE_W == 0):
      if self.input_batch.dbMode & dc_event.Batch.DB_MODE_W == 0:
        self.wrapper.affect_db = False
      if batchItem.urlObj is not None:
        ret["url"] = batchItem.urlObj
      else:
        ret["url"] = self.loadURL(batchItem)

      # Save raw content charset to dict
      self.logger.debug("Save charset '" + str(ret["url"].charset) + "' to dict")
      ret["charset"] = ret["url"].charset

      # Check current state of site
      if self.isDisabledSite(ret["site"]):
        raise ProcessorException("Site state is not active! Actual site state is: %s. " % ret["site"].state)

      # Check overlimit max resources limits
      if self.isOverlimitMaxResources(ret["site"], ret["url"]):
        ret["errorMask"] |= APP_CONSTS.ERROR_MASK_SITE_MAX_RESOURCES_NUMBER
        return ret

      if ret["url"].processed != 0 and ret["url"].errorMask == ERROR_MASK_NO_ERRORS and \
      ret["url"].tagsCount > 0 and ret["errorMask"] == ERROR_MASK_NO_ERRORS:
        self.logger.debug("Real time crawling. Check reprocessing.")
        self.logger.debug("Batch item properties: %s", json.dumps(batchItem.properties))

      if ("PROCESSOR_NAME" in batchItem.properties) and \
      (batchItem.properties["PROCESSOR_NAME"] == "NONE"):
        self.logger.debug("RealTime Crawling: Only crawling mode. Exit.")
        ret["batchItem"] = None
        return ret

      self.logger.debug("batchItem.properties: %s", json.dumps(batchItem.properties))

      if "PROCESSOR_NAME" in batchItem.properties:
        ret["processorName"] = batchItem.properties["PROCESSOR_NAME"]
      elif "processorName" in batchItem.properties:
        ret["processorName"] = batchItem.properties["processorName"]

      if (CONSTS.REPROCESS_KEY in batchItem.properties) and \
      (batchItem.properties[CONSTS.REPROCESS_KEY] == CONSTS.REPROCESS_VALUE_NO):
        self.logger.debug("RealTime Crawling: Cashed resource. Resource crawled and errorMask is empty." +
                          "Don't need to reprocess.")
        ret["batchItem"] = None
        return ret
      else:
        self.logger.debug("RealTime Crawling: Cashed resource. Resource crawled and errorMask is emppty but " +
                          "properties reprocess is Yes or empty. Send to reprocessing.")

      # (1) Apply SQLExpression filter before processor for zero site
      if batchItem.siteId == '0':
        self.logger.debug("Check SQLExpression filter for zero site ...")
        fields = {}
        for key, value in batchItem.urlObj.__dict__.items():
          fields[key.upper()] = value

        if self.filtersApply('', self.wrapper, batchItem.siteId,
                             fields, Filters.OC_SQLE, Filters.STAGE_BEFORE_PROCESSOR, True):
          self.logger.debug("SQLExpression filter for zero site checked - SUCCESS")
        else:
          self.logger.debug("SQLExpression filter for zero site checked - Fail")
          ret["errorMask"] |= APP_CONSTS.ERROR_PROCESSOR_FILTERS_BREAK
          ret["batchItem"] = None
          return ret
      # (1) END

      if len(batchItem.properties.keys()) == 0:
        self.logger.debug('>>> property  len(batchItem.properties.keys()) == 0')
        # self.logger.debug('>>> loadSiteProperties  ret["site"].properties: ' + varDump(ret['site'].properties))

        for localProperty in ret["site"].properties:
          batchItem.properties[localProperty["name"]] = copy.deepcopy(localProperty["value"])
          # self.logger.debug('>>> copy property ' + str(localProperty["name"]) + ' = ' \
          #                  + varDump(localProperty["value"]))

      self.loadSiteProperties(ret["site"], ret["url"], batchItem, ret)  # #

      if "urlNormalizeMaskProcessor" in ret:
        self.normMask = int(ret["urlNormalizeMaskProcessor"])

      if "processCTypes" in ret and ret["url"].contentType not in ret["processCTypes"]:
        self.logger.debug('>>>> ret["url"].contentType = ' + str(ret["url"].contentType))
        self.logger.debug('>>>> ret["processCTypes"] = ' + str(ret["processCTypes"]))

        isOkContentType = False
        try:
          if "contentTypeMap" in ret:
            contentTypeMap = json.loads(ret["contentTypeMap"])
            if ret["processCTypes"] in contentTypeMap:
              self.logger.debug('>>>> Found in ret["contentTypeMap"] = ' + str(contentTypeMap))

              if ret["processCTypes"] in contentTypeMap:
                if ret["url"].contentType == contentTypeMap[ret["processCTypes"]]:
                  self.logger.debug('>>>> Good!!!')
                  isOkContentType = True

        except Exception, err:
          self.logger.debug("Fail loads of 'CONTENT_TYPE_MAP': " + str(err))

        if not isOkContentType:
          ret["errorMask"] |= APP_CONSTS.ERROR_MASK_SITE_UNSUPPORTED_CONTENT_TYPE
          ret["batchItem"] = batchItem
          self.logger.error("url ContentType not matched! url.contentType: '%s', site_properties.PROCESS_CTYPES: '%s'",
                            str(ret["url"].contentType), ret["processCTypes"])
          if self.input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER and \
          (self.input_batch.dbMode & dc_event.Batch.DB_MODE_W > 0):
            self.updateURL(batchItem)

      self.resolveProcessorNameByContentType(ret["url"].contentType, ret)
      # Check if content stored on disk
      if batchItem.urlObj.contentMask != dc_event.URL.CONTENT_STORED_ON_DISK:
        self.logger.debug(">>> Content not found on disk. Exit.")
      elif batchItem.urlObj.httpCode != 200:
        self.logger.debug(">>> HTTP Code != 200. Code == " + str(batchItem.urlObj.httpCode) + ". Exit")
      if batchItem.urlObj.contentMask != dc_event.URL.CONTENT_STORED_ON_DISK or batchItem.urlObj.httpCode != 200:
        self.updateURL(batchItem)
        ret["batchItem"] = None
        self.logger.debug("Exit. batchItem.urlObj.contentMask = " + str(batchItem.urlObj.contentMask) + \
                          " batchItem.urlObj.httpCode = " + str(batchItem.urlObj.httpCode))
        return ret
      self.updateURL(batchItem)


      # (2) Apply filter before processor to 'URL.url'
      self.logger.debug("Check filter to 'url' use regular expression ...")
      if self.filtersApply(batchItem.urlObj.url, self.wrapper, batchItem.siteId,
                           None, Filters.OC_RE, Filters.STAGE_BEFORE_PROCESSOR, True):
        self.logger.debug("Filter to 'url' use regular expression checked - SUCCESS")
      else:
        self.logger.debug("Filter to 'url' use regular expression checked - Fail")
        ret["errorMask"] |= APP_CONSTS.ERROR_PROCESSOR_FILTERS_BREAK
        ret["batchItem"] = None
        return ret
      # (2) END

      # Get raw content
      ret["rawContent"] = self.getRawContentFromFS(batchItem, ret)

      if ret["rawContent"] is not None:
        # (3) Apply filter before processor to 'raw content'
        self.logger.debug("Check filter to 'raw content' use regular expression (STAGE_BEFORE_PROCESSOR)...")
        if self.filtersApply(ret["rawContent"], self.wrapper, batchItem.siteId,
                             None, Filters.OC_RE, Filters.STAGE_BEFORE_PROCESSOR, True):
          self.logger.debug("Filter to 'raw content' use regular expression checked - SUCCESS")
        else:
          self.logger.debug("Filter to 'raw content' use regular expression checked - Fail")
          ret["errorMask"] |= APP_CONSTS.ERROR_PROCESSOR_FILTERS_BREAK
          ret["batchItem"] = None
          return ret
        # (3) END

        # Parse templates
        self.parseTemplate(batchItem, ret)

#         if "HTTP_REDIRECT_LINK" in ret and int(ret["HTTP_REDIRECT_LINK"]) > 0:
#           self.logger.debug('>>>>> headerContent batchItem.siteId: ' + str(batchItem.siteId))
#           self.logger.debug('>>>>> headerContent batchItem.urlObj.url: ' + str(batchItem.urlObj.url))
#           headerContent = self.getHeaderContent(batchItem.siteId, batchItem.urlObj.url)
#           urlValue = self.getLocationFromHeaderContent(headerContent)
#           self.logger.debug('>>>>> headerContent urlValue: ' + str(urlValue))
#           if urlValue is not None:
#             pass
#             batchItem.urlObj.url = urlValue
#             batchItem.urlObj.urlMd5 = hashlib.md5(batchItem.urlObj.url).hexdigest()
#             batchItem.urlObj.parentMd5 = batchItem.urlObj.urlMd5

        # (3) Apply filter 'STAGE_AFTER_DOM_PRE' to 'raw content'
        self.logger.debug("Check filter to 'raw content' use regular expression ('STAGE_AFTER_DOM_PRE')...")
        if self.filtersApply(ret["rawContent"], self.wrapper, batchItem.siteId, \
                             None, Filters.OC_RE, Filters.STAGE_AFTER_DOM_PRE, True):
          self.logger.debug("Filter to 'raw content' use regular expression checked - SUCCESS")
        else:
          self.logger.debug("Filter to 'raw content' use regular expression checked - Fail")
          ret["errorMask"] |= APP_CONSTS.ERROR_PROCESSOR_FILTERS_BREAK
          ret["batchItem"] = None
          return ret
        # (3) END

        self.convertRawContentCharset(ret)
        self.processTask(batchItem, ret)
        localContentHash = self.processContentHash(ret)
        if localContentHash is not None:
          ret["contentURLMd5"] = localContentHash

      # self.logger.debug("!!! batchItem.properties: " + varDump(batchItem.properties))
      if APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR in batchItem.properties:
        self.logger.debug("!!! Found '" + str(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR) + \
                          "' in batchItem.properties")

        localSiteUpdate = dc_event.SiteUpdate(batchItem.siteId)
        for attr in localSiteUpdate.__dict__:
          if hasattr(localSiteUpdate, attr):
            setattr(localSiteUpdate, attr, None)

        localSiteUpdate.id = batchItem.siteId
        localSiteUpdate.updateType = dc_event.SiteUpdate.UPDATE_TYPE_UPDATE

        # Evaluate 'Site' class values if neccessary
        changedFieldsDict = FieldsSQLExpressionEvaluator.execute(batchItem.properties, self.wrapper, ret["site"],
                                                                 None, self.logger,
                                                                 APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR)
        # Update 'Site' class values
        for name, value in changedFieldsDict.items():
          if hasattr(localSiteUpdate, name) and value is not None and name not in ['CDate', 'UDate', 'tcDate']:
            setattr(localSiteUpdate, name, value)

        localSiteUpdate.errorMask = SQLExpression(("`ErrorMask` | %s" % ret["site"].errorMask))

        updatedCount = self.wrapper.siteNewOrUpdate(siteObject=localSiteUpdate, stype=dc_event.SiteUpdate)
        self.logger.debug("!!! Use property '" + str(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR) + \
                          "' updated " + str(updatedCount) + " rows.")

    except DatabaseException, err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH_ITEM, (ret))
      ret["errorMask"] = ret["errorMask"] | APP_CONSTS.ERROR_DATABASE_ERROR
    except ProcessorException, err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH_ITEM, (ret))
      ret["errorMask"] = ret["errorMask"] | APP_CONSTS.ERROR_PROCESSOR_BATCH_ITEM_PROCESS
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH_ITEM, (ret))
      ret["errorMask"] = ret["errorMask"] | APP_CONSTS.ERROR_PROCESSOR_BATCH_ITEM_PROCESS

    # #self.logger.debug(">>> NEW DICT IS = " + str(ret))
    return ret


  # #resolveProcessorNameByContentType replaced processorName by url's contentType
  # @param urlContentType incoming url's content type
  # @param batchItemDict incoming dict of batches properties
  def resolveProcessorNameByContentType(self, urlContentType, batchItemDict):
    if "PROCESSOR_NAME_REPLACE" in batchItemDict:
      self.logger.debug(">>> PROCESSOR_NAME_REPLACE is; " + batchItemDict["PROCESSOR_NAME_REPLACE"])
      try:
        localJson = json.loads(batchItemDict["PROCESSOR_NAME_REPLACE"])
        if isinstance(localJson, dict):
          for elem in localJson:
            if isinstance(localJson[elem], types.ListType) and urlContentType in localJson[elem]:
              batchItemDict["processorName"] = elem
              self.logger.debug("Resolved processor name: " + str(elem))
              break
      except Exception as excp:
        self.logger.debug(">>> PROCESSOR_NAME_REPLACE bad json;" + str(excp))


  # #resortProcessedContentsByMetrics sorted processed contents by getting metric
  # @param batchItemDict - incoming bathitemDict
  # @param sortedMetric - name of sorted metric
  def resortProcessedContentsByMetrics(self, batchItemDict, sortedMetric):
    if "scraperResponse" in batchItemDict:
      for scraperResponse in batchItemDict["scraperResponse"]:
        if scraperResponse is not None:
          sortedContents = Metrics.sortElementsByMetric(scraperResponse.processedContent["internal"], sortedMetric)
          scraperResponse.processedContent["internal"] = sortedContents
          if len(sortedContents[0]) > 0:
            scraperResponse.processedContent["default"] = sortedContents[0]


  # #processBatchItemTemplateSelectStep implements second step of batchitem processing (template selecting)
  # @param batchItem - incoming bathitem
  # @param batchItemDict - incoming bathitemDict
  def processBatchItemTemplateSelectStep(self, batchItem, batchItemDict):  # pylint: disable=W0613
    self.logger.debug(">>> 2 step")
    if "template" in batchItemDict and "templates" in batchItemDict["template"]:
      if "scraperResponse" in batchItemDict and len(batchItemDict["scraperResponse"]) > 0:
        templateSelectType = \
            batchItemDict["template"]["select"] if "select" in batchItemDict["template"] else "first_nonempty"
        processingTemplatesDict = []
        i = 0
        self.logger.debug(">>> Tmpl Len = " + str(len(batchItemDict["template"]["templates"])))
        self.logger.debug(">>> Responce Len = " + str(len(batchItemDict["scraperResponse"])))
        for localTemplate in batchItemDict["template"]["templates"]:
          if "state" in localTemplate and not bool(int(localTemplate["state"])):
            self.logger.debug(">>> Template disable")
            i += 1
            continue
          self.templateMetricsCalculate(localTemplate, batchItemDict["scraperResponse"][i])
          processingTemplatesDict.append([copy.deepcopy(localTemplate), batchItemDict["scraperResponse"][i]])
          i += 1
        self.reduceResponse(processingTemplatesDict, templateSelectType, batchItemDict)
      else:
        self.logger.debug(">>> no scraperResponse or scraperResponse is empty")
    else:
      self.logger.debug(">>> wrong !!! empty batchItemDict[\"template\"][\"templates\"]")


  # #mergeChains pastes batches in one chain
  # @param batchItem - incoming bathitem
  # @param batchItemDict - incoming bathitemDict
  # @param chainElem - incoming chainElem
  # @param delimiter - delimiter for stick chain contents
  def mergeChains(self, chainElem, batchItem, batchItemDict, delimiter=' '):  # pylint: disable=W0612,W0613
    self.logger.debug(">>> mergeChains")
    scraperResponseDest = chainElem["batchItemDict"]["scraperResponse"][0]
    scraperResponseSrc = batchItemDict["scraperResponse"][0]
    if "site" in chainElem["batchItemDict"]:
      sitePropetries = chainElem["batchItemDict"]["site"].properties
      self.logger.debug(">>> mergeChains sitePropetries = " + str(sitePropetries))
      for sitePropElem in sitePropetries:
        if sitePropElem["name"] == "URL_CHAIN" and sitePropElem["value"] is not None:
          urlChainDict = json.loads(sitePropElem["value"])
          if "tags_name" in urlChainDict:
            self.logger.debug(">>> mergeChains URL_CHAIN = " + str(urlChainDict))

            for srcData in scraperResponseSrc.processedContent["default"].data["data"]["tagList"][0]:
              isAppended = False
              self.logger.debug(">>> mergeChains srcData = " + str(srcData["name"]))
              if urlChainDict["tags_name"] is None or srcData["name"] in urlChainDict["tags_name"]:
                for destData in scraperResponseDest.processedContent["default"].data["data"]["tagList"][0]:
                  if srcData["name"] == destData["name"]:
                    # destData["data"].extend(srcData["data"])
                    if "delimiter" in urlChainDict and urlChainDict["delimiter"] is not None:
                      localDelimiter = urlChainDict["delimiter"]
                    else:
                      localDelimiter = DEFSULT_CHAIN_DELIMITER
                    destData["data"][0] += localDelimiter
                    destData["data"][0] += srcData["data"][0]
                    if "extractors" in chainElem and srcData["name"] in chainElem["extractors"] and \
                    srcData["extractor"] not in chainElem["extractors"][srcData["name"]]:
                      destData["extractor"] += delimiter
                      destData["extractor"] += srcData["extractor"]
                    isAppended = True
                    break
                if not isAppended:
                  scraperResponseDest.processedContent["default"].data["data"]["tagList"][0].\
                  append(copy.deepcopy(srcData))
                  isAppended = True
                if isAppended:
                  if "extractors" not in chainElem:
                    chainElem["extractors"] = {}
                  if srcData["name"] not in chainElem["extractors"]:
                    chainElem["extractors"][srcData["name"]] = []
                  if srcData["extractor"] not in chainElem["extractors"][srcData["name"]]:
                    chainElem["extractors"][srcData["name"]].append(srcData["extractor"])


  # #setDefaultInternalForChainContents reassign first element in processedContent["internal"] list
  # for processedContents of chain batchItems
  # @param chainDict - incoming chainDict, where keepts addition chain batches
  def setDefaultInternalForChainContents(self, chainDict):
    self.logger.debug(">>> 3.1 reformatted Chain internal")
    for chainElem in chainDict.values():
      scraperResponseDest = chainElem["batchItemDict"]["scraperResponse"][0]
      if scraperResponseDest.processedContent["default"] is not None and \
      len(scraperResponseDest.processedContent["internal"]) > 0:
        scraperResponseDest.processedContent["internal"] = [scraperResponseDest.processedContent["default"]]


  # #processBatchItemChainSelectStep implements third step of batchitem processing (chain pasting)
  # @param batchItem - incoming bathitem
  # @param batchItemDict - incoming bathitemDict
  # @param chainDict - incoming chainDict, where keepts addition chain batches
  def processBatchItemChainSelectStep(self, batchItem, batchItemDict, chainDict):
    self.logger.debug(">>> 3 step")
    self.logger.debug(">>> Chain Id = " + str(batchItem.urlObj.chainId) + " Md5= " + batchItem.urlObj.urlMd5)
    if batchItem.urlObj.chainId is not None:
      batchItemDict["dellBatch"] = True
      if batchItem.urlObj.chainId in chainDict:
        self.logger.debug(">>> old Chain Id = " + str(batchItem.urlObj.chainId) + " Md5= " + batchItem.urlObj.urlMd5)
        if "scraperResponse" in batchItemDict and len(batchItemDict["scraperResponse"]) > 0 and \
        batchItemDict["scraperResponse"][0] is not None:
          if "scraperResponse" not in chainDict[batchItem.urlObj.chainId]["batchItemDict"] or \
          len(chainDict[batchItem.urlObj.chainId]["batchItemDict"]["scraperResponse"]) == 0 or \
          chainDict[batchItem.urlObj.chainId]["batchItemDict"]["scraperResponse"][0] is None:
            chainDict[batchItem.urlObj.chainId]["batchItemDict"]["scraperResponse"] = batchItemDict["scraperResponse"]
          else:
            self.mergeChains(chainDict[batchItem.urlObj.chainId], batchItem, batchItemDict)
        else:
          self.logger.debug(">>> no or empty scraperResponse for current BatchItem")
      else:
        self.logger.debug(">>> new Chain Id = " + str(batchItem.urlObj.chainId) + " Md5= " + batchItem.urlObj.urlMd5)
        chainDict[batchItem.urlObj.chainId] = {"batchItem": copy.deepcopy(batchItem),
                                               "batchItemDict": copy.deepcopy(batchItemDict)}


  # #processBatchItemTemplateFillStep fills batchItemDict["processedContent"] field
  # @param batchItem - incoming bathitem
  # @param batchItemDict - incoming bathitemDict
  def processBatchItemTemplateFillStep(self, batchItem, batchItemDict):  # pylint: disable=W0613
    self.logger.debug(">>> 4 step")
    try:
      if "template" in batchItemDict:
        # self.logger.debug(">>> template is = " + str(batchItemDict["template"]))
        if "output_format" in batchItemDict["template"]:
          self.mapResponse(batchItemDict["template"], batchItemDict["url"].crawlingTime,
                           batchItemDict["scraperResponse"][0] if "scraperResponse" in batchItemDict and \
                           len(batchItemDict["scraperResponse"]) > 0 else None,
                           batchItemDict["processorProperties"])
        else:
          self.logger.debug(">>> wrong no output_format field for batch template")

        batchItemDict["processedContent"] = self.getProcessedContent(batchItemDict["template"],
                                                                     batchItemDict["scraperResponse"][0] if \
                                                                     "scraperResponse" in batchItemDict and \
                                                                     len(batchItemDict["scraperResponse"]) > 0 \
                                                                     else None,
                                                                     batchItemDict["errorMask"])
      else:
        self.logger.debug(">>> wrong !!! empty batchItemDict[\"template\"]")
    except Exception, err:
      self.logger.error("Template error: " + str(err) + "\nSiteId: " + str(batchItem.siteId) + \
                        "\nurl: " + batchItem.urlObj.url + "\nurlMD5: " + str(batchItem.urlObj.urlMd5))
      self.logger.debug(Utils.getTracebackInfo())
      batchItemDict["errorMask"] = batchItemDict["errorMask"] | APP_CONSTS.ERROR_TEMPLATE_SOURCE


  # #processBatchItemURLContentStep creates and fills urlContent field
  # @param batchItem - incoming bathitem
  # @param batchItemDict - incoming bathitemDict
  def processBatchItemURLContentStep(self, batchItem, batchItemDict):  # pylint: disable=W0613
    self.logger.debug(">>> 5 step")
    if "template" in batchItemDict and "templates" not in batchItemDict["template"]:
      batchItemDict["template"] = {"templates": batchItemDict["template"]}
    if "processedContent" in batchItemDict and batchItemDict["processedContent"] is not None:
      self.putContent(batchItem, batchItemDict["processedContent"], batchItemDict)
    self.updateProcessedURL(batchItem, batchItemDict)


  def processBatchItems(self, inputItems):
    #----------------------------------------------------------------------------------------
    localBatchItems = inputItems
    batchProcessingData = []
    chainDict = {}

    try:
      for batchItem in localBatchItems:
        self.logger.debug("!!! urlId: %s, maxExecutionTimeReached = %s", str(batchItem.urlId),
                          str(self.maxExecutionTimeReached))

        if self.maxExecutionTimeReached:
          self.logger.debug("Maximum execution time %ss reached, news extraction loop interrupted!",
                            str(self.maxExecutionTimeValue))
          self.logger.debug("!!! ERROR_MAX_EXECUTION_TIME !!! Set errorMask = %s",
                            str(APP_CONSTS.ERROR_MAX_EXECUTION_TIME))

          if self.removeUnprocessedItems:
            if len(batchProcessingData) > 0:
              batchProcessingData[-1]["errorMask"] = APP_CONSTS.ERROR_MAX_EXECUTION_TIME
            break
          else:
            elem = {}
            elem["errorMask"] |= APP_CONSTS.ERROR_MAX_EXECUTION_TIME
            batchItem.urlObj.status = dc_event.URL.STATUS_CRAWLED
            elem["batchItem"] = batchItem
            batchProcessingData.append(elem)
            continue

        batchProcessingData.append(self.processBatchItemScrapyStep(batchItem))

      for i in xrange(0, len(batchProcessingData)):
        # self.logger.debug(">>> i = " + str(i))
        if "batchItem" not in batchProcessingData[i] or batchProcessingData[i]["batchItem"] is not None:
          # self.logger.debug(">>> i = " + str(i))
          self.processBatchItemTemplateSelectStep(localBatchItems[i], batchProcessingData[i])

      for i in xrange(0, len(batchProcessingData)):
        if "batchItem" not in batchProcessingData[i] or batchProcessingData[i]["batchItem"] is not None:
          sortedMetric = self.getPropValueFromSiteProperties(batchProcessingData[i], "DEFAULT_METRIC")
          if sortedMetric is not None:
            self.resortProcessedContentsByMetrics(batchProcessingData[i], sortedMetric)

      for i in xrange(0, len(batchProcessingData)):
        if "batchItem" not in batchProcessingData[i] or batchProcessingData[i]["batchItem"] is not None:
          self.processBatchItemChainSelectStep(localBatchItems[i], batchProcessingData[i], chainDict)

      self.setDefaultInternalForChainContents(chainDict)

      newBatchProcessingData = []
      newBatchitems = []
      for i in xrange(0, len(batchProcessingData)):
        if "dellBatch" not in batchProcessingData[i] or not batchProcessingData[i]["dellBatch"]:
          newBatchitems.append(localBatchItems[i])
          newBatchProcessingData.append(batchProcessingData[i])
        else:
          self.updateProcessedURL(localBatchItems[i], batchProcessingData[i])
      localBatchItems = newBatchitems
      batchProcessingData = newBatchProcessingData
      for key in chainDict:
        localBatchItems.append(chainDict[key]["batchItem"])
        batchProcessingData.append(chainDict[key]["batchItemDict"])

      for i in xrange(0, len(batchProcessingData)):
        if "batchItem" not in batchProcessingData[i] or batchProcessingData[i]["batchItem"] is not None:
          self.processBatchItemTemplateFillStep(localBatchItems[i], batchProcessingData[i])

      for i in xrange(0, len(batchProcessingData)):
        self.processBatchItemURLContentStep(localBatchItems[i], batchProcessingData[i])

    except Exception, err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH_ITEM)
      if len(localBatchItems) > 0:
        localBatchItems[-1].urlObj.errorMask = APP_CONSTS.ERROR_PROCESSOR_BATCH_ITEM_PROCESS

    ret = localBatchItems
    #----------------------------------------------------------------------------------------
    return ret


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    try:
      start_batch_time = time.time()

      # read pickled batch object from stdin and unpickle it
      input_pickled_object = sys.stdin.read()
      input_batch = pickle.loads(input_pickled_object)

      # self.logger.info("Incoming batch id: %s, items: %s", str(input_batch.id), str(len(input_batch.items)))
      # self.logger.debug("input_batch: %s", varDump(input_batch))

      app.Profiler.messagesList.append("Batch.id=" + str(input_batch.id))
      self.input_batch = input_batch
      Utils.storePickleOnDisk(input_pickled_object, ENV_PROCESSOR_STORE_PATH, "processor.in." +
                              str(self.input_batch.id))

      if int(self.input_batch.maxExecutionTime) > 0 or (self.maxTimeCli is not None and self.maxTimeCli > 0):
        self.maxExecutionTimeValue = self.input_batch.maxExecutionTime
        # # set value from cli
        if self.maxTimeCli is not None and self.maxTimeCli > 0:
          self.maxExecutionTimeValue = int(self.maxTimeCli)

        signal.signal(signal.SIGALRM, self.signalHandlerTimer)
        signal.alarm(self.maxExecutionTimeValue)
        self.removeUnprocessedItems = bool(self.input_batch.removeUnprocessedItems)
        self.logger.debug("Set maxExecutionTime = %s, removeUnprocessedItems = %s",
                          str(self.maxExecutionTimeValue), str(self.removeUnprocessedItems))

      #----------------------------------------------------------------------------------------
      batchItems = self.input_batch.items
      batchItems = self.extendBatchItemsWithChain(batchItems)
      self.logger.info(">>> batchItems len = " + str(len(batchItems)))
      batchItems = self.processBatchItems(batchItems)
      #----------------------------------------------------------------------------------------
      # Main processing over every url from list of urls in the batch object
      batchItems = [localItem for localItem in batchItems if localItem is not None]

      self.logger.debug('len(batchItems) = ' + str(len(batchItems)))
      self.logger.debug('len(self.accumulatedBatchItems) = ' + str(len(self.accumulatedBatchItems)))

      self.accumulateProcessing = True
      # check allowed limits
      if self.input_batch.maxItems is not None and \
      int(self.input_batch.maxItems) < len(self.accumulatedBatchItems) + len(batchItems):
        self.accumulatedBatchItems = self.accumulatedBatchItems[0: (int(self.input_batch.maxItems) - len(batchItems))]
        self.accumulatedBatchItems[-1].urlObj.errorMask |= APP_CONSTS.ERROR_MAX_ITEMS
        self.logger.debug("Truncated scraper responces list because over limit 'maxItems' = " + \
                        str(self.input_batch.maxItems) + " set errorMask = " + str(APP_CONSTS.ERROR_MAX_ITEMS))

      if self.input_batch.crawlerType != dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        self.logger.debug('>>> call putUrlsMultiItems()')
        self.putUrlsMultiItems(self.accumulatedBatchItems)
        if len(batchItems) > 0:
          self.logger.debug('>>> call putRawContentsMultiItems()')
          self.putRawContentsMultiItems(batchItems[0].siteId, batchItems[0].urlObj.url, self.accumulatedBatchItems)

      self.accumulatedBatchItems = self.processBatchItems(self.accumulatedBatchItems)
      self.accumulatedBatchItems = [localItem for localItem in self.accumulatedBatchItems if localItem is not None]

      batchItems.extend(self.accumulatedBatchItems)

      # self.logger.debug("Output batch items: " + varDump(batchItems))

      # TODO: for what this difference ???
#       if input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
#         input_batch.items = batchItems
#         process_task_batch = input_batch
#       else:
#         process_task_batch = Batch(input_batch.id, batchItems)

      input_batch.items = batchItems

      # self.logger.info("Outgoing batch id: %s, items: %s", str(input_batch.id), str(len(input_batch.items)))
      # self.logger.debug("%s", varDump(input_batch))

      # send response to the stdout
      output_pickled_object = pickle.dumps(input_batch)  # #process_task_batch)
      Utils.storePickleOnDisk(output_pickled_object, ENV_PROCESSOR_STORE_PATH, "processor.out." + str(input_batch.id))
      sys.stdout.write(output_pickled_object)
      sys.stdout.flush()

      # Update db counters
      self.wrapper.fieldsRecalculating(self.batchSites)

      batch_processing_time = int((time.time() - start_batch_time) * 1000)
      self.logger.debug("Batch processing time: %s msec.", str(batch_processing_time))
    except ProcessorException, err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH)
      raise Exception(MSG_INFO_PROCESS_BATCH + " : " + str(err))
    except DatabaseException, err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH)
      raise Exception(MSG_INFO_PROCESS_BATCH + " : " + str(err))
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_INFO_PROCESS_BATCH, (err))
      raise Exception(MSG_ERROR_PROCESS_BATCH + " : " + str(err))


  # # load cli arguments
  #
  # @param - None
  # @return - None
  def loadAppParams(self):
    # # max time execution
    if self.pargs.maxtime:
      self.maxTimeCli = int(self.pargs.maxtime)


  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      if self.pargs.config:
        self.config = ConfigParser.ConfigParser()
        self.config.optionxform = str
        self.config.read(self.pargs.config)
      else:
        raise Exception(MSG_ERROR_EMPTY_CONFIG_FILE_NAME)
    except Exception, err:
      raise Exception(MSG_ERROR_LOAD_CONFIG + ' ' + str(err))


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      log_conf_file = self.config.get("Application", "log")
      logging.config.fileConfig(log_conf_file)
      # Logger initialization
      self.logger = Utils.MPLogger().getLogger()
    except Exception, err:
      raise Exception(MSG_ERROR_LOAD_LOG_CONFIG_FILE + str(err))


  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    try:
      self.raw_data_dir = self.config.get(self.__class__.__name__, "raw_data_dir")
      self.db_task_ini = self.config.get(self.__class__.__name__, "db-task_ini")
      try:
        self.algorithmsModel = self.config.getint(self.__class__.__name__, "algorithmsModel")
      except Exception as err:
        pass
      # Add support operations updateCollectedURLs and removeURLs
      cfgParser = ConfigParser.ConfigParser()
      cfgParser.read(self.db_task_ini)
      self.wrapper = DBTasksWrapper(cfgParser)
    except Exception, err:
      raise Exception(MSG_ERROR_LOAD_OPTIONS + str(err))


  # # Applies filters and returns bool result
  #
  # @param localValue - subject for apply filter
  # @param wrapper - DBTasksWrapper instance
  # @param siteId - site ID used with db-task wrapper
  # @param fields - dictionary values of support macro names ('PDATE' and other)
  # @param opCode - operation code
  # @param stage - stage of apply filter
  # @param defaultRet - default value for result
  # @return True  if filter is good or False otherwise
  def filtersApply(self, localValue, wrapper, siteId, fields=None, opCode=Filters.OC_RE, stage=Filters.STAGE_ALL, \
                   defaultRet=False):
    ret = defaultRet
    fValue = Utils.generateReplacementDict()
    localFilters = None
    if siteId in self.objFilters:
      localFilters = self.objFilters[siteId]

    if localFilters is None:
      localFilters = Filters(self.filters, wrapper, siteId, 0, fields, opCode, stage)
      self.objFilters[siteId] = localFilters

    self.logger.debug("Filters with stage (" + str(stage) + ") count = " + \
                      str(localFilters.searchFiltersWithStage(stage)) + \
                      '\nfields: ' + str(fields))

    if localFilters.isExistStage(stage):
      self.logger.debug(">>> value before filter include = " + localValue[:255] + ' . . . ')
      fResult = localFilters.filterAll(stage, fValue, Filters.LOGIC_OR, localValue, 1)
      self.logger.debug(">>> filter result - " + str(fResult))

      ret = False
      for elem in fResult:
        self.logger.debug('elem = ' + str(elem) + ' type: ' + str(type(elem)))
        if elem > 0:
          ret = True
          break

      if ret is True:
        self.logger.debug(">>> value before filter exclude = " + localValue[:255] + ' . . . ')
        fResult = localFilters.filterAll(stage, fValue, Filters.LOGIC_OR, localValue, -1)
        self.logger.debug(">>> filter result - " + str(fResult))
        for elem in fResult:
          self.logger.debug('elem = ' + str(elem) + ' type: ' + str(type(elem)))
          if elem < 0:
            ret = False
            break

    return ret


  # #get exit code
  # return extt code
  # 0 if no critical errors was encountered during processing
  # 1 if smth bad happened
  #
  def getExitCode(self):
    return self.exit_code


  # # put multi items Urls to DB
  #
  # @param batchItems - batch items list
  # @return - bool flag of execution (True - if success)
  def putUrlsMultiItems(self, batchItems):
    # result variable
    params = []

    for batchItem in batchItems:
      params.append(batchItem.urlObj)
      self.logger.debug(">>> putUrlsMultiItems url: " + str(batchItem.urlObj.url))

    self.logger.debug(">>> putUrlsMultiItems params: " + varDump(params))

    result = self.wrapper.urlNew(params)
    self.logger.debug(">>> putUrlsMultiItems result: " + str(result))
    self.logger.debug(">>>             bool(result): " + str(bool(result)))

    return bool(result)


  # # Get raw content from FS
  #
  # @param siteId - site ID of batch
  # @param url - url string
  # @return rawContent, dynamicContent, headerContent, requestsContent
  def getRawContent(self, siteId, url):
    # #Local function for check and print of data
    #
    # @param rawContentData - raw content data
    # @param rawContentName - raw content name
    def printContentStatus(rawContentData, rawContentName):
      if rawContentData is not None:
        self.logger.debug("Some %s content size %s on disk", rawContentName, str(len(rawContentData)))
      else:
        self.logger.debug("NO %s content on disk", rawContentName)

    # variables for result
    rawContent = None
    dynamicContent = None
    headerContent = None
    requestsContent = None

    urlContentObj = dc_event.URLContentRequest(siteId, url, \
                                      dc_event.URLContentRequest.CONTENT_TYPE_RAW_LAST + \
                                      dc_event.URLContentRequest. CONTENT_TYPE_RAW + \
                                      dc_event.URLContentRequest.CONTENT_TYPE_DYNAMIC + \
                                      dc_event.URLContentRequest.CONTENT_TYPE_HEADERS + \
                                      dc_event.URLContentRequest.CONTENT_TYPE_REQUESTS)

    rawContentData = self.wrapper.urlContent([urlContentObj])

    if rawContentData is not None and len(rawContentData) > 0:
      if rawContentData[0].headers is not None and len(rawContentData[0].headers) > 0 and \
        rawContentData[0].headers[0] is not None:
        headerContent = rawContentData[0].headers[0].buffer

      if rawContentData[0].requests is not None and len(rawContentData[0].requests) > 0 and \
        rawContentData[0].requests[0] is not None:
        requestsContent = rawContentData[0].requests[0].buffer

      if rawContentData[0].rawContents is not None:
        if len(rawContentData[0].rawContents) > 0 and rawContentData[0].rawContents[0] is not None:
          rawContent = rawContentData[0].rawContents[0].buffer
        else:
          pass
        if len(rawContentData[0].rawContents) > 1 and rawContentData[0].rawContents[1] is not None:
          dynamicContent = rawContentData[0].rawContents[1].buffer
        else:
          pass

    printContentStatus(rawContent, 'raw')
    printContentStatus(dynamicContent, 'dynamic')
    printContentStatus(headerContent, 'header')
    printContentStatus(requestsContent, 'requests')

    return rawContent, dynamicContent, headerContent, requestsContent


  # # Put raw content from FS use certain request type
  #
  # @param batchItems - batch items list
  # @param rawContentData - content data for put
  # @param contentRequestType - type of content request
  # @return - None
  def putRawContentOfType(self, batchItems, rawContentData, contentRequestType):

    rawContent = ''
    urlPutList = []

    if rawContentData is not None:
      rawContent = rawContentData

    # put raw content to DB
    for batchItem in batchItems:

      putDict = {}
      putDict["id"] = batchItem.urlObj.urlMd5
      putDict["data"] = rawContent
      putDict["cDate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      urlPutList.append(dc_event.URLPut(batchItem.siteId,
                                        batchItem.urlObj.urlMd5,
                                        contentRequestType,
                                        putDict))

    self.wrapper.putURLContent(urlPutList)


  # # put raw multi items Contents to DB
  #
  # @param siteId - site ID of batch
  # @param url - url string
  # @param batchItems - batch items list
  # @return - None
  def putRawContentsMultiItems(self, siteId, url, batchItems):

    self.logger.debug(">>> putRawContentsMultiItems enter...")

    rawContent, dynamicContent, headerContent, requestsContent = self.getRawContent(siteId, url)

    self.putRawContentOfType(batchItems, rawContent, dc_event.Content.CONTENT_RAW_CONTENT)
    self.putRawContentOfType(batchItems, dynamicContent, dc_event.Content.CONTENT_DYNAMIC_CONTENT)
    self.putRawContentOfType(batchItems, headerContent, dc_event.Content.CONTENT_HEADERS_CONTENT)
    self.putRawContentOfType(batchItems, requestsContent, dc_event.Content.CONTENT_REQUESTS_CONTENT)


  # #Timer alarm signal handler
  #
  # @param signum
  # @param frame
  def signalHandlerTimer(self, signum, frame):
    del frame
    self.maxExecutionTimeReached = True
    self.logger.debug("Signal %s - timer trapped!", str(signum))
