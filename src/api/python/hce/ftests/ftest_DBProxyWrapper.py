#!/usr/bin/python

import sys
import ConfigParser
import logging
from app.Utils import varDump
from dc_crawler.DBTasksWrapper import DBTasksWrapper
from dc_crawler.DBProxyWrapper import DBProxyWrapper
import dbi.EventObjects as dbi_event

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



configFile = '../../ini/db-task.ini'

dbWrapper = getDBWrapper(configFile)
proxyWrapper = DBProxyWrapper(dbWrapper)

# res = proxyWrapper.getEnaibledProxies('0')
#
# siteId = None
# host = None
# faults = None
# print varDump(res)
# for proxy in res:
#   siteId = proxy.siteId
#   host = proxy.host
#   faults = proxy.faults
#
# print 'siteId = ', siteId, ' host: ', host

# res = proxyWrapper.addFault(siteId, host)
# print varDump(res)

# res = proxyWrapper.disableProxy(siteId, host)
# print varDump(res)

query = "SELECT Domain, Count, Date FROM site_5367c2aa49849cb1056eb8dd5ffa3e28 WHERE Domain = 'bbc.com'"
dbName = "dc_stat_domains"
res = dbWrapper.customRequest(query, dbName, dbi_event.CustomRequest.SQL_BY_NAME)

print res
