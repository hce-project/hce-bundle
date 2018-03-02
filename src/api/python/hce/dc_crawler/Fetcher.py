"""
HCE project, Python bindings, Distributed Tasks Manager application.
web page fetchers.

@package: dc
@file Fetcher.py
@author madk, bgv <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-201 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

# #The BaseFetcher class, defines the interface of fetchers
# #this class don't implement any fetcher
# concrete fetcher class should extends from this class
#


import re
import time
import ctypes
import os
import json
import logging
import base64
import shutil
from random import randint
from urlparse import urlsplit
import psutil
import requests  # pylint: disable=W0611
import requests.exceptions
from requests.auth import HTTPBasicAuth

import dc_crawler.Constants as CONSTS
from dc_crawler.Exceptions import InternalCrawlerException
from dc_crawler.Exceptions import CrawlerFilterException
from dc_crawler.RequestsRedirectWrapper import RequestsRedirectWrapper
import app.Consts as APP_CONSTS
import app.Utils as Utils
from app.Utils import varDump
from app.Exceptions import SeleniumFetcherException

logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)

# max content size for use chardet to detect charset
MAX_CONTENT_SIZE_FOR_CHARDET = 5000000


class BaseFetcher(object):

  fetchers = None

  TYP_NORMAL = 1
  TYP_DYNAMIC = 2
  TYP_URLLIB = 5
  TYP_CONTENT = 6
  TYP_AUTO = 7

  CONNECTION_TIMEOUT = 1.0

  # # Initialization
  #
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  def __init__(self, fetcherPostObj=None):
    self.connectionTimeout = self.CONNECTION_TIMEOUT
    self.logger = None
    self.fetcherPostObj = fetcherPostObj


  # # Init
  #
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  # @param dbWrapper  - DB wrapper instance
  # @param siteId - site ID
  # @param tmpDirOptions - tmp dir options as dictionary
  # @param log - logger instance
  @staticmethod
  def init(fetcherPostObj=None, dbWrapper=None, siteId=None, tmpDirOptions=None, log=None):
    # enumerate content_types we don't want to fetch
    BaseFetcher.prohibited_conten_types = ["audio/mpeg", "application/pdf"]

    BaseFetcher.fetchers = {
        BaseFetcher.TYP_NORMAL : RequestsFetcher(fetcherPostObj, dbWrapper, siteId),
        BaseFetcher.TYP_DYNAMIC: SeleniumFetcher(fetcherPostObj, tmpDirOptions, log),
        BaseFetcher.TYP_URLLIB: URLLibFetcher(fetcherPostObj),
        BaseFetcher.TYP_CONTENT: ContentFetcher(fetcherPostObj)
    }

  # #fetch a url, and return the response
  #
  # @param url, the url to fetch
  # @param method, fetch HTTP method
  # @param headers, request headers dict
  # @param timeout, request timeout(seconds)
  # @param allow_redirects, should follow redirect
  # @param proxies, proxy setting, tuple of proxy_type, host, port, username, password
  # @param auth, basic auth setting, tuple of username and password
  # @param data, post data, used only when method is post
  # @return Response object
  def open(self,
           url,
           method='get',
           headers=None,
           timeout=100,
           allow_redirects=True,
           proxies=None,
           auth=None,
           data=None,
           log=None,
           allowed_content_types=None,
           max_resource_size=None,
           max_redirects=CONSTS.MAX_HTTP_REDIRECTS_LIMIT,
           filters=None,
           executable_path=None,
           depth=None,
           macro=None):
    if headers is None:
      headers = {}
    del url, method, headers, timeout, allow_redirects, proxies, auth, data, log, allowed_content_types, \
        max_resource_size, max_redirects, filters, executable_path, depth, macro


  # #get fetched by fetch type
  #
  # @param typ - the fetch type
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  # @param dbWrapper  - DB wrapper instance
  # @param siteId - site ID
  # @param tmpDirOptions - tmp dir options as dictionary
  # @param log - logger instance
  # @return fetcher
  @staticmethod
  def get_fetcher(typ, fetcherPostObj=None, dbWrapper=None, siteId=None, tmpDirOptions=None, log=None):
    if not BaseFetcher.fetchers:
      BaseFetcher.init(fetcherPostObj, dbWrapper, siteId, tmpDirOptions, log)
    if typ in BaseFetcher.fetchers:
      return BaseFetcher.fetchers[typ]
    else:
      raise BaseException("unsupported fetch type:%s" % (typ,))


  # #check whether the fetcher have meta resource
  #
  # @return whether the fetcher have meta resource
  def should_have_meta_res(self):

    return False

  # Get domain name from URL string
  #
  # @param url string
  # @param default value in case of some URL parsing problem
  # @return domain name string or empty if error
  def getDomainNameFromURL(self, url, default=''):
    ret = default

    urlParts = urlsplit(url)
    if len(urlParts) > 1:
      ret = urlParts[1]

    return ret


# # Check redirects hook
#
#
def checkRedirectsHook(r, *args, **kwargs):
  logger.debug('r.url = ' + str(r.url))
  logger.debug('args = ' + str(args))
  logger.debug('kwargs = ' + str(kwargs))
  logger.debug('type(r): %s,  r = %s', str(type(r)), varDump(r))


# # Fetcher base on the requests module, cann't execute javascript
#
#
class RequestsFetcher(BaseFetcher):

  # # Initialization
  #
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  # @param dbWrapper  - DB wrapper instance
  # @param siteId - site ID
  def __init__(self, fetcherPostObj=None, dbWrapper=None, siteId=None):
    BaseFetcher.__init__(self, fetcherPostObj)

    self.dbWrapper = dbWrapper
    self.siteId = siteId


  # #fetch a url, and return the response
  #
  # @param url, the url to fetch
  # @param method, fetch HTTP method
  # @param headers, request headers dict
  # @param timeout, request timeout(seconds)
  # @param allow_redirects, should follow redirect
  # @param proxies - proxy setting tuple
  # @param auth, basic auth setting, tuple of name and password
  # @param data, post data, used only when method is post
  # @return Response object
  def open(self,
           url,
           method='get',
           headers=None,
           timeout=100,
           allow_redirects=True,
           proxies=None,
           auth=None,
           data=None,
           log=None,
           allowed_content_types=None,
           max_resource_size=None,
           max_redirects=CONSTS.MAX_HTTP_REDIRECTS_LIMIT,
           filters=None,
           executable_path=None,
           depth=None,
           macro=None):

    # set logger
    log = logger if log is None else log

    headers1 = {}
    for key in headers.keys():
      if not key.startswith('--'):
        headers1[key] = headers[key]
    headers = headers1

    if not isinstance(timeout, tuple):
      if hasattr(self, 'connectionTimeout'):
        timeout = (self.connectionTimeout, timeout)
      else:
        timeout = (self.CONNECTION_TIMEOUT, timeout)

    if auth:
      auth = HTTPBasicAuth(auth[0], auth[1])

    proxy_setting = None
    if proxies is not None:
      proxy_type, proxy_host, proxy_port, proxy_user, proxy_passwd = proxies
      if proxy_type is None:
        proxy_type = "http"
      if proxy_user is not None:
        proxies = "%s://%s:%s@%s:%s" % (proxy_type, proxy_user, proxy_passwd, proxy_host, proxy_port)
      else:
        proxies = "%s://%s:%s" % (proxy_type, proxy_host, proxy_port)
      proxy_setting = {proxy_type : proxies}

    # # save location value
    location = url
    res = Response()
    try:
      requestsRedirect = RequestsRedirectWrapper(self.dbWrapper, self.siteId)
      impl_res = requestsRedirect.request(url=url,
                                          method=method,
                                          timeout=timeout,
                                          headers=headers,
                                          allowRedirects=allow_redirects,
                                          proxySetting=proxy_setting,
                                          auth=auth,
                                          data=data,
                                          maxRedirects=max_redirects,
                                          filters=filters)

      log.debug("!!! impl_res.headers: %s", varDump(impl_res.headers))
      log.debug("!!! impl_res.url: %s", str(impl_res.url))

      location = impl_res.url
      headers = dict(impl_res.headers.lower_items())

      # try to prevent huge content fetching
      if "content-length" in impl_res.headers and \
        max_resource_size != CONSTS.MAX_HTTP_SIZE_UNLIMIT and \
        int(impl_res.headers['content-length']) > max_resource_size:
        log.debug("Content size overshooted. content-length: %s, max_resource_size: %s" % \
                     (str(impl_res.headers['content-length']), str(max_resource_size)))
        res.content_size = int(impl_res.headers['content-length'])
      else:
        ct = impl_res.headers.get('content-type', '').lower()
        # don't detect charset for binary content type or BIG response
        if ct.startswith('application') or ct.startswith('audio') or \
          len(impl_res.content) >= MAX_CONTENT_SIZE_FOR_CHARDET:
          if "xml" in ct:
            encoding = SimpleCharsetDetector().detect(impl_res.content, contentType='xml')
            log.debug("encoding3=%s", str(encoding))
            if encoding is not None:
              impl_res.encoding = encoding
          else:
            detected_encoding = impl_res.encoding
          log.debug("Headers contains 'application' or 'audio' content-type: %s",
                    impl_res.headers.get('content-type', ''))
        else:
          # use chardet to improve encoding detect
#           ct = impl_res.headers.get('content-type', '').lower()
          log.debug("impl_res.encoding1=%s, content-type=%s", impl_res.encoding, ct)
          # Try simple way of charset detection for an html
          encoding = None
          if "html" in ct:
            log.debug("Using the SimpleCharsetDetector()")
            encoding = SimpleCharsetDetector().detect(impl_res.content)
            log.debug("encoding=%s", str(encoding))
            if encoding is not None:
              impl_res.encoding = encoding

          elif "xml" in ct:
            encoding = SimpleCharsetDetector().detect(impl_res.content, contentType='xml')
            log.debug("encoding3=%s", str(encoding))
            if encoding is not None:
              impl_res.encoding = encoding


          if (impl_res.encoding is None) or ((encoding is None) and (impl_res.encoding not in ct and "xml" not in ct)):
            log.debug("Using the charset to improve encoding detect")
            detected_encoding = impl_res.apparent_encoding
            if detected_encoding != 'ascii' and detected_encoding != 'ISO-8859-2':
              impl_res.encoding = detected_encoding
          log.debug("impl_res.encoding2=%s", impl_res.encoding)
        # Fix for pages that has xml document tag but no html structure inside
        text_buffer = self.fixWrongXMLHeader(impl_res.content)
        if impl_res.headers.get('content-type', '').startswith('application'):
          res.unicode_content = impl_res.content
        else:
          res.unicode_content = text_buffer
        res.str_content = impl_res.content
        if impl_res.headers.get('content-type', '').startswith('application'):
          res.rendered_unicode_content = impl_res.content
        else:
          res.rendered_unicode_content = text_buffer
        # res.content_size = impl_res.raw.tell()
        if res.rendered_unicode_content is None:
          res.content_size = 0
        else:
          res.content_size = len(res.rendered_unicode_content)

      res.headers = impl_res.headers
      res.redirects = impl_res.history
      res.status_code = impl_res.status_code
      res.url = impl_res.url
      res.encoding = impl_res.encoding
      res.request = impl_res.request
      res.cookies = requests.utils.dict_from_cookiejar(impl_res.cookies)

      # update location value
      res.headers.update({'Location':location})

    except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout), err:
      res.error_mask = APP_CONSTS.ERROR_REQUEST_TIMEOUT
      msg = "Requests fetcher has thrown '%s' exception: " % str(type(err))
      if isinstance(err, requests.exceptions.Timeout):
        msg += "The request timed out."
      elif isinstance(err, requests.exceptions.ReadTimeout):
        msg += "The server did not send any data in the allotted amount of time."
      elif isinstance(err, requests.exceptions.ConnectTimeout):
        msg += "The request timed out while trying to connect to the remote server."

      log.debug(str(msg))
      raise err
    except requests.exceptions.ConnectionError, err:
      res.error_mask = APP_CONSTS.ERROR_FETCH_CONNECTION_ERROR
      log.debug(">>> Requests fetcher has thrown ConnectionError exception: " + str(err))
      raise err
    except requests.exceptions.HTTPError, err:
      res.error_mask = APP_CONSTS.ERROR_FETCH_HTTP_ERROR
      log.debug(">>> Requests fetcher has thrown HTTPError exception: " + str(err))
      raise err
    except requests.exceptions.URLRequired, err:
      res.error_mask = APP_CONSTS.ERROR_FETCH_INVALID_URL
      log.debug(">>> Requests fetcher has thrown URLRequired exception: " + str(err))
      raise err
    except requests.exceptions.TooManyRedirects, err:
      res.error_mask = APP_CONSTS.ERROR_FETCH_TOO_MANY_REDIRECTS
      log.debug(">>> Requests fetcher has thrown TooManyRedirects exception: " + str(err))
      raise err
    except requests.exceptions.RequestException, err:
      res.error_mask = APP_CONSTS.ERROR_FETCH_AMBIGUOUS_REQUEST
      log.debug(">>> Requests fetcher has thrown RequestException exception: " + str(err))
      raise err
    except CrawlerFilterException, err:
      res.error_mask = APP_CONSTS.ERROR_CRAWLER_FILTERS_BREAK
      log.debug("Crawler has not allowed filter: " + str(err))
      raise err
    except Exception, err:
      res.error_mask = APP_CONSTS.ERROR_FETCHER_INTERNAL
      log.debug(">>> Requests fetcher has thrown exception" + \
                " type: " + str(type(err)) + "\n" + Utils.getTracebackInfo())
      raise InternalCrawlerException("Requests fetcher has thrown exception")

    # fetcher post processing if necessary
    if self.fetcherPostObj is not None:
      self.fetcherPostObj.process(res)

    return res


  # #Fix the wrong html document structure in case of XML header is defined first
  #
  # @param content input content
  # @return fixed contentStr
  def fixWrongXMLHeader(self, contentStr):
    # text_file = open("/tmp/fetcher_log.txt", "w")
    # text_file.write("Fetcher: start\n")

    if contentStr.startswith('<?xml ') and '<html' in contentStr and '<head' in contentStr:
      # text_file.write("Fetcher: xml detected!\n")
      p = re.compile(r'<\?xml .*\?>')
      contentStr = p.sub('', contentStr, count=1)
      # text_file.write(contentStr)

    # text_file.close()

    return contentStr


# # Fetcher based on the selenium project web-driver
#
#
class SeleniumFetcher(BaseFetcher):

  DEFAUIL_TIMEOUT = 5
  CONTENT_TYPE_JSON = 'text/json'
  CONTENT_TYPE_HTML = 'text/html'
  DELAY_TERMINATE_AND_QUIT = 0.5

  ERROR_FATAL = 1
  ERROR_GENERAL = 2
  ERROR_CONTENT_OR_COOKIE = 3
  ERROR_NAME_NOT_RESOLVED = 400
  ERROR_TOO_MANY_REDIRECTS = 11
  ERROR_MACRO_RETURN_VALUE = 12
  ERROR_PROXY_CONNECTION_FAILED = 504
  ERROR_CONNECTION_TIMED_OUT = 505
  ERROR_TUNNEL_CONNECTION_FAILED = 403
  ERROR_SERVICE_UNAVAILABLE = 503
  ERROR_CONFLICT = 409
  ERROR_EMPTY_RESPONSE = 13

  LOG_MESSAGE_RENDERRER_TIMEOUT = 'Timed out receiving message from renderer'
  LOG_MESSAGE_SERVER_RESPONSE_503 = 'server responded with a status of 503'
  LOG_MESSAGE_SERVER_RESPONSE_409 = 'server responded with a status of 409 (Conflict)'

  CHROME_PROCESS_NAMES = ['chrome', 'BrowserBlocking']
  CHROME_DIRS_TEMPLATE = '.google.Chrome.'
  CHROME_DEBUG_LOG_NAME = 'chrome_debug.log'

  MACRO_RESULT_TYPE_DEFAULT = 0
  MACRO_RESULT_TYPE_URLS_LIST = 1
  MACRO_RESULT_TYPE_CONTENT = 2
  MACRO_RESULT_TYPE_AUTO = 3

  TMP_DIR_TYPE_OPEN = 0
  TMP_DIR_TYPE_INSTANTIATE = 1


  # # Initialization
  #
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  # @param tmpDirOptions - temporary dirrectory options
  # @param log - logger instance
  def __init__(self, fetcherPostObj=None, tmpDirOptions=None, log=None):
    super(SeleniumFetcher, self).__init__(fetcherPostObj)

    if log is not None:
      self.logger = log

    if self.logger:
      self.logger.debug("Initialization of instance, tmpDirOptions: %s", str(tmpDirOptions))

    self.tmpDirPath = '/tmp'
    self.tmpDirPrefix = 'dfetcher_tmp_%PID%'
    self.tmpDirSuffix = ''
    self.tmpDirType = self.TMP_DIR_TYPE_OPEN
    self.tmpDirRemoveBeforeCreate = True
    if tmpDirOptions is not None:
      if 'path' in tmpDirOptions:
        self.tmpDirPath = tmpDirOptions['path']
      if 'prefix' in tmpDirOptions:
        self.tmpDirPrefix = tmpDirOptions['prefix']
      if 'suffix' in tmpDirOptions:
        self.tmpDirSuffix = tmpDirOptions['suffix']
      if 'type' in tmpDirOptions:
        self.tmpDirType = int(tmpDirOptions['type'])
      if 'remove_before_create' in tmpDirOptions:
        self.tmpDirRemoveBeforeCreate = bool(int(tmpDirOptions['remove_before_create']))
    pid = str(os.getpid()).strip()

    if self.tmpDirPath == '' and self.tmpDirPrefix == '' and self.tmpDirSuffix == '':
      self.tmpDir = ''
    else:
      self.tmpDir = self.tmpDirPath + '/' + self.tmpDirPrefix.replace('%PID%', pid) + \
                    self.tmpDirSuffix.replace('%PID%', pid)
    if self.tmpDirType == self.TMP_DIR_TYPE_INSTANTIATE:
      if not self.initializeTmpDirs(None):
        msg = 'Temporary directory type INSTANTIATE `%s` initialization error!', self.tmpDir
        if self.logger is not None:
          self.logger.error(msg)
        raise SeleniumFetcherException(msg)
      else:
        if self.logger is not None:
          self.logger.debug("Temporary directory type INSTANTIATE `%s` initialized!", self.tmpDir)
    self.driver = None
    self.driverPid = 0
    self.inlineURLMacroDelimiter = '###'
    self.sessionId = '--sessionId=' + str(pid)
    self.userDataDirUsed = ''


  # delete
  #
  def __del__(self):
    if self.logger:
      self.logger.debug("Delete instance, temporary dir type: %s", str(self.tmpDirType))

    if self.tmpDirType == self.TMP_DIR_TYPE_INSTANTIATE:
      self.removeTmpDirs()


  # #fetch a url, and return the response
  #
  # @param url, the url to fetch
  # @param method, fetch HTTP method
  # @param headers, request headers dict
  # @param timeout, request timeout(seconds)
  # @param allow_redirects, should follow redirect
  # @param proxies, proxy setting
  # @param auth, basic auth setting
  # @param data, post data, used only when method is post
  # @param logger
  # @param allowed_content_types
  # @param max_resource_size
  # @param max_redirects
  # @param executable_path path and file name of the driver binary executable
  # @return Response object
  def open(self,
           url,
           method='get',
           headers=None,
           timeout=DEFAUIL_TIMEOUT,
           allow_redirects=True,
           proxies=None,
           auth=None,
           data=None,
           log=None,
           allowed_content_types=None,
           max_resource_size=None,
           max_redirects=1,
           filters=None,
           executable_path=None,
           depth=None,
           macro=None):

    if log is not None:
      self.logger = log

    if self.logger is not None:
      self.logger.debug("Dynamic fetcher call:\nurl:" + str(url) + \
                        "\nmethod:" + str(method) + "\nheaders:" + str(headers) + "\ntimeout:" + str(timeout) + \
                        "\nallow_redirects:" + str(allow_redirects) + "\nproxies:" + str(proxies) + "\nauth:" + \
                        str(auth) + "\ndata:" + str(data) + "\nlogger:" + str(self.logger) + \
                        "\nallowed_content_types:" + str(allowed_content_types) + "\nmax_resource_size:" + \
                        str(max_resource_size) + "\nmax_redirects:" + str(max_redirects) + "\nexecutable_path:" + \
                        str(executable_path) + "\ncur_dir:" + str(os.getcwd()) + "\nmacro:" + str(macro))

    t1 = 0
    if isinstance(timeout, tuple):
      t = int(timeout[0])
      if isinstance(timeout[0], float):
        t1 = int(str(timeout[0]).strip()[str(timeout[0]).strip().find('.') + 1:])
    else:
      t = int(timeout)
      if isinstance(timeout, float):
        t1 = int(str(timeout).strip()[str(timeout).strip().find('.') + 1:])
    if self.logger is not None:
      self.logger.debug("Execution timeout: %s, damping timeout: %s", str(t), str(t1))
    if t1 >= t:
      msg = "Execution timeout: %s less or equal than damping timeout: %s, aborted" % (str(t), str(t1))
      if self.logger is not None:
        self.logger.error(msg)
      raise SeleniumFetcherException(msg)

    if self.tmpDirType == self.TMP_DIR_TYPE_OPEN:
      if not self.initializeTmpDirs(headers):
        msg = 'Temporary directory type OPEN `%s` initialization error!' % self.tmpDir
        if self.logger is not None:
          self.logger.error(msg)
        raise SeleniumFetcherException(msg)
      else:
        if self.logger is not None:
          self.logger.debug('Temporary directory type OPEN `%s` initialized', self.tmpDir)

    from app.Utils import executeWithTimeout
    try:
      ret = executeWithTimeout(func=self.openT, args=(url, headers, t1, proxies, executable_path, macro,),
                               timeout=t, log=self.logger)
      if ret is None:
        if self.logger is not None:
          msg = 'Execution timeout: ' + str(t) + ' reached!'
          self.logger.error(msg)
        raise SeleniumFetcherException(msg, APP_CONSTS.ERROR_FETCH_TIMEOUT)
    except SeleniumFetcherException, err:
      if self.logger is not None:
        self.logger.error("Error SeleniumFetcherException: %s", str(err))
      self.cleanup(1, headers)
      raise err
    except Exception, err:
      if self.logger is not None:
        msg = 'Execution with timeout error:' + str(err)
        self.logger.error(msg)
      self.cleanup(1, headers)
      raise SeleniumFetcherException(msg)
    finally:
      self.cleanup(0, headers)

    if self.logger is not None:
      self.logger.debug("Dynamic fetcher call finished normally.")

    # fetcher post processing if necessary
    if self.fetcherPostObj is not None:
      self.fetcherPostObj.process(ret)

    return ret


  # #Called by open() method with timeout of execution
  #
  # @param url
  # @param headers
  # @param timeout
  # @param proxies
  # @param executable_path
  # @macro
  # @return Response object
  def openT(self, url, headers, timeout, proxies, executable_path, macro):
    startTime = time.time()
    inlineMacro = ''

    try:
      # Prepare inline macro
      if self.inlineURLMacroDelimiter in url:
        t = url.split(self.inlineURLMacroDelimiter)
        url = t[0]
        inlineMacro = t[1]
      # Dependent import
      try:
        from selenium import webdriver
        import selenium.webdriver.support.ui  # pylint: disable=W0612
      except Exception, err:
        msg = 'Selenium module import error: ' + str(err)
        if self.logger is not None:
          self.logger.error(msg)
        raise SeleniumFetcherException(msg)

      if self.logger is not None:
        # One way
        from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
        seleniumLogger.setLevel(self.logger.getEffectiveLevel())
        # Second way
        selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        # Only display possible problems
        # selenium_logger.setLevel(logging.WARNING)
        selenium_logger.setLevel(self.logger.getEffectiveLevel())

      # Initialize defaults
      exec_path = "./"
      driver_name = "chromedriver"
      error_msg = ""
      error_code = 0
      error_code_macro = 0
      page_source_macro = None
      content_type_macro = None
      result_type_macro = self.MACRO_RESULT_TYPE_DEFAULT
      fatalErrors = [self.ERROR_FATAL, self.ERROR_GENERAL, self.ERROR_NAME_NOT_RESOLVED, self.ERROR_TOO_MANY_REDIRECTS,
                     self.ERROR_PROXY_CONNECTION_FAILED, self.ERROR_CONNECTION_TIMED_OUT, self.ERROR_CONFLICT,
                     self.ERROR_TUNNEL_CONNECTION_FAILED, self.ERROR_EMPTY_RESPONSE, self.ERROR_SERVICE_UNAVAILABLE]

      # Check environment
      # TODO: add dependecy argument pass, now reduced and hardcoded
      checkEnv = True
      if checkEnv:
        # envVars = {"DISPLAY": "", "LC_ALL":"en_US.UTF-8", "LANG":"en_US.UTF-8", "LANGUAGE":"en_US.UTF-8"}
        envVars = {"DISPLAY": "", "LANG":"en_US.UTF-8"}
        for varName in envVars:
          v = os.getenv(varName, "")
          if varName == "DISPLAY":
            if v == "":
              raise SeleniumFetcherException("Environment variable 'DISPLAY' is not set!")
          else:
            if v != envVars[varName]:
              raise SeleniumFetcherException("Environment variable '" + varName + "' value expected:'" + \
                                             envVars[varName] + "', got from os: '" + v + "'; all env: " + \
                                             str(os.environ))

      # Create driver instance
      try:
        # get chrome options
        chrome_option = self.getOptions(webdriver, headers, proxies, url)

        # The platform-dependent path to the driver executable
        if executable_path is None:
          path = exec_path + driver_name + str(ctypes.sizeof(ctypes.c_voidp) * 8)
        else:
          path = executable_path
        if self.logger is not None:
          self.logger.debug("Chrome driver executable path: %s, options: %s", str(path), str(chrome_option.arguments))
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        # enable browser logging
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = {'browser':'ALL'}
        # Get driver
        self.driver = webdriver.Chrome(executable_path=path, chrome_options=chrome_option, desired_capabilities=d)
        self.driverPid = self.driver.service.process.pid
        if self.logger:
          self.logger.debug("Driver pid: " + str(self.driverPid))
      except Exception, err:
        error_msg = 'Driver initialization error: ' + str(err)
        error_code = self.ERROR_FATAL
      except:  # pylint: disable=W0702
        error_msg = 'General driver initialization!'
        error_code = self.ERROR_GENERAL

      if error_code > 0:
        if self.logger is not None:
          self.logger.error('Fatal error: ' + error_msg)
        raise SeleniumFetcherException(error_msg)

      # Make request
      try:
        # driver.set_page_load_timeout(timeout * 10)
        # driver.set_script_timeout(timeout * 10)
        # driver.implicitly_wait(timeout * 10)

        if self.logger is not None:
          self.logger.debug("Chrome driver get url: `%s`", str(url))
        self.driver.get(url)
        # Get logs
        log_types = self.driver.log_types
        if 'browser' in log_types:
          log_list = self.driver.get_log('browser')
          if self.logger is not None:
            self.logger.debug("Driver logs: " + str(log_list))
          for item_dict in log_list:
            if self.logger is not None:
              self.logger.debug("Driver message: `%s`", str(item_dict["message"]))
            if "message" in item_dict and ((url + ' ') in item_dict["message"] or (url + '/ ') in item_dict["message"]):
              error_msg += item_dict["message"] + " | "
        else:
          if self.logger is not None:
            self.logger.error("No driver logs!")
        if error_msg != "":
          entrances = [
              (r"(.*)net::ERR_NAME_NOT_RESOLVED(.*)", self.ERROR_NAME_NOT_RESOLVED),
              (r"(.*)net::ERR_TOO_MANY_REDIRECTS(.*)", self.ERROR_TOO_MANY_REDIRECTS),
              (r"(.*)ERR_PROXY_CONNECTION_FAILED(.*)", self.ERROR_PROXY_CONNECTION_FAILED),
              (r"(.*)net::ERR_CONNECTION_TIMED_OUT(.*)", self.ERROR_CONNECTION_TIMED_OUT),
              (r"(.*)net::ERR_TUNNEL_CONNECTION_FAILED(.*)", self.ERROR_TUNNEL_CONNECTION_FAILED),
              (r"(.*)net::ERR_CONNECTION_RESET(.*)", self.ERROR_TUNNEL_CONNECTION_FAILED),
              (r"(.*)net::ERR_INVALID_URL(.*)", self.ERROR_TUNNEL_CONNECTION_FAILED),
              (r"(.*)net::ERR_EMPTY_RESPONSE(.*)", self.ERROR_EMPTY_RESPONSE),
              (r"(.*)" + self.LOG_MESSAGE_RENDERRER_TIMEOUT + r"(.*)", self.ERROR_CONNECTION_TIMED_OUT),
              (r"(.*)" + self.LOG_MESSAGE_SERVER_RESPONSE_503 + r"(.*)", self.ERROR_SERVICE_UNAVAILABLE),
              (r"(.*)" + self.LOG_MESSAGE_SERVER_RESPONSE_409 + r"(.*)", self.ERROR_CONFLICT),
              (r"(.*)403 \(Forbidden\)(.*)", 403),
              (r"(.*)404 \(Not Found\)(.*)", 404),
              (r"(.*)500 \(Internal Server Error\)(.*)", 500),
              (r"(.*)net::(.*)", 520)]
          for item in entrances:
            regex = re.compile(item[0])
            r = regex.search(error_msg)
            if r:
              error_code = item[1]
              if self.logger is not None:
                self.logger.debug("Page error: " + error_msg)
              break
        if error_code not in fatalErrors and inlineMacro != '':
          if self.logger is not None:
            self.logger.debug("Execute inline macro: %s", str(inlineMacro))
          macroResults, errorCode, errorMsg = self.execMacroSimple([inlineMacro])
        if error_code not in fatalErrors and macro is not None:
          if self.logger is not None:
            self.logger.debug("Execute macro: %s", str(macro))
          if isinstance(macro, list):
            macroResults, errorCode, errorMsg = self.execMacroSimple(macro)
          else:
            macroResults, errorCode, errorMsg, content_type_macro, result_type_macro = self.execMacroExtended(macro)
          if errorCode > 0:
            error_code_macro |= APP_CONSTS.ERROR_MACRO
            error_msg = errorMsg
          if len(macroResults) > 0:
            if result_type_macro == self.MACRO_RESULT_TYPE_CONTENT:
              page_source_macro = macroResults
            else:
              page_source_macro = json.dumps(macroResults, ensure_ascii=False)
      except Exception, err:
        error_msg = 'Driver error: ' + str(err) + '; logs: ' + self.getAllLogsAsString()
        error_code = self.ERROR_FATAL
      except:  # pylint: disable=W0702
        error_msg = "General driver usage error!"
        error_code = self.ERROR_GENERAL

      if error_code == 0:
        if timeout > 0:
          if self.logger is not None:
            self.logger.debug("Wait on damping timeout to load all dynamic parts of the page: %s sec", str(timeout))
          # Wait fixed time to load all dynamic parts of the page
          time.sleep(timeout)
      elif error_code in fatalErrors:
        if self.logger is not None:
          self.logger.debug("Fatal error, code: %s, msg: %s", str(error_code), error_msg)
        if error_code == self.ERROR_NAME_NOT_RESOLVED:
          code = APP_CONSTS.ERROR_FETCH_INVALID_URL
        elif error_code == self.ERROR_TOO_MANY_REDIRECTS:
          code = APP_CONSTS.ERROR_FETCH_TOO_MANY_REDIRECTS
        elif error_code == self.ERROR_PROXY_CONNECTION_FAILED:
          code = APP_CONSTS.ERROR_FETCH_CONNECTION_ERROR
        elif error_code == self.ERROR_CONNECTION_TIMED_OUT:
          code = APP_CONSTS.ERROR_FETCH_CONNECTION_TIMEOUT
        elif error_code == self.ERROR_TUNNEL_CONNECTION_FAILED:
          code = APP_CONSTS.ERROR_FETCH_FORBIDDEN
        elif error_code == self.ERROR_EMPTY_RESPONSE:
          code = APP_CONSTS.ERROR_EMPTY_RESPONSE
        elif error_code == self.ERROR_SERVICE_UNAVAILABLE:
          code = APP_CONSTS.ERROR_FETCH_FORBIDDEN
        elif error_code == self.ERROR_CONFLICT:
          code = APP_CONSTS.ERROR_FETCH_HTTP_ERROR
        else:
          code = APP_CONSTS.ERROR_FETCHER_INTERNAL
        # self.cleanup(driver)
        raise SeleniumFetcherException(error_msg, code)

      page_source = ""
      cookies = {}
      try:
        page_source = self.driver.page_source
        cookies = self.driver.get_cookies()
      except Exception, err:
        error_msg = str(err)
        error_code = self.ERROR_CONTENT_OR_COOKIE
      except:  # pylint: disable=W0702
        error_msg = "Content and cookies get error!"
        error_code = self.ERROR_CONTENT_OR_COOKIE

      content_type = None
      charset = None
      try:
        attr = self.driver.find_element_by_xpath(".//meta[translate(@http-equiv,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='content-type']").get_attribute("content")  # pylint: disable=C0301
        regex = re.compile(r"(.*); charset=(.*)", re.IGNORECASE)
        items = regex.search(attr)
        if items is not None:
          items = items.groups()
          if len(items) > 1:
            content_type = items[0]
            charset = items[1]
      except Exception, err:
        pass
      if content_type is None:
        try:
          attr = self.driver.find_element_by_xpath('//html')
          content_type = self.CONTENT_TYPE_HTML
        except Exception, err:
          pass
      if content_type is not None and charset is None:
        try:
          charset = self.driver.find_element_by_xpath('//meta[@charset]').get_attribute("charset")
        except Exception, err:
          pass
      if charset is None:
        try:
          charset = self.driver.execute_script("return document.characterSet;")
        except Exception, err:
          if self.logger is not None:
            self.logger.debug("Charset detection error: %s", str(err))

      try:
        current_url = self.driver.current_url
      except Exception, err:
        current_url = url
        if self.logger is not None:
          self.logger.debug("Get 'current_url' error: %s, input url assumed: %s", str(err), str(url))

      # if self.LOG_MESSAGE_RENDERRER_TIMEOUT in error_msg:
      #  self.cleanup(driver)
      #  raise SeleniumFetcherException(error_msg, APP_CONSTS.ERROR_FETCH_CONNECTION_TIMEOUT)

      try:
        res = Response()
        res.url = current_url
        if error_code > 100 or error_code == self.ERROR_FATAL:
          res.status_code = error_code
        else:
          res.status_code = 200
        res.redirects = []
        res.page_source = page_source
        if page_source_macro is None:
          res.unicode_content = page_source
        else:
          res.unicode_content = page_source_macro
        res.str_content = res.unicode_content
        res.rendered_unicode_content = res.unicode_content
        res.content_size = len(res.unicode_content)
        res.encoding = charset
        res.headers = {'content-length': res.content_size}
        if page_source_macro is not None:
          if content_type_macro is not None:
            content_type = content_type_macro
          else:
            content_type = self.CONTENT_TYPE_JSON
        if content_type is not None:
          res.headers['content-type'] = content_type
        if current_url != url:
          res.headers['location'] = current_url
        res.meta_res = res.unicode_content
        res.cookies = cookies
        res.dynamic_fetcher_type = driver_name
        res.dynamic_fetcher_result_type = result_type_macro
        if error_code_macro != APP_CONSTS.ERROR_OK:
          res.error_mask |= error_code_macro
        res.time = time.time() - startTime
        res.request = {'headers':headers}  # # alexv
        res.error_msg = error_msg
      except Exception, err:
        msg = 'Response fill error: ' + str(err)
        if self.logger is not None:
          self.logger.error(msg)
        raise SeleniumFetcherException(msg)

      if self.logger is not None and error_msg != "":
        self.logger.debug("Dynamic fetcher none fatal error: " + error_msg)

      return res

    except Exception, err:
      msg = 'Unrecognized dynamic fetcher error: ' + str(err)
      if self.logger is not None:
        self.logger.error(msg)
      raise SeleniumFetcherException(msg)


  # #Finish and close all dependencies, quit driver, remove temporary directory
  #
  # @param state: 0 - normal finish, 1 - after error
  # @param headers
  def cleanup(self, state=0, headers=None):
    if self.logger is not None and '--log-chrome-debug-log' in headers:
      logFile = self.userDataDirUsed + '/' + self.CHROME_DEBUG_LOG_NAME
      try:
        with open(logFile, 'r') as f:
          logData = f.read()
        self.logger.debug("Chrome debug log file `%s`:\n%s", logFile, logData)
      except Exception, err:
        self.logger.debug("Error read chrome debug log file `%s`: %s", logFile, str(err))

    if self.logger is not None:
      self.logger.debug("Cleanup type: %s, driver: %s", str(state), str(self.driver))

    try:
      if self.driver is not None:
        self.driver.quit()
        time.sleep(self.DELAY_TERMINATE_AND_QUIT)
    except Exception:
      pass

    if state == 1:
      time.sleep(self.DELAY_TERMINATE_AND_QUIT)
      try:
        if self.driver is not None:
          self.driver.quit()
      except Exception:
        pass
      time.sleep(self.DELAY_TERMINATE_AND_QUIT)
      try:
        if self.logger:
          self.logger.debug("Driver pid: " + str(self.driverPid))
        self.killProcess(self.driverPid)
      except Exception:
        if self.logger:
          self.logger.debug("Error kill driver pid: %s", str(self.driverPid))

    self.chromeProcessesCleanup(headers)

    if self.tmpDirType == self.TMP_DIR_TYPE_OPEN:
      self.removeTmpDirs(self.DELAY_TERMINATE_AND_QUIT)


  # #Chrome processes cleanup
  #
  # @param headers
  def chromeProcessesCleanup(self, headers):
    if self.logger:
      self.logger.debug("Chrome processes cleanup started")

    if self.sessionId != '':
      key = self.sessionId
    else:
      if self.tmpDir == '':
        if '--disk-cache-dir' in headers:
          key = '--disk-cache-dir=' + headers['--disk-cache-dir']
        if '--profile-directory' in headers:
          key = '--profile-directory=' + headers['--profile-directory']
        if '--user-data-dir' in headers:
          key = '--user-data-dir=' + headers['--user-data-dir']
      else:
        key = self.tmpDir

    try:
      for proc in psutil.process_iter():
        try:
          # if self.logger:
          #  self.logger.debug("Candidate, pid:%s, name: %s cmdline: %s", str(proc.pid), str(proc.name()),
          #                    str(proc.cmdline()))
          for name in self.CHROME_PROCESS_NAMES:
            if name in proc.name():
              found = False
              for item in proc.cmdline():
                if key in item:
                  found = True
                  break
              if found:
                if self.logger:
                  self.logger.debug("Chrome process killing, pid:%s, cmdline: %s", str(proc.pid), str(proc.cmdline()))
                self.killProcess(proc.pid, self.CHROME_DIRS_TEMPLATE, self.DELAY_TERMINATE_AND_QUIT)
        except Exception, err:
          if self.logger:
            self.logger.debug("Chrome process kill error: %s", str(err))
    except Exception, err:
      if self.logger:
        self.logger.debug("Chrome process kill error: %s", str(err))


  def killProcess(self, pid, dirsTemplate=CHROME_DIRS_TEMPLATE, dirDeleteBeforeTimeout=DELAY_TERMINATE_AND_QUIT):
    del dirsTemplate, dirDeleteBeforeTimeout
    try:
      if self.logger:
        self.logger.debug("Try to Kill process pid: %s", str(pid))
        process = psutil.Process(pid)
        for proc in process.children(recursive=True):
          if self.logger:
            self.logger.debug("Killing child process pid: %s", str(proc.pid))
          try:
            # dirs = self.getProcessDirs(proc, dirsTemplate)
            proc.kill()
            # if self.logger:
            #  self.logger.debug("Dirs to remove: %s", str(dirs))
            # for d in dirs:
            #  time.sleep(dirDeleteBeforeTimeout)
              # self.removeTmpDirs(d)
            # os.kill(pid, signal.SIGKILL)
          except Exception, err:
            if self.logger:
              self.logger.debug("Child process pid: %s kill error: ", str(pid), str(err))
        if self.logger:
          self.logger.debug("Killing main process pid: %s", str(process.pid))
        # dirs = self.getProcessDirs(process, dirsTemplate)
        process.kill()
        # if self.logger:
        #  self.logger.debug("Dirs to remove: %s", str(dirs))
        # for d in dirs:
        #  time.sleep(dirDeleteBeforeTimeout)
          # self.removeTmpDirs(d)
        # os.kill(pid, signal.SIGKILL)
    except Exception, err:
      if self.logger:
        self.logger.debug("Process pid: %s kill error: %s", str(pid), str(err))


  # #check whether the fetcher have meta resource
  #
  # @return whether the fetcher have meta resource
  def should_have_meta_res(self):
    return True


  # #Get list of directories of files opened by process
  #
  # @param process - from the psutil.Process() or process.children()
  # @param dirsTemplate - template string for a path item
  # @return options object
  def getProcessDirs(self, process, dirsTemplate):
    ret = []

    for f in process.open_files():
      # if self.logger:
      #  self.logger.debug("Path candidate: %s", str(f.path))
      fp = f.path.split('/')
      fpr = ''
      templateFound = False
      for item in fp:
        fpr += '/' + item
        if dirsTemplate is not None and dirsTemplate != '' and dirsTemplate in item:
          templateFound = True
          break
      if templateFound or dirsTemplate is None or dirsTemplate == '':
        ret.append(fpr)

    return ret


  # #Create and returns the options object
  #
  # @param headers dictionary
  # @param proxies dictionary
  # @param url - requested URL
  # @return options object
  def getOptions(self, webdriver, headers, proxies, url):
    chrome_option = webdriver.ChromeOptions()

    arg_disable_http_cache = "--disable-http-cache"
    arg_clear_data_reduction_proxy_data_savings = '--clear-data-reduction-proxy-data-savings'
    arg_host_resolver_retry_attempts = '--host-resolver-retry-attempts=0'
    arg_start_maximized = '--start-maximized'
    if headers is not None and '--use-mobile-user-agent' in headers:
      use_mobile_user_agent = '--use-mobile-user-agent'
    else:
      use_mobile_user_agent = None

    if headers is not None and '--disable-web-security' in headers:
      disable_web_security = '--disable-web-security'
    else:
      disable_web_security = None
    # disable_web_security = '--disable-web-security'

    if headers is not None and '--enable-logging' in headers:
      enable_logging = '--enable-logging'
    else:
      enable_logging = None
    # enable_logging = '--enable-logging'

    if headers is not None and '--disable-gpu' in headers:
      disable_gpu = '--disable-gpu'
    else:
      disable_gpu = None
    # disable_gpu = '--disable-gpu'

    if headers is not None and '--allow-running-insecure-content' in headers:
      allow_running_insecure_content = '--allow-running-insecure-content'
    else:
      allow_running_insecure_content = None
    # allow_running_insecure_content = '--allow-running-insecure-content'

    if headers is not None and '--allow-file-access-from-files' in headers:
      allow_file_access_from_files = '--allow-file-access-from-files'
    else:
      allow_file_access_from_files = None
    # allow_file_access_from_files = '--allow-file-access-from-files'

    if headers is not None and '--proxy-bypass-list' in headers:
      arg_proxy_bypass_list = '--proxy-bypass-list=' + headers['--proxy-bypass-list']
    else:
      arg_proxy_bypass_list = None

    # if headers is not None and 'User-Agent' in headers and '--user-agent' in headers and\
    if headers is not None and 'User-Agent' in headers and\
      '--use-mobile-user-agent' not in headers:
      arg_user_agent = '--user-agent=' + headers['User-Agent']
    else:
      arg_user_agent = None
    if '--disk-cache-dir' in headers:
      if os.path.isdir(headers['--disk-cache-dir']):
        arg_disk_cache_dir = '--disk-cache-dir=' + headers['--disk-cache-dir']
      else:
        if self.logger:
          self.logger.debug("Header `--disk-cache-dir` directory: `%s` not found!", headers['--disk-cache-dir'])
    else:
      arg_disk_cache_dir = None
    if '--profile-directory' in headers:
      if os.path.isdir(headers['--profile-directory']):
        arg_profile_directory = '--profile-directory=' + headers['--profile-directory']
      else:
        if self.logger:
          self.logger.debug("Header `--profile-directory` directory: `%s` not found!", headers['--profile-directory'])
    else:
      arg_profile_directory = None
    if '--user-data-dir' in headers:
      if os.path.isdir(headers['--user-data-dir']):
        arg_user_data_dir = '--user-data-dir=' + headers['--user-data-dir']
        self.userDataDirUsed = headers['--user-data-dir']
      else:
        if self.logger:
          self.logger.debug("Header `--user-data-dir` directory: `%s` not found!", headers['--user-data-dir'])
    else:
      if self.tmpDir != '':
        arg_user_data_dir = '--user-data-dir=' + self.tmpDir
        self.userDataDirUsed = self.tmpDir
      else:
        arg_user_data_dir = None
        if self.logger:
          self.logger.error("Empty tmp dir configured!")

    if self.userDataDirUsed != '' and not os.path.isdir(self.userDataDirUsed):
      if self.logger:
        self.logger.debug("Profile archive user data dir `%s` not found, trying to create...",
                          str(self.userDataDirUsed))
      try:
        os.makedirs(self.userDataDirUsed)
      except Exception, err:
        if self.logger:
          self.logger.debug("Profile archive user data dir creation error: %s", str(err))
      if os.path.isdir(self.userDataDirUsed):
        if self.logger:
          self.logger.debug("Profile archive user data dir `%s` created", str(self.userDataDirUsed))

    if '--user-data-dir-zip' in headers and self.userDataDirUsed != '' and os.path.isdir(self.userDataDirUsed):
      try:
        profiles = [p.strip() for p in headers['--user-data-dir-zip'].split(',') if p.strip() != '']
        if '--user-data-dir-zip-rotation' in headers and headers['--user-data-dir-zip-rotation'] is not None and\
          headers['--user-data-dir-zip-rotation'] != '':
          rotationType = int(headers['--user-data-dir-zip'])
        else:
          rotationType = 0
        profileIndex = 0
        if len(profiles) > 1:
          if rotationType == 0:
            r = [randint(0, len(profiles) - 1) for p in range(0, len(profiles) - 1)]
            profileIndex = r[0]
          elif rotationType == 1:
            pass
          elif rotationType == 2:
            pass
#         os.system('unzip -qq ' + profiles[profileIndex] + ' -d ' + self.userDataDirUsed)
#         os.system('mv ' + self.userDataDirUsed + '/' + \
#                   os.path.splitext(os.path.basename(profiles[profileIndex]))[0] + \
#                   '/* ' + self.userDataDirUsed)

        res = Utils.executeCommand('unzip -qq ' + profiles[profileIndex] + ' -d ' + self.userDataDirUsed)
        if res.exitCode != APP_CONSTS.EXIT_SUCCESS:
          raise Exception(str(res.stderr))

        res = Utils.executeCommand('mv ' + self.userDataDirUsed + '/' + \
                  os.path.splitext(os.path.basename(profiles[profileIndex]))[0] + \
                  '/* ' + self.userDataDirUsed)
        if res.exitCode != APP_CONSTS.EXIT_SUCCESS:
          raise Exception(str(res.stderr))

        if self.logger:
          self.logger.debug("Profile archive `%s` extracted to `%s` directory, rotation: %s",
                            profiles[profileIndex], self.userDataDirUsed, str(rotationType))
      except Exception, err:
#         if self.logger:
#           self.logger.error("Profile archive extraction error: %s", str(err))
        raise Exception("Profile archive extraction error: %s" % str(err))

    else:
      d = {'--user-data-dir-zip in headers':str('--user-data-dir-zip' in headers),
           'self.userDataDirUsed':self.userDataDirUsed,
           'os.path.isdir(self.userDataDirUsed)':str(os.path.isdir(self.userDataDirUsed))}
      if self.logger:
        self.logger.debug("Profile archive not used, condition data:\n%s", str(d))

    arg_dns_prefetch_disable = '--dns-prefetch-disable'
    # --disk-cache-size=1
    # --media-cache-size=1
    # --safe-plugins

    if headers is not None and '--disable-setuid-sandbox' in headers:
      chrome_option.add_argument('--disable-setuid-sandbox')

    if headers is not None and '--no-sandbox' in headers:
      chrome_option.add_argument('--no-sandbox')

    if headers is not None and '--incognito' in headers:
      chrome_option.add_argument('--incognito')

    # chrome_option.add_argument('--enable-logging')
    # chrome_option.add_argument('--v=1')
    # chrome_option.add_argument('--log-level=0')

    if arg_user_agent is not None:
      chrome_option.add_argument(arg_user_agent)
    if use_mobile_user_agent is not None:
      chrome_option.add_argument(use_mobile_user_agent)
    if disable_web_security is not None:
      chrome_option.add_argument(disable_web_security)
    if enable_logging is not None:
      chrome_option.add_argument(enable_logging)
    if disable_gpu is not None:
      chrome_option.add_argument(disable_gpu)
    if allow_running_insecure_content is not None:
      chrome_option.add_argument(allow_running_insecure_content)
    if allow_file_access_from_files is not None:
      chrome_option.add_argument(allow_file_access_from_files)
    if arg_proxy_bypass_list is not None:
      chrome_option.add_argument(arg_proxy_bypass_list)
    chrome_option.add_argument(arg_disable_http_cache)
    chrome_option.add_argument(arg_clear_data_reduction_proxy_data_savings)
    chrome_option.add_argument(arg_host_resolver_retry_attempts)
    chrome_option.add_argument(arg_start_maximized)
    if arg_disk_cache_dir is not None and arg_disk_cache_dir != '':
      chrome_option.add_argument(arg_disk_cache_dir)
    if arg_profile_directory is not None and arg_profile_directory != '':
      chrome_option.add_argument(arg_profile_directory)
    if arg_user_data_dir is not None and arg_user_data_dir != '':
      chrome_option.add_argument(arg_user_data_dir)
    chrome_option.add_argument(arg_dns_prefetch_disable)
    # chrome_option.add_argument(arg_incognito)

    if self.sessionId != '':
      chrome_option.add_argument(self.sessionId)

    # Proxy options
    if proxies is not None:
      proxy_type, proxy_host, proxy_port, proxy_user, proxy_passwd = proxies
      if self.logger:
        self.logger.debug("Proxy used from argument tuple: %s", str(proxies))
      if proxy_user:
        proxies = proxy_type + "://%s:%s@%s:%s" % (proxy_user, proxy_passwd, proxy_host, proxy_port)
      else:
        proxies = proxy_type + "://%s:%s" % (proxy_host, proxy_port)
      chrome_option.add_argument("--proxy-server=" + proxies)
    else:
      if '--proxy-http' in headers and headers['--proxy-http'] is not None and headers['--proxy-http'] != '':
        if '--proxy-http-domains' in headers and headers['--proxy-http-domains'] is not None and\
          headers['--proxy-http-domains'] != '':
          dn = self.getDomainNameFromURL(url)
          domain = bool(dn in headers['--proxy-http-domains'].split(','))
          if self.logger and domain is False:
            self.logger.debug("Proxy not used because domain `%s` not listed in `--proxy-http-domains`", str(dn))
        else:
          domain = True
        if domain:
          p = headers['--proxy-http'].replace('%3A', ':')
          if self.logger:
            self.logger.debug("Proxy used from header: %s", str(p))
          chrome_option.add_argument("--proxy-server=" + p)

    return chrome_option


  # #Initializes tmp dir for browser data from headers or default /tmp/dfetcher_tmp_<pid>
  #
  # @param macro structure object
  # @param driver object
  # @return True if directories are created or False if error
  def initializeTmpDirs(self, headers):
    ret = True

    if self.tmpDir != '':
      try:
        if headers is not None and 'tmp-dir' in headers:
          self.tmpDir = headers['tmp-dir']
        if self.tmpDirRemoveBeforeCreate:
          self.removeTmpDirs()
        if not os.path.isdir(self.tmpDir):
          if logger is not None:
            self.logger.debug("Create temporary directory: %s", str(self.tmpDir))
          os.makedirs(self.tmpDir)
      except Exception, err:
        if self.logger is not None:
          ret = False
          if logger is not None:
            self.logger.debug("Error temporary directories initialization: %s", str(err))

      if os.path.isdir(self.tmpDir):
        ret = True

    return ret


  # #Remove tmp dir
  #
  def removeTmpDirs(self, delay=DELAY_TERMINATE_AND_QUIT, tries=3):
    if self.tmpDir != '':
      for i in xrange(1, tries):
        try:
          time.sleep(delay)
          if os.path.isdir(self.tmpDir):
            if self.logger is not None:
              self.logger.debug("Removing tmp dir: %s, try: %s", self.tmpDir, str(i))
            shutil.rmtree(self.tmpDir)
          else:
            break
        except Exception, err:
          if self.logger is not None:
            self.logger.debug("Remove tmp dir: %s, try: %s, error: %s", self.tmpDir, str(i), str(err))


  # #Execute macro with simple object structure
  #
  # @param macro structure object
  # @return result dict()
  def execMacroSimple(self, macro):
    def executeMacro(m):
      error_code = 0
      error_msg = u''
      try:
        r = self.driver.execute_script(m)
        if self.logger is not None:
          self.logger.debug("Macro returned: %s", json.dumps(r))
      except Exception, err:
        error_msg = 'Error macro execution: ' + str(err) + '; logs: ' + self.getAllLogsAsString()
        error_code = self.ERROR_MACRO_RETURN_VALUE
        if self.logger is not None:
          self.logger.debug(error_msg)
      return r, error_code, error_msg

    macroResults = []
    error_code = 0
    error_msg = u''
    macroCounter = 0
    maxLenToLog = 512

    for m in macro:
      if self.logger is not None:
        self.logger.debug("Macro #%s in set of %s items:\n%s...",
                          str(macroCounter), str(len(macro)), str(m)[:maxLenToLog])
      macroCounter += 1
      if m.isdigit():
        if self.logger is not None:
          self.logger.debug("Macro sleep: %s sec", str(m))
        time.sleep(int(m))
      elif m.startswith(u'^'):
        kInputItems = m[1:].split(u'\t')
        if len(kInputItems) > 1:
          if self.logger is not None:
            self.logger.debug(u'Keyboard input macro items: %s', str(kInputItems))
          for kInputItemIndex in xrange(len(kInputItems) - 1):
            try:
              itemSelector = self.driver.find_element_by_xpath(kInputItems[kInputItemIndex])
              itemString = kInputItems[kInputItemIndex + 1]
              if itemString == u'':
                itemSelector.clear()
              else:
                itemSelector.send_keys(itemString)
            except Exception, err:
              if self.logger is not None:
                self.logger.debug(u'Warning, selector `%s` usage: %s', kInputItems[kInputItemIndex], str(err))
      else:
        iType = 0
        iDelay = 0
        iMaxIterations = 1
        iEnvCheckIteration = 0
        iEnvCheckMacro = u''
        if m.startswith('!'):
          m = m[1:]
          iType = 1
          params = m.split(':')
          if len(params) > 3:
            iDelay = int(params[0])
            iMaxIterations = int(params[1])
            m = params[2]
            iEnvCheckIteration = int(params[3])
            iEnvCheckMacro = params[4]
          elif len(params) > 2:
            iDelay = int(params[0])
            iMaxIterations = int(params[1])
            m = params[2]
          elif len(params) > 1:
            iDelay = int(params[0])
            m = params[1]
          elif len(params) == 1:
            m = params[0]
          if self.logger is not None:
            self.logger.debug("Macro blocking iterative, delay: %s, max ierations: %s", str(iDelay), str(iMaxIterations))
        for i in xrange(0, iMaxIterations):
          if iType == 1:
            if self.logger is not None:
              self.logger.debug("Macro blocking iteration: %s of: %s", str(i + 1), str(iMaxIterations))
            if iEnvCheckIteration != -1 and i == iEnvCheckIteration and iEnvCheckMacro != u'':
              if self.logger is not None:
                self.logger.debug("Macro blocking iteration: %s, execute an environment check macro: %s", str(i + 1), str(iEnvCheckMacro))
              r, error_code, error_msg = executeMacro(iEnvCheckMacro)
              if error_code > 0:
                if self.logger is not None:
                  self.logger.debug("Macro blocking iteration: %s, an environment check macro execution error, loop aborted!", str(i + 1))
                r = None
                break
              else:
                if r is True:
                  if self.logger is not None:
                    self.logger.debug("Macro blocking iteration: %s, an environment check passed!", str(i + 1))
                elif r is not True:
                  if self.logger is not None:
                    self.logger.debug("Macro blocking iteration: %s, an environment check fault, loop aborted!", str(i + 1))
                  r = None
                  break
          if m.startswith('http://') or m.startswith('https://') or m.startswith('file://'):
            try:
              if m.startswith('file://'):
                with open(m[7:].replace('%PID%', str(os.getpid())), 'r') as f:
                  m = f.read()
              else:
                r = requests.get(m.replace('%PID%', str(os.getpid())))
                m = r.text
              if self.logger is not None:
                self.logger.debug("Macro %s bytes loaded:\n%s...", str(len(str(m))), str(m)[:maxLenToLog])
            except Exception, err:
              error_msg = 'Error load macro code, URL: `' + str(m) + '` : ' + str(err)
              error_code = self.ERROR_MACRO_RETURN_VALUE
              if self.logger is not None:
                self.logger.debug(error_msg)
              r = None
              break
          r, error_code, error_msg = executeMacro(m)
          if error_code > 0:
            r = None
            break
          if iType == 0 and r is not None:
            if isinstance(r, (basestring, list, dict)):
              macroResults.append(r)
              if isinstance(r, (list, dict)):
                if self.logger is not None:
                  self.logger.debug("Macro items returned: %s", str(len(r)))
            else:
              error_msg = 'Error macro result value, type is: ' + str(type(r))
              error_code = self.ERROR_MACRO_RETURN_VALUE
              if self.logger is not None:
                self.logger.debug(error_msg)
              break
          elif iType == 1:
            if r is True:
              if self.logger is not None:
                self.logger.debug("Macro blocking got `True` on iteration: %s, sleeped: %s sec", str(i + 1), str(int(iDelay) * i))
              break
            elif r is not True and iDelay > 0:
              if self.logger is not None:
                self.logger.debug("Macro blocking iteration: %s sleep on: %s sec", str(i + 1), str(iDelay))
              time.sleep(int(iDelay))
        if iType == 1 and r is not True:
          if self.logger is not None:
            self.logger.debug("Macro blocking finished, but no `True` value returned!")
        if error_code > 0:
          break

    return macroResults, error_code, error_msg


  # #Get all kind of logs as string
  #
  # @return string of logs lists
  def getAllLogsAsString(self):
    return 'browser: ' + str(self.driver.get_log('browser')) + '; driver: ' + str(self.driver.get_log('driver'))


  # #Execute macro with extended object structure
  #
  # @param macro structure object
  # @return result dict()
  def execMacroExtended(self, macro):
    macroResults = []
    error_code = 0
    error_msg = ''
    content_type = None
    result_type = self.MACRO_RESULT_TYPE_DEFAULT

    for mset in macro['sets']:
      if 'name' not in mset:
        mset['name'] = ''
      if 'repeat' not in mset:
        mset['repeat'] = '1'
      if 'delay' not in mset:
        mset['delay'] = '0'
      if self.logger is not None:
        self.logger.debug("Set:\n%s", str(mset))
      for i in xrange(0, int(mset['repeat'])):
        if int(mset['delay']) > 0:
          time.sleep(int(mset['delay']))
        if self.logger is not None:
          self.logger.debug("Macro %s in set", str(i))
        r, error_code, error_msg = self.execMacroSimple(mset['items'])
        if error_code > 0:
          break
        macroResults += r
      if error_code > 0:
        break

    if 'result_type' in macro:
      result_type = int(macro['result_type'])
    self.logger.debug("Macro results type: %s", str(result_type))
    if 'result_content_type' in macro:
      content_type = str(macro['result_content_type'])
    self.logger.debug("Macro results content type: %s", str(content_type))

    if result_type == self.MACRO_RESULT_TYPE_AUTO:
      self.logger.debug("Macro results before autodetect type: %s", str(macroResults))
      for r in macroResults:
        if isinstance(r, basestring):
          result_type = self.MACRO_RESULT_TYPE_CONTENT
          self.logger.debug("Macro results type autodetected as string content")
          break
        elif isinstance(r, list):
          for ri in r:
            if isinstance(ri, basestring):
              result_type = self.MACRO_RESULT_TYPE_URLS_LIST
              self.logger.debug("Macro results type autodetected as URLs list")
              break
      if result_type == self.MACRO_RESULT_TYPE_CONTENT:
        macroResults = ''.join(macroResults)
      if result_type == self.MACRO_RESULT_TYPE_URLS_LIST:
        macroResults = [item for sublist in macroResults for item in sublist]
      self.logger.debug("Macro results after autodetect type: %s", str(macroResults))

    return macroResults, error_code, error_msg, content_type, result_type



# # external Fetcher
#
#

# # urllib Fetcher
#
#
class URLLibFetcher(BaseFetcher):
  
  # # Initialization
  #
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  def __init__(self, fetcherPostObj=None):
    super(URLLibFetcher, self).__init__(fetcherPostObj)
    
  
  # #fetch a url, and return the response
  #
  # @param url, the url to fetch
  # @param method, fetch HTTP method
  # @param headers, request headers dict
  # @param timeout, request timeout(seconds)
  # @param allow_redirects, should follow redirect
  # @param proxies, proxy setting
  # @param auth, basic auth setting
  # @param data, post data, used only when method is post
  # @return Response object
  def open(self, url, **kwargs):
    import urllib2

    if 'logger' in kwargs['logger']:
      log = kwargs['logger']
    else:
      log = logger
    allowed_content_types = kwargs['allowed_content_types']
    # max_resource_size = kwargs["max_resource_size"]

    res = Response()
    log.debug("url: <%s>", url)
    response = None
    try:
      response = urllib2.urlopen(url)
      headers_info = response.info()
      if headers_info is not None:
        if headers_info.type in allowed_content_types:
          if response is not None:
            # res.encoding = impl_res.encoding
            # res.cookies = requests.utils.dict_from_cookiejar(impl_res.cookies)
            res.url = response.geturl()
            res.status_code = response.getcode()
            content_response = response.read()
            res.unicode_content = content_response
            res.str_content = content_response
            res.rendered_unicode_content = content_response
            res.content_size = len(content_response)
            headers = {}
            headers["content-length"] = res.content_size
            headers["content-type"] = headers_info.type
            res.headers = headers
            history = []
            res.redirects = history
          else:
            log.debug("URLLib return empty response.")
        else:
          log.debug("Content-Type not allowed. headers_info.type: %s", str(headers_info.type))
      else:
        log.debug("URLLib info is empty.")
    except urllib2.HTTPError, err:
    # except Exception, err:
      log.debug("Exception <%s>", str(err.code))

    # fetcher post processing if necessary
    if self.fetcherPostObj is not None:
      self.fetcherPostObj.process(res)

    return res


# # external Fetcher
#
#
class ContentFetcher(BaseFetcher):

  # # Initialization
  #
  # @param fetcherPostObj - fetcher post instance if necessary post processing  or None as default
  def __init__(self, fetcherPostObj=None):
    super(ContentFetcher, self).__init__(fetcherPostObj)


  # #fetch a url, and return the response
  #
  # @param url, the url to fetch
  # @param method, fetch HTTP method
  # @param headers, request headers dict
  # @param timeout, request timeout(seconds)
  # @param allow_redirects, should follow redirect
  # @param proxies, proxy setting
  # @param auth, basic auth setting
  # @param data, post data, used only when method is post
  # @return Response object
  def open(self, url, **kwargs):
    try:
      localBuf = base64.b64decode(kwargs["inputContent"])
    except TypeError:
      localBuf = kwargs["inputContent"]
    res = Response()
    res.content_size = len(localBuf)
    res.headers = {}
    res.redirects = []
    res.status_code = 200
    res.url = url
    res.encoding = SimpleCharsetDetector().detect(localBuf)
    if res.encoding is None:
      res.encoding = "utf-8"
    res.unicode_content = localBuf
    res.str_content = localBuf
    res.rendered_unicode_content = localBuf

    # fetcher post processing if necessary
    if self.fetcherPostObj is not None:
      self.fetcherPostObj.process(res)

    return res


# #The Response class
# represents an web page response
class Response(object):
  def __init__(self):
    # final url
    self.url = None
    # http status code
    self.status_code = 0
    # redirect lists
    self.redirects = None
    # unicode content
    self.unicode_content = None
    # str content
    self.str_content = None
    # rendered(by command line browser) unicode content
    self.rendered_unicode_content = None
    # http response content size
    self.content_size = None
    # content encoding
    self.encoding = None
    # headers
    self.headers = None
    # meta resource
    self.meta_res = None
    # cookies
    self.cookies = None
    # dynamic fetcher type
    self.dynamic_fetcher_type = None
    # dynamic fetcher result type, see the macro definition specification
    self.dynamic_fetcher_result_type = None
    # error mask from fetcher
    self.error_mask = APP_CONSTS.ERROR_OK
    # request
    self.request = None
    # execution time
    self.time = 0
    self.error_msg = ''
    self.page_source = None



# #The Response class
# represents an web page response
class SimpleCharsetDetector(object):


  def __init__(self, content=None):
    # content
    self.content = content

  def detect(self, content=None, contentType="html"):
    ret = None

    if content is None:
      cnt = self.content
    else:
      cnt = content

    try:
      if contentType == 'html':
        pattern = r'<meta(?!\s*(?:name|value)\s*=)(?:[^>]*?content\s*=[\s"\']*)?([^>]*?)[\s"\';]*charset\s*=[\s"\']*([^\s"\'/>]*)'  #  pylint: disable=C0301
        matchObj = re.search(pattern, cnt, re.I | re.M | re.S)
        if matchObj:
          ret = matchObj.group(2)
      elif contentType == 'xml':
        ret = self.xmlCharsetDetector(None, cnt)

    except Exception, err:
      logger.error("Exception: %s", str(err))

    if ret is not None and ret in CONSTS.charsetDetectorMap:
      logger.debug("Extracted wrong encoding '%s' from page replace to correct '%s'", ret,
                   CONSTS.charsetDetectorMap[ret])
      ret = CONSTS.charsetDetectorMap[ret]

    return ret


  def xmlCharsetDetector(self, fp, buff=None):
    """ Attempts to detect the character encoding of the xml file
    given by a file object fp. fp must not be a codec wrapped file
    object!

    The return value can be:
        - if detection of the BOM succeeds, the codec name of the
        corresponding unicode charset is returned

        - if BOM detection fails, the xml declaration is searched for
        the encoding attribute and its value returned. the "<"
        character has to be the very first in the file then (it's xml
        standard after all).

        - if BOM and xml declaration fail, None is returned. According
        to xml 1.0 it should be utf_8 then, but it wasn't detected by
        the means offered here. at least one can be pretty sure that a
        character coding including most of ASCII is used :-/
    """
    # ## detection using BOM

    # # the BOMs we know, by their pattern
    bomDict = {  # bytepattern : name
        (0x00, 0x00, 0xFE, 0xFF) : "utf_32_be",
        (0xFF, 0xFE, 0x00, 0x00) : "utf_32_le",
        (0xFE, 0xFF, None, None) : "utf_16_be",
        (0xFF, 0xFE, None, None) : "utf_16_le",
        (0xEF, 0xBB, 0xBF, None) : "utf_8",
        }

    if fp is not None:
      # # go to beginning of file and get the first 4 bytes
      oldFP = fp.tell()
      fp.seek(0)
      (byte1, byte2, byte3, byte4) = tuple(map(ord, fp.read(4)))

      # # try bom detection using 4 bytes, 3 bytes, or 2 bytes
      bomDetection = bomDict.get((byte1, byte2, byte3, byte4))
      if not bomDetection:
        bomDetection = bomDict.get((byte1, byte2, byte3, None))
        if not bomDetection:
          bomDetection = bomDict.get((byte1, byte2, None, None))

      # # if BOM detected, we're done :-)
      if bomDetection:
        fp.seek(oldFP)
        return bomDetection

      # # still here? BOM detection failed.
      # #  now that BOM detection has failed we assume one byte character
      # #  encoding behaving ASCII - of course one could think of nice
      # #  algorithms further investigating on that matter, but I won't for now.

      # # assume xml declaration fits into the first 2 KB (*cough*)
      fp.seek(0)
      buff = fp.read(2048)

    # # set up regular expression
    xmlDeclPattern = r"""
    ^<\?xml             # w/o BOM, xmldecl starts with <?xml at the first byte
    .+?                 # some chars (version info), matched minimal
    encoding=           # encoding attribute begins
    ["']                # attribute start delimiter
    (?P<encstr>         # what's matched in the brackets will be named encstr
     [^"']+              # every character not delimiter (not overly exact!)
    )                   # closes the brackets pair for the named group
    ["']                # attribute end delimiter
    .*?                 # some chars optionally (standalone decl or whitespace)
    \?>                 # xmldecl end
    """

    xmlDeclRE = re.compile(xmlDeclPattern, re.VERBOSE)

    # # search and extract encoding string
    match = xmlDeclRE.search(buff)
    if fp is not None:
      fp.seek(oldFP)
    if match:
      return match.group("encstr")
    else:
      return None
