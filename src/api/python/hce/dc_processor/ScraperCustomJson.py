# coding: utf-8
'''
Created on Mar 02, 2016

@package: dc_processor
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

# import re
import json
# import base64
import ConfigParser
import logging.config
import types
import sys
import copy
# import datetime
import time
import xml.sax.saxutils
try:
  import cPickle as pickle
except ImportError:
  import pickle
# import MySQLdb as mdb
from cement.core import foundation

# import dc.EventObjects as dc_event
from app.Utils import varDump
import app.Profiler
import app.Utils as Utils
import app.Consts as APP_CONSTS
from app.Utils import ExceptionLog
# from app.DateTimeType import DateTimeType
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
import dc_processor.Constants as CONSTS
from dc_processor.Scraper import Scraper
from dc_processor.ScraperResponse import ScraperResponse
# from dc_processor.PDateTimezonesHandler import PDateTimezonesHandler

from dc_processor.scraper_resource import Resource
from dc_processor.scraper_result import Result as Result
from dc_processor.ScraperLangDetector import ScraperLangDetector

# scraper's modules used via eval()
from dc_processor.newspaper_extractor import NewspaperExtractor  # pylint: disable=W0611
from dc_processor.custom_extractor import CustomExtractor  # pylint: disable=W0611
from dc_processor.goose_extractor import GooseExtractor  # pylint: disable=W0611
from dc_processor.scrapy_extractor import ScrapyExtractor  # pylint: disable=W0611
from dc_processor.ml_extractor import MLExtractor  # pylint: disable=W0611
from dc_crawler.DBTasksWrapper import DBTasksWrapper

# staus code
ERROR_OK = 0

# exit staus code
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

MSG_ERROR_LOAD_EXTRACTORS = "Error load extractors "

ENV_SCRAPER_STORE_PATH = "ENV_SCRAPER_STORE_PATH"

TAGS_DATETIME_NEWS_NAMES = [CONSTS.TAG_PUB_DATE, CONSTS.TAG_DC_DATE]

class ScraperCustomJson(Scraper):  # #foundation.CementApp):

  # # Constants error messages used in class
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  # # Constans used in class
  TAGS_DATETIME_TEMPLATE_TYPES = [CONSTS.TAG_TYPE_DATETIME]
  OPTION_SECTION_DATETIME_TEMPLATE_TYPES = 'tags_datetime_template_types'

  # Mandatory
  class Meta(object):
    label = CONSTS.SCRAPER_CUSTOM_JSON_APP_CLASS_NAME
    def __init__(self):
      pass


  # # Constructor
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
    self.extractor = None
    self.extractors = []
    self.itr = None
    self.pubdate = None
    self.timezone = None
    self.errorMask = APP_CONSTS.ERROR_OK
    self.scraperPropFileName = None
    self.algorithm_name = None
    self.scraperResponses = []
    self.tagsCount = 0
    self.tagsMask = 0
    self.pubdate = None
    self.processedContent = None
    self.outputFormat = None
    self.metrics = None
    self.altTagsMask = None
    self.errorMask = APP_CONSTS.ERROR_OK
    self.urlHost = None
    self.output_data = None
    self.dbWrapper = None
    self.datetimeTemplateTypes = []
    self.useCurrentYear = 0


  # # setup application
  def setup(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class setup method
      foundation.CementApp.setup(self)


  # #run
  # run application
  def run(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class run method
      foundation.CementApp.run(self)

    # config section
    self.loadConfig()

    # load logger config file
    self.loadLogConfigFile()

    # options
    self.loadOptions()

    # scraper properties
    self.loadScraperProperties()

    # Do applied algorithm's job
    self.processBatch()

    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # Finish logging
      self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      self.config = ConfigParser.ConfigParser()
      self.config.optionxform = str
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        if self.pargs.config:
          self.config.read(self.pargs.config)
        else:
          self.config.read(CONSTS.SCRAPER_CUSTOM_JSON_APP_CLASS_NAME)
      else:
        self.config.read(self.configFile)
    except:
      raise


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        log_conf_file = self.config.get("Application", "log")
        logging.config.fileConfig(log_conf_file)
        # Logger initialization
        self.logger = Utils.MPLogger().getLogger()
    except Exception, err:
      raise Exception(CONSTS.MSG_ERROR_LOAD_CONFIG + " : " + str(err))


  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    try:
      # class_name = self.__class__.__name__
      self.scraperPropFileName = self.config.get("Application", "property_file_name")
      # self.config_db_dir = self.config.get(class_name, "config_db_dir")
      # self.sqliteTimeout = self.config.getint("sqlite", "timeout")

      self.useCurrentYear = self.config.getint("DateTimeType", "useCurrentYear")

      if self.config.has_section(self.OPTION_SECTION_DATETIME_TEMPLATE_TYPES):
        self.datetimeTemplateTypes = []
        for key, value in self.config.items(self.OPTION_SECTION_DATETIME_TEMPLATE_TYPES):
          self.datetimeTemplateTypes.append(key)
          if self.logger is not None:
            self.logger.debug('load form config: ' + str(key) + ' = ' + str(value))
      else:
        self.datetimeTemplateTypes = self.TAGS_DATETIME_TEMPLATE_TYPES
        if self.logger is not None:
          self.logger.debug("Config file hasn't section: " + str(self.OPTION_SECTION_DATETIME_TEMPLATE_TYPES))

      # DBWrapper initialization
      dbTaskIniConfigFileName = self.config.get(self.__class__.__name__, "db-task_ini")
      config = ConfigParser.ConfigParser()
      config.optionxform = str
      readOk = config.read(dbTaskIniConfigFileName)
      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + dbTaskIniConfigFileName)
      self.dbWrapper = DBTasksWrapper(config)
    except:
      raise


  # #loadScraperProperties
  # loadScraperProperties loads scraper propeties from json file
  def loadScraperProperties(self):
    if self.scraperPropFileName is not None:
      try:
        with open(self.scraperPropFileName, "rb") as fd:
          scraperProperies = json.loads(fd.read())
          self.properties = scraperProperies[self.__class__.__name__][CONSTS.PROPERTIES_KEY]
      except Exception as excp:
        self.logger.debug(">>> Some error with scraper property loads = " + str(excp))


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # read pickled batch object from stdin
      input_pickled_object = sys.stdin.read()
    try:
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        scraper_in_data = pickle.loads(input_pickled_object)
    except Exception as err:
      ExceptionLog.handler(self.logger, err, 'pickle.loads() error:')
      self.logger.debug("input_pickled_object:\n" + str(input_pickled_object))
      self.exitCode = EXIT_FAILURE
      raise Exception(err)

    try:
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        self.input_data = scraper_in_data
      if self.input_data.batch_item.urlObj is not None:
        urlString = self.input_data.batch_item.urlObj.url
      else:
        urlString = ""
      logMsg = "BatchItem.siteId=" + str(self.input_data.batch_item.siteId) + \
               ", BatchItem.urlId=" + str(self.input_data.batch_item.urlId) + \
               ", BatchItem.urlObj.url=" + urlString
      app.Profiler.messagesList.append(logMsg)
      self.logger.info("Incoming data: %s", logMsg)

      self.urlHost = app.Utils.UrlParser.getDomain(self.input_data.url)


      if self.input_data.output_format is not None and "name" in self.input_data.output_format:
        self.outputFormat = self.input_data.output_format["name"]

      if self.outputFormat is None and "templates" in self.input_data.batch_item.properties["template"] and \
      len(self.input_data.batch_item.properties["template"]["templates"]) > 0 and \
      "output_format" in self.input_data.batch_item.properties["template"]["templates"][0] and \
      "name" in self.input_data.batch_item.properties["template"]["templates"][0]["output_format"]:
        self.outputFormat = self.input_data.batch_item.properties["template"]["templates"][0]["output_format"]["name"]

      if "TAGS_MAPPING" in self.input_data.batch_item.properties and \
      self.input_data.batch_item.properties["TAGS_MAPPING"] is not None:
        try:
          self.altTagsMask = json.loads(self.input_data.batch_item.properties["TAGS_MAPPING"])
          self.logger.debug(">>> AltTags = " + str(self.altTagsMask))
        except Exception as exp:
          self.logger.debug(">>> Bad TAGS_MAPPING properties value, err=" + str(exp))

      try:
        if (self.input_data is not None) and (self.input_data.processor_properties is not None):
          processor_properties = self.input_data.processor_properties
          self.logger.debug("Processor's properties was taken from input data: %s" % processor_properties)
          self.logger.debug("Processor's properties type: %s" % str(type(processor_properties)))
          if not isinstance(processor_properties, types.DictType):
            processor_properties = json.loads(self.input_data.processor_properties)
          self.logger.debug("Processor's properties was taken from input data: %s" % processor_properties)
          self.properties.update(processor_properties)
      except Exception as err:
        ExceptionLog.handler(self.logger, err, 'Error load properties from input data:')

      self.algorithm_name = self.properties[CONSTS.ALGORITHM_KEY][CONSTS.ALGORITHM_NAME_KEY]
      self.logger.debug("Algorithm : %s" % self.algorithm_name)
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        Utils.storePickleOnDisk(input_pickled_object, ENV_SCRAPER_STORE_PATH, "scraper.in." + \
                                str(self.input_data.urlId))
      if "metrics" in self.properties:
        try:
          self.metrics = json.loads(self.properties["metrics"])
          self.logger.debug(">>> Metrics loads = " + str(self.metrics))
        except Exception as excp:
          self.logger.debug(">>> Metrcis dumps exception = " + str(excp))
      # TODO main processing over every url from list of urls in the batch object
      tmp = sys.stdout
      sys.stdout = open("/dev/null", "wb")

      # initialization of scraper
      # load scraper's modules
      self.loadExtractors()

      # # Initialization pubdate
      # self.logger.debug("Initialization pubdate from urlObj.pDate use value: %s",
      #                  str(self.input_data.batch_item.urlObj.pDate))
      # self.pubdate = self.input_data.batch_item.urlObj.pDate

      scraperResponses = self.jsonParserProcess()

      sys.stdout = tmp

      self.logger.debug("scraperResponse:\n%s", varDump(scraperResponses))
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        output_pickled_object = pickle.dumps(scraperResponses)
        Utils.storePickleOnDisk(output_pickled_object, ENV_SCRAPER_STORE_PATH,
                                "scraper.out." + str(self.input_data.urlId))
        print output_pickled_object
        sys.stdout.flush()
      else:
        self.output_data = scraperResponses
    except Exception as err:
      ExceptionLog.handler(self.logger, err, 'ScraperCustomJson process batch error:')
      self.exitCode = EXIT_FAILURE
      raise Exception('ScraperCustomJson process batch error:' + str(err))


  # #load extractors
  #
  def loadExtractors(self):
    try:
      # modules
      if CONSTS.MODULES_KEY in self.properties and self.algorithm_name in self.properties[CONSTS.MODULES_KEY]:
        modules = self.properties[CONSTS.MODULES_KEY][self.algorithm_name]
      else:
        self.logger.debug(">>> No moduler_key or algorithm_name in self.properties")
        modules = []

      self.logger.debug("Algorithm name: <%s>" % (self.algorithm_name))
      self.logger.debug("Modules: %s" % modules)

      self.extractors = []
      for module in modules:
        exrtactor = self.createModule(module)
        # Check if module was created successfully and then insert it to extractors
        if exrtactor is not None:
          self.extractors.append(exrtactor)

      # Info show extractors loaded
      self.logger.debug("*******************")
      self.logger.debug("Loaded extractors:")
      for exrtactor in self.extractors:
        self.logger.debug(exrtactor.name)
      self.logger.debug("*******************")

    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_LOAD_EXTRACTORS)
      raise


  # #createApp
  # create application's pool
  #
  # @param app_name application name which instance will be created
  # @return instance of created application
  def createModule(self, module_name):
    appInst = None
    try:
      appInst = (module_name, eval(module_name)(self.config, None, self.urlHost, self.properties))[1]  # pylint: disable=W0123
      self.logger.debug("%s has been created!" % module_name)
    except Exception as err:
      ExceptionLog.handler(self.logger, err, "Can't create module %s. Error is:" % (module_name))

    return appInst


  def getNextBestExtractor(self):
    # return extractor with highest rank
    try:
      extractor = next(self.itr)
    except StopIteration:
      extractor = None
    return extractor


  def resourceExtraction(self, jsonElem):
    ret = []
    # get resource as dictionary
    resource_set = {}
    resource_set["url"] = self.input_data.url
    resource_set["resId"] = self.input_data.urlId
    resource_set["siteId"] = self.input_data.siteId
    resource_set["raw_html"] = jsonElem
    resource = Resource(resource_set)

    # get best matching extractor
    self.extractor = self.getNextBestExtractor()
    self.logger.debug("get best matching extractor: " + str(self.extractor))

    # search engine parsing ???
    collectResult = Result(self.config, self.input_data.urlId, self.metrics)
    # main loooop
    while self.extractor:
      result = Result(self.config, self.input_data.urlId, self.metrics)
      self.logger.debug(">>> TAG BEGIN extractor = " + str(self.extractor))
      result = self.extractor.extractTags(resource, result)

      self.logger.debug(">>> TAG END")
      empty_tags = result.getEmptyTags()
      self.logger.debug("get list of empty tags from result: " + str(empty_tags))
      filled_tags = result.getFilledTags()
      self.logger.debug("get list of filled_tags from result: " + str(filled_tags))
      self.extractor = self.getNextBestExtractor()
      self.logger.debug("get best matching extractor: " + str(self.extractor))

      for key in result.tags:
        if key not in collectResult.tags or not collectResult.isTagFilled(key):
          collectResult.tags[key] = copy.deepcopy(result.tags[key])
      ret.append(result)
    self.logger.debug(">>> EXIT LOOP")
    ret = [collectResult] + ret
    return ret


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
    elif localOutputFormat == "html" or localOutputFormat == "xml":
      ret = xml.sax.saxutils.escape(elem, {"'": "&apos;", "\"" : "&quot;"})
    elif localOutputFormat == "sql":
      # ret = mdb.escape_string(elem)  # pylint: disable=E1101
      ret = Utils.escape(elem)
    return ret


  # formatOutputData formats internal response's data by localOutputFormat format
  #
  def formatOutputData(self, response, localOutputFormat):
    # result.tags[key]["data"]
    for key in response.tags:
      if "data" in response.tags[key]:
        if isinstance(response.tags[key]["data"], types.ListType):
          for i, elem in enumerate(response.tags[key]["data"]):
            response.tags[key]["data"][i] = self.formatOutpuElement(elem, localOutputFormat)
        elif isinstance(response.tags[key]["data"], types.StringTypes):
          response.tags[key]["data"] = self.formatOutpuElement(response.tags[key]["data"], localOutputFormat)


  # jsonParserExtractor extract one element
  #
  def jsonParserExtractor(self, jsonElem):
    if self.extractors is not None:
      self.itr = iter(sorted(self.extractors, key=lambda extractor: 0, reverse=True))  # pylint: disable=W0612,W0613
      self.logger.debug("Extractors: %s" % varDump(self.itr))

    responses = self.resourceExtraction(jsonElem)
    for response in responses:
      response.metricsPrecalculate()
      response.stripResult()
      # Add tag 'source_url'
      self.addCustomTag(result=response, tag_name=CONSTS.TAG_SOURCE_URL,
                        tag_value=[str(self.input_data.url)])

      if CONSTS.LANG_PROP_NAME in self.properties:
        # response.tagsLangDetecting(self.properties[CONSTS.LANG_PROP_NAME])
        langDetector = ScraperLangDetector(self.properties[CONSTS.LANG_PROP_NAME])
        langDetector.process(response, self.logger)
        langTagsDict = langDetector.getLangTags()
        self.logger.debug("langTagsDict: %s", varDump(langTagsDict))

        # add lang tags to processed content
        for tagName, langValue in langTagsDict.items():
          self.addCustomTag(result=response, tag_name=tagName, tag_value=langValue)

        summaryLang = langDetector.getSummaryLang(response, self.logger)
        self.addCustomTag(result=response, tag_name=CONSTS.TAG_SUMMARY_LANG, tag_value=summaryLang)

      pubdate, timezone = self.normalizeDatetime(response, self.algorithm_name)
      if pubdate is not None:
        self.pubdate = pubdate
        self.logger.debug("Pubdate from 'pubdate': " + str(self.pubdate))

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

      if self.outputFormat is not None:
        self.formatOutputData(response, self.outputFormat)
      else:
        self.logger.debug(">>> Warning, can't extracr output format")
      response.recalcTagMaskCount(None, self.altTagsMask)
      self.tagsCount = response.tagsCount
      self.tagsMask = response.tagsMask
      # self.putArticleToDB({"default":response})
      self.logger.debug("self.tagsCount: %s", self.tagsCount)
      self.logger.debug("self.tagsMasks: %s", self.tagsMask)

      self.logger.debug(">>> Resp: %s\n", varDump(response))

      # TODO: Seems need to be done more system way
      response.finish = time.time()
      response.data["time"] = "%s" % (response.finish - response.start)

      response = self.applyHTTPRedirectLink(self.input_data.batch_item.siteId, self.input_data.batch_item.urlObj.url,
                                            self.input_data.batch_item.properties, response)

    self.getProcessedContent(responses)


  # getProcessedContent fills self.processedContent's fields
  #
  def getProcessedContent(self, result):
    for elem in result:
      elem.get()
    self.processedContent = {}
    self.processedContent["default"] = result[0]
    self.processedContent["internal"] = result
    self.processedContent["custom"] = []
    self.tagsCount = result[0].tagsCount
    self.tagsMask = result[0].tagsMask

    if "pubdate" in result[0].tags and "data" in result[0].tags["pubdate"] and \
    len(result[0].tags["pubdate"]["data"]) > 0:
      self.pubdate = result[0].tags["pubdate"]["data"][0]
      self.logger.debug('>>>> Set self.pubdate =  ' + str(self.pubdate))


  # fillScraperResponse clears all ScraperResponse class fields and return new ScraperResponse instance
  #
  def fillScraperResponse(self, jsonElem):
    self.tagsCount = 0
    self.tagsMask = 0
    self.pubdate = None
    self.processedContent = None
    self.errorMask = APP_CONSTS.ERROR_OK
    self.jsonParserExtractor(jsonElem)
    return ScraperResponse(self.tagsCount, self.tagsMask, self.pubdate, self.processedContent, self.errorMask)


  # generateEmptyResponse generates and returns empty response
  #
  def generateEmptyResponse(self):
    localResult = Result(self.config, self.input_data.urlId, self.metrics)
    # Add tag 'source_url'
    self.addCustomTag(result=localResult, tag_name=CONSTS.TAG_SOURCE_URL, tag_value=[str(self.input_data.url)])
    self.getProcessedContent([localResult])
    return ScraperResponse(0, 0, self.pubdate, self.processedContent, APP_CONSTS.ERROR_MASK_SCRAPER_ERROR)


  # jsonParserProcess method execute for json_parser algorithm
  #
  def jsonParserProcess(self):
    rawDataJson = None
    ret = []
    try:
      rawDataJson = json.loads(self.input_data.raw_content)
    except Exception as excp:
      self.logger.debug(">>> jsonParserProcess wrong rawData json: " + str(excp))

    self.logger.debug("!!! type(rawDataJson) = %s", str(type(rawDataJson)))
    if not isinstance(rawDataJson, list):
      self.logger.debug("!!! rawDataJson: %s", varDump(rawDataJson))


    if rawDataJson is not None and isinstance(rawDataJson, list):
      for elem in rawDataJson:
        if isinstance(elem, list):
          for internalElem in elem:
            ret.append(self.fillScraperResponse(internalElem))
        else:
          ret.append(self.fillScraperResponse(elem))
    else:
      self.logger.debug(">>> rawDataJson structure not List type")

    if len(ret) == 0:
      ret.append(self.generateEmptyResponse())
    return ret


  # getExitCode method returns exitCode value
  #
  def getExitCode(self):
    return self.exitCode


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
#     if tag_name not in result.tags:
#       result.tags[tag_name] = data


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
#               if (response.tags.get(responseTagName) is not None and \
#               'type' in response.tags[responseTagName] and \
#               response.tags[responseTagName]['type'] == responseType) or \
#               (responseTagName == CONSTS.TAG_PUB_DATE and response.tags.get(responseTagName) is not None):
#                 tagNames.append(responseTagName)
#         else:
#           tagNames = TAGS_DATETIME_NEWS_NAMES
#
#         self.logger.debug('normalizeDatetime  tagNames: ' + varDump(tagNames))
#         retDict = {}
#         for tagName in tagNames:
#           pubdate, tzone = self.extractPubDate(response, tagName)  # , properties, urlString)
#           if self.extractor and tagName in response.tags:
#             self.extractor.addTag(result=response, tag_name=tagName + '_normalized', tag_value=pubdate, \
#                                   xpath=response.tags[tagName]['xpath'])
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
#                            {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
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
#       if response is not None and dataTagName in response.tags and response.tags[dataTagName] is not None:
#
#         # self.logger.debug("extractPubDate response: " + varDump(response))
#
#         inputData = response.tags[dataTagName]["data"]
#         self.logger.debug("extractPubDate response has '" + str(dataTagName) + "' is: " + str(inputData))
#         self.logger.debug("extractPubDate type of '" + str(dataTagName) + "' is: " + str(type(inputData)))
#
#         inputList = []
#         if isinstance(inputData, basestring):
#           inputList = [inputData]
#         elif isinstance(inputData, list):
#           inputList = inputData
#         else:
#           pass
#
#         pubdate = []
#         timezones = []
#         for inputElem in inputList:
#           d = DateTimeType.parse(inputElem, bool(self.useCurrentYear), self.logger, False)
#           self.logger.debug('pubdate: ' + str(d))
#
#           if d is not None:
#             d, tzone = DateTimeType.split(d)
#             pubdate.append(d.isoformat(DateTimeType.ISO_SEP))
#             timezones.append(tzone)
#
#         self.logger.debug("extractPubDate result pubdate: " + str(pubdate))
#         response.tags[dataTagName]["data"] = pubdate
#         if len(pubdate) > 0:
#           ret = pubdate[0]
#
#         if len(timezones) > 0:
#           timezone = timezones[0]
#
#     except Exception, err:
#       ExceptionLog.handler(self.logger, err, 'extractPubDate error:', (), \
#                            {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
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
