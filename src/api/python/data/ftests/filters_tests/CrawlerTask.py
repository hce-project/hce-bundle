"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file CrawlerTask.py
@author Oleksii <developers.hce@gmail.com>
@author madk <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

# import os
import os.path
import sys
import time

import magic
# import pickle
try:
  import cPickle as pickle
except ImportError:
  import pickle

# import logging
import logging.config
import ConfigParser
import robotparser
import urlparse
import re
import requests
from dc_crawler.Fetcher import BaseFetcher
from dc_crawler import LangDetector
import json
import urllib
import hashlib
import datetime
from dateutil.parser import *
import lxml.html
import lxml.etree
import MySQLdb.cursors
import MySQLdb as mdb
import sqlite3
import tidylib
from contextlib import closing
from cement.core import foundation
from collections import namedtuple

from app.Utils import varDump
from dc.EventObjects import URL
from dc.EventObjects import Site
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dc.EventObjects import SiteFilter
from dc_crawler.CrawledResource import CrawledResource
from app.Utils import PathMaker
import app.Utils as Utils  # pylint: disable=F0401
from dc_crawler.CrawlerException import CrawlerException
import dc.Constants as DC_CONSTS
from dc import EventObjects
from dc_db.TasksManager import TasksManager as DBTasksManager
import dc_db.Constants  as Constants
from dc_crawler import Filters
import app.Consts as APP_CONSTS


MSG_ERROR_LOAD_CONFIG = "Error loading config file. Exciting. "
MSG_ERROR_LOAD_OPTIONS = "Error loading options. Exciting. "
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Can't load logging config file. Exiting. "
MSG_ERROR_LOAD_SITE_DATA = "Can't load site data: "
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
MSG_ERROR_CONTENT_TYPE = "Invalid content-type"

MSG_INFO_PROCESS_BATCH = "ProcessBatch "
MSG_INFO_STORE_COOKIES_FILE = "Store cookies file on disk."

MSG_DEBUG_NON_PROCESSING = "ProcessorName is NONE. Exclude batch item from further processing."


ERROR_BAD_URL = 0b1
ERROR_REQUEST_TIMEOUT = 0b10
ERROR_HTTP_ERROR = 0b100
ERROR_EMPTY_RESPONSE = 0b1000

ERROR_WRONG_MIME = 0b10000
ERROR_CONNECTION_ERROR = 0b100000
ERROR_PAGE_CONVERT_ERROR = 0b1000000
ERROR_BAD_REDIRECTION = 0b10000000

ERROR_RESPONSE_SIZE_ERROR = 0b100000000
ERROR_AUTH_ERROR = 0b1000000000
ERROR_WRITE_FILE_ERROR = 0b10000000000
ERROR_ROBOTS_NOT_ALLOW = 0b100000000000

ERROR_HTML_PARSE_ERROR = 0b1000000000000
ERROR_BAD_ENCODING = 0b10000000000000
ERROR_SITE_MAX_ERRORS = 0b100000000000000
ERROR_SITE_MAX_RESOURCES = 0b1000000000000000

ERROR_MIME_NOT_WRITE = 0b10000000000000000
ERROR_MAX_ALLOW_HTTP_REDIRECTS = 0b100000000000000000
ERROR_MAX_ALLOW_HTML_REDIRECTS = 0b1000000000000000000
ERROR_HTML_STRUCTURE = 0b10000000000000000000

ERROR_DTD_INVALID = 0b100000000000000000000
ERROR_CONTENT_TYPE = 0b1000000000000000000000

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

PATTERN_WITH_PROTOCOL = re.compile('[a-zA-Z]+:(//)?')

# URL_PATTERN = re.compile(r'https?://.*', re.I)
#BINARY_CONTENT_TYPE_PATTERN = re.compile('(image)|(application)', re.I)
BINARY_CONTENT_TYPE_PATTERN = re.compile('(text)|(xml)', re.I)
TEXT_CONTENT_TYPE_PATTERN = re.compile('text', re.I)

WITH_URL_XPATH_LIST = ["//a/@href", "//applet/@codebase", "//area/@href", "//base/@href", \
"//blockquote/@cite", "//body/@background", "//del/@cite", \
"//frame/@src", "//head/@profile", "//iframe/@src", "//img/@src", "//input/@src", "//ins/@cite", \
"//object/@codebase", "//q/@cite", "//audio/@src", \
"//button/@formaction", "//command/@icon", "//embed/@src", "//html/@manifest", \
"//input/@formaction", "//source/@src", "//video/@src", "//video/@poster", "//category/@domain",
"//link", "//guid"]

KV_TABLE_TEMPLATES = {
    "titles": ''' CREATE TABLE titles (
    url_id VARCHAR(32) NOT NULL PRIMARY KEY,
    data VARCHAR(100) NOT NULL DEFAULT '')''',

    "redirects": ''' CREATE TABLE redirects (
    url_id VARCHAR(32) NOT NULL PRIMARY KEY,
    data VARCHAR(1000000) NOT NULL DEFAULT '') ''',

   "internal_links": ''' CREATE TABLE internal_links (
    url_id VARCHAR(32) NOT NULL PRIMARY KEY,
    data VARCHAR(1000000) NOT NULL DEFAULT '') ''',

   "external_links": ''' CREATE TABLE external_links (
    url_id VARCHAR(32) NOT NULL PRIMARY KEY,
    data VARCHAR(1000000) NOT NULL DEFAULT '') '''
}

ENV_CRAWLER_STORE_PATH = "ENV_CRAWLER_STORE_PATH"
# SiteProperties = namedtuple("http_header", "http_cookie")
# CrawlResponse = namedtuple("html_content", "html_header", "html_request")
# named tuple for filters
#Filter = namedtuple("Filter", "pattern, pattern_name, type, state")

DETECT_MIME_MAIN_CONTENT = "1"
DETECT_MIME_COLLECTED_URL = "2"

#timeout(seconds) for mime type detecting
DETECT_MIME_TIMEOUT = 1



DETECT_MIME_MAIN_CONTENT = "1"
DETECT_MIME_COLLECTED_URL = "2"

#timeout(seconds) for mime type detecting
DETECT_MIME_TIMEOUT = 1

# #The CrawlerTask class, is a interface for fetching content from the web
#
# This object is a run at once application
class CrawlerTask(foundation.CementApp):


  URL_EXTRACT_PA = re.compile(r'[\'"](https?://[^\'" ]*)[\'"]')

  # Configuration settings options names
  DB_HOST = "db_host"
  DB_PORT = "db_port"
  DB_USER = "db_user"
  DB_PWD = "db_pwd"
  DB_SITES = "db_dc_sites"
  DB_URLS = "db_dc_urls"

  RAW_DATA_DIR = "raw_data_dir"
  SITE_TEMPLATES = "dc_site_template"
  KEY_VALUE_STORAGE_DIR = "key_value_storage_dir"
  DB_DATA_DIR = "db_data_dir"


  # Mandatory
  class Meta(object):
    label = APP_NAME
    def __init__(self):
      self.site_table_row = None


  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.dc_urls_db_connect = None
    self.need_store_mime = None
    self.site = None
    self.raw_data_dir = None
    self.robotparser = None
    self.batch_item = None
    self.dc_sites_db_connect = None
    self.site_table = None
    self.site_connector = None
    self.headers_dict = None
    self.store_http_headers = None
    self.cookie = None
    self.url_connector = None
    self.proxies = None
    self.logger = None
    self.url_table = None
    self.real_url = None
    self.url = None
    self.crawledResource = None
    self.batch = None
    self.headers = None
    self.table_name = None
    self.crawled_time = None
    self.store_http_request = None
    self.dir = None
    self.default_header_file = None
    self.default_cookie_file = None
    self.kvConnector = None
    self.kvCursor = None
    self.processorName = None
    self.site_properties = None
    self.siteId = None
    self.auto_remove_props = None
    self.store_cookies = None
    self.allow_http_redirects = True
    self.allow_html_redirects = None
    self.http_redirects = 0
    self.html_redirects = 0
    self.max_http_redirects = 1
    self.max_html_redirects = None
    self.dom = None
    self.time_postfix = None
    self.res = None
    self.post_forms = None
    self.auth_name = None
    self.auth_pwd = None
    self.kvDbDir = None
    self.default_icr_crawl_time = None
    self.db_task_ini = None


  # #setup
  # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)
    self.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file')


  # #run
  # run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # config section
    self.loadConfig()

    # load logger config file
    self.loadLogConfigFile()

    # load mandatory options
    self.loadOptions()

    # load db backend
    self.loadDBBackend()

    # load key-value db
    self.loadKeyValueDB()

  # #helper function for correct query execution
  #
  # @param query query for execution
  def executeQuery(self, connector, query):
    try:
      self.logger.info("executing query: %s", query)
      with closing(connector.cursor(MySQLdb.cursors.DictCursor)) as cursor:
        cursor.execute(query)
        connector.commit()
        return cursor.fetchall()
    except mdb.Error:  # @todo logging in db_task
      connector.rollback()
      raise


  # #helper function for correct update/insert/delete execution
  #
  # @param sql sql statement for execution
  def executeUpdate(self, connector, sql):
    try:
      self.logger.info("executing update: %s", sql)
      with closing(connector.cursor(MySQLdb.cursors.DictCursor)) as cursor:
        cursor.execute(sql)
        connector.commit()
        return cursor.rowcount
    except mdb.Error:  # @todo logging in db_task
      connector.rollback()
      raise


  # #helper function for execute batch update
  #
  # @param connector database connector
  # @param sql sql statement for execution
  # @param params argument sequence
  def executeMany(self, connector, sql, params):
    self.logger.warn("executing batch update, sql :%s, params:%s", sql, params)
    try:
      with closing(connector.cursor()) as cursor:
        cursor.executemany(sql, params)
        connector.commit()
        return cursor.rowcount
    except mdb.Error as err:  # @todo logging in db_task
      connector.rollback()
      self.logger.error("%s %s" % (err.args[0], err.args[1]))
      raise


  # #
  #
  # @param
  def addBatchItem(self, url):
    try:
      siteId = self.batch_item.siteId
      urlId = str(hashlib.md5(url).hexdigest())
      self.batch.append(BatchItem(siteId, urlId, None))
    except Exception as err:
      self.logger.error(MSG_ERROR_ADD_URL_TO_BATCH_ITEM + err.message)
      raise


  # #parseHost parse the root host name from url
  # for example: the result of http://s1.y1.example.com/path/to is example.com
  # @param url the full url
  # @return host of the url, eg: example.com
  @staticmethod
  def parseHost(url):
    host = None
    if urlparse.urlparse(url).hostname:
      host = '.'.join(urlparse.urlparse(url).hostname.split('.')[-2:])
    return host


  # #collectURLs collect URL from response body
  #
  # @return is collect successfully
  def collectURLs(self):
    #if BINARY_CONTENT_TYPE_PATTERN.match(self.crawledResource.content_type):
    if not BINARY_CONTENT_TYPE_PATTERN.search(self.crawledResource.content_type):
      self.logger.debug("Binary content: <<%s>>", self.crawledResource.content_type)
      return False

    # don't parse url for 4XX or 5XX response
    code_type = int(self.crawledResource.http_code) / 100
    if code_type == 4 or code_type == 5:
      return False
    if not self.crawledResource.html_content:
      return False
    internal_links, external_links = [], []
    host = CrawlerTask.parseHost(self.real_url)
    query = "SELECT `Type`, `Pattern`,`Stage`,`Subject`,`Action` FROM `sites_filters` WHERE `Site_Id` = '%s' AND `Mode`=0 AND `State`=%s" % (self.siteId, SiteFilter.TYPE_ENABLED)
    results = self.executeQuery(self.site_connector, query)
    self.filters = Filters.Filters(results, self.url)
    self.filters.updateFetchResult(self.res, self.dom)
    if self.dom is None:
      return False
    # use set for avoid duplicate urls
    url_set = set()
    for xpath in WITH_URL_XPATH_LIST:
      # self.logger.debug("xpath: %s", str(xpath))
      elem = self.dom.xpath(xpath)
      elem_type = type(elem)
      # self.logger.debug("elem_type: %s", str(elem_type))
      # self.logger.debug("elem: %s", str(elem))
      # self.logger.debug("len(elem): %s", str(len(elem)))
      # if elem_type == list and len(elem) > 0:
        # self.logger.debug("elem[0]: %s", str(elem[0]))
      if elem_type == list and len(elem) > 0 and hasattr(elem[0], "tail"):
        url_set.update([el.tail for el in elem])
      elif elem_type == list and len(elem) > 0 and isinstance(elem[0], lxml.html.HtmlElement):
        url_set.update([el.text for el in elem])
      else:
        url_set.update(elem)
    self.logger.debug("url_set: %s", str(url_set))
    form_urls, form_methods, form_fields = self.extractFormURL(self.dom)
    url_set.update(form_urls)

    # Updated by Oleksii
    # support maxURLsFromPage
    num_urls_from_page = 0

    if self.site.maxURLs:
      # Updated by Oleksii
      # omit fake urls inserted from foreign host
      # countsql = "SELECT COUNT(*) AS cnt FROM %s" % (self.url_table,)
      countsql = "SELECT COUNT(*) AS cnt FROM %s WHERE NOT (Status=4 AND Crawled=0 AND Processed=0)" % (self.url_table,)
      row = self.executeQuery(self.url_connector, countsql)
      current_cnt = row[0]['cnt']
    # use executeMany to improve performance
    params = []
    self.logger.debug("URL_SET: %s", str(url_set))
    for url in url_set:
      if self.url["Type"] == URL.TYPE_SINGLE or not url: continue
      # url contains protocol, but protocol is not http/https(such as javascript,mailto),
      # just ignore it
      self.logger.debug("URL: %s", url)
      if PATTERN_WITH_PROTOCOL.match(url) and \
       not url.lower().startswith("http://") and not url.lower().startswith("https://"):
        continue
      if not url.lower().startswith("http://") and not url.lower().startswith("https://"):
        url = urlparse.urljoin(self.real_url, url)
        # normalization
        # self.logger.debug("NORMALIZATION: init url: %s", url)
        url = URL(0, url).getURL()
        # self.logger.debug("NORMALIZATION: norm url: %s", url)
        internal_links.append(url)
        self.logger.info("internal")
      else:
        # normalization
        # self.logger.debug("NORMALIZATION: init url: %s", url)
        url = URL(0, url).getURL()
        # self.logger.debug("NORMALIZATION: norm url: %s", url)
        if CrawlerTask.parseHost(url) == host:
          internal_links.append(url)
          self.logger.info("internal")
        elif CrawlerTask.parseHost(url):
          external_links.append(url)
          self.logger.info("external")
        else:  # not valid url like http://
          continue

      flag = False
      if self.filters.filterAll(stage = Filters.STAGE_PROCESSING, value = url) < 0:
        flag = True
        
      # if isinstance(filters, list) and len(filters):
      #   # filter by Pattern
      #   for filter in filters:
      #     match = filter.pattern.match(url)
      #     if filter.type == SiteFilter.TYPE_EXCLUDE and match:
      #       self.logger.debug("Exclude url: %s", url)
      #       flag = True
      #       break
      #       # continue
      #     if filter.type == SiteFilter.TYPE_INCLUDE and not match and not filter.date:
      #       self.logger.debug("Exclude url: %s", url)
      #       flag = True
      #       break
      #       # continue
      #     if filter.date:
      #       self.logger.debug("Filter has date rule.")
      #       r1 = re.compile(".*[2][0-9]{3}")
      #       r2 = re.compile("(.*)/\d{6}/")
      #       if r1.match(url) or r2.match(url):
      #         self.logger.debug("url has date pattern")
      #         match = filter.pattern.match(url)
      #         if not match:
      #           self.logger.debug("Exclude by date url: %s", url)
      #           flag = True
      #           break
      if flag: continue
      url_md5 = hashlib.md5(url).hexdigest()
      query = "SELECT COUNT(*) AS cnt, (DATE_ADD(UDate, INTERVAL %s MINUTE)-NOW()) AS td FROM %s WHERE \
      `URLMd5` = '%s'" % (str(self.site.recrawlPeriod), self.url_table, url_md5)
      result = self.executeQuery(self.url_connector, query)
      if result[0]['cnt'] > 0:
        if self.site.recrawlPeriod == 0 or result[0]['td'] > 0:
          # ignore if already exists
          self.logger.debug("URL skipped, exists and re-crawling not active or time not reached\n %s %s", url, url_md5)
          continue
        else:
          query = "UPDATE %s SET `TcDate`=NOW(), `UDate`=NOW(), `Status`=1 WHERE `URLMd5` = '%s' AND `State`=0"\
                  % (self.url_table, url_md5)
          result = self.executeQuery(self.url_connector, query)
          # TODO: analize the UPDATE query results
          self.logger.debug("URL state updated to NEW because re-crawling\n %s %s", url, url_md5)
          continue
      else:
        self.logger.debug("URL passed check and treated as new\n %s %s", url, url_md5)

      # MaxURLs limit
      if self.site.maxURLs:
        if self.site.maxURLs and current_cnt < self.site.maxURLs:
          self.logger.debug("Site MaxURLs limit need to be checked.")
          current_cnt += 1
        else:
          if self.autoRemoveURL() == 0:
            # should not use break, because need add to internal/external links although reach the MaxURL limit
            continue

      # Updated by Oleksii
      # support maxURLsFromPage
      if  self.site_table_row["MaxURLsFromPage"] and num_urls_from_page >= self.site_table_row["MaxURLsFromPage"]:
        self.logger.debug("Site maxURLsFromPage limit reached! Site.MaxURLsFromPage: %s, current_page_num: %s", 
                          self.site_table_row["MaxURLsFromPage"], num_urls_from_page)
        continue

      #detect collected url mime type and ignore non-match URL
      detected_mime = ''
      if self.auto_detect_mime == DETECT_MIME_COLLECTED_URL:
        detected_mime = self.detectUrlMime(url)
        if detected_mime not in self.process_content_types:
          continue
      num_urls_from_page += 1

      #Calculate the depth
      query = "SELECT Depth FROM %s WHERE `URLMd5` = '%s'" % (self.url_table, self.batch_item.urlId)
      result = self.executeQuery(self.url_connector, query)
      if len(result) > 0 and "Depth" in result[0]:
        depth = result[0]['Depth']
      else:
        depth = 0

      params.append((self.batch_item.siteId, mdb.escape_string(url), self.url['Type'],
        url_md5, self.url['RequestDelay'], self.url['HTTPTimeout'],

        form_methods.get(url, "get"), self.batch_item.urlId, self.site_table_row["MaxURLsFromPage"], (depth + 1), detected_mime))
    if params:
      query = "INSERT IGNORE INTO `" + self.url_table + \
      "` (`Site_Id`, `URL`, `Type`, `URLMd5`, `RequestDelay`, `HTTPTimeout`, `HTTPMethod`, \
      `ParentMd5`, `MaxURLsFromPage`, `TcDate`, `UDate`, `Depth`, `ContentType`) \
       VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)"
      rows_count = self.executeMany(self.url_connector, query, params)
      self.logger.debug("rows_count: %s", rows_count)

    if form_fields:
      field_params = []
      for field_name, field_value in form_fields.iteritems():
        if field_name in self.post_forms:
          continue
        self.logger.debug("field_name: %s", field_name)
        self.logger.debug("field_value: %s", field_value)
        field_params.append((self.batch_item.siteId, "HTTP_POST_FORM_" + field_name, field_value))
        # field_params.append((self.batch_item.siteId, "HTTP_POST_FORM_" + field_name, field_value.decode("string_escape")))
      query = "INSERT INTO `" + DC_SITES_PROPERTIES_TABLE_NAME + "` (`Site_Id`, `Name`, `Value`) VALUES(%s, %s, %s)"
      self.executeMany(self.site_connector, query, field_params)

    try:
      self.collectProperties(self.dom, internal_links, external_links)
    except Exception:
      self.logger.warn("collect base properties to key-value db failed", exc_info=True)

    try:
      self.collectAddtionalProp(len(internal_links), len(external_links))
    except Exception:
      self.logger.warn("collect addtional propeties to main db failed", exc_info=True)
    return True

  # # detect mime type for an URL using HEAD method
  #
  # @param url the target URL
  # @return mime_type detected mime type, empty string if failed
  def detectUrlMime(self, url):
    try:
      res = requests.head(url, timeout=DETECT_MIME_TIMEOUT)
      return res.headers.get('content-type', '').lower()
    except BaseException:
      self.logger.warn("detect mime type for %s failed", url, exc_info=True)
      return ''


  # # detect mime type for an URL using HEAD method
  #
  # @param url the target URL
  # @return mime_type detected mime type, empty string if failed
  def detectUrlMime(self, url):
    try:
      res = requests.head(url, timeout = DETECT_MIME_TIMEOUT)
      return res.headers.get('content-type', '').lower()
    except BaseException:
      self.logger.warn("detect mime type for %s failed", url, exc_info = True)
      return ''
        

  # # detect mime type for an URL using HEAD method
  # 
  # @param url the target URL
  # @return mime_type detected mime type, empty string if failed
  def detectUrlMime(self, url):
    try:
      res = requests.head(url, timeout = DETECT_MIME_TIMEOUT)
      return res.headers.get('content-type', '').lower()
    except BaseException:
      self.logger.warn("detect mime type for %s failed", url, exc_info = True)
      return ''


  # #collectAddtionalProp collect addtional properties to main MySQL db
  #
  # @param internal_links_num the count of internal link list
  # @param external_links_num the count of external link list
  def collectAddtionalProp(self, internal_links_num, external_links_num):
    self.logger.debug("Response: %s", str(self.res))
    size = len(self.res.str_content)
    content_md5 = hashlib.md5(self.res.str_content).hexdigest()
    kv_sql = "SELECT data FROM internal_links WHERE url_id <> '%s'" % \
    (self.batch_item.urlId,)
    self.kvCursor.execute(kv_sql)
    freq = 0
    for row in self.kvCursor.fetchall():
      url_internal_lists = row["data"]
      if self.real_url in url_internal_lists:
        freq += 1
    sql = '''UPDATE `%s` SET `TcDate`=NOW(), `Size` = %s, `LinksI` = %s, `LinksE` = %s,
      `Freq` = %s, `RawContentMd5` = '%s' WHERE  `URLMd5` = '%s' ''' % \
      (self.url_table, size, internal_links_num, external_links_num, \
      freq, content_md5, self.batch_item.urlId)
    self.executeUpdate(self.url_connector, sql)


  # # extrace URL, form action, and fields from html dom
  #
  # @param dom the dom tree
  # @return form_urls    sequence of urls extracted
  # @return form_methods  dict of form methods, {form_action: form_method}
  # @return form_fields  dict of fields {field_name: field_value}
  def extractFormURL(self, dom):
    form_urls, form_methods, form_fields = [], {}, {}
    for form in dom.xpath("//form"):
      form_action = None
      form_method = 'get'
      for attr in form.keys():
        if attr.lower() == "action":
          form_action = form.get(attr)
          form_urls.append(form_action)
        elif attr.lower() == "method":
          form_method = form.get(attr)
      if not form_action:
        continue
      form_methods[form_action] = form_method
      for field in form.getchildren():
        tag_name, tag_value = None, ""
        for field_tag in field.keys():
          if field_tag.lower() == "name":
            tag_name = field.get(field_tag)
          elif field_tag.lower() == "value":
            tag_value = field.get(field_tag)
        if tag_name:
          form_fields[tag_name] = tag_value
    self.logger.info("extracted form data, form_urls:%s, \
      form_methods:%s, form_fields:%s", \
     form_urls, form_methods, form_fields)
    return form_urls, form_methods, form_fields


  # # checkKVTable check weather the sqlite table exists
  # if not, then create it
  #
  def checkKVTable(self):
    for table in ("titles", "redirects", "internal_links", "external_links"):
      sql = "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table' AND name='%s'" \
      % table
      self.kvCursor.execute(sql)
      if self.kvCursor.fetchone()["cnt"] == 0:
        self.logger.info("kv table %s dose not exist, now create it", table)
        self.kvCursor.execute(KV_TABLE_TEMPLATES[table])
        self.kvConnector.commit()


  # #collectProperties collect page properties to Key-Value DB
  #
  # @param dom the dom tree of the page
  # @param internal_links internal link list
  # @param external_links external link list
  def collectProperties(self, dom, internal_links, external_links):
    self.logger.info("start collect properties")
    self.prepareKvDbConnector()
    self.checkKVTable()
    title = None
    dom_title = None
    tmp = dom.find(".//title")
    if tmp:
      dom_title = tmp.text
    if isinstance(dom_title, lxml.etree._Element):
      title = dom_title.text
    if isinstance(title, str):
      title = title.decode('utf-8')

    histories = []
    for history in self.res.redirects:
      text_headers = '\r\n'.join(['%s: %s' % (k, v) for k, v in history.headers.iteritems()])
      history_item = {"status_code": history.status_code, "headers": text_headers}
      histories.append(history_item)
    histories_data = json.dumps(histories)
    internal_links_data = json.dumps(internal_links)
    external_links_data = json.dumps(external_links)
    # save title
    self.kvCursor.execute('''INSERT OR REPLACE INTO titles(url_id, data) VALUES(?, ?)''', \
      (self.batch_item.urlId, title))

    # save redirects
    self.kvCursor.execute('''INSERT OR REPLACE INTO redirects(url_id, data) VALUES(?, ?)''', \
      (self.batch_item.urlId, histories_data))

    # save internal links
    self.kvCursor.execute('''INSERT OR REPLACE INTO internal_links(url_id, data) VALUES(?, ?)''', \
      (self.batch_item.urlId, internal_links_data))

    # save external links
    self.kvCursor.execute('''INSERT OR REPLACE INTO external_links(url_id, data) VALUES(?, ?)''', \
      (self.batch_item.urlId, external_links_data))

    self.kvConnector.commit()


  # #writeData  write the response body and headers to file
  #
  # @param
  def writeData(self):
    # check wether need store to disk
    if self.need_store_mime and self.need_store_mime != '*':
      if self.crawledResource.content_type.lower() not in self.need_store_mime:
        self.logger.info("do not store resource files to disk")
        return
        # self.logger.info("do not store resource files to disk")
        # self.updateURLForFailed(ERROR_MIME_NOT_WRITE)
        # raise CrawlerException("MIME Content-Type not allow store content to disk")

    self.logger.info("store resource files to disk")
    self.makeDir()
    # html content
    self.time_postfix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    base_path = os.path.join(self.dir, self.batch_item.urlId + "_" + self.time_postfix)

    # save raw file
    html_content_file_name = base_path + ".bin"
    with open(html_content_file_name, "wb") as f:
      if TEXT_CONTENT_TYPE_PATTERN.match(self.crawledResource.content_type):
        # save UTF-8 encoding text for text content types
        if self.crawledResource.dynamic_fetcher_type:
          raw_unicode_content = self.crawledResource.meta_content
        else:
          raw_unicode_content = self.crawledResource.html_content
        if raw_unicode_content:
          if isinstance(raw_unicode_content, unicode):
            f.write(raw_unicode_content.encode('utf-8'))
          else:
            f.write(raw_unicode_content)

          # save tidy recovered file
          if self.html_recover == "1":
            with open(base_path + ".tidy", "wb") as tidy_f:
              tidy_content, errors = tidylib.tidy_document(raw_unicode_content)
              tidy_f.write(tidy_content)
      else:
        # save origin binary data for non-text content types
        if self.crawledResource.binary_content:
          f.write(self.crawledResource.binary_content)

    #detect mime type
    detected_mime = None
    if self.auto_detect_mime == DETECT_MIME_MAIN_CONTENT:
      detected_mime = magic.from_file(html_content_file_name, mime=True)
      self.logger.info("detected mime type:%s", detected_mime)

    # save rendered file
    if self.crawledResource.dynamic_fetcher_type and self.crawledResource.html_content:
      rendered_file_name = base_path + "." + self.crawledResource.dynamic_fetcher_type + ".dyn"
      with open(rendered_file_name, "wb") as f:
        f.write(self.crawledResource.html_content)

    # html header
    if self.store_http_headers:
      html_header_file_name = base_path + ".headers.txt"
      with open(html_header_file_name, "wb") as f:
        self.logger.warn("file is %s", html_header_file_name)
        if self.crawledResource.response_header:
          f.write(self.crawledResource.response_header)
    # html request
    if self.store_http_request:
      html_request_file_name = base_path + ".request.txt"
      with open(html_request_file_name, "wb") as f:
        f.write("GET %s HTTP/1.0\r\n\r\n" % (self.real_url,))
        if self.crawledResource.html_request:
          f.write(self.crawledResource.html_request)
    return detected_mime


  # #getDir prepare dir
  #
  # @param
  def getDir(self):
    if len(self.batch_item.siteId):
      self.dir = os.path.join(self.raw_data_dir, self.batch_item.siteId, \
         PathMaker(self.batch_item.urlId).getDir())
      # self.dir = self.raw_data_dir + "/" + self.batch_item.siteId + "/" + self.batch_item.urlId
    else:
      self.dir = os.path.join(self.raw_data_dir, "0", \
        PathMaker(self.batch_item.urlId).getDir())


  # #getDir prepare dir
  #
  # @param
  def makeDir(self):
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    elif not os.path.isdir(self.dir):
      self.updateURLForFailed(ERROR_WRITE_FILE_ERROR)
      raise Exception("path %s exists, but is not a directory" % (self.dir,))


  # #updateURLForFailed
  #
  # @param error_bit BitMask of error
  def updateURLForFailed(self, error_bit):
    query = "UPDATE `%s` \
      SET `Status` = %s, \
      `ErrorMask` = `ErrorMask` | %s, \
      `UDate` = NOW(), \
      `TcDate` = NOW() \
      WHERE `URLMd5` = '%s' AND `Status` = 3" \
      % (self.url_table, \
      URL.STATUS_CRAWLED, \
      error_bit, \
      self.batch_item.urlId)
    self.executeUpdate(self.url_connector, query)
    self.updateSite(error_bit)

  # #crawl site
  #
  # @return should continue to write data and collect URLs
  def crawl(self):
    self.crawledResource = None
    # delay
    time.sleep(self.url["RequestDelay"] / 1000.0)
    # response = Popen("scrapy fetch --nolog  " + self.url["URL"], stdout=PIPE, shell=True).communicate()[0]
    # remove the unquote call, since don't pass thr url to Popen
    # url = urllib.unquote(self.url["URL"]).decode('utf8')
    if self.url["URL"].startswith("http%3A") or self.url["URL"].startswith("https%3A"):
      url = urllib.unquote(self.url["URL"]).decode('utf-8')
    else:
      url = self.url["URL"].decode('utf8')
    self.real_url = url
    # self.parseRobotFile(url)
    # user_agent = self.headers_dict.get('User-Agent', '*')
    # if not self.robotparser.can_fetch(user_agent, url):
    #   self.logger.warn("not allowed in robots.txt")
    #   self.updateURLForFailed(ERROR_ROBOTS_NOT_ALLOW)
    #   return False
    self.logger.info("allowed in robots.txt")
    start_time = time.time()

    try:
      self.logger.info("start to fetch %s", url)
      if self.auth_name and self.auth_pwd:
        auth = (self.auth_name, self.auth_pwd)
        self.logger.info("using http basic auth %s:%s", self.auth_name, self.auth_pwd)
      else:
        auth = None
      try:
        method = self.url["HTTPMethod"].lower()
      except Exception:
        method = "get"
      post_data = None
      if method == "post":
        post_data = self.post_forms
        self.logger.info("use post, post_data:%s", post_data)
      else:
        if self.url["LastModified"]:
          self.logger.info("If-Modified-Since: <<%s>>", self.url["LastModified"])
          self.logger.info("If-Modified-Since type: <<%s>>", str(type(self.url["LastModified"])))
          self.headers_dict["If-Modified-Since"] = self.convertToHttpDateFmt(self.url["LastModified"])

      res = BaseFetcher.get_fetcher(self.site.fetchType).open(url,
        external_url=self.external_url,
        timeout=int(self.url["HTTPTimeout"]) / 1000.0,
        headers=self.headers_dict,
        allow_redirects=self.allow_http_redirects,
        proxies=self.proxies, auth=auth,
        data=post_data, logger=self.logger,
        max_redirects=self.max_http_redirects)

      self.logger.info("request headers:%s", self.headers_dict)
      if not res.headers:
        self.logger.debug("'content-type': 'application/pdf'. Not crawl.")
        self.logger.debug(MSG_ERROR_CONTENT_TYPE)
        self.updateURLForFailed(ERROR_CONTENT_TYPE)
        return False

      if "content-length" in res.headers and res.headers["content-length"] == EMPTY_RESPONSE_SIZE:
        self.logger.debug("content-length: %s", str(res.headers["content-length"]))
        self.logger.debug(MSG_ERROR_EMPTY_RESPONSE_SIZE)
        self.updateURLForFailed(ERROR_EMPTY_RESPONSE)
        return False

      # save res to self, will use it in next steps
      self.res = res
      self.logger.info("response code:%s", str(self.res.status_code))
      # use charset to improve encoding detect
      self.crawled_time = time.time()
      resource = CrawledResource()
      resource.meta_content = res.meta_res
      resource.crawling_time = int((self.crawled_time - start_time) * 1000)
      resource.bps = res.content_size / resource.crawling_time * 1000
      self.logger.warn("crawling_time: %s, bps: %s", resource.crawling_time, resource.bps)
      resource.http_code = res.status_code
      self.logger.warn("headers is :%s", res.headers)
      resource.content_type = res.headers.get('Content-Type', 'text/html').split(';')[0]
      if res.encoding:
        resource.charset = res.encoding
      else:
        resource.charset = ""
      resource.html_request = self.headers
      resource.response_header = '\r\n'.join(['%s: %s' % (k, v) for k, v in res.headers.iteritems()])
      resource.last_modified = self.calcLastModified(resource, res)
      resource.language = LangDetector.detect(res.unicode_content)[0]
      self.logger.debug("detected language is %s for url %s", resource.language, self.real_url)
      if resource.language is None:
        resource.language = self.url["LangMask"]
      self.logger.debug("request is: %s", resource.html_request)
      self.logger.debug("response is: %s", resource.response_header)

      # updated by Oleksii
      # save cookies from response
      resource.cookies = res.cookies
      resource.dynamic_fetcher_type = res.dynamic_fetcher_type
      self.crawledResource = resource

      if "content-type" in res.headers and (res.headers["content-type"] == "image/x-icon" or \
          res.headers["content-type"] == "application/pdf"):
        self.updateSite(0)
        return True
      # Added by Oleksii
      # Build DOM object
      parser = lxml.etree.HTMLParser(encoding='utf-8')
      if resource.http_code == 304 or resource.content_type.startswith("application"):
        self.dom = lxml.html.fromstring("<html></html>", parser=parser)
      else:
        self.dom = lxml.html.fromstring(res.rendered_unicode_content, parser=parser)
      # Added by Oleksii
      # support of HTTP_REDIRECTS_MAX
      self.checkResponse()
      if not self.allow_html_redirects:
        self.updateSite(ERROR_MAX_ALLOW_HTML_REDIRECTS)
        return False
      if not self.allow_http_redirects:
        self.updateSite(ERROR_MAX_ALLOW_HTTP_REDIRECTS)
        return False

      resource_size = res.content_size
      self.logger.debug("MaxResourceSize: %s, ResourceSize: %s " % (self.site.maxResourceSize, resource_size))
      if resource_size == 0 and resource.http_code / 100 != 3:
        resource.error_mask = ERROR_EMPTY_RESPONSE
        self.updateSite(ERROR_EMPTY_RESPONSE)
        return False
      elif self.site.maxResourceSize and resource_size > self.site.maxResourceSize:
        resource.error_mask = ERROR_RESPONSE_SIZE_ERROR
        self.updateSite(ERROR_RESPONSE_SIZE_ERROR)
        self.logger.debug("Site MaxResourceSize limit overshooted.")
        return False
      else:
        resource.html_content = res.rendered_unicode_content
        resource.binary_content = res.str_content
      if res.status_code / 100 == 4 or res.status_code / 100 == 5:
        resource.error_mask = ERROR_HTTP_ERROR
        self.updateSite(ERROR_HTTP_ERROR)
        return False
      self.addSiteSize(resource_size)
    except requests.exceptions.Timeout, err:
      self.updateURLForFailed(ERROR_REQUEST_TIMEOUT)
      # tbi = Utils.getTracebackInfo()
      # self.logger.error(str(type(err)) + "\n")
      # self.logger.error(str(err.message) + "\n" + tbi)
      # self.logger.debug("Can't crawl resource.")
      return False
    except requests.exceptions.InvalidURL:
      self.updateURLForFailed(ERROR_BAD_URL)
      return False
    except requests.exceptions.TooManyRedirects:
      self.updateURLForFailed(ERROR_BAD_REDIRECTION)
      return False
    except requests.exceptions.ChunkedEncodingError:
      self.updateURLForFailed(ERROR_PAGE_CONVERT_ERROR)
      return False
    except requests.exceptions.ConnectionError:
      self.updateURLForFailed(ERROR_CONNECTION_ERROR)
      return False
    except requests.exceptions.ContentDecodingError:
      self.updateURLForFailed(ERROR_PAGE_CONVERT_ERROR)
      return False
    except lxml.etree.XMLSyntaxError:
      self.logger.warning("XML HTML syntax error")
      self.updateURLForFailed(ERROR_DTD_INVALID)
      return False
    except Exception, err:
      self.updateURLForFailed(ERROR_HTML_STRUCTURE)
      tbi = Utils.getTracebackInfo()
      self.logger.error(str(vars(err)) + "\n" + tbi)
      self.logger.error(str(type(err)) + "\n")
      self.logger.error(str(err.message) + "\n" + tbi)
      self.logger.debug("Can't crawl resource." + err.message)
      return False
    self.updateSite(0)
    return True


  # # convert date str to HTTP header format
  # 2014-07-29 20:31:50 (GMT+8) to Tue, 29 Jul 2014 12:31:50 GMT
  # @param date_str date str, 2014-07-29 20:31:50
  # @return HTTP header formated date str : Tue, 29 Jul 2014 12:31:50 GMT
  def convertToHttpDateFmt(self, date_str):
    # stamp = time.mktime(date_str.timetuple())
    stamp = time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S'))
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(stamp))


  # addResource add Resources counter for sites table
  def addResource(self):
    # Increment site.Resources if it is first crawling, but not re-crawling
    if self.url["Crawled"] == 0:
      siteId = self.batch_item.siteId if self.batch_item.siteId else "0"
      sql = "UPDATE %s SET `TcDate`=NOW(), `Resources` = `Resources` + 1 WHERE `Id` = '%s'" % \
      (self.site_table, siteId)
      self.executeUpdate(self.site_connector, sql)


  # #parseRobotFile fetch the robot file for spefic url
  #
  # @param url the url to fetch(not the url of robots.txt)
  def parseRobotFile(self, url):
    robots_txt_url = ROBOTS_PATTERN.sub(r'\1/robots.txt', url)
    self.robotparser = robotparser.RobotFileParser(robots_txt_url)
    self.robotparser.read()


  # updateAVGSpeed update sites.AVGSpeed property
  def updateAVGSpeed(self):
    if self.res.status_code == 304:
      # not modified will return empty response body
      return
    newSpeed = (self.site.AVGSpeed * self.site.AVGSpeedCounter + self.crawledResource.bps) / \
               (self.site.AVGSpeedCounter + 1)
    query = "UPDATE `%s` SET \
    `TcDate`=NOW(), `AVGSpeed` = %s, `AVGSpeedCounter` = `AVGSpeedCounter` + 1 \
    WHERE `Id` = '%s'" % \
    (self.site_table, newSpeed, self.siteId)
    self.executeUpdate(self.site_connector, query)


  # saveCookies
  def saveCookies(self):
    self.logger.debug(MSG_INFO_STORE_COOKIES_FILE)
    self.logger.debug("Store cookies properties:\n%s", varDump(self.store_cookies))
    if self.store_cookies and self.store_cookies == "1":
      cookies_str = [key + ": " + value + "; " for (key, value) in self.crawledResource.cookies.items()]
      self.makeDir()
      self.time_postfix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
      self.logger.debug("Response cookies dict: %s", str(self.crawledResource.cookies))
      self.logger.debug("Response cookies string: %s", str(cookies_str))
      self.logger.debug("self.batch_item.urlId: %s", str(self.batch_item.urlId))
      self.logger.debug("self.time_postfix: %s", str(self.time_postfix))
      base_path = os.path.join(self.dir, self.batch_item.urlId + "_" + self.time_postfix)
      cookies_file_name = base_path + COOKIES_FILE_POSTFIX
      with open(cookies_file_name, "wb") as f:
        f.write(''.join(sorted(cookies_str)))


  # #updateCrwledURL
  #
  # @param site - site object
  def updateCrawledURL(self):
    state = URL.STATE_ENABLED
    # updated by Oleksii
    # don't set url's state to error
    # if self.crawledResource.error_mask:
    #  state = URL.STATE_ERROR
    # calc new MRate
    updated_count = self.url["MRate"] * self.url["MRateCounter"]
    if self.crawledResource.http_code != 304:
      updated_count += 1
    total_count = self.url["MRateCounter"] + 1
    mrate = updated_count / total_count
    query = "UPDATE `%s` SET \
      `Status`=%s, \
      `State`=%s, \
      `ContentType`='%s', \
      `Charset`='%s', \
      `ErrorMask`= `ErrorMask` | %s, \
      `CrawlingTime`= %s, \
      `TotalTime` = `TotalTime` + %s, \
      `UDate`=NOW(), \
      `HTTPCode`=%s, \
      `LastModified` = CONVERT_TZ('%s','+00:00',@@global.time_zone), \
      `TcDate` = NOW(), \
      `MRate` = %s, \
      `MRateCounter` = `MRateCounter` + 1, \
      `LangMask` = '%s' \
      WHERE `URLMd5`='%s' AND `Status` = 3" \
      % (self.url_table, \
      URL.STATUS_CRAWLED, \
      state, \
      self.crawledResource.content_type, \
      self.crawledResource.charset, \
      self.crawledResource.error_mask, \
      self.crawledResource.crawling_time, \
      self.crawledResource.crawling_time, \
      self.crawledResource.http_code, \
      self.crawledResource.last_modified, \
      mrate,
      self.crawledResource.language,
      self.batch_item.urlId)
    updated_rows = self.executeUpdate(self.url_connector, query)
    return updated_rows > 0


  # #updateURL
  #
  # @param site - site object
  def updateURL(self, status=URL.STATUS_CRAWLING):
    if not self.url['HTTPMethod']:
      query = "UPDATE `%s` \
        SET `Status`=%s, \
        `Crawled`=`Crawled`+1, \
        `Batch_Id`=%s, `TcDate`=NOW(), `UDate` = NOW(), \
        `HTTPMethod` = 'get' \
        WHERE `URLMd5`='%s'" \
        % (self.url_table, \
        URL.STATUS_CRAWLING, \
        self.batch.id, \
        self.batch_item.urlId)
    else:
      query = "UPDATE `%s` \
        SET `Status`=%s, \
        `Crawled`=`Crawled`+1, \
        `Batch_Id`=%s, `TcDate`=NOW(), `UDate` = NOW() \
        WHERE `URLMd5`='%s'" \
        % (self.url_table, \
        status, \
        self.batch.id, \
        self.batch_item.urlId)

    rows = self.executeUpdate(self.url_connector, query)
    return rows > 0


  # #addSiteSize update sites table to increase size
  #
  # @param size content size of this crawler
  def addSiteSize(self, size):
    query = "UPDATE %s SET `TcDate`=NOW(), `Size` = `Size` + %s WHERE `Id`='%s'"\
     % (self.site_table, size, self.siteId)
    self.logger.debug("query: " + query)
    self.executeUpdate(self.site_connector, query)


  # #prepare request headers and cookie
  #
  # @param site - site object
  def readSiteProperties(self):
    # TODO not sure is it right that fetch headers and cookie
    # by `Name` = 'headers'/'cookie'
    self.store_http_request = True
    self.store_http_headers = True
    query = "SELECT `Name`, `Value` FROM `%s` WHERE `Site_Id` = '%s'"\
      % (DC_SITES_PROPERTIES_TABLE_NAME, self.siteId)
    self.headers_dict = {}
    self.post_forms = {}
    self.headers, self.cookie = None, None
    self.proxies = None
    self.need_store_mime = '*'
    self.auth_name, self.auth_pwd = None, None
    self.external_url = None
    self.auto_remove_props = {}
    self.html_recover = None
    self.auto_detect_mime = None
    self.process_content_types = []

    try:
      rows = self.executeQuery(self.dc_sites_db_connect, query)
      self.site_properties = rows
      headers, cookie = None, None
      proxy_host, proxy_port = None, None
      for row in rows:
        name, value = row['Name'], row['Value']
        if name == 'HTTP_HEADERS':
          headers = value
        elif name == 'HTTP_COOKIE':
          cookie = value
        elif name == 'STORE_HTTP_REQUEST':
          self.store_http_request = (value != u'0' and value != '0' and value != 0)
        elif name == 'STORE_HTTP_HEADERS':
          self.store_http_headers = (value != u'0' and value != '0' and value != 0)
        elif name == 'HTTP_PROXY_HOST':
          proxy_host = value
        elif name == 'HTTP_PROXY_PORT':
          proxy_port = value
        elif name == 'MIME_TYPE_STORE_ON_DISK':
          allow_mimes = value
          if allow_mimes == '' or allow_mimes == '*':
            self.need_store_mime = '*'
          else:
            self.need_store_mime = set([mime.lower() for mime in allow_mimes.split(',')])
        elif name == 'HTTP_AUTH_NAME':
          self.auth_name = value
        elif name == 'HTTP_AUTH_PWD':
          self.auth_pwd = value
        elif name.startswith("HTTP_POST_FORM_"):
          self.post_forms[name[15:]] = value
        elif name == 'EXTERNAL_FETCHER_URL':
          self.external_url = value
        elif name == 'HTML_RECOVER':
          self.html_recover = value
        elif name == 'MITE_TYPE_AUTO_DETECT':
          self.auto_detect_mime = value
        elif name == 'PROCESS_CTYPES':
          self.process_content_types = value.lower().split(',')
        # Added by Oleksii
        # support of PROCESSOR_NAME
        elif row.has_key("Name") and row["Name"] == "PROCESSOR_NAME":
          self.processorName = row["Value"]
          self.logger.debug("PROCESSOR_NAME: " + str(self.processorName))
        elif name == DC_CONSTS.SITE_PROP_SAVE_COOKIES:
          self.store_cookies = value
        elif name == DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES:
          self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES] = value
        elif name == DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER:
          self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER] = value
        elif name == DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE:
          self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE] = value
        # Added by Oleksii
        # support HTTP_REDIRECTS_MAX
        elif row.has_key("Name") and row["Name"] == "HTTP_REDIRECTS_MAX":
          self.max_http_redirects = int(row["Value"])
          self.logger.debug("HTTP_REDIRECTS_MAX: " + str(self.max_http_redirects))
        # Added by Oleksii
        # support HTML_REDIRECTS_MAX
        elif row.has_key("Name") and row["Name"] == "HTML_REDIRECTS_MAX":
          self.max_html_redirects = int(row["Value"])
          self.logger.debug("HTML_REDIRECTS_MAX: " + str(self.max_html_redirects))

      if headers is None:
        # read request headers from crawler-task_headers.txt file
        headers = CrawlerTask.readSmallFileContent(self.default_header_file)
      if cookie is None:
        # read request cookies from crawler-task_headers.txt file
        cookie = CrawlerTask.readSmallFileContent(self.default_cookie_file)
      self.headers = headers
      if cookie and cookie.lower().startswith('cookie:'):
        self.cookie = cookie[7:]
      else:
        self.cookie = cookie

      for header in headers.splitlines():
        if not header:
          continue
        try:
          key, value = header[:header.index(':')].strip(), header[header.index(':') + 1:].strip()
        except Exception:
          self.logger.warn("header:%s", header)
        self.headers_dict[key] = value
      if self.cookie:
        self.headers_dict['Cookie'] = self.cookie

      if proxy_host and proxy_port:
        self.proxies = {'http' : 'http://%s:%s' % (proxy_host, proxy_port)}
      self.logger.info("proxies: %s", self.proxies)
    except Exception:
      self.logger.error(MSG_ERROR_LOAD_SITE_PROPERTIES, exc_info=True)


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
  def updateSite(self, mask, is_suspend=False):
    response = False
    try:
      if mask:
        if is_suspend:
          query = "UPDATE %s \
            SET `TcDate` = NOW(), \
            `Errors` = `Errors` + 1, \
            `ErrorMask` = `ErrorMask` | %s, \
            State = %s \
            WHERE Id = '%s'" \
            % (self.site_table, \
            mask, \
            Site.STATE_SUSPENDED, \
            self.siteId)
        else:
          query = "UPDATE %s SET `TcDate` = NOW(), `Errors` = `Errors` + 1, \
          `ErrorMask` = `ErrorMask` | %s \
          WHERE Id = '%s'" \
          % (self.site_table, mask, self.siteId)
      else:
        query = "UPDATE %s \
          SET `TcDate` = NOW() WHERE Id = '%s'" % (self.site_table, self.siteId)
      self.logger.debug("query: %s", query)
      updated_site = self.executeUpdate(self.site_connector, query)
      if updated_site:
        response = True
    except Exception as err:
      self.logger.error(MSG_ERROR_LOAD_SITE_DATA + err.message)
      raise
    return response


  # #check site params
  # check site params
  #
  # @return should continue execute this BatchItem
  def checkSite(self):
    # TODO: self.site and self.url not must be none
    if not self.site or not self.url: return False
    self.logger.debug("url:" + str(self.url))
    if self.site.state != Site.STATE_ACTIVE:
      return False
    # if not root url
    if self.url["ParentMd5"] != "":
      # url wasn't inserted before
      if self.url["Crawled"] == 0:
        # if site not recrawl
        if self.site.recrawlPeriod == 0:
          if self.site.maxErrors and self.site.errors > self.site.maxErrors:
            self.logger.debug("Errors=" + str(self.site.errors) + " limit is reached maxErrors=" + 
                              str(self.site.maxErrors))
            # TODO: possible improve suspend logic
            # self.updateSite(ERROR_SITE_MAX_ERRORS, True)
            self.updateSite(ERROR_SITE_MAX_ERRORS)
            return False
          elif self.site.maxURLs and self.site.resources > self.site.maxURLs:
            self.logger.debug("Resources=" + str (self.site.resources) + " limit is reached maxURLs=" + 
                              str(self.site.maxURLs))
            # TODO: possible improve suspend logic
            # self.updateSite(ERROR_SITE_MAX_RESOURCES, True)
            self.updateSite(ERROR_SITE_MAX_RESOURCES)
            return False
    self.updateSite(0)
    return True


  # #load url
  # the site object to crawl
  # @param site - object to crawl
  def loadSite(self):
    try:
      if not len(self.batch_item.siteId):
        self.batch_item.siteId = "0"
      self.readSiteFromDB()
    except Exception as err:
      self.logger.error(MSG_ERROR_LOAD_SITE_DATA + err.message)
      raise


  # #load url
  # the site object to crawl
  # @param site - object to crawl
  def readSiteFromDB(self):
    self.site = None
    try:
      self.site_table = DC_SITES_TABLE_NAME
      query = "SELECT * FROM `%s` \
        WHERE `Id`='%s'" \
        % (self.site_table, self.siteId)
      self.logger.info("query: " + query)
      row = self.executeQuery(self.site_connector, query)
      self.logger.info("row: " + str(row))
      if len(row):
        # """
        self.site = Site("")
        self.site.state = row[0]["State"]
        self.site.errors = row[0]["Errors"]
        self.site.maxErrors = row[0]["MaxErrors"]
        # self.site.incrMaxErrors = row[0]["IncrMaxErrors"]
        self.site.resources = row[0]["Resources"]
        self.site.maxURLs = row[0]["MaxURLs"]
        # self.site.incrMaxURLs = row[0]["IncrMaxURLs"]
        self.site.maxResources = row[0]["MaxResources"]
        self.site.AVGSpeed = row[0]['AVGSpeed']
        self.site.AVGSpeedCounter = row[0]['AVGSpeedCounter']
        self.site.maxResourceSize = row[0]['MaxResourceSize']
        self.site.fetchType = row[0]['FetchType']
        self.logger.warn("fetch type:%s", self.site.fetchType)
        # self.site.incrMaxResourceSize = row[0]['IncrMaxResourceSize']
        self.site.recrawlPeriod = row[0]['RecrawlPeriod']
        # updated by Oleksii
        # add support for newly added fields to the dc_sites.sites table
        self.site_table_row = row[0]
    except Exception as err:
      self.logger.error(MSG_ERROR_READ_SITE_FROM_DB + err.message)
      raise
    self.logger.info("site object: " + str(self.site))


  def resetErrorMask(self, batch_item):
    query = "UPDATE `%s` SET `ErrorMask` = 0, `TcDate`=NOW(), `UDate` = NOW() \
    WHERE `URLMd5`='%s'" \
    % (self.url_table, batch_item.urlId)
    self.executeUpdate(self.url_connector, query)


  # #readUrlFromDB read url object from database
  #
  #
  def readUrlFromDB(self):
    self.table_name = self.url_table
    self.url = None
    try:
      query = "SELECT * FROM `%s` \
        WHERE `URLMd5`='%s'" \
        % (self.table_name, \
        self.batch_item.urlId)
      self.logger.info("query: " + query)
      row = self.executeQuery(self.url_connector, query)
      self.logger.info("row: " + str(row))
      if len(row):
        self.url = row[0]
      # when url come from another dc cluster's host
      else:
        if self.addURL():
          self.readUrlFromDB()
        else:
          self.logger.debug("Can't add url from another host.")
          raise CrawlerException("Can't add url from another host.")
    except CrawlerException as err:
      self.logger.debug(MSG_ERROR_LOAD_URL_DATA + err.message)
      raise
    self.logger.info("url object: " + str(self.url))


  # #load url
  # the site object to crawl
  # @param site - object to crawl
  def addURL(self):
    # self.table_name = self.url_table???
    ret = True
    try:
      # add only if site accepted
      self.site_table = DC_SITES_TABLE_NAME
      query = "SELECT * FROM `%s` WHERE `Id`='%s'" % (self.site_table, self.siteId)
      self.logger.debug("query: " + query)
      row = self.executeQuery(self.site_connector, query)
      self.logger.debug("row: " + str(row))
      resources = None  # pylint: disable=unused-variable
      if len(row):
        maxURLs = row[0]["MaxURLs"]
        resources = row[0]["Resources"]
        if row[0]["State"] != Site.STATE_ACTIVE:
          raise CrawlerException("Site state is not active, state=" + str(row[0]["State"]))
        if row[0]["MaxErrors"] and row[0]["Errors"] > row[0]["MaxErrors"]:
          raise CrawlerException("Site maxErrors limit " + str(row[0]["MaxErrors"]) + " reached " + \
                                 str(row[0]["Errors"]))
        elif row[0]["Resources"] > maxURLs:
          if self.autoRemoveURL() == 0:
            return False
            # raise CrawlerException("Site MaxURLs limit " + str(maxURLs) + " reached " + str(row[0]["Resources"]))
          else:
            self.logger.debug("Resources>maxURLs check : Resource(s) auto removed to add one more from external host!")
        query = "SELECT COUNT(*) AS url_count FROM `%s` WHERE `Status` IN (1,2)" % self.url_table
        self.logger.debug("query: %s", query)
        row = self.executeQuery(self.url_connector, query)
        if len(row):
          self.logger.debug("url_count: %s, maxURLs: %s" % (row[0]["url_count"], maxURLs))
          if row[0]["url_count"] > maxURLs:
            if self.autoRemoveURL() == 0:
              raise CrawlerException("URLs count " + str(row[0]["url_count"]) + \
                                     " in state 1 and 2 is grater than limit sites.MaxURLs:" + str(maxURLs))
            else:
              self.logger.debug("urls>maxURLs check : Resource(s) auto removed to add one more from external host!")
        else:
          raise CrawlerException("Execute last SQL query, no rows returned:\n" + query)


        QUERY_TEMPLATE = "INSERT INTO `%s` SET %s"
        query = None
        #self.batch_item.urlObj.CDate = str(self.batch_item.urlObj.CDate)
        self.batch_item.urlObj.CDate = str(datetime.datetime.now())
        fields, values = Constants.getFieldsValuesTuple(self.batch_item.urlObj, Constants.URLTableDict)
        fieldValueString = Constants.createFieldsValuesString(fields, values)
        if fieldValueString != None and fieldValueString != "":
          query = QUERY_TEMPLATE % ((Constants.DC_URLS_TABLE_NAME_TEMPLATE % self.batch_item.urlObj.siteId), 
                                    fieldValueString)
          # queryCallback(query, Constants.SECONDARY_DB_ID)
        # query = "INSERT INTO `%s` (`Site_Id`, `URL`, `Type`, `Status`, `URLMd5`, `ParentMd5`, `TcDate`, `UDate`) \
        #        VALUES('%s', '%s', %s, 2, '%s', '%s', NOW(), NOW())" \
        #        % (self.url_table, self.batch_item.urlObj.siteId, mdb.escape_string(self.batch_item.urlObj.url),
        #           self.batch_item.urlObj.type, self.batch_item.urlObj.urlMd5, self.batch_item.urlObj.parentMd5)
        else:
          raise CrawlerException("Execute last SQL query, no rows returned:\n" + query)
        self.logger.debug("query: %s", query)
        row = self.executeQuery(self.url_connector, query)
        # TODO: result of INSERT query must be checked, wrong state must be logged!
      else:
        raise CrawlerException("Execute last SQL query, no rows returned:\n" + query)
    except CrawlerException as err:
      self.logger.debug("Error add new url from batch (another host source): " + err.message)
      ret = False
    except Exception as err:
      self.logger.error("Error add new url from batch (another host source): " + err.message)
      ret = False
      raise err
    return ret


  # #load url
  # the site object to crawl
  # @param site - object to crawl
  def loadURL(self):
    # do siteId
    self.url_connector = self.dc_urls_db_connect
    if len(self.batch_item.siteId):
      self.url_table = DC_URLS_TABLE_PREFIX + self.batch_item.siteId
    else:
      self.url_table = DC_URLS_TABLE_PREFIX + "0"
    self.logger.info("db backend Table for siteId %s is: %s" % (self.batch_item.siteId, self.url_table))
    self.readUrlFromDB()


  # #resetVars
  def resetVars(self):
    self.need_store_mime = None
    self.site = None
    self.robotparser = None
    self.headers_dict = None
    self.store_http_headers = None
    self.cookie = None
    self.proxies = None
    self.real_url = None
    self.url = None
    self.crawledResource = None
    self.headers = None
    self.table_name = None
    self.crawled_time = None
    self.store_http_request = None
    self.dir = None
    self.kvConnector = None
    self.kvCursor = None
    self.processorName = None
    self.site_properties = None
    self.siteId = None
    self.auto_remove_props = None
    self.store_cookies = None
    self.allow_http_redirects = True
    self.allow_html_redirects = None
    self.http_redirects = 0
    self.html_redirects = 0
    self.max_http_redirects = 1
    self.max_html_redirects = None
    self.dom = None
    self.time_postfix = None
    self.res = None
    self.post_forms = None
    self.auth_name = None
    self.auth_pwd = None
    self.site_table_row = None


  # #process batch item
  # the batch item is the one from list of batch items within batch object
  # @param item - the batch item is the one from list of batch items within batch object
  def processBatchItem(self, batch_item):
    response = None
    self.resetVars()
    self.site_properties = {}
    self.batch_item = batch_item
    self.siteId = batch_item.siteId if batch_item.siteId else "0"
    self.logger.info("Batch item: siteId: %s, urlId: %s" % (batch_item.siteId, batch_item.urlId))
    try:

      self.loadSite()
      # prepare headers and cookie
      self.readSiteProperties()
      self.loadURL()

      if not self.checkSite():
        self.updateURL(status=URL.STATUS_NEW)
        self.logger.debug("Site check was failed. ")
        return response

      if not self.url:
        self.logger.debug("Can't load url. ")
        return response
      # reset error mask for current crawled url
      self.resetErrorMask(batch_item)

      # update state to crawling
      self.updateURL()
      # crawl
      crawl_result = self.crawl()
      if self.crawledResource:
        self.updateCrawledURL()
        self.updateAVGSpeed()
      if not crawl_result:
        self.logger.debug("Crawl results was failed. ")
        return response
      response = self.batch_item
      # not save data to disk/collect URL/collect properties if not modified
      if self.crawledResource.http_code != 304:
        detected_mime = None
        self.getDir()
        try:
          detected_mime = self.writeData()
          self.saveCookies()
        except CrawlerException, cerr:
          self.logger.debug(cerr.message)
          raise
        except Exception as err:
          self.updateURLForFailed(ERROR_WRITE_FILE_ERROR)
          self.logger.error(MSG_ERROR_WRITE_CRAWLED_DATA + err.message, exc_info=True)
        self.collectURLs()
        self.updateCollectTimeAndMime(detected_mime)
        #self.updateCollectTime()
      self.addResource()
    except CrawlerException as err:
      self.logger.debug(MSG_ERROR_PROCESS_BATCH_ITEM)
    except Exception as err:
      self.logger.error(MSG_ERROR_PROCESS_BATCH_ITEM)
      self.logger.error("xxx", exc_info=True)
      tbi = Utils.getTracebackInfo()
      self.logger.error(str(vars(err)) + "\n" + tbi)


    # Added by Oleksii
    # support PROCESSOR_NAME
    if self.processorName == NON_PROCESSING:
      self.logger.debug(MSG_DEBUG_NON_PROCESSING)
      response = None

    self.logger.debug("response: " + str(response))
    return response


  # #updateCollectTimeAndMime
  # add time cost of collect url to URL.CrawlingTime
  # and update Detected MIME type
  #
  #
  def updateCollectTimeAndMime(self, detected_mime):
    collect_time = int((time.time() - self.crawled_time) * 1000)
    if self.auto_detect_mime == DETECT_MIME_MAIN_CONTENT:
      query = "UPDATE %s SET `CrawlingTime` = `CrawlingTime` + %s,  \
      `TotalTime` = `TotalTime` + %s, `TcDate`=NOW(), `UDate` = NOW(), `ContentType`='%s' \
      WHERE `URLMd5` = '%s'" % (self.url_table, collect_time, collect_time, detected_mime, self.batch_item.urlId)
    else:
      query = "UPDATE %s SET `CrawlingTime` = `CrawlingTime` + %s,  \
      `TotalTime` = `TotalTime` + %s, `TcDate`=NOW(), `UDate` = NOW() \
      WHERE `URLMd5` = '%s'" % (self.url_table, collect_time, collect_time, self.batch_item.urlId)
    self.logger.debug("query: %s", query)
    self.executeUpdate(self.url_connector, query)


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    try:
      # read pickled batch object from stdin and unpickle it
      input_pickled_object = sys.stdin.read()
      input_batch = pickle.loads(input_pickled_object)
      self.logger.info("input_batch: " + str(input_batch.items))
      self.batch = input_batch
      Utils.storePickleOnDisk(input_pickled_object, ENV_CRAWLER_STORE_PATH, "crawler.in." + str(self.batch.id))
      # TODO main processing over every url from list of urls in the batch object
      batch_items = []
      for batch_item in input_batch.items:
        if not batch_item:
          continue
        processed_item = self.processBatchItem(batch_item)
        if not processed_item:
          self.logger.debug("LOST BATCH ITEM: %s" + varDump(batch_item))
        else:
          self.logger.debug("ACCEPT BATCH ITEM: %s" + varDump(batch_item))
        batch_items.append(processed_item)
      self.logger.info("process_task_batch: " + str(batch_items))
      process_task_batch = Batch(input_batch.id, batch_items)
      self.logger.info("process_task_batch: " + str(process_task_batch.items))
      # TODO main processing over every url from list of urls in the batch object
      # PT_input_pickled_object = pickle.dumps(process_task_batch)
      # response = self.processTask(PT_input_pickled_object)
      # send response to the stdout
      # print pickle.dumps(process_task_batch)
      output_pickled_object = pickle.dumps(process_task_batch)
      Utils.storePickleOnDisk(output_pickled_object, ENV_CRAWLER_STORE_PATH, "crawler.out." + str(self.batch.id))
      sys.stdout.write(output_pickled_object)
      sys.stdout.flush()
    except Exception, err:
      self.logger.error("Crawler has failed. %s", err.message)
      tbi = Utils.getTracebackInfo()
      self.logger.error(str(vars(err)) + "\n" + tbi)


  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      self.config = ConfigParser.ConfigParser()
      self.config.optionxform = str
      if self.pargs.config:
        self.config.read(self.pargs.config)
    except:
      print MSG_ERROR_LOAD_CONFIG
      raise


  # #load db backend
  # load from cli argument or default config file
  def loadDBBackend(self):
    try:
      className = self.__class__.__name__
      dbHost = self.config.get(className, self.DB_HOST)
      dbPort = int(self.config.get(className, self.DB_PORT))
      dbUser = self.config.get(className, self.DB_USER)
      dbPWD = self.config.get(className, self.DB_PWD)

      db_dc_sites = self.config.get(className, self.DB_SITES)
      db_dc_urls = self.config.get(className, self.DB_URLS)

      self.dc_sites_db_connect = mdb.connect(dbHost, dbUser, dbPWD, db_dc_sites, dbPort, charset="utf8", 
                                             use_unicode=True)
      self.dc_urls_db_connect = mdb.connect(dbHost, dbUser, dbPWD, db_dc_urls, dbPort, charset="utf8", use_unicode=True)
      # self.dc_sites_db_connect.set_character_set("utf8")
      # self.dc_urls_db_connect.set_character_set("utf8")
      self.site_connector = self.dc_sites_db_connect
      self.url_connector = self.dc_urls_db_connect
      self.site_table = None
      self.url_table = None
    except Exception, err:
      self.logger.error("Error load config param: %s" % err.message)
      raise


  # #loadKeyValueDB load key-value db
  #
  #
  def loadKeyValueDB(self):
    try:
      className = self.__class__.__name__
      self.kvDbDir = self.config.get(className, self.DB_DATA_DIR)
    except Exception, err:
      self.logger.error("Error load config param: %s" % err.message)
      raise


  # prepare sqlite DB connector and cursor object
  #
  #
  def prepareKvDbConnector(self):
    if hasattr(self, "kvConnector") and self.kvConnector:
      self.kvConnector.close()
    dbFile = os.path.join(self.kvDbDir, "%s_fields.db" % (self.siteId,))
    self.kvConnector = sqlite3.connect(dbFile)
    self.kvConnector.row_factory = sqlite3.Row
    self.kvConnector.text_factory = unicode
    self.kvCursor = self.kvConnector.cursor()


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      log_conf_file = self.config.get("Application", "log")
      logging.config.fileConfig(log_conf_file)
      # logging.basicConfig()
#      self.logger = logging.getLogger(APP_NAME)
      self.logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
    except:
      print MSG_ERROR_LOAD_LOG_CONFIG_FILE
      raise


  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    try:
      self.raw_data_dir = self.config.get(self.__class__.__name__, "raw_data_dir")
      self.default_header_file = self.config.get(self.__class__.__name__, "headers_file")
      self.default_cookie_file = self.config.get(self.__class__.__name__, "cookie_file")
      self.default_icr_crawl_time = self.config.getfloat(self.__class__.__name__, "default_icr_crawl_time")
      self.db_task_ini = self.config.get(self.__class__.__name__, "db-task_ini")
      LangDetector.init(self.config)
    except Exception, err:
      self.logger.error("Error load config param: %s" % err.message)
      raise


  # #Auto remove resources
  # Removes resources in condition based on dc_sites.sites_properties items
  #
  # @return number of URLs
  def autoRemoveURL(self):
    ret = 0
    try:
      self.logger.debug("Auto remove properties:\n%s", varDump(self.auto_remove_props))
      # If defined auto remove properties???
      if DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES in self.auto_remove_props and\
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES] != "" and\
        DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE in self.auto_remove_props and\
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE] != "" and\
        DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER in self.auto_remove_props and\
        self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER] != "":
        # Select candidates to remove
        query = "SELECT Site_Id, URLMd5 FROM %s WHERE %s ORDER BY %s LIMIT %s" % (self.url_table,
                self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_WHERE].replace("%RecrawlPeriod%",
                                                                                      str(self.site.recrawlPeriod)),
                self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_ORDER],
                self.auto_remove_props[DC_CONSTS.SITE_PROP_AUTO_REMOVE_RESOURCES])
        self.logger.debug("SQL to select auto remove candidates: %s", query)
        result = self.executeQuery(self.url_connector, query)
        if hasattr(result, '__iter__') and len(result) > 0:
          urlsToDelete = []
          for row in result:
            # Create new URLDelete object
            urlDelete = EventObjects.URLDelete(row['Site_Id'], row['URLMd5'], EventObjects.URLStatus.URL_TYPE_MD5)
            urlsToDelete.append(urlDelete)
            self.logger.debug("URL added to auto remove URLMd5:[%s]", row['URLMd5'])
          # Delete list of URLDelete
          # ???
          cfgParser = ConfigParser.ConfigParser()
          cfgParser.read(self.db_task_ini)
          dbTask = DBTasksManager(cfgParser)
          drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_DELETE, urlsToDelete)
          responseDRCESyncTasksCover = dbTask.process(drceSyncTasksCoverObj)
          self.logger.debug("Response from db-task module on URLDelete operation:\n%s", \
                            varDump(responseDRCESyncTasksCover))
          ret = len(result)
        else:
          self.logger.debug("No auto remove candidates or SQL query error!")
      else:
        self.logger.debug("No mandatory auto remove properties in auto_remove_props:\n" + \
                          varDump(self.auto_remove_props))
    except Exception, err:
      self.logger.error("Error of auto remove operation: %s", str(err.message))

    return ret

  # #checkResponse
  #
  def checkResponse(self):
    self.logger.debug("Requests response history: " + str(self.res.redirects))
    # calculate http redirect
    if HTTP_REDIRECT  in self.res.redirects:
      self.http_redirects = self.http_redirects + 1
      self.logger.debug("http redirect: " + str(self.http_redirects))
      self.logger.debug("http max redirect: " + str(self.max_http_redirects))
    # calculate html redirect
    if bool(self.dom.xpath(META_XPATH)):
      self.html_redirects = self.html_redirects + 1
      self.logger.debug("html redirect: " + str(self.html_redirects))
      self.logger.debug("html max redirect: " + str(self.max_html_redirects))
    # check http redirect
    if self.max_http_redirects and self.max_http_redirects != MAX_HTTP_REDIRECTS_UNLIMITED and \
    self.http_redirects >= self.max_http_redirects:
      self.allow_http_redirects = False
      self.logger.debug("http redirect limit was reached! Max http redirects: %s, encountered http redirects: %s." % 
                        (str(self.max_http_redirects), str(self.http_redirects)))
    else:
      self.allow_http_redirects = True
    # check html redirect
    if self.max_html_redirects and int(self.max_html_redirects) != MAX_HTML_REDIRECTS_UNLIMITED and \
    int(self.html_redirects) >= int(self.max_html_redirects):
      self.allow_html_redirects = False
      self.logger.debug("html redirect limit was reached! Max html redirects: %s, encountered html redirects: %s." % 
                        (str(self.max_html_redirects), str(self.html_redirects)))
    else:
      self.allow_html_redirects = True

  # #calcLastModified
  #
  def calcLastModified(self, resource, res):
    if resource.http_code == 304:
      resource.last_modified = self.url["TcDate"]
      # self.logger.debug("resource.last_modified: <<%s>>", str(resource.last_modified))
      # resource.last_modified = datetime.datetime.strptime(resource.last_modified, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M:%S')
      # resource.last_modified = parse(resource.last_modified).strftime('%Y-%m-%d %H:%M:%S')
    elif 'Last-Modified' in res.headers:
      resource.last_modified = res.headers['Last-Modified']
      # resource.last_modified = datetime.datetime.strptime(resource.last_modified, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M:%S')
      resource.last_modified = parse(resource.last_modified).strftime('%Y-%m-%d %H:%M:%S')
    elif 'Date' in res.headers:
      resource.last_modified = res.headers['Date']
      # resource.last_modified = datetime.datetime.strptime(resource.last_modified, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M:%S')
      resource.last_modified = parse(resource.last_modified).strftime('%Y-%m-%d %H:%M:%S')
    else:
      resource.last_modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() - self.default_icr_crawl_time))
    self.logger.debug("LastModified date:" + str(resource.last_modified))
    # from 'Tue, 15 Jul 2014 08:24:42 GMT' to 2014-07-16 12:59:56
    # resource.last_modified = datetime.datetime.strptime(resource.last_modified, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d %H:%M:%S')
    return resource.last_modified


# #RedirectHistory model,
# contains status code and response headers of one redirect response
class RedirectHistory(object):


  # #constructor
  # initialize fields
  def __init__(self, status_code, response_header):
    self.status_code = status_code
    self.response_header = response_header

