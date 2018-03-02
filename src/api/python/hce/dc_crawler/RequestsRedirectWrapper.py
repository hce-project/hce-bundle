# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
RequestsRedirectWrapper Class content main functional for resolve redirect.

@package: dc_crawler
@file RequestsRedirectWrapper.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""
import copy
import requests.exceptions
import requests.packages
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from app.Filters import Filters
from app.Utils import varDump
from app.Utils import getTracebackInfo
import app.Utils as Utils  # pylint: disable=F0401
import dc_crawler.Constants as CONSTS
from dc_crawler.Exceptions import CrawlerFilterException
from dc_crawler.HTTPCookieResolver import HTTPCookieResolver

logger = Utils.MPLogger().getLogger()


class RequestsRedirectWrapper(object):
  # Constants used in class
  REQUEST_COOKIE_HEADER_NAME = 'Cookie'
  RESPONSE_COOKIE_HEADER_NAME = 'set-cookie'
  REFERER_HEADER_NAME = 'Referer'

  # Usage algorithm constants
  USAGE_ALGORITHM_BASE = 0
  USAGE_ALGORITHM_CUSTOM = 1
  DEFAULT_USAGE_ALGORITHM = USAGE_ALGORITHM_BASE

  # Constants of error messages
  ERROR_BAD_STATUS_CODE_VALUE = "Not allowed status code '%s'. Allowed list: %s"

  # Constructor
  def __init__(self, dbWrapper=None, siteId=None, usageAlgorithm=DEFAULT_USAGE_ALGORITHM, redirectCodes=None):
    object.__init__(self)
    self.dbWrapper = dbWrapper
    self.siteId = siteId
    self.usageAlgorithm = usageAlgorithm
    self.redirectCodes = CONSTS.REDIRECT_HTTP_CODES if not isinstance(redirectCodes, list) else redirectCodes


  # @param url - the url to fetch
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param headers - request headers dict
  # @param allowRedirects - boolean flag allowed redirects
  # @param proxySetting - proxy setting
  # @param auth - basic auth setting, tuple of name and password
  # @param data - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @param filters - filters dict
  # @return Response object
  def request(self, url, method, timeout, headers, allowRedirects, proxySetting, auth, data, maxRedirects, filters):
    # variable for return
    implRes = None

    if self.usageAlgorithm == self.USAGE_ALGORITHM_BASE:
      try:
        implRes = self.requestBase(url, method, timeout, headers, allowRedirects, proxySetting,
                                   auth, data, maxRedirects, filters)
      except CrawlerFilterException, err:
        raise err
      except Exception:
        logger.debug("!!! Hard case. Don't worry. We will try using more complexity way...")
        implRes = self.requestBase(url, 'head', timeout, headers, allowRedirects, proxySetting,
                                   auth, data, maxRedirects, filters)
        if implRes is not None:
          logger.debug("!!! implRes.headers: %s", varDump(implRes.headers))
          implRes = self.requestBase(url, method, timeout, implRes.headers, allowRedirects, proxySetting,
                                     auth, data, maxRedirects, filters)

    elif self.usageAlgorithm == self.USAGE_ALGORITHM_CUSTOM:
      implRes = self.requestCustom(url, method, timeout, headers, allowRedirects, proxySetting, auth, data,
                                   maxRedirects, filters)

    else:
      raise Exception("Try using not support algorithm usage of 'requests' =  %s" % (str(self.usageAlgorithm)))

    return implRes


  # @param url - the url to fetch
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param headers - request headers dict
  # @param allowRedirects - boolean flag allowed redirects
  # @param proxySetting - proxy setting
  # @param auth - basic auth setting, tuple of name and password
  # @param data - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @param filters - filters dict
  # @return Response object
  def requestBase(self, url, method, timeout, headers, allowRedirects, proxySetting, auth, data, maxRedirects, filters):
    # variable for return
    res = None
    try:
      req = requests.Request(method=method,
                             url=url,
                             headers=headers,
                             auth=auth,
                             data=data,
                             hooks={'response':[RequestsRedirectWrapper.checkRedirect]})

      logger.debug("!!! headers: %s, type: %s", varDump(headers), str(type(headers)))

      if self.REFERER_HEADER_NAME in headers:
        del headers[self.REFERER_HEADER_NAME]

      reqv = req.prepare()

      rSession = requests.Session()
      rSession.max_redirects = int(maxRedirects)
      rSession.stream = True
      rSession.verify = False  # don't verify ssl
      rSession.proxies = proxySetting
      res = rSession.send(request=reqv, allow_redirects=allowRedirects, timeout=timeout)

      self.__checkResponse(res, filters)

      logger.debug("!!! res.cookies: %s, type: %s", varDump(res.cookies), str(type(res.cookies)))
      cookies = requests.utils.dict_from_cookiejar(res.cookies)
      logger.debug("!!! cookies: %s, type: %s", varDump(cookies), str(type(cookies)))
      if len(cookies) > 0:
        cookiesList = [key + '=' + value for key, value in cookies.items()]
        cookie = ''
        if self.REQUEST_COOKIE_HEADER_NAME in headers:
          cookie = headers[self.REQUEST_COOKIE_HEADER_NAME]
        headers[self.REQUEST_COOKIE_HEADER_NAME] = cookie + (';'.join(cookiesList))
        logger.debug("!!! headers updated by 'cookies': %s", varDump(headers))

    except requests.exceptions.TooManyRedirects, err:
      raise err
    except CrawlerFilterException, err:
      raise err
    except Exception, err:
      logger.debug("!!! We have a problem: %s", str(err))
      logger.info(getTracebackInfo())
      raise err

#     logger.debug("!!! url: %s", str(url))
#     logger.debug("!!! status_code: %s, method: %s, res.request.url: %s", str(res.status_code), str(method),
#                  str(res.request.url))

    return res


  # #Check allowed Response object
  # # if check not passed will be raise exception
  #
  # @param res - Response object
  # @param filters - filters dict
  # @return - None
  def __checkResponse(self, res, filters):

    logger.debug("!!! res.url: %s", varDump(res.url))
    if not self.__isAllowedUrl(res.url, filters):
      raise CrawlerFilterException("Url %s not passed filter" % str(res.url))

    for history in res.history:
      logger.debug("!!! history.url: %s", varDump(history.url))
      logger.debug("!!! history.status_code: %s", varDump(history.status_code))
      if not self.__isAllowedUrl(history.url, filters):
        raise CrawlerFilterException("Url %s not passed filter" % str(history.url))

    if isinstance(self.redirectCodes, list):
      for history in res.history:
        if history.status_code not in self.redirectCodes:
          raise requests.exceptions.TooManyRedirects(self.ERROR_BAD_STATUS_CODE_VALUE % \
                                                     (str(history.status_code), str(self.redirectCodes)))


  # @param url - the url to fetch
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param headers - request headers dict
  # @param allowRedirects - boolean flag allowed redirects
  # @param proxySetting - proxy setting
  # @param auth - basic auth setting, tuple of name and password
  # @param data - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @param filters - filters dict
  # @return Response object
  def requestCustom(self, url, method, timeout, headers, allowRedirects, proxySetting, auth, data, maxRedirects,
                    filters):
    # variable for return
    implRes = None
    applyHeaders = copy.deepcopy(headers)
    # logger.debug("!!! request enter ...  applyHeaders: %s", varDump(applyHeaders))

    cookieResolver = HTTPCookieResolver()
    redirectsCount = 0

    while redirectsCount < int(maxRedirects):
      implRes, localUrl = self.__sendRequest(url, method, timeout, applyHeaders, proxySetting, \
                                           auth, data, maxRedirects)

      logger.debug("!!! implRes.status_code = %s", str(implRes.status_code))
      # logger.debug("!!! implRes.headers: %s", str(implRes.headers))
      # logger.debug("!!! implRes.cookies: %s, type: %s", str(implRes.cookies), str(type(implRes.cookies)))
      # logger.debug("!!! implRes: %s, type: %s", varDump(implRes, maxDepth=10), str(type(implRes)))

      self.__saveCookies(url, implRes, cookieResolver)

      # logger.debug("!!! cookieResolver: %s", varDump(cookieResolver))

      if redirectsCount > 0:
        if not self.__isAllowedUrl(localUrl, filters):
          raise CrawlerFilterException("Url %s not passed filter" % str(localUrl))

      redirectsCount += 1
      logger.debug("!!! redirectsCount = %s, maxRedirects = %s", str(redirectsCount), str(maxRedirects))

      # remove referer and other fields from header
      applyHeaders = self.updateHeaderFields(applyHeaders)
      logger.debug("!!!>>> applyHeaders: %s", varDump(applyHeaders))

      applyHeaders = self.updateHeadersByCookies(applyHeaders, localUrl, cookieResolver)
      url = localUrl

      if implRes.status_code not in self.redirectCodes or not allowRedirects:
        logger.debug("!!! break !!!")
        break

    if implRes.status_code in self.redirectCodes:
      raise requests.exceptions.TooManyRedirects('Exceeded %s redirects.' % str(maxRedirects))

    return implRes


  # # Send request
  #
  # @param url - the next url to fetch
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param headers - request headers dict
  # @param proxySetting - proxy setting
  # @param auth - basic auth setting, tuple of name and password
  # @param data - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @return response object
  def __sendRequest(self, url, method, timeout, headers, proxySetting, auth, data, maxRedirects):

    logger.debug("!!! request arguments: " + str((url, timeout, headers, proxySetting, auth, data)))
    logger.debug("!!! send request to url: %s", str(url))

    rSession = requests.Session()
    rSession.max_redirects = int(maxRedirects)
    methodFunc = rSession.__getattribute__(method)

    implRes = methodFunc(url,
                         timeout=timeout,
                         headers=headers,
                         allow_redirects=False,
                         proxies=proxySetting,
                         auth=auth,
                         data=data,
                         stream=True,
                         verify=False,  # don't verify ssl
                         # hooks={'response':[RequestsRedirectWrapper.checkRedirectMax(handler=self)]}) # reserved
                         hooks={'response':[RequestsRedirectWrapper.checkRedirect]})

    redirect = None
    redirectUrl = url
    for redirect in rSession.resolve_redirects(implRes, implRes.request):
      redirectUrl = redirect.url
      break

    if redirect is not None:
      implRes = redirect

    implRes.url = redirectUrl
    logger.debug("!!! redirect.url: %s", str(redirectUrl))

    return implRes, redirectUrl


  # # update headers fields
  #
  # @param headers - request headers dict
  # @return headers - result headers alredy updated
  @staticmethod
  def updateHeaderFields(headers):
    cid = requests.structures.CaseInsensitiveDict(headers)
    for name in CONSTS.REDIRECT_HEADER_FIELDS_FOR_REMOVE:
      for key, value in cid.lower_items():  # pylint: disable=W0612
        # logger.debug("!!! key: %s, value: %s", str(key), str(value))
        if key.lower() == name.lower():
          del cid[name]
    headers = dict(cid.lower_items())

    return headers


  # # check allowed url by filter
  #
  # @param url - url for check
  # @param inputFilters - filters dict
  # @return - True if allowed by filter or othrwise False
  def __isAllowedUrl(self, url, inputFilters=None):
    # variable for result
    ret = True

    if self.dbWrapper is not None and self.siteId is not None and inputFilters is not None:
#       # Create class Filters instance for check 'redirect' use regular expressions
#       localFilters = Filters(filters=inputFilters,
#                              dbTaskWrapper=self.dbWrapper,
#                              siteId=self.siteId,
#                              readMode=0,
#                              fields=None,
#                              opCode=Filters.OC_RE,
#                              stage=None)  # Filters.STAGE_REDIRECT_URL)
#
# #       logger.debug('!!! localFilters.filters: ' + varDump(localFilters.filters))
#
#       isExistStageRedirectUrl = localFilters.isExistStage(Filters.STAGE_REDIRECT_URL)
#       isExistStageAll = localFilters.isExistStage(Filters.STAGE_ALL)
#
#       logger.debug("!!! isExistStage('STAGE_REDIRECT_URL'): %s", str(isExistStageRedirectUrl))
#       logger.debug("!!! isExistStage('STAGE_ALL'): %s", str(isExistStageAll))
# #
# #       logger.debug('!!! inputFilters: ' + varDump(inputFilters))

      # Check redirect url use regular expression
      from dc_crawler.CollectURLs import CollectURLs

      filters = copy.deepcopy(inputFilters)
      if filters is not None:
        for inputFilter in filters:
          if inputFilter.stage == Filters.STAGE_ALL or inputFilter.stage == Filters.STAGE_REDIRECT_URL:
            inputFilter.stage = Filters.STAGE_COLLECT_URLS

      ret = CollectURLs.filtersApply(filters, url, 0, None, 0, None, Filters.OC_RE, Filters.STAGE_COLLECT_URLS)

    return ret


#   # # save cookies
#   #
#   # @param url - url string
#   # @param headers - request headers dict
#   # @param cookieResolver - cookie resolver instance
#   # @return - None
#   def __saveCookies(self, url, headers, cookieResolver):
#
#     if self.REQUEST_COOKIE_HEADER_NAME in headers:
#       cookies = headers[self.REQUEST_COOKIE_HEADER_NAME]
#       logger.debug("!!! cookies: '%s'", str(cookies))
#       cookieResolver.addCookie(url, cookies)
#
#     if self.RESPONSE_COOKIE_HEADER_NAME in headers:
#       cookies = headers[self.RESPONSE_COOKIE_HEADER_NAME]
#       logger.debug("!!! cookies: '%s'", str(cookies))
#       cookieResolver.addCookie(url, cookies)

  # # save cookies
  #
  # @param url - url string
  # @param res - responce object
  # @param cookieResolver - cookie resolver instance
  # @return - None
  def __saveCookies(self, url, res, cookieResolver):

    if self.RESPONSE_COOKIE_HEADER_NAME in res.headers:
      cookies = res.headers[self.RESPONSE_COOKIE_HEADER_NAME]
      logger.debug("!!! cookies: '%s'", str(cookies))
      if cookies is not None:
        cookieResolver.addCookie(url, cookies)


  # # Update headers by cached cookies
  #
  # @param headers - headers values dict
  # @param url - url string
  # @param cookieResolver - cookie resolver instance
  # @param stage - allowed stage of usage (support of different stages use bitmask)
  # @return updated headers object
  @staticmethod
  def updateHeadersByCookies(headers, url, cookieResolver, stage=HTTPCookieResolver.STAGE_DEFAULT):
    try:
      logger.debug('!!! Headers before update by cookies:\n' + str(headers))
      cookies = cookieResolver.getCookie(url, stage)
      if cookies is not None and isinstance(headers, dict):
        headers[RequestsRedirectWrapper.REQUEST_COOKIE_HEADER_NAME] = cookies
        logger.debug('!!! Cookies was updated ...Use headers:\n' + str(headers))
    except Exception, err:
      logger.error("!!! Error: %s", str(err))

    return headers


  # # Next two callback function awhile not use, but possible can use in future.
  #   Now, they show different samles of usage hooks.

  # # check redirect max alowed count
  #
  # @param handler - RequestsRedirectWrapper instance reference
  @staticmethod
  def checkRedirectMax(handler, *args, **kwargs):
    logger.debug('handler: %s', varDump(handler))
    logger.debug('args = ' + str(args))
    logger.debug('kwargs = ' + str(kwargs))

    if handler is not None:
      handler.redirectCount += 1
      if handler.redirectCount > handler.maxRedirects:
        raise requests.exceptions.TooManyRedirects('Exceeded %s redirects.' % str(handler.maxRedirects))


  # # check redirect
  #
  # @param r - result object instance
  @staticmethod
  def checkRedirect(r, *args, **kwargs):
    # logger.debug('r: %s', varDump(r))
    logger.debug('args = ' + str(args))
    logger.debug('kwargs = ' + str(kwargs))
    logger.debug('r.url: %s', str(r.url))
    logger.debug('r.status_code = %s', str(r.status_code))
