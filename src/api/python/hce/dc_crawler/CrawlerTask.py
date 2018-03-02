# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file CrawlerTask.py
@author scorp <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""
import os.path
import sys
import hashlib
import datetime

try:
  import cPickle as pickle
except ImportError:
  import pickle

import time
from time import strftime

from collections import namedtuple

import signal
import logging.config
import ConfigParser
import re
import types
import copy
import json
import base64
import urlparse
import urllib
import requests
import lxml.etree
import tidylib
from dateutil.parser import parse
from cement.core import foundation
from dc_crawler.CollectURLs import CollectURLs
from dc_crawler.CollectProperties import CollectProperties
from dc_crawler.DetectModified import DetectModified
from dc_crawler.DetectModified import NotModifiedException
from dc_crawler.Fetcher import BaseFetcher
from dc_crawler.FetcherType import FetcherType
from dc_crawler.Fetcher import Response
from dc_crawler.Fetcher import SeleniumFetcher
from dc_crawler.CrawledResource import CrawledResource
from dc_crawler.UrlSchema import UrlSchema
from dc_crawler.Exceptions import SyncronizeException
from dc_crawler.Exceptions import InternalCrawlerException
from dc_crawler.Exceptions import CrawlerFilterException
from dc_crawler.DBTasksWrapper import DBTasksWrapper
from dc_crawler.RobotsParser import RobotsParser
from dc_crawler.RefererHeaderResolver import RefererHeaderResolver
from dc_crawler.HTTPCookieResolver import HTTPCookieResolver
from dc_crawler.RequestsRedirectWrapper import RequestsRedirectWrapper
from dc_crawler.ResourceProcess import ResourceProcess
from dc_crawler.URLProcess import URLProcess
from dc_crawler.DBProxyWrapper import DBProxyWrapper
from dc_crawler.HTTPProxyResolver import HTTPProxyResolver
import dc_crawler.Constants as CONSTS
from app.Utils import varDump
from app.Utils import PathMaker
from app.Filters import Filters
from app.Utils import SQLExpression
from app.LFSDataStorage import LFSDataStorage
from app.HostRequestStorage import HostRequestStorage
from app.DateTimeType import DateTimeType
from app.Exceptions import SeleniumFetcherException
from app.Exceptions import UrlAvailableException
from app.Exceptions import DatabaseException
from app.Exceptions import ProxyException
from app.Utils import ExceptionLog
from app.Utils import UrlNormalizator
from app.Utils import strToProxy
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
from app.ContentEvaluator import ContentEvaluator
import app.Profiler
import app.Consts as APP_CONSTS
import app.Utils as Utils  # pylint: disable=F0401
from app.UrlNormalize import UrlNormalize
import dc.Constants as DC_CONSTS
import dc.EventObjects as dc_event
from dc.EventObjects import Site
from dc.EventObjects import Batch
import dc_processor.Constants as PCONSTS

DB_SITES = "dc_sites"
DB_URLS = "dc_urls"

MSG_ERROR_LOAD_CONFIG = "Error loading config file. Exciting. "
MSG_ERROR_LOAD_OPTIONS = "Error loading options. Exciting. "
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Can't load logging config file. Exiting. "
MSG_ERROR_LOAD_SITE_DATA = "Can't load site data: "
MSG_ERROR_UPDATE_SITE_DATA = "Can't update site data: "
MSG_ERROR_LOAD_URL_DATA = "Can't load url data: "
MSG_ERROR_PROCESS_BATCH_ITEM = "Can't process batch item "
MSG_ERROR_WRITE_CRAWLED_DATA = "Can't write crawled data "
MSG_ERROR_COLLECT_URLS = "Can't collect urls "
MSG_ERROR_ADD_URL_TO_BATCH_ITEM = "Can't add url to batch item "
MSG_ERROR_LOAD_SITE_PROPERTIES = "Can't load site properties "
MSG_ERROR_CRAWL_SITE = "Can't crawl site "
MSG_ERROR_CHECK_SITE = "Site don't passed check site "
MSG_ERROR_GET_DIR = "Can't get dir "
MSG_ERROR_READ_SITE_FROM_DB = "Can't read site data from db"
MSG_ERROR_EMPTY_RESPONSE_SIZE = "Empty response"
MSG_ERROR_NOT_EXIST_ANY_VALID_PROXY = "Not exist any valid proxy"
MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong: %s"
MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file. %s"
MSG_ERROR_EXTRACT_BASE_URL = "Extract base url failed. Error: %s"


MSG_INFO_PROCESS_BATCH = "ProcessBatch "
MSG_INFO_STORE_COOKIES_FILE = "Store cookies file on disk."

MSG_DEBUG_NON_PROCESSING = "ProcessorName is NONE. Exclude batch item from further processing."

SITE_MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"

DEFAULT_MAX_SIZE = 1000000
EMPTY_RESPONSE_SIZE = "0"

APP_NAME = "crawler-task"

HTTP_COOKIE = "HTTP_COOKIE"
DEFAULT_HTTP_COOKIE = ""
HTTP_HEADERS = "HTTP_HEADERS"
DEFAULT_HTTP_HEADER = ""

DC_URLS_DB_NAME = "dc_urls"
DC_URLS_TABLE_PREFIX = "urls_"
DC_SITES_DB_NAME = "dc_sites"
DC_SITES_PROPERTIES_TABLE_NAME = "sites_properties"
DC_SITES_TABLE_NAME = "sites"
DC_URLS_TABLE_NAME = "urls"
COOKIES_FILE_POSTFIX = ".cookies.txt"

NON_PROCESSING = "NONE"

HTTP_REDIRECT = "<Response [301]>"
HTML_REDIRECT = ""
MAX_HTTP_REDIRECTS_UNLIMITED = 0
MAX_HTML_REDIRECTS_UNLIMITED = 0
META_XPATH = "//meta[contains(@content, 'url')]/@content"

Results = namedtuple("Results", "exit_code, output, err")

ROBOTS_PATTERN = re.compile(r'(https?://[^/]+).*', re.I)

TEXT_CONTENT_TYPE_PATTERN = re.compile('text', re.I)

ENV_CRAWLER_STORE_PATH = "ENV_CRAWLER_STORE_PATH"
# SiteProperties = namedtuple("http_header", "http_cookie")
# CrawlResponse = namedtuple("html_content", "html_header", "html_request")
# named tuple for filters
# Filter = namedtuple("Filter", "pattern, pattern_name, type, state")

DETECT_MIME_MAIN_CONTENT = "1"
RECOVER_IF_FAILED = "2"

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# #The CrawlerTask class, is a interface for fetching content from the web
#
# This object is a run at once application
class CrawlerTask(foundation.CementApp):

  # Dict matches of error masks and http codes
  errorMaskHttpCodeDict = { \
                          APP_CONSTS.ERROR_FETCH_INVALID_URL : SeleniumFetcher.ERROR_NAME_NOT_RESOLVED, \
                          APP_CONSTS.ERROR_FETCHER_INTERNAL : SeleniumFetcher.ERROR_FATAL, \
                          APP_CONSTS.ERROR_FETCHER_INTERNAL : SeleniumFetcher.ERROR_GENERAL, \
                          APP_CONSTS.ERROR_FETCH_TOO_MANY_REDIRECTS : SeleniumFetcher.ERROR_TOO_MANY_REDIRECTS, \
                          APP_CONSTS.ERROR_FETCH_CONNECTION_ERROR : SeleniumFetcher.ERROR_PROXY_CONNECTION_FAILED, \
                          APP_CONSTS.ERROR_FETCH_CONNECTION_TIMEOUT : SeleniumFetcher.ERROR_CONNECTION_TIMED_OUT, \
                          APP_CONSTS.ERROR_FETCH_FORBIDDEN : SeleniumFetcher.ERROR_TUNNEL_CONNECTION_FAILED, \
                          APP_CONSTS.ERROR_EMPTY_RESPONSE : SeleniumFetcher.ERROR_EMPTY_RESPONSE, \
                          APP_CONSTS.ERROR_FETCH_FORBIDDEN : SeleniumFetcher.ERROR_SERVICE_UNAVAILABLE, \
                          APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY : SeleniumFetcher.ERROR_PROXY_CONNECTION_FAILED, \
                          APP_CONSTS.ERROR_FETCH_HTTP_ERROR : SeleniumFetcher.ERROR_PROXY_CONNECTION_FAILED
                          }

  # Configuration settings options names
  DB_HOST_CFG_NAME = "db_host"
  DB_PORT_CFG_NAME = "db_port"
  DB_USER_CFG_NAME = "db_user"
  DB_PWD_CFG_NAME = "db_pwd"
  DB_SITES_CFG_NAME = "db_dc_sites"
  DB_URLS_CFG_NAME = "db_dc_urls"

  RAW_DATA_DIR = "raw_data_dir"
  SITE_TEMPLATES = "dc_site_template"
  KEY_VALUE_STORAGE_DIR = "key_value_storage_dir"
  DB_DATA_DIR = "db_data_dir"
  URL_SCHEMA_DIR = "url_schema_data_dir"
  URLS_XPATH_LIST_FILE = "urls_xpath_list_file"

  # Constants used in class
  HOST_ALIVE_CHECK_NAME = 'HOST_ALIVE_CHECK'
  HOST_ALIVE_CHECK_PROXY_NAME = 'HOST_ALIVE_CHECK_PROXY'
  DEFAULT_PROTOCOL_PREFIX = 'http://'

  SEARCH_BASE_URL_PATTERN = r'<base[^>]+href="([^">]+)"'

  # Mandatory
  class Meta(object):
    label = APP_NAME
    def __init__(self):
      # self.site_table_row = None
      self.urlXpathList = {}


  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.refererHeaderResolver = RefererHeaderResolver()
    self.raw_data_dir = None
    self.batchItem = None
    self.siteTable = None
    self.logger = None
    self.loggerDefault = None
    self.urlTable = None
    self.batch = None
    self.defaultHeaderFile = None
    self.defaultCookieFile = None
    self.kvDbDir = None
    self.defaultIcrCrawlTime = None
    self.dbWrapper = None
    self.store_items = []
    self.url = None
    self.max_fetch_time = CONSTS.FETCHER_TIME_LIMIT_MAX
    self.collect_additional_prop = False
    self.exit_code = EXIT_SUCCESS
    self.keep_old_resources = False
    self.urlProcess = URLProcess()
    self.resourceProcess = ResourceProcess()
    self.siteHTTPHeaders = None
    self.tidyOptions = {'numeric-entities': 1, 'char-encoding': 'utf8'}
    self.headerFileDir = None
    self.robotsFileDir = None
    self.fileHeaders = None
    self.siteHeaders = None
    self.hTTPHeadersStorage = LFSDataStorage()
    self.robotsParser = RobotsParser()
    self.feedItems = None
    self.collectURLsItems = []
    self.errorMask = APP_CONSTS.ERROR_OK
    self.httpApplyHeaders = None
    self.chainDict = {}
    self.chainIndex = 0
    self.schemaBatchItems = []
    self.useZeroSiteIdSiteNotExists = False
    self.dir = None
    self.curBatchIterations = 1
    self.crawledResource = None
    self.realUrl = None
    self.res = None
    self.crawledTime = None
    self.storeHttpRequest = True
    self.store_http_headers = True
    self.headersDict = {}
    self.postForms = {}
    self.headers = None
    self.cookie = ''
    self.proxies = None
    self.authName = None,
    self.authPwd = None
    self.external_url = None
    self.auto_remove_props = {}
    self.htmlRecover = None
    self.autoDetectMime = None
    self.processContentTypes = []
    self.siteProperties = {}
    self.needStoreMime = None
    self.allow_http_redirects = True
    self.processorName = None
    self.storeCookies = True
    self.dom = None
    self.max_http_redirects = CONSTS.MAX_HTTP_REDIRECTS_LIMIT
    self.max_html_redirects = CONSTS.MAX_HTML_REDIRECTS_LIMIT
    self.urlXpathList = {}
    self.urlTempalteRegular = None
    self.urlTempalteRealtime = None
    self.urlTempalteRegularEncode = None
    self.urlTempalteRealtimeEncode = None
    self.detectModified = None
    self.site = None
    self.urlSchemaDataDir = None
    self.proxyResolver = None
    self.normMask = UrlNormalizator.NORM_DEFAULT
    self.urlsXpathList = None
    self.cookieResolver = None
    # status update variables from 'URL_SCHEMA'
    self.statusUpdateEmptyProxyList = None
    self.statusUpdateNoAvailableProxy = None
    self.statusUpdateTriesLimit = None
    self.feedUrl = {}
    self.resetVars()
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

    # load logger config file
    self.loadLogConfigFile()

    # load mandatory options
    self.loadOptions()

    # load key-value db
    self.loadKeyValueDB()

    # make processing batch data
    self.processBatch()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # #fetchSiteHeader reads from file and returns fileHeader element
  #
  # @return is collect successfully
  # bullshit, move it to the separate module (like URLCollector)
  def fetchFileHeader(self, url, siteId):
    ret = None
    if self.headerFileDir is not None and self.headerFileDir:
      host = Utils.UrlParser.getDomain(url)
      if host is not None and self.siteHeaders is not None:
        ret = self.hTTPHeadersStorage.loadElement(self.headerFileDir, host, siteId, self.siteHeaders)
    return ret


  # #fetchSiteHeader reads from file and returns fileHeader element
  #
  # @return is collect successfully
  # bullshit, move it to the separate module (like URLCollector)
  def saveFileHeader(self, url, siteId, localFileHeaders):
    if self.headerFileDir is not None:
      auth = urlparse.urlsplit(url.strip())[1]
      host = re.search('([^@]*@)?([^:]*):?(.*)', auth).groups()[1]
      if host is not None:
        self.hTTPHeadersStorage.saveElement(self.headerFileDir, host, siteId, localFileHeaders)


  # #RLs collect URL from response body and fills new batch items for batching iterations
  #
  # @return is collect successfully
  def collectURLs(self):
    collectURLsResult = False
    if True or self.dom is not None:
      collectURLs = CollectURLs(isAbortedByTTL=self.isAbortedByTTL)
      collectURLs.crawledResource = self.crawledResource
      collectURLs.url = self.url
      collectURLs.dom = self.dom
      collectURLs.realUrl = self.realUrl
      collectURLs.baseUrl = self.batchItem.baseUrl
      collectURLs.processorName = self.processorName
      collectURLs.batchItem = self.batchItem
      collectURLs.urlXpathList = self.urlXpathList
      collectURLs.siteProperties = self.siteProperties
      collectURLs.site = self.site
      collectURLs.autoRemoveProps = self.auto_remove_props
      collectURLs.autoDetectMime = self.autoDetectMime
      collectURLs.processContentTypes = self.processContentTypes
      collectURLs.postForms = self.postForms
      collectURLs.urlProcess = self.urlProcess
      collectURLs.urlsXpathList = self.urlsXpathList

      self.logger.debug("!!! self.batchItem.baseUrl = %s" , str(self.batchItem.baseUrl))

      if self.batch.crawlerType != dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        collectURLs.dbWrapper = self.dbWrapper

      if "ROBOTS_COLLECT" not in self.siteProperties or int(self.siteProperties["ROBOTS_COLLECT"]) > 0:
        collectURLs.robotsParser = self.robotsParser

      # get proxy name
      proxyName, isValid = CrawlerTask.getProxyName(siteProperties=self.siteProperties,
                                                    siteId=self.site.id,
                                                    url=self.url.url,
                                                    dbWrapper=self.dbWrapper,
                                                    logger=self.logger)

      if not isValid and proxyName is not None:
        self.logger.debug("Got invalid proxy '%s'. Collect urls processing skipped...", str(proxyName))
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY
        self.updateSiteParams(APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY)
        self.updateURLForFailed(self.errorMask)
        return

      self.httpApplyHeaders = self.updateHeadersByCookies(self.httpApplyHeaders,
                                                          self.url.url,
                                                          HTTPCookieResolver.STAGE_REGULAR)

      collectURLsResult, internalLinks, externalLinks, urlObjects, self.feedItems, chainUrls = \
                          collectURLs.process(self.crawledResource.http_code,
                                              not self.batch.dbMode & dc_event.Batch.DB_MODE_W,
                                              self.httpApplyHeaders,
                                              proxyName)

      self.logger.debug("!!! internalLinks (%s): %s", str(len(internalLinks)), str(internalLinks))
      self.logger.debug("!!! externalLinks (%s): %s", str(len(externalLinks)), str(externalLinks))

      if self.dom is not None and collectURLsResult and self.collect_additional_prop and (len(internalLinks) > 0 or\
                                                                                           len(externalLinks)):
        collectPropertiesObj = CollectProperties()
        collectPropertiesObj.siteId = Utils.autoFillSiteId(self.batchItem.siteId, self.logger)
        collectPropertiesObj.kvDbDir = self.kvDbDir
        collectPropertiesObj.res = self.res
        collectPropertiesObj.batchItem = self.batchItem
        collectPropertiesObj.realUrl = self.realUrl
        collectPropertiesObj.process(self.dom, internalLinks, externalLinks)

      # Fill new batch items in self.collectURLsItems
      if urlObjects is not None and len(urlObjects) > 0 and \
      (self.batchItem.depth > 0 or self.processorName == PCONSTS.PROCESSOR_RSS):
        self.fillItemsFromIterations(urlObjects)
      if chainUrls is not None and len(chainUrls) > 0:
        self.fillItemsFromIterationsWithChain(chainUrls, self.batchItem)


  # #writeData  write the response body and headers to file
  #
  # @param
  def writeData(self):
    if self.dbWrapper is None:
      self.logger.info("self.dbWrapper is None")
      return

    # check wether need store to disk
    if self.needStoreMime is not None and self.needStoreMime != '*':
      if self.crawledResource.content_type.lower() not in self.needStoreMime:
        self.logger.info("Content not set on disk because a conent-type `%s` is not in MIME types list:\n%s",
                         str(self.crawledResource.content_type), str(self.needStoreMime))
        return

    urlPut_list = []

    if TEXT_CONTENT_TYPE_PATTERN.match(self.crawledResource.content_type):
      # save UTF-8 encoding text for text content types
      if self.crawledResource.dynamic_fetcher_type:
        raw_unicode_content = self.crawledResource.meta_content
      else:
        raw_unicode_content = self.crawledResource.html_content
      if raw_unicode_content:
        if self.crawledResource.charset is not None and self.crawledResource.charset.lower() != "utf-8":
          self.logger.debug('Decoding content charset: ' + str(self.crawledResource.charset))
          try:
            raw_unicode_content = raw_unicode_content.decode(self.crawledResource.charset)
          except Exception, err:
            self.logger.debug("Decoding content charset error, type: '" + str(type(raw_unicode_content)) + \
                              "', length: " + str(len(raw_unicode_content)) + " to charset: '" + \
                              str(self.crawledResource.charset) + "', error message: " + str(err))
        putDict = {'data': base64.b64encode(raw_unicode_content)}
        contentType = dc_event.Content.CONTENT_RAW_CONTENT
        urlPut_list.append(dc_event.URLPut(self.batchItem.siteId, self.batchItem.urlId, contentType, putDict))

        # save tidy recovered file
        # localDom = None
        # if self.htmlRecover is not None and self.htmlRecover == '2':
        #  localDom = self.resourceProcess.domParser(None, raw_unicode_content, 200,
        #                                            self.crawledResource.charset if self.crawledResource \
        #                                            is not None else None)
        # if self.htmlRecover is not None and (self.htmlRecover == '1' or self.htmlRecover == '2' and localDom is None):
        if self.htmlRecover is not None and (self.htmlRecover == '1' or self.htmlRecover == '2'):
          tidy_content = tidylib.tidy_document(raw_unicode_content, self.tidyOptions)[0]
          if self.crawledResource.charset is not None and self.crawledResource.charset.lower() != "utf-8":
            self.logger.debug('Decoding tidy content charset: ' + str(self.crawledResource.charset))
            try:
              tidy_content = tidy_content.decode(self.crawledResource.charset)
            except Exception, err:
              self.logger.debug("Decoding tidy content charset error, type: '" + str(type(tidy_content)) + \
                                "', length: " + str(len(tidy_content)) + " to charset: '" + \
                                str(self.crawledResource.charset) + "', error message: " + str(err))
          putDict = {'data': base64.b64encode(tidy_content)}
          contentType = dc_event.Content.CONTENT_TIDY_CONTENT
          urlPut_list.append(dc_event.URLPut(self.batchItem.siteId, self.batchItem.urlId, contentType, putDict))
    else:
      # save origin binary data for non-text content types
      if self.crawledResource.binary_content is not None:
        putDict = {'data': base64.b64encode(self.crawledResource.binary_content)}
        contentType = dc_event.Content.CONTENT_RAW_CONTENT
        urlPut_list.append(dc_event.URLPut(self.batchItem.siteId, self.batchItem.urlId, contentType, putDict))

    # save rendered file
    if self.crawledResource.dynamic_fetcher_type and self.crawledResource.html_content:
      putDict = {"data": base64.b64encode(self.crawledResource.html_content)}
      contentType = dc_event.Content.CONTENT_DYNAMIC_CONTENT
      urlPut_list.append(dc_event.URLPut(self.batchItem.siteId, self.batchItem.urlId, contentType, putDict))

    self.logger.debug('!!! self.crawledResource.response_header = ' + str(self.crawledResource.response_header))
#     self.logger.debug('!!! self.httpApplyHeaders = ' + str(self.httpApplyHeaders))
#     self.logger.debug('!!! self.crawledResource.html_request = ' + str(self.crawledResource.html_request))
#     self.logger.debug('!!! Before change self.httpApplyHeaders = ' + str(self.httpApplyHeaders))
    # ##self.httpApplyHeaders = self.crawledResource.response_header  # #???
#     self.logger.debug('!!! After change self.httpApplyHeaders = ' + str(self.httpApplyHeaders))
    # html header
    if self.store_http_headers and self.crawledResource.response_header:
      putDict = {"data": base64.b64encode(self.crawledResource.response_header)}
      contentType = dc_event.Content.CONTENT_HEADERS_CONTENT
      urlPut_list.append(dc_event.URLPut(self.batchItem.siteId, self.batchItem.urlId, contentType, putDict))

    # html request
    if self.storeHttpRequest and self.crawledResource.html_request:
      putDict = {"data": base64.b64encode(self.crawledResource.html_request)}
      contentType = dc_event.Content.CONTENT_REQUESTS_CONTENT
      urlPut_list.append(dc_event.URLPut(self.batchItem.siteId, self.batchItem.urlId, contentType, putDict))

    # Write raw content on disk via db-task
    # Check if Real-Time crawling
    self.dbWrapper.putURLContent(urlPut_list)

    # change url's contentMask
    self.url.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK
    self.batchItem.urlObj.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK


  # #getDir prepare dir
  #
  # @param
  def getDir(self):
    if len(self.batchItem.siteId):
      self.dir = os.path.join(self.raw_data_dir, self.batchItem.siteId, PathMaker(self.batchItem.urlId).getDir())
    else:
      self.dir = os.path.join(self.raw_data_dir, "0", PathMaker(self.batchItem.urlId).getDir())


  # #makeDir prepare dir
  #
  # @param
  def makeDir(self):
    self.logger.debug('!!! makeDir() enter .... self.dir = ' + str(self.dir))
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)

    if not os.path.isdir(self.dir):
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_WRITE_FILE_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_WRITE_FILE_ERROR)
      raise Exception("path %s exists, but is not a directory" % (self.dir,))


  # #updateURLForFailed
  #
  # @param error_bit BitMask of error
  def updateURLForFailed(self, errorBit, httpCode=CONSTS.HTTP_CODE_400, status=dc_event.URL.STATUS_CRAWLED, \
                         updateUdate=True):
    self.urlProcess.siteId = self.batchItem.siteId
    self.urlProcess.updateURLForFailed(errorBit, self.batchItem, httpCode, status, updateUdate)
    if self.crawledResource is not None:
      self.crawledResource.http_code = httpCode
      self.writeData()


  # #httpRequestWrapper method makes http request, using detectModified object if it present
  #
  # @param url - http requests url
  # @param headers - http headers, using in http request
  # @param auth - authentification
  # @param postData - data using in post request
  # @param urlObj - url's Obj
  # @param incomingContent - raw content that is externally provided
  # @param macroCode - list of the strings with the source code to be executed at the dynamic fetcher,
  # for example JavaScript
  # @param proxyName - proxy name
  # @return http resource (http response)
  def httpRequestWrapper(self, url, headers, auth, postData, urlObj, incomingContent, macroCode=None, proxyName=None):
    ret = None
    # (1) Fetcher type detection section
    localFetchType = copy.deepcopy(self.site.fetchType)
    if localFetchType == BaseFetcher.TYP_DYNAMIC:
      if urlObj is not None and urlObj.parentMd5 is not None and \
      "DYNAMIC_FETCH_ONLY_FOR_ROOT_URL" in self.siteProperties and \
      int(self.siteProperties["DYNAMIC_FETCH_ONLY_FOR_ROOT_URL"]) > 0:
        if urlObj.parentMd5 == "":
          localFetchType = BaseFetcher.TYP_DYNAMIC
        else:
          localFetchType = BaseFetcher.TYP_NORMAL
    elif localFetchType == BaseFetcher.TYP_AUTO:
      localFetchType = BaseFetcher.TYP_NORMAL
    # if self.curBatchIterations == 2 and self.processorName == PCONSTS.PROCESSOR_RSS and \
    # localFetchType == BaseFetcher.TYP_DYNAMIC:
    if urlObj is not None and urlObj.parentMd5 is not None and urlObj.parentMd5 == "" and \
    self.processorName == PCONSTS.PROCESSOR_RSS and localFetchType == BaseFetcher.TYP_DYNAMIC:
      localFetchType = BaseFetcher.TYP_NORMAL

    if urlObj is not None and "FETCHER_TYPE" in self.siteProperties and self.siteProperties["FETCHER_TYPE"]:
      fetchResType = FetcherType.getFromProperty(self.siteProperties["FETCHER_TYPE"], urlObj.url, self.logger)
      if fetchResType is not None:
        localFetchType = fetchResType

    # (1) END
    self.logger.debug(">>> FetchType before applying = " + str(localFetchType))
    if self.detectModified is not None:
      self.logger.debug(">>> self.detectModified.modifiedSettings = " + str(self.detectModified.modifiedSettings))
    self.logger.debug(">>> self.urlProcess.urlObj.lastModified = " + str(self.urlProcess.urlObj.lastModified))

    if self.detectModified is None or self.detectModified.modifiedSettings is None or \
    (urlObj is not None and urlObj.crawled == 0):
      if incomingContent is None:
#         self.logger.debug(">>> Filters() (1) self.site.filters: " + varDump(self.site.filters))
#         localFilters = Filters(None, self.dbWrapper, self.batchItem.siteId, 0, \
#                                None, Filters.OC_RE)
        # ret = BaseFetcher.get_fetcher(localFetchType).\
        #  open(url, external_url=self.external_url, timeout=int(self.url.httpTimeout) / 1000.0, headers=headers,
        #       allow_redirects=self.allow_http_redirects, proxies=self.proxies, auth=auth, data=postData,
        #       logger=self.logger, allowed_content_types=self.processContentTypes,
        #       max_resource_size=self.site.maxResourceSize, max_redirects=self.max_http_redirects,
        #       filters=localFilters, depth=urlObj.depth, macro=macroCode)

        fetcher = BaseFetcher.get_fetcher(localFetchType, None, self.dbWrapper, self.site.id)
        if "CONNECTION_TIMEOUT" in self.siteProperties:
          fetcher.connectionTimeout = float(self.siteProperties["CONNECTION_TIMEOUT"])
        else:
          fetcher.connectionTimeout = CONSTS.CONNECTION_TIMEOUT

        if self.external_url is not None and \
        (isinstance(self.external_url, str) or isinstance(self.external_url, unicode)):
          self.logger.debug('self.external_url: ' + str(self.external_url) + ' url: ' + str(url))
          if '%URL%' in self.external_url:
            url = self.external_url.replace('%URL%', urllib.quote(url))
            self.logger.debug('New url: ' + str(url))
        tm = int(self.url.httpTimeout) / 1000.0
        if isinstance(self.url.httpTimeout, float):
          tm += float('0' + str(self.url.httpTimeout).strip()[str(self.url.httpTimeout).strip().find('.'):])

        cookieStage = HTTPCookieResolver.STAGE_REDIRECT
        if self.processorName == PCONSTS.PROCESSOR_RSS:
          cookieStage = cookieStage | HTTPCookieResolver.STAGE_RSS
        headers = self.updateHeadersByCookies(headers, url, cookieStage)

        self.logger.debug("!!! Before fetcher.open() for url: %s", str(url))
        self.logger.debug("!!! Before fetcher.open() self.site.maxResourceSize = %s", str(self.site.maxResourceSize))

        ret = fetcher.open(url, timeout=tm, headers=headers,
                           allow_redirects=self.allow_http_redirects, proxies=strToProxy(proxyName, self.logger), auth=auth,
                           data=postData, log=self.logger, allowed_content_types=self.processContentTypes,
                           max_resource_size=self.site.maxResourceSize, max_redirects=self.max_http_redirects,
                           filters=None if urlObj.parentMd5 == "" else self.site.filters,
                           depth=urlObj.depth, macro=macroCode)
      else:
        # ret = BaseFetcher.get_fetcher(BaseFetcher.TYP_CONTENT).open(url, inputContent=incomingContent)
        fetcher = BaseFetcher.get_fetcher(BaseFetcher.TYP_CONTENT, None, self.dbWrapper, self.site.id)
        if "CONNECTION_TIMEOUT" in self.siteProperties:
          fetcher.connectionTimeout = float(self.siteProperties["CONNECTION_TIMEOUT"])
        else:
          fetcher.connectionTimeout = CONSTS.CONNECTION_TIMEOUT
        ret = fetcher.open(url, inputContent=incomingContent, log=self.logger)
    else:
      self.detectModified.expiredData = urlObj.CDate
      self.detectModified.eTags = urlObj.eTag
      self.detectModified.prevContentLen = urlObj.size
      self.detectModified.prevContentCrc32 = urlObj.rawContentMd5
      self.detectModified.prevContentDate = urlObj.CDate
      httpParams = {}
      httpParams["url"] = url
      httpParams["externalUrl"] = self.external_url
      tm = int(self.url.httpTimeout) / 1000.0
      if isinstance(self.url.httpTimeout, float):
        tm += float('0' + str(self.url.httpTimeout).strip()[str(self.url.httpTimeout).strip().find('.'):])
      httpParams["httpTimeout"] = tm
      httpParams["httpHeader"] = headers
      httpParams["allowHttpRedirects"] = self.allow_http_redirects
      httpParams["proxies"] = self.proxies
      httpParams["auth"] = auth
      httpParams["postData"] = postData
      httpParams["processContentTypes"] = self.processContentTypes
      httpParams["maxResourceSize"] = self.site.maxResourceSize
      httpParams["maxHttpRedirects"] = self.max_http_redirects
      ret = self.detectModified.makeHTTPRequest(localFetchType, httpParams)

      if self.detectModified.isNotModified():
        self.logger.debug("!!! self.detectModified.isNotModified()  ret.status_code: %s !!!", str(ret.status_code))
        if ret is not None:
          self.res = ret
          raise NotModifiedException("Detect resource not modified state", ret.status_code)

    return ret


  # #getRotatedHeaders get dict() of rotated headers with low frequency of usage and update frequencies
  #
  # @return dict() of rotated headers with low frequency of usage
  def processRotatedHeaders(self, url):
    self.fileHeaders = self.fetchFileHeader(url, self.batchItem.siteId)
    rotatedHeaders = self.hTTPHeadersStorage.fetchLowFreqHeaders(self.fileHeaders, self.siteHeaders)
    self.httpApplyHeaders = {}
    # Initialize with single-value string type not rotated headers
    for h in self.headersDict:
      if isinstance(self.headersDict[h], basestring):
        self.httpApplyHeaders[h] = self.headersDict[h]
    # Add rotated headers, possible overwrite someone from initialized before
    for h in rotatedHeaders:
      self.fileHeaders[h[0]][h[1]] += 1
      self.httpApplyHeaders[h[0]] = h[1]
      self.saveFileHeader(url, self.batchItem.siteId, self.fileHeaders)
#     self.logger.debug("self.fileHeaders:\n%s\nEffective headers:\n%s", str(self.fileHeaders),
#                       str(self.httpApplyHeaders))
    # Overwrite a referrer header with custom per site property rule definition
    self.refererHeaderResolver.\
        resolveRefererHeader(self.httpApplyHeaders, int(self.siteProperties["REFERER_SELF_URL"])
                             if "REFERER_SELF_URL" in self.siteProperties else RefererHeaderResolver.MODE_SIMPLE, url,
                             self.batchItem.siteId, self.url.parentMd5, self.dbWrapper)


  # #crawl site
  #
  # @return should continue to write data and collect URLs
  def crawl(self, incomingContent):
    self.crawledResource = None
    # delay
    self.logger.debug("Make request delay " + str(self.url.requestDelay / 1000.0) + " sec.")
    time.sleep(self.url.requestDelay / 1000.0)
    # (1) Decode url - [UrlProcess]
    # TODO move to - [UrlProcess]
    self.logger.debug("!!! self.url.url = '%s'", str(self.url.url))

    self.urlProcess.url = self.url.url
    self.urlProcess.site = self.site
    # (1) END
    url = self.urlProcess.getRealUrl()
    self.realUrl = url
    startTime = time.time()

    self.processRotatedHeaders(url)

    self.logger.debug("!!! url = '%s'", str(url))

    macro = None
    if 'FETCHER_MACRO' in self.siteProperties and self.siteProperties['FETCHER_MACRO'] is not None\
    and self.siteProperties['FETCHER_MACRO'] != '':
      try:
        macro = json.loads(self.siteProperties['FETCHER_MACRO'])
      except Exception, err:
        self.logger.error("Initialization of macro error: %s, source: %s", str(err),
                          str(self.siteProperties['FETCHER_MACRO']))
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_MACRO_DESERIALIZATION
        self.updateSiteParams(APP_CONSTS.ERROR_MACRO_DESERIALIZATION)
        self.updateURLForFailed(self.errorMask)
        return False

    try:
      # (2) Makes auth tuple - []
      # TODO move to - []
      if self.authName and self.authPwd:
        auth = (self.authName, self.authPwd)
        self.logger.info("using http basic auth %s:%s", self.authName, self.authPwd)
      else:
        auth = None
      # (2) END
      # (3) Resolve HTTP Method (move convertToHttpDateFmt to Utils) - [UrlProcess]
      # TODO move to - [UrlProcess]
      self.urlProcess.urlObj = self.url
      postData = self.urlProcess.resolveHTTP(self.postForms, self.httpApplyHeaders)
      # (3) END

      # Workaround
      url = self.urlProcess.urlTemplateApply(url, self.batch.crawlerType, self.urlTempalteRegular,
                                             self.urlTempalteRealtime, self.urlTempalteRegularEncode,
                                             self.urlTempalteRealtimeEncode)

      self.logger.debug("!!! urlTemplateApply() return url = '%s'", str(url))

      # Checking is available urs or not
      if not CrawlerTask.isAvailableUrl(siteProperties=self.siteProperties, url=url, logger=self.logger):
        self.logger.debug("Host '%s' is not available!", str(url))
        raise UrlAvailableException("Host '%s' is not available!" % str(url))

      # Check robots mode use proxy if allowed
      if "ROBOTS_MODE" not in self.siteProperties or int(self.siteProperties["ROBOTS_MODE"]) > 0:
        self.logger.debug("Robots.txt obey mode ON")

        # get proxy name
        proxyName, isValid = CrawlerTask.getProxyName(siteProperties=self.siteProperties,
                                                      siteId=self.site.id,
                                                      url=self.url.url,
                                                      dbWrapper=self.dbWrapper,
                                                      logger=self.logger)
        if not isValid and proxyName is not None:
          self.logger.debug("Try usage invalid proxy '%s'. Skipped...", str(proxyName))
          self.errorMask = self.errorMask | APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY
          self.updateSiteParams(APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY)
          self.updateURLForFailed(self.errorMask)
          return False

        if self.robotsParser.loadRobots(url, self.batchItem.siteId, self.httpApplyHeaders, proxyName):
          self.httpApplyHeaders = self.updateHeadersByCookies(self.httpApplyHeaders,
                                                              url,
                                                              HTTPCookieResolver.STAGE_ROBOTS)

          isAllowed, retUserAgent = self.robotsParser.checkUrlByRobots(url, self.batchItem.siteId,
                                                                       self.httpApplyHeaders)
          if not isAllowed:
            self.logger.debug(">>> URL " + url + " is NOT Allowed by user-agent:" + str(retUserAgent))
            self.errorMask = self.errorMask | APP_CONSTS.ERROR_ROBOTS_NOT_ALLOW
            self.updateSiteParams(APP_CONSTS.ERROR_ROBOTS_NOT_ALLOW)
            self.updateURLForFailed(self.errorMask)
            return False

      # (3.2) HTTP Fetcher with html redirect resolving
      localUrl = url
      prevUrl = localUrl
      res = self.makeDefaultResponse(Response())

      self.logger.debug("!!! localUrl = '%s'", str(localUrl))

      retriesCount = HTTPProxyResolver.getTriesCount(self.siteProperties)
      proxyTriesCount = 0
      proxyName = None
      isValidProxy = True
      for count in range(0, retriesCount + 1):
        self.logger.debug("retriesCount = %s, count = %s", str(retriesCount), str(count))
        # check is exceeded tries count
        HTTPProxyResolver.checkTriesCount(siteProperties=self.siteProperties, currentTriesCount=proxyTriesCount)

        # get proxy name
        proxyName, isValidProxy = CrawlerTask.getProxyName(siteProperties=self.siteProperties,
                                                      siteId=self.site.id,
                                                      url=self.url.url,
                                                      dbWrapper=self.dbWrapper,
                                                      logger=self.logger)

        # increment counter
        if proxyName is not None:
          proxyTriesCount += 1

        if not isValidProxy and proxyName is not None:
          self.logger.debug("Try usage invalid proxy '%s'. Fetching skipped...", str(proxyName))
          continue

        try:
          self.logger.debug("Use headers: %s type: %s", str(self.httpApplyHeaders), str(type(self.httpApplyHeaders)))
          self.logger.info("start to fetch: %s", localUrl)
          res = self.httpRequestWrapper(localUrl, self.httpApplyHeaders, auth, postData, self.url, incomingContent, \
                                          macro, proxyName)
            
          if res is not None and res.url is not None:
            self.logger.debug("!!! res.url: %s", str(res.url))
            self.batchItem.urlObj.baseUrl = res.url
            
          if res is not None and res.request is not None:
            self.logger.info("!!! res.request.url: %s", str(res.request))

        except SeleniumFetcherException, err:
          self.logger.debug("!!! httpRequestWrapper return error: %s", str(err))
          CrawlerTask.addProxyFaults(siteProperties=self.siteProperties,
                                     siteId=self.site.id,
                                     proxyName=proxyName,
                                     dbWrapper=self.dbWrapper)
          continue

        # Check raw content use patterns
        if CrawlerTask.isNeedRotateProxy(siteProperties=self.siteProperties,
                                         siteId=self.site.id,
                                         proxyName=proxyName,
                                         dbWrapper=self.dbWrapper,
                                         rawContent=res.rendered_unicode_content):
          self.logger.debug('Necessary rotate proxy. Go to the next...')
          continue

        if res is not None and res.error_mask != APP_CONSTS.ERROR_OK:
          self.logger.debug("res.error_mask = %s", str(res.error_mask))
          continue
        elif res is None or self.max_html_redirects is None or \
          self.max_html_redirects < CONSTS.MAX_HTML_REDIRECTS_LIMIT or \
          not self.allow_html_redirects:
          break
        elif self.max_html_redirects > 0 and self.htmlRedirects >= self.max_html_redirects:
          self.logger.debug("Max html redirects reached %s>=%s", str(self.htmlRedirects), str(self.max_html_redirects))
          self.errorMask = self.errorMask | APP_CONSTS.ERROR_MAX_ALLOW_HTML_REDIRECTS
          self.updateURLForFailed(APP_CONSTS.ERROR_MAX_ALLOW_HTML_REDIRECTS)
          return False
        elif res.rendered_unicode_content is not None:
          if 'content-type' in res.headers and res.headers['content-type'].find('text/html') > -1:
            prevUrl = localUrl

            if self.site.fetchType == BaseFetcher.TYP_DYNAMIC:
              res.rendered_unicode_content = Utils.eraseNoScript(res.rendered_unicode_content)

            try:
              localUrl = Utils.getHTMLRedirectUrl(res.rendered_unicode_content, self.logger)
            except Exception, err:
              self.logger.error("Error: %s", str(err))
              self.logger.info(Utils.getTracebackInfo())

            self.logger.debug("!!! HTML redirect to '%s'", str(localUrl))
            if localUrl is None or localUrl == '':
              break
            elif res.status_code != CONSTS.HTTP_CODE_200 and res.status_code not in CONSTS.REDIRECT_HTTP_CODES:
              self.logger.debug("!!! Url skipped, because http code = '%s'", str(res.status_code))
              localUrl = None
              break
            else:
              # HTML Redirect section
              collectURLs = CollectURLs()
              isAllowedByFilter = collectURLs.filtersApply(self.site.filters, localUrl, 0, self.dbWrapper, \
                                                        self.batchItem.siteId, None, \
                                                        Filters.OC_RE, Filters.STAGE_COLLECT_URLS)
              if not isAllowedByFilter:
                localUrl = urlparse.urljoin(prevUrl, localUrl)

              localUrl = dc_event.URL(0, localUrl, normalizeMask=self.normMask).getURL(self.normMask)
              self.logger.debug("HTML redirect: %s, is allowed by filters: %s", localUrl, str(bool(isAllowedByFilter)))
            self.htmlRedirects += 1
          else:
            break
        else:
          break

      if not isValidProxy:
        self.logger.debug("Not found any valid proxy for usage...")
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY
        self.updateSiteParams(APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY)
        self.updateURLForFailed(self.errorMask)
        return False

      # (4) Checks and update url in db-task them - [UrlProcess]
      # TODO move to - [UrlProcess]
      # (OLD if version) if res.headers is None:
      if res is not None and res.error_mask != 0:
        self.logger.debug("Positive res.error_mask: %s", str(res.error_mask))
        self.updateURLForFailed(res.error_mask)
        self.errorMask = self.errorMask | res.error_mask
        return False

      if res is not None and res.headers is not None and "content-length" in res.headers and \
      res.headers["content-length"] == EMPTY_RESPONSE_SIZE:
        self.logger.debug('Zero content-length!')
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_EMPTY_RESPONSE
        self.updateURLForFailed(self.errorMask)
        return False
      # (4) END

      # save res to self, will use it in next steps
      # (5) Create and fill resource struct - [ResourceProcess]
      # TODO move to - [ResourceProcess]
      self.res = res
      self.logger.info("!!! response code: '%s'", str(self.res.status_code))
      self.logger.info("!!! response cookies: '%s'", str(self.res.cookies))
      # use charset to improve encoding detect
      self.crawledTime = time.time()
      self.resourceProcess.urlObj = self.url
      resource = self.resourceProcess.generateResource(startTime, res, self.headers, self.crawledTime,
                                                       self.defaultIcrCrawlTime,
                                                       self.siteProperties["CONTENT_TYPE_MAP"] if \
                                                       "CONTENT_TYPE_MAP" in self.siteProperties else None)

      # Execution 'REPLACE' property if necessary
      if APP_CONSTS.REPLACEMENT_CONTENT_DATA in self.siteProperties:
        self.logger.debug("!!! Found property 'REPLACE' !!!")

        self.res.rendered_unicode_content = ContentEvaluator.executeReplace(
            dbWrapper=self.dbWrapper,
            siteId=self.batchItem.siteId,
            propertyString=self.siteProperties[APP_CONSTS.REPLACEMENT_CONTENT_DATA],
            contentData=self.res.rendered_unicode_content)

        self.res.content_size = len(self.res.rendered_unicode_content)


      # collect cookies
      self.cookieResolver.addCookie(url, resource.cookies)

      resource.dynamic_fetcher_type = res.dynamic_fetcher_type
      resource.dynamic_fetcher_result_type = res.dynamic_fetcher_result_type
      self.crawledResource = resource
      # (5) END

      # Save last modified value to detect modified object
      if self.detectModified is not None:
        self.detectModified.lastModified = self.crawledResource.last_modified

      if self.crawledResource.http_code >= CONSTS.HTTP_CODE_400:
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_HTTP_ERROR
        # Add error mask about forbidden fetch
        if self.crawledResource.http_code == CONSTS.HTTP_CODE_403:
          self.errorMask = APP_CONSTS.ERROR_FETCH_FORBIDDEN

        self.updateSiteParams(self.errorMask)
        self.updateURLForFailed(self.errorMask, self.crawledResource.http_code)
        return False

      # Added by Oleksii
      # support of HTTP_REDIRECTS_MAX
      # (7) Check response for redirect count [???]
      self.checkResponse()

      if not self.allow_http_redirects:
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_MAX_ALLOW_HTTP_REDIRECTS
        self.updateSiteParams(APP_CONSTS.ERROR_MAX_ALLOW_HTTP_REDIRECTS)
        self.updateURLForFailed(self.errorMask)  # #, self.crawledResource.http_code)
        return False
      # (7) END

      # (8) Check Content size and response code - [ResourceProcess]
      # TODO move to - [ResourceProcess]
      self.resourceProcess.resource = resource
      self.resourceProcess.batchItem = self.batchItem
      if not self.resourceProcess.checkResourcesResponse(res, self.site.maxResourceSize, self.updateSiteParams):
        self.errorMask = self.errorMask | resource.error_mask
        self.updateURLForFailed(self.errorMask, res.status_code)  # #, self.crawledResource.http_code)
        return False
      # (8) END

      # # Block handlers 'STAGE_BEFORE_DOM_PRE'
      self.logger.debug("+++++++++++++++++++++++++++++++++++++")
      self.logger.debug("Block handlers 'STAGE_BEFORE_DOM_PRE'")
      collectURLs = CollectURLs()
      self.logger.debug("self.site.filters: " + varDump(self.site.filters))
      # Create class Filters instance for check 'raw content' use regular expressions
      localFilters = Filters(None, self.dbWrapper, self.batchItem.siteId, 0,
                             None, Filters.OC_RE, Filters.STAGE_BEFORE_DOM_PRE, Filters.SELECT_SUBJECT_RAW_CONTENT)

      self.logger.debug('>>> localFilters.filters: ' + varDump(localFilters.filters))
      self.logger.debug(">>> isExistStage('STAGE_BEFORE_DOM_PRE'): " + \
                        str(localFilters.isExistStage(Filters.STAGE_BEFORE_DOM_PRE)))
      # (9) Check RAW content text regular expression
      if localFilters.isExistStage(Filters.STAGE_BEFORE_DOM_PRE):
        self.logger.debug("Check RAW content text regular expression ...")
        if collectURLs.filtersApply(None, resource.binary_content, 0, self.dbWrapper,
                                    self.batchItem.siteId, None, Filters.OC_RE,
                                    Filters.STAGE_BEFORE_DOM_PRE, Filters.SELECT_SUBJECT_RAW_CONTENT, True):
          self.logger.debug("RAW content text regular expression check SUCCESS")
        else:
          self.logger.debug("RAW content text regular expression check FAILED")
          self.errorMask = self.errorMask | APP_CONSTS.ERROR_CRAWLER_FILTERS_BREAK
          self.updateURLForFailed(self.errorMask)
          return False
      # (9) END

      # Create class Filters instance for check 'headers' use regular expressions
      localFilters = Filters(None, self.dbWrapper, self.batchItem.siteId, 0,
                             None, Filters.OC_RE, Filters.STAGE_BEFORE_DOM_PRE, Filters.SELECT_SUBJECT_HEADERS_ALL)

      self.logger.debug('>>> localFilters.filters: ' + varDump(localFilters.filters))
      self.logger.debug(">>> isExistStage('STAGE_BEFORE_DOM_PRE'): " + \
                        str(localFilters.isExistStage(Filters.STAGE_BEFORE_DOM_PRE)))
      # (10) Check HTTP headers by name text regular expression check
      if localFilters.isExistStage(Filters.STAGE_BEFORE_DOM_PRE):
        self.logger.debug("Check HTTP headers by name text regular expression check ...")
        if collectURLs.filtersApply(None, resource.response_header, 0, self.dbWrapper,
                                    self.batchItem.siteId, None, Filters.OC_RE,
                                    Filters.STAGE_BEFORE_DOM_PRE, Filters.SELECT_SUBJECT_HEADERS_ALL, True):
          self.logger.debug("HTTP headers by name text regular expression check SUCCESS")
        else:
          self.logger.debug("HTTP headers by name text regular expression check FAILED")
          self.errorMask = self.errorMask | APP_CONSTS.ERROR_CRAWLER_FILTERS_BREAK
          self.updateURLForFailed(self.errorMask)
          return False
      # (10) END

      # (11) Check Last modified datetime value date comparison check
      self.logger.debug("Check Last modified datetime value date comparison check ...")
      self.logger.debug('resource.last_modified = ' + str(resource.last_modified))

      localFilters = Filters(None, self.dbWrapper, self.batchItem.siteId, 0,
                             {'PDATE':str(resource.last_modified)}, Filters.OC_SQLE, Filters.STAGE_BEFORE_DOM_PRE,
                             Filters.SELECT_SUBJECT_LAST_MODIFIED)

      self.logger.debug('>>> localFilters.filters: ' + varDump(localFilters.filters))
      self.logger.debug(">>> isExistStage('STAGE_BEFORE_DOM_PRE'): " + \
                        str(localFilters.isExistStage(Filters.STAGE_BEFORE_DOM_PRE)))

      if localFilters.isExistStage(Filters.STAGE_BEFORE_DOM_PRE):
        if collectURLs.filtersApply(None, '', 0, self.dbWrapper, self.batchItem.siteId,
                                    {'PDATE':str(resource.last_modified)}, Filters.OC_SQLE,
                                    Filters.STAGE_BEFORE_DOM_PRE, Filters.SELECT_SUBJECT_LAST_MODIFIED, True):
          self.logger.debug("Last modified datetime value date comparison check SUCCESS")
        else:
          self.logger.debug("Last modified datetime value date comparison check FAILED")
          self.errorMask = self.errorMask | APP_CONSTS.ERROR_CRAWLER_FILTERS_BREAK
          self.updateURLForFailed(self.errorMask)
          return False
      # (11) END


    except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout), err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_REQUEST_TIMEOUT
      self.updateURLForFailed(APP_CONSTS.ERROR_REQUEST_TIMEOUT)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.InvalidURL:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_BAD_URL
      self.updateURLForFailed(APP_CONSTS.ERROR_BAD_URL)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.TooManyRedirects:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_FETCH_TOO_MANY_REDIRECTS
      self.updateURLForFailed(APP_CONSTS.ERROR_FETCH_TOO_MANY_REDIRECTS)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.ChunkedEncodingError:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_PAGE_CONVERT_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_PAGE_CONVERT_ERROR)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.ConnectionError:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_CONNECTION_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_CONNECTION_ERROR)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.ContentDecodingError:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_PAGE_CONVERT_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_PAGE_CONVERT_ERROR)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except lxml.etree.XMLSyntaxError:  # pylint: disable=E1101
      self.logger.debug("XML HTML syntax error")
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_DTD_INVALID
      self.updateURLForFailed(APP_CONSTS.ERROR_DTD_INVALID)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except ProxyException, err:
      self.logger.debug('self.errorMask = ' + str(self.errorMask) + ' err.code = ' + str(err.code) + \
                        ' err.statusUpdate = ' + str(err.statusUpdate))
      status = dc_event.URL.STATUS_CRAWLED
      if err.statusUpdate is not None:
        status = err.statusUpdate
      self.logger.debug('Set status update = ' + str(status))
      self.errorMask = self.errorMask | err.code
      self.updateURLForFailed(self.errorMask, SeleniumFetcher.ERROR_PROXY_CONNECTION_FAILED, status)
      self.res = self.makeDefaultResponse(self.res, SeleniumFetcher.ERROR_PROXY_CONNECTION_FAILED)
      return False
    except SeleniumFetcherException, err:
      self.logger.error("Selenium fetcher error: " + str(err) + ' code = ' + str(err.code))
      httpCode = CONSTS.HTTP_CODE_400
      if err.code in self.errorMaskHttpCodeDict:
        httpCode = self.errorMaskHttpCodeDict[err.code]
      self.errorMask = self.errorMask | err.code
      self.updateURLForFailed(self.errorMask, httpCode)
      self.res = self.makeDefaultResponse(self.res, httpCode)
      return False
    except UrlAvailableException, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_CONNECTION_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_CONNECTION_ERROR)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.HTTPError, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_FETCH_HTTP_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_FETCH_HTTP_ERROR)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.URLRequired, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_FETCH_INVALID_URL
      self.updateURLForFailed(APP_CONSTS.ERROR_FETCH_INVALID_URL)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except requests.exceptions.RequestException, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_FETCH_AMBIGUOUS_REQUEST
      self.updateURLForFailed(APP_CONSTS.ERROR_FETCH_AMBIGUOUS_REQUEST)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except CrawlerFilterException, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_CRAWLER_FILTERS_BREAK
      self.updateURLForFailed(APP_CONSTS.ERROR_CRAWLER_FILTERS_BREAK)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except NotModifiedException, err:
      status = dc_event.URL.STATUS_CRAWLED
      updateUDate = True
      if self.detectModified is not None:
        status, updateUDate = self.detectModified.notModifiedStateProcessing(self.batchItem.siteId, self.realUrl,
                                                                             self.dbWrapper, status, updateUDate)
        self.logger.debug("!!! URL is NOT MODIFIED. Update httpCode = %s, status = %s, updateUDate = %s",
                          str(err.httpCode), str(status), str(updateUDate))

      self.updateURLForFailed(self.errorMask, err.httpCode, status, updateUDate)
      self.res = self.makeDefaultResponse(self.res, err.httpCode)
      return False
    except DatabaseException, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_DATABASE_ERROR
      self.updateURLForFailed(APP_CONSTS.ERROR_DATABASE_ERROR)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except InternalCrawlerException, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_FETCHER_INTERNAL
      self.updateURLForFailed(APP_CONSTS.ERROR_FETCHER_INTERNAL)
      self.res = self.makeDefaultResponse(self.res)
      return False
    except Exception, err:
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_GENERAL_CRAWLER
      self.updateURLForFailed(APP_CONSTS.ERROR_GENERAL_CRAWLER)
      ExceptionLog.handler(self.logger, err, "Crawler fatal error.", (err), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      return False

    return True


  # # Make defailt response
  #
  # @param response - instance of Response
  # @param httpCode - HTTP code
  # @return response - updated instance of Response
  def makeDefaultResponse(self, response, httpCode=CONSTS.HTTP_CODE_400):

    if response is None:
      response = Response()
    # set default values for response
    response.status_code = httpCode
    response.unicode_content = ""
    response.str_content = ""
    response.rendered_unicode_content = ""
    response.content_size = 0
    response.encoding = ""
    response.headers = {"content-length": 0, "content-type": ""}
    response.meta_res = ""

    return response


  # updateAVGSpeed update sites.AVGSpeed property
  def updateAVGSpeed(self):
    if self.res.status_code == CONSTS.HTTP_CODE_304:
      # not modified will return empty response body
      return

    avgSpeed = (self.site.avgSpeed * self.site.avgSpeedCounter + self.crawledResource.bps)\
               / (self.site.avgSpeedCounter + 1)
    self.site.avgSpeed = avgSpeed
    self.site.avgSpeedCounter += 1

    if self.dbWrapper is not None:
      localSiteUpdate = dc_event.SiteUpdate(self.batchItem.siteId)
      for attr in localSiteUpdate.__dict__:
        if hasattr(localSiteUpdate, attr):
          setattr(localSiteUpdate, attr, None)
      localSiteUpdate.id = self.batchItem.siteId
      localSiteUpdate.avgSpeed = avgSpeed
      localSiteUpdate.avgSpeedCounter = SQLExpression("`AVGSpeedCounter` + 1")
      self.dbWrapper.siteNewOrUpdate(localSiteUpdate)


  # saveCookies
  def saveCookies(self):
    self.logger.debug(MSG_INFO_STORE_COOKIES_FILE)
    timePostfix = ""
    if self.keep_old_resources:
      timePostfix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    self.logger.debug("self.storeCookies = %s", str(self.storeCookies))
    if self.storeCookies:
      # #cookies_str = [key + ": " + value + "; " for (key, value) in self.crawledResource.cookies.items()]
#       self.logger.debug("self.res.headers: '%s'", str(self.res.headers))
#       self.logger.debug("self.crawledResource.cookies: '%s'", str(self.crawledResource.cookies))

      cookies_str = ''
      if RequestsRedirectWrapper.RESPONSE_COOKIE_HEADER_NAME in self.res.headers:
        # set raw cookies string from header
        cookies_str = self.res.headers[RequestsRedirectWrapper.RESPONSE_COOKIE_HEADER_NAME]

      elif isinstance(self.crawledResource.cookies, dict):
        # set cookies from cookies dictionary
        cookies_str = ''.join([key + ": " + value + "; " for (key, value) in self.crawledResource.cookies.items()])

      self.makeDir()
      self.logger.debug("Response cookies string: %s", str(cookies_str))
      self.logger.debug("self.batchItem.urlId: %s", str(self.batchItem.urlId))
      self.logger.debug("timePostfix: %s", str(timePostfix))
      if timePostfix == "":
        base_path = os.path.join(self.dir, self.batchItem.urlId)
      else:
        base_path = os.path.join(self.dir, self.batchItem.urlId + "_" + str(timePostfix))
      cookies_file_name = base_path + COOKIES_FILE_POSTFIX
      with open(cookies_file_name, "wb") as f:
        # #f.write(''.join(sorted(cookies_str)))
        f.write(cookies_str)


  # #prepare request headers and cookie
  #
  # @param site - site object
  # TODO move to - [SiteProcess]
  def readSiteProperties(self):
    # TODO not sure is it right that fetch headers and cookie
    # by `Name` = 'headers'/'cookie'
    self.storeHttpRequest = True
    self.store_http_headers = True
    self.headersDict = {}
    self.postForms = {}
    self.headers = None
    self.cookie = ''
    self.proxies = None
    self.authName = None,
    self.authPwd = None
    self.external_url = None
    self.auto_remove_props = {}
    self.htmlRecover = None
    self.autoDetectMime = None
    self.processContentTypes = []
    cookie = None

    try:
      # stub
      # self.logger.debug("self.site.properties: %s", varDump(self.site.properties))

      # Update site properties from batch item properties
      keys = [localProperty["name"] for localProperty in self.site.properties]
      # self.logger.debug("keys: %s" % str(keys))
      for key in self.batchItem.properties.keys():
        if key in keys:
          for localProperty in self.site.properties:
            if localProperty["name"] == key:
              self.logger.debug("%s present in site properties. Rewrite localProperty" % key)
              localProperty["value"] = self.batchItem.properties[key]
        else:
          self.logger.debug("%s not present in site properties. Add localProperty" % key)
          self.site.properties.append({"name":key, "value":self.batchItem.properties[key],
                                       "URLMd5":self.batchItem.urlId})
      # self.logger.debug("Updated site's properties: " + str(self.site.properties))
      self.siteProperties = {}
      for item in self.site.properties:
        self.siteProperties[item["name"]] = item["value"]
      self.initHTTPHeaders()
      if 'HTTP_COOKIE' in self.siteProperties and self.siteProperties['HTTP_COOKIE'] != "":
        self.cookieResolver = HTTPCookieResolver(self.siteProperties['HTTP_COOKIE'])
      else:
        self.cookieResolver = HTTPCookieResolver()

      if 'STORE_HTTP_REQUEST' in self.siteProperties:
        self.storeHttpRequest = int(self.siteProperties['STORE_HTTP_REQUEST']) != 0
      if 'STORE_HTTP_HEADERS' in self.siteProperties:
        self.store_http_headers = int(self.siteProperties['STORE_HTTP_HEADERS']) != 0
      if 'MIME_TYPE_STORE_ON_DISK' in self.siteProperties:
        allowMimes = self.siteProperties['MIME_TYPE_STORE_ON_DISK']
        if allowMimes is not None and allowMimes != '' and allowMimes != '*':
          self.needStoreMime = set([mime.lower() for mime in allowMimes.split(',')])
      if 'HTTP_AUTH_NAME' in self.siteProperties:
        self.authName = self.siteProperties['HTTP_AUTH_NAME']
      if 'HTTP_AUTH_PWD' in self.siteProperties:
        self.authPwd = self.siteProperties['HTTP_AUTH_PWD']
      for key in self.siteProperties.keys():
        if key.startswith('HTTP_POST_FORM_'):
          self.postForms[key[15:]] = self.siteProperties[key]
      if 'EXTERNAL_URL' in self.siteProperties:
        self.external_url = self.siteProperties['EXTERNAL_URL']  # pylint: disable=W0201
      if 'HTML_RECOVER' in self.siteProperties:
        self.htmlRecover = self.siteProperties['HTML_RECOVER']  # pylint: disable=W0201
      if 'MIME_TYPE_AUTO_DETECT' in self.siteProperties:
        self.autoDetectMime = self.siteProperties['MIME_TYPE_AUTO_DETECT']  # pylint: disable=W0201
      if 'ALLOWED_CTYPES' in self.siteProperties:
        self.processContentTypes = self.siteProperties['ALLOWED_CTYPES'].lower().split(',')  # pylint: disable=W0201
      if 'PROCESSOR_NAME' in self.siteProperties:
        self.processorName = self.siteProperties['PROCESSOR_NAME']
      if DC_CONSTS.SITE_PROP_SAVE_COOKIES in self.siteProperties:
        self.storeCookies = int(self.siteProperties[DC_CONSTS.SITE_PROP_SAVE_COOKIES]) > 0
      if DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES in self.siteProperties:
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES] = \
        self.siteProperties[DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES]
      if DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER in self.siteProperties:
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER] = \
        self.siteProperties[DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER]
      if DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE in self.siteProperties:
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE] = \
        self.siteProperties[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE]
      if DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE_ACTIVE in self.siteProperties:
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE_ACTIVE] = \
        self.siteProperties[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE_ACTIVE]
      if 'URL_NORMALIZE_MASK' in self.siteProperties:
        self.normMask = int(self.siteProperties['URL_NORMALIZE_MASK'])
      if APP_CONSTS.URL_NORMALIZE in self.siteProperties:
        self.normMask = UrlNormalize.getNormalizeMask(siteProperties=self.siteProperties, defaultValue=self.normMask)
      if self.urlProcess is not None:
        self.urlProcess.normMask = self.normMask
      if 'HTTP_REDIRECTS_MAX' in self.siteProperties:
        self.max_http_redirects = int(self.siteProperties['HTTP_REDIRECTS_MAX'])
      if 'HTML_REDIRECTS_MAX' in self.siteProperties:
        self.max_html_redirects = int(self.siteProperties['HTML_REDIRECTS_MAX'])
      if 'COLLECT_URLS_XPATH_LIST' in self.siteProperties:
        self.urlXpathList = json.loads(self.siteProperties['COLLECT_URLS_XPATH_LIST'])
      if 'URL_TEMPLATE_REGULAR' in self.siteProperties:
        self.urlTempalteRegular = self.siteProperties['URL_TEMPLATE_REGULAR']
      if 'URL_TEMPLATE_REALTIME' in self.siteProperties:
        self.urlTempalteRealtime = self.siteProperties['URL_TEMPLATE_REALTIME']
      if 'URL_TEMPLATE_REGULAR_URLENCODE' in self.siteProperties:
        self.urlTempalteRegularEncode = self.siteProperties['URL_TEMPLATE_REGULAR_URLENCODE']
      if 'URL_TEMPLATE_REALTIME_URLENCODE' in self.siteProperties:
        self.urlTempalteRealtimeEncode = self.siteProperties['URL_TEMPLATE_REALTIME_URLENCODE']
      if 'PROTOCOLS' in self.siteProperties:
        if self.urlProcess is not None:
          self.urlProcess.setProtocols(self.siteProperties['PROTOCOLS'])
      if 'DETECT_MODIFIED' in self.siteProperties:
        self.detectModified = DetectModified(self.siteProperties['DETECT_MODIFIED'])
      if 'CONTENT_TYPE_MAP' in self.siteProperties:
        try:
          self.siteProperties['CONTENT_TYPE_MAP'] = json.loads(self.siteProperties['CONTENT_TYPE_MAP'])
        except Exception:
          self.siteProperties['CONTENT_TYPE_MAP'] = {}

      if self.defaultHeaderFile is not None:
        # read request headers from crawler-task_headers.txt file
        self.headers = CrawlerTask.readSmallFileContent(self.defaultHeaderFile)

      if self.cookieResolver is None:
        # read request cookies from crawler-task_headers.txt file
        cookie = CrawlerTask.readSmallFileContent(self.defaultCookieFile)

      if cookie is not None and cookie != "":
        if cookie.lower().startswith('cookie:'):
          self.cookie = cookie[len('cookie:'):]
        else:
          self.cookie = cookie

      # TODO: algorithm is not clear
      for header in self.headers.splitlines():
        if not header:
          continue
        try:
          key, value = header[:header.index(':')].strip(), header[header.index(':') + len(':'):].strip()
        except Exception:
          self.logger.debug("header:%s", header)

        if key[0] != '#':
          self.headersDict[key] = value
      if self.cookie != "":
        self.headersDict['Cookie'] = self.cookie

      self.logger.debug("proxies: %s", self.proxies)
      self.urlProcess.siteProperties = self.siteProperties
    except Exception, err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_LOAD_SITE_PROPERTIES)
      self.errorMask |= APP_CONSTS.ERROR_CRAWLER_FATAL_INITIALIZATION_PROJECT_ERROR


  # # initHeaders initialize HTTP request headers set
  #
  def initHTTPHeaders(self):
    if 'HTTP_HEADERS' in self.siteProperties and self.siteProperties['HTTP_HEADERS'] != "":
      lh = self.siteProperties['HTTP_HEADERS']
      if lh.startswith('file://'):
        lh = Utils.loadFromFileByReference(fileReference=lh, loggerObj=self.logger)
        self.siteHeaders = {'User-Agent': [h.strip() for h in lh.split("\n") if len(h) > 0 and h[0] != '#']}
      else:
        self.siteHeaders = self.hTTPHeadersStorage.extractSiteStorageElement(lh)
        for lh in self.siteHeaders:
          if isinstance(self.siteHeaders[lh], basestring):
            if self.siteHeaders[lh].startswith('file://'):
              self.siteHeaders[lh] = Utils.loadFromFileByReference(fileReference=lh, loggerObj=self.logger)
            else:
              self.siteHeaders[lh] = [self.siteHeaders[lh]]


# #   # # resolveProxy resolve http proxies for current url
# #   #
# #   def resolveProxy(self, tmpProxies):
# #     ret = None
# #     if self.url is not None:
# #       self.proxyResolver = ProxyResolver(self.siteProperties, self.dbWrapper, self.batchItem.siteId, self.url.url)
# #       result = self.proxyResolver.getProxy(tmpProxies)
# #       if result is not None:
# #         ret = ("http", result[0], result[1], None, None)
# #     return ret


  # # readSmallFileContent read small file content
  #
  # @param path the file path to read
  @staticmethod
  def readSmallFileContent(path):
    with open(path, 'r') as f:
      return ''.join(f.readlines())


  # #update site params
  # update site params
  # @param mask ErrorMask
  # @param is_suspend should set state to suspend for this site
  def updateSiteParams(self, mask, is_suspend=False):
    ret = False
    if self.dbWrapper is None:
      ret = True
    else:
      try:
        localSiteUpdate = dc_event.SiteUpdate(self.batchItem.siteId)
        for attr in localSiteUpdate.__dict__:
          if hasattr(localSiteUpdate, attr):
            setattr(localSiteUpdate, attr, None)

        # TODO: possible redundant for the URLFetch algorithm and need to be removed
        if mask:
          # localSiteUpdate.errors = SQLExpression("`Errors` + 1")
          localSiteUpdate.errorMask = SQLExpression(("`ErrorMask` | %s" % mask))
          if is_suspend:
            localSiteUpdate.state = Site.STATE_SUSPENDED

        localSiteUpdate.id = self.batchItem.siteId
        localSiteUpdate.updateType = dc_event.SiteUpdate.UPDATE_TYPE_UPDATE
        updated_count = self.dbWrapper.siteNewOrUpdate(siteObject=localSiteUpdate, stype=dc_event.SiteUpdate)
        if updated_count > 0:
          ret = True
      except DatabaseException, err:
        ExceptionLog.handler(self.logger, err, MSG_ERROR_UPDATE_SITE_DATA, (err))
        raise err
      except Exception, err:
        ExceptionLog.handler(self.logger, err, MSG_ERROR_UPDATE_SITE_DATA, (err))
        raise err

    return ret


  # # update site use sql expression evaluator
  #
  # @param - None
  # @return ret - True if success or False otherwise
  def updateSite(self):
    ret = False

    if self.dbWrapper is None:
      ret = True
    else:
      if self.site is not None and APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER in self.siteProperties:
        try:
          localSiteUpdate = dc_event.SiteUpdate(self.batchItem.siteId)
          for attr in localSiteUpdate.__dict__:
            if hasattr(localSiteUpdate, attr):
              setattr(localSiteUpdate, attr, None)

          # Evaluate 'Site' class values if neccessary
          changedFieldsDict = FieldsSQLExpressionEvaluator.execute(self.siteProperties, self.dbWrapper, self.site,
                                                                   None, self.logger,
                                                                   APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
          # Update 'Site' class values
          for name, value in changedFieldsDict.items():
            if hasattr(localSiteUpdate, name) and value is not None and name not in ['CDate', 'UDate', 'tcDate']:
              setattr(localSiteUpdate, name, value)

          localSiteUpdate.errorMask = SQLExpression(("`ErrorMask` | %s" % self.site.errorMask))
          localSiteUpdate.id = self.batchItem.siteId
          localSiteUpdate.updateType = dc_event.SiteUpdate.UPDATE_TYPE_UPDATE

          updatedCount = self.dbWrapper.siteNewOrUpdate(siteObject=localSiteUpdate, stype=dc_event.SiteUpdate)
          self.logger.debug('Updated ' + str(updatedCount) + ' rows.')
          if updatedCount > 0:
            ret = True
        except DatabaseException, err:
          self.logger.error("Update 'Site' failed, error: %s", str(err))
          raise err
        except Exception, err:
          self.logger.error("Update 'Site' failed, error: %s", str(err))
          raise err

    return ret


  # #Check sevarl common conditions
  #
  # @return Boolean that means - should continue execute this BatchItem or not
  def commonChecks(self, urlObj):
    if self.site is None or urlObj is None:
      self.logger.error('Error: self.site or urlObj is None!')
      return False
    # self.logger.debug("urlObj:" + str(urlObj))

    if((self.batch.crawlerType != dc_event.Batch.TYPE_REAL_TIME_CRAWLER) and (self.site.state != Site.STATE_ACTIVE)) \
    or ((self.batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER) and (self.site.state == Site.STATE_DISABLED)):
      self.logger.debug("Warning: Batch CrawlerType: %s, site state is %s but is not STATE_ACTIVE!"
                        % (str(self.batch.crawlerType), str(self.site.state)))
      self.errorMask = self.errorMask | APP_CONSTS.ERROR_MASK_SITE_STATE
      return False

    if not self.isRootURL(urlObj):
      if self.site.maxErrors > 0 and self.site.errors > self.site.maxErrors:
        self.logger.debug("Site max errors: %s limit: %s is reached", str(self.site.errors), str(self.site.maxErrors))
        # TODO: possible improve suspend logic to use the property to define, suspend the site if limit reached or not
        # self.updateSiteParams(CONSTS.ERROR_SITE_MAX_ERRORS, True)
        self.errorMask = self.errorMask | APP_CONSTS.ERROR_SITE_MAX_ERRORS
        self.updateSiteParams(APP_CONSTS.ERROR_SITE_MAX_ERRORS)
        return False

    return True


  # #Is URL object a root URL
  #
  # @param urlObj
  # @param urlString
  # @return True if URL object a root URL or False
  def isRootURL(self, urlObj, urlString=None):
    ret = False

    if urlString is None:
      if urlObj.parentMd5 == '':
        ret = True
    else:
      if urlString == '':
        ret = True

    return ret


  # # load site structure
  # the site object to crawl
  # @param batch - batch object instance
  def loadSite(self, batch):
    try:
      # # FIXED alexv 2015-11-11
      # if not len(self.batchItem.siteId):
      #  self.batchItem.siteId = "0"

      if batch.crawlerType != dc_event.Batch.TYPE_REAL_TIME_CRAWLER:  # # FIXED alexv 2017-07-24
        self.readSiteFromDB()

        # Check if site not exist then read site for siteId=0
        if self.site.id == SITE_MD5_EMPTY and bool(self.useZeroSiteIdSiteNotExists):
          self.logger.debug("Site not found. Assume a site id as: `0`")
          self.batchItem.siteId = '0'
          self.batchItem.urlObj.siteId = '0'
          self.readSiteFromDB()
      else:
        # Create empty Site object
        self.site = dc_event.Site("")
        self.site.id = '0'

      # self.logger.debug(">>> site before = " + varDump(self.site))
      if self.site is not None and self.batchItem.siteObj is not None:
        self.site.rewriteFields(self.batchItem.siteObj)
      # self.logger.debug(">>> site after = " + varDump(self.site))
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_LOAD_SITE_DATA, (err))
      self.errorMask |= APP_CONSTS.ERROR_CRAWLER_FATAL_INITIALIZATION_PROJECT_ERROR
      raise err


  # #load url
  # the site object to crawl
  # @param site - object to crawl
  def readSiteFromDB(self):
    siteStatus = dc_event.SiteStatus(self.batchItem.siteId)
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.SITE_STATUS, siteStatus)
    responseDRCESyncTasksCover = self.dbWrapper.process(drceSyncTasksCoverObj)
    self.site = None
    self.siteTable = DC_SITES_TABLE_NAME
    try:
      self.site = responseDRCESyncTasksCover.eventObject
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_READ_SITE_FROM_DB, (err))
      raise Exception


  # #load url
  # the site object to crawl
  # @param site - object to crawl
  def loadURL(self):
    # do siteId

    if len(self.batchItem.siteId):
      self.urlTable = DC_URLS_TABLE_PREFIX + self.batchItem.siteId
    else:
      self.urlTable = DC_URLS_TABLE_PREFIX + "0"
    self.logger.debug("db backend Table for siteId %s is: %s" % (self.batchItem.siteId, self.urlTable))
    self.urlProcess.siteId = self.batchItem.siteId
    self.urlProcess.urlTable = self.urlTable
    self.url = self.batchItem.urlObj
    self.urlProcess.urlDBSync(self.batchItem, self.batch.crawlerType, self.site.recrawlPeriod,
                              self.auto_remove_props)
    if self.urlProcess.isUpdateCollection:
      self.updateCollectedURLs()


  # #resetVars
  def resetVars(self):
    self.needStoreMime = None  # pylint: disable=F0401,W0201
    self.site = None  # pylint: disable=F0401,W0201
    self.headersDict = None  # pylint: disable=F0401,W0201
    self.store_http_headers = True  # pylint: disable=F0401,W0201
    self.cookie = None  # pylint: disable=F0401,W0201
    self.proxies = None  # pylint: disable=F0401,W0201
    self.realUrl = None  # pylint: disable=F0401,W0201
    self.url = None
    self.crawledResource = None
    self.headers = None  # pylint: disable=F0401,W0201
    self.crawledTime = None  # pylint: disable=F0401,W0201
    self.storeHttpRequest = True  # pylint: disable=F0401,W0201
    self.dir = None  # pylint: disable=F0401,W0201
    self.kvConnector = None  # pylint: disable=F0401,W0201
    self.kvCursor = None  # pylint: disable=F0401,W0201
    self.processorName = None  # pylint: disable=F0401,W0201
    self.auto_remove_props = None  # pylint: disable=F0401,W0201
    self.storeCookies = True  # pylint: disable=F0401,W0201
    self.allow_http_redirects = True
    self.allow_html_redirects = True  # pylint: disable=F0401,W0201
    self.httpRedirects = 0  # pylint: disable=F0401,W0201
    self.htmlRedirects = 0  # pylint: disable=F0401,W0201
    self.max_http_redirects = CONSTS.MAX_HTTP_REDIRECTS_LIMIT  # pylint: disable=F0401,W0201
    self.max_html_redirects = CONSTS.MAX_HTML_REDIRECTS_LIMIT  # pylint: disable=F0401,W0201
    self.dom = None
    self.res = None  # pylint: disable=F0401,W0201
    self.postForms = None  # pylint: disable=F0401,W0201
    self.authName = None  # pylint: disable=F0401,W0201
    self.authPwd = None  # pylint: disable=F0401,W0201
    self.siteProperties = {}  # pylint: disable=F0401,W0201
    self.urlXpathList = {}  # pylint: disable=F0401,W0201
    self.errorMask = APP_CONSTS.ERROR_OK
    self.feed = None  # pylint: disable=F0401,W0201
    self.feedItems = None
    self.urlTempalteRegular = None  # pylint: disable=F0401,W0201
    self.urlTempalteRealtime = None  # pylint: disable=F0401,W0201
    self.urlTempalteRegularEncode = None  # pylint: disable=F0401,W0201
    self.urlTempalteRealtimeEncode = None  # pylint: disable=F0401,W0201
    self.detectModified = None  # pylint: disable=F0401,W0201
    self.collectURLsItems = []
    self.schemaBatchItems = []


  # #updateBatchItemAfterCarwling fills some field in the class fields objects after crawling
  def updateBatchItemAfterCarwling(self, status=dc_event.URL.STATUS_CRAWLED):
    self.urlProcess.urlObj = self.url
    self.urlProcess.siteId = self.batchItem.siteId
    self.logger.debug("set siteId = '" + str(self.urlProcess.siteId) + "' from 'updateBatchItemAfterCarwling'")

    # Update status value accord to dict HTTP codes
    if "HTTP_CODE_STATUS_UPDATE" in self.siteProperties and self.siteProperties["HTTP_CODE_STATUS_UPDATE"] != "":
      self.logger.debug('!!!!!! HTTP_CODE_STATUS_UPDATE !!!!! ')
      # Default value
      status = dc_event.URL.STATUS_CRAWLED
      try:
        statusDict = json.loads(self.siteProperties["HTTP_CODE_STATUS_UPDATE"])
        self.logger.debug('!!!!!! statusDict: ' + str(statusDict))
        if str(self.crawledResource.http_code) in statusDict:
          self.logger.debug("Change status from (%s) to (%s), because http_code = %s", str(status), \
                            str(statusDict[str(self.crawledResource.http_code)]), str(self.crawledResource.http_code))
          status = int(statusDict[str(self.crawledResource.http_code)])
      except Exception, err:
        self.logger.error("Load property 'HTTP_CODE_STATUS_UPDATE' has error: " + str(err))

    if status is not None:
      self.batchItem.urlObj.status = dc_event.URL.STATUS_CRAWLED
    self.batchItem.urlObj.crawlingTime = self.crawledResource.crawling_time
    self.batchItem.urlObj.errorMask |= self.crawledResource.error_mask
    if self.batchItem.urlObj.charset == "":
      self.batchItem.urlObj.charset = self.crawledResource.charset
    if self.batchItem.urlObj.httpCode == 0:
      self.batchItem.urlObj.httpCode = self.crawledResource.http_code
    if self.batchItem.urlObj.contentType == "":
      self.batchItem.urlObj.contentType = self.crawledResource.content_type
    self.batchItem.urlObj.crawled = 1
    if self.batchItem.urlObj.size == 0:
      self.batchItem.urlObj.size = self.res.content_size
    self.batchItem.urlObj.CDate = self.batchItem.urlObj.UDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.batchItem.urlObj.tagsCount = 0
    self.batchItem.urlObj.tagsMask = 0

    if self.urlProcess.siteProperties is None:
      self.urlProcess.siteProperties = self.siteProperties

    self.urlProcess.updateCrawledURL(self.crawledResource, self.batchItem, self.res.content_size, status)


  # #process batch item
  # the batch item is the one from list of batch items within batch object
  # @param item - the batch item is the one from list of batch items within batch object
  def processBatchItem(self):
    self.resetVars()
    self.logger.info("Batch item START, siteId: %s, urlId: %s, self.batch.crawlerType: %s",
                     self.batchItem.siteId, self.batchItem.urlId, str(self.batch.crawlerType))
    isResourceCrawled = False
    nextStep = True
    detectedMime = None
    mpLogger = Utils.MPLogger()
    self.urlProcess.siteId = self.batchItem.siteId

    try:
      # self.logger.debug("BatchItem: %s" % varDump(self.batchItem))
      self.loadSite(self.batch)

      # prepare headers and cookie
      self.readSiteProperties()

      if 'LOGGER' in self.siteProperties and self.siteProperties['LOGGER'] is not None and\
        self.siteProperties['LOGGER'] != '':
        self.logger.info("Switch logger to dedicated project %s log", str(self.batchItem.siteId))
        self.setLogConfigFileProject(mpLogger, self.batchItem.siteId, self.siteProperties['LOGGER'])

      # self.batchItem = self.changeBatchItemByUrlSchema(self.batchItem, self.batch.id)
      self.setChainId(self.batchItem)
      if self.robotsParser is not None:
        self.robotsParser.\
        initFiends(None, (bool(int(self.siteProperties['ROBOTS_CACHE'])) if \
                          'ROBOTS_CACHE' in self.siteProperties else False),
                   self.robotsFileDir)
      # Check if Real-Time crawling
      if self.batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        if self.batchItem.urlObj.urlPut is not None:
          self.batchItem.urlObj.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK
          # save tidy recovered file
          if "data" in self.batchItem.urlObj.urlPut.putDict:
            raw_unicode_content = self.batchItem.urlObj.urlPut.putDict["data"]
            localDom = None
            if self.htmlRecover is not None and self.htmlRecover == "2":
              localDom = self.resourceProcess.\
                          domParser(None, raw_unicode_content, CONSTS.HTTP_CODE_200,
                                    self.crawledResource.charset if self.crawledResource is not None else None)
            if self.htmlRecover is not None and (self.htmlRecover == "1" or self.htmlRecover == "2" and \
              localDom is None):
              tidy_content = tidylib.tidy_document(raw_unicode_content, self.tidyOptions)[0]
              self.batchItem.urlObj.urlPut.putDict["data"] = base64.b64encode(tidy_content)
        # TODO: need for comments
        if self.batch.dbMode & dc_event.Batch.DB_MODE_W == 0:
          self.url = self.batchItem.urlObj  # pylint: disable=W0201
      else:
        self.loadURL()

      if not self.commonChecks(self.url):
        self.logger.debug("Common checks failed!")
        nextStep = False
        # self.batchItem = None
        # return self.batchItem

      if nextStep and "HTTP_FREQ_LIMITS" in self.siteProperties:
        hostRequestStorage = HostRequestStorage(self.siteProperties["HTTP_FREQ_LIMITS"])
        if hostRequestStorage.checkHost(None, self.url.url, self.batchItem.siteId) == HostRequestStorage.ITEM_BREAK:
          self.logger.debug(">>> Skip url [%s] by http requests freq", self.url.url)
          self.url.status = dc_event.URL.STATUS_NEW
          self.url.errorMask = APP_CONSTS.ERROR_NO_TIME_WINDOW
          self.url.httpCode = CONSTS.HTTP_CODE_400
          self.urlProcess.updateURLStatus(self.batchItem.urlId, self.url.status)
          nextStep = False

      # Check if Real-Time crawling resource already crawled
      if nextStep and self.batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        # TODO: strange condition: self.url.tagsCount > 0
        if self.url.crawled > 0 and self.url.errorMask == APP_CONSTS.ERROR_OK and self.url.tagsCount > 0 and\
          self.errorMask == APP_CONSTS.ERROR_OK:
          self.logger.debug("RealTime Crawling: Cashed resource. Resource crawled and error mask is empty")
          if PCONSTS.RECRAWL_KEY not in self.batchItem.properties or \
          int(self.batchItem.properties[PCONSTS.RECRAWL_KEY]) == PCONSTS.RECRAWL_VALUE_NO:
            self.logger.debug("Item not need to be recrawled.")
            # set contentMask stored on disk
            self.batchItem.urlObj.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK
            # return self.batchItem
            nextStep = False
          else:
            self.logger.debug("Property `recrawl` = %s. Item recrawling." % \
                              str(self.batchItem.properties[PCONSTS.RECRAWL_KEY]))

      if nextStep:
        # reset error mask for current crawled url
        self.urlProcess.resetErrorMask(self.batchItem)
        # update state to crawling
        self.urlProcess.urlObj = self.url
        self.urlProcess.updateURL(self.batchItem, self.batch.id)
        self.logger.debug('Start to crawl item')
        isResourceCrawled = self.crawl(self.batchItem.urlObj.urlPut.putDict["data"] if \
                                       (self.batchItem.urlObj.urlPut is not None and \
                                       self.batchItem.urlObj.urlPut.putDict is not None and "data" in \
                                       self.batchItem.urlObj.urlPut.putDict) else None)

        self.logger.debug("After crawl() isResourceCrawled: %s", str(isResourceCrawled))

        if self.crawledResource is not None and isResourceCrawled:
          # TODO move to - [SiteProcess]
          self.updateAVGSpeed()
          # Build DOM object
          if self.batchItem.urlObj.type == dc_event.URL.TYPE_SINGLE:
            self.logger.debug('URL type single, do not pars and build DOM, set self.dom = None')
            self.dom = None
          else:
            self.logger.debug('Build DOM, call domParser()\n self.crawledResource.charset = ' + \
                              str(self.crawledResource.charset))
            self.dom = self.resourceProcess.domParser(self.htmlRecover, self.crawledResource.html_content,
                                                      self.crawledResource.http_code,
                                                      self.crawledResource.charset if self.crawledResource is not None\
                                                      else None)
            # # check dom value
            if self.dom is None:
              self.errorMask |= APP_CONSTS.ERROR_PARSE_ERROR
              self.updateURLForFailed(self.errorMask)

          # Set pDate accord to site property 'PDATE_SOURCE_MASK'
          self.logger.debug('>>>>> self.crawledResource.last_modified = ' + str(self.crawledResource.last_modified))

          self.logger.debug('>>> Before getPubdateUseSourceMask() self.batchItem.urlObj.pDate = ' + \
                            str(self.batchItem.urlObj.pDate))
          self.batchItem.urlObj.pDate = self.getPubdateUseSourceMask(self.siteProperties, \
                                                             self.crawledResource, \
                                                             self.batchItem.urlObj)
          self.logger.debug('>>> After getPubdateUseSourceMask() self.batchItem.urlObj.pDate = ' + \
                            str(self.batchItem.urlObj.pDate))

          # Add 'feed_url' to headers
          if self.processorName == PCONSTS.PROCESSOR_FEED_PARSER or self.processorName == PCONSTS.PROCESSOR_RSS:
            parentUrl = self.refererHeaderResolver.fetchParentUrl(self.batchItem.siteId,
                                                                  self.url.parentMd5,
                                                                  self.dbWrapper)
            self.logger.debug("!!! parentUrl: %s", str(parentUrl))
            self.logger.debug("!!! self.url.parentMd5: %s", str(self.url.parentMd5))
            self.logger.debug("!!! self.url.url: %s", str(self.url.url))
            self.logger.debug("!!! self.feedUrl: %s", str(self.feedUrl))

            if self.url.parentMd5 == "":
              self.feedUrl[hashlib.md5(self.url.url).hexdigest()] = self.url.url
            elif self.url.parentMd5 != "" and parentUrl is None:
              if self.url.parentMd5 in self.feedUrl:
                parentUrl = self.feedUrl[self.url.parentMd5]

            if parentUrl is not None and parentUrl != "":
              self.addFeedUrlToHeader(self.crawledResource, parentUrl)

          self.logger.debug("!!! self.batchItem.urlObj.baseUrl: %s", str(self.batchItem.urlObj.baseUrl))
          self.logger.debug("!!! self.batchItem.urlObj.url: %s", str(self.batchItem.urlObj.url))
          # Add 'base_url' to batch item and header
          baseUrl = self.extractBaseUrl(self.crawledResource.html_content, \
                                   self.batchItem.urlObj.baseUrl if hasattr(self.batchItem.urlObj, 'baseUrl')  else self.batchItem.urlObj.url)


          self.batchItem.baseUrl = Utils.urlNormalization(base=self.batchItem.urlObj.url, url=baseUrl, log=self.logger)
          self.addBaseUrlToHeader(self.crawledResource, self.batchItem.baseUrl)

          self.getDir()
          try:
            if self.processorName != PCONSTS.PROCESSOR_FEED_PARSER:
              self.writeData()
              try:
                self.saveCookies()
              except Exception, err:
                self.logger.error("saveCookies fail: %s\n%s", str(err), Utils.getTracebackInfo())

            if self.autoDetectMime is not None and \
            ResourceProcess.isAllowedReplaceMimeType(self.autoDetectMime, self.batchItem.urlObj):
              detectedMime = self.resourceProcess.\
                                mimeDetectByContent(self.crawledResource, self.siteProperties["CONTENT_TYPE_MAP"] if \
                                "CONTENT_TYPE_MAP" in self.siteProperties else None, self.batchItem.urlObj)
          except Exception, err:
            self.errorMask |= APP_CONSTS.ERROR_WRITE_FILE_ERROR
            self.updateURLForFailed(self.errorMask)
            self.logger.error(MSG_ERROR_WRITE_CRAWLED_DATA + ': ' + str(err))
        else:
          nextStep = False

      if nextStep:
        self.logger.debug("Enter in collectURLs()")
        self.collectURLs()

        if self.batchItem.urlObj.chainId is not None and self.batchItem.urlObj.chainId in self.chainDict and \
        self.chainDict[self.batchItem.urlObj.chainId]["batchItem"].urlId == self.batchItem.urlId:
          self.updateBatchItemAfterCarwling(None)
          self.logger.debug(">>> ChainId, update URL without status")
        else:
          self.updateBatchItemAfterCarwling()
        # self.logger.debug('self.feed: %s, self.feedItems: %s', str(self.feed), str(self.feedItems))
        # TODO move to - [UrlProcess]
        self.urlProcess.siteId = self.batchItem.siteId
        # self.logger.debug("!!! detectedMime = %s, self.autoDetectMime = %s ",
        #                  str(detectedMime), str(self.autoDetectMime))
        if self.res is not None:
          self.urlProcess.updateCollectTimeAndMime(detectedMime, self.batchItem, self.crawledTime,
                                                   self.autoDetectMime, self.res.headers, self.res.str_content)
        else:
          self.urlProcess.updateCollectTimeAndMime(detectedMime, self.batchItem, self.crawledTime,
                                                   self.autoDetectMime)
      # (1) END

      # # Update site properties if necessary
      if APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER in self.siteProperties:
        self.updateSite()

    except DatabaseException, err:
      self.errorMask |= APP_CONSTS.ERROR_DATABASE_ERROR
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS_BATCH_ITEM, (err))
    except SyncronizeException, err:
      self.errorMask |= APP_CONSTS.ERROR_SYNCHRONIZE_URL_WITH_DB
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS_BATCH_ITEM, (err), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS_BATCH_ITEM, (err))

    if 'LOGGER' in self.siteProperties and self.siteProperties['LOGGER'] is not None and\
      self.siteProperties['LOGGER'] != '':
      self.logger.info("Switch logger back to default from dedicated for project %s", str(self.batchItem.siteId))
      self.setLogConfigFileDefault(mpLogger)
      self.logger.info("Switched logger back to default from dedicated for project %s", str(self.batchItem.siteId))

    if self.dbWrapper is not None:
      # Update db counters
      self.logger.debug('>>>>> Before self.dbWrapper.fieldsRecalculating([self.batchItem.siteId])')
      self.dbWrapper.fieldsRecalculating([self.batchItem.siteId])
      self.logger.info("Batch item FINISH, siteId: %s, urlId: %s" % (self.batchItem.siteId, self.batchItem.urlId))


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    try:
      input_pickled_object = sys.stdin.read()
      # self.logger.debug("len(input_pickle)=%i", len(input_pickled_object))
      input_batch = pickle.loads(input_pickled_object)

      if input_batch.crawlerType != dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        self.urlProcess.dbWrapper = self.dbWrapper
        self.resourceProcess.dbWrapper = self.dbWrapper

      app.Profiler.messagesList.append("Batch.id: " + str(input_batch.id))
      self.logger.info("Input batch id: %s, items: %s", str(input_batch.id), str(len(input_batch.items)))
      # self.logger.debug("input_batch:\n" + varDump(input_batch))
      self.logger.debug("len before (batch_items)=%i", len(input_batch.items))
      self.generateBatchitemsByURLSchema(input_batch)
      self.logger.debug("len after (batch_items)=%i", len(input_batch.items))

      if int(input_batch.maxExecutionTime) > 0 or (self.maxTimeCli is not None and self.maxTimeCli > 0):
        self.maxExecutionTimeValue = input_batch.maxExecutionTime
        # # set value from cli
        if self.maxTimeCli is not None and self.maxTimeCli > 0:
          self.maxExecutionTimeValue = int(self.maxTimeCli)

        signal.signal(signal.SIGALRM, self.signalHandlerTimer)
        signal.alarm(self.maxExecutionTimeValue)
        self.removeUnprocessedItems = bool(input_batch.removeUnprocessedItems)
        self.logger.debug("Set maxExecutionTime = %s, removeUnprocessedItems = %s",
                          str(self.maxExecutionTimeValue), str(self.removeUnprocessedItems))

      self.batch = input_batch
      Utils.storePickleOnDisk(input_pickled_object, ENV_CRAWLER_STORE_PATH, "crawler.in." + str(self.batch.id))
      batch_items = []
      self.curBatchIterations = 1
      maxBatchIterations = input_batch.maxIterations
      # input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        # TODO: temporary set as 2 to test w/o support on client side
        # maxBatchIterations = 2
      self.logger.debug("maxBatchIterations=%s", str(maxBatchIterations))
      if self.batch.dbMode & dc_event.Batch.DB_MODE_W == 0:
        if self.dbWrapper is not None:
          self.dbWrapper.affect_db = False
      while True:
        self.curBatchIterations += 1
        beforeItems = 0
        self.logger.debug("self.curBatchIterations=%s, beforeItems=%s", str(self.curBatchIterations), str(beforeItems))
        for index, batchItem in enumerate(self.batch.items):
          # check max execution time
          if self.maxExecutionTimeReached:
            self.logger.debug("Maximum execution time %ss reached, process batch items loop interrupted!",
                              str(self.maxExecutionTimeValue))
            self.errorMask = APP_CONSTS.ERROR_MAX_EXECUTION_TIME
            if self.removeUnprocessedItems:
              break
            else:
              batchItem.urlObj.status = dc_event.URL.STATUS_NEW
              batch_items.append(batchItem)
              continue

          if batchItem.urlObj.status == dc_event.URL.STATUS_NEW or \
          batchItem.urlObj.status == dc_event.URL.STATUS_SELECTED_CRAWLING or \
          batchItem.urlObj.status == dc_event.URL.STATUS_SELECTED_CRAWLING_INCREMENTAL:
            self.errorMask = batchItem.urlObj.errorMask
            batchItem.urlObj.status = dc_event.URL.STATUS_CRAWLING
            self.batchItem = batchItem
            self.logger.debug('========== log flush for batchId = ' + str(self.batch.id) +
                              ' batchItem index = ' + str(index))
            Utils.loggerFlush(self.logger)  # flush logger
            self.processBatchItem()
            self.logger.debug('========== log flush for batchId = ' + str(self.batch.id))
            Utils.loggerFlush(self.logger)  # flush logger
            self.fillChainUrlMD5List(self.batchItem)
            # Currently we update URL.ErrorMask for each url in batch
            self.updateUrlObjInBatchItem(batchItem.urlObj)

            if self.processorName != PCONSTS.PROCESSOR_RSS and not self.batchItem:
              self.logger.debug('!!! Before self.updateBatchItem(self.batchItem)')
              # self.updateBatchItem(batchItem)
              self.updateBatchItem(self.batchItem)
              input_batch.errorMask |= self.errorMask
            elif self.processorName != PCONSTS.PROCESSOR_RSS:
              self.logger.debug('!!! Before self.updateBatchItem(batchItem)')
              # self.updateBatchItem(self.batchItem)
              # batch_items.append(self.batchItem)
              self.updateBatchItem(batchItem)
              batch_items.append(batchItem)

            # Extend self.store_items with new batch items if iterations >1 and not last iteration
            if maxBatchIterations > 1 and self.curBatchIterations <= maxBatchIterations:
              self.batchItemsExtendUnique(self.store_items, self.collectURLsItems)
            beforeItems += len(self.collectURLsItems)

        # self.logger.debug("!!! self.collectURLsItems: " + varDump(self.collectURLsItems))
        # Exit the batch cycling if no one new item added or max iterations reached
        if self.curBatchIterations > maxBatchIterations or beforeItems == 0:
          self.logger.debug("Exit from batching iteration:" + \
                            "self.curBatchIterations=%s, maxBatchIterations=%s, beforeItems=%s, self.store_items=%s",
                            str(self.curBatchIterations), str(maxBatchIterations), str(beforeItems),
                            str(len(self.store_items)))
          break
        else:
          self.batch.items = self.store_items
          # self.logger.debug("Next batching iteration %s\n%s", str(self.curBatchIterations), varDump(self.store_items))
          self.logger.debug("Next batching iteration %s, len(self.store_items): %s", str(self.curBatchIterations),
                            str(len(self.store_items)))

      if input_batch.crawlerType == dc_event.Batch.TYPE_REAL_TIME_CRAWLER:
        process_task_batch = input_batch
        process_task_batch.items = self.store_items
      else:
        process_task_batch = Batch(input_batch.id, batch_items)
        process_task_batch.errorMask |= self.errorMask
      self.saveChainStorageData()
      if self.processorName == PCONSTS.PROCESSOR_RSS and len(process_task_batch.items) == 0 and \
        self.batchItem is not None:
        self.logger.debug("RSS empty!")
        if self.batchItem.urlObj is not None:
          self.batchItem.urlObj.errorMask |= APP_CONSTS.ERROR_RSS_EMPTY
        process_task_batch.items.append(self.batchItem)

      # self.logger.debug("output_batch:\n" + varDump(process_task_batch))
      self.logger.info("Out batch id: %s, items: %s", str(process_task_batch.id), str(len(process_task_batch.items)))
      output_pickled_object = pickle.dumps(process_task_batch)
      Utils.storePickleOnDisk(output_pickled_object, ENV_CRAWLER_STORE_PATH, "crawler.out." + str(self.batch.id))
      sys.stdout.write(output_pickled_object)
      sys.stdout.flush()
    except Exception, err:
      ExceptionLog.handler(self.logger, err, 'Batch processing failed!', (err))


  # #generateBatchitemsByURLSchema methon added new items into the batch.items list
  #
  # @param batch - incoming batch
  def generateBatchitemsByURLSchema(self, batch):

    additionBatchItems = []
    for batchItem in batch.items:
      self.batchItem = batchItem
      self.resetVars()
      self.loadSite(batch)
      self.readSiteProperties()
      self.batchItem.siteProperties = copy.deepcopy(self.siteProperties)
      batchItem = self.changeBatchItemByUrlSchema(self.batchItem, batch.id)

      self.logger.debug("batchItem.urlObj.url: " + str(batchItem.urlObj.url))

      self.logger.debug('>>> len(additionBatchItems) = ' + str(len(additionBatchItems)) + \
                        ' len(self.schemaBatchItems) = ' + str(len(self.schemaBatchItems)))

      for elem in self.schemaBatchItems:
        self.logger.debug("url: " + str(elem.urlObj.url))

      additionBatchItems += self.schemaBatchItems
    tmpBatchItems = []
    for elem in additionBatchItems:
      if elem.urlId not in [e.urlId for e in tmpBatchItems]:
        tmpBatchItems.append(elem)

    batch.items += tmpBatchItems

    self.logger.debug("len(batch.items) = " + str(len(batch.items)) + \
                      " len(tmpBatchItems) = " + str(len(tmpBatchItems)))

    # TODO maxItems, maxItems <= len(batch.items)
    if batch.maxItems is not None and int(batch.maxItems) < len(batch.items):
      batch.items = batch.items[0: self.batch.maxItems]
      batch.items[-1].urlObj.errorMask |= APP_CONSTS.ERROR_MAX_ITEMS


  # #changeBatchItemByUrlSchema generates new url bu urlSchema and replace batchItem.urlObject if url was change
  #
  # @param batchItem - incoming batchItem
  # @return batchItem with changed urlObj or untoched batchItem
  def changeBatchItemByUrlSchema(self, batchItem, batchId):
    # self.schemaBatchItems
    if "URLS_SCHEMA" in self.siteProperties:
      urlSchema = UrlSchema(self.siteProperties["URLS_SCHEMA"], batchItem.urlObj.siteId, self.urlSchemaDataDir)
      newUrls = urlSchema.generateUrlSchema(batchItem.urlObj.url)
      self.logger.debug("Generated new urls count = %s", str(len(newUrls)))

      # check limits
      if self.site.maxURLs > 0 and len(newUrls) >= self.site.maxURLs:
        newUrls = set(list(newUrls)[:self.site.maxURLs])
        self.logger.debug("Site maxURLs = %s limit reached.", str(self.site.maxURLs))

      if self.site.maxResources > 0 and len(newUrls) >= self.site.maxResources:
        newUrls = set(list(newUrls)[:self.site.maxResources])
        self.logger.debug("Site maxResources = %s limit reached.", str(self.site.maxResources))

      # url update
      if len(newUrls) > 0:
        self.logger.debug("Url was changed. From %s to %s", batchItem.urlObj.url, newUrls[0])

        if self.dbWrapper is not None:
          urlUpdateObj = dc_event.URLUpdate(siteId=batchItem.urlObj.siteId, urlString=batchItem.urlObj.url,
                                            normalizeMask=UrlNormalizator.NORM_NONE)
          urlUpdateObj.urlMd5 = batchItem.urlObj.urlMd5
          urlUpdateObj.batchId = batchId
          urlUpdateObj.crawled = SQLExpression("`Crawled`+1")
          urlUpdateObj.processed = 0
          urlUpdateObj.status = dc_event.URL.STATUS_CRAWLED
          urlUpdateObj.size = 0
          urlUpdateObj.contentType = ""
          result = self.dbWrapper.urlUpdate(urlUpdateObj)
          self.logger.debug("urlUpdate() return result: " + str(result))

        batchItem.urlObj.url = newUrls[0]
        batchItem.urlObj.parentMd5 = batchItem.urlObj.urlMd5
        if urlSchema.externalError != APP_CONSTS.ERROR_OK:
          batchItem.urlObj.errorMask |= urlSchema.externalError
        batchItem.urlId = batchItem.urlObj.urlMd5

        if self.dbWrapper is not None:
          result = self.dbWrapper.urlNew([batchItem.urlObj])
          self.logger.debug("urlNew() return result: " + str(result))

      if len(newUrls) > 1:
        for newUrl in newUrls[1:]:
          localBatchItem = copy.deepcopy(batchItem)
          localBatchItem.urlObj.batchId = 0
          localBatchItem.urlObj.status = dc_event.URL.STATUS_NEW
          localBatchItem.urlObj.url = newUrl
          localBatchItem.urlObj.urlMd5 = hashlib.md5(newUrl).hexdigest()
          localBatchItem.urlObj.parentMd5 = batchItem.urlObj.urlMd5
          localBatchItem.urlId = localBatchItem.urlObj.urlMd5
          localBatchItem.urlObj.CDate = str(datetime.datetime.now())
          localBatchItem.urlObj.errorMask = 0
          localBatchItem.urlObj.tagsCount = 0
          localBatchItem.urlObj.tagsMask = 0
          localBatchItem.urlObj.crawled = 0
          localBatchItem.urlObj.processed = 0
          localBatchItem.urlObj.size = 0
          localBatchItem.urlObj.contentType = ""
          localBatchItem.urlObj.rawContentMd5 = ""
          localBatchItem.urlObj.state = dc_event.URL.STATE_ENABLED

          if urlSchema.externalError != APP_CONSTS.ERROR_OK:
            localBatchItem.urlObj.errorMask |= urlSchema.externalError
          self.schemaBatchItems.append(localBatchItem)

        if self.dbWrapper is not None:
          # result = self.dbWrapper.urlNew([elem.urlObj for elem in self.schemaBatchItems])
          for elem in self.schemaBatchItems:
            result = self.dbWrapper.urlNew([elem.urlObj])
            self.logger.debug("urlNew() for urls list return result: " + str(result))
            if int(result) == 0:  # necessary update url
              urlUpdateObj = dc_event.URLUpdate(siteId=elem.urlObj.siteId, urlString=elem.urlObj.url,
                                                normalizeMask=UrlNormalizator.NORM_NONE)
              urlUpdateObj.urlMd5 = elem.urlObj.urlMd5
              urlUpdateObj.parentMd5 = batchItem.urlObj.urlMd5
              urlUpdateObj.batchId = 0  # #batchId
              urlUpdateObj.status = dc_event.URL.STATUS_NEW
              urlUpdateObj.UDate = SQLExpression("NOW()")
              urlUpdateObj.errorMask = 0
              urlUpdateObj.tagsCount = 0
              urlUpdateObj.tagsMask = 0
              urlUpdateObj.crawled = SQLExpression("`Crawled`+1")
              urlUpdateObj.processed = 0
              urlUpdateObj.size = 0
              urlUpdateObj.contentType = ""
              urlUpdateObj.rawContentMd5 = ""
              urlUpdateObj.state = dc_event.URL.STATE_ENABLED

              result = self.dbWrapper.urlUpdate(urlUpdateObj)
              self.logger.debug("urlUpdate() for urls list return result: " + str(result))

      # # Apply 'batch_insert' property
      if urlSchema.batchInsert == UrlSchema.BATCH_INSERT_ALL_NEW_ITEMS:
        self.logger.debug("UrlSchema use 'batch_insert' as 'BATCH_INSERT_ALL_NEW_ITEMS'")
      elif urlSchema.batchInsert == UrlSchema.BATCH_INSERT_ONLY_FIRST_ITEM:
        self.logger.debug("UrlSchema use 'batch_insert' as 'BATCH_INSERT_ONLY_FIRST_ITEM'")
        if len(self.schemaBatchItems) > 0:
          self.schemaBatchItems = self.schemaBatchItems[0:1]
      elif urlSchema.batchInsert == UrlSchema.BATCH_INSERT_NO_ONE_ITEMS:
        self.logger.debug("UrlSchema use 'batch_insert' as 'BATCH_INSERT_NO_ONE_ITEMS'")
        self.schemaBatchItems = []
      else:
        self.logger.error("UrlSchema use 'batch_insert' an unsupported value: " + str(urlSchema.batchInsert))

    return batchItem


  # #updateUrlObjInBatchItem update urlObj's fields in batchitem
  #
  # @param urlObj - reference to batchItem.urlObj
  # @param batchId - batch's id
  def updateUrlObjInBatchItem(self, urlObj):
    if urlObj is not None:
      urlObj.errorMask |= self.errorMask
      self.logger.debug("Set error_mask: %s", str(urlObj.errorMask))
      if self.crawledResource is not None:
        urlObj.httpCode = self.crawledResource.http_code
        self.logger.debug("Set HTTP Code: %s, contentType: %s", str(self.crawledResource.http_code),
                          str(self.crawledResource.content_type))
        if self.crawledResource.content_type is not None and \
        self.crawledResource.content_type != dc_event.URL.CONTENT_TYPE_UNDEFINED:
          urlObj.contentType = self.crawledResource.content_type


  # #updateBatchItem
  #
  def updateBatchItem(self, batchItem):
    # update batchItem properties
    # RSS feed items -> batch items
    if batchItem is not None:
      self.logger.debug("self.processorName: %s", varDump(self.processorName))

      if self.processorName == PCONSTS.PROCESSOR_FEED_PARSER:
        if self.feedItems is not None and len(self.feedItems) > 0:
          self.logger.debug("len(self.feedItems): %s", str(len(self.feedItems)))
          batchItem = self.createBatchItemsFromFeedItems(batchItem)
      elif self.url is not None:
        self.logger.debug("Before: batchItem urlObj errorMask: %s, url ErrorMask: %s" % (batchItem.urlObj.errorMask,
                                                                                         self.url.errorMask))
        batchItem.urlObj.errorMask |= self.url.errorMask
        batchItem.urlObj.errorMask |= self.errorMask
        self.logger.debug("After: batchItem urlObj errorMask: %s, url ErrorMask: %s" % (batchItem.urlObj.errorMask,
                                                                                        self.url.errorMask))
      if isinstance(batchItem, types.ListType):
        self.batchItemsExtendUnique(self.store_items, batchItem)
      else:
        self.batchItemsExtendUnique(self.store_items, [batchItem], False)
      if self.feedItems is not None:
        self.logger.debug("self.feedItems: %s, self.store_items: %s", str(len(self.feedItems)),
                          str(len(self.store_items)))
    else:
      self.logger.debug(">>> wrong !!! updateBatchItem, batchItem is None")


  # #createBatchItems
  #
  def createBatchItemsFromFeedItems(self, parentBatchItem):
    self.logger.debug("!!!  createBatchItemsFromFeedItems() enter ... self.crawledResource: " + \
                      varDump(self.crawledResource))
    items = []
    for elem in self.feedItems:
      if self.batch.maxItems > len(items):  # update only in case allowed high value of limits
        urlMd5 = elem["urlMd5"]
        self.logger.debug("URLMD5: %s" % str(urlMd5))
        self.logger.debug("value: %s" % str(elem))
        siteId = self.batchItem.siteId
        urlObj = elem["urlObj"]

        # serialize content
        elem.pop("urlObj", None)

        # list of objects must be converted to string before json dumps
        dates = ["published_parsed", "updated_parsed"]
        for date in dates:
          if date in elem["entry"] and elem["entry"][date] is not None:
            elem["entry"][date] = strftime("%a, %d %b %Y %H:%M:%S +0000", elem["entry"][date])
        elem["urlMd5"] = urlMd5
        elem["entry"] = dict(elem["entry"])
        # store raw content on disk
        saveBatchItemUrlId = self.batchItem.urlId
        try:
          self.crawledResource = CrawledResource()  # pylint: disable=W0201
          self.crawledResource.binary_content = json.dumps(elem)
          self.batchItem.urlId = urlMd5
          self.getDir()
          self.writeData()
          self.batchItem.urlId = saveBatchItemUrlId
        except Exception, err:
          ExceptionLog.handler(self.logger, err, "Can't save object on disk. Reason:", (), \
                               {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
          self.batchItem.urlId = saveBatchItemUrlId
          continue

        urlObj.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK
        if parentBatchItem is not None:
          batchItem = copy.deepcopy(parentBatchItem)
          batchItem.siteId = siteId
          batchItem.urlId = urlMd5
          batchItem.urlObj = urlObj
        else:
          batchItem = dc_event.BatchItem(siteId, urlMd5, urlObj)
        batchItem.urlObj.urlPut = None
        items.append(batchItem)

    return items


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


  # #loadKeyValueDB load key-value db
  #
  #
  def loadKeyValueDB(self):
    try:
      className = self.__class__.__name__
      self.kvDbDir = self.config.get(className, self.DB_DATA_DIR)
    except Exception, err:
      ExceptionLog.handler(self.logger, err, "Error load KVDB config option: %s", self.DB_DATA_DIR)
      raise


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      log_conf_file = self.config.get("Application", "log")
      logging.config.fileConfig(log_conf_file)
      self.logger = Utils.MPLogger().getLogger()
      self.loggerDefault = self.logger
    except:
      print MSG_ERROR_LOAD_LOG_CONFIG_FILE
      raise


  # #load project/site-specific logging
  # load logging configuration (log file, log level, filters) for project-specific file name
  #
  def setLogConfigFileProject(self, mpLogger, projectId, propertyStr):  # pylint: disable=W0622
    if propertyStr is not None and propertyStr != '':
      try:
        propertyObj = json.loads(propertyStr)
        if 'suffix' in propertyObj:
          suffix = propertyObj['suffix'].replace('%PROJECT_ID%', projectId)
          self.logger = mpLogger.getLogger(fileNameSuffix=suffix)
        else:
          self.logger.debug("Suffix field not found for project %s in property: %s", str(projectId), str(propertyObj))
      except Exception, err:
        self.logger.error("Error set project-specific logger: %s", str(err))
    else:
      self.logger.debug("Wrong or empty file name suffix, project %s logger not set: %s", str(projectId), \
                        str(propertyObj))


  # #set default logging
  #
  def setLogConfigFileDefault(self, mpLogger):
    # self.logger = self.loggerDefault
    try:
      self.logger = mpLogger.getLogger(restore=True)
    except Exception, err:
      self.logger.error("Error set default logger: %s", str(err))


  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    try:
      self.raw_data_dir = self.config.get(self.__class__.__name__, "raw_data_dir")
      self.defaultHeaderFile = self.config.get(self.__class__.__name__, "headers_file")
      self.defaultCookieFile = self.config.get(self.__class__.__name__, "cookie_file")
      self.defaultIcrCrawlTime = self.config.getfloat(self.__class__.__name__, "default_icr_crawl_time")
      self.headerFileDir = self.config.get(self.__class__.__name__, "header_file_dir")
      self.robotsFileDir = self.config.get(self.__class__.__name__, "robots_file_dir")
      dbTaskIni = self.config.get(self.__class__.__name__, "db-task_ini")
      self.urlSchemaDataDir = self.config.get(self.__class__.__name__, self.URL_SCHEMA_DIR)
      # Read urls xpath list from file as json and make loads
      self.urlsXpathList = \
      json.loads(open(self.config.get(self.__class__.__name__, self.URLS_XPATH_LIST_FILE), 'r').read())

      if self.config.has_option(self.__class__.__name__, "useZeroSiteIdSiteNotExists"):
        try:
          self.useZeroSiteIdSiteNotExists = \
          bool(int(self.config.get(self.__class__.__name__, "useZeroSiteIdSiteNotExists")))
        except Exception:
          self.useZeroSiteIdSiteNotExists = False
      # Add support operations updateCollectedURLs and removeURLs
#       cfgParser = ConfigParser.ConfigParser()
#       cfgParser.read(db_task_ini)
#       self.dbWrapper = DBTasksWrapper(cfgParser)
      self.dbWrapper = self.__createDBTasksWrapper(dbTaskIni)
      # does call collectAddtionalProp and collectProperties methods
      self.max_fetch_time = self.config.getint(self.__class__.__name__, "max_fetch_time")
      # keep old resources on disk
      if self.config.has_option(self.__class__.__name__, "keep_old_resources"):
        self.keep_old_resources = self.config.getboolean(self.__class__.__name__, "keep_old_resources")
      self.collect_additional_prop = self.config.getboolean(self.__class__.__name__, "collect_additional_prop")
      # self.urlProcess = URLProcess()
      #self.urlProcess.dbWrapper = None  ### self.dbWrapper  #####
      # self.resourceProcess = ResourceProcess()
      #self.resourceProcess.dbWrapper = None  ####self.dbWrapper  ####
    except Exception, err:
      ExceptionLog.handler(self.logger, err, "Error load config options:")
      raise Exception('CRAWLER FATAL INITIALIZATION INI ERROR: ' + str(err))


  # #checkResponse checkMaxHttpRedirects
  #
  def checkResponse(self):
    self.logger.debug("Requests response history: %s", str(self.res.redirects))
    # calculate http redirect
    if self.res.redirects and HTTP_REDIRECT in self.res.redirects:
      self.httpRedirects += 1
      self.logger.debug("http redirects: %s, http max redirects: %s", str(self.httpRedirects),
                        str(self.max_http_redirects))
    # check http redirect
    if self.max_http_redirects and self.max_http_redirects != MAX_HTTP_REDIRECTS_UNLIMITED and \
    self.httpRedirects >= self.max_http_redirects:
      self.allow_http_redirects = False
      self.logger.debug("http redirect limit was reached! Max http redirects: %s, encountered http redirects: %s." %
                        (str(self.max_http_redirects), str(self.httpRedirects)))
    else:
      self.allow_http_redirects = True  # pylint: disable=W0201


  # #calcLastModified
  #
  def calcLastModified(self, resource, res):
    if resource.http_code == CONSTS.HTTP_CODE_304:
      resource.last_modified = self.url.tcDate
    elif 'Last-Modified' in res.headers:
      resource.last_modified = res.headers['Last-Modified']
      resource.last_modified = parse(resource.last_modified).strftime('%Y-%m-%d %H:%M:%S')
    elif 'Date' in res.headers:
      resource.last_modified = res.headers['Date']
      resource.last_modified = parse(resource.last_modified).strftime('%Y-%m-%d %H:%M:%S')
    else:
      resource.last_modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() - self.defaultIcrCrawlTime))
    self.logger.debug("LastModified date: %s", str(resource.last_modified))

    return str(resource.last_modified)


  # #fillItemsFromIterations
  #
  # Optionally resets and fills the list of the BatchItems with the new instances initialized from the URLs objects list
  # @param urlObjects the list of the URL objects
  # @param siteObject the site object
  # @param reset the Boolean defines reset the items list before fill, True means reset
  def fillItemsFromIterations(self, urlObjects=None, siteObject=None, reset=True):
    if reset:
      self.collectURLsItems = []

    if urlObjects is not None:
      if siteObject is None:
        siteObjectLocal = self.batchItem.siteObj
        siteIdLocal = self.batchItem.siteId
      else:
        siteObjectLocal = siteObject
        siteIdLocal = siteObject.id

      for urlObject in urlObjects:
        self.logger.debug("Create new batch item, URLMd5: %s, siteId: %s", urlObject.urlMd5, siteIdLocal)
        batchItem = dc_event.BatchItem(siteId=siteIdLocal, urlId=urlObject.urlMd5, urlObj=urlObject,
                                       siteObj=siteObjectLocal)
        batchItem.properties = self.batchItem.properties
        self.collectURLsItems.append(batchItem)


  # #batchItemsExtendUnique
  #
  # Fills the batch items list with unique items from another list
  # @param destinationBatchItems the destination BatchItem objects list
  # @param destinationBatchItems the source BatchItem objects list
  def batchItemsExtendUnique(self, destinationBatchItems, sourceBatchItems, lookIncomingBatch=True, urlType=1):
    for srcBatchItem in sourceBatchItems:
      inList = False
      if lookIncomingBatch:
        for dstBatchItem in self.batch.items:
          if srcBatchItem.siteId == dstBatchItem.siteId and srcBatchItem.urlId == dstBatchItem.urlId:
            self.logger.debug("batchItemsExtendUnique baseItems duplicate " + srcBatchItem.urlId + " " +
                              dstBatchItem.urlId)
            inList = True
            break
      if not inList:
        for dstBatchItem in destinationBatchItems:
          if srcBatchItem.siteId == dstBatchItem.siteId and srcBatchItem.urlId == dstBatchItem.urlId:
            self.logger.debug("batchItemsExtendUnique duplicate " + srcBatchItem.urlId + " " + dstBatchItem.urlId)
            inList = True
            break
      if not inList:
        self.logger.debug("batchItemsExtendUnique added, urlId: %s", srcBatchItem.urlId)
        srcBatchItem.urlObj.type = urlType
        # check max allowed limits of resources
        if self.batch.maxItems is not None and int(self.batch.maxItems) <= len(destinationBatchItems):
          destinationBatchItems = destinationBatchItems[0: self.batch.maxItems]
          destinationBatchItems[-1].urlObj.errorMask |= APP_CONSTS.ERROR_MAX_ITEMS
          self.logger.debug("Set ErrorMask^ %s", str(destinationBatchItems[-1].urlObj.errorMask))
        else:
          destinationBatchItems.append(srcBatchItem)


  # #updateCollectedURLs
  #
  def updateCollectedURLs(self):
    self.dbWrapper.collectedURLsRecalculating(Utils.autoFillSiteId(self.batchItem.siteId, self.logger))


  # #setChainId
  #
  # @param batchItem incoming batch item
  def setChainId(self, batchItem):
    if batchItem.urlObj.chainId is None and "URL_CHAIN" in self.siteProperties and \
    self.siteProperties["URL_CHAIN"] is not None:
      batchItem.urlObj.chainId = self.chainIndex
      self.chainIndex += 1


  # #fillItemsFromIterationsWithChain
  #
  # @param urlObjects the list of the URL objects
  def fillItemsFromIterationsWithChain(self, urlObjects, batchItem):
    if urlObjects is not None and len(urlObjects) > 0:
      if batchItem.urlObj.chainId not in self.chainDict:
        self.chainDict[batchItem.urlObj.chainId] = {}
        self.chainDict[batchItem.urlObj.chainId]["batchItem"] = batchItem
        self.chainDict[batchItem.urlObj.chainId]["chainUrlMD5List"] = []
      for urlObj in urlObjects:
        urlObj.chainId = batchItem.urlObj.chainId
      self.fillItemsFromIterations(urlObjects, None, False)


  # #fillChainUrlMD5List
  #
  # @param batchItem incoming batch item
  def fillChainUrlMD5List(self, batchItem):
    if batchItem.urlObj.chainId is not None and batchItem.urlObj.chainId in self.chainDict:
      localChainElem = self.chainDict[batchItem.urlObj.chainId]
      if batchItem.urlObj.urlMd5 != localChainElem["batchItem"].urlObj.urlMd5 and \
      batchItem.urlObj.urlMd5 not in localChainElem["chainUrlMD5List"]:
        localChainElem["chainUrlMD5List"].append(batchItem.urlObj.urlMd5)


  # # Check available of host
  #
  # @param url - input url for check
  # @param parameters - input parameters dict
  # @param logger - logger instance
  # @param timeout - timeout value
  # @return boolean flag True if success, otherwise False
  @staticmethod
  def isHostAvailable(url, parameters, logger=None, timeout=0.5):
    ret = True
    if logger is not None:
      logger.debug('isHostAvailable  url: ' + str(url) + ', parameters: ' + str(parameters))
    try:
      if not isinstance(url, basestring) or url == "":
        raise Exception("Bad parameter 'url'")

      if 'method' in parameters and int(parameters['method']) == 0:
        # from urlparse import urlparse
        pr = urlparse.urlparse(url)
        # print str(pr)
        pr = pr.netloc.split(':')
        if len(pr) == 1:
          port = 80
        else:
          port = int(pr[1])
        host = pr[0]
        # print host, port
        if 'domain_name_resolve' in parameters and int(parameters['domain_name_resolve']) == 1:
          import socket
          ai = socket.getaddrinfo(host, port, 0, 0, socket.IPPROTO_TCP)
          # print ai
          if 'connect_resolve' in parameters and int(parameters['connect_resolve']) == 1:
            if 'connection_timeout' in parameters and float(parameters['connection_timeout']) > 0:
              timeout = float(parameters['connection_timeout'])
            for item in ai:
              af, socktype, proto, canonname, sa = item  # pylint: disable=W0612
              s = socket.socket(af, socktype, proto)
              s.settimeout(float(timeout))
              try:
                s.connect(sa)
              except Exception, err:
                ret = False
                # print str(sa), str(err)
                if logger is not None:
                  logger.debug("Host %s, timeout %f connect check error: %s", str(sa), str(timeout), str(err))
                  # logger.debug("Traceback: \n" + str(Utils.getTracebackInfo()))
                continue
              s.close()
              ret = True
              break

    except Exception, err:
      ret = False
      # print str(err)
      if logger is not None:
        logger.debug("Host %s availability check error: %s", str(url), str(err))
        # logger.debug("Traceback: \n" + str(Utils.getTracebackInfo()))

    return ret


  # #saveChainStorageData
  #
  def saveChainStorageData(self):
    urlPutList = []
    for localChainKay in self.chainDict:
      localChainElem = self.chainDict[localChainKay]
      saveBuf = '\n'.join(localChainElem["chainUrlMD5List"])
      saveBuf = saveBuf.strip()
      putDict = {"data": base64.b64encode(saveBuf)}
      urlPutObj = dc_event.URLPut(localChainElem["batchItem"].siteId, localChainElem["batchItem"].urlObj.urlMd5, \
                                  dc_event.Content.CONTENT_CHAIN_PARTS, putDict)
      urlPutList.append(urlPutObj)
      if len(urlPutList) > 0:
        self.dbWrapper.putURLContent([urlPutObj])

      self.urlProcess.siteId = localChainElem["batchItem"].siteId
      self.urlProcess.updateURLStatus(localChainElem["batchItem"].urlId)


  # #Get pubdate accord to 'PDATE_SOURCE_MASK'
  #
  # @param siteProperties - site properites instance
  # @param crawledResource - CrawledResource instance
  # @param urlObj - class URL instance
  # @return datetime as string in iso format
  def getPubdateUseSourceMask(self, siteProperties, crawledResource, urlObj):
    # variable to result
    ret = None
    try:
      if siteProperties is not None and crawledResource is not None:
        # default values
        pdateSourceMask = APP_CONSTS.PDATE_SOURCES_MASK_BIT_DEFAULT
        pdateSourceMaskOverwrite = APP_CONSTS.PDATE_SOURCES_MASK_OVERWRITE_DEFAULT

        # get value 'PDATE_SOURCES_MASK' from site properties
        if APP_CONSTS.PDATE_SOURCES_MASK_PROP_NAME in siteProperties:
          pdateSourceMask = int(siteProperties[APP_CONSTS.PDATE_SOURCES_MASK_PROP_NAME])

        # get value 'PDATE_SOURCES_MASK_OVERWRITE' from site properties
        if APP_CONSTS.PDATE_SOURCES_MASK_OVERWRITE_PROP_NAME in siteProperties:
          pdateSourceMaskOverwrite = int(siteProperties[APP_CONSTS.PDATE_SOURCES_MASK_OVERWRITE_PROP_NAME])

        self.logger.debug('pdateSourceMask = %s, pdateSourceMaskOverwrite = %s',
                          str(pdateSourceMask), str(pdateSourceMaskOverwrite))
        # self.logger.debug('crawledResource.response_header = ' + str(crawledResource.response_header))
        self.logger.debug('crawledResource.last_modified = ' + str(crawledResource.last_modified))

        # Extracted from URL name (not implemented)
        if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_URL_NAME:  # reserved
          if pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_URL_NAME:  # ON
            pass
          else:  # OFF
            pass

        # URL object the "pdate" field (supposed was got from the RSS feed)
        if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_RSS_FEED:
          if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_RSS_FEED and ret is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_RSS_FEED:
            try:
              dt = DateTimeType.parse(urlObj.pDate, True, self.logger, False)
              if dt is not None:
                ret = dt.strftime("%Y-%m-%d %H:%M:%S")
                self.addPubdateRssFeedToHeader(crawledResource, ret)
            except TypeError:
              self.logger.debug("Unsupported date format: <%s>", Utils.varDump(urlObj.pDate))

            self.logger.debug('pubdate from rss feed: ' + str(ret))


        # URL object "Date" field (supposed was got from the web server's HTTP response header)
        if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_HTTP_DATE and 'date' in crawledResource.response_header:
          if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_HTTP_DATE and ret is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_HTTP_DATE:
            value = self.extractValueFromHeader(crawledResource.response_header, 'date')
            dt = DateTimeType.parse(value, True, self.logger)
            if dt is not None:
              ret = dt.strftime('%Y-%m-%d %H:%M:%S')
              self.logger.debug('pubdate from http header: ' + str(ret))

        # URL object "lastModified" field (supposed was got from the web server's HTTP response header)
        if pdateSourceMask & APP_CONSTS.PDATE_SOURCES_MASK_HTTP_LAST_MODIFIED:
          if (pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_HTTP_LAST_MODIFIED and ret is None) or \
          not pdateSourceMaskOverwrite & APP_CONSTS.PDATE_SOURCES_MASK_HTTP_LAST_MODIFIED:
            d = None
            if 'last-modified' in crawledResource.response_header:
              value = self.extractValueFromHeader(crawledResource.response_header, 'last-modified')
              d = DateTimeType.parse(value, True, self.logger)
            else:
              d = DateTimeType.parse(crawledResource.last_modified, True, self.logger)

            if d is not None:
              ret = d.strftime('%Y-%m-%d %H:%M:%S')
              self.logger.debug('pubdate from last modified: ' + str(ret))

    except Exception, err:
      self.logger.error('Error: ' + str(err))

    return ret


  # #Extract field from response header string
  #
  # @param responseHeader - input response header as string
  # @param name - name for extracted
  # @return value as string extracted from response header
  def extractValueFromHeader(self, responseHeader, name):
    # variable for result
    ret = ''
    if isinstance(responseHeader, str) or isinstance(responseHeader, unicode):
      responseHeader = responseHeader.split('\r\n')

    # self.logger.debug('responseHeader: ' + str(responseHeader))
    for elem in responseHeader:
      begPos = elem.find(name)
      endPos = elem.find(':')
      if begPos > -1 and endPos > -1:
        foundName = elem[begPos:endPos].strip()
        self.logger.debug('foundName: %s', str(foundName))
        if foundName == name:
          ret = elem[endPos + 1:].strip()
          self.logger.debug("value extracted from field '%s': %s", name, str(ret))
          break

    return ret


  # # Add pubdate to rss feed crawler resource header
  # @param crawledResource - crawled resource
  # @param pubdateRssFeed - pubdate to rss feed
  def addPubdateRssFeedToHeader(self, crawledResource, pubdateRssFeed):
    if crawledResource is not None and pubdateRssFeed is not None:
      self.crawledResource.response_header = (crawledResource.response_header + '\r\n' +
                                              CONSTS.pubdateRssFeedHeaderName + ': ' + str(pubdateRssFeed + '+0000'))


  # # Add feed url to rss feed crawler resource header
  # @param crawledResource - crawled resource
  # @param feedUrl - feed url
  def addFeedUrlToHeader(self, crawledResource, feedUrl):
    if crawledResource is not None and feedUrl is not None:
      self.crawledResource.response_header = (crawledResource.response_header + '\r\n' +
                                              CONSTS.rssFeedUrlHeaderName + ': ' + str(feedUrl))


  # # Add base url to crawler resource header
  # @param crawledResource - crawled resource
  # @param feedUrl - feed url
  def addBaseUrlToHeader(self, crawledResource, baseUrl):
    if crawledResource is not None and baseUrl is not None:
      self.crawledResource.response_header = (crawledResource.response_header + '\r\n' +
                                              CONSTS.baseUrlHeaderName + ': ' + str(baseUrl))


  # # Extract base url
  #
  # @param htmlContent - batct item
  # @param default - default value of url
  # @return base url
  def extractBaseUrl(self, htmlContent, default):
    # variable for result
    ret = default

    try:
      if isinstance(htmlContent, basestring):
        urlsList = re.findall(pattern=self.SEARCH_BASE_URL_PATTERN, string=htmlContent, flags=re.M + re.I + re.U)
        if len(urlsList) > 0:
          ret = urlsList[0]

    except Exception, err:
      self.logger.error(MSG_ERROR_EXTRACT_BASE_URL, str(err))

    return ret


  # # Update headers by cached cookies
  #
  # @param headers - headers values dict
  # @param url - url string
  # @param stage - stage of apply cookies
  # @return updated headers object
  def updateHeadersByCookies(self, headers, url, stage):

#     self.logger.debug('!!! stage = %s, headers: %s', str(stage), str(headers))
    if headers is not None:
      headers = RequestsRedirectWrapper.updateHeadersByCookies(headers, url, self.cookieResolver, stage)

    return headers


  # # host alive property common handler
  #
  # @param propertyName - property name
  # @param siteProperties - site properties
  # @param url - input url for check
  # @param logger - logger instance
  @staticmethod
  def hostAliveHandler(propertyName, siteProperties, url, logger=None):
    # variable for result
    ret = True
    if propertyName in siteProperties:
      try:
        if logger is not None:
          logger.debug("Property '%s' found in site properties", str(propertyName))

        parameters = json.loads(siteProperties[propertyName])
        if logger is not None:
          logger.debug("Property '%s' successfully got from json", str(propertyName))

        ret = CrawlerTask.isHostAvailable(url, parameters, logger)
      except Exception, err:
        if logger is not None:
          logger.error("Try getting '%s' was fail: %s", str(propertyName), str(err))

    return ret


  # # check is available url or not
  #
  # @param siteProperties - site properties
  # @param url - input url for check
  # @param logger - logger instance
  # @return True - if available or False otherwise
  @staticmethod
  def isAvailableUrl(siteProperties, url, logger=None):
    return CrawlerTask.hostAliveHandler(propertyName=CrawlerTask.HOST_ALIVE_CHECK_NAME,
                                        siteProperties=siteProperties,
                                        url=url,
                                        logger=logger)


  # # check is available proxy or not
  #
  # @param siteProperties - site properties
  # @param proxyName - input proxy name for check
  # @param logger - logger instance
  # @return True - if available or False otherwise
  @staticmethod
  def isAvailableProxy(siteProperties, proxyName, logger=None):
    return CrawlerTask.hostAliveHandler(propertyName=CrawlerTask.HOST_ALIVE_CHECK_PROXY_NAME,
                                        siteProperties=siteProperties,
                                        url=CrawlerTask.DEFAULT_PROTOCOL_PREFIX + proxyName,
                                        logger=logger)


  # # Get proxy name
  #
  # @param siteProperties - sites property dict
  # @param siteId - site id
  # @param url - resource url for check allowed domain
  # @param dbWrapper - DBTaskWrapper instance
  # @param logger - logger instance
  # @return - proxy name as string or None and boolean flag is valid proxy
  @staticmethod
  def getProxyName(siteProperties, siteId, url, dbWrapper, logger):
    # variable for result
    proxyName = None
    isValid = True

    # create DBProxyWrapper instance if necessary
    dbProxyWrapper = None
    if HTTPProxyResolver.USER_PROXY_PROPERTY_NAME in siteProperties and dbWrapper is not None:
      dbProxyWrapper = DBProxyWrapper(dbWrapper)

    for triesCount in xrange(HTTPProxyResolver.getTriesCount(siteProperties)):
      proxyName = HTTPProxyResolver.getProxy(siteProperties=siteProperties,
                                             siteId=siteId,
                                             url=url,
                                             dbProxyWrapper=dbProxyWrapper)

      # Check host available parameters proxy
      if proxyName is not None and not CrawlerTask.isAvailableProxy(siteProperties=siteProperties,
                                                                    proxyName=proxyName,
                                                                    logger=logger):

        logger.debug("Tries count = %s. Proxy: '%s' is not available!!!", str(triesCount), str(proxyName))
        HTTPProxyResolver.addFaults(siteProperties=siteProperties,
                                    siteId=siteId,
                                    proxyName=proxyName,
                                    dbProxyWrapper=dbProxyWrapper)
        isValid = False
      else:
        logger.debug("Tries count = %s. Proxy: '%s' is available!!!", str(triesCount), str(proxyName))
        break

    return proxyName, isValid


  # # add proxy faults
  #
  # @param siteProperties - sites property dict
  # @param siteId - site ID value for request
  # @param proxyName - proxy host name
  # @param dbWrapper - DBTaskWrapper instance
  # @return - None
  @staticmethod
  def addProxyFaults(siteProperties, siteId, proxyName, dbWrapper):
    # create DBProxyWrapper instance if necessary
    dbProxyWrapper = None
    if HTTPProxyResolver.USER_PROXY_PROPERTY_NAME in siteProperties and dbWrapper is not None:
      dbProxyWrapper = DBProxyWrapper(dbWrapper)

    # add faults
    if proxyName is not None:
      HTTPProxyResolver.addFaults(siteProperties=siteProperties,
                                  siteId=siteId,
                                  proxyName=proxyName,
                                  dbProxyWrapper=dbProxyWrapper)


  # # check is necessary rotate proxy
  #
  # @param siteProperties - sites property dict
  # @param siteId - site ID value for request
  # @param proxyName - proxy host name
  # @param dbWrapper - DBTaskWrapper instance
  # @param rawContent - sites property dict
  # @return True if success or False - otherwise
  @staticmethod
  def isNeedRotateProxy(siteProperties, siteId, proxyName, dbWrapper, rawContent):
    # variable for result
    ret = False

    # create DBProxyWrapper instance if necessary
    dbProxyWrapper = None
    if HTTPProxyResolver.USER_PROXY_PROPERTY_NAME in siteProperties and dbWrapper is not None:
      dbProxyWrapper = DBProxyWrapper(dbWrapper)

    if proxyName is not None:
      ret = HTTPProxyResolver.isNeedRotateProxy(siteProperties=siteProperties,
                                                siteId=siteId,
                                                proxyName=proxyName,
                                                dbProxyWrapper=dbProxyWrapper,
                                                rawContent=rawContent)

    return ret


  # #Timer alarm signal handler
  #
  # @param signum
  # @param frame
  def signalHandlerTimer(self, signum, frame):
    del frame
    self.maxExecutionTimeReached = True
    self.logger.debug("Signal %s - timer trapped!", str(signum))


  # # Check is set flag max execution time reached
  #
  # @param - None
  # @return True if set or False otherwise
  def isAbortedByTTL(self):
    return self.maxExecutionTimeReached


  # # create dbtask wrapper instance
  #
  # @param configName - dbtask ini file
  # @return instance of DBTasksWrapper class
  def __createDBTasksWrapper(self, configName):
    # variable for result
    dbTasksWrapper = None
    try:
      if configName == "":
        raise Exception(MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(MSG_ERROR_WRONG_CONFIG_FILE_NAME % configName)

      dbTasksWrapper = DBTasksWrapper(config)

    except Exception, err:
      raise Exception(MSG_ERROR_LOAD_APP_CONFIG % str(err))

    return dbTasksWrapper
