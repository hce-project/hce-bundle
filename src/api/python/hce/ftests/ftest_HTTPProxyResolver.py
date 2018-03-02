#!/usr/bin/python

import sys
import ConfigParser
import logging
from dc_crawler.DBTasksWrapper import DBTasksWrapper
from dc_crawler.DBProxyWrapper import DBProxyWrapper
from dc_crawler.HTTPProxyResolver import HTTPProxyResolver


def getLogger():
  # create logger
  log = logging.getLogger('hce')
  log.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)

  return log


def getDBWrapper(configFileName):
  # variable for result
  ret = None
  try:
    configParser = ConfigParser.ConfigParser()
    configParser.read(configFileName)
    ret = DBTasksWrapper(configParser)
  except Exception, err:
    sys.stderr.write(str(err) + '\n')

  return ret


logger = getLogger()

# # initialization DBProxyWrapper
configFile = '../../ini/db-task.ini'
dbWrapper = getDBWrapper(configFile)
dbProxyWrapper = DBProxyWrapper(dbWrapper)


siteProperty = {"USER_PROXY": "{\"source\": 0,\"file_path\":\"~\/proxy.json\",\"proxies\":{\"84.23.107.195:8080\":{\"host\":\"84.23.107.195:8080\",\"domains\": [\"*\"],\"priority\":11,\"limits\":null}}}" }
siteId = '0'
url = 'localhost'

proxyName = HTTPProxyResolver.getProxy(siteProperties=siteProperty, siteId=siteId, url=url, dbProxyWrapper=dbProxyWrapper)
HTTPProxyResolver.addFaults(siteProperties=siteProperty, siteId=siteId, proxyName=proxyName, dbProxyWrapper=dbProxyWrapper)

logger.info("proxyResolver.getProxy() = %s", str(proxyName))
