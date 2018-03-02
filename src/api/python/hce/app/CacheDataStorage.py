# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Cache data storage main functional.

@package: app
@file CacheDataStorage.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2018 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import copy
import json
import hashlib
import warnings
import ConfigParser
import MySQLdb as mdb
import MySQLdb.cursors

import app.Consts as APP_CONSTS
import app.Utils as Utils

class CacheDataStorage(object):
  # # Constants error messages used in class
  MSG_ERROR_MISSED_SECTION = "Missed mandatory section '%s'"
  MSG_ERROR_MAKE_DB_CONNECTIONS = "Error creation db connections: %s"
  MSG_ERROR_SQL_QUERY_EXECUTION = "Error: %s of the query '%s' executions"
  MSG_ERROR_LOAD_CACHED_DATA = "Load cached data failed. Error: %s"
  MSG_ERROR_SAVE_CACHED_DATA = "Save cached data failed. Error: %s"
  MSG_ERROR_GET_CONFIG_OPTIONS = "Get configuration options failed. Error: %s"
  MSG_ERROR_INPUT_PARAMETER = "Wrong input parameter."

  # Constants used in class
  DEFAULT_UPDATE_TABLE_FIELDS_VALUE = "NULL"
  DEFAULT_UPDATE_TABLE_ALL_FIELDS_PATTERN = '%\w+%'


  # # Internal class for save and fast search items data
  class ItemsDataDict(object):
    # # Initialization
    def __init__(self, uniqueKeyName, cachedFieldName):
      self.uniqueKeyName = uniqueKeyName
      self.cachedFieldName = cachedFieldName
      self.jsonDict = {}


    # # Add data to internal dict
    #
    # @param kwarg - parameters dictionary
    # @return - None
    def add(self, **kwarg):
      if isinstance(self.uniqueKeyName, basestring) and self.uniqueKeyName in kwarg:
        dataDict = {}
        for key, value in kwarg.items():
          dataDict[key] = value

        self.jsonDict[kwarg[self.uniqueKeyName]] = dataDict


    # # Get items from internal dict
    #
    # @param - None
    # @return dictionary values
    def items(self):
      return self.jsonDict.items()


    # # Get keys from internal dict
    #
    # @param - None
    # @return dictionary values
    def getKeys(self):
      return self.jsonDict.keys()


    # # Get values from internal dict
    #
    # @param - None
    # @return dictionary values
    def getValues(self):
      return self.jsonDict.values()


    # # Get size of item data dict
    #
    # @param - None
    # @return count of elements in item data dict
    def getSize(self):
      return len(self.jsonDict)
    
    
    ## Update from other items data dict
    #
    # @param itemsDataDict - items data dict
    # @return - None
    def update(self, itemsDataDict):
      if isinstance(itemsDataDict, CacheDataStorage.ItemsDataDict):
        self.jsonDict.update(itemsDataDict.jsonDict)


    # # Set cached data
    #
    # @param kwarg - parameters dictionary. Sample: (urlmd5='123', cachedData={})
    # @return - None
    def setCachedData(self, **kwarg):
      if self.uniqueKeyName in kwarg and kwarg[self.uniqueKeyName] in self.jsonDict and self.cachedFieldName in self.jsonDict[kwarg[self.uniqueKeyName]] and \
        self.cachedFieldName in kwarg and isinstance(kwarg[self.cachedFieldName], dict):
        self.jsonDict[kwarg[self.uniqueKeyName]][self.cachedFieldName] = kwarg[self.cachedFieldName]


    # # Get cached data
    #
    # @param kwarg - parameters dictionary. Sample: (urlmd5='123')
    # @return - cached data if exist or empty dict
    def getCachedData(self, **kwarg):
      # variable for result
      cachedData = {}

      if self.uniqueKeyName in kwarg and kwarg[self.uniqueKeyName] in self.jsonDict and self.cachedFieldName in self.jsonDict[kwarg[self.uniqueKeyName]] and \
        isinstance(self.jsonDict[kwarg[self.uniqueKeyName]][self.cachedFieldName], dict):
        cachedData = self.jsonDict[kwarg[self.uniqueKeyName]][self.cachedFieldName]

      return cachedData


    # # add cached data from other items data dict
    #
    # @param itemsDataDict - items data dict
    # @return - None
    def addCachedData(self, itemsDataDict):
      if isinstance(itemsDataDict, CacheDataStorage.ItemsDataDict):
        for dataDict in itemsDataDict.getValues():
          if isinstance(dataDict, dict):
            self.setCachedData(**dataDict)


  # # Internal class for database options from config
  class DBConnectionOptions(object):
    # # Constans used options from config file
    CONFIG_OPTION_DB_HOST = "db_host"
    CONFIG_OPTION_DB_PORT = "db_port"
    CONFIG_OPTION_DB_USER = "db_user"
    CONFIG_OPTION_DB_PWD = "db_pwd"
    CONFIG_OPTION_DB_CHARSET = "db_charset"

    DEFAULT_VALUE_DB_CHARSET = 'utf8'

    def __init__(self):
      self.dbHost = None
      self.dbPort = None
      self.dbUser = None
      self.dbPwd = None
      self.dbCharset = self.DEFAULT_VALUE_DB_CHARSET


  # # Config options internal class
  class ConfigOptions(object):
    # # Constans used options from config file
    CONFIG_OPTION_UNIQUE_KEY_NAME = "uniqueKeyName"
    CONFIG_OPTION_CACHED_FIELD_NAME = "cachedFieldName"
    CONFIG_OPTION_SELECT_QUERY = "selectQuery"
    CONFIG_OPTION_INSERT_QUERY = "insertQuery"
    CONFIG_OPTION_DELETE_QUERY = "deleteQuery"
    CONFIG_OPTION_CACHE_DB_NAME = "SocialDataCacheDB"
    CONFIG_OPTION_MACRO_NAMES_MAP = "macroNamesMap"  

    def __init__(self):
      self.uniqueKeyName = None
      self.cachedFieldName = None
      self.selectQuery = None
      self.insertQuery = None
      self.deleteQuery = None
      self.dbDataCacheName = None
      self.dbConnectionOptions = None
      self.macroNamesMap = None


  # # Initialization of class
  #
  # @param configOptionsExtractor - it can be config parser instance or callback function for getting config options
  # @param log - logger instance
  # @param delayInit - boolean flag in mean delay initialization
  def __init__(self, configOptionsExtractor, log, delayInit=False):
    self.logger = log
    self.configOptions = self.getConfigOptions(configOptionsExtractor)
    self.dbConnection = None
    
    if not delayInit:
      self.init()


  # # Initialization
  #
  # @param - None
  # @return - None
  def init(self):
    try:
      self.dbConnection = self.makeConnection(self.configOptions.dbConnectionOptions, self.configOptions.dbDataCacheName)
    except Exception, err:
      self.logger.error(str(err))

  
  # # Get config options
  #
  # @param configOptionsExtractor - it can be config parser instance or callback function for getting config options
  # @return confgi options instance
  def getConfigOptions(self, configOptionsExtractor):
    # variable for result
    configOptions = CacheDataStorage.ConfigOptions()

    try:
      getConfigOption = None

      if isinstance(configOptionsExtractor, ConfigParser.RawConfigParser):
        getConfigOption = configOptionsExtractor.get
      elif callable(configOptionsExtractor):
        getConfigOption = configOptionsExtractor
      else:
        raise Exception(CacheDataStorage.MSG_ERROR_INPUT_PARAMETER)

      configOptions.uniqueKeyName = str(getConfigOption(self.__class__.__name__, CacheDataStorage.ConfigOptions.CONFIG_OPTION_UNIQUE_KEY_NAME))
      configOptions.cachedFieldName = str(getConfigOption(self.__class__.__name__, CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHED_FIELD_NAME))
      configOptions.selectQuery = str(getConfigOption(self.__class__.__name__, CacheDataStorage.ConfigOptions.CONFIG_OPTION_SELECT_QUERY))
      configOptions.insertQuery = str(getConfigOption(self.__class__.__name__, CacheDataStorage.ConfigOptions.CONFIG_OPTION_INSERT_QUERY))
      configOptions.deleteQuery = str(getConfigOption(self.__class__.__name__, CacheDataStorage.ConfigOptions.CONFIG_OPTION_DELETE_QUERY))
      configOptions.dbDataCacheName = str(getConfigOption(self.__class__.__name__, CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME))
      configOptions.dbConnectionOptions = self.loadDBConnectionOptions(configOptionsExtractor,
                                                                       CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME)
      configOptions.macroNamesMap = Utils.jsonLoadsSafe(jsonString=getConfigOption(self.__class__.__name__, \
                                    CacheDataStorage.ConfigOptions.CONFIG_OPTION_MACRO_NAMES_MAP), default={}, log=self.logger)
    except Exception, err:
        self.logger.error(CacheDataStorage.MSG_ERROR_GET_CONFIG_OPTIONS, str(err))
        self.logger.info(Utils.getTracebackInfo())

    return configOptions


  # # load database connection options use config parser
  #
  # @param configOptionsExtractor - it can be config parser instance or callback function for getting config options
  # @param dbName - database name
  # @return - DBConnectionOptions instance
  def loadDBConnectionOptions(self, configOptionsExtractor, dbName):
    # check type of the config extractor
    getConfigOption = None
    if isinstance(configOptionsExtractor, ConfigParser.RawConfigParser):
      getConfigOption = configOptionsExtractor.get
    elif callable(configOptionsExtractor):
      getConfigOption = configOptionsExtractor
    else:
      raise Exception(CacheDataStorage.MSG_ERROR_INPUT_PARAMETER)

    connectionOptions = CacheDataStorage.DBConnectionOptions()
    connectionOptions.dbHost = str(getConfigOption(dbName, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_HOST))
    connectionOptions.dbPort = int(getConfigOption(dbName, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_PORT))
    connectionOptions.dbUser = str(getConfigOption(dbName, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_USER))
    connectionOptions.dbPwd = str(getConfigOption(dbName, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_PWD))
    # option if not set use default 'utf-8'
    try:
      connectionOptions.dbCharset = str(getConfigOption(dbName, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_CHARSET))
    except Exception, err:
      self.logger.debug("%s. Use default value '%s'", str(err), str(connectionOptions.dbCharset))

    return connectionOptions


  # # make one database connection
  #
  # @param connectionOptions - connection options structure
  # @param dbName - database name
  # @return created database connection
  def makeConnection(self, connectionOptions, dbName):
    # variable for result
    dbConnection = None
    try:
      dbConnection = mdb.connect(connectionOptions.dbHost,
                                 connectionOptions.dbUser,
                                 connectionOptions.dbPwd,
                                 dbName,
                                 connectionOptions.dbPort,
                                 charset=connectionOptions.dbCharset)
    except mdb.Error, err:
      raise Exception(self.MSG_ERROR_MAKE_DB_CONNECTIONS % str(err))

    return dbConnection


  # # Execute sql query
  #
  # @param query - sql query for execution
  # @return result execution
  def executeQuery(self, query):
    # variable for result
    ret = None
    try:
      if query is not None and query != "":
        with warnings.catch_warnings(record=True) as warn:
          warnings.simplefilter("always")

          with self.dbConnection:
            cursor = self.dbConnection.cursor(MySQLdb.cursors.DictCursor)
            affectedRows = cursor.execute(query)
            self.dbConnection.commit()
            ret = cursor.fetchall()

            self.logger.debug("affectedRows = %s", str(affectedRows))

          if len(warn) > 0:
            self.logger.warning(str(warn[-1].message))
    except mdb.Error, err:
      self.dbConnection.rollback()
      self.logger.error("%s %s" % (err.args[0], err.args[1]))
    except Exception, err:
      self.logger.error(self.MSG_ERROR_SQL_QUERY_EXECUTION, str(err), str(query))

    return ret


  # # Get cached data from DB
  #
  # @param kwarg - parameters dictionary
  # @return social data from DB
  def getCachedlDataFromDB(self, **kwarg):
    # variable for result
    ret = None

    if self.configOptions.selectQuery is not None and self.configOptions.selectQuery != "":
      query = copy.copy(self.configOptions.selectQuery)
      for key, value in kwarg.items():
        query = re.sub(pattern='%' + str(key) + '%', repl=value, string=query, flags=re.U + re.I)

      self.logger.debug("query: %s", str(query))
      rows = self.executeQuery(query)
      if rows is not None:
        for row in rows:
          try:
            for key, value in row.items():
              if self.configOptions.cachedFieldName.upper() == key.upper():
                if value != self.DEFAULT_UPDATE_TABLE_FIELDS_VALUE:
                  ret = json.loads(value, encoding='utf-8')
                self.logger.debug("FOUND CACHED DATA\n%s", json.dumps(obj=ret, ensure_ascii=False, encoding='utf-8'))
                break

          except Exception, err:
            self.logger.debug(self.MSG_ERROR_LOAD_CACHED_DATA, str(err))

          break

    return ret


  # # Set cached data to DB
  #
  # @param kwarg - parameters dictionary
  # @return - None
  def setCachedDataToDB(self, **kwarg):
    if self.configOptions.insertQuery is not None and self.configOptions.insertQuery != "":
      try:
        self.logger.debug("macroNamesMap: %s", str(self.configOptions.macroNamesMap))

        query = copy.copy(self.configOptions.insertQuery)
        for key, value in kwarg.items():
          if key.upper() == self.configOptions.cachedFieldName.upper():
            value = self.dbConnection.escape_string(json.dumps(value, encoding='utf-8'))
            
          query = re.sub(pattern='%' + str(key) + '%', repl=str(value), string=query, flags=re.U + re.I)

          for macroNameKey, macroNameValue in self.configOptions.macroNamesMap.items():
            if key.upper() == macroNameKey.upper() and isinstance(macroNameValue, list):
              for macroName in macroNameValue:
                query = re.sub(pattern='%' + str(macroName) + '%', repl=str(value), string=query, flags=re.U + re.I)

        query = re.sub(pattern=self.DEFAULT_UPDATE_TABLE_ALL_FIELDS_PATTERN,
                       repl=self.DEFAULT_UPDATE_TABLE_FIELDS_VALUE,
                       string=query,
                       flags=re.U + re.I)

        self.logger.debug("query: %s", str(query))
        self.executeQuery(query)

      except Exception, err:
        self.logger.debug(self.MSG_ERROR_SAVE_CACHED_DATA, str(err))
        self.logger.info(Utils.getTracebackInfo())


  # # Save cached data to DB
  #
  # @param itemsDataDict - items data dict
  # @return - None
  def saveCachedDataToDB(self, itemsDataDict):
    if isinstance(itemsDataDict, CacheDataStorage.ItemsDataDict):
        for dataDict in itemsDataDict.getValues():
          if dataDict is not None:
            self.setCachedDataToDB(**dataDict)


  # # Remove obsolete cached data from DB
  #
  # @param - None
  # @return - None
  def removeObsoleteCachedData(self):
    if self.configOptions.deleteQuery is not None and self.configOptions.deleteQuery != "":
      # execution removing old records
      self.logger.debug("query: %s", str(self.configOptions.deleteQuery))
      self.executeQuery(self.configOptions.deleteQuery)
