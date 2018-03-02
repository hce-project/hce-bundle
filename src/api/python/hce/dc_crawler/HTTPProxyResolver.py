# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
HTTPProxyResolver it's class content main http proxy functional.

@package: dc_crawler
@file HTTPProxyResolver.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import os
import sys
import re
import json

import app.Utils as Utils
from app.Utils import varDump
# import app.Consts as APP_CONSTS
from app.Exceptions import ProxyException
from dc_crawler.ProxyJsonWrapper import ProxyJsonWrapper
from dc_crawler.UserProxyJsonWrapper import UserProxyJsonWrapper
from dc.EventObjects import Proxy


logger = Utils.MPLogger().getLogger()

class HTTPProxyResolver(object):
  # #Constants used in class
  USER_PROXY_PROPERTY_NAME = 'USER_PROXY'
  HTTP_PROXY_HOST_NAME = 'HTTP_PROXY_HOST'
  HTTP_PROXY_PORT_NAME = 'HTTP_PROXY_PORT'

  INDEX_FILE_EXTENTION = 'json'

  USAGE_ALGORITM_FREQUENCY = 0
  DEFAULT_USAGE_ALGORITM = USAGE_ALGORITM_FREQUENCY

  DEFAULT_VALUE_INCREMENT_FAULTS = ProxyJsonWrapper.DEFAULT_VALUE_INCREMENT_FAULTS

  # #Constants of error messages
  ERROR_MSG_LOAD_SITE_PTOPERTIES = "Load site properties failed. Error: %s"
  ERROR_MSG_NOT_SUPPORT_ALGORITHM = "Not support algorithm type = %s"
  ERROR_MSG_CHECK_ALLOWED_DOMAINS = "Check is allowed domains '%s' has error: %s"
  ERROR_MSG_CHECK_ALLOWED_LIMITS = "Check is allowed limits '%s' has error: %s"

  ERROR_MSG_EMPTY_PROXIES_LIST = "Empty proxies list."
  ERROR_MSG_NOT_EXIST_ANY_VALID_PROXY = "No available proxy in proxies list."
  ERROR_MSG_TRIES_LIMIT_EXCEEDED = "Tries usage proxies limit was exceeded."

  # # Initialization
  def __init__(self):
    pass


  # # get user proxy json wrapper instance
  #
  # @param siteProperties - site properties dict
  # @return user proxy json wrapper instance
  @staticmethod
  def __getUserProxyJsonWrapper(siteProperties):
    # variable for result
    userProxyJsonWrapper = None
    try:
      if HTTPProxyResolver.USER_PROXY_PROPERTY_NAME in siteProperties:
        userProxyJsonWrapper = UserProxyJsonWrapper(json.loads(siteProperties[HTTPProxyResolver.\
                                                                              USER_PROXY_PROPERTY_NAME]))
      elif HTTPProxyResolver.USER_PROXY_PROPERTY_NAME.lower() in siteProperties:
        userProxyJsonWrapper = UserProxyJsonWrapper(json.loads(siteProperties[HTTPProxyResolver.\
                                                                              USER_PROXY_PROPERTY_NAME.lower()]))
    except Exception, err:
      logger.error(HTTPProxyResolver.ERROR_MSG_LOAD_SITE_PTOPERTIES, str(err))

    return userProxyJsonWrapper


  # # make file name
  #
  # @param filePath - file path or dirrectory name
  # @param siteId - site id
  # @return full file name
  @staticmethod
  def __makFileName(filePath, siteId):
    # variable for result
    ret = None
    logger.debug("filePath: %s", str(filePath))

    if isinstance(filePath, basestring) and filePath != "":
      dirName, fileName = os.path.split(filePath)
      if os.extsep in  fileName:
        # it's file
        ret = filePath
      else:
        # it's dir
        if siteId is not None:
          ret = (dirName if fileName == '' else filePath) + os.sep + str(siteId) + os.extsep + \
            HTTPProxyResolver.INDEX_FILE_EXTENTION

    return ret


  # # read json file
  #
  # @param fileName - file name
  # @return data of file as dict
  @staticmethod
  def __readJsonFile(fileName):
    # variable for result
    ret = {}
    try:
      if fileName is not None:
        # get full file name
        fullName = os.path.expanduser(fileName)
        if os.path.exists(fullName):
          f = open(fullName, 'r')
          ret = json.load(f)
          f.close()
    except Exception, err:
      logger.error(str(err))

    return ret


  # # save json file
  #
  # @param fileName - file name
  # @param jsonData -  data dict for save as json in file
  # @return - None
  @staticmethod
  def __saveJsonFile(fileName, jsonData):
    if fileName is not None and jsonData is not None and len(jsonData) > 0:
      try:
        # get full file name
        fullName = os.path.expanduser(fileName)
        # make directories if necessary
        dirName = os.path.dirname(fullName)
        if not os.path.exists(dirName):
          os.makedirs(dirName)

        f = open(fullName, 'w')
        json.dump(jsonData, f)
        f.close()
      except (IOError, Exception), err:
        logger.error(str(err))


  # # get proxy list allowed domains
  #
  # @param proxyList - list of Proxy objects
  # @param url - resource url for check allowed domain
  # @return list of Proxy objects
  @staticmethod
  def __getProxyListAllowedDomains(proxyList, url):
    # variable for result
    resList = []
    # logger.debug("proxyList: %s", varDump(proxyList))

    if isinstance(proxyList, list):
      if url is None:
        resList = proxyList
      else:
        allowedDomains = []
        for proxy in proxyList:
          if isinstance(proxy, Proxy) and isinstance(url, basestring):
            try:
              # logger.debug("!!! '%s' has type: %s", str(proxy.domains), str(type(proxy.domains)))
              if isinstance(proxy.domains, basestring):
                domains = json.loads(proxy.domains)
              else:
                domains = proxy.domains

              if isinstance(domains, list):
                for domain in domains:
                  if domain == '*' or (url != "" and re.search(domain, url, re.I + re.U) is not None):
                    resList.append(proxy)
                    # logger.debug("Is allowed domain: '%s'", str(domain))
                    allowedDomains.append(domain)
                    break

            except Exception, err:
              logger.error(HTTPProxyResolver.ERROR_MSG_CHECK_ALLOWED_DOMAINS, str(proxy.domains), str(err))

        logger.debug("Found allowed domains: %s", varDump(list(set(allowedDomains))))

    return resList


  # # get proxy list allowed limits
  #
  # @param proxyList - list of Proxy objects
  # @return list of Proxy objects
  @staticmethod
  def __getProxyListAllowedLimits(proxyList):
    # variable for result
    resList = []
    if isinstance(proxyList, list):
      for proxy in proxyList:
        if isinstance(proxy, Proxy):
          try:
            # logger.debug("!!! '%s' has type: %s", str(proxy.limits), str(type(proxy.limits)))
            if isinstance(proxy.limits, basestring):
              limits = json.loads(proxy.limits)
            else:
              limits = proxy.limits

            # logger.debug("!!! '%s' has type: %s", str(limits), str(type(limits)))

            if limits is None:
              resList = proxyList
            elif isinstance(limits, list):
              # #TODO Not implemented case of checking limits
#               for limit in limits:
#                 # #TODO checking limits
#                 if limit == :
#                   resList.append(proxy)
#                   logger.debug("Is allowed limit: '%s'", str(limit))
#                   break
              # logger.debug("!!! Not implemented case of checking limits")
              resList = proxyList
            else:
              logger.debug("!!! Default case checking limits")
              resList.append(proxy)

          except Exception, err:
            logger.error(HTTPProxyResolver.ERROR_MSG_CHECK_ALLOWED_LIMITS, str(proxy.limits), str(err))

    return resList


  # # usage algorithm frequency
  #
  # @param proxyList - list of Proxy objects
  # @return proxyName - proxy name
  @staticmethod
  def __usageAlgorithmFrequency(proxyList):
    # variable for result
    proxyName = None

    # # local method for debug print
    #
    # @param proxyList - list of Proxy objects
    # @param msg - message string
    # @return - None
    def __debugPrint(proxyList, msg):  # pylint: disable=W0613
      out = []
      if isinstance(proxyList, list):
        for proxy in proxyList:
          if hasattr(proxy, ProxyJsonWrapper.PROXIES_HOST_NAME) and hasattr(proxy, ProxyJsonWrapper.PROXIES_FREQ_NAME) \
            and hasattr(proxy, ProxyJsonWrapper.PROXIES_PRIORITY_NAME):
            out.append("priority: %s, freq: %s, host: %s" % (getattr(proxy, ProxyJsonWrapper.PROXIES_PRIORITY_NAME),
                                                             getattr(proxy, ProxyJsonWrapper.PROXIES_FREQ_NAME),
                                                             getattr(proxy, ProxyJsonWrapper.PROXIES_HOST_NAME)))
#       logger.debug("%s:\n%s", str(msg), '\n'.join(out))


    # log before sort
    __debugPrint(proxyList, "Before sort")

    proxyList.sort(key=lambda obj: getattr(obj, ProxyJsonWrapper.PROXIES_FREQ_NAME) * \
                   getattr(obj, ProxyJsonWrapper.PROXIES_PRIORITY_NAME) \
                   if hasattr(obj, ProxyJsonWrapper.PROXIES_FREQ_NAME) and \
                   hasattr(obj, ProxyJsonWrapper.PROXIES_PRIORITY_NAME) else sys.maxint)

    # log after sort
    __debugPrint(proxyList, "After sort")

    if len(proxyList) > 0 and hasattr(proxyList[0], ProxyJsonWrapper.PROXIES_HOST_NAME):
      proxyName = getattr(proxyList[0], ProxyJsonWrapper.PROXIES_HOST_NAME)

    return proxyName


  # # usage algorithm
  #
  # @param proxyList - list of Proxy objects
  # @param algorithmType - type of algorithm
  # @return proxyName - proxy name
  @staticmethod
  def __usageAlgorithm(proxyList, algorithmType=DEFAULT_USAGE_ALGORITM):
    # variable for result
    ret = None

    if algorithmType == HTTPProxyResolver.USAGE_ALGORITM_FREQUENCY:
      ret = HTTPProxyResolver.__usageAlgorithmFrequency(proxyList)
    else:
      logger.error(HTTPProxyResolver.ERROR_MSG_NOT_SUPPORT_ALGORITHM, str(HTTPProxyResolver))

    return ret


  # # get default proxy name
  #
  # @param siteProperties - sites property dict
  # @return proxy data as string or None
  @staticmethod
  def __getDefaultProxyName(siteProperties):
    # variable for result
    proxyName = None
    if HTTPProxyResolver.HTTP_PROXY_HOST_NAME in siteProperties and \
      HTTPProxyResolver.HTTP_PROXY_PORT_NAME in siteProperties:
      proxyName = "%s:%s" % (str(siteProperties[HTTPProxyResolver.HTTP_PROXY_HOST_NAME]),
                             str(siteProperties[HTTPProxyResolver.HTTP_PROXY_PORT_NAME]))

    return proxyName


  # # get proxy method
  #
  # @param siteProperties - sites property dict
  # @param siteId - site id
  # @param url - resource url for check allowed domain
  # @param dbProxyWrapper - DBProxyWrapper instance
  # @return - proxy data as string or None
  @staticmethod
  def getProxy(siteProperties, siteId, url, dbProxyWrapper=None):
    # variable for result
    proxyName = HTTPProxyResolver.__getDefaultProxyName(siteProperties)

    userProxyJsonWrapper = HTTPProxyResolver.__getUserProxyJsonWrapper(siteProperties)
    if userProxyJsonWrapper is not None:
      # get file name or dir
      fileName = HTTPProxyResolver.__makFileName(userProxyJsonWrapper.getFilePath(), siteId)
      logger.debug("Usage file name: %s", str(fileName))

      # read from index file
      jsonData = HTTPProxyResolver.__readJsonFile(fileName)
      proxyJsonWrapper = ProxyJsonWrapper(jsonData)
      logger.debug("Read json from index file: %s", varDump(proxyJsonWrapper.getData()))

      # extract proxies list from site property
      proxyList = userProxyJsonWrapper.getProxyList()
      logger.debug("Extract proxies list from site property: %s", varDump(proxyList))

      proxyJsonWrapper.addProxyList(proxyList)

      # extract proxies list from DB if necessary
      if dbProxyWrapper is not None and userProxyJsonWrapper.getSource() == UserProxyJsonWrapper.SOURCE_DATABASE:
        enaibledProxiesList = dbProxyWrapper.getEnaibledProxies(siteId)
        logger.debug("Extract enabled proxies list from DB: %s", varDump(enaibledProxiesList))
        proxyJsonWrapper.addProxyList(enaibledProxiesList)

      # check exist any proxies
      fullProxiesList = proxyJsonWrapper.getProxyList()
      logger.debug("Full proxies list: %s", varDump(fullProxiesList))
      if len(fullProxiesList) == 0:
        raise ProxyException(message=HTTPProxyResolver.ERROR_MSG_EMPTY_PROXIES_LIST,
                             statusUpdate=userProxyJsonWrapper.getStatusUpdateEmptyProxyList())

      # truncate list of only enabled proxies
      proxyList = proxyJsonWrapper.getProxyList(ProxyJsonWrapper.PROXY_STATE_ENABLED)
      logger.debug("Only enabled proxies: %s", varDump(proxyList))

      # check exist any valid proxies
      if len(proxyList) == 0:
        raise ProxyException(message=HTTPProxyResolver.ERROR_MSG_NOT_EXIST_ANY_VALID_PROXY,
                             statusUpdate=userProxyJsonWrapper.getStatusUpdateNoAvailableProxy())

      # truncate list of proxies use check allowed domains
      proxyList = HTTPProxyResolver.__getProxyListAllowedDomains(proxyList, url)
      logger.debug("Only allowed domains: %s", varDump(proxyList))

      # truncate list of proxies use check allowed limits
      proxyList = HTTPProxyResolver.__getProxyListAllowedLimits(proxyList)
      logger.debug("Only allowed limits: %s", varDump(proxyList))

      # exctract data use different algorithms
      proxyName = HTTPProxyResolver.__usageAlgorithm(proxyList, algorithmType=HTTPProxyResolver.DEFAULT_USAGE_ALGORITM)

      logger.debug("Result proxy name: %s", varDump(proxyName))
      if proxyName is not None:
        # increment frequency counter
        proxyJsonWrapper.addFrequency(proxyName)

        # save index file
        HTTPProxyResolver.__saveJsonFile(fileName, jsonData)

    return proxyName


  # # add faults to counter
  #
  # @param siteProperties - sites property dict
  # @param siteId - site ID value for request
  # @param proxyName - proxy host name
  # @param dbProxyWrapper - DBProxyWrapper instance
  # @param incrementSize - value for increment of faults counter
  # @return - None
  @staticmethod
  def addFaults(siteProperties, siteId, proxyName, dbProxyWrapper=None, incrementSize=DEFAULT_VALUE_INCREMENT_FAULTS):

    userProxyJsonWrapper = HTTPProxyResolver.__getUserProxyJsonWrapper(siteProperties)
    if userProxyJsonWrapper is not None:
      # extract file name
      fileName = HTTPProxyResolver.__makFileName(userProxyJsonWrapper.getFilePath(), siteId)
      logger.debug("Usage file name: %s", str(fileName))

      # read from index file
      jsonData = HTTPProxyResolver.__readJsonFile(fileName)
      proxyJsonWrapper = ProxyJsonWrapper(jsonData)
      logger.debug("Read json from index file: %s", varDump(proxyJsonWrapper.getData()))

      # increment faults counter for json data
      proxyJsonWrapper.addFaults(proxyName, incrementSize)

      # save index file
      HTTPProxyResolver.__saveJsonFile(fileName, jsonData)
      logger.debug("Save json to file: %s", varDump(jsonData))

      # increment faults counter for DB if necessary
      if dbProxyWrapper is not None:
        dbProxyWrapper.addFaults(proxyName, incrementSize)


  # # check tries count
  #
  # @param siteProperties - sites property dict
  # @param currentTriesCount - current tries count
  # @return - None
  @staticmethod
  def checkTriesCount(siteProperties, currentTriesCount):
    userProxyJsonWrapper = HTTPProxyResolver.__getUserProxyJsonWrapper(siteProperties)
    if userProxyJsonWrapper is not None:
      triesCount = userProxyJsonWrapper.getTriesCount()
      if triesCount is not None and int(currentTriesCount) >= int(triesCount):
        raise ProxyException(message=HTTPProxyResolver.ERROR_MSG_TRIES_LIMIT_EXCEEDED,
                             statusUpdate=userProxyJsonWrapper.getStatusUpdateTriesLimits())


  # # get tries count
  #
  # @param siteProperties - sites property dict
  # @return - tries count
  @staticmethod
  def getTriesCount(siteProperties):
    # variable for result
    triesCount = UserProxyJsonWrapper.DEFAULT_VALUE_TRIES_COUNT
    userProxyJsonWrapper = HTTPProxyResolver.__getUserProxyJsonWrapper(siteProperties)
    if userProxyJsonWrapper is not None:
      triesCount = userProxyJsonWrapper.getTriesCount()

    return triesCount


  # # check is necessary rotate proxy
  #
  # @param siteProperties - sites property dict
  # @param siteId - site ID value for request
  # @param proxyName - proxy host name
  # @param dbProxyWrapper - DBProxyWrapper instance
  # @param rawContent - sites property dict
  # @return True if success or False - otherwise
  @staticmethod
  def isNeedRotateProxy(siteProperties, siteId, proxyName, dbProxyWrapper, rawContent):
    # variable for result
    ret = False

    if rawContent is not None:
      userProxyJsonWrapper = HTTPProxyResolver.__getUserProxyJsonWrapper(siteProperties)
      if userProxyJsonWrapper is not None:
        patterns = userProxyJsonWrapper.getRawContentCheckPatterns()
        if isinstance(patterns, list):
          for pattern in patterns:
            if re.search(pattern, rawContent, re.M | re.U) is not None:

              # increment faults if necessary
              if int(userProxyJsonWrapper.getRawContentCheckFaults()) > 0:
                HTTPProxyResolver.addFaults(siteProperties, siteId, proxyName, dbProxyWrapper)

              # set result value
              ret = bool(int(userProxyJsonWrapper.getRawContentCheckRotate()) > 0)
              break

    return ret
