"""
@package: dc
@file ProxyResolver.py
@author Scorp <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import os
import json
import sys
import time
# import copy

import dbi.EventObjects
from app.Utils import ExceptionLog
from app.Utils import UrlParser
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401
import dc_db.Constants as DB_CONSTS

logger = Utils.MPLogger().getLogger()


# # ProxyResolver Class, implements http proxy resolving functionality
#
class ProxyResolver(object):

  SOURCE_PROPERTY = 0
  SOURCE_SQL = 1

  PROXY_SQL_QUERY = ("SELECT * FROM `sites_proxy` WHERE `State` = 1 AND (`Site_Id` = '%s' OR `Site_Id` = '*')" +
                     " ORDER BY `Priority`")

  PROXY_SQL_UPDATE_FAULTS_QUERY = "UPDATE `sites_proxy` SET `Faults`= %s WHERE `Site_Id` = '%s' AND `Host` = '%s'"
  PROXY_SQL_DISABLE_QUERY = "UPDATE `sites_proxy` SET `State`= 0 WHERE `Site_Id` = '%s' AND `Host` = '%s'"

  PROXY_SQL_DB = "dc_sites"

  LIMITS = ["MIN", "HOUR", "DAY", "MONTH", "YEAR"]
  SECONDS_MULTI = [60, 3600, 86400, 2590000, 31100000]
  DEFAULT_PORT = 80

  JSON_SUFF = ".json"

  STATUS_UPDATE_MIN_ALLOWED_VALUE = 1
  STATUS_UPDATE_MAX_ALLOWED_VALUE = 7

  RAW_CONTENT_CHECK_ROTATE_DEFAULT = 1
  RAW_CONTENT_CHECK_FAULTS_DEFAULT = 1

  # #Class constructor
  #
  # @param siteProperties - incomig sites property dict
  # @param dbWrapper - sql db acces wrapper
  # @param siteId - current site id
  # @param url - current resource url
  def __init__(self, siteProperties, dbWrapper, siteId, url=None):
    self.dbWrapper = dbWrapper
    self.siteId = siteId
    self.source = self.SOURCE_PROPERTY
    self.proxyTuple = None
    self.proxyStruct = None
    self.internalIndexes = {}
    self.domain = UrlParser.getDomain(url) if url is not None else None
    self.indexFileName = None
    proxyJson = None
    # status update passible variables
    self.statusUpdateEmptyProxyList = None
    self.statusUpdateNoAvailableProxy = None
    self.statusUpdateTriesLimit = None
    # raw content check variables
    self.rawContentCheckPatterns = None
    self.rawContentCheckRotate = self.RAW_CONTENT_CHECK_ROTATE_DEFAULT
    self.rawContentCheckFaults = self.RAW_CONTENT_CHECK_FAULTS_DEFAULT

    try:
      if siteProperties is not None:
        if "HTTP_PROXY_HOST" in siteProperties and "HTTP_PROXY_PORT" in siteProperties:
          self.proxyTuple = (siteProperties["HTTP_PROXY_HOST"], siteProperties["HTTP_PROXY_PORT"])
        elif "USER_PROXY" in siteProperties:
          try:
            proxyJson = json.loads(siteProperties["USER_PROXY"])
          except Exception as excp:
            ExceptionLog.handler(logger, excp, ">>> Bad json in USER_PROXY property: " + \
                                 str(siteProperties["USER_PROXY"]))

        # extract 'source' property
        if proxyJson is not None and "source" in proxyJson:
          self.source = int(proxyJson["source"])

          if self.source == self.SOURCE_PROPERTY:
            if "proxies" in proxyJson:
              self.proxyStruct = proxyJson["proxies"]
          elif self.source == self.SOURCE_SQL:
            self.proxyStruct = self.readSQLProxy(dbWrapper, siteId)

        logger.debug('>>> self.proxyStruct: ' + str(self.proxyStruct))

        # set status update different variables
        if proxyJson is not None and "status_update_empty_proxy_list" in proxyJson and \
        int(proxyJson["status_update_empty_proxy_list"]) >= self.STATUS_UPDATE_MIN_ALLOWED_VALUE and \
        int(proxyJson["status_update_empty_proxy_list"]) <= self.STATUS_UPDATE_MAX_ALLOWED_VALUE:
          self.statusUpdateEmptyProxyList = int(proxyJson["status_update_empty_proxy_list"])

        if proxyJson is not None and "status_update_no_available_proxy" in proxyJson and \
        int(proxyJson["status_update_no_available_proxy"]) >= self.STATUS_UPDATE_MIN_ALLOWED_VALUE and \
        int(proxyJson["status_update_no_available_proxy"]) <= self.STATUS_UPDATE_MAX_ALLOWED_VALUE:
          self.statusUpdateNoAvailableProxy = int(proxyJson["status_update_no_available_proxy"])

        if proxyJson is not None and "status_update_tries_limit" in proxyJson and \
        int(proxyJson["status_update_tries_limit"]) >= self.STATUS_UPDATE_MIN_ALLOWED_VALUE and \
        int(proxyJson["status_update_tries_limit"]) <= self.STATUS_UPDATE_MAX_ALLOWED_VALUE:
          self.statusUpdateTriesLimit = int(proxyJson["status_update_tries_limit"])

        # set raw content check different variables
        if proxyJson is not None and "raw_content_check" in proxyJson:
          rawContentCheck = proxyJson["raw_content_check"]
          if "patterns" in rawContentCheck:
            self.rawContentCheckPatterns = rawContentCheck["patterns"]
            if "rotate" in rawContentCheck:
              self.rawContentCheckRotate = int(rawContentCheck["rotate"])
            if "faults" in rawContentCheck:
              self.rawContentCheckFaults = int(rawContentCheck["faults"])
          else:
            logger.error("Mandatory parameter 'patterns' for 'raw_content_check' not found")

      if self.proxyTuple is None and proxyJson is not None:
        if "file_path" in proxyJson:
          self.indexFileName = proxyJson["file_path"]
          if siteId is not None and not (self.indexFileName.find(self.JSON_SUFF) != -1 and \
          self.indexFileName.find(self.JSON_SUFF) == len(self.indexFileName) - len(self.JSON_SUFF)):
            if self.indexFileName[-1] != '/':
              self.indexFileName += '/'
            self.indexFileName += siteId
            self.indexFileName += self.JSON_SUFF

          # logger.debug('>>> self.indexFileName: ' + str(self.indexFileName))
          self.internalIndexes = self.readIndexFile(self.indexFileName)

          # logger.debug('>>> self.proxyStruct: ' + str(self.proxyStruct))
          # logger.debug('>>> self.internalIndexes: ' + str(self.internalIndexes))

          if self.proxyStruct is not None:
            for key in self.proxyStruct.keys():
              if key in self.internalIndexes:
                self.proxyStruct[key].update(self.internalIndexes[key])

            # for key in self.internalIndexes:
            #  if key not in self.proxyStruct:
            #    self.proxyStruct.update({key:self.internalIndexes[key]})
            # logger.debug('>>> self.proxyStruct2: ' + str(self.proxyStruct))


    except Exception as err:
      ExceptionLog.handler(logger, err, ">>> ProxyResolver exception", (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})


  # #Method readIndexFile reads from file and return param index structure
  #
  # @param fileName - incoming file name
  # @return json structure, just readed from file
  @staticmethod
  def readIndexFile(fileName):
    ret = {}
    if os.path.isfile(fileName):
      fd = None
      try:
        fd = open(fileName, "r")
        if fd is not None:
          fileData = fd.read()
          logger.debug('>>> readIndexFile fileData: ' + str(fileData) + ' length: ' + str(len(fileData)) + ' bytes.')
          ret = json.loads(str(fileData))

          # logger.debug('>>> readIndexFile ret: ' + str(ret))
          fd.close()
      except Exception as excp:
        ExceptionLog.handler(logger, excp, ">>> readIndexFile error, file name = " + str(fileName))
        if fd is not None:
          fd.close()

    return ret


  # #Method saveIndexInFile saves indexes structute into the file
  #
  # @param fileName - incoming file name
  # @param jsonData - output data in json format for save to file
  # @return None
  @staticmethod
  def saveIndexInFile(fileName, jsonData):
    if jsonData is not None and len(jsonData) > 0:
      fd = None
      try:
        # logger.debug('jsonData: ' + str(jsonData))
        fileData = json.dumps(jsonData)
        fd = open(fileName, "w")
        if fd is not None:
          fd.write(fileData)
          fd.close()
      except Exception as excp:
        ExceptionLog.handler(logger, excp, ">>> saveIndexInFile error, file name = " + str(fileName))


#   # #Method fieldsToLower return dict, which is copy of elem with lowercase keys
#   #
#   # @param elem incoming dict
#   # @return lowcase dict
#   def fieldsToLower(self, elem):
#     ret = {}
#     for key in elem:
#       ret[key.lower()] = elem[key]
#     return ret


  # #Method fieldsToObjectName return dict, which is copy of elem with names using in objects
  #
  # @param inDict - incoming dict
  # @return lowcase dict
  def fieldsToObjectName(self, inDict):
    # variable for result value
    ret = {}
    for fieldName in inDict:
      for key, value in DB_CONSTS.ProxyTableDict.items():
        if value == fieldName:
          ret[key] = inDict[fieldName]
          break

    return ret


  # #Method readSQLProxy, reads proxy data from SQL storage
  #
  # @param dbWrapper - sql db acces wrapper
  # @param siteId - current site id
  # @return just fetched proxy data
  def readSQLProxy(self, dbWrapper, siteId):
    ret = {}
    saveDBMode = dbWrapper.affect_db
    dbWrapper.affect_db = True
    result = dbWrapper.customRequest(self.PROXY_SQL_QUERY % siteId, self.PROXY_SQL_DB,
                                     dbi.EventObjects.CustomRequest.SQL_BY_NAME)
    dbWrapper.affect_db = saveDBMode
    if result is not None and len(result) > 0:
      for elem in result:
        elemInLower = self.fieldsToObjectName(elem)  # self.fieldsToLower(elem)
        ret[elemInLower["host"]] = elemInLower
        # ret[elem["host"]]["freq"] = 0
        # #logger.debug('readSQLProxy  ret: ' + varDump(ret))

        try:
          if "limits" in ret[elemInLower["host"]] and ret[elemInLower["host"]]["limits"] is not None:
            if not ret[elemInLower["host"]]["limits"]:
              ret[elemInLower["host"]]["limits"] = []
            else:
              ret[elemInLower["host"]]["limits"] = json.loads(ret[elemInLower["host"]]["limits"])
        except Exception, err:
          ExceptionLog.handler(logger, err, ">>> Wrong json in 'limits': " + \
                               varDump(ret[elemInLower["host"]]["limits"]) + \
                               ", host = " + (elem["host"] if "host" in elem else "None"))
        try:
          if "domains" in ret[elemInLower["host"]] and ret[elemInLower["host"]]["domains"] is not None:
            if ret[elemInLower["host"]]["domains"] == "":
              ret[elemInLower["host"]]["domains"] = ['*']
            else:
              ret[elemInLower["host"]]["domains"] = json.loads(ret[elemInLower["host"]]["domains"])
        except Exception as err:
          ExceptionLog.handler(logger, err, ">>> Wrong json in 'domains': " + \
                               varDump(ret[elemInLower["host"]]["domains"]) + ", host = " +
                               (elem["host"] if "host" in elem else "None"))
        try:
          if "cDate" in ret[elemInLower["host"]] and ret[elemInLower["host"]]["cDate"] is not None:
            ret[elemInLower["host"]]["cDate"] = str(ret[elemInLower["host"]]["cDate"])
        except Exception as err:
          ExceptionLog.handler(logger, err, ">>> Wrong json in 'cDate': " + \
                               varDump(ret[elemInLower["host"]]["cDate"]) + ", host = " +
                               (elem["host"] if "host" in elem else "None"))
        try:
          if "uDate" in ret[elemInLower["host"]] and ret[elemInLower["host"]]["uDate"] is not None:
            ret[elemInLower["host"]]["uDate"] = str(ret[elemInLower["host"]]["uDate"])
        except Exception as err:
          ExceptionLog.handler(logger, err, ">>> Wrong json in 'uDate': " + \
                               varDump(ret[elemInLower["host"]]["uDate"]) + ", host = " +
                               (elem["host"] if "host" in elem else "None"))

    return ret


#   # #Method updateProxyByFreqAndLimits, updates (if available) freq statistic in common proxy structure
#   #
#   def updateProxyByFreqAndLimits(self, proxyName):
#     logger.debug('>>> updateProxyByFreqAndLimits enter...')
#     # logger.debug('>>> self.proxyStruct: ' + str(self.proxyStruct))
#     logger.debug('>>> self.internalIndexes: ' + str(self.internalIndexes))
#     if self.proxyStruct is not None:
#       for key in self.proxyStruct:
#         if key == proxyName:
#           if key in self.internalIndexes:
#             logger.debug('>>> if key in self.internalIndexes')
#             if "freq" in self.internalIndexes[key]:
#               logger.debug('>>> if "freq" in self.internalIndexes[key]')
#               self.proxyStruct[key]["freq"] = self.internalIndexes[key]["freq"]
#             else:
#               logger.debug('>>> else1')
#               if "freq" in self.proxyStruct[key]:
#                 logger.debug('>>> if "freq" in self.proxyStruct[key]')
#                 self.proxyStruct[key]["freq"] += 1
#               else:
#                 logger.debug('>>> else2')
#                 self.proxyStruct[key].update({"freq":1})
#
#             if "limits_stat" in self.internalIndexes[key]:
#               self.proxyStruct[key]["limits_stat"] = copy.deepcopy(self.internalIndexes[key]["limits_stat"])
#             else:
#               self.proxyStruct[key].update({"limits_stat":{}})
#           else:
#             if "freq" in self.proxyStruct[key]:
#               logger.debug('>>> if "freq" in self.proxyStruct[key]')
#               self.proxyStruct[key]["freq"] += 1
#             else:
#               logger.debug('>>> else3')
#               self.proxyStruct[key]["freq"] = 1  # sys.maxint
#
#             if not "limits_stat" in self.proxyStruct[key]:
#               self.proxyStruct[key]["limits_stat"] = {}
#
#       # logger.debug('>>> self.proxyStruct: ' + str(self.proxyStruct))


  # #Method checkLimits, checks freq limits for current proxy
  #
  # @param key - proxy key
  # @return bool value - is available proxy by limits or not
  def checkLimits(self, key):
    ret = True
    if key in self.proxyStruct and "limits" in self.proxyStruct[key] and \
     self.proxyStruct[key]["limits"] is not None and \
    "limits_stat" in self.proxyStruct[key] and \
    isinstance(self.proxyStruct[key]["limits_stat"], dict) and \
    len(self.proxyStruct[key]["limits_stat"]) > 0:
      index = 0
      curTimeStamp = int(time.time())
      for limit in self.proxyStruct[key]["limits"]:
        if index >= len(self.LIMITS):
          break
        if self.LIMITS[index] + "_START_POINT" in self.proxyStruct[key]["limits_stat"]:
          if curTimeStamp - self.proxyStruct[key]["limits_stat"][self.LIMITS[index] + "_START_POINT"] >= \
          self.SECONDS_MULTI[index]:
            self.proxyStruct[key]["limits_stat"][self.LIMITS[index] + "_START_POINT"] = curTimeStamp
            self.proxyStruct[key]["limits_stat"][self.LIMITS[index] + "_FREQ"] = 0
        if limit > 0 and self.LIMITS[index] + "_FREQ" in self.proxyStruct[key]["limits_stat"] and \
        self.proxyStruct[key]["limits_stat"][self.LIMITS[index] + "_FREQ"] >= limit:
          ret = False
          break
        index += 1
    return ret


  # #Method checkLimits, checks available domains for current proxy
  #
  # @param key - proxy key
  # @return bool value - is available proxy by domain or not
  def checkDomains(self, key):
    ret = True
    if self.domain is not None and key in self.proxyStruct and "domains" in self.proxyStruct[key] and \
    self.proxyStruct[key]["domains"] is not None \
    and self.domain not in self.proxyStruct[key]["domains"] and '*' not in self.proxyStruct[key]["domains"]:
      ret = False
    return ret


  # #Method commonIncrementLimits, method increments freq fields in common type container
  #
  # @param container - incoming container
  # @param key - proxy key
  def commonIncrementLimits(self, container, key):
    logger.debug('>>> commonIncrementLimits enter...')
    if key in container:
      if "freq" in container[key]:
        logger.debug('>>> container[key]["freq"] += 1')
        container[key]["freq"] += 1
      else:
        logger.debug('>>> container[key].update({"freq":1})')
        container[key].update({"freq":1})

      if "limits_stat" in container[key] and len(container[key]["limits_stat"]) > 0:
        for elem in self.LIMITS:
          if elem + "_FREQ" in container[key]["limits_stat"]:
            container[key]["limits_stat"][elem + "_FREQ"] += 1
      else:
        logger.debug('>>> container[key].update({"limits_stat":{}})')
        container[key].update({"limits_stat":{}})

    else:
      container.update({key:{"host":key, "freq":1, "limits_stat":{}}})


  # #Method incrementLimits increments freq firlds in proxyStruct and internalIndexes containers
  #
  # @param key - proxy key
  def incrementLimits(self, key):
    self.commonIncrementLimits(self.proxyStruct, key)


  # #Method fillProxyTuple - fills and returns proxy tuple
  #
  # @param elem - incoming proxy data in raw (string format)
  # @return resolver proxy (as pair tuple (host, port)) or None
  def fillProxyTuple(self, elem):
    ret = None
    if len(elem["host"].split(':')) > 1:
      ret = (elem["host"].split(':')[0], elem["host"].split(':')[1])
    else:
      ret = (elem["host"].split(':')[0], self.DEFAULT_PORT)
    return ret


  # #Method getProxy - public method which implements main proxy resolver functionality
  #
  # @param previousProxy - previously returned proxy
  # @return resolver proxy (as pair tuple (host, port)) or None
  def getProxy(self, previousProxy=None):
    logger.debug('>>> getProxy enter...')
    ret = None
    saveIndexFile = False
    if self.proxyTuple is not None:
      ret = self.proxyTuple
    elif self.proxyStruct is not None:
      logger.debug('>>> elif self.proxyStruct is not None')
      if previousProxy is None and "priority" in self.proxyStruct:
        logger.debug('>>> previousProxy is None')
        for elem in sorted(self.proxyStruct.values(), key=lambda x: x["freq"] + \
                           x["priority"] * sys.maxint if "freq" in x else x["priority"]):
          if self.checkLimits(elem["host"]) and self.checkDomains(elem["host"]):
            logger.debug('>>> if self.checkLimits(elem["host"]) and self.checkDomains(elem["host"])')
            ret = self.fillProxyTuple(elem)
            self.incrementLimits(elem["host"])
            saveIndexFile = True
            break
      else:
        logger.debug('>>> else')
        for elem in self.proxyStruct.values():
          logger.debug('>>> self.checkLimits: ' + str(bool(self.checkLimits(elem["host"]))))
          logger.debug('>>> self.checkDomains: ' + str(bool(self.checkDomains(elem["host"]))))

          if self.checkLimits(elem["host"]) and self.checkDomains(elem["host"]):
            ret = self.fillProxyTuple(elem)
            self.incrementLimits(elem["host"])
            saveIndexFile = True
            break
          # tmpRes = self.fillProxyTuple(elem)
          # if (tmpRes[0] != previousProxy[1] or tmpRes[1] != previousProxy[2]) and len(self.proxyStruct) > 1:
          #  tmpRes = None

    logger.debug('>>> self.indexFileName: ' + str(self.indexFileName))
    logger.debug('>>> saveIndexFile: ' + str(saveIndexFile))

    if saveIndexFile and self.indexFileName is not None:
      self.saveIndexInFile(self.indexFileName, self.proxyStruct)

    logger.debug('>>> getProxy leave... ret: ' + str(ret))
    return ret


  # #getTriesCount class's static method, parse and returns tries_count value from USER_PROXY property
  #
  # @param siteProperties - incomig sites property dict
  # @return tries_count value or None
  @staticmethod
  def getTriesCount(siteProperties):
    ret = None
    if "USER_PROXY" in siteProperties:
      try:
        proxyJson = json.loads(siteProperties["USER_PROXY"])
        if "tries_count" in proxyJson:
          ret = int(proxyJson["tries_count"])
      except Exception as excp:
        ExceptionLog.handler(logger, excp, ">>> Bad json in USER_PROXY property: " + str(siteProperties["USER_PROXY"]))
    return ret


  # #Add fault proxy
  #
  # @param proxyName - proxy host name
  # @param incrementSize - value for increment of faults counter
  # @return - None
  def addFault(self, proxyName, incrementSize=1):
    logger.debug('addFault enter ... proxyName: ' + str(proxyName))
    if proxyName in self.proxyStruct and "faultsMax" in self.proxyStruct[proxyName] and \
    "faults" in self.proxyStruct[proxyName]:
      faultsMax = int(self.proxyStruct[proxyName]["faultsMax"])
      faults = int(self.proxyStruct[proxyName]["faults"])
      faults += incrementSize
      self.proxyStruct[proxyName].update({"faults":faults})
      if self.source == self.SOURCE_SQL:
        saveDBMode = self.dbWrapper.affect_db
        self.dbWrapper.affect_db = True
        result = self.dbWrapper.customRequest(self.PROXY_SQL_UPDATE_FAULTS_QUERY % (faults, self.siteId, proxyName),
                                              self.PROXY_SQL_DB,
                                              dbi.EventObjects.CustomRequest.SQL_BY_NAME)
        self.dbWrapper.affect_db = saveDBMode
        logger.debug('customRequest result: ' + varDump(result))

      if faultsMax > 0 and faults >= faultsMax:
        self.proxyStruct[proxyName].update({"state":0})

        if self.source == self.SOURCE_SQL:
          saveDBMode = self.dbWrapper.affect_db
          self.dbWrapper.affect_db = True
          result = self.dbWrapper.customRequest(self.PROXY_SQL_DISABLE_QUERY % (self.siteId, proxyName),
                                                self.PROXY_SQL_DB,
                                                dbi.EventObjects.CustomRequest.SQL_BY_NAME)
          self.dbWrapper.affect_db = saveDBMode
          logger.debug('customRequest result: ' + varDump(result))

      self.saveIndexInFile(self.indexFileName, self.proxyStruct)


  # # Check is empty proxies list
  #
  # @param - None
  # @return True in case of empty list, otherwise False
  def isEmptyProxiesList(self):
    # variable for result
    ret = False
    if self.proxyStruct is None or len(self.proxyStruct) == 0:
      ret = True

    return ret


  # # Check raw content use regular expression patterns
  #
  # @param rawContent - raw content for check
  # @return boolean flag - True if raw content has match or False otherwise
  def checkPattern(self, rawContent):
    # variable for result
    ret = True
    if rawContent is not None and isinstance(self.rawContentCheckPatterns, list):
      ret = False
      for pattern in self.rawContentCheckPatterns:
        if re.search(pattern, rawContent, re.M | re.U) is not None:
          ret = True
          break

    return ret
