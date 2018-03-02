# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
HTTPRedirectResolver Class content main functional for resolve redirects

@package: dc_crawler
@file HTTPRedirectResolver.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import json
# import requests
import requests.exceptions
# from requests.packages.urllib3.exceptions import InsecureRequestWarning

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import app.Utils as Utils
from app.Utils import varDump
from app.Utils import getTracebackInfo
from dc_crawler.Fetcher import BaseFetcher
import dc_crawler.Constants as CONSTS
from dc_crawler.Exceptions import CrawlerFilterException

logger = Utils.MPLogger().getLogger()

class HTTPRedirectResolver(object):
  # # Constants

  # #Constants error message
  ERROR_INITIALIZATION = "Initialization class '%s' was failed. Error: %s"
  ERROR_BAD_TYPE_PROPERTY_VALUE = "Wrong type (%s) of property value: %s"
  ERROR_BAD_TYPE_HEADERS_VALUE = "Wrong type (%s) of headers: %s"
  ERROR_BAD_PROPERTY_VALUE = "Not support value '%s' for property '%s'"
  ERROR_BAD_STATUS_CODE_VALUE = "Not allowed status code '%s'. Allowed list: %s"


  # # Internal class for redirect property
  class RedirectProperty(object):
    # #Constants used in class
    PROPERTY_METHOD_NAME = "METHOD"
    PROPERTY_URL_PATTERN_LIST = "URL"
    PROPERTY_MAX_REDIRECTS = "MAX"
    PROPERTY_TYPES_LIST = "TYPES"

    METHOD_NAME_HEAD = 'HEAD'
    METHOD_NAME_SGET = 'SGET'
    METHOD_NAME_DGET = 'DGET'

    METHOD_NAME_GET = 'GET'

    DEFAULT_VALUE_METHOD_NAME = METHOD_NAME_HEAD
    DEFAULT_VALUE_URL_PATTERN_LIST = ['.*']
    DEFAULT_VALUE_MAX_REDIRECTS = 10
    DEFAULT_VALUE_TYPES_LIST = [301, 302, 303, 304]

    SUPPORT_METHOD_NAMES = [METHOD_NAME_HEAD, METHOD_NAME_SGET, METHOD_NAME_DGET]

    def __init__(self, methodName=None, urlPatternList=None, maxRedirects=None, typesList=None):
      self.methodName = self.DEFAULT_VALUE_METHOD_NAME if methodName is None else methodName
      self.urlPatternList = self.DEFAULT_VALUE_URL_PATTERN_LIST if urlPatternList is None else urlPatternList
      self.maxRedirects = self.DEFAULT_VALUE_MAX_REDIRECTS if maxRedirects is None else maxRedirects
      self.typesList = self.DEFAULT_VALUE_TYPES_LIST if typesList is None else typesList


  # Initialization
  # @param propertyString - contains string with json format
  # @param fetchType - fetcher type
  # @param dbWrapper - DBTaskWrapper instance
  # @param connectionTimeout - connection timeout
  # @param siteId- site ID
  def __init__(self, propertyString=None, fetchType=BaseFetcher.TYP_NORMAL, dbWrapper=None, siteId=None,
               connectionTimeout=CONSTS.CONNECTION_TIMEOUT):
    self.redirectProperty = self.__loadProperty(propertyString)
    self.fetchType = fetchType
    self.dbWrapper = dbWrapper
    self.siteId = siteId
    self.connectionTimeout = connectionTimeout


  # # get redirect property
  #
  # @param propertyDict - contains dictionary
  # @return RedirectProperty instance
  def getRedirectProperty(self, propertyDict):
  # variable for result
    redirectProperty = HTTPRedirectResolver.RedirectProperty()
    try:
      if not isinstance(propertyDict, dict):
        raise Exception(self.ERROR_BAD_TYPE_PROPERTY_VALUE % (str(type(propertyDict)), varDump(propertyDict)))

      # extract method name
      if HTTPRedirectResolver.RedirectProperty.PROPERTY_METHOD_NAME in propertyDict:
        if propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_METHOD_NAME] in \
          HTTPRedirectResolver.RedirectProperty.SUPPORT_METHOD_NAMES:
          redirectProperty.methodName = propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_METHOD_NAME]
        else:
          raise Exception(self.ERROR_BAD_PROPERTY_VALUE % \
                          (varDump(propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_METHOD_NAME]),
                           str(HTTPRedirectResolver.RedirectProperty.PROPERTY_METHOD_NAME)))

      # extract url pattern list
      if HTTPRedirectResolver.RedirectProperty.PROPERTY_URL_PATTERN_LIST in propertyDict:
        if isinstance(propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_URL_PATTERN_LIST], list):
          redirectProperty.urlPatternList = \
            propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_URL_PATTERN_LIST]

          for i in xrange(len(redirectProperty.urlPatternList)):
            if isinstance(redirectProperty.urlPatternList[i], dict):
              redirectProperty.urlPatternList[i] = self.getRedirectProperty(redirectProperty.urlPatternList[i])

        else:
          raise Exception(self.ERROR_BAD_PROPERTY_VALUE % \
                          (varDump(propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_URL_PATTERN_LIST]),
                           str(HTTPRedirectResolver.RedirectProperty.PROPERTY_URL_PATTERN_LIST)))

      # extract max redirects value
      if HTTPRedirectResolver.RedirectProperty.PROPERTY_MAX_REDIRECTS in propertyDict:
        redirectProperty.maxRedirects = \
          int(propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_MAX_REDIRECTS])

      # extract redirect types list
      if HTTPRedirectResolver.RedirectProperty.PROPERTY_TYPES_LIST in propertyDict:
        if isinstance(propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_TYPES_LIST], list):
          redirectProperty.typesList = propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_TYPES_LIST]
        else:
          raise Exception(self.ERROR_BAD_PROPERTY_VALUE % \
                          (varDump(propertyDict[HTTPRedirectResolver.RedirectProperty.PROPERTY_TYPES_LIST]),
                           str(HTTPRedirectResolver.RedirectProperty.PROPERTY_TYPES_LIST)))

    except Exception, err:
      logger.error(self.ERROR_INITIALIZATION, self.__class__.__name__, str(err))
      logger.info(getTracebackInfo())

    return redirectProperty


  # # load property from input json
  #
  # @param propertyString - contains string with json format
  # @return RedirectProperty instance
  def __loadProperty(self, propertyString):
    # variable for result
    redirectProperty = HTTPRedirectResolver.RedirectProperty()

    if propertyString is not None:
      try:
        if not isinstance(propertyString, basestring) or propertyString == "":
          raise Exception(self.ERROR_BAD_TYPE_PROPERTY_VALUE % (str(type(propertyString)), varDump(propertyString)))

        propertyDict = json.loads(propertyString)
        redirectProperty = self.getRedirectProperty(propertyDict)

      except Exception, err:
        logger.error(self.ERROR_INITIALIZATION, self.__class__.__name__, str(err))
        logger.info(getTracebackInfo())

    return redirectProperty


  # # check is allowed url use incming pattern list
  #
  # @param url - url string
  # @param patterns - regular expression pattern list
  # @return True if allowed or False - otherwise
  @staticmethod
  def isAllowedUrl(url, patterns):
    # variable for result
    ret = True
    try:
      if isinstance(patterns, list):
        for pattern in patterns:
          if isinstance(pattern, basestring):
            ret = False
            if re.search(pattern, url, re.UNICODE + re.IGNORECASE) is not None:
              logger.debug("pattern: '%s' allowed for '%s'", str(pattern), str(url))
              ret = True
              break

    except Exception, err:
      logger.error(str(err))

    return ret


  # repair headers dictionary values if necessary
  #
  # @param headers - headers dictionary
  # @return headers dictionary after repair values
  def __repairHeaders(self, headers):
    if isinstance(headers, dict):
      for key, value in headers.items():
        headers[key] = ';'.join(value.split())


  # # resolve redirect url
  #
  # @param url - the url to fetch
  # @param headers - request headers dict
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param allowRedirects - boolean flag allowed redirects
  # @param proxies - proxy setting tuple
  # @param auth - basic auth setting, tuple of name and password
  # @param postData - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @param filters - filters dict
  # @return resolved result url
  def resolveRedirectUrl(self, url, headers, timeout=None,
                         allowRedirects=True, proxies=None, auth=None, postData=None,
                         maxRedirects=RedirectProperty.DEFAULT_VALUE_MAX_REDIRECTS, filters=None):

    # variable for result
    ret = None

    logger.debug("Input url: %s \nheaders: %s", str(url), varDump(headers))
#     logger.debug("method name: %s, max redirects = %s, redirect codes: %s",
#                  str(self.redirectProperty.methodName), str(self.redirectProperty.maxRedirects),
#                  str(self.redirectProperty.typesList))

#     self.__repairHeaders(headers) # remove in future because it's wrong logic
#     logger.debug("headers: %s", varDump(headers))

    try:

      ret = self.__resolveRedirect(url=url, method=self.redirectProperty.methodName, headers=headers, timeout=timeout,
                                   allowRedirects=allowRedirects, proxies=proxies, auth=auth, postData=postData,
                                   maxRedirects=maxRedirects, filters=filters,
                                   redirectProperty=self.redirectProperty)

      for urlPatternElem in self.redirectProperty.urlPatternList:
        logger.debug("urlPatternElem: %s", varDump(urlPatternElem))
        logger.debug("type(urlPatternElem) = %s", str(type(urlPatternElem)))

        if isinstance(urlPatternElem, HTTPRedirectResolver.RedirectProperty):
          res = self.__resolveRedirect(url=url, method=self.redirectProperty.methodName, headers=headers,
                                       timeout=timeout, allowRedirects=allowRedirects, proxies=proxies, auth=auth,
                                       postData=postData, maxRedirects=maxRedirects, filters=filters,
                                       redirectProperty=urlPatternElem)
          if res is not None:
            ret = res

    except CrawlerFilterException:
      logger.debug("Url '%s' should be skipped.", str(url))
    except (requests.exceptions.RequestException, Exception), err:
      logger.debug("Resolve redirect url failed: %s", str(err))
      logger.info(Utils.getTracebackInfo())

    return ret


  # # resolve redirect
  #
  # @param url - the url to fetch
  # @param headers - request headers dict
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param allowRedirects - boolean flag allowed redirects
  # @param proxies - proxy setting tuple
  # @param auth - basic auth setting, tuple of name and password
  # @param postData - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @param filters - filters dict
  # @param redirectProperty - RedirectProperty instance
  # @return resolved result url
  def __resolveRedirect(self, url, headers, method, timeout=None,
                         allowRedirects=True, proxies=None, auth=None, postData=None,
                         maxRedirects=RedirectProperty.DEFAULT_VALUE_MAX_REDIRECTS, filters=None,
                         redirectProperty=None):
    # variable for result
    ret = None
    logger.debug("type(redirectProperty) = %s", str(type(redirectProperty)))
    if isinstance(redirectProperty, HTTPRedirectResolver.RedirectProperty):
      logger.debug("type is GOOD!!!")

      # check is allowed url for processing by pattern list
      if HTTPRedirectResolver.isAllowedUrl(url, redirectProperty.urlPatternList):

        if redirectProperty.methodName == HTTPRedirectResolver.RedirectProperty.METHOD_NAME_HEAD:
          # method 'HEAD' execution
          ret = self.__fetch(url=url, method=HTTPRedirectResolver.RedirectProperty.METHOD_NAME_HEAD,
                             headers=headers, timeout=timeout, allowRedirects=allowRedirects, proxies=proxies,
                             auth=auth, postData=postData, maxRedirects=maxRedirects, filters=filters,
                             fetchType=self.fetchType)

        elif redirectProperty.methodName == HTTPRedirectResolver.RedirectProperty.METHOD_NAME_SGET:
          # method 'GET' for static fetcher type execution
          ret = self.__fetch(url=url, method=HTTPRedirectResolver.RedirectProperty.METHOD_NAME_GET,
                             headers=headers, timeout=timeout, allowRedirects=allowRedirects, proxies=proxies,
                             auth=auth, postData=postData, maxRedirects=maxRedirects, filters=filters,
                             fetchType=BaseFetcher.TYP_NORMAL)

        elif self.redirectProperty.methodName == HTTPRedirectResolver.RedirectProperty.METHOD_NAME_DGET:
          # method 'GET' for dynamic fetcher type execution
          ret = self.__fetch(url=url, method=HTTPRedirectResolver.RedirectProperty.METHOD_NAME_GET,
                             headers=headers, timeout=timeout, allowRedirects=allowRedirects, proxies=proxies,
                             auth=auth, postData=postData, maxRedirects=maxRedirects, filters=filters,
                             fetchType=BaseFetcher.TYP_DYNAMIC)

    return ret


  # # make fetch
  #
  # @param url - the url to fetch
  # @param headers - request headers dict
  # @param method - fetch by HTTP method
  # @param timeout - request timeout(seconds)
  # @param allowRedirects - boolean flag allowed redirects
  # @param proxies - proxy setting tuple
  # @param auth - basic auth setting, tuple of name and password
  # @param postData - post data, used only when method is post
  # @param maxRedirects - max allowed redirects count
  # @param filters - filters dict
  # @param fetchType - fetch type
  # @return result url
  def __fetch(self, url, headers, method, timeout=None,
                         allowRedirects=True, proxies=None, auth=None, postData=None,
                         maxRedirects=RedirectProperty.DEFAULT_VALUE_MAX_REDIRECTS, filters=None,
                         fetchType=BaseFetcher.TYP_NORMAL):
    # variable for result
    ret = None
    fetcher = BaseFetcher.get_fetcher(fetchType, None, self.dbWrapper, self.siteId)
    fetcher.connectionTimeout = self.connectionTimeout

    res = fetcher.open(url=url, method=method, headers=headers, timeout=timeout,
                       allow_redirects=allowRedirects, proxies=proxies, auth=auth, data=postData, log=logger,
                       max_redirects=maxRedirects, filters=filters)

    if res.url is not None:
      ret = res.url

    return ret
