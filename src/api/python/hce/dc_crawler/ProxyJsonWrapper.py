# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
It's wrapper proxy data struct.

@package: dc_crawler
@file ProxyJsonWrapper.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

from dc.EventObjects import Proxy


class ProxyJsonWrapper(object):
  # #Constants used in class
  PROXIES_HOST_NAME = 'host'
  PROXIES_DOMAINS_NAME = 'domains'
  PROXIES_PRIORITY_NAME = 'priority'
  PROXIES_LIMITS_NAME = 'limits'
  PROXIES_STATE_NAME = 'state'
  PROXIES_FREQ_NAME = 'freq'
  PROXIES_FAULTS_NAME = 'faults'
  PROXIES_FAULTS_MAX_NAME = 'faultsMax'

  PROXIES_DATA_LIST_NAMES = [PROXIES_HOST_NAME, PROXIES_DOMAINS_NAME, PROXIES_PRIORITY_NAME, PROXIES_LIMITS_NAME, \
                             PROXIES_STATE_NAME, PROXIES_FREQ_NAME, PROXIES_FAULTS_NAME, PROXIES_FAULTS_MAX_NAME]
  # support state values
  PROXY_STATE_DISABLED = 0
  PROXY_STATE_ENABLED = 1

  DEFAULT_VALUE_JSON_DATA = {}
  DEFAULT_VALUE_PROXIES_DOMAIN = ['*']
  DEFAULT_VALUE_PROXIES_PRIORITY = 10
  DEFAULT_VALUE_PROXIES_LIMITS = None
  DEFAULT_VALUE_PROXIES_STATE = PROXY_STATE_ENABLED
  DEFAULT_VALUE_PROXIES_FREQ = 0
  DEFAULT_VALUE_PROXIES_FAULTS = 0
  DEFAULT_VALUE_PROXIES_FAULTS_MAX = 0

  DEFAULT_VALUE_INCREMENT_FREQUENCY = 1
  DEFAULT_VALUE_INCREMENT_FAULTS = 1
  DEFAULT_VALUE_UNLIMITED_FAULTS_MAX = 0


  # # Initialization
  #
  # @param jsonData - json data
  def __init__(self, jsonData):
    self.jsonData = (jsonData if isinstance(jsonData, dict) else self.DEFAULT_VALUE_JSON_DATA)


  # # set proxies data value to json
  #
  # @param proxyData - proxy data value
  # @return - None
  def setProxyData(self, proxyData):
    if isinstance(proxyData, dict):
      if self.PROXIES_HOST_NAME in proxyData.keys() and proxyData[self.PROXIES_HOST_NAME] not in self.jsonData:

        proxyData[self.PROXIES_DOMAINS_NAME] = proxyData[self.PROXIES_DOMAINS_NAME] \
          if self.PROXIES_PRIORITY_NAME in proxyData.keys() and proxyData[self.PROXIES_DOMAINS_NAME] is not None \
            and len(proxyData[self.PROXIES_DOMAINS_NAME]) > 0 else self.DEFAULT_VALUE_PROXIES_DOMAIN

        proxyData[self.PROXIES_PRIORITY_NAME] = proxyData[self.PROXIES_PRIORITY_NAME] \
          if self.PROXIES_PRIORITY_NAME in proxyData.keys() and proxyData[self.PROXIES_PRIORITY_NAME] is not None \
          and int(proxyData[self.PROXIES_PRIORITY_NAME]) > 0 else self.DEFAULT_VALUE_PROXIES_PRIORITY

        proxyData[self.PROXIES_LIMITS_NAME] = proxyData[self.PROXIES_LIMITS_NAME] \
          if self.PROXIES_LIMITS_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_LIMITS

        proxyData[self.PROXIES_STATE_NAME] = proxyData[self.PROXIES_STATE_NAME] \
          if self.PROXIES_STATE_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_STATE

        proxyData[self.PROXIES_FREQ_NAME] = proxyData[self.PROXIES_FREQ_NAME] \
          if self.PROXIES_FREQ_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_FREQ

        proxyData[self.PROXIES_FAULTS_NAME] = proxyData[self.PROXIES_FAULTS_NAME] \
          if self.PROXIES_FAULTS_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_FAULTS

        proxyData[self.PROXIES_FAULTS_MAX_NAME] = proxyData[self.PROXIES_FAULTS_MAX_NAME] \
          if self.PROXIES_FAULTS_MAX_NAME in proxyData.keys() else self.DEFAULT_VALUE_PROXIES_FAULTS_MAX

        self.jsonData[proxyData[self.PROXIES_HOST_NAME]] = proxyData


  # # get proxies data value from json
  #
  # @param proxyName - proxy name
  # @return - proxy data value
  def getProxyData(self, proxyName):
    # variable for result
    ret = None
    if proxyName in self.jsonData:
      ret = self.jsonData[proxyName]

    return ret


  # # get full json data
  #
  # @param - None
  # @return json data
  def getData(self):
    return self.jsonData


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
  # @param state - state of proxy (default value None return full list enabled and disabled proxies)
  # @return list of Proxy objects
  def getProxyList(self, state=None):
    # variable for result
    proxyList = []

    for proxyName in self.jsonData.keys():
      proxyData = self.getProxyData(proxyName)

      proxy = Proxy(siteId='0', host='')
      for name in self.PROXIES_DATA_LIST_NAMES:
        if name in proxyData:
          setattr(proxy, name, proxyData[name])

      if self.PROXIES_FREQ_NAME in proxyData:
        setattr(proxy, self.PROXIES_FREQ_NAME, int(proxyData[self.PROXIES_FREQ_NAME]))

      if proxy.host != "" and (proxy.state == state if state is not None else True):
        proxyList.append(proxy)

    return proxyList


  # # add frequency value for proxy
  #
  # @param proxyName - proxy name
  # @param incrementSize - value for increment of frequency counter
  def addFrequency(self, proxyName, incrementSize=DEFAULT_VALUE_INCREMENT_FREQUENCY):
    proxyData = self.getProxyData(proxyName)
    if proxyData is not None:
      # increment frequency counter
      frequency = int(proxyData[self.PROXIES_FREQ_NAME]) if self.PROXIES_FREQ_NAME in proxyData \
                  else self.DEFAULT_VALUE_PROXIES_FREQ
      frequency += int(incrementSize)
      proxyData[self.PROXIES_FREQ_NAME] = frequency

      # apply changes
      self.setProxyData(proxyData)


  # # add faults to counter
  #
  # @param proxyName - proxy host name
  # @param incrementSize - value for increment of faults counter
  # @return - None
  def addFaults(self, proxyName, incrementSize=DEFAULT_VALUE_INCREMENT_FAULTS):
    proxyData = self.getProxyData(proxyName)
    if proxyData is not None:
      # increment faults counter
      faults = int(proxyData[self.PROXIES_FAULTS_NAME]) if self.PROXIES_FAULTS_NAME in proxyData \
               else self.DEFAULT_VALUE_PROXIES_FAULTS
      faults += incrementSize
      proxyData[self.PROXIES_FAULTS_NAME] = faults

      # get faults max value
      faultsMax = int(proxyData[self.PROXIES_FAULTS_MAX_NAME]) if self.PROXIES_FAULTS_MAX_NAME in proxyData \
                  else self.DEFAULT_VALUE_PROXIES_FAULTS_MAX

      # check max allowed faults and disable if necessary
      if faultsMax != self.DEFAULT_VALUE_UNLIMITED_FAULTS_MAX and faults >= faultsMax:
        # disable proxy
        proxyData[self.PROXIES_STATE_NAME] = self.PROXY_STATE_DISABLED

      # apply changes
      self.setProxyData(proxyData)
