#!/usr/bin/python

import os
import json
import logging
import copy
from dc_crawler.ProxyResolver import ProxyResolver

def getLogger():
  # create logger
  log = logging.getLogger('hce')
  log.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)

  return log


class FakeDBWrapper(object):

  TEMPL_ELEMENT = {"Site_Id": None, "Host": None, "Domains": None, "Priority": None, "State": None, "Limits": None}

  def __init__(self):
    self.affect_db = True


  def customRequest(self, query, dbName, includeFieldsNames=None):
    ret = []
    elem = self.TEMPL_ELEMENT
    elem["Site_Id"] = "1"
    elem["Host"] = "ibm.com:9090"
    elem["Domains"] = None
    elem["Priority"] = 1
    elem["State"] = 1
    elem["Limits"] = None
    ret.append(copy.deepcopy(elem))
    elem["Site_Id"] = "1"
    elem["Host"] = "intel.com:11"
    elem["Domains"] = '["*"]'
    elem["Priority"] = 1
    elem["State"] = 1
    elem["Limits"] = '[10, 10, 2]'
    ret.append(copy.deepcopy(elem))
    elem["Site_Id"] = "1"
    elem["Host"] = "intel.com:22"
    elem["Domains"] = '["mazda.com"]'
    elem["Priority"] = 1
    elem["State"] = 1
    elem["Limits"] = '[10, 10, 2]'
    ret.append(copy.deepcopy(elem))
    elem["Site_Id"] = "1"
    elem["Host"] = "intel.com:44"
    elem["Domains"] = '["www.latimes.com"]'
    elem["Priority"] = 1
    elem["State"] = 1
    elem["Limits"] = '[11, 12, 13]'
    ret.append(copy.deepcopy(elem))
    elem["Site_Id"] = "1"
    elem["Host"] = "intel.com:55"
    elem["Domains"] = '["www.latimes.com"]'
    elem["Priority"] = 1
    elem["State"] = 1
    elem["Limits"] = '[11, 12, 13]'
    ret.append(copy.deepcopy(elem))

    return ret


logger = getLogger()

# don't work rotation use frequence
# siteProperties = {"USER_PROXY": "{\"source\": 0,\"file_path\":\"\/tmp\/proxy.json\",\"proxies\":{\"11.23.107.195:8080\":{\"host\":\"11.23.107.195:8080\",\"domains\": [\"*\"],\"priority\":11,\"limits\":null},\"22.23.107.195:8080\":{\"host\":\"22.23.107.195:8080\",\"domains\": [\"*\"],\"priority\":11,\"limits\":null}}}" }
# dbWrapper = None
# siteId = '0'
# url = None
#
# proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
# proxyTuple = proxyResolver.getProxy()
# logger.debug("!!! proxyTuple: %s", str(proxyTuple))


# don't work rotation use frequence
# siteProperties = {"USER_PROXY": "{\"source\": 1,\"file_path\":\"\/tmp\/proxy.json\",\"proxies\":{\"11.23.107.195:8080\":{\"host\":\"11.23.107.195:8080\",\"domains\": [\"*\"],\"priority\":11,\"limits\":null},\"22.23.107.195:8080\":{\"host\":\"22.23.107.195:8080\",\"domains\": [\"*\"],\"priority\":11,\"limits\":null}}}" }
siteProperties = {"USER_PROXY": "{\"source\": 1,\"file_path\":\"\/tmp\/proxy.json\",\"proxies\":{}}" }
dbWrapper = FakeDBWrapper()
siteId = '1'
url = 'http://www.latimes.com/dev/index.html'

proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
proxyTuple = proxyResolver.getProxy()
logger.debug("!!! proxyTuple: %s", str(proxyTuple))


