"""@package docstring
 @file Scraper.py
 @author Alexey <developers.hce@gmail.com>, scorp, bgv
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013-2016 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""
import re
import sys
import time
import json
import pickle
import logging.config
import ConfigParser
import xml.sax.saxutils
import urlparse
import copy
import datetime
import base64

from dateutil.parser import *  # pylint: disable=W0401,W0614
from dateutil import parser
from cement.core import foundation

from app.Utils import varDump
from app.Utils import isValidURL
from app.SelectorWrapper import SelectorWrapper
import app.Utils as Utils  # pylint: disable=F0401
from app.Utils import ExceptionLog
from app.Utils import SQLExpression
from app.Utils import UrlNormalizator
from app.Utils import urlNormalization
# scraper's modules
import app.Consts as APP_CONSTS
import app.Profiler
from app.DateTimeType import DateTimeType
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
# import dc.EventObjects
import dc.EventObjects as dc_event
from dc.EventObjects import SiteFilter
import dc_processor.Constants as CONSTS
from dc_processor.scraper_resource import Resource
from dc_processor.scraper_result import Result as Result
from dc_processor.ScraperResponse import ScraperResponse
from dc_processor.TemplateExtractorXPathPreparing import TemplateExtractorXPathPreparing
from dc_processor.PDateTimezonesHandler import PDateTimezonesHandler
from dc_processor.AuthorType import AuthorType
from dc_processor.MediaLimitsHandler import MediaLimitsHandler
from dc_processor.ScraperLangDetector import ScraperLangDetector
# scraper's modules used via eval()
from dc_processor.newspaper_extractor import NewspaperExtractor  # pylint: disable=W0611
from dc_processor.goose_extractor import GooseExtractor  # pylint: disable=W0611
from dc_processor.scrapy_extractor import ScrapyExtractor
from dc_processor.ml_extractor import MLExtractor  # pylint: disable=W0611
from dc_processor.custom_extractor import CustomExtractor  # pylint: disable=W0611
from dc_crawler.DBTasksWrapper import DBTasksWrapper
import dc_crawler.Constants as CRAWLER_CONSTS

APP_NAME = "scraper"

MSG_ERROR_LOAD_CONFIG = "Error loading config file. Exciting."
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Error loading logging config file. Exiting."
MSG_ERROR_LOAD_EXTRACTORS = "Error load extractors "
MSG_ERROR_TEMPLATE_EXTRACTION = "Error template extraction "
MSG_ERROR_DYNAMIC_EXTRACTION = "Error dynamic extraction "
MSG_ERROR_LOAD_DB_BACKEND = "Error load db backend"
MSG_ERROR_LOAD_OPTIONS = "Error load options"
MSG_INFO_PREPARE_CONTENT = "Prepare content: "
MSG_ERROR_ADJUST_PR = "Error adjust partial references. "
MSG_ERROR_ADJUST_PUBDATE = "PUBDATE_ERROR "
MSG_ERROR_ADJUST_TITLE = "Can't adjust title. "

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SQLITE_TIMEOUT = 30

ENV_SCRAPER_STORE_PATH = "ENV_SCRAPER_STORE_PATH"
# CONTENT_REPLACEMENT = "[\"\\n\", \"\\r\\n\", \"\\t\"]"
CONTENT_REPLACEMENT_LIST = ['\n', '\r\n', '\t', ' ', '<br>', '<p>', '</p>']
DEFAULT_TAG_REDUCE_MASK = 65535

EXTENDED_NEWS_TAGS = {"description": ["//meta[@name='description']//@content"]}
LINKS_NEWS_TAGS = [CONSTS.TAG_MEDIA, CONSTS.TAG_LINK, CONSTS.TAG_MEDIA_CONTENT, "links", "href"]
# DATA_NEWS_TAGS = [CONSTS.TAG_DC_DATE]
DATA_NEWS_TAGS = []

TAGS_DATETIME_NEWS_NAMES = [CONSTS.TAG_PUB_DATE, CONSTS.TAG_DC_DATE]
TAGS_DATETIME_TEMPLATE_TYPES = [CONSTS.TAG_TYPE_DATETIME]

OPTION_SECTION_DATETIME_NEWS_NAMES = 'tags_datetime_news_names'
OPTION_SECTION_DATETIME_TEMPLATE_TYPES = 'tags_datetime_template_types'

OPTION_SECTION_TAGS_TYPE = 'tagsTypes'

OPTION_SECTION_URL_SOURCES_RULES = 'urlSourcesRules'
URL_SOURCES_RULE_DATA_URL = 'd_url'
URL_SOURCES_RULE_REDIRECT_URL = 'r_url '
URL_SOURCES_RULE_FEED_URL = 'f_url'

# #Scraper
#
#
class Scraper(foundation.CementApp):

  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  # Constants use in class
  WWW_PREFIX = "www."

  # Mandatory
  class Meta(object):
    label = APP_NAME
    def __init__(self):
      pass


  # #constructor
  # initialize default fields
  def __init__(self, usageModel=APP_CONSTS.APP_USAGE_MODEL_PROCESS, configFile=None, logger=None, inputData=None):
    if usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class __init__ method
      foundation.CementApp.__init__(self)

    self.exitCode = EXIT_SUCCESS
    self.itr = None
    self.extractor = None
    self.extractors = []
    self.input_data = inputData
    self.logger = logger
    self.sqliteTimeout = SQLITE_TIMEOUT
    self.scraperPropFileName = None
    self.properties = {}
    self.algorithm_name = None
    self.pubdate = None
    self.message_queue = []
    self.entry = None
    self.article = None
    self.outputFormat = None
    self.errorMask = APP_CONSTS.ERROR_OK
    self.metrics = None
    self.altTagsMask = None
    self.tagsCount = 0
    self.tagsMask = 0
    self.processedContent = None
    self.usageModel = usageModel
    self.configFile = configFile
    self.output_data = None
    self.urlHost = None
    self.xpathSplitString = ' '
    self.useCurrentYear = 0
    self.datetimeNewsNames = []
    self.datetimeTemplateTypes = []
    self.tagsTypes = None
    self.attrConditions = None
    self.dbWrapper = None
    self.mediaLimitsHandler = None
    self.urlSourcesRules = None
    self.tagReduceMask = DEFAULT_TAG_REDUCE_MASK
    self.baseUrl = None


  # #setup
  # setup application
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


  # # Check DOM element
  #
  # @param elem - element of DOM model
  # @return True if is DOM model or otherwise False
  def checkDOMElement(self, elem):
    ret = False
    if re.search('<', elem):
      self.logger.debug("Media tag contain DOM element: %s", elem)
      ret = True
    return ret


  # #adjust partial references
  # adjust partial references
  #
  def adjustPartialReferences(self, response):
    # self.logger.debug("!!! response.tags: " + varDump(response.tags))
#     self.logger.debug("!!! self.input_data.template: " + varDump(self.input_data.template))
#     self.logger.debug("self.input_data.url: %s", varDump(self.input_data.url))
#     self.logger.debug("self.input_data.siteId: %s", varDump(self.input_data.siteId))

    if "link" in response.tags and isinstance(response.tags["link"], dict) and \
      "media" in response.tags and isinstance(response.tags["media"], dict):
      try:
        url = None
        if self.input_data.template and "link" in self.input_data.template:
          self.logger.debug("url type: %s", str(type(response.tags["link"]["data"])))
          if isinstance(response.tags["link"]["data"], basestring):
            url = response.tags["link"]["data"]
          else:
            url = response.tags["link"]["data"][0]

          url = urlNormalization(self.baseUrl, url)
          response.tags["link"]["data"] = url

        else:
          url = self.input_data.url

#         self.logger.debug("link tag in response: '%s'", str(url))
#         self.logger.debug("response.tags['media']: %s", str(response.tags["media"]))
#         self.logger.debug("media tag in response: %s, type: %s" , str(response.tags["media"]["data"]), str(type(response.tags["media"]["data"])))
        res = []
        mediaData = []
        if isinstance(response.tags["media"]["data"], basestring):
          mediaData = [response.tags["media"]["data"]]
        elif isinstance(response.tags["media"]["data"], list):
          mediaData = list(set(response.tags["media"]["data"]))
        else:
          self.logger.error("!!! Wrong type of tag 'media': %s", str(type(response.tags["media"]["data"])))

        filter_patterns, filter_types = [], []
        if self.input_data.filters:
          self.logger.debug("filter: %s", varDump(self.input_data.filters))
          # filter_types = [filter_item["Type"] for filter_item in self.input_data.filters]
          # filter_patterns = [re.compile(filter_item["Pattern"]) for filter_item in self.input_data.filters]
          filter_types = [filter_item.type for filter_item in self.input_data.filters]
          filter_patterns = [re.compile(filter_item.pattern) for filter_item in self.input_data.filters]

        for media in mediaData:
          self.logger.debug("Media link: '%s'", media)
          # instead pure url
          if self.checkDOMElement(media):
            res.append(media)
            break
#           media = urlparse.urljoin(url, media)
          media = urlNormalization(self.baseUrl, media)
#           self.logger.debug("media 2: %s", media)

          for filter_type, filter_pattern in zip(filter_types, filter_patterns):
            match = filter_pattern.search(media)
            if filter_type == SiteFilter.TYPE_EXCLUDE and match:
              break
            if filter_type == SiteFilter.TYPE_INCLUDE and match:
              allowedUrls = self.checkMediaTag(media)
              if len(allowedUrls) > 0:
                res.append(','.join(allowedUrls))
              break
            else:
              self.logger.debug("media: %s", media)
              self.logger.debug("url: %s", url)
              allowedUrls = self.checkMediaTag(media)
              if len(allowedUrls) > 0:
                res.append(','.join(allowedUrls))

          # If media tag after adjusting is empty remove it from response
          if not len(res):
            self.logger.debug("media tag is empty. Remove media tag from response.")
            del response.tags["media"]
          else:
            self.logger.debug("media tag is adjusted. Copy media tag to response.")
            response.tags["media"]["data"] = res
          # End code block removing empty media tag
#        else:
#          self.logger.debug("resource hasn't template with media tag. adjustPartialReferences doesn't execute")
      except Exception as err:
        ExceptionLog.handler(self.logger, err, MSG_ERROR_ADJUST_PR, (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})

    else:
      self.logger.debug(">>> Response has not have link or media tag, Don't need adjust media")


  # adjustTitle
  #
  def adjustTitle(self, response):
    try:
      if self.input_data.template and "title" in self.input_data.template and "title" in response.tags:
        self.logger.debug("resource has template with title tag. Try to adjust title.")
        self.logger.debug("response.tags['title']: " + str(response.tags["title"]))
        localExtractor = self.extractor
        if localExtractor is None:
          if len(self.extractors) > 2:
            localExtractor = self.extractors[2]
          else:
            raise Exception(">>> Wrong! self.extractors list doesn't have 3'th element (index 2)")
        if isinstance(response.tags["title"], basestring):
          self.logger.debug("response has not have title tag")
          sel = SelectorWrapper(text=self.input_data.raw_content)
          title = sel.xpath("//title/text()").extract()
          localExtractor.addTag(result=response, tag_name="title", tag_value=title)
        self.logger.debug("TYPE response.tags['title']['data']" + str(type(response.tags["title"]["data"])))
      else:
        self.logger.debug("resource hasn't template with title tag. Don't need adjust title.")
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_ADJUST_TITLE, (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})


  # adjustLinkURL
  #
  def adjustLinkURL(self, response):
    flag = False
    try:
      if response.tags and "link" in response.tags:
        self.logger.debug("resource has template with link tag. Try to adjust link.")
        self.logger.debug("response.tags['link']: " + str(response.tags["link"]))
        self.logger.debug("self.extractor: %s", str(self.extractor))
        flag = True
        if self.extractor:
          self.logger.debug("Extractor exists")
          if isinstance(response.tags["link"], basestring):
            self.logger.debug("response has not have link tag")
            self.extractor.addTag(result=response, tag_name="link", tag_value=[self.input_data.url])
          # bypass
          else:
            response.tags["link"]["data"] = self.input_data.url
        else:
          if len(self.extractors) > 2:
            self.extractors[2].addTag(result=response, tag_name="link", tag_value=[self.input_data.url])
          else:
            self.logger.debug(">>> Wrong! self.extractors list doesn't have 3'th element (index 2)")
        self.logger.debug("TYPE response.tags['link']['data']" + str(type(response.tags["link"]["data"])))
      else:
        self.logger.debug("resource hasn't template with link tag. Don't need adjust link.")
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_ADJUST_PR, (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})

    return flag


  # # Normalize author tags procedure
  #
  # @param confProp - properties as JSON already read from config file
  # @param procProp - properties as JSON from PROCESSOR_PROPERTIES
  # @param response - scraper response instance
  # @return - None
  def normalizeAuthor(self, confProp, procProp, response):
    try:
      if response is not None and response.tags is not None:
        # self.logger.debug("normalizeAuthor scraper response: " + varDump(response))

        if self.input_data.template and self.algorithm_name != CONSTS.PROCESS_ALGORITHM_REGULAR:
          if AuthorType.MAIN_TAG_NAME in response.tags and response.tags[AuthorType.MAIN_TAG_NAME] is not None and \
          "data" in response.tags[AuthorType.MAIN_TAG_NAME]:
            inputData = response.tags[AuthorType.MAIN_TAG_NAME]["data"]
            self.logger.debug("normalizeAuthor response has '" + str(AuthorType.MAIN_TAG_NAME) + "' is: " + \
                              str(inputData))
            self.logger.debug("normalizeAuthor type of '" + str(AuthorType.MAIN_TAG_NAME) + "' is: " + \
                              str(type(inputData)))

            inputList = []
            if isinstance(inputData, str) or isinstance(inputData, unicode):
              inputList = [inputData]
            elif isinstance(inputData, list):
              inputList = inputData
            else:
              pass

            self.logger.debug("normalizeAuthor confProp: " + varDump(confProp))
            self.logger.debug("normalizeAuthor procProp: " + varDump(procProp))

            authors = []
            for inputElem in inputList:
              author = AuthorType.parse(confProp, procProp, inputElem, self.logger)
              if author is not None:
                authors.append(author)

            self.logger.debug("normalizeAuthor result author: " + str(authors))
            if len(authors) > 0:
              response.tags[AuthorType.MAIN_TAG_NAME]["data"] = authors

    except Exception, err:
      ExceptionLog.handler(self.logger, err, 'normalizeAuthor error:', (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})


  # # Normalize datetime tags procedure
  #
  # @param response - scraper response instance
  # @param algorithmName - algorithm name
  # @return - 'pubdate tag value'
  def normalizeDatetime(self, response, algorithmName):
    ret = None
    timezone = ''
    try:
      if response is not None and response.tags is not None:
        # self.logger.debug("normalizeDatetime scraper response: " + varDump(response))
        tagNames = []
        if self.input_data.template and algorithmName == CONSTS.PROCESS_ALGORITHM_REGULAR:
          # temlate
          for responseType in self.datetimeTemplateTypes:
            for responseTagName in response.tags:
              self.logger.debug("normalizeDatetime responseTagName: '" + str(responseTagName) + "'")
              if (response.tags.get(responseTagName) is not None and \
              'type' in response.tags[responseTagName] and \
              response.tags[responseTagName]['type'] == responseType) or \
              (responseTagName == CONSTS.TAG_PUB_DATE and response.tags.get(responseTagName) is not None):
                tagNames.append(responseTagName)
        else:
          # dynamic
          tagNames = self.datetimeNewsNames

        self.logger.debug('normalizeDatetime  tagNames: ' + varDump(tagNames))
        retDict = {}
        for tagName in tagNames:
          pubdate, tzone = self.extractPubDate(response, tagName)
          if self.extractor and tagName in response.tags:
            self.extractor.addTag(result=response, tag_name=tagName + '_normalized', tag_value=pubdate, \
                                  xpath=response.tags[tagName]['xpath'])

          self.logger.debug('tagName: ' + str(tagName) + ' pubdate: ' + str(pubdate))
          retDict[tagName] = pubdate

          if tagName == CONSTS.TAG_PUB_DATE:
            ret = pubdate
            timezone = tzone
          else:
            pass

        if ret is None:
          for key, value in retDict.items():
            if value is not None:
              ret = value
              self.logger.debug('set return value from ' + str(key) + ' : ' + str(value))
              break

    except Exception, err:
      ExceptionLog.handler(self.logger, err, 'normalizeDatetime error:', (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})

    return ret, timezone


  # # Extract pubdate
  #
  # @param response - response instance
  # @param dataTagName - tag name for extracting
  # @return pubdate if success or None
  def extractPubDate(self, response, dataTagName):
    # variable for result
    ret = None
    timezone = ''
    try:
      if response is not None and dataTagName in response.tags and response.tags[dataTagName] is not None:

        # self.logger.debug("extractPubDate response: " + varDump(response))

        inputData = response.tags[dataTagName]["data"]
        self.logger.debug("extractPubDate response has '" + str(dataTagName) + "' is: " + str(inputData))
        self.logger.debug("extractPubDate type of '" + str(dataTagName) + "' is: " + str(type(inputData)))

        inputList = []
        if isinstance(inputData, basestring):
          inputList = [inputData]
        elif isinstance(inputData, list):
          inputList = inputData
        else:
          pass

        pubdate = []
        timezones = []
        for inputElem in inputList:
          d = DateTimeType.parse(inputElem, bool(self.useCurrentYear), self.logger, False)
          self.logger.debug('pubdate: ' + str(d))

          if d is not None:
            d, tzone = DateTimeType.split(d)
            pubdate.append(d.isoformat(DateTimeType.ISO_SEP))
            timezones.append(tzone)

        self.logger.debug("extractPubDate result pubdate: " + str(pubdate))
        response.tags[dataTagName]["data"] = pubdate
        if len(pubdate) > 0:
          ret = pubdate[0]

        if len(timezones) > 0:
          timezone = timezones[0]

    except Exception, err:
      ExceptionLog.handler(self.logger, err, 'extractPubDate error:', (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})

    return ret, timezone


  # # pubdate transformation use timezone value
  #
  # @param rawPubdate - raw pubdate string
  # @param rawTimezone - raw timezone string
  # @param properties - properties from PROCESSOR_PROPERTIES
  # @param urlString - url string value
  # @return pubdate and timezone if success or None and empty string
  def pubdateTransform(self, rawPubdate, rawTimezone, properties, urlString):
    # variables for result
    pubdate = rawPubdate
    timezone = rawTimezone

    # self.logger.debug('properties: ' + varDump(properties))
    if CONSTS.PDATE_TIMEZONES_NAME in properties:
      propertyString = properties[CONSTS.PDATE_TIMEZONES_NAME]
      self.logger.debug('inputted ' + CONSTS.PDATE_TIMEZONES_NAME + ':' + str(propertyString))

      dt = DateTimeType.parse(rawPubdate, bool(self.useCurrentYear), self.logger, False)
      self.logger.debug('pubdate: ' + str(dt))
      if dt is not None:
        # get utc offset if necessary
        utcOffset = DateTimeType.extractUtcOffset(rawTimezone, self.logger)
        self.logger.debug('utcOffset: ' + str(utcOffset))
        # transformation accord to PDATE_TIMEZONES properties
        d = PDateTimezonesHandler.transform(dt, utcOffset, propertyString, urlString, self.logger)
        if d is not None:
          dt = d

      if dt is not None:
        d, tzone = DateTimeType.split(dt)
        pubdate = d.isoformat(DateTimeType.ISO_SEP)
        timezone = tzone

    return pubdate, timezone


  # # refineBadDateTags, deleles, from result, datetime tags with bad datetime value.
  #
  def refineBadDateTags(self, response):
    removeKeys = []
    for key in response.tags:
      if key in DATA_NEWS_TAGS:
        tagsValue = None

        if isinstance(response.tags[key], basestring):
          tagsValue = response.tags[key]
        elif isinstance(response.tags[key], dict) and "data" in response.tags[key]:
          if isinstance(response.tags[key]["data"], basestring):
            tagsValue = response.tags[key]["data"]
          elif isinstance(response.tags[key]["data"], list) and len(response.tags[key]["data"]) > 0 and \
          isinstance(response.tags[key]["data"][0], basestring):
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


  # #Internal method of url's domain crc calculating
  #
  # @param url - incoming url
  def calcUrlDomainCrc(self, url):
    urlHost = None
    auth = urlparse.urlsplit(url)[1]
    if auth is not None:
      urlHost = (re.search('([^@]*@)?([^:]*):?(.*)', auth).groups())[1]
      if urlHost is not None and urlHost.find(self.WWW_PREFIX) == 0:
        urlHost = urlHost[len(self.WWW_PREFIX): len(urlHost)]

    return urlHost


  # # The main processing of the batch object
  #
  # @param config - config parser
  # @return None
  def process(self, config):
    # info input data
    self.logger.info("input_data url: %s, urlId: %s, siteId: %s", str(self.input_data.url), str(self.input_data.urlId),
                     str(self.input_data.siteId))

    self.baseUrl = self.extractBaseUrlRssFeed(self.input_data.siteId, self.input_data.url)
    if self.baseUrl is None:
      self.baseUrl = self.input_data.url

    if self.input_data.template and self.algorithm_name == CONSTS.PROCESS_ALGORITHM_REGULAR:
      # Reconfigure processor's properties to involve only template scraper
      responses = self.templateExtraction(config, self.urlHost)
    else:
      # get iterator to ranked list of extractors
      self.itr = iter(sorted(self.extractors, key=lambda extractor: 0, reverse=True))
      self.logger.debug("Extractors: %s" % varDump(self.itr))
      responses = self.newsExtraction()

    self.logger.info("!!!!! response after extraction: " + varDump(responses))

    if CONSTS.MEDIA_LIMITS_NAME in self.input_data.batch_item.properties:
      self.logger.debug("Found property '%s'", str(CONSTS.MEDIA_LIMITS_NAME))
      self.mediaLimitsHandler = MediaLimitsHandler(self.input_data.batch_item.properties[CONSTS.MEDIA_LIMITS_NAME])

    for response in responses:
      response.metricsPrecalculate()
      response.stripResult()
      # Add tag 'source_url'
      self.addCustomTag(result=response, tag_name=CONSTS.TAG_SOURCE_URL, \
                        tag_value=str(self.input_data.url))

      #self.logger.debug("self.properties: %s", varDump(self.properties))
      if CONSTS.LANG_PROP_NAME in self.properties:
        self.logger.debug("!!! Enter '%s' !!!", str(CONSTS.LANG_PROP_NAME))
        ####response.tagsLangDetecting(self.properties[CONSTS.LANG_PROP_NAME])
        langDetector = ScraperLangDetector(self.properties[CONSTS.LANG_PROP_NAME])
        langDetector.process(response, self.logger)
        langTagsDict = langDetector.getLangTags()
        self.logger.debug("langTagsDict: %s", varDump(langTagsDict))

# #         self.logger.debug("!!! self.input_data.batch_item.properties = %s, type = %s", varDump(self.input_data.batch_item.properties), str(type(self.input_data.batch_item.properties)))
# #
# #         if 'template' in self.input_data.batch_item.properties and \
# #           'templates' in self.input_data.batch_item.properties['template'] and \
# #           len(self.input_data.batch_item.properties['template']['templates']) > 0 and \
# #           'output_format' in self.input_data.batch_item.properties['template']['templates'][0] and \
# #           'item' in self.input_data.batch_item.properties['template']['templates'][0]['output_format']:
# #           itemString = self.input_data.batch_item.properties['template']['templates'][0]['output_format']['item']
# #           self.logger.debug("itemString: %s:", str(itemString))
# #           try:
# #             jsonDict = json.loads(itemString, encoding='utf-8')
# #             self.logger.debug("jsonDict: %s:", varDump(jsonDict))
# #             for tagName, langValue in langTagsDict.items():
# #               jsonDict[tagName] = langValue
# #
# #             self.input_data.batch_item.properties['template']['templates'][0]['output_format']['item'] = \
# #               json.dumps(jsonDict, ensure_ascii=False, encoding='utf-8')
# #           except Exception, err:
# #             self.logger.error(str(err))
# #             self.logger.info(Utils.getTracebackInfo())

        # add lang tags to processed content
        for tagName, langValue in langTagsDict.items():
          self.addCustomTag(result=response, tag_name=tagName, tag_value=langValue)

        summaryLang = langDetector.getSummaryLang(response, self.logger)
        self.addCustomTag(result=response, tag_name=CONSTS.TAG_SUMMARY_LANG, tag_value=summaryLang)
        self.logger.debug("!!! Leave '%s' !!!", str(CONSTS.LANG_PROP_NAME))

      # put extracted article to the db

      if self.algorithm_name != CONSTS.PROCESS_ALGORITHM_REGULAR:
        self.adjustTitle(response)
        self.adjustLinkURL(response)
        self.adjustPartialReferences(response)

        # self.logger.debug("CONSTS.TAG_PUB_DATE response: " + varDump(response))

      self.preparseResponse(response)

      # Improvement author
      tagsTypes = None
      if CONSTS.TAGS_TYPES_NAME in self.input_data.batch_item.properties:
        tagsTypes = self.input_data.batch_item.properties[CONSTS.TAGS_TYPES_NAME]

      self.logger.info('=' * 50)
      self.logger.info('self.properties: ' + varDump(self.properties))

      self.normalizeAuthor(self.tagsTypes, tagsTypes, response)

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
            if len(response.tags[CONSTS.TAG_PUB_DATE]["data"]) > 0 and response.tags[CONSTS.TAG_PUB_DATE]["data"][0]:
              self.pubdate = response.tags[CONSTS.TAG_PUB_DATE]["data"][0]
              self.logger.debug("Pubdate from 'dc_date': " + str(self.pubdate))
              # Check format
              d = DateTimeType.parse(self.pubdate, bool(self.useCurrentYear), self.logger, False)
              self.logger.debug('Check format pubdate: ' + str(d))
              if d is not None:
                d, timezone = DateTimeType.split(d)
                self.pubdate = d.isoformat(DateTimeType.ISO_SEP)
                self.logger.debug("Result pubdate from 'dc_date': %s, timezone: %s", str(self.pubdate), str(timezone))
              else:
                self.pubdate = ''

      # Normalization procedure after the scraping, supposes the "pubdate" tag for the NEWS or TEMPLATE scraping.
      if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_PUBDATE:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_PUBDATE and self.pubdate is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_PUBDATE:
          pubdate, tzone = self.normalizeDatetime(response, self.algorithm_name)
          if pubdate is not None:
            self.pubdate = pubdate
            timezone = tzone
            self.logger.debug("Pubdate from 'pubdate': " + str(self.pubdate) + " timezone: " + str(timezone))

      # Current date (SQL NOW())
      if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_NOW:
        if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_NOW and self.pubdate is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_NOW:
          self.pubdate = SQLExpression("NOW()")  # pylint: disable=R0204
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
#       self.input_data.batch_item.urlObj.pDate = self.pubdate
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

      self.logger.debug("!!! self.pubdate: %s", str(self.pubdate))
#       self.logger.debug("!!! response.tags: %s", varDump(response.tags))

      # apply content of 'pubdate' before formatOutputData
      self.applyPubdate(response, self.pubdate)

      # Add tag 'feed_url'
      feedUrl = self.extractFeedUrlRssFeed(self.input_data.siteId, self.input_data.url)
      if feedUrl is not None:
        self.addCustomTag(result=response, tag_name=CONSTS.TAG_FEED_URL, tag_value=[feedUrl])

      self.logger.debug("!!! befor formatOutputData response: %s", varDump(response))

      if self.outputFormat is None:
        self.logger.debug(">>> Warning, can't extract output format")
      else:
        self.formatOutputData(response, self.outputFormat)

      response.recalcTagMaskCount(None, self.altTagsMask)
      self.tagsCount = response.tagsCount
      self.tagsMask = response.tagsMask
      # self.putArticleToDB({"default":response})
      self.logger.debug("self.tagsCount: " + str(self.tagsCount) + " self.tagsMasks: " + str(self.tagsMask))

      response.finish = time.time()
      response.data["time"] = "%s" % (response.finish - response.start)

      response = self.applyHTTPRedirectLink(self.input_data.batch_item.siteId, self.input_data.batch_item.urlObj.url,
                                            self.input_data.batch_item.properties, response)

    self.getProcessedContent(responses)


  # # Apply pubdate for processed content
  #
  # @param response - Scraper result instance for response
  # @param pubdate - pubdate value for apply
  # @return - None
  def applyPubdate(self, response, pubdate):
    if isinstance(pubdate, SQLExpression) and str(pubdate) == "NOW()":
      pubdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
      d = DateTimeType.parse(pubdate, bool(self.useCurrentYear), self.logger, False)
      self.logger.debug("Check pubdate: '%s'", str(d))
      if d is not None:
        pubdate = d.strftime("%Y-%m-%d %H:%M:%S")
      else:
        pubdate = ''

    if "pubdate" in response.tags and "data" not in response.tags["pubdate"]:
      response.tags["pubdate"]["data"] = []

    if "pubdate" in response.tags and "data" in response.tags["pubdate"]:
      if len(response.tags["pubdate"]["data"]) > 0:
        response.tags["pubdate"]["data"][0] = pubdate
      else:
        response.tags["pubdate"]["data"] = [pubdate]

    if "pubdate" not in response.tags:
      self.addCustomTag(result=response, tag_name=CONSTS.TAG_PUB_DATE, tag_value=[pubdate])


  def preparseResponse(self, response):
    for key in response.tags:
      if "data" in response.tags[key]:
        if isinstance(response.tags[key]["data"], basestring):
          localStr = response.tags[key]["data"]
          response.tags[key]["data"] = []
          response.tags[key]["data"].append(localStr)


  def formatOutpuElement(self, elem, localOutputFormat):
    ret = elem
    if localOutputFormat == "json":
      localStr = json.dumps(elem, ensure_ascii=False, encoding='utf-8')

      if len(localStr) > 0:
        if localStr[0] == '\"' or localStr[0] == '\'':
          localStr = localStr[1:]
        if localStr[-1] == '\"' or localStr[-1] == '\'':
          localStr = localStr[0:-1]

      ret = localStr
    elif localOutputFormat == "html" or localOutputFormat == "xml":
      ret = xml.sax.saxutils.escape(elem, {"'": "&apos;", "\"" : "&quot;"})
    elif localOutputFormat == "sql":
      # ret = mdb.escape_string(elem)  # pylint: disable=E1101
      ret = Utils.escape(elem)

    return ret


  def formatOutputData(self, response, localOutputFormat):
    for key in response.tags:
      if "data" in response.tags[key]:
        if isinstance(response.tags[key]["data"], list):
          for i, elem in enumerate(response.tags[key]["data"]):
            if len(response.tags[key]["data"]) > i:
              response.tags[key]["data"][i] = self.formatOutpuElement(elem, localOutputFormat)

        elif isinstance(response.tags[key]["data"], str) or isinstance(response.tags[key]["data"], unicode):
          response.tags[key]["data"] = self.formatOutpuElement(response.tags[key]["data"], localOutputFormat)


  def getTemplate(self, explicit=True):
    if isinstance(self.input_data.template, dict):
      template = self.input_data.template
    else:
      # template = ast.literal_eval(self.input_data.template)
      # TODO:strange potential backdoor for malicious code, cancelled by bgv
      if explicit:
        self.logger.error("Wrong template structure: `%s` but dict expected, assumed empty!",
                          str(type(self.input_data.template)))
        self.logger.debug("Template:\n%s", str(self.input_data.template))
      template = {}

    return template


  def postprocessing(self, result, rule, tag):
    self.logger.debug("!!! rule: '%s'", varDump(rule))
    if rule.get('postProcessing') is not None and rule["postProcessing"] != "":
      self.logger.debug("Post-processing applied for tag `%s` with expression: %s",
                        str(tag), str(rule["postProcessing"]))
      self.applyPostProcessing(result, tag, rule["postProcessing"])
    else:
      self.logger.debug("Post-processing is not applied for tag `%s`", str(tag))


  # # template extraction processing
  #
  # @param config - config parser
  # @param urlHost - domain name
  # @return resultsList - list of Result
  def templateExtraction(self, config, urlHost):
    resultsList = []

    self.extractor = ScrapyExtractor(config, self.input_data.template, urlHost)
    result = Result(None, self.input_data.urlId, self.metrics)
    sel = SelectorWrapper(text=self.input_data.raw_content)
    template = self.getTemplate()
    for tag in template:
      self.logger.debug("Template tag: " + tag)
      if "state" in template[tag] and not bool(int(template[tag]["state"])):
        self.logger.debug("Tag skipped because state disabled, name: %s", str(tag))
        continue
      xPathPreparing = TemplateExtractorXPathPreparing(self.properties[CONSTS.TAG_MARKUP_PROP_NAME] \
                                                      if CONSTS.TAG_MARKUP_PROP_NAME in self.properties else None)
      for rule in template[tag]:
        if not isinstance(rule, dict):
          self.logger.error("Rule skipped because wrong structure - is not dict() type: %s", str(type(rule)))
          continue
        if "attributesExclude" in rule:
          try:
            if rule["attributesExclude"] != "":
              self.attrConditions = json.loads(rule["attributesExclude"])
          except Exception as err:
            self.logger.error("Feature of attributesExclude ignored because wrong structure: %s", str(err))
            self.attrConditions = None
        else:
          self.attrConditions = None
        xPathPreparing.attrConditions = self.attrConditions
        pathDict = Utils.getPairsDicts(rule)
        isExtract = True
        localResult = Result(None, self.input_data.urlId, self.metrics)
        # Added new template format conversion
        xpath = None
        xpathValue = None
        self.logger.debug(">>> self.properties: " + varDump(self.properties))
        # Added new template type specification
        self.xpathSplitString = xPathPreparing.resolveDelimiter(rule, self.properties, self.xpathSplitString)
        innerDelimiter = xPathPreparing.resolveInnerDelimiter(rule, self.properties)
        self.logger.debug(">>> xpathSplitString: '" + str(self.xpathSplitString) + "'")
        self.logger.debug(">>> innerDelimiter: '" + str(innerDelimiter) + "'")
        try:
          xpath, xpathValue = xPathPreparing.process(rule, sel, self.xpathSplitString, innerDelimiter)
        except Exception as excp:
          ExceptionLog.handler(self.logger, excp, "Rule/xpath exception: ", (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
          continue
        self.logger.debug("xpath: `%s`, xpathType: `%s`, xpathValue: `%s`",
                          str(xpath), str(type(xpathValue)), str(xpathValue))
        if (isinstance(xpathValue, list) and len(xpathValue) == 0) or\
          (isinstance(xpathValue, basestring) and xpathValue == ''):
          self.logger.debug(">>> set default xpathValue")
          xpathValue = []
          xpathValue.append(rule["default"])
          isExtract = False
        self.logger.debug("result before:\n%s", varDump(localResult))
        self.extractor.addTag(localResult, tag, xpathValue, xpath, not isExtract, False, rule["type"])
        self.logger.debug("result after:\n%s", varDump(localResult))

        self.logger.debug("Tag type: `%s`, tags data type: `%s`",
                          str(type(localResult.tags)), str(type(localResult.tags[tag]["data"])))
        if tag in localResult.tags and isinstance(localResult.tags[tag]["data"], basestring):
          self.logger.debug("Convert result for tag: `%s`", str(tag))
          localString = localResult.tags[tag]["data"]
          localResult.tags[tag]["data"] = []
          localResult.tags[tag]["data"].append(localString)

        self.formatTag(localResult, rule, tag, pathDict, isExtract)

        if isExtract:
          self.postprocessing(localResult, rule, tag)

        localResult.finish = time.time()

        resultsList.append({"obj": localResult, "join": rule["join"], "isExtract": isExtract, "mandatory":
                            (bool(rule["mandatory"]) if "mandatory" in rule else False),
                            "delimiter": (rule["delimiter"] if "delimiter" in rule else self.xpathSplitString),
                            "type": rule["type"]})

      prepareResultsList = self.prepareResults(resultsList)
      self.compileResults(result, prepareResultsList, tag, xPathPreparing)
      resultsList = []
      result.finish = time.time()

    return [result]


  # # Add custom tag
  #
  # @param result - Scraper result instance
  # @param tag_name - value name of tag
  # @param tag_value - value value of tag
  # @return - None
  def addCustomTag(self, result, tag_name, tag_value):
    if tag_name not in result.tags:
      data = {"extractor": "Base extractor", "data": "", "name": ""}
      data["data"] = tag_value
      data["name"] = tag_name
      data["xpath"] = None
      data["type"] = None
      data["extractor"] = self.__class__.__name__
      result.tags[tag_name] = data


#   def compileResults(self, result, resultsList, key, xPathPreparing=None):
#     for elem in resultsList:
#       if key in result.tags:
#         if result.tags[key]["xpath"] is None:
#           result.tags[key]["xpath"] = elem["obj"].tags[key]["xpath"]
#         else:
#           result.tags[key]["xpath"] += ' '
#           result.tags[key]["xpath"] += elem["obj"].tags[key]["xpath"]
#         if result.tags[key]["data"] is None or len(result.tags[key]["data"]) == 0:
#           result.tags[key]["data"] = elem["obj"].tags[key]["data"]
#         else:
#           if xPathPreparing is not None:
#             self.xpathSplitString = xPathPreparing.resolveDelimiter(elem, self.properties, self.xpathSplitString)
#           result.tags[key]["data"][0] += self.xpathSplitString
#           result.tags[key]["data"][0] += elem["obj"].tags[key]["data"][0]
#       else:
#         result.tags.update(elem["obj"].tags)

  def compileResults(self, result, resultsList, key, xPathPreparing=None):
    for elem in resultsList:
      if key in result.tags:
        if result.tags[key] is not None:
          if result.tags[key]["xpath"] is None:
            result.tags[key]["xpath"] = elem["obj"].tags[key]["xpath"]
          else:
            result.tags[key]["xpath"] += ' '
            result.tags[key]["xpath"] += elem["obj"].tags[key]["xpath"]
          if result.tags[key]["data"] is None or len(result.tags[key]["data"]) == 0:
            result.tags[key]["data"] = elem["obj"].tags[key]["data"]
          else:
            if xPathPreparing is not None:
              self.xpathSplitString = xPathPreparing.resolveDelimiter(elem, self.properties, self.xpathSplitString)
              result.tags[key]["data"][0] += self.xpathSplitString
            else:
              result.tags[key]["data"][0] += ' '
            result.tags[key]["data"][0] += elem["obj"].tags[key]["data"][0]
      else:
        result.tags.update(elem["obj"].tags)


  def prepareResults(self, resultsList):
    ret = []
    if len(resultsList) > 0:
      localElemWeight = 0
      firstElemWeight = 0
      firstElem = None
      tempList = []
      for elem in resultsList:
        localElemWeight = 0
        if elem["join"] == "concat":
          tempList.append(elem)
        else:
          if elem["mandatory"]:
            #>>> Mandatory breaking block -------------
            if not elem["isExtract"]:
              return []
            #-------------
            localElemWeight = localElemWeight | CONSTS.TAGS_RULES_MASK_MANDATORY_FIELD
          if elem["join"] == "best":
            localElemWeight = localElemWeight | CONSTS.TAGS_RULES_MASK_RULE_PRIORITY
          if elem["isExtract"]:
            localElemWeight = localElemWeight | CONSTS.TAGS_RULES_MASK_DEFAULT_VALUE

          self.logger.debug(">>> Rule weight = " + str(localElemWeight))
          self.logger.debug(">>> Rule join = " + elem["join"])
          if localElemWeight > firstElemWeight:
            firstElemWeight = localElemWeight
            firstElem = elem

      if firstElem is not None:
        tempList = [firstElem] + tempList
      isExtractResults = any([elem["isExtract"] for elem in tempList])
      if isExtractResults:
        ret = [elem for elem in tempList if elem["isExtract"]]
      elif len(tempList) > 0:
        ret.append(tempList[0])
    return ret


  # #elemUrlsCanoizator canonizates incoming string buf as url string, parses it before by " " and " " symbols
  #
  # @param data - incoming string/strings list buffer
  # @param baseUrl - base url
  # @return - canonizated url string
  def elemUrlsCanoizator(self, data, baseUrl=None, firstDelim=' ', secondDelim=',', useAdditionEncoding=False):
    normMask = UrlNormalizator.NORM_NONE
    if "URL_NORMALIZE_MASK_PROCESSOR" in self.properties:
      normMask = int(self.properties["URL_NORMALIZE_MASK_PROCESSOR"])

    ret = data
    if data.strip() != "":
      ret = ""
      for elem in data.split(firstDelim):
        if elem.strip() != "":
          localUrl = elem
          if baseUrl is not None:
#             localUrl = urlparse.urljoin(baseUrl, localUrl)
            localUrl = urlNormalization(baseUrl, localUrl)
          processedUrl = dc_event.URL(0, localUrl, normalizeMask=normMask).getURL(normMask)
          if useAdditionEncoding:
            processedUrl = xml.sax.saxutils.escape(processedUrl, {})
          ret += processedUrl + secondDelim
      if ret != "" and ret[-1] == secondDelim:
        ret = ret[0: len(ret) - 1]
    return ret


  # #dataUrlsCanonizator canonizates incoming string/list as url string
  #
  # @param data - incoming string/strings list buffer
  # @param baseUrl - base url
  # @return - canonizated url string
  def dataUrlsCanonizator(self, data, baseUrl=None, useAdditionEncoding=False):
    ret = data
    # self.logger.debug(">>> url canonizator = " + str(data))
    if isinstance(data, basestring):
      ret = self.elemUrlsCanoizator(data, baseUrl, useAdditionEncoding=useAdditionEncoding)
    elif isinstance(data, list):
      ret = []
      for elem in data:
        elem = self.elemUrlsCanoizator(elem, baseUrl, useAdditionEncoding=useAdditionEncoding)
        ret.append(elem)
    return ret


  # # formatTag
  #
  def formatTag(self, result, path, key, pathDict, isExtract):
    # Andrey Add
    self.logger.debug("Tag name: '%s', tag type: %s, tag format: '%s'",
                      str(key), str(path["type"]), str(path["format"]))
    # Add End
    if path["type"] == "text":
      localText = ''
      for elem in result.tags[key]["data"]:
        localText += (elem.strip() + self.xpathSplitString)
      localText = localText.strip(self.xpathSplitString)
      localMaxCh = None
      if "format" in pathDict and "maxCh" in pathDict["format"]:
        localMaxCh = pathDict["format"]["maxCh"]
        self.logger.debug("!!! get localMaxCh from pathDict[\"format\"][\"maxCh\"] = %s", str(localMaxCh))
      else:
        localMaxCh = path["format"]
        if isinstance(localMaxCh, basestring) and localMaxCh == "":
          localMaxCh = 0
        self.logger.debug("!!! get localMaxCh from [\"format\"] = %s", str(localMaxCh))

      try:
        if localMaxCh is not None and int(localMaxCh) > 0 and len(localText) > int(localMaxCh):
          localText = localText[0: int(localMaxCh)]
      except ValueError, err:
        self.logger.debug("!!! Use wrong value, error: %s", str(err))

      result.tags[key]["data"] = []
      result.tags[key]["data"].append(localText)
    elif path["type"] == "html":
      # >>> html
      for i, elem in enumerate(result.tags[key]["data"]):
        result.tags[key]["data"][i] = re.sub(r"\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>", "", elem)
      self.logger.debug(">>> After RE = " + str(result.tags[key]["data"]))
#       # # apply post processing algorithm
#       self.postprocessing(result, path, key)
      # >>> html END
    elif path["type"] == "datetime":
      # >>> datetime
      bestData = ''
      try:
        self.logger.debug("Try to convert data")
        if not isExtract:
        # New use default value as a format string for current date
          if len(result.tags[key]["data"][0]) > 0 and result.tags[key]["data"][0][0] == '@':
            localFormatStr = result.tags[key]["data"][0][1: len(result.tags[key]["data"][0])]
            localTm = datetime.datetime.fromtimestamp(time.time())
            result.tags[key]["data"][0] = datetime.datetime.strftime(localTm, localFormatStr)
        else:
          bestData = self.getBestDatatimeData(result.tags[key]["data"])
          self.logger.debug(">>> Time log Before = " + bestData)
          if path["format"] != "" and path["format"] != "FULL":
            result.tags[key]["data"][0] = datetime.datetime.strftime(parser.parse(bestData), path["format"])
          else:
            result.tags[key]["data"][0] = str(parser.parse(bestData))
        self.logger.debug(">>> Time log after = " + result.tags[key]["data"][0])
      except Exception as err:
        self.logger.debug("Can't convert data <<< " + str(result.tags) + " " + str(key) + " err = " + str(err))
        result.tags[key]["data"][0] = bestData
      if len(result.tags[key]["data"]) > 0:
        result.tags[key]["data"] = [result.tags[key]["data"][0]]
      # >>> datetime END
    elif path["type"] == "image":
      if path["format"] == "URL" and "canonicalizeURLs" in path and int(path["canonicalizeURLs"]) == 1:
        result.tags[key]["data"] = self.dataUrlsCanonizator(result.tags[key]["data"], self.baseUrl)
    elif path["type"] == "link":
      formatName = path["format"]
      if len(formatName.split(',')) > 1:
        formatName = formatName.split(',')[1]
      if formatName == "email-address" or formatName == "email-to":
        localText = ''
        if isinstance(result.tags[key]["data"], basestring):
          self.logger.debug(">>> mail to str type")
          localText = result.tags[key]["data"].strip(self.xpathSplitString)
          index = localText.find("mailto:")
          if index >= 0:
            localText = localText[index + len("mailto:"), len(localText)]
          else:
            localText = ""
        elif isinstance(result.tags[key]["data"], list):
          self.logger.debug(">>> mail to list type")
          for elem in result.tags[key]["data"]:
            elemText = elem.strip(self.xpathSplitString)
            index = elemText.find("mailto:")
            if index >= 0:
              elemText = elemText[index + len("mailto:"): len(elemText)]
              if formatName == "email-address":
                elemText = Utils.emailParse(elemText)
              else:
                elemText = Utils.emailParse(elemText, True)
            else:
              elemText = ""
            if elemText != "":
              localText += (elemText + self.xpathSplitString)

        result.tags[key]["data"] = []
        result.tags[key]["data"].append(localText)
      if "canonicalizeURLs" in path and int(path["canonicalizeURLs"]) == 1:
        result.tags[key]["data"] = self.dataUrlsCanonizator(result.tags[key]["data"], self.baseUrl)
    elif path["type"] == "attribute":
      if isExtract:
        localText = ''
        if isinstance(result.tags[key]["data"], basestring):
          localText = result.tags[key]["data"]
        elif isinstance(result.tags[key]["data"], list):
          localText = self.xpathSplitString.join([elem for elem in result.tags[key]["data"] if elem != ''])
        splittedFormatString = path["format"].split(',')
        if len(splittedFormatString) >= 2:
          try:
            if int(splittedFormatString[0]) < len(localText):
              localText = localText[0: int(splittedFormatString[0])]
          except Exception as err:
            self.logger.debug("Error: %s; Wrong path format for attribute rule, format=%s", str(err), path["format"])
        result.tags[key]["data"] = []
        result.tags[key]["data"].append(localText)

    localElem = ''
    for elem in result.tags[key]["data"]:
      localElem += elem
      localElem += self.xpathSplitString
    result.tags[key]["data"][0] = localElem
    result.tags[key]["data"][0] = result.tags[key]["data"][0].strip(self.xpathSplitString)


  def applyPostProcessing(self, result, key, postProcessingRE):
    if key in result.tags and "data" in result.tags[key] and result.tags[key]["data"] is not None and \
      len(result.tags[key]["data"]) > 0:
      try:
        matchingVal = re.compile(postProcessingRE)  # #, re.UNICODE | re.MULTILINE)
      except re.error as err:
        self.logger.debug("Post-processing RE error: %s", str(err))
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_RE_ERROR
      else:
        self.logger.debug("!!! type(result.tags[%s][\"data\"] = %s", str(key), type(result.tags[key]["data"]))

        tmpStr = ""
        matchingResult = []
        if isinstance(result.tags[key]["data"], basestring):
          matchingResult = matchingVal.findall(result.tags[key]["data"])
        elif isinstance(result.tags[key]["data"], list):
          # accumulate all results
          for tagData in result.tags[key]["data"]:
            self.logger.debug("!!! type(tagData) = %s, tagData: %s", str(type(tagData)), varDump(tagData))
            localRes = matchingVal.findall(tagData)
            matchingResult.extend(localRes)
#             match = re.search(postProcessingRE, tagData, re.U | re.M)
#             self.logger.debug("!!! match = %s, postProcessingRE = '%s'", str(match), str(postProcessingRE))
#             if match is not None:
#               matchingResult.append(str(match.group()))

        innerSplitString = '|||||'
        self.logger.debug("Post-processing has %s matched results!", str(len(matchingResult)))
        self.logger.debug("Post-processing matchingResult: %s", varDump(matchingResult))
        if len(matchingResult) > 0:
          for elem in matchingResult:
            if isinstance(elem, basestring):
              tmpStr += str(elem)
              tmpStr += self.xpathSplitString
            else:
              for innerElem in elem:
                if innerElem is not None and innerElem != '':
                  tmpStr += str(innerElem)
                  tmpStr += innerSplitString
        else:
          self.logger.debug("Post-processing has no matched results!")

        tmpStr = tmpStr.strip(self.xpathSplitString)
        if tmpStr != "":
          self.logger.debug("Post-processing matched and replaced with pieces!")
          self.logger.debug("!!! type(result.tags[%s][\"data\"])) = %s", str(key), str(type(result.tags[key]["data"])))
          self.logger.debug("!!! tmpStr: %s", varDump(tmpStr))
          if isinstance(result.tags[key]["data"], basestring):
            result.tags[key]["data"] = tmpStr
#           else:
#             result.tags[key]["data"][0] = tmpStr
          elif isinstance(result.tags[key]["data"], list):
            result.tags[key]["data"] = matchingResult  # #tmpStr.split(innerSplitString)
        else:
          # Set not detected value if no match, changed default behavior by bgv
          self.logger.debug("Post-processing not matched, value replaced with None or empty!")
          if isinstance(result.tags[key]["data"], basestring):
            result.tags[key]["data"] = ''
          else:
            result.tags[key]["data"][0] = None
    else:
      self.logger.debug("Post-processing keys not found!")


  def processingHTMLData(self, htmlBuf, bufFormat):
    ret = htmlBuf
    if bufFormat.find("NO_SCRIPT") >= 0:
      ret = Utils.stripHTMLComments(htmlBuf, soup=None)
    if bufFormat.find("NO_META") >= 0:
      pass
    if bufFormat.find("NO_COMMENTS") >= 0:
      pass
    if bufFormat.find("ENTITIES_ENCODED") >= 0:
      pass
    return ret


  def getBestDatatimeData(self, data):
    ret = ""
    if isinstance(data, list):
      for elem in data:
        for ch in elem:
          if ch >= '0' and ch <= '9':
            ret = elem
            break
        if ret is not None:
          break
      if ret is None:
        ret = data[0]
    else:
      ret = data
    if isinstance(ret, basestring):
      ret = ret.replace('\n', '')
      ret = ret.replace('\t', '')
    else:
      ret = ""
    return ret


  def newsExtraction(self):
    ret = []

    template = self.getTemplate(explicit=False)

    # get resource as dictionary
    resource_set = {}
    resource_set["url"] = self.input_data.url
    resource_set["resId"] = self.input_data.urlId
    resource_set["siteId"] = self.input_data.siteId
    resource_set["raw_html"] = self.input_data.raw_content
    resource = Resource(resource_set)

    collectResult = Result(self.config, self.input_data.urlId, self.metrics)
    blockedByXpathTags = []

    while True:
      self.extractor = self.getNextBestExtractor()
      self.logger.debug("Got best matching extractor: " + str(self.extractor))
      if self.extractor is None:
        self.logger.debug("No more extractors, exiting loop")
        break

      result = Result(self.config, self.input_data.urlId, self.metrics)

      if CONSTS.TAG_MEDIA in collectResult.tags.keys() and \
        not self.extractor.isTagNotFilled(collectResult, CONSTS.TAG_MEDIA):
        self.logger.debug("!!! Check collectResult. Tag 'media' already selected. Copy.")
        result.tags[CONSTS.TAG_MEDIA] = collectResult.tags[CONSTS.TAG_MEDIA]

      result.blockedByXpathTags = blockedByXpathTags
      self.logger.debug(">>> TAG BEGIN extractor = " + str(self.extractor))

      result = self.extractor.extractTags(resource, result)

      self.logger.debug(">>> TAG END")
      empty_tags = result.getEmptyTags()
      self.logger.debug("get list of empty tags from result: " + str(empty_tags))
      filled_tags = result.getFilledTags()
      self.logger.debug("get list of filled_tags from result: " + str(filled_tags))

      self.commonResultOperations(result)
      for tag in result.tags:
        if tag in template:
          for rule in template[tag]:
            self.postprocessing(result, rule, tag)
        if tag not in collectResult.tags or not collectResult.isTagFilled(tag):
          collectResult.tags[tag] = copy.deepcopy(result.tags[tag])
      blockedByXpathTags = result.blockedByXpathTags
      result.finish = time.time()
      ret.append(result)

    collectResult.blockedByXpathTags = blockedByXpathTags
    ret = [collectResult] + ret

    return ret


  def commonResultOperations(self, result):
    empty_tags = result.getEmptyTags()
    for localKey in EXTENDED_NEWS_TAGS:
      if localKey in empty_tags or (localKey in result.tags and result.isTagFilled(localKey) is False):
        self.extractAdditionTagsByScrapy(result, localKey, EXTENDED_NEWS_TAGS[localKey])
    for tagName in LINKS_NEWS_TAGS:
      if tagName in result.tags:
        if isinstance(result.tags[tagName], dict) and (result.tags[tagName]["xpath"] == "" or \
        result.tags[tagName]["xpath"].find("/@src") != -1 or result.tags[tagName]["xpath"].find("/@href") != -1):
          result.tags[tagName]["data"] = \
          self.dataUrlsCanonizator(result.tags[tagName]["data"], self.baseUrl)

    self.refineCommonText(CONSTS.TAG_CONTENT_UTF8_ENCODED, result)
    self.refineBadDateTags(result)


  def replaceLoopValue(self, buf, replaceFrom, replaceTo):
    localValue = buf
    replaceValue = localValue.replace(replaceFrom, replaceTo)
    while len(replaceValue) != len(buf):
      localValue = replaceValue
      replaceValue = localValue.replace(replaceFrom, replaceTo)
    return localValue


  def refineCommonText(self, tagName, result):
    if tagName in result.tags:
      if isinstance(result.tags[tagName], dict):
        localValue = None
        if isinstance(result.tags[tagName]["data"], list) and len(result.tags[tagName]["data"]) > 0:
          localValue = result.tags[tagName]["data"][0]
        elif isinstance(result.tags[tagName]["data"], basestring):
          localValue = result.tags[tagName]["data"]
        if localValue is not None:
          replaceList = None
          if CONSTS.TAG_REDUCE_PROP_NAME in self.properties:
            try:
              replaceList = json.loads(self.properties[CONSTS.TAG_REDUCE_PROP_NAME])
            except Exception:
              self.logger.debug(">>> Bad processor_property json format, [" + CONSTS.TAG_REDUCE_PROP_NAME + "]")
          if replaceList is None:
            replaceList = CONTENT_REPLACEMENT_LIST  # json.loads(CONTENT_REPLACEMENT)

          if CONSTS.TAG_REDUCE_MASK_PROP_NAME in self.properties:
            try:
              self.tagReduceMask = int(self.properties[CONSTS.TAG_REDUCE_MASK_PROP_NAME])
            except Exception:
              self.logger.error("Bad processor property '%s' value: '%s'", CONSTS.TAG_REDUCE_MASK_PROP_NAME,
                                str(self.properties[CONSTS.TAG_REDUCE_MASK_PROP_NAME]))

          self.logger.debug("self.tagReduceMask = %s", str(self.tagReduceMask))
#           self.logger.debug("replaceList: %s", str(replaceList))

          replaceList = [replaceList[i] for i in xrange(len(replaceList)) if 1 << i & self.tagReduceMask]

#           if " " not in replaceList:
#             replaceList.append(" ")
#           self.logger.debug(">>> Repl list = " + str(replaceList))
          for elem in replaceList:
            # self.logger.debug(">>> Value before = " + localValue)
            localValue = Utils.replaceLoopValue(localValue, (elem * 2), elem)
            # self.logger.debug(">>> Value after = " + localValue)
          localValue = localValue.replace("\r", " ")

          if isinstance(result.tags[tagName]["data"], list) and len(result.tags[tagName]["data"]) > 0:
            result.tags[tagName]["data"][0] = localValue
          elif isinstance(result.tags[tagName]["data"], basestring):
            result.tags[tagName]["data"] = localValue


  def extractAdditionTagsByScrapy(self, localResult, key, tagsXpaths):
    self.logger.debug(">>> Start addition news extracting")
    extractor = self.getExtractorByName("ScrapyExtractor")
    if extractor is not None:
      sel = SelectorWrapper(text=self.input_data.raw_content)
      for tagsXpath in tagsXpaths:
        if tagsXpath is not None and tagsXpath != "":
          localXpath = sel.xpath(tagsXpath)
          localValue = Utils.innerText(localXpath, ' ', ' ', self.properties[CONSTS.TAG_MARKUP_PROP_NAME] \
                                       if CONSTS.TAG_MARKUP_PROP_NAME in self.properties else None, None,
                                       self.attrConditions)
          if localValue != "":
            extractor.addTag(localResult, key, localValue, tagsXpath)
            break
          else:
            self.logger.debug(">>> Cant extract tag=%s for xpath=%s" % (key, tagsXpath))


  def getNextBestExtractor(self):
    # return extractor with highest rank
    try:
      extractor = next(self.itr)
    except StopIteration:
      extractor = None
    return extractor


  # #getProcessedContent
  #
  def getProcessedContent(self, result):
    for elem in result:
      elem.get()

#     self.logger.info("!!! result[0].tags[\"content_encoded\"][\"data\"][0]: %s",
#                      str(result[0].tags["content_encoded"]["data"][0]))

#     if "content_encoded" in result[0].tags and "data" in result[0].tags["content_encoded"] and \
#     len(result[0].tags["content_encoded"]["data"]) > 0:
#       result[0].tags["content_encoded"]["data"][0] = result[0].tags["content_encoded"]["data"][0].replace('\\n', '\n')

    self.processedContent = {}
    self.processedContent["default"] = result[0]
    self.processedContent["internal"] = result
    self.processedContent["custom"] = []
    self.tagsCount = result[0].tagsCount
    self.tagsMask = result[0].tagsMask

# #TODO remove in future ## checked now
    if "pubdate" in result[0].tags and "data" in result[0].tags["pubdate"] and \
    len(result[0].tags["pubdate"]["data"]) > 0:
      self.pubdate = result[0].tags["pubdate"]["data"][0]
      self.logger.debug('>>>> Set self.pubdate =  ' + str(self.pubdate))
      self.input_data.batch_item.urlObj.pDate = self.pubdate


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


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    # logger
    for entry in self.message_queue:
      self.logger.debug(entry)

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
      # self.logger.debug("self.input_data:\n%s", varDump(self.input_data))
      self.urlHost = self.calcUrlDomainCrc(self.input_data.url)

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
      # check properties in input data
      try:
        if (self.input_data is not None) and (self.input_data.processor_properties is not None):
          processor_properties = self.input_data.processor_properties
          # self.logger.debug("Processor's properties was taken from input data: %s" % processor_properties)
          # self.logger.debug("Processor's properties type: %s" % str(type(processor_properties)))
          if not isinstance(processor_properties, dict):
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

      self.logger.info("Process with extractor algorithm: " + str(self.algorithm_name))
      # SUPPORT METRICS ALGORITHTM
      # if self.algorithm_name == CONSTS.PROCESS_ALGORITHM_METRIC:
        # self.processMetrics()
      # SUPPORT FEED_PARSER ALGORITHTM
      if self.algorithm_name == CONSTS.PROCESS_ALGORITHM_FEED_PARSER:
        self.feedParserProcess()
      else:
        self.process(self.config)

      # send response to the stdout
      sys.stdout = tmp

      scraperResponse = ScraperResponse(self.tagsCount, self.tagsMask, self.pubdate, self.processedContent,
                                        self.errorMask)
#       self.logger.debug("scraperResponse:\n%s", varDump(scraperResponse))

      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        output_pickled_object = pickle.dumps(scraperResponse)
        Utils.storePickleOnDisk(output_pickled_object, ENV_SCRAPER_STORE_PATH,
                                "scraper.out." + str(self.input_data.urlId))
        print output_pickled_object
        sys.stdout.flush()
      else:
        self.output_data = scraperResponse

    except Exception as err:
      ExceptionLog.handler(self.logger, err, 'Scraper process batch error:')
      self.exitCode = EXIT_FAILURE
      raise Exception('Scraper process batch error:' + str(err))



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
          self.config.read(APP_NAME)
      else:
        self.config.read(self.configFile)
    except:
      print MSG_ERROR_LOAD_CONFIG
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
      class_name = self.__class__.__name__
      self.scraperPropFileName = self.config.get("Application", "property_file_name")
      # DBWrapper initialization
      dbTaskIniConfigFileName = self.config.get(self.__class__.__name__, "db-task_ini")
      config = ConfigParser.ConfigParser()
      config.optionxform = str
      readOk = config.read(dbTaskIniConfigFileName)
      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + dbTaskIniConfigFileName)
      self.dbWrapper = DBTasksWrapper(config)

      # url sources rules initialization
      urlSourcesList = self.config.get(self.__class__.__name__, OPTION_SECTION_URL_SOURCES_RULES)
      if isinstance(urlSourcesList, basestring):
        self.urlSourcesRules = [urlSourcesRule.strip() for urlSourcesRule in urlSourcesList.split(',')]
      self.logger.debug("Initialization urlSourcesRules: %s", varDump(self.urlSourcesRules))

      self.sqliteTimeout = self.config.getint("sqlite", "timeout")

      self.useCurrentYear = self.config.getint("DateTimeType", "useCurrentYear")

      self.tagsTypes = self.config.get(class_name, OPTION_SECTION_TAGS_TYPE)

      if self.config.has_section(OPTION_SECTION_DATETIME_NEWS_NAMES):
        self.datetimeNewsNames = []
        for item in self.config.items(OPTION_SECTION_DATETIME_NEWS_NAMES):
          self.datetimeNewsNames.append(item[0])
      else:
        self.logger.debug("Config file hasn't section: " + str(OPTION_SECTION_DATETIME_NEWS_NAMES))
        self.datetimeNewsNames = TAGS_DATETIME_NEWS_NAMES

      if self.config.has_section(OPTION_SECTION_DATETIME_TEMPLATE_TYPES):
        self.datetimeTemplateTypes = []
        for item in self.config.items(OPTION_SECTION_DATETIME_TEMPLATE_TYPES):
          self.datetimeTemplateTypes.append(item[0])
      else:
        self.logger.debug("Config file hasn't section: " + str(OPTION_SECTION_DATETIME_TEMPLATE_TYPES))
        self.datetimeTemplateTypes = TAGS_DATETIME_TEMPLATE_TYPES
    except:
      print MSG_ERROR_LOAD_OPTIONS
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


  # #createApp
  # create application's pool
  #
  # @param app_name application name which instance will be created
  # @return instance of created application
  def createModule(self, module_name):
    appInst = None
    try:
#       appInst = (module_name, eval(module_name)(self.config, None, self.urlHost, self.properties))[1]  # pylint: disable=W0123
      appInst = (module_name, eval(module_name)(self.config,
                                                None,
                                                self.getDomainsForUrlSourcesRules(self.urlSourcesRules),
                                                self.properties))[1]
      self.logger.debug("%s has been created!" % module_name)
    except Exception as err:
      ExceptionLog.handler(self.logger, err, "Can't create module %s. Error is:" % (module_name))

    return appInst


  # #createApp
  # create application's pool
  #
  # @param app_name application name which instance will be created
  # @return instance of created application
  def getExtractorByName(self, extractorName):
    for extractor in self.extractors:
      if extractor.__class__.__name__ == extractorName:
        return extractor


  # #
  #
  #
  def getExitCode(self):
    return self.exitCode

  #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  # FeedParser section
  #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  # #main content processing
  # main content processing
  #
  def feedParserProcess(self):
    self.logger.debug("URL: %s" % str(self.input_data.url))
    self.logger.debug("URLMd5: %s" % str(self.input_data.urlId))
    self.logger.debug("SiteId: %s" % str(self.input_data.siteId))
    if self.parseFeed():
      self.tagsCount = self.article.tagsCount
      self.tagsMask = self.article.tagsMask
      self.processedContent = self.article.get()
      # correct pubdate
      if CONSTS.PUBLISHED in self.article.tags:
        # self.pubdate = parse(self.article.tags[CONSTS.PUBLISHED]["data"]).strftime(CONSTS.COMMON_DATE_FORMAT)
        self.pubdate = DateTimeType.parse(self.article.tags[CONSTS.PUBLISHED]["data"], bool(self.useCurrentYear), \
                                          self.logger)
      else:
        self.logger.debug("Resource %s hasn't publish date" % str(self.article.tags[CONSTS.TAG_LINK]["data"]))
    else:
      self.logger.debug("Resource hasn't raw content. Exit.")


  # #main content processing
  # main content processing
  #
  def createArticle(self):
    resid = self.entry["urlMd5"]
    self.article = Result(self.config, resid, self.metrics)

    for tag in self.entry["entry"]:
      data = {"extractor":"feedParser extractor", "data":"", "name":""}
      data["data"] = self.entry["entry"][tag]
      data["name"] = tag
      self.article.tags[tag] = data

    date_tags = ["published", "updated", "updated_parsed"]
    if len(set(self.entry["entry"].keys()).intersection(date_tags)) == 0:
      self.logger.debug("PUBDATE_ERROR: list of tags from rss feed: %s" % str(self.entry["entry"].keys()))

    if "pubdate" in self.entry and self.article.tags["pubdate"] == "":
      data = {"extractor":"feedParser extractor", "data":"", "name":""}
      data["data"] = self.entry["pubdate"]
      data["name"] = "pubdate"
      self.article.tags["pubdate"] = data

    # parent rss feed
    data = {"extractor":"feedParser extractor", "data":"", "name":""}
    data["data"] = self.entry["parent_rss_feed"]
    data["name"] = "parent_rss_feed"
    data["xpath"] = ""
    data["extractor"] = self.__class__.__name__
    self.article.tags["parent_rss_feed"] = data

    # parent rss feed urlMd5
    data = {"extractor":"feedParser extractor", "data":"", "name":""}
    data["data"] = self.entry["parent_rss_feed_urlMd5"]
    data["name"] = "parent_rss_feed_urlMd5"
    data["xpath"] = ""
    data["extractor"] = self.__class__.__name__
    self.article.tags["parent_rss_feed_urlMd5"] = data

    # tags count
    self.article.tagsCount = len(self.article.tags.keys())


  # #main content processing
  # main content processing
  #
  def parseFeed(self):
    ret = True
    try:
      self.entry = json.loads(self.input_data.raw_content)
      self.createArticle()
      self.putArticleToDB({"default":self.article})  # pylint: disable=E1101
    except ValueError, err:
      ExceptionLog.handler(self.logger, err, 'Bad raw content:', (self.input_data.raw_content), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      ret = False

    return ret


  # # Extract pubdate rss feed from header
  #
  # @param siteId - Site/Project ID
  # @param url - url string
  # @return pubdate from rss feed
  def extractPubdateRssFeed(self, siteId, url):
    # variable for result
    pubdate = None
    timezone = ''

    self.logger.debug("!!! siteId: %s, url: %s", str(siteId), str(url))
    headerContent = self.getHeaderContent(siteId, url)
    rawPubdate = self.getVariableFromHeaderContent(headerContent, CRAWLER_CONSTS.pubdateRssFeedHeaderName)

#     self.logger.debug('!!! getVariableFromHeaderContent: ' + str(rawPubdate))
    if rawPubdate is not None:
      try:
        dt = DateTimeType.parse(rawPubdate, True, self.logger, False)
        if dt is not None:
          dt, timezone = DateTimeType.split(dt)
          pubdate = dt.strftime("%Y-%m-%d %H:%M:%S")

          if timezone is '':
            timezone = '+0000'
      except Exception, err:
        self.logger.debug("Unsupported date format: '%s', error: %s", str(rawPubdate), str(err))

    return pubdate, timezone


  # # Extract feed url of rss feed from header
  #
  # @param siteId - Site/Project ID
  # @param url - url string
  # @return feed url
  def extractFeedUrlRssFeed(self, siteId, url):
    # variable for result
    ret = None

    self.logger.debug("!!! siteId: %s, url: %s", str(siteId), str(url))
    headerContent = self.getHeaderContent(siteId, url)
    if headerContent is not None:
      ret = self.getVariableFromHeaderContent(headerContent, CRAWLER_CONSTS.rssFeedUrlHeaderName)

    self.logger.debug('!!! ret: ' + str(ret))

    return ret


  # # Extract base url from header
  #
  # @param siteId - Site/Project ID
  # @param url - url string
  # @return base url
  def extractBaseUrlRssFeed(self, siteId, url):
    # variable for result
    ret = None

    self.logger.debug("!!! siteId: %s, url: %s", str(siteId), str(url))
    headerContent = self.getHeaderContent(siteId, url)
    if headerContent is not None:
      ret = self.getVariableFromHeaderContent(headerContent, CRAWLER_CONSTS.baseUrlHeaderName)

    self.logger.debug('!!! ret: ' + str(ret))

    return ret


  # # Get header content
  #
  # @param siteId - Site/Project ID
  # @param url - url string
  # @return extracted header content
  def getHeaderContent(self, siteId, url):
    # variable for result
    headerContent = None
    urlContentObj = dc_event.URLContentRequest(siteId, url, \
                                      dc_event.URLContentRequest.CONTENT_TYPE_RAW_LAST + \
                                      dc_event.URLContentRequest. CONTENT_TYPE_RAW + \
                                      dc_event.URLContentRequest.CONTENT_TYPE_HEADERS)

    rawContentData = self.dbWrapper.urlContent([urlContentObj])

    if rawContentData is not None and len(rawContentData) > 0:
      if rawContentData[0].headers is not None and len(rawContentData[0].headers) > 0 and \
        rawContentData[0].headers[0] is not None:
        headerContent = rawContentData[0].headers[0].buffer

    return headerContent


  # #Get variable from header content
  #
  # @param headerContent - header content
  # @param name - variable name
  # @param makeDecode - boolean flag necessary decode
  # @return extracted value of incoming name (for sample 'Location')
  def getVariableFromHeaderContent(self, headerContent, name, makeDecode=True):
    # variable for result
    ret = None

    header = ''
    if isinstance(headerContent, basestring):
      if makeDecode:
        header = base64.b64decode(headerContent)
      else:
        header = headerContent

      headerList = header.split('\r\n')
      self.logger.debug("headerList: " + varDump(headerList))

      for elem in headerList:
        pos = elem.find(name + ':')
#         self.logger.debug("!!! name: '%s', pos = %s", str(name), str(pos))
        if pos > -1:
          ret = elem.replace(name + ':', '').strip()
          self.logger.debug("Found  '" + name + "' has value: " + str(ret))
          break

    return ret


  # # change month orden in pubdate if neccessary
  #
  # @param rawPubdate - raw pubdate string in iso format. sample: '2016-02-07 16:28:00'
  # @param properties - properties from PROCESSOR_PROPERTIES
  # @param urlString - url string value
  # @return pubdate and timezone if success or None and empty string
  def pubdateMonthOrder(self, rawPubdate, properties, urlString):
    # variables for result
    pubdate = rawPubdate

    self.logger.debug('pubdateMonthOrder() enter... rawPubdate: ' + str(rawPubdate))
    if CONSTS.PDATE_DAY_MONTH_ORDER_NAME in properties and isinstance(rawPubdate, basestring):
      propertyObj = []
      try:
        self.logger.debug('inputted ' + CONSTS.PDATE_DAY_MONTH_ORDER_NAME + ':' + \
                          str(properties[CONSTS.PDATE_DAY_MONTH_ORDER_NAME]))
        propertyObj = json.loads(properties[CONSTS.PDATE_DAY_MONTH_ORDER_NAME])
      except Exception, err:
        self.logger.error("Fail loads '%s', error: %s", str(CONSTS.PDATE_DAY_MONTH_ORDER_NAME), str(err))

      for propertyElem in propertyObj:
        try:
          if "pattern" not in propertyElem:
            raise Exception('Property "pattern" not found')

          if "order" not in propertyElem:
            raise Exception('Property "order" not found')

          pattern = str(propertyElem["pattern"])
          order = int(propertyElem["order"])

          if re.search(pattern, urlString, re.UNICODE) is not None:
            self.logger.debug("Pattern '%s' found in url: %s", str(pattern), str(urlString))

            dt = None
            if order == 0:  # means day follows month
              dt = datetime.datetime.strptime(rawPubdate, "%Y-%d-%m %H:%M:%S")
            elif order == 1:  # means month follows day
              dt = datetime.datetime.strptime(rawPubdate, "%Y-%m-%d %H:%M:%S")
            else:
              raise Exception("Unsupported value of 'order' == " + str(order))

            if dt is not None:
              pubdate = dt.strftime("%Y-%d-%m %H:%M:%S")

        except Exception, err:
          self.logger.error("Fail execution '%s', error: %s", str(CONSTS.PDATE_DAY_MONTH_ORDER_NAME), str(err))

    self.logger.debug('pubdateMonthOrder() leave... pubdate: ' + str(pubdate))

    return pubdate


  # # Check media tag and append to list
  #
  # @param urlStringMedia - url string of media tag
  # @return allowedUrls  list already accumulated allowed url strings
  def checkMediaTag(self, urlStringMedia):
    # variable for result
    allowedUrls = []
    # self.logger.debug("!!! urlStringMedia: %s", varDump(urlStringMedia))
    mediaUrls = self.splitMediaTagString(urlStringMedia)
    # self.logger.debug("!!! mediaUrls: %s", varDump(mediaUrls))

    for media in mediaUrls:
      # Check if media is binary picture
      if re.search(MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR, media, re.UNICODE) is not None:
        self.logger.debug("Tag 'media' has binary picture...")

        if self.mediaLimitsHandler is None:
          allowedUrls.append(media)
        else:
          if self.mediaLimitsHandler.isAllowedLimits(urlString=media, binaryType=True):
            allowedUrls.append(media)
          else:
            self.logger.debug("Binary media tag has not allowed limits. Skipped...")

      # Check is media content valid url
      elif isValidURL(media):
        self.logger.debug("Tag 'media' has valid url: %s", str(media))
        if self.mediaLimitsHandler is None:
          allowedUrls.append(media)
        else:
          if self.mediaLimitsHandler.isAllowedLimits(media):
            allowedUrls.append(media)
          else:
            self.logger.debug("Media tag has not allowed limits. Skipped. Url: %s", str(media))

      # Invalid url of 'media' tag
      else:
        self.logger.debug("Invalid url in tag 'media'... Url: %s", str(media))

    return allowedUrls


  # # Split media tag string
  #
  # @param urlStringMedia - url string of media tag
  # @return list urls extracted from string of media tag
  def splitMediaTagString(self, urlStringMedia):
    # variable for result
    urls = []
    PROTOCOL_STR = 'http'
    DELIMITER_OLD = ','
    DELIMITER_NEW = '|||||'
    urlStringMedia = urlStringMedia.replace(DELIMITER_OLD + PROTOCOL_STR, DELIMITER_NEW + PROTOCOL_STR)
    # temporary string for replace in url string
    REPLACE_STR = 'base64|'
    if urlStringMedia.find(MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR) > -1:
      urlStringMedia = urlStringMedia.replace(MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR, REPLACE_STR)
      urls = urlStringMedia.split(DELIMITER_NEW)
      self.logger.debug("!!! urls before: " + varDump(urls))
      urls = [url.replace(REPLACE_STR, MediaLimitsHandler.BINARY_IMAGE_SEARCH_STR) for url in urls]
      self.logger.debug("!!! urls after: " + varDump(urls))
    else:
      urls = urlStringMedia.split(DELIMITER_NEW)

    return urls


  # # apply http redirect link
  #
  # @param siteId - Site/Project ID
  # @param url - url string
  # @param properties - properties
  # @param response - scraper result object
  # @return response - alredy modified if necessary
  def applyHTTPRedirectLink(self, siteId, url, properties, response):
    if CONSTS.HTTP_REDIRECT_LINK_NAME in properties:
      self.logger.debug("Found property '%s'", str(CONSTS.HTTP_REDIRECT_LINK_NAME))
      propertyValue = int(properties[CONSTS.HTTP_REDIRECT_LINK_NAME])

      self.logger.debug("siteId: %s, url: %s, propertyValue: %s", str(siteId), str(url), str(propertyValue))
#       self.logger.debug("response: %s", varDump(response))

      headerContent = self.getHeaderContent(siteId, url)
      urlValue = self.getVariableFromHeaderContent(headerContent, CONSTS.LOCATION_NAME)
      self.logger.debug("%s value: %s", str(CONSTS.LOCATION_NAME), str(urlValue))

      if propertyValue == CONSTS.HTTP_REDIRECT_LINK_VALUE_URL:
        self.logger.debug("!!! propertyValue & %s", str(CONSTS.HTTP_REDIRECT_LINK_VALUE_URL))

        if CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME in response.tags and \
        "data" in response.tags[CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME] and \
        len(response.tags[CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME]["data"]) > 0:
          response.tags[CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME]["data"][0] = url

      if urlValue is not None and propertyValue == CONSTS.HTTP_REDIRECT_LINK_VALUE_LOCATION:
        self.logger.debug("!!! propertyValue & %s", str(CONSTS.HTTP_REDIRECT_LINK_VALUE_LOCATION))

        if CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME in response.tags and \
        "data" in response.tags[CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME] and \
        len(response.tags[CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME]["data"]) > 0:
          response.tags[CONSTS.HTTP_REDIRECT_LINK_LINK_TAG_NAME]["data"][0] = str(urlValue)

      if urlValue is not None and propertyValue == CONSTS.HTTP_REDIRECT_LINK_VALUE_REDIRECT_URL:
        self.logger.debug("!!! propertyValue & %s", str(CONSTS.HTTP_REDIRECT_LINK_VALUE_REDIRECT_URL))
        self.addCustomTag(result=response, tag_name=CONSTS.REDIRECT_URL_NAME, tag_value=[str(urlValue)])

      if propertyValue == CONSTS.HTTP_REDIRECT_LINK_VALUE_SOURCE_URL:
        self.logger.debug("!!! propertyValue & %s", str(CONSTS.HTTP_REDIRECT_LINK_VALUE_SOURCE_URL))

        if urlValue is not None:
          self.addCustomTag(result=response, tag_name=CONSTS.REDIRECT_URL_NAME, tag_value=[str(urlValue)])
        else:
          self.addCustomTag(result=response, tag_name=CONSTS.REDIRECT_URL_NAME, tag_value=[url])

    return response


  # # get domains accord to url sources rules
  #
  # @param urlSourcesRules - url sources rules
  # @return domains - domains list accord to url sources rules
  def getDomainsForUrlSourcesRules(self, urlSourcesRules):
    self.logger.debug("Incoming value urlSourcesRules: %s", varDump(urlSourcesRules))
    # variable for result
    domains = []

    for urlSourcesRule in urlSourcesRules:
      if urlSourcesRule == URL_SOURCES_RULE_DATA_URL:
        self.logger.debug("dataUrl: %s", str(self.input_data.url))
        self.logger.debug("urlHost: %s", str(self.urlHost))

        domain = self.calcUrlDomainCrc(self.input_data.url)
        self.logger.debug("domain: %s", str(domain))

        if domain is not None:
          domains.append(domain)

      if urlSourcesRule == URL_SOURCES_RULE_REDIRECT_URL:
        headerContent = self.getHeaderContent(self.input_data.siteId, self.input_data.url)
        redirectUrl = self.getVariableFromHeaderContent(headerContent, CONSTS.LOCATION_NAME)
        self.logger.debug("redirectUrl: %s", str(redirectUrl))

        if isinstance(redirectUrl, basestring):
          domain = self.calcUrlDomainCrc(redirectUrl)
          self.logger.debug("domain: %s", str(domain))

          if domain is not None:
            domains.append(domain)

      if urlSourcesRule == URL_SOURCES_RULE_FEED_URL:
        feedUrl = self.extractFeedUrlRssFeed(self.input_data.siteId, self.input_data.url)
        self.logger.debug("feedUrl: %s", str(feedUrl))

        if isinstance(feedUrl, basestring):
          domain = self.calcUrlDomainCrc(feedUrl)
          self.logger.debug("domain: %s", str(domain))

          if domain is not None:
            domains.append(domain)

    if len(domains) == 0:
      domains.append(self.urlHost)

    self.logger.debug("return domains: %s", varDump(domains))

    return domains
