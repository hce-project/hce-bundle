"""
HCE project,  Python bindings, Distributed Tasks Manager application.
HTTPCookieResolver Class content main functional for collect and resolve cookies

@package: dc_crawler
@file HTTPCookieResolver.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import json
import datetime

import app.Utils as Utils
from app.Utils import parseHost
from app.DateTimeType import DateTimeType
from app.Utils import varDump

logger = Utils.MPLogger().getLogger()

class HTTPCookieResolver(object):
  # Constants names of usage stages
  STAGE_REGULAR = 1
  STAGE_REDIRECT = 2
  STAGE_ROBOTS = 4
  STAGE_RSS = 8
  # Default value of stage
  STAGE_DEFAULT = STAGE_REGULAR | STAGE_REDIRECT | STAGE_ROBOTS | STAGE_RSS
  DOMAIN_DEFAULT = '.*'

  # Constants error message
  ERROR_BAD_TYPE_INPUT_PROPERTY = "Bad type (%s) of input property: %s"
  ERROR_BAD_TYPE_FOUND_PROPERTY = "Bad type (%s) of found property: %s"
  ERROR_INPUT_PROPERTY = "Input wrong properties: %s"
  ERROR_INITIALIZATION = "Initialization class '%s' was failed. Error: '%s'"

  # # Internal class for cookie properties
  class Cookie(object):
    supportNames = ['expires', 'domain', 'path']
    def __init__(self):
      self.expires = None
      self.domain = None
      self.path = None
      self.name = None
      self.value = None

    # # get data
    #
    # @param - None
    # @return cookie data as string
    def getData(self):
      # variable for result
      ret = ''
      if isinstance(self.name, basestring) and isinstance(self.value, basestring) and \
        self.name != "" and self.value != "":
        ret = str(self.name) + '=' + str(self.value) + '; '

      return ret


  # # Internal class for domain properties
  class DomainProperty(object):
    def __init__(self, stage=None, cookie=None):
      self.stage = stage
      self.cookie = cookie


  # Constructor
  # @param propertyString - contains string with json format
  def __init__(self, propertyString=None):
    self.cookiesDict = {}
    self.property = {self.DOMAIN_DEFAULT:{'stage':self.STAGE_DEFAULT}}

    if propertyString is not None and isinstance(propertyString, basestring):
      self.property = self.__loadProperty(propertyString)
      logger.debug("!!! self.property: %s", varDump(self.property))

  # # load property from input json
  #
  # @param propertyString - contains string with json format
  # @return object properties
  def __loadProperty(self, propertyString):
    # variable for result
    ret = None
    try:
      ret = json.loads(propertyString)
    except Exception, err:
      logger.error(self.ERROR_INITIALIZATION, self.__class__.__name__, str(err))

    return ret


  # # Add cookie to dict as raw string
  #
  # @param url - url string use as key in dict
  # @param cookie - cookie string value or dict
  # @param strip - use strip for url
  # @return - None
  def addCookie(self, url, cookie, strip=True):
    # logger.debug("!!! addCookie ENTER !!! cookiesDict: %s", varDump(self.cookiesDict))
    # logger.debug("!!! url: '%s', cookie: %s, type = %s, strip = %s",
    #              str(url), str(cookie), str(type(cookie)), str(strip))

    localUrl = self.__stripUrl(url) if strip else url
    # logger.debug("!!! localUrl: %s", str(localUrl))

    if isinstance(cookie, basestring):
      if cookie != "":
        self.cookiesDict[localUrl] = ';'.join(cookie.split())
    elif isinstance(cookie, dict):
      self.cookiesDict[localUrl] = ';'.join(['%s=%s' % (k, v) for k, v in cookie.iteritems()])

    # logger.debug("!!! addCookie LEAVE !!! cookiesDict: %s", varDump(self.cookiesDict))


  # # Strip url (remove parameters from url string)
  #
  # @param url - url string
  # @return url - stripped url
  def __stripUrl(self, url):
    if isinstance(url, basestring) and url.count('?') > 0:
      url = url[:url.find('?')]

    return url


  # # Extract pair of name and values
  #
  # @param element - element string
  # @return name and value extracted from element string
  def __extractPair(self, element):
    # variables for result
    name = value = ''
    pairElem = element.split('=')
    if len(pairElem) > 0:
      name = pairElem[0]

    if len(pairElem) > 1:
      value = pairElem[1]

    return name, value


  # # Split cookies string
  #
  # @param cookie - cookie string value
  # @return cookies - list of Cookie class instances
  def __splitCookieString(self, cookieString):
    # variable for result
    cookies = []
    # extract elements
    elementsList = cookieString.split(';')
    elements = []
    for element in elementsList:
      if element.count('=') > 1:
        endPos = element.rfind('=')
        begPos = element.rfind(' ', 0, endPos)

        first = element[:begPos]
        second = element[begPos:]
        first = first.strip(',')

        elements.append(first.strip())
        elements.append(second.strip())
      else:
        elements.append(element.strip())

    # logger.debug("!!! elements: %s", varDump(elements))
    cookieObj = HTTPCookieResolver.Cookie()
    for element in elements:
      name, value = self.__extractPair(element)
      # logger.debug("!!! name = %s, value = %s", name, value)

      if name.lower() not in HTTPCookieResolver.Cookie.supportNames and \
        cookieObj.name is not None and cookieObj.value is not None:
        cookies.append(cookieObj)
        cookieObj = HTTPCookieResolver.Cookie()

      if name.lower() in HTTPCookieResolver.Cookie.supportNames:
        if hasattr(cookieObj, name.lower()):
          setattr(cookieObj, name.lower(), value)
      elif cookieObj.name is None and cookieObj.value is None:
        cookieObj.name = name
        cookieObj.value = value

    if cookieObj.name is not None and cookieObj.value is not None:
      cookies.append(cookieObj)

    logger.debug("!!! cookies:")
    for cookie in cookies:
      logger.debug("%s", varDump(cookie))

    return cookies


  # # Check is allowed cookie instance
  #
  # @param url - url string for search cookie
  # @param cookieObj - cookie instance for check
  # @return True if allowed or otherwise False
  def __isAllowedCookie(self, url, cookieObj):
    # variable for result
    ret = False

    isAllowedPath = isAllowedExpires = True

    # check 'path'
    if cookieObj.path is not None and re.search('.*' + cookieObj.path + '.*', url, re.UNICODE) is None:
      isAllowedPath = False

    # check 'expired'
    if cookieObj.expires is not None:
      expiresDatetime = DateTimeType.parse(cookieObj.expires, True, logger, False)
      if expiresDatetime is not None:
        expiresDatetime = DateTimeType.toUTC(expiresDatetime)
        currentDatetime = datetime.datetime.utcnow()
        currentDatetime = currentDatetime.replace(tzinfo=None)
        if currentDatetime > expiresDatetime:
          isAllowedExpires = False

    logger.debug("Is allowed = %s for path '%s'", str(isAllowedPath), str(cookieObj.path))
    logger.debug("Is allowed = %s for expired '%s'", str(isAllowedExpires), str(cookieObj.expires))

    if isAllowedPath and isAllowedExpires:
      ret = True

    return ret


  # # Exctract domain properties
  #
  # @param url - url string for search cookie
  # @return propertyStage and propertyCookie - extracted stage and cookies from domain properties
  def __extractDomainProperty(self, url):
    # variables for result
    propertyStage = HTTPCookieResolver.STAGE_DEFAULT
    propertyCookie = None

    propertyObj = self.__getDomainProperty(self.property, url)
    # logger.debug('propertyObj: ' + str(propertyObj))

    if propertyObj is not None:
      if propertyObj.stage is not None:
        propertyStage = propertyObj.stage
      propertyCookie = propertyObj.cookie

    return propertyStage, propertyCookie


  # # Check is allowed stage
  #
  # @param stage - allowed stage of usage (support of different stages use bitmask)
  # @param propertyStage - stage from properties
  # @return True if allowed or otherwise False
  def __isAllowedStage(self, stage, propertyStage):
    # variable for result
    ret = False
    if stage & int(propertyStage):
      ret = True

    return ret


  # # Get domain property
  #
  # @param properties - properties structure
  # @param domain - domain name for extract from property
  # @return DomainProperty instance is success or otherwise None
  def __getDomainProperty(self, properties, domain):
    # variable for result
    ret = None
    try:
      if not isinstance(properties, dict):
        raise Exception(self.ERROR_BAD_TYPE_INPUT_PROPERTY % (str(type(property)), str(property)))

      foundProperty = None
      if domain in properties:
        foundProperty = properties[domain]
      elif self.DOMAIN_DEFAULT in properties:
        foundProperty = properties[self.DOMAIN_DEFAULT]
      else:
        logger.debug(self.ERROR_INPUT_PROPERTY, varDump(property))

      if foundProperty is not None:
        if not isinstance(foundProperty, dict):
          raise Exception(self.ERROR_BAD_TYPE_FOUND_PROPERTY % (str(type(foundProperty)), str(foundProperty)))

        domainPropertyObj = HTTPCookieResolver.DomainProperty()
        for name, value in foundProperty.items():
          if hasattr(domainPropertyObj, name):
            setattr(domainPropertyObj, name, value)
        ret = domainPropertyObj

    except Exception, err:
      logger.error(str(err))

    return ret


  # # Get valid cookie
  #
  # @param url - url string for search cookie
  # @param stage - allowed stage of usage (support of different stages use bitmask)
  # @return ret - cookie string if found cookie or otherwise None
  def getCookie(self, url, stage=STAGE_DEFAULT):
    # variable for result
    ret = None

    logger.debug('!!! getCookie ENTER !!! url: ' + str(url))
    if url in self.cookiesDict.keys():
      if self.cookiesDict[url] is not None and self.cookiesDict[url] != "":
        logger.debug('!!! getCookie LEAVE !!! return: ' + str(';'.join(self.cookiesDict[url].split())))
        return ';'.join(self.cookiesDict[url].split())

    for localUrl, cookieString in self.cookiesDict.items():
      logger.debug("!!! localUrl = %s, cookieString: %s", str(localUrl), str(cookieString))

      propertyStage, propertyCookie = self.__extractDomainProperty(parseHost(localUrl))
      logger.debug("!!! propertyStage = %s, propertyCookie: %s", str(propertyStage), varDump(propertyCookie))
      logger.debug('is allowed stage: ' + str(self.__isAllowedStage(stage, propertyStage)))

      if self.__isAllowedStage(stage, propertyStage):
        if propertyCookie is None:  # not exist default cookie
          logger.debug('cookieString: ' + str(cookieString))

          cookies = self.__splitCookieString(cookieString)
          logger.debug('cookies: ' + varDump(cookies))
          logger.debug('localUrl: ' + str(localUrl))
          logger.debug('url: ' + str(url))

          resStr = ''
          resList = []
          for cookie in cookies:
            if cookie.domain is None or (cookie.domain is not None and \
                                         re.search('.*' + cookie.domain + '.*', url, re.UNICODE) is not None):

              logger.debug('is allowed: ' + str(self.__isAllowedCookie(url, cookie)))
              if self.__isAllowedCookie(url, cookie):
                resList.append(cookie.getData())

          # remove dublicate
          resList = list(set(resList))
          resStr = ''.join(resList)

          if resStr is not '':
            ret = resStr

        else:  # apply default value of cookie
          ret = propertyCookie

    logger.debug('return cookie: ' + str(ret))

    return ret
