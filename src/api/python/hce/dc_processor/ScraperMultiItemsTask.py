"""
HCE project,  Python bindings, Distributed Tasks Manager application.
ScraperMultiItemsTask Class content main functional scrapering for multi items.

@package: dc_processor
@file ScraperMultiItemsTask.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import os  # pylint: disable=W0611
import re
import sys
import time
import logging.config
import ConfigParser
import pickle
import json
# import datetime
# import base64
import copy
# import urlparse
import xml.sax.saxutils
# from contextlib import closing  # pylint: disable=W0611
from cement.core import foundation
from dateutil.parser import *  # pylint: disable=W0401,W0614
from dateutil import parser
from scrapy.selector import Selector

from dc.EventObjects import SiteFilter  # pylint: disable=W0611
from dc.EventObjects import Batch  # pylint: disable=W0611
import dc.EventObjects as dc_event
from app.Utils import varDump
from app.Utils import isValidURL
import app.Utils as Utils
import app.Consts as APP_CONSTS
from app.Utils import SQLExpression
import app.Profiler
from app.DateTimeType import DateTimeType
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
from app.Utils import ExceptionLog
import dc_processor.Constants as CONSTS
from dc_processor.Scraper import Scraper
from dc_processor.ScraperInData import ScraperInData  # pylint: disable=W0611
from dc_processor.ScraperResponse import ScraperResponse
from dc_processor.TemplateExtractorXPathPreparing import TemplateExtractorXPathPreparing
from dc_processor.scraper_result import Result as Result
from dc_processor.PDateTimezonesHandler import PDateTimezonesHandler
from dc_processor.MediaLimitsHandler import MediaLimitsHandler
# scraper's modules used via eval()
from dc_processor.newspaper_extractor import NewspaperExtractor  # pylint: disable=W0611
from dc_processor.goose_extractor import GooseExtractor  # pylint: disable=W0611
from dc_processor.scrapy_extractor import ScrapyExtractor
from dc_processor.ml_extractor import MLExtractor  # pylint: disable=W0611
from dc_processor.base_extractor import BaseExtractor  # pylint: disable=W0611
from dc_processor.custom_extractor import CustomExtractor  # pylint: disable=W0611
from dc_crawler.DBTasksWrapper import DBTasksWrapper
import dc_crawler.Constants as CRAWLER_CONSTS

# # ScraperResultDocuments class for support ScraperMultiItemsTask
#
class ScraperResultDocuments(object):
  # Constructor
  #
  # @param keys - list of templates names
  # @param urlId - input data urlId
  def __init__(self, keys, urlId):
    self.urlId = urlId
    self.docs = {}
    self.join = {}
    self.isExtract = {}
    self.mandatory = {}
    self.etree = {}
    for key in keys:
      self.docs[key] = []
      self.join[key] = []
      self.isExtract[key] = []
      self.mandatory[key] = []
      self.etree[key] = []


  # #Add etree for documents
  #
  # @param key - name of key
  # @param value - new value of etree
  # @return - None
  def addEtree(self, key, value):
    if not self.etree.has_key(key):
      self.docs[key] = []
      self.join[key] = []
      self.isExtract[key] = []
      self.mandatory[key] = []
      self.etree[key] = []

    self.etree.get(key).append(copy.deepcopy(value))


  # # Add new document
  #
  # @param key - name of key
  # @param value - new value of doc
  def addDoc(self, key, value, join, isExtract, mandatory):
    if not self.docs.has_key(key):
      self.docs[key] = []
      self.join[key] = []
      self.isExtract[key] = []
      self.mandatory[key] = []

    self.docs.get(key).append(copy.deepcopy(value))
    self.join.get(key).append(copy.deepcopy(join))
    self.isExtract.get(key).append(copy.deepcopy(isExtract))
    self.mandatory.get(key).append(copy.deepcopy(mandatory))


  # # Get count of documents
  #
  # @param inDict - input dictionary whose has value as list
  # @return count of documents
  def getMaxCount(self, inDict):
    # variable for result
    count = 0
    for key in inDict.keys():
      count = max(count, len(inDict.get(key)))

    return count


  # # Get tag names list exist in all documents
  #
  # @param - None
  # @return list of tag names exist in all documents
  def getTagNamesExistAllDocs(self):
    # variable for result
    tagNames = []
    count = self.getMaxCount(self.docs)
    for key in self.docs.keys():
      size = len(self.docs.get(key))
      if count == size:
        tagNames.append(key)

    return tagNames


  # #Compare two paths and return common part
  # @param lhs - first path
  # @param rhs - second path
  # @return - common part of paths
  def getCommonPath(self, lhs, rhs, logger=None):  # pylint: disable=W0612,W0613
    # variable for result
    ret = []
    length = min(len(lhs), len(rhs))

    # if logger is not None:
      # logger.debug('>>> lhs: ' + str(lhs))
      # logger.debug('>>> rhs: ' + str(rhs))

    for i in range(length):
      if isinstance(lhs[i], str) and isinstance(rhs[i], str) and lhs[i] != rhs[i]:
        if i > 0:
          ret = lhs[:i]
        return ret

      # logger.info('len(lhs[' + str(i) + ']) = ' + str(len(lhs[i])) + \
      # ' len(rhs[' + str(i) + ']) = ' + str(len(rhs[i])))

      if isinstance(lhs[i], tuple) and isinstance(rhs[i], tuple) and len(lhs[i]) == len(rhs[i]):
        for j in range(len(lhs[i])):
          # logger.info('lhs[' + str(j) + '] = ' + str(lhs[i][j] + ' rhs[' + str(j) + '] = ' + str(rhs[i][j])))
          if lhs[i][j] != rhs[i][j]:

            # logger.info('lhs[:i] = ' + str(lhs[:i]))
            if i > 0:
              ret = lhs[:i]

            # logger.debug('ret = ' + str(ret))
            return ret

    return ret


  # #Calculate index path
  #
  # @param etree - etree input data
  # @result path - common path got from etree
  def calculateIndexPath(self, etree, logger=None):
    # variable for result
    ret = []
    pathDict = {}
    pathList = []

    for key in etree.keys():
      pathList.extend(etree.get(key))

    for index in range(len(pathList) - 1):
      commonPath = self.getCommonPath(pathList[index], pathList[index + 1], logger)
      commonPathCount = 0
      if pathDict.has_key(str(commonPath)):
        commonPathCount = int(pathDict.get(str(commonPath))[1])

      pathDict[str(commonPath)] = (commonPath, commonPathCount + 1)

    localpathList = []
    for elem in pathDict.values():
      localpathList.append(elem)

    localpathList.sort(key=lambda tup: tup[1], reverse=True)
    if len(localpathList) > 0:
      ret = (localpathList[0])[0]

    return ret


  # # Get index number of path
  #
  # @param indexPath - common index path
  # @param elementPath - element path
  # @return indexNumber - index number (-1 if wrong indexPath) and first inequal elements
  def getIndexNumberOfPath(self, indexPath, elemPath, logger=None):
    elementPath = copy.deepcopy(elemPath)
    length = min(len(indexPath), len(elementPath))

    if logger is not None:
      logger.debug('\n>>> indexPath: ' + str(indexPath))
      logger.debug('\n>>> elementPath: ' + str(elementPath))

    for i in range(length):
      if isinstance(indexPath[i], str) and isinstance(elementPath[i], str) and indexPath[i] != elementPath[i]:
        if logger is not None:
          logger.debug("Both have type 'str' and indexPath[" + str(i) + "] != elementPath[" + str(i) + "]")
        return -1

      if isinstance(indexPath[i], tuple) and isinstance(elementPath[i], tuple):
        size = min(len(indexPath[i]), len(elementPath[i]))
        for j in range(size):
          if indexPath[i][j] != elementPath[i][j]:
            if logger is not None:
              logger.debug("Both have type 'tuple' and indexPath[" + str(i) + "][" + str(j) + "] != elementPath[" + \
                           str(i) + "][" + str(j) + "]")
            return -1

    if len(elementPath) > len(indexPath):
      if logger is not None:
        logger.debug('type(elementPath[len(indexPath)])) = ' + str(type(elementPath[len(indexPath)])) + \
                     ' elementPath[' + str(len(indexPath)) + ']: ' + str(elementPath[len(indexPath)]))

      if isinstance(elementPath[len(indexPath)], tuple):
        if len(elementPath[len(indexPath)]) > 1:
          if logger is not None:
            logger.debug('>>> elementPath[' + str(len(indexPath)) + '][1] = ' + str(elementPath[len(indexPath)][1]))

          return elementPath[len(indexPath)][1]

    return -1


  # # Get all tags
  #
  # @param mandatoryTags - dyctionary of mandatory properties for tags (key - tag name, value - boolean mandatory flag)
  # @param logger - logger instance
  # @return all tags
  def getAllTags(self, mandatoryTags, logger=None):
    # variable for result
    resTags = []
    count = self.getMaxCount(self.docs)

    # #Calculate index block
    indexPath = self.calculateIndexPath(self.etree, logger)
    if logger is not None:
      logger.info('Calculated indexPath: ' + str(indexPath))

    if logger is not None:
      for key in self.etree:
        logger.debug('len(self.etree.get(' + str(key) + ') = ' + str(len(self.etree.get(key))))
      for key in self.docs:
        logger.debug('len(self.docs.get(' + str(key) + ') = ' + str(len(self.docs.get(key))))

    resultList = []
    for index in range(self.getMaxCount(self.etree)):
      localRes = Result(None, self.urlId)
      resultList.append(localRes)

    if logger is not None:
      logger.debug('count = ' + str(count))
      logger.debug('len(resultList) = ' + str(len(resultList)))

    for key in self.docs.keys():
      for index in range(len(self.docs.get(key))):
        if logger is not None:
          logger.debug('==== key: ' + str(key) + ' index: ' + str(index) + ' ====')

        if len(self.etree.get(key)) > index:
          number = int(self.getIndexNumberOfPath(indexPath, self.etree.get(key)[index], logger))
          if logger is not None:
            logger.debug('number = ' + str(number) + ' self.docs.get(' + str(key) + ')[' + str(index) + '].tags: ' + \
                         varDump(self.docs.get(key)[index].tags))

          if int(number) > 0 and int(number) <= len(self.docs.get(key)):
            if resultList[int(number) - 1].tags.has_key(key):
              result = self.updateTagValue(resultList[int(number) - 1], self.docs.get(key)[index].tags, key)
              resultList[int(number) - 1].tags.update(result.tags)
            else:
              resultList[int(number) - 1].tags.update({key:self.docs.get(key)[index].tags[key]})

            if logger is not None:
              logger.debug("resultList[" + str(int(number) - 1) + "].tags.update({" + str(key) + ":self.docs.get(" + \
                         str(key) + ")[" + str(index) + "].tags[" + str(key) + "]})")

    for index in range(0, len(resultList)):
      isMandatory = True
      countSelected = 0
      for key in self.docs.keys():
        if not resultList[index].tags.has_key(key) and bool(mandatoryTags[key]) is True:
          isMandatory = False
          break

        if resultList[index].tags.has_key(key):
          countSelected = countSelected + 1

      if countSelected == 0:
        isMandatory = False

      if isMandatory:
        resTags.append(resultList[index])

    if len(resTags) == 0:
      resTags.append(Result(None, self.urlId))

    return resTags


  # # Update value of tag
  #
  # @param result - instance of Result for update
  # @param tags - instance of tags object for append to Result object
  # @param tag_name - tag name used as key
  # @return - None
  def updateTagValue(self, result, tags, tag_name):

    data = {"extractor":"Base extractor", "data":"", "name":""}
    data["data"] = [result.tags[tag_name]["data"][0] + tags[tag_name]["data"][0]]
    data["name"] = result.tags[tag_name]["name"]
    data["xpath"] = result.tags[tag_name]["xpath"]
    data["type"] = result.tags[tag_name]["type"]
    data["extractor"] = result.tags[tag_name]["extractor"]
    result.tags[tag_name] = data

    return result


  # # Get all documents
  #
  # @param mandatoryTags - dyctionary of mandatory properties for tags (key - tag name, value - boolean mandatory flag)
  # @param logger - logger instance
  # @return all documents
  def getAllDocs(self, mandatoryTags, logger=None):
    # variable for result
    resDocs = []

    resTags = self.getAllTags(mandatoryTags, logger)
    count = len(resTags)

    tagsNames = self.getTagNamesExistAllDocs()

    if len(tagsNames) > 0:
      key = tagsNames[0]

      for index in range(count):
        if len(self.join.get(key)) > index and \
        len(self.isExtract.get(key)) > index and \
        len(self.mandatory.get(key)) > index:
          resDocs.append({"obj": resTags[index],
                          "join": self.join.get(key)[index],
                          "isExtract": self.isExtract.get(key)[index],
                          "mandatory": self.mandatory.get(key)[index],
                          CONSTS.TAG_ORDER_NUMBER: len(resDocs) + 1})

    return resDocs



# # ScraperMultiItemsTask Class content main functional scrapering for multi items,
# class inherits from foundation.CementApp
#
class ScraperMultiItemsTask(Scraper):  # #foundation.CementApp):

  # # Constants error messages used in class
  MSG_ERROR_PARSE_CMD_PARAMS = "Error parse command line parameters."
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"

  MSG_ERROR_LOAD_PROPERTIES_FROM_FILE = "Error load Scraper multi items properties from file"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."

  MSG_ERROR_READ_INPUT_DATA = "Error read input data from stdin."
  MSG_ERROR_INPUT_DATA_NONE = "Input data is none"
  MSG_ERROR_INPUT_DATA_WITHOUT_BATCH = "Input data without batch item."
  MSG_ERROR_INPUT_DATA_WITHOUT_PROPERTIES = "Input data has batch item without 'properties'."
  MSG_ERROR_GET_PROPERTIES = "Error getting properties from input data"

  MSG_ERROR_LOAD_EXTRACTORS = "Error load extractors "
  MSG_ERROR_ADJUST_PR = "Error adjust partial references. "
  MSG_ERROR_ADJUST_PUBDATE = "Error adjust PUBDATE. "
  MSG_ERROR_ADJUST_TITLE = "Error adjust title. "
  MSG_ERROR_ADJUST_LINK_URL = "Error adjust link URL. "


  # #Constans used options from config file
  SCRAPER_MULTI_ITEMS_OPTION_LOG = "log"
  SCRAPER_MULTI_ITEMS_OPTION_PROPERTY_JSON_FILE = "property_file_name"

  # #Constans used in class
  ENV_SCRAPER_STORE_PATH = "self.ENV_SCRAPER_STORE_PATH"
  EXTENDED_NEWS_TAGS = {"description": ["//meta[@name='description']//@content"]}
  DATA_NEWS_TAGS = [CONSTS.TAG_DC_DATE]
#   WWW_PREFIX = "www."

  TAGS_DATETIME_TEMPLATE_TYPES = [CONSTS.TAG_TYPE_DATETIME]
  OPTION_SECTION_DATETIME_TEMPLATE_TYPES = 'tags_datetime_template_types'

  # Mandatory
  class Meta(object):
    label = CONSTS.SCRAPER_MULTI_ITEMS_APP_CLASS_NAME
    def __init__(self):
      pass


  # #constructor
  def __init__(self, usageModel=APP_CONSTS.APP_USAGE_MODEL_PROCESS, configFile=None, logger=None, inputData=None):
    if usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class __init__ method
      # #foundation.CementApp.__init__(self)
      Scraper.__init__(self)

    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.usageModel = usageModel
    self.configFile = configFile
    self.logger = logger
    self.input_data = inputData
    self.properties = {}
    self.outputFormat = None
    self.output_data = None
    self.extractor = None
    self.extractors = []
    self.itr = None
    self.pubdate = None
    self.errorMask = APP_CONSTS.ERROR_OK
    self.xpathSplitString = ' '
    self.useCurrentYear = 0
    self.datetimeTemplateTypes = []
    self.dbWrapper = None
    self.mediaLimitsHandler = None


  # # setup application
  def setup(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class setup method
      foundation.CementApp.setup(self)

  # # run application
  def run(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class run method
      foundation.CementApp.run(self)
      # get input data from stdin
      self.input_data = self.__getInputData()

    # call initialization application
    config = self.__initApp(self.configFile)

    self.process(config)

    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # Finish logging
      self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # #initialize application from config files
  #
  # @param - configName - name of application config file
  # @return config - config parser
  def __initApp(self, configName=None):

    if configName is None:
      configName = self.pargs.config
    else:
      pass

    config, confLogFileName, scraperPropertyFileName = self.__loadAppConfig(configName)

    self.properties = self.__loadScraperProperties(scraperPropertyFileName)

    if self.logger is None:
      self.__loadLogConfig(confLogFileName)
    else:
      pass

    self.logger.info('self.properties: ' + varDump(self.properties))

    return config


  # #loads scraper propeties from json file
  #
  # @param scraperPropertyFileName - input scraper property json file
  # @return properties - extracted property
  def __loadScraperProperties(self, scraperPropertyFileName):
    # variable for result
    properties = None
    if scraperPropertyFileName is not None:
      try:
        with open(scraperPropertyFileName, "rb") as fd:
          scraperProperies = json.loads(fd.read())
          properties = scraperProperies[self.__class__.__name__][CONSTS.PROPERTIES_KEY]
      except Exception, err:
        if self.logger is not None:
          self.logger.error(self.MSG_ERROR_LOAD_PROPERTIES_FROM_FILE + " '" + \
                          str(scraperPropertyFileName) + "': " + str(err))

    return properties


  # #load application config file
  #
  # @param configName - name of application config file
  # @return config - config parser
  # @return confLogFileName - log config file name,
  # @return scraperPropertyFileName - input scraper property file name,
  def __loadAppConfig(self, configName):
    # variables for result
    confLogFileName = ''
    scraperPropertyFileName = ''
    try:
      if configName is None or configName == "":
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        confLogFileName = Utils.getConfigParameter(config, APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, \
                                                   self.SCRAPER_MULTI_ITEMS_OPTION_LOG, '')

        scraperPropertyFileName = Utils.getConfigParameter(config, APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, \
                                                   self.SCRAPER_MULTI_ITEMS_OPTION_PROPERTY_JSON_FILE, '')

      self.useCurrentYear = config.getint("DateTimeType", "useCurrentYear")

      if config.has_section(self.OPTION_SECTION_DATETIME_TEMPLATE_TYPES):
        self.datetimeTemplateTypes = []
        for key, value in config.items(self.OPTION_SECTION_DATETIME_TEMPLATE_TYPES):
          self.datetimeTemplateTypes.append(key)
          if self.logger is not None:
            self.logger.debug('load form config: ' + str(key) + ' = ' + str(value))
      else:
        self.datetimeTemplateTypes = self.TAGS_DATETIME_TEMPLATE_TYPES
        if self.logger is not None:
          self.logger.debug("Config file hasn't section: " + str(self.OPTION_SECTION_DATETIME_TEMPLATE_TYPES))

      # DBWrapper initialization
      dbTaskIniConfigFileName = config.get(self.__class__.__name__, "db-task_ini")
      readOk = config.read(dbTaskIniConfigFileName)
      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + dbTaskIniConfigFileName)
      self.dbWrapper = DBTasksWrapper(config)
    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return config, confLogFileName, scraperPropertyFileName


  # #load log config file
  #
  # @param configName - name of log scraper multi items config file
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


  # # get exist extractor use extractor name
  #
  # @param extractorName - extractor name
  # @return instance of extractor or None
  def getExtractorByName(self, extractorName):
    for extractor in self.extractors:
      if extractor.__class__.__name__ == extractorName:
        return extractor
    # in case if not found
    return None


  # # get exit code og application
  def getExitCode(self):
    return self.exitCode


  # # get input data from stdin
  #
  # @param - None
  # @return inputData - input data read from stdin
  def __getInputData(self):
    # variable for result
    scraperInputData = None
    try:
      # read pickled object from stdin and extract it
      scraperInputData = pickle.loads(sys.stdin.read())
    except Exception, err:
      if self.logger is not None:
        ExceptionLog.handler(self.logger, err, self.MSG_ERROR_READ_INPUT_DATA)
      else:
        pass
      raise Exception(self.MSG_ERROR_READ_INPUT_DATA + ' ' + str(err))

    return scraperInputData


  # # check input data
  #
  # @param inputData - input data
  # @return - None
  def __checkInputData(self, inputData):

    if inputData is None:
      raise Exception(self.MSG_ERROR_INPUT_DATA_NONE)

    if inputData.batch_item is None:
      raise Exception(self.MSG_ERROR_INPUT_DATA_WITHOUT_BATCH)

    if inputData.batch_item.properties is None:
      raise Exception(self.MSG_ERROR_INPUT_DATA_WITHOUT_PROPERTIES)



  # # fill profiler message list from input data
  #
  # @param inputData - input data
  # @return - None
  def __fillProfilerMessageList(self, inputData):

    if inputData.batch_item.urlObj is not None:
      urlString = inputData.batch_item.urlObj.url
    else:
      urlString = ""
    logMsg = "BatchItem.siteId=" + str(inputData.batch_item.siteId) + \
             ", BatchItem.urlId=" + str(inputData.batch_item.urlId) + \
             ", BatchItem.urlObj.url=" + urlString
    app.Profiler.messagesList.append(logMsg)
    self.logger.info("Incoming data: %s", logMsg)


  # # get output format from input data
  #
  # @param inputData - input data
  # @return outputFormat - output format data
  def __getOutputFormat(self, inputData):
    # variable for result
    outputFormat = None

    if inputData.output_format is not None and "name" in inputData.output_format:
      outputFormat = inputData.output_format["name"]

    if outputFormat is None and "templates" in inputData.batch_item.properties["template"] and \
          len(inputData.batch_item.properties["template"]["templates"]) > 0 and \
          "output_format" in inputData.batch_item.properties["template"]["templates"][0] and \
          "name" in inputData.batch_item.properties["template"]["templates"][0]["output_format"]:
      outputFormat = inputData.batch_item.properties["template"]["templates"][0]["output_format"]["name"]
    else:
      self.logger.debug(">>> 'output_format' hasn't in template of input batch.")

    return outputFormat


  # # get alt tags mask as property from input data
  #
  # @param inputData - input data
  # @return altTagsMask - alt tags mask from input data
  def __getAltTagsMask(self, inputData):
    # variable for result
    altTagsMask = None
    if "TAGS_MAPPING" in inputData.batch_item.properties and \
      inputData.batch_item.properties["TAGS_MAPPING"] is not None:
      try:
        altTagsMask = json.loads(inputData.batch_item.properties["TAGS_MAPPING"])
        self.logger.debug(">>> AltTagsMask = " + str(altTagsMask))
      except Exception, err:
        ExceptionLog.handler(self.logger, err, 'Bad TAGS_MAPPING properties value:', \
                             (inputData.batch_item.properties["TAGS_MAPPING"]), \
                             {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})

    return altTagsMask



  # # get properties from input data
  #
  # @param inputData - input data
  # @return properties - properties loaded from input data
  def __getPropertiesFromInputData(self, inputData):
    # variable for result
    properties = {}
    try:
      if (self.input_data is not None) and \
        inputData.processor_properties is not None:
        processor_properties = inputData.processor_properties
        self.logger.debug("Processor's properties was taken from input data: %s" % processor_properties)
        self.logger.debug("Processor's properties type: %s" % str(type(processor_properties)))
        if not isinstance(processor_properties, dict):
          processor_properties = json.loads(inputData.processor_properties)
        self.logger.debug("Processor's properties was taken from input data: %s" % processor_properties)
        properties = processor_properties

        self.logger.debug('>>> inputData.batch_item.properties: ' + varDump(inputData.batch_item.properties) + \
                          ' type: ' + str(type(inputData.batch_item.properties)))
        if isinstance(inputData.batch_item.properties, dict):
          properties.update(inputData.batch_item.properties)

    except Exception, err:
      ExceptionLog.handler(self.logger, err, self.MSG_ERROR_GET_PROPERTIES, (inputData.processor_properties))

    return properties


  # # load extractors
  #
  # @param algorithmName - name of algorithm used for extraction
  # @param config - config parser
  # @param urlHost - url of host
  # @return - None
  def __loadExtractors(self, algorithmName, config, urlHost):
    # varable for result
    extractors = []
    try:
      # modules
      modules = self.properties[CONSTS.MODULES_KEY][algorithmName]

      self.logger.debug("Algorithm name: <%s>" % (algorithmName))
      self.logger.debug("Modules: %s" % modules)

      for module in modules:
        exrtactor = self.__createModule(module, config, urlHost)
        # Check if module was created successfully and then insert it to extractors
        if exrtactor is not None:
          extractors.append(exrtactor)

      # Info show extractors loaded
      self.logger.debug("*******************")
      self.logger.debug("Loaded extractors:")
      for extractor in extractors:
        self.logger.debug(extractor.name)
      self.logger.debug("*******************")

    except Exception, err:
      ExceptionLog.handler(self.logger, err, self.MSG_ERROR_LOAD_EXTRACTORS)
      raise Exception(self.MSG_ERROR_LOAD_EXTRACTORS + ' ' + str(err))

    return extractors


  # # create module
  #
  # @param moduleName - modules name which instance will be created
  # @param config - config parser
  # @param urlHost - url of host
  # @return appInst - instance of created application
  def __createModule(self, moduleName, config, urlHost):
    # varable for result
    appInst = None
    try:
      appInst = (moduleName, eval(moduleName)(config, None, urlHost))[1]  # pylint: disable=W0123
      self.logger.debug("%s has been created!" % moduleName)
    except Exception, err:
      ExceptionLog.handler(self.logger, err, "Can't create module %s. Error is:" % (moduleName))

    return appInst



#   # #adjust partial references
#   # adjust partial references
#   #
#   def checkDOMElement(self, elem):
#     ret = False
#     if re.search('<', elem):
#       self.logger.debug("Media tag contain DOM element: %s", elem)
#       ret = True
#     return ret


#   # #adjust partial references
#   # adjust partial references
#   #
#   def adjustPartialReferences(self, response):
#     if "links" in response.tags and isinstance(response.tags["link"], dict) and \
#       "media" in response.tags and isinstance(response.tags["media"], dict):
#       try:
#         url = None
#         if self.input_data.template and "link" in self.input_data.template:
#           self.logger.debug("url type: %s", str(type(response.tags["link"]["data"])))
#           if isinstance(response.tags["link"]["data"], str) or isinstance(response.tags["link"]["data"], unicode):
#             url = response.tags["link"]["data"]
#           else:
#             url = response.tags["link"]["data"][0]
#         else:
#           url = self.input_data.url
#         if self.input_data.template and "media" in self.input_data.template:
#           self.logger.debug("resource has template with media tag. Try to adjust media.")
#           # if type(response.tags["media"]) == str and response.tags["media"] == "": return
#           self.logger.debug("response.tags['media']: " + str(response.tags["media"]))
#           self.logger.debug("media tag in response: <<%s>>" % str(response.tags["media"]["data"]))
#           self.logger.debug("link tag in response: <<%s>>" % str(url))
#           res = []
#
#           filter_patterns, filter_types = [], []
#           if self.input_data.filters:
#             # filter_types = [filter_item["Type"] for filter_item in self.input_data.filters]
#             # filter_patterns = [re.compile(filter_item["Pattern"]) for filter_item in self.input_data.filters]
#             filter_types = [filter_item.type for filter_item in self.input_data.filters]
#             filter_patterns = [re.compile(filter_item.pattern) for filter_item in self.input_data.filters]
#           self.logger.debug("filter: %s" % (str(self.input_data.filters)))
#           for media in response.tags["media"]["data"]:
#             self.logger.debug("Media link: <<%s>>", media)
#             # instead pure url
#             if self.checkDOMElement(media):
#               res.append(media)
#               break
#             media = urlparse.urljoin(url, media)
#             for filter_type, filter_pattern in zip(filter_types, filter_patterns):
#               match = filter_pattern.match(media)
#               if filter_type == SiteFilter.TYPE_EXCLUDE and match:
#                 break
#               if filter_type == SiteFilter.TYPE_INCLUDE and match:
#                 res = self.checkMediaTag(media, res)
#                 break
#             else:
#               self.logger.debug("media: %s", media)
#               self.logger.debug("url: %s", url)
#               res = self.checkMediaTag(media, res)
#
#           # If media tag after adjusting is empty remove it from response
#           if not len(res):
#             self.logger.debug("media tag is empty. Remove media tag from response.")
#             del response.tags["media"]
#           else:
#             self.logger.debug("media tag is adjusted. Copy media tag to response.")
#             response.tags["media"]["data"] = res
#           # End code block removing empty media tag
#         else:
#           self.logger.debug("resource hasn't template with media tag. adjustPartialReferences doesn't execute")
#       except Exception as err:
#         ExceptionLog.handler(self.logger, err, self.MSG_ERROR_ADJUST_PR, (err), \
#                              {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
#     else:
#       self.logger.debug(">>> Response has not have link or media tag, Don't need adjust media")


#   # adjustTitle
#   #
#   def adjustTitle(self, response):
#     try:
#       if self.input_data.template and "title" in self.input_data.template:
#         self.logger.debug("resource has template with title tag. Try to adjust title.")
#         self.logger.debug("response.tags['title']: " + str(response.tags["title"]))
#         if not self.extractor:
#           if len(self.extractors) > 2:
#             self.extractor = self.extractors[2]
#           else:
#             raise Exception(" >>> Wrong! self.extractors list doesn't have 3'th element (index 2)")
#         if isinstance(response.tags["title"], str):
#           self.logger.debug("response has not have title tag")
#           sel = Selector(text=self.input_data.raw_content)
#           title = sel.xpath("//title/text()").extract()
#           self.extractor.addTag(result=response, tag_name="title", tag_value=title, xpath="", \
#                                  isDefaultTag=False, callAdjustment=True, tagType=None, allowNotFilled=True)
#         self.logger.debug("TYPE response.tags['title']['data']" + str(type(response.tags["title"]["data"])))
#       else:
#         self.logger.debug("resource hasn't template with title tag. Don't need adjust title.")
#     except Exception as err:
#       ExceptionLog.handler(self.logger, err, self.MSG_ERROR_ADJUST_TITLE, (err), \
#                              {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})


#   # adjustLinkURL
#   #
#   def adjustLinkURL(self, response):
#     flag = False
#     try:
#       if response.tags and "link" in response.tags:
#         self.logger.debug("resource has template with link tag. Try to adjust link.")
#         self.logger.debug("response.tags['link']: " + str(response.tags["link"]))
#         self.logger.debug("self.extractor: %s", str(self.extractor))
#         flag = True
#         if self.extractor:
#           self.logger.debug("Extractor exists")
#           if isinstance(response.tags["link"], str):
#             self.logger.debug("response has not have link tag")
#             self.extractor.addTag(result=response, tag_name="link", tag_value=[self.input_data.url], xpath="", \
#                                   isDefaultTag=False, callAdjustment=True, tagType=None, allowNotFilled=True)
#           # bypass
#           else:
#             response.tags["link"]["data"] = self.input_data.url
#         else:
#           if len(self.extractors) > 2:
#             self.extractors[2].addTag(result=response, tag_name="link", tag_value=[self.input_data.url], xpath="", \
#                                       isDefaultTag=False, callAdjustment=True, tagType=None, allowNotFilled=True)
#           else:
#             self.logger.debug(">>> Wrong! self.extractors list doesn't have 3'th element (index 2)")
#         self.logger.debug("TYPE response.tags['link']['data']" + str(type(response.tags["link"]["data"])))
#       else:
#         self.logger.debug("resource hasn't template with link tag. Don't need adjust link.")
#     except Exception as err:
#       ExceptionLog.handler(self.logger, err, self.MSG_ERROR_ADJUST_LINK_URL, (err), \
#                              {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
#
#     return flag


#   # # Normalize datetime tags procedure
#   #
#   # @param response - scraper response instance
#   # @param algorithmName - algorithm name
#   # @return - 'pubdate tag value'
#   def normalizeDatetime(self, response, algorithmName):
#     ret = None
#     timezone = ''
#     try:
#       if response is not None and response.tags is not None:
#         self.logger.debug("normalizeDatetime scraper response: " + varDump(response))
#         tagNames = []
#         if self.input_data.template and algorithmName == CONSTS.PROCESS_ALGORITHM_REGULAR:
#           # temlate
#           for responseType in self.datetimeTemplateTypes:
#             for responseTagName in response.tags:
#               self.logger.debug("normalizeDatetime responseTagName: '" + str(responseTagName) + "'")
#               if (responseTagName in response.tags and \
#               response.tags[responseTagName] is not None and \
#               response.tags[responseTagName].has_key('type') and \
#               response.tags[responseTagName]['type'] == responseType) or \
#               (responseTagName in response.tags and response.tags[responseTagName] is not None and \
#               responseTagName == CONSTS.TAG_PUB_DATE):
#                 tagNames.append(responseTagName)
#               else:
#                 pass
#         else:
#           pass
#
#         self.logger.debug('normalizeDatetime  tagNames: ' + varDump(tagNames))
#         retDict = {}
#         for tagName in tagNames:
#           pubdate, tzone = self.extractPubDate(response, tagName)  # , properties, urlString)
#           if self.extractor and tagName in response.tags:
#             self.extractor.addTag(result=response, tag_name=tagName + '_normalized', tag_value=pubdate, \
#                                   xpath=response.tags[tagName]['xpath'], isDefaultTag=False, \
#                                   callAdjustment=True, tagType=None, allowNotFilled=True)
#
#           self.logger.debug('tagName: ' + str(tagName) + ' pubdate: ' + str(pubdate))
#           retDict[tagName] = pubdate
#
#           if tagName == CONSTS.TAG_PUB_DATE:
#             ret = pubdate
#             timezone = tzone
#           else:
#             pass
#
#         if ret is None:
#           for key, value in retDict.items():
#             if value is not None:
#               ret = value
#               self.logger.debug('set return value from ' + str(key) + ' : ' + str(value))
#               break
#
#     except Exception, err:
#       ExceptionLog.handler(self.logger, err, 'normalizeDatetime error:', (), \
#                              {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
#
#     return ret, timezone


#   # # Extract pubdate
#   #
#   # @param response - response instance
#   # @param dataTagName - tag name for extracting
#   # @param properties - properties from PROCESSOR_PROPERTIES
#   # @param urlString - url string value
#   # @return pubdate if success or None
#   def extractPubDate(self, response, dataTagName):  # , properties, urlString):
#     # variable for result
#     ret = None
#     timezone = ''
#     try:
#       if response is not None and dataTagName in response.tags and response.tags[dataTagName] != "":
#
#         self.logger.debug("extractPubDate response: " + varDump(response))
#
#         if dataTagName in response.tags and response.tags[dataTagName] is not None:
#           inputData = response.tags[dataTagName]["data"]
#           self.logger.debug("extractPubDate response has '" + str(dataTagName) + "' is: " + str(inputData))
#           self.logger.debug("extractPubDate type of '" + str(dataTagName) + "' is: " + str(type(inputData)))
#
#           inputList = []
#           if isinstance(inputData, str) or isinstance(inputData, unicode):
#             inputList = [inputData]
#           elif isinstance(inputData, list):
#             inputList = inputData
#           else:
#             pass
#
#           pubdate = []
#           timezones = []
#           for inputElem in inputList:
#             d = DateTimeType.parse(inputElem, bool(self.useCurrentYear), self.logger, False)
#             self.logger.debug('pubdate: ' + str(d))
#
#             if d is not None:
#               d, tzone = DateTimeType.split(d)
#               pubdate.append(d.isoformat(DateTimeType.ISO_SEP))
#               timezones.append(tzone)
#
#           self.logger.debug("extractPubDate result pubdate: " + str(pubdate))
#           response.tags[dataTagName]["data"] = pubdate
#           if len(pubdate) > 0:
#             ret = pubdate[0]
#
#           if len(timezones) > 0:
#             timezone = timezones[0]
#
#     except Exception, err:
#       ExceptionLog.handler(self.logger, err, 'extractPubDate error:', (), \
#                              {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
#
#     return ret, timezone


#   # # pubdate transformation use timezone value
#   #
#   # @param rawPubdate - raw pubdate string
#   # @param rawTimezone - raw timezone string
#   # @param properties - properties from PROCESSOR_PROPERTIES
#   # @param urlString - url string value
#   # @return pubdate and timezone if success or None and empty string
#   def pubdateTransform(self, rawPubdate, rawTimezone, properties, urlString):
#     # variables for result
#     pubdate = rawPubdate
#     timezone = rawTimezone
#
#     self.logger.debug('properties: ' + varDump(properties))
#     if CONSTS.PDATE_TIMEZONES_NAME in properties:
#       propertyString = properties[CONSTS.PDATE_TIMEZONES_NAME]
#       self.logger.debug('inputted ' + CONSTS.PDATE_TIMEZONES_NAME + ':' + str(propertyString))
#
#       dt = DateTimeType.parse(rawPubdate, bool(self.useCurrentYear), self.logger, False)
#       self.logger.debug('pubdate: ' + str(dt))
#       if dt is not None:
#         # get utc offset if necessary
#         utcOffset = DateTimeType.extractUtcOffset(rawTimezone, self.logger)
#         self.logger.debug('utcOffset: ' + str(utcOffset))
#         # transformation accord to PDATE_TIMEZONES properties
#         d = PDateTimezonesHandler.transform(dt, utcOffset, propertyString, urlString, self.logger)
#         if d is not None:
#           dt = d
#
#       if dt is not None:
#         d, tzone = DateTimeType.split(dt)
#         pubdate = d.isoformat(DateTimeType.ISO_SEP)
#         timezone = tzone
#
#     return pubdate, timezone


  # # refineBadDateTags, deleles, from result, datetime tags with bad datetime value.
  #
  def refineBadDateTags(self, response):
    removeKeys = []
    for key in response.tags:
      if key in self.DATA_NEWS_TAGS:
        tagsValue = None

        if isinstance(response.tags[key], str) or isinstance(response.tags[key], unicode):
          tagsValue = response.tags[key]
        elif isinstance(response.tags[key], dict) and "data" in response.tags[key]:
          if isinstance(response.tags[key]["data"], str) or isinstance(response.tags[key]["data"], unicode):
            tagsValue = response.tags[key]["data"]
          elif isinstance(response.tags[key]["data"], list) and len(response.tags[key]["data"]) > 0 and \
          isinstance(response.tags[key]["data"][0], str) or isinstance(response.tags[key]["data"][0], unicode):
            tagsValue = response.tags[key]["data"][0]

        if tagsValue is not None:
          try:
            dt = parser.parse(tagsValue)
            int(time.mktime(dt.timetuple()))
          except Exception:
            removeKeys.append(key)

    for key in removeKeys:
      if key in response.tags:
        logging.debug(">>> Remove " + key + " element besause it empty")
        del response.tags[key]


  def preparseResponse(self, response):
    self.logger.debug('>>> preparseResponse enter <<<')

    for key in response.tags:
      if response.tags[key] is not None:
        if "data" in response.tags[key]:
          if isinstance(response.tags[key]["data"], str) or isinstance(response.tags[key]["data"], unicode):
            localStr = response.tags[key]["data"]

            self.logger.debug('-----------------------------------------')
            self.logger.debug('key: ' + str(key) + ' => ' + str(localStr))
            self.logger.debug('-----------------------------------------')

            response.tags[key]["data"] = []
            response.tags[key]["data"].append(localStr)

            self.logger.debug('response.tags[key]["data"]: ' + str(response.tags[key]["data"]))
            self.logger.debug('-----------------------------------------')


  def formatOutpuElement(self, elem, localOutputFormat):
    ret = elem
    if localOutputFormat == "json":
      # self.logger.debug(">>> JSON HTML = " + elem)
      localStr = json.dumps(elem, ensure_ascii=False)
      if localStr[0] == '\"' or localStr[0] == '\'':
        localStr = localStr[1:]
      if localStr[-1] == '\"' or localStr[-1] == '\'':
        localStr = localStr[0:-1]
      ret = localStr
      # self.logger.debug(">>> JSON HTML = " + ret)
    elif localOutputFormat == "html":
      ret = xml.sax.saxutils.escape(elem, {"'": "&apos;", "\"" : "&quot;"})
    elif localOutputFormat == "sql":
      # ret = mdb.escape_string(elem)  # pylint: disable=E1101
      ret = Utils.escape(elem)
    return ret


  def formatOutputData(self, response, localOutputFormat):
    # result.tags[key]["data"]
    for key in response.tags:
      if response.tags[key] is not None:
        if "data" in response.tags[key]:
          if isinstance(response.tags[key]["data"], list):
            for i, elem in enumerate(response.tags[key]["data"]):
              response.tags[key]["data"][i] = self.formatOutpuElement(elem, localOutputFormat)
          elif isinstance(response.tags[key]["data"], str) or isinstance(response.tags[key]["data"], unicode):
            response.tags[key]["data"] = self.formatOutpuElement(response.tags[key]["data"], localOutputFormat)


  # # template extraction processing
  #
  # @param config - config parser
  # @param urlHost - domain name
  # @return resultsList - list of Result
  def templateExtraction(self, config, urlHost):
    self.extractor = ScrapyExtractor(config, self.input_data.template, urlHost)
    sel = Selector(text=self.input_data.raw_content)
    if isinstance(self.input_data.template, dict):
      template = self.input_data.template
    else:
      # template = ast.literal_eval(self.input_data.template)
      # TODO:strange potential backdoor for malicious code, cancelled by bgv
      pass

    # Calculate mandatory properties for exist tags
    mandatoryTags = {}
    for key, value in template.items():
      isMandatory = True
      self.logger.debug(">>> Calculate mandatory for '" + str(key) + "'")
      for elem in value:
        self.logger.debug(">>> mandatory = " + str(elem["mandatory"]) + " type: " + str(type(elem["mandatory"])))
        if bool(elem["mandatory"]) is False:
          isMandatory = False
          continue

      mandatoryTags[key] = isMandatory

    self.logger.debug(">>> Calculated mandatoryTags: " + varDump(mandatoryTags))

    scraperDocs = ScraperResultDocuments(template.keys(), self.input_data.urlId)

    # Add End
    for key in template:
      self.logger.debug(">>> Template key: " + key)
      if "state" in template[key] and not bool(int(template[key]["state"])):
        self.logger.debug(">>> Template disable: template name = " + str(key))
        continue
      for path in template[key]:
        if not isinstance(path, dict):
          self.logger.debug(">>> WARNING path not DICT type ")
          continue

        isExtract = True
        localResult = Result(None, self.input_data.urlId)
        # Added new template format conversion
        xpath = None
        xpathValue = None

        # Logging xPath trees
        self.logger.debug(">>> Logging xPath trees for key: '" + str(key) + "'")
        etrees = sel.xpath(path['target'])
        for etree in etrees:

          self.logger.debug(">>> etree: " + varDump(etree))
          if isinstance(etree._root, basestring):  # pylint: disable=W0212
            continue

          etreeValue = self.get_path(etree._root)  # pylint: disable=W0212
          self.logger.debug('>>> etreeValue: ' + varDump(etreeValue))
          scraperDocs.addEtree(key, copy.deepcopy(etreeValue))

        # Added new template type specification
        xPathPreparing = TemplateExtractorXPathPreparing(self.properties[CONSTS.TAG_MARKUP_PROP_NAME] \
                                                      if CONSTS.TAG_MARKUP_PROP_NAME in self.properties else None)

        self.logger.debug(">>> xPathPreparing: " + varDump(xPathPreparing))
        self.logger.debug(">>> path: " + varDump(path))
        self.logger.debug(">>> sel: " + varDump(sel))

        self.logger.debug(">>> self.properties: " + varDump(self.properties))
        # Added new template type specification
        self.xpathSplitString = xPathPreparing.resolveDelimiter(path, self.properties, self.xpathSplitString)
        innerDelimiter = xPathPreparing.resolveInnerDelimiter(path, self.properties)
        self.logger.debug(">>> xpathSplitString: '" + str(self.xpathSplitString) + "'")
        self.logger.debug(">>> innerDelimiter: '" + str(innerDelimiter) + "'")
        try:
          xpath, xpathValue = xPathPreparing.process(path, sel, self.xpathSplitString, innerDelimiter,
                                                     Utils.innerTextToList)
        except Exception, err:
          ExceptionLog.handler(self.logger, err, "some rule/xpath exception:", (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
          continue

        self.logger.debug(">>> xpathValue " + str(type(xpathValue)) + " " + str(xpathValue))
        self.logger.debug(">>> xpath: %s" % str(xpath))
        if (isinstance(xpathValue, list) and len(xpathValue) == 0) or\
        (isinstance(xpathValue, basestring) and xpathValue == ''):
          self.logger.debug(">>> set default xpathValue")
          xpathValue = []
          xpathValue.append(path["default"])
          isExtract = False

        if not isinstance(xpathValue, list):
          xpathValue = [xpathValue]

        for xpathElem in xpathValue:
          elemResult = copy.deepcopy(localResult)
          self.logger.debug("result before:\n%s", varDump(elemResult))
          self.extractor.addTag(result=elemResult, tag_name=key, tag_value=xpathElem, xpath=xpath,
                                isDefaultTag=(not isExtract), callAdjustment=False, tagType=path["type"],
                                allowNotFilled=True)

          self.logger.debug("result after:\n%s", varDump(elemResult))

          self.logger.debug(">>> tag type = " + str(type(elemResult.tags)))
          self.logger.debug(">>> tags data type = " + str(type(elemResult.tags[key]["data"])))

          if key in elemResult.tags and isinstance(elemResult.tags[key]["data"], basestring):
            self.logger.debug(">>> Convert result = " + str(key))
            localString = elemResult.tags[key]["data"]
            elemResult.tags[key]["data"] = []
            elemResult.tags[key]["data"].append(localString)

          if isExtract and "postProcessing" in path and path["postProcessing"] is not None and \
          path["postProcessing"] != "":
            self.applyPostProcessing(elemResult, key, path["postProcessing"])


          self.logger.debug("scraperDocs.addDoc key: " + str(key) + ' mandatory = ' + varDump(mandatoryTags[key]))

          scraperDocs.addDoc(key, elemResult, path["join"], isExtract,
                             (bool(path["mandatory"]) if "mandatory" in path else False))

    # for response
    resultsList = []
    resultDocs = scraperDocs.getAllDocs(mandatoryTags, self.logger)

    for elem in resultDocs:
      result = Result(None, self.input_data.urlId)
      # Add tag 'order_number'
      self.addCustomTag(result=result, tag_name=CONSTS.TAG_ORDER_NUMBER, \
                             tag_value=str(elem[CONSTS.TAG_ORDER_NUMBER]))
      # Add tag 'source_url'
      self.addCustomTag(result=result, tag_name=CONSTS.TAG_SOURCE_URL, \
                        tag_value=[self.input_data.url])

      # Prepare result
      prepareResultsList = self.prepareResults([elem])
      self.compileResults(result, prepareResultsList, key, xPathPreparing)
      result.finish = time.time()
      resultsList.append(copy.deepcopy(result))

    return resultsList


#   # # Add custom tag
#   #
#   # @param result - Scrper result instance
#   # @param tag_name - value name of tag
#   # @param tag_value - value value of tag
#   # @return - None
#   def addCustomTag(self, result, tag_name, tag_value):
#     data = {"extractor": "Base extractor", "data": "", "name": ""}
#     data["data"] = tag_value
#     data["name"] = tag_name
#     data["xpath"] = None
#     data["type"] = None
#     data["extractor"] = self.__class__.__name__
#     result.tags[tag_name] = data


#   def compileResults(self, result, resultsList, key, xPathPreparing=None):
#     for elem in resultsList:
#       if key in result.tags:
#         if result.tags[key] is not None:
#           if result.tags[key]["xpath"] is None:
#             result.tags[key]["xpath"] = elem["obj"].tags[key]["xpath"]
#           else:
#             result.tags[key]["xpath"] += ' '
#             result.tags[key]["xpath"] += elem["obj"].tags[key]["xpath"]
#           if result.tags[key]["data"] is None or len(result.tags[key]["data"]) == 0:
#             result.tags[key]["data"] = elem["obj"].tags[key]["data"]
#           else:
#             if xPathPreparing is not None:
#               self.xpathSplitString = xPathPreparing.resolveDelimiter(elem, self.properties, self.xpathSplitString)
#               result.tags[key]["data"][0] += self.xpathSplitString
#             else:
#               result.tags[key]["data"][0] += ' '
#             result.tags[key]["data"][0] += elem["obj"].tags[key]["data"][0]
#       else:
#         result.tags.update(elem["obj"].tags)


#   def prepareResults(self, resultsList):
#     ret = []
#     if len(resultsList) > 0:
#       localElemWeight = 0
#       firstElemWeight = 0
#       firstElem = None
#       tempList = []
#       for elem in resultsList:
#         localElemWeight = 0
#         if elem["join"] == "concat":
#           tempList.append(elem)
#         else:
#           if elem["mandatory"]:
#             #>>> Mandatory breaking block -------------
#             if not elem["isExtract"]:
#               return []
#             #-------------
#             localElemWeight = localElemWeight | CONSTS.TAGS_RULES_MASK_MANDATORY_FIELD
#           if elem["join"] == "best":
#             localElemWeight = localElemWeight | CONSTS.TAGS_RULES_MASK_RULE_PRIORITY
#           if elem["isExtract"]:
#             localElemWeight = localElemWeight | CONSTS.TAGS_RULES_MASK_DEFAULT_VALUE
#
#           self.logger.debug(">>> Rule weight = " + str(localElemWeight))
#           self.logger.debug(">>> Rule join = " + elem["join"])
#           if localElemWeight > firstElemWeight:
#             firstElemWeight = localElemWeight
#             firstElem = elem
#
#       if firstElem is not None:
#         tempList = [firstElem] + tempList
#       isExtractResults = any([elem["isExtract"] for elem in tempList])
#       if isExtractResults:
#         ret = [elem for elem in tempList if elem["isExtract"]]
#       else:
#         ret.append(tempList[0])
#     return ret


  def applyPostProcessing(self, result, key, postProcessingRE):
    if key in result.tags and "data" in result.tags[key] and result.tags[key]["data"] is not None and \
    len(result.tags[key]["data"]) > 0:
      try:
        matchingVal = re.compile(postProcessingRE)
      except re.error as err:
        self.logger.debug(">>> RE error = " + str(err))
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_RE_ERROR
      else:
        tmpStr = ""
        matchingResult = matchingVal.findall(result.tags[key]["data"][0])
        if matchingResult is not None:
          for elem in matchingResult:
            if isinstance(elem, str) or isinstance(elem, unicode):
              tmpStr += str(elem)
              tmpStr += ' '
            else:
              for innerElem in elem:
                if innerElem is not None and innerElem != '':
                  tmpStr += str(innerElem)
                  tmpStr += ' '
        tmpStr = tmpStr.strip()
        if tmpStr != "":
          self.logger.debug(">>> Replace value, prev. value is = " + result.tags[key]["data"][0])
          result.tags[key]["data"][0] = tmpStr
        else:
          # Set not detected value if no match, changed default behavior by bgv
          result.tags[key]["data"][0] = None


  def getProcessedContent(self, result):
    result.get()
    processedContent = {}
    processedContent["default"] = result
    processedContent["internal"] = [result]
    processedContent["custom"] = []

    if "pubdate" in result.tags and "data" in result.tags["pubdate"] and \
    len(result.tags["pubdate"]["data"]) > 0:
      self.pubdate = result.tags["pubdate"]["data"]
      self.logger.debug('>>>> Set self.pubdate =  ' + str(self.pubdate))

    return processedContent


#   # #Internal method of url's domain crc calculating
#   #
#   # @param url - incoming url
#   def calcUrlDomainCrc(self, url):
#     urlHost = None
#     auth = urlparse.urlsplit(url)[1]
#     if auth is not None:
#       urlHost = (re.search('([^@]*@)?([^:]*):?(.*)', auth).groups())[1]
#       if urlHost is not None and urlHost.find(self.WWW_PREFIX) == 0:
#         urlHost = urlHost[len(self.WWW_PREFIX): len(urlHost)]
#
#     return urlHost


  # # The main processing of the batch object
  #
  # @param config - config parser
  # @return None
  def process(self, config):

    # check recieved input data accord to protocol
    self.__checkInputData(self.input_data)

    self.logger.info('Start processing on BatchItem from Batch: ' + str(self.input_data.batchId))

    # fill profiler message list
    self.__fillProfilerMessageList(self.input_data)
    self.logger.debug("self.inputData:\n%s", varDump(self.input_data))

    # get output data format
    self.outputFormat = self.__getOutputFormat(self.input_data)

    # get alt tags mask as property from input data
    altTagsMask = self.__getAltTagsMask(self.input_data)

    # get property from input data and use in valid case
    properties = self.__getPropertiesFromInputData(self.input_data)
    if properties is not None:
      self.properties = properties

    algorithmName = self.properties[CONSTS.ALGORITHM_KEY][CONSTS.ALGORITHM_NAME_KEY]

    self.logger.debug("Algorithm : %s" % algorithmName)
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      Utils.storePickleOnDisk(self.input_data, self.ENV_SCRAPER_STORE_PATH, "scraper.in." + \
                                 str(self.input_data.urlId))

    tmp = sys.stdout
    sys.stdout = open("/dev/null", "wb")

    # initialization of scraper
    # load scraper's modules


    urlHost = self.calcUrlDomainCrc(self.input_data.url)
    self.logger.info('urlHost: ' + str(urlHost))

    self.extractors = self.__loadExtractors(algorithmName, config, urlHost)


    # log info input data
    self.logger.info("input_data url: %s, urlId: %s, siteId: %s", str(self.input_data.url), str(self.input_data.urlId),
                     str(self.input_data.siteId))
    # self.logger.debug("input_data:\n" + varDump(self.input_data))

    # self.logger.debug("Initialization pubdate from urlObj.pDate use value: %s",
    #                  str(self.input_data.batch_item.urlObj.pDate))
    # self.pubdate = self.input_data.batch_item.urlObj.pDate

    # get iterator to ranked list of extractors
    self.itr = iter(sorted(self.extractors, key=lambda extractor: extractor.rank, reverse=True))
    self.logger.debug("Extractors: %s" % varDump(self.itr))

    # Reconfigure processor's properties to involve only template scraper
    responses = self.templateExtraction(config, urlHost)

    if CONSTS.MEDIA_LIMITS_NAME in self.input_data.batch_item.properties:
      self.logger.debug("Found property '%s'", str(CONSTS.MEDIA_LIMITS_NAME))
      self.mediaLimitsHandler = MediaLimitsHandler(self.input_data.batch_item.properties[CONSTS.MEDIA_LIMITS_NAME])

    # variable for result
    scraperResponseList = []
    for response in responses:
      if response is not None:
        response.stripResult()

      # put extracted article to the db
      if algorithmName != CONSTS.PROCESS_ALGORITHM_REGULAR:
        self.adjustTitle(response)
        self.adjustLinkURL(response)
        self.adjustPartialReferences(response)
        self.logger.debug("PDate: %s" % str(self.input_data.batch_item.urlObj.pDate))
        self.logger.debug("PDate type: %s" % str(type(self.input_data.batch_item.urlObj.pDate)))


      self.preparseResponse(response)

      self.logger.debug('>>>>> self.properties = ' + varDump(self.properties))

      # Setting pubdate in depend of different sources masks
      # default values
      pdateSourceMask = APP_CONSTS.PDATE_SOURCES_MASK_BIT_DEFAULT
      pdateSourceMaskOverwrite = APP_CONSTS.PDATE_SOURCES_MASK_OVERWRITE_DEFAULT

      # get value 'PDATE_SOURCES_MASK' from site properties
      if APP_CONSTS.PDATE_SOURCES_MASK_PROP_NAME in self.input_data.batch_item.properties:
        pdateSourceMask = int(self.input_data.batch_item.properties[APP_CONSTS.PDATE_SOURCES_MASK_PROP_NAME])

      # get value 'PDATE_SOURCES_MASK_OVERWRITE' from site properties
      if APP_CONSTS.PDATE_SOURCES_MASK_OVERWRITE_PROP_NAME in self.input_data.batch_item.properties:
        pdateSourceMaskOverwrite = \
        int(self.input_data.batch_item.properties[APP_CONSTS.PDATE_SOURCES_MASK_OVERWRITE_PROP_NAME])

      self.logger.debug('pdateSourceMask = %s, pdateSourceMaskOverwrite = %s',
                        str(pdateSourceMask), str(pdateSourceMaskOverwrite))

      self.logger.debug("!!! self.input_data.batch_item.urlObj.pDate = " + str(self.input_data.batch_item.urlObj.pDate))

      timezone = ''
      # URL object the "pdate" field (supposed was got from the RSS feed)
      if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_RSS_FEED:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_RSS_FEED) or \
        not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_RSS_FEED:
          self.pubdate, timezone = self.extractPubdateRssFeed(self.input_data.siteId, self.input_data.url)

      # Normalization procedure after the scraping, supposes the tag dc_date for the NEWS or TEMPLATE scraping.
      if CONSTS.TAG_DC_DATE in response.tags and pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_DC_DATE:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_DC_DATE and self.pubdate is None) or \
        not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_DC_DATE:
          if CONSTS.TAG_PUB_DATE not in response.tags or \
          (isinstance(response.tags[CONSTS.TAG_PUB_DATE]["data"], basestring) and \
          response.tags[CONSTS.TAG_PUB_DATE]["data"].strip() == ""):
            response.tags[CONSTS.TAG_PUB_DATE] = copy.deepcopy(response.tags[CONSTS.TAG_DC_DATE])
            response.tags[CONSTS.TAG_PUB_DATE]["name"] = CONSTS.TAG_PUB_DATE
            if len(response.tags[CONSTS.TAG_PUB_DATE]) > 0 and response.tags[CONSTS.TAG_PUB_DATE][0]:
              self.pubdate = response.tags[CONSTS.TAG_PUB_DATE][0]
              self.logger.debug("Pubdate from 'dc_date': " + str(self.pubdate))

      # Normalization procedure after the scraping, supposes the "pubdate" tag for the NEWS or TEMPLATE scraping.
      timezone = ''
      if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_PUBDATE:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_PUBDATE and self.pubdate is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_PUBDATE:
          pubdate, timezone = self.normalizeDatetime(response, algorithmName)
          if pubdate is not None:
            self.pubdate = pubdate
            self.logger.debug("Pubdate from 'pubdate': " + str(self.pubdate))

      # Current date (SQL NOW())
      if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_NOW:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_NOW and self.pubdate is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_NOW:
          self.pubdate = SQLExpression("NOW()")
          self.logger.debug("Pubdate from 'SQL NOW()': " + str(self.pubdate))

      # Custom SQL expression defined in the property PDATE_SOURCES_EXPRESSION
      if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_SQL_EXPRESSION and \
      APP_CONSTS.PDATE_SOURCES_EXPRESSION_PROP_NAME in self.properties:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_SQL_EXPRESSION and self.pubdate is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_SQL_EXPRESSION:
          self.pubdate = SQLExpression(str(self.properties[APP_CONSTS.PDATE_SOURCES_EXPRESSION_PROP_NAME]))
          self.logger.debug("Pubdate from 'sql expression': " + str(self.pubdate))

      # Apply property 'PDATE_DAY_MONTH_ORDER'
      self.pubdate = self.pubdateMonthOrder(self.pubdate, self.input_data.batch_item.properties, self.input_data.url)

      # Apply property 'PDATE_TIME'
      self.input_data.batch_item.urlObj.pDate = self.pubdate
      self.pubdate = FieldsSQLExpressionEvaluator.evaluatePDateTime(self.input_data.batch_item.properties,
                                                                    self.dbWrapper,
                                                                    self.input_data.batch_item.urlObj,
                                                                    self.logger,
                                                                    self.pubdate)

      # Apply property 'PDATE_TIMEZONES'
      self.pubdate, timezone = self.pubdateTransform(self.pubdate,
                                                     timezone,
                                                     self.input_data.batch_item.properties,
                                                     self.input_data.url)

      # Add tag 'pubdate_tz'
      self.addCustomTag(result=response, tag_name=CONSTS.TAG_PUBDATE_TZ, tag_value=[timezone])

      if "pubdate" in response.tags and "data" in response.tags["pubdate"] and \
      len(response.tags["pubdate"]["data"]) > 0:
        response.tags["pubdate"]["data"][0] = self.pubdate

      if self.outputFormat is None:
        self.logger.debug(">>> Warning, can't extract output format")
      else:
        self.formatOutputData(response, self.outputFormat)

      response.recalcTagMaskCount(None, altTagsMask)

      self.logger.debug("response.tagsCount: " + str(response.tagsCount) + \
                        " response.tagsMasks: " + str(response.tagsMask) + \
                        "\n>>> Resp: " + varDump(response))

    # Get start and finish times
    startTime = 0
    if len(responses) > 0:
      startTime = responses[0].start

    finishTime = time.time()
    # recalculate spend time
    for response in responses:
      response.start = startTime
      response.finish = finishTime
      response.data["time"] = "%s" % str(finishTime - startTime)

      response = self.applyHTTPRedirectLink(self.input_data.batch_item.siteId, self.input_data.batch_item.urlObj.url,
                                            self.input_data.batch_item.properties, response)

      # get processed content and append to list of scraper responses
      processedContent = self.getProcessedContent(response)
      scraperResponseList.append(ScraperResponse(response.tagsCount, response.tagsMask, self.pubdate, \
                                                 processedContent, self.errorMask))

    self.logger.debug('len(scraperResponseList): ' + varDump(len(scraperResponseList)))
    self.logger.debug('maxURLsFromPage: ' + str(self.input_data.batch_item.urlObj.maxURLsFromPage))

    # check allowed limits
    if self.input_data.batch_item.urlObj.maxURLsFromPage is not None and \
    int(self.input_data.batch_item.urlObj.maxURLsFromPage) > 0 and \
    int(self.input_data.batch_item.urlObj.maxURLsFromPage) < len(scraperResponseList):
      self.logger.debug('>>> scraperResponseList 1')
      scraperResponseList = scraperResponseList[0: int(self.input_data.batch_item.urlObj.maxURLsFromPage)]
      self.logger.debug('>>> scraperResponseList 2')
      scraperResponseList[-1].errorMask |= APP_CONSTS.ERROR_MAX_URLS_FROM_PAGE
      self.logger.debug("Truncated scraper responces list because over limit 'maxURLsFromPage' = " + \
                        str(self.input_data.batch_item.urlObj.maxURLsFromPage) + " set errorMask = " + \
                        str(APP_CONSTS.ERROR_MAX_URLS_FROM_PAGE))

    # send response to the stdout
    sys.stdout = tmp

    # output result of scraping
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      output_pickled_object = pickle.dumps(scraperResponseList)
      Utils.storePickleOnDisk(output_pickled_object, self.ENV_SCRAPER_STORE_PATH,
                              "scraper.out." + str(self.input_data.urlId))
      print output_pickled_object
      sys.stdout.flush()
    else:
      self.output_data = scraperResponseList
      self.logger.debug('self.output_data: ' + str(varDump(self.output_data)))


  # #get_path returns list of tuples xPath tree
  #
  # @param etreeElement - element of etree
  # @param path - xPath value
  # @return - result list of tuples xPath tree
  def get_path(self, etreeElement, path=None):
    if path is None:
      rpath = []
    else:
      rpath = path

    p = etreeElement.getparent()
    if p is not None:
      index = p.index(etreeElement) + 1
      rpath.insert(0, (etreeElement.tag, str(index)))
      return self.get_path(p, rpath)
    else:
      rpath.insert(0, etreeElement.tag)
      return rpath


#   # # Extract pubdate rss feed from header
#   #
#   # @param siteId - Site/Project ID
#   # @param url - url string
#   # @return pubdate from rss feed
#   def extractPubdateRssFeed(self, siteId, url):
#     # variable for result
#     pubdate = None
#     timezone = ''
#
#     self.logger.debug('!!! extractPubdateRssFeed siteId: ' + str(siteId))
#     self.logger.debug('!!! extractPubdateRssFeed url: ' + str(url))
#     headerContent = self.getHeaderContent(siteId, url)
#     rawPubdate = self.getVariableFromHeaderContent(headerContent, CRAWLER_CONSTS.pubdateRssFeedHeaderName)
#
#     self.logger.debug('!!! getVariableFromHeaderContent: ' + str(rawPubdate))
#     if rawPubdate is not None:
#       try:
#         dt = DateTimeType.parse(rawPubdate, True, self.logger, False)
#         if dt is not None:
#           dt, timezone = DateTimeType.split(dt)
#           pubdate = dt.strftime("%Y-%m-%d %H:%M:%S")
#
#           if timezone is '':
#             timezone = '+0000'
#       except Exception, err:
#         self.logger.debug("Unsupported date format: <%s>, error: %s", str(rawPubdate), str(err))
#
#     return pubdate, timezone


#   # # Get header content
#   #
#   # @param siteId - Site/Project ID
#   # @param url - url string
#   # @return extracted header content
#   def getHeaderContent(self, siteId, url):
#     # variable for result
#     headerContent = None
#     urlContentObj = dc_event.URLContentRequest(siteId, url, \
#                                       dc_event.URLContentRequest.CONTENT_TYPE_RAW_LAST + \
#                                       dc_event.URLContentRequest. CONTENT_TYPE_RAW + \
#                                       dc_event.URLContentRequest.CONTENT_TYPE_HEADERS)
#
#     rawContentData = self.dbWrapper.urlContent([urlContentObj])
#
#     if rawContentData is not None and len(rawContentData) > 0:
#       if rawContentData[0].headers is not None and len(rawContentData[0].headers) > 0 and \
#         rawContentData[0].headers[0] is not None:
#         headerContent = rawContentData[0].headers[0].buffer
#
#     return headerContent
#
#
#   # #Get variable from header content
#   #
#   # @param headerContent - header content
#   # @param name - variable name
#   # @param makeDecode - boolean flag necessary decode
#   # @return extracted value of 'Location'
#   def getVariableFromHeaderContent(self, headerContent, name, makeDecode=True):
#     # variable for result
#     ret = None
#
#     header = ''
#     if makeDecode and headerContent is not None:
#       header = base64.b64decode(headerContent)
#
#     headerList = header.split('\r\n')
#     self.logger.debug("headerList: " + varDump(headerList))
#
#     for elem in headerList:
#       pos = elem.find(name + ':')
#       if pos > -1:
#         ret = elem.replace(name + ':', '').strip()
#         self.logger.debug("Found  '" + name + "' has value: " + str(ret))
#         break
#
#     return ret


#   # # change month orden in pubdate if neccessary
#   #
#   # @param rawPubdate - raw pubdate string in iso format. sample: '2016-02-07 16:28:00'
#   # @param properties - properties from PROCESSOR_PROPERTIES
#   # @param urlString - url string value
#   # @return pubdate and timezone if success or None and empty string
#   def pubdateMonthOrder(self, rawPubdate, properties, urlString):
#     # variables for result
#     pubdate = rawPubdate
#
#     self.logger.debug('pubdateMonthOrder() enter... rawPubdate: ' + str(rawPubdate))
#     if CONSTS.PDATE_DAY_MONTH_ORDER_NAME in properties and isinstance(rawPubdate, basestring):
#       propertyObj = []
#       try:
#         self.logger.debug('inputted ' + CONSTS.PDATE_DAY_MONTH_ORDER_NAME + ':' + \
#                           str(properties[CONSTS.PDATE_DAY_MONTH_ORDER_NAME]))
#         propertyObj = json.loads(properties[CONSTS.PDATE_DAY_MONTH_ORDER_NAME])
#       except Exception, err:
#         self.logger.error("Fail loads '%s', error: %s", str(CONSTS.PDATE_DAY_MONTH_ORDER_NAME), str(err))
#
#       for propertyElem in propertyObj:
#         try:
#           if "pattern" not in propertyElem:
#             raise Exception('Property "pattern" not found')
#
#           if "order" not in propertyElem:
#             raise Exception('Property "order" not found')
#
#           pattern = str(propertyElem["pattern"])
#           order = int(propertyElem["order"])
#
#           if re.search(pattern, urlString, re.UNICODE) is not None:
#             self.logger.debug("Pattern '%' found in url: %s", str(pattern), str(urlString))
#
#             dt = None
#             if order == 0:  # means day follows month
#               dt = datetime.datetime.strptime(rawPubdate, "%Y-%d-%m %H:%M:%S")
#             elif order == 1:  # means month follows day
#               dt = datetime.datetime.strptime(rawPubdate, "%Y-%m-%d %H:%M:%S")
#             else:
#               raise Exception("Unsupported value of 'order' == " + str(order))
#
#             if dt is not None:
#               pubdate = dt.strftime("%Y-%d-%m %H:%M:%S")
#
#         except Exception, err:
#           self.logger.error("Fail execution '%s', error: %s", str(CONSTS.PDATE_DAY_MONTH_ORDER_NAME), str(err))
#
#     self.logger.debug('pubdateMonthOrder() leave... pubdate: ' + str(pubdate))
#
#     return pubdate


#   # # Check media tag and append to list
#   #
#   # @param urlStringMedia - url string of media tag
#   # @param allowedUrls - list for accumulate allowed url strings (by validator and limits)
#   # @return allowedUrls  list already accumulated allowed url strings
#   def checkMediaTag(self, urlStringMedia, allowedUrls):
#
#     mediaUrls = self.splitMediaTagString(urlStringMedia)
#     for media in mediaUrls:
#       # Check if media is binary picture
#       if re.search(MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR, media, re.UNICODE) is not None:
#         self.logger.debug("Tag 'media' has binary picture...")
#
#         if self.mediaLimitsHandler is None:
#           allowedUrls.append(media)
#         else:
#           if self.mediaLimitsHandler.isAllowedLimits(urlString=media, binaryType=True):
#             allowedUrls.append(media)
#           else:
#             self.logger.debug("Binary media tag has not allowed limits. Skipped...")
#
#       # Check is media content valid url
#       elif isValidURL(media):
#         self.logger.debug("Tag 'media' has valid url of picture...")
#         if self.mediaLimitsHandler is None:
#           allowedUrls.append(media)
#         else:
#           if self.mediaLimitsHandler.isAllowedLimits(media):
#             allowedUrls.append(media)
#           else:
#             self.logger.debug("Media tag has not allowed limits. Skipped. Url: %s", str(media))
#
#       # Invalid url of 'media' tag
#       else:
#         self.logger.debug("Invalid url in tag 'media'... Url: %s", str(media))
#
#     return allowedUrls
#
#
#   # # Split media tag string
#   #
#   # @param urlStringMedia - url string of media tag
#   # @return list urls extracted from string of media tag
#   def splitMediaTagString(self, urlStringMedia):
#     # variable for result
#     urls = []
#     # temporary string for replace in url string
#     REPLACE_STR = 'base64|'
#     if urlStringMedia.find(MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR) > -1:
#       urlStringMedia = urlStringMedia.replace(MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR, REPLACE_STR)
#       urls = urlStringMedia.split(',')
#       self.logger.debug("!!! urls before: " + varDump(urls))
#       urls = [url.replace(REPLACE_STR, MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR) for url in urls]
#       self.logger.debug("!!! urls after: " + varDump(urls))
#     else:
#       urls = urlStringMedia.split(',')
#
#     return urls
