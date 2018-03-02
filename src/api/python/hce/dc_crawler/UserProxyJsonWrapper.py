# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
It's wrapper user proxy property.

@package: dc_crawler
@file UserProxyJsonWrapper.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

from dc.EventObjects import Proxy


class UserProxyJsonWrapper(object):

  # #Constants used in class
  SOURCE_NAME = 'source'
  FILE_PATH_NAME = 'file_path'
  TRIES_COUNT_NAME = 'tries_count'
  STATUS_UPDATE_EMPTY_PROXY_LIST_NAME = 'status_update_empty_proxy_list'
  STATUS_UPDATE_NO_AVAILABLE_PROXY_NAME = 'status_update_no_available_proxy'
  STATUS_UPDATE_TRIES_LIMITS_NAME = 'status_update_tries_limit'

  PROXIES_NAME = 'proxies'
  PROXIES_HOST_NAME = 'host'
  PROXIES_DOMAINS_NAME = 'domains'
  PROXIES_PRIORITY_NAME = 'priority'
  PROXIES_LIMITS_NAME = 'limits'
  PROXIES_STATE_NAME = 'state'

  PROXIES_DATA_LIST_NAMES = [PROXIES_HOST_NAME, PROXIES_DOMAINS_NAME, PROXIES_PRIORITY_NAME, PROXIES_LIMITS_NAME, \
                             PROXIES_STATE_NAME]

  RAW_CONTENY_CHECK_NAME = 'raw_content_check'
  RAW_CONTENY_CHECK_PATTERNS_NAME = 'patterns'
  RAW_CONTENY_CHECK_ROTATE_NAME = 'rotate'
  RAW_CONTENY_CHECK_FAULTS_NAME = 'faults'


  # Support state values
  PROXY_STATE_DISABLED = 0
  PROXY_STATE_ENABLED = 1

  # Support source type values
  SOURCE_PROPERTY = 0
  SOURCE_DATABASE = 1

  # Status update range allowed values
  STATUS_UPDATE_MIN_ALLOWED_VALUE = 1
  STATUS_UPDATE_MAX_ALLOWED_VALUE = 7

  # Default values
  DEFAULT_VALUE_JSON_DATA = {}
  DEFAULT_VALUE_SOURCE = SOURCE_PROPERTY
  DEFAULT_VALUE_PROXIES = {}
  DEFAULT_VALUE_PROXIES_DOMAIN = ['*']
  DEFAULT_VALUE_PROXIES_PRIORITY = 10
  DEFAULT_VALUE_PROXIES_LIMITS = None
  DEFAULT_VALUE_PROXIES_STATE = PROXY_STATE_ENABLED

  DEFAULT_VALUE_RAW_CONTENY_CHECK_PATTERNS = []
  DEFAULT_VALUE_RAW_CONTENY_CHECK_ROTATE = 1
  DEFAULT_VALUE_RAW_CONTENY_CHECK_FAULTS = 1

  DEFAULT_VALUE_TRIES_COUNT = 1


  # # Initialization
  #
  # @param jsonData - json data
  def __init__(self, jsonData):
    self.jsonData = (jsonData if isinstance(jsonData, dict) else self.DEFAULT_VALUE_JSON_DATA)


  # # get source value from json
  #
  # @param - None
  # @return source value from json
  def getSource(self):
    return int(self.jsonData[self.SOURCE_NAME] if self.SOURCE_NAME in self.jsonData and \
               int(self.jsonData[self.SOURCE_NAME]) == (self.SOURCE_PROPERTY or self.SOURCE_DATABASE) else \
               self.SOURCE_PROPERTY)

  # # set source value to json
  #
  # @param - source value
  # @return - None
  def setSource(self, source):
    if int(source) == self.SOURCE_PROPERTY or int(source) == self.SOURCE_DATABASE:
      self.jsonData[self.SOURCE_NAME] = int(source)


  # # get file path value from json
  #
  # @param - None
  # @return file path value from json
  def getFilePath(self):
    return self.jsonData[self.FILE_PATH_NAME] if self.FILE_PATH_NAME in self.jsonData else None


  # # get tries count value from json
  #
  # @param - None
  # @return tries count value from json
  def getTriesCount(self):
    return int(self.jsonData[self.TRIES_COUNT_NAME]) if self.TRIES_COUNT_NAME in self.jsonData \
      else self.DEFAULT_VALUE_TRIES_COUNT


  # # get status_update_empty_proxy_list value from json
  #
  # @param - None
  # @return status_update_empty_proxy_list value from json
  def getStatusUpdateEmptyProxyList(self):
    return int(self.jsonData[self.STATUS_UPDATE_EMPTY_PROXY_LIST_NAME]) \
      if self.STATUS_UPDATE_EMPTY_PROXY_LIST_NAME in self.jsonData and \
        int(self.jsonData[self.STATUS_UPDATE_EMPTY_PROXY_LIST_NAME]) >= self.STATUS_UPDATE_MIN_ALLOWED_VALUE and \
        int(self.jsonData[self.STATUS_UPDATE_EMPTY_PROXY_LIST_NAME]) <= self.STATUS_UPDATE_MAX_ALLOWED_VALUE else None


  # # get status_update_no_available_proxy value from json
  #
  # @param - None
  # @return status_update_no_available_proxy value from json
  def getStatusUpdateNoAvailableProxy(self):
    return int(self.jsonData[self.STATUS_UPDATE_NO_AVAILABLE_PROXY_NAME]) \
      if self.STATUS_UPDATE_NO_AVAILABLE_PROXY_NAME in self.jsonData and \
        int(self.jsonData[self.STATUS_UPDATE_NO_AVAILABLE_PROXY_NAME]) >= self.STATUS_UPDATE_MIN_ALLOWED_VALUE and \
        int(self.jsonData[self.STATUS_UPDATE_NO_AVAILABLE_PROXY_NAME]) <= self.STATUS_UPDATE_MAX_ALLOWED_VALUE else None


  # # get status_update_tries_limit value from json
  #
  # @param - None
  # @return status_update_tries_limit value from json
  def getStatusUpdateTriesLimits(self):
    return int(self.jsonData[self.STATUS_UPDATE_TRIES_LIMITS_NAME]) \
      if self.STATUS_UPDATE_TRIES_LIMITS_NAME in self.jsonData and \
        int(self.jsonData[self.STATUS_UPDATE_TRIES_LIMITS_NAME]) >= self.STATUS_UPDATE_MIN_ALLOWED_VALUE and \
        int(self.jsonData[self.STATUS_UPDATE_TRIES_LIMITS_NAME]) <= self.STATUS_UPDATE_MAX_ALLOWED_VALUE else None


  # # get proxies value from json
  #
  # @param - None
  # @return proxies value from json
  def getProxies(self):
    return self.jsonData[self.PROXIES_NAME] if self.PROXIES_NAME in self.jsonData else self.DEFAULT_VALUE_PROXIES


  # # set proxies value to json
  #
  # @param proxies - proxies value as dict
  # @return - None
  def setProxies(self, proxies):
    if isinstance(proxies, dict):
      self.jsonData[self.PROXIES_NAME] = proxies


  # # set proxies data value to json
  #
  # @param proxyData - proxy data value
  # @return - None
  def setProxyData(self, proxyData):
    if isinstance(proxyData, dict):
      proxies = self.getProxies()
      if self.PROXIES_HOST_NAME in proxyData.keys():

        proxyData[self.PROXIES_DOMAINS_NAME] = proxyData[self.PROXIES_DOMAINS_NAME] \
          if self.PROXIES_DOMAINS_NAME in proxyData.keys() and proxyData[self.PROXIES_DOMAINS_NAME] is not None \
          and proxyData[self.PROXIES_DOMAINS_NAME] != "" else self.DEFAULT_VALUE_PROXIES_DOMAIN

        proxyData[self.PROXIES_PRIORITY_NAME] = proxyData[self.PROXIES_PRIORITY_NAME] \
          if self.PROXIES_PRIORITY_NAME in proxyData.keys() and proxyData[self.PROXIES_PRIORITY_NAME] is not None \
          and int(proxyData[self.PROXIES_PRIORITY_NAME]) > 0 else self.DEFAULT_VALUE_PROXIES_PRIORITY

        proxyData[self.PROXIES_LIMITS_NAME] = proxyData[self.PROXIES_LIMITS_NAME] \
          if self.PROXIES_LIMITS_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_LIMITS

        proxyData[self.PROXIES_STATE_NAME] = proxyData[self.PROXIES_STATE_NAME] \
          if self.PROXIES_STATE_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_STATE

        proxies[proxyData[self.PROXIES_HOST_NAME]] = proxyData
        self.setProxies(proxies)


  # # get proxies data value from json
  #
  # @param proxyName - proxy name
  # @return - proxy data value
  def getProxyData(self, proxyName):
    # variable for result
    ret = None
    proxies = self.getProxies()
    if proxyName in proxies:
      ret = proxies[proxyName]

    return ret


  # # add list of Proxy objects to json
  #
  # @param proxyList - list of Proxy objects
  # @return - None
  def addProxyList(self, proxyList):
    if isinstance(proxyList, list):
      for proxy in proxyList:
        if isinstance(proxy, Proxy):
          proxyData = {}
          for name in self.PROXIES_DATA_LIST_NAMES:
            if hasattr(proxy, name):
              proxyData[name] = getattr(proxy, name)

          self.setProxyData(proxyData)


  # # get list of Proxy objects from json
  #
  # @param - None
  # @return list of Proxy objects
  def getProxyList(self):
    # variable for result
    proxyList = []

    proxies = self.getProxies()
    for proxyName in proxies.keys():
      proxyData = self.getProxyData(proxyName)

      proxy = Proxy(siteId='0', host='')
      proxy.state = self.DEFAULT_VALUE_PROXIES_STATE

      for name in self.PROXIES_DATA_LIST_NAMES:
        if name in proxyData:
          setattr(proxy, name, proxyData[name])

      if proxy.host != "":
        proxyList.append(proxy)

    return proxyList


  # # get raw_content_check value from json
  #
  # @param - None
  # @return raw_content_check value from json
  def getRawContentCheck(self):
    return self.jsonData[self.RAW_CONTENY_CHECK_NAME] if self.RAW_CONTENY_CHECK_NAME in self.jsonData else None


  # # get patterns value from raw_content_check value
  #
  # @param - None
  # @return patterns value from raw_content_check value
  def getRawContentCheckPatterns(self):
    rawContentCheck = self.getRawContentCheck()
    return rawContentCheck[self.RAW_CONTENY_CHECK_PATTERNS_NAME] if rawContentCheck is not None and \
      self.RAW_CONTENY_CHECK_PATTERNS_NAME in rawContentCheck and \
      isinstance(rawContentCheck[self.RAW_CONTENY_CHECK_PATTERNS_NAME], list) \
      else self.DEFAULT_VALUE_RAW_CONTENY_CHECK_PATTERNS


  # # get rotate value from raw_content_check value
  #
  # @param - None
  # @return rotate value from raw_content_check value
  def getRawContentCheckRotate(self):
    rawContentCheck = self.getRawContentCheck()
    return rawContentCheck[self.RAW_CONTENY_CHECK_ROTATE_NAME] if \
      rawContentCheck is not None and self.RAW_CONTENY_CHECK_ROTATE_NAME in rawContentCheck \
      else self.DEFAULT_VALUE_RAW_CONTENY_CHECK_ROTATE


  # # get faults value from raw_content_check value
  #
  # @param - None
  # @return faults value from raw_content_check value
  def getRawContentCheckFaults(self):
    rawContentCheck = self.getRawContentCheck()
    return rawContentCheck[self.RAW_CONTENY_CHECK_FAULTS_NAME] if \
      rawContentCheck is not None and self.RAW_CONTENY_CHECK_FAULTS_NAME in rawContentCheck \
      else self.DEFAULT_VALUE_RAW_CONTENY_CHECK_FAULTS
