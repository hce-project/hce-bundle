'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import hashlib
import logging
import Constants
import dc.Constants
import shutil
import dc.EventObjects
import MySQLdb
import copy
import sqlite3
import os
import os.path
import itertools
import types
import datetime
import app.Utils as Utils  # pylint: disable=F0401
from app.Utils import SQLExpression
from app.Utils import PathMaker
from BaseTask import BaseTask

logger = Utils.MPLogger().getLogger()


# @todo move to apropriate place
class DBDataTask(BaseTask):

  NO_DIR_STR = "No such file or directory:"

  # #constructor
  #
  # @param dbDataType is a type of DBData operations
  # @param keyValueStorageDir root point of kvdb file storage
  def __init__(self, dbDataType=Constants.DB_DATA_KVDB, keyValueDefaultFile=None, dcContentTemplate=None,
               keyValueStorageDir=None, rawDataDir=None):
    super(DBDataTask, self).__init__()
    self.rawDataDir = rawDataDir
    self.keyValueStorageDir = ""
    self.dbDataType = dbDataType
    self.queryCallback = None
    self.fetchFunc = None
    self.insertFunc = None
    self.createTableFunc = None
    if self.dbDataType == Constants.DB_DATA_KVDB:
      logger.debug(">>> set KVDB")
      self.fetchFunc = self.KVDBFetch
      self.insertFunc = self.KVDBInsert
      self.delRecordFunc = self.KVDBDelRecord
      self.delTableFunc = self.KVDBDelTable
      self.createTableFunc = self.KVDBCreateTable
    elif self.dbDataType == Constants.DB_DATA_MYSQL:
      logger.debug(">>> set MySQL")
      self.fetchFunc = self.MySQLFetch
      self.insertFunc = self.MySQLInsert
      self.delRecordFunc = self.MySQLDelRecord
      self.delTableFunc = self.MySQLDelTable
      self.createTableFunc = self.MySQLCreateTable
    self.keyValueDefaultFile = keyValueDefaultFile
    self.dcContentTemplate = dcContentTemplate
    self.keyValueStorageDir = keyValueStorageDir


  # #makes operations with Data Storage
  #
  # @param dbDataRequest - one of DBDataStorageRequests
  # @param queryCallback function for quieries execution
  def process(self, dbDataRequest, queryCallback):
    ret = None
    self.queryCallback = queryCallback
    logger.debug(">>> DBDataTask process")
    if type(dbDataRequest) == dc.EventObjects.DataFetchRequest:
      if self.fetchFunc is not None:
        ret = self.fetchFunc(dbDataRequest)
      else:
        ret = dc.EventObjects.DataFetchResponse({})
    elif type(dbDataRequest) == dc.EventObjects.URLPut:
      if ("id" not in dbDataRequest.putDict or dbDataRequest.putDict["id"] is None) and \
      dbDataRequest.urlMd5 is not None:
        dbDataRequest.putDict["id"] = dbDataRequest.urlMd5
      if "CDate" not in dbDataRequest.putDict or dbDataRequest.putDict["CDate"] is None:
        dbDataRequest.putDict["CDate"] = SQLExpression('CURRENT_TIMESTAMP')
      if dbDataRequest.contentType == dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT:
        if self.insertFunc is not None:
          ret = self.insertFunc(dbDataRequest)
        else:
          ret = dc.EventObjects.URLPutResponse(dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
      else:
        ret = self.insertFSFunc(dbDataRequest)

      ret.contentType = dbDataRequest.contentType
    elif type(dbDataRequest) == dc.EventObjects.DataDeleteRequest:
      if dbDataRequest.urlMd5 is None:
        self.delTableFunc(dbDataRequest)
      else:
        self.delRecordFunc(dbDataRequest)
    elif type(dbDataRequest) == dc.EventObjects.DataCreateRequest:
      if dbDataRequest.urlMd5 is None:
        self.createTableFunc(dbDataRequest)
      else:
        pass
    else:
      logger.error(">>> Unsupport request object type = " + str(type(dbDataRequest)))
    return ret


  def fetchKVDBSpecificFunct(self, dbConnect, query, response):
    dbConnect.row_factory = sqlite3.Row
    cursor = dbConnect.cursor()
    for row in cursor.execute(query):
      response.resultDict = dict(itertools.izip(row.keys(), row))


  def insertKVDBSpecificFunct(self, dbConnect, query, response):
    cursor = dbConnect.cursor()
    cursor.execute(query)


  def KVDBCommonExecute(self, request, response, specificFunc, query):
    dbName = Constants.KEY_VALUE_FILE_NAME_TEMPLATE % request.siteId
    dbFileName = self.keyValueStorageDir + "/" + dbName
    logger.debug(">>> KVDB SQL = " + query)
    logger.debug(">>> KVDB Path = " + str(dbFileName))
    try:
      if os.path.exists(dbFileName):
        dbConnect = sqlite3.connect(dbFileName)  # pylint: disable-all
        dbConnect.text_factory = str
        specificFunc(dbConnect, query, response)
        dbConnect.commit()
      else:
        logger.error(">>> path not exist")
        response.errCode = 1
        response.errMessage = ">>> path not exist"
    except:
      logger.error(">>> some kvdb exception")
      response.errCode = 1
      response.errMessage = ">>> some kvdb exception"


  def KVDBFetch(self, request):
    logger.debug(">>> KVDBFetch start")
    ret = dc.EventObjects.DataFetchResponse({})
    self.KVDBCommonExecute(request, ret, self.fetchKVDBSpecificFunct,
                           (Constants.SELECT_DB_STORAGE % ("articles", request.urlMd5)))
    return ret


  def MySQLFetch(self, request):
    logger.debug(">>> MySQLFetch start")
    ret = dc.EventObjects.DataFetchResponse({})
    if self.queryCallback is not None:
      tableName = Constants.DC_CONTENTS_TABLE_NAME_TEMPLATE % request.siteId
      query = Constants.SELECT_DB_STORAGE % (tableName, request.urlMd5)
      res = self.queryCallback(query, Constants.FIFTH_DB_ID, Constants.EXEC_NAME)
      if hasattr(res, '__iter__') and len(res) >= 1:
        ret.resultDict = res[0]
        for key in ret.resultDict:
          if type(ret.resultDict[key]) == datetime.datetime:
            ret.resultDict[key] = str(ret.resultDict[key])
        # type(insertDict[key]) == datetime.datetime
      else:
        ret.errCode = 1
        ret.errMessage = ">>> empty mysql response"
    return ret


  def createInsertQueryKVDB(self, insertDict, supportFields, tableName):
    mainSQL = "REPLACE INTO `%s`"
    valusesStr = "VALUES("
    fieldsStr = "("
    for key in insertDict:
      if key in supportFields and insertDict[key] is not None:
        fieldsStr += "`"
        fieldsStr += key
        fieldsStr += "`,"

        if type(insertDict[key]) in types.StringTypes or type(insertDict[key]) == datetime.datetime:
          valusesStr += "'"
        valusesStr += str(insertDict[key])
        if type(insertDict[key]) in types.StringTypes or type(insertDict[key]) == datetime.datetime:
          valusesStr += "'"
        valusesStr += ","
      else:
        logger.debug(">>> field not in Constants fields list field or None value = " + key)
    if valusesStr[-1] == ",":
      valusesStr = valusesStr[0:-1]
    if fieldsStr[-1] == ",":
      fieldsStr = fieldsStr[0:-1]
    valusesStr += ")"
    fieldsStr += ")"

    query = mainSQL % tableName
    query += " "
    query += fieldsStr
    query += " "
    query += valusesStr
    return query


  def createInsertQueryMySQL(self, insertDict, supportFields, tableName):
    keyList = []
    valueList = []
    SQL_INSERT_TEMPLATE = "INSERT INTO %s SET %s ON DUPLICATE KEY UPDATE %s"
    for key in insertDict:
      if key in supportFields and insertDict[key] is not None:
        keyList.append(key)
        if type(insertDict[key]) in types.StringTypes:
          escapingStr = MySQLdb.escape_string(str(insertDict[key]))
          valueList.append(("'" + escapingStr + "'"))
        else:
          valueList.append(str(insertDict[key]))
    setString = Constants.createFieldsValuesString(keyList, valueList)
    query = ""
    if len(setString) > 0:
      query = SQL_INSERT_TEMPLATE % (tableName, setString, setString)
    else:
      logger.debug(">>> createInsertQueryMySQL empty SET list")
    return query


  def KVDBInsert(self, request):
    logger.debug(">>> KVDBInsert start")
    ret = dc.EventObjects.URLPutResponse(dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
    query = self.createInsertQueryKVDB(request.putDict, Constants.DbContentFields["KVDB"],
                                       Constants.DB_STORAGE_TABLE_NAME)
    self.KVDBCommonExecute(request, ret, self.insertKVDBSpecificFunct, query)
    return ret


  def MySQLInsert(self, request):
    logger.debug(">>> MySQLInsert start")
    ret = dc.EventObjects.URLPutResponse(dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
    if self.queryCallback is not None:
      tableName = Constants.DC_CONTENTS_TABLE_NAME_TEMPLATE % request.siteId
      SQL_CHECK_TABLE = "SELECT count(*) FROM `%s`"
      query = SQL_CHECK_TABLE % tableName
      res = self.queryCallback(query, Constants.FIFTH_DB_ID)
      if res is None or len(res) == 0:
        mySQLCreateTableRequest = dc.EventObjects.DataCreateRequest(request.siteId, None, None)
        self.MySQLCreateTable(mySQLCreateTableRequest)

      query = self.createInsertQueryMySQL(request.putDict, Constants.DbContentFields["MYSQL"], tableName)
      self.queryCallback(query, Constants.FIFTH_DB_ID)
    return ret


  def deleteSurroundStorageFiles(self, rawStoragePath, urlMd5):
    delContentTypes = [dc.EventObjects.Content.CONTENT_TIDY_CONTENT, dc.EventObjects.Content.CONTENT_HEADERS_CONTENT,
                       dc.EventObjects.Content.CONTENT_REQUESTS_CONTENT, dc.EventObjects.Content.CONTENT_META_CONTENT,
                       dc.EventObjects.Content.CONTENT_COOKIES_CONTENT, dc.EventObjects.Content.CONTENT_DYNAMIC_CONTENT]

    for cType in delContentTypes:
      localFileSuffix = self.resolveFileSuffix(cType)
      rawStorageFileName = Utils.accumulateSubstrings([urlMd5, None, localFileSuffix], ["", "_", ""])
      localPath = rawStoragePath + rawStorageFileName
      try:
        os.remove(localPath)
      except OSError:
        pass


  def insertFSFunc(self, dbDataRequest):
    logger.debug(">>> insertFSFunc start")
    ret = dc.EventObjects.URLPutResponse(dbDataRequest.contentType)
    if "data" in dbDataRequest.putDict and dbDataRequest.putDict["data"] is not None:
      if self.rawDataDir is not None:
        localFileSuffix = self.resolveFileSuffix(dbDataRequest.contentType)
        rawStoragePath = self.rawDataDir
        if rawStoragePath[-1] != '/':
          rawStoragePath += '/'
        rawStoragePath += str(dbDataRequest.siteId)
        rawStoragePath += '/'
        pathMaker = PathMaker(dbDataRequest.urlMd5)
        rawStoragePath += pathMaker.getDir()
        rawStoragePath += '/'
        rawStorageFileName = Utils.accumulateSubstrings(
                            [dbDataRequest.urlMd5, dbDataRequest.fileStorageSuffix, localFileSuffix], ["", "_", ""])
        localPath = rawStoragePath + rawStorageFileName
        if not os.path.exists(rawStoragePath):
          os.makedirs(rawStoragePath)
          logger.debug(">>> MAKE PATH - " + rawStoragePath)
        if os.path.exists(localPath):
          logger.debug(">>> file is exists - " + localPath)
        if dbDataRequest.contentType == dc.EventObjects.Content.CONTENT_RAW_CONTENT:
          self.deleteSurroundStorageFiles(rawStoragePath, dbDataRequest.urlMd5)
        fd = None
        try:
          fd = open(localPath, "w")
        except IOError as ex:
          if self.NO_DIR_STR in str(ex):
            logger.error(">>> Wrong path, file - " + str(localPath))
          else:
            logger.error(">>> Some file open error, file - " + localPath)
        if fd is not None:
          fd.write(dbDataRequest.putDict["data"])
          fd.flush()
          fd.close()
      else:
        logger.error(">>> rawDataDir is None")
        ret.errCode = 1
        ret.errMessage = ">>> rawDataDir is None"
    else:
      logger.error(">>> 'data' not in dbDataRequest.putDict or dbDataRequest.putDict['data'] is None")
      ret.errCode = 1
      ret.errMessage = ">>> 'data' not in dbDataRequest.putDict or dbDataRequest.putDict['data'] is None"
    return ret


  def KVDBDelRecord(self, request):
    logger.debug(">>> KVDBDelRecord start")
    ret = dc.EventObjects.DataDeleteResponse()
    dbName = Constants.KEY_VALUE_FILE_NAME_TEMPLATE % request.siteId
    dbFileName = self.keyValueStorageDir + "/" + dbName
    try:
      if os.path.exists(dbFileName):
        dbConnect = sqlite3.connect(dbFileName)  # pylint: disable-all
        dbConnect.text_factory = str
        cursor = dbConnect.cursor()
        cursor.execute("DELETE from `articles` where `id` = '%s'" % request.urlMd5)
        dbConnect.commit()
      else:
        logger.error(">>> path not exist")
        ret.errCode = 1
        ret.errMessage = ">>> path not exist"
    except:
      logger.error(">>> some kvdb exception")
      ret.errCode = 1
      ret.errMessage = ">>> some kvdb exception"
    return ret


  def KVDBDelTable(self, request):
    logger.debug(">>> KVDBDelTable start")
    ret = dc.EventObjects.DataDeleteResponse()
    try:
      if request.filesSuffix is not None:
        delFile = self.keyValueStorageDir + "/" + (request.filesSuffix % request.siteId)
        logger.debug(">>> Del file = %s", str(delFile))
        os.remove(delFile)
      else:
        logger.error(">>> request.filesSuffix is None")
        ret.errCode = 1
        ret.errMessage = (">>> request.filesSuffix is None")
    except OSError as err:
      logger.error((str(err.filename) + " " + str(err.strerror)))
      ret.errCode = 1
      ret.errMessage = (str(err.filename) + " " + str(err.strerror))
      logger.debug(">>> [KVDBDelTable] CURRENT DIR " + str(os.getcwd()))
    return ret


  def MySQLDelRecord(self, request):
    logger.debug(">>> MySQLDelRecord start")
    ret = dc.EventObjects.DataDeleteResponse()
    if self.queryCallback is not None:
      DELETE_SQL_REQUEST = "DELETE FROM `%s` WHERE `id`='%s'"
      tableName = Constants.DC_CONTENTS_TABLE_NAME_TEMPLATE % request.siteId
      query = DELETE_SQL_REQUEST % (tableName, request.urlMd5)
      self.queryCallback(query, Constants.FIFTH_DB_ID)
    return ret


  def MySQLDelTable(self, request):
    logger.debug(">>> MySQLDelTable start")
    ret = dc.EventObjects.DataDeleteResponse()
    if self.queryCallback is not None:
      DROP_SQL_REQUEST = "DROP TABLE IF EXISTS `%s`"
      tableName = Constants.DC_CONTENTS_TABLE_NAME_TEMPLATE % request.siteId
      query = DROP_SQL_REQUEST % tableName
      self.queryCallback(query, Constants.FIFTH_DB_ID)
    return ret


  def KVDBCreateTable(self, request):
    logger.debug(">>> KVDBCreateTable start")
    ret = dc.EventObjects.DataCreateResponse()
    if self.keyValueDefaultFile is not None:
      keyValueFileName = self.keyValueStorageDir
      if keyValueFileName[-1] != '/':
        keyValueFileName += '/'
      keyValueFileName += (Constants.KEY_VALUE_FILE_NAME_TEMPLATE % request.siteId)
      shutil.copy(self.keyValueDefaultFile, keyValueFileName)
    else:
      logger.error(">>> keyValueDefaultFile is None")
      ret.errCode = 1
      ret.errMessage = ">>> keyValueDefaultFile is None"
    return ret


  def MySQLCreateTable(self, request):
    logger.debug(">>> MySQLCreateTable start")
    ret = dc.EventObjects.DataCreateResponse()
    if self.dcContentTemplate is not None:
      if self.queryCallback is not None:
        template = open(self.dcContentTemplate).read()
        query = template.replace("%SITE_ID%", str(request.siteId))
        logger.debug(">>> create content_tables id = " + str(request.siteId))
        self.queryCallback(query, Constants.FIFTH_DB_ID)
      else:
        logger.error(">>> queryCallback is None")
        ret.errCode = 1
        ret.errMessage = ">>> queryCallback is None"
    else:
      logger.error(">>> keyValueDefaultFile is None")
      ret.errCode = 1
      ret.errMessage = ">>> keyValueDefaultFile is None"
    return ret


  def resolveFileSuffix(self, contentType):
    ret = ""
    if contentType == dc.EventObjects.Content.CONTENT_RAW_CONTENT:
      ret = dc.Constants.RAW_DATA_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_TIDY_CONTENT:
      ret = dc.Constants.RAW_DATA_TIDY_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_HEADERS_CONTENT:
      ret = dc.Constants.RAW_DATA_HEADERS_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_REQUESTS_CONTENT:
      ret = dc.Constants.RAW_DATA_REQESTS_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_META_CONTENT:
      ret = dc.Constants.RAW_DATA_META_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_COOKIES_CONTENT:
      ret = dc.Constants.RAW_DATA_COOKIES_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_DYNAMIC_CONTENT:
      ret = dc.Constants.RAW_DATA_DYNAMIC_SUFF
    elif contentType == dc.EventObjects.Content.CONTENT_CHAIN_PARTS:
      ret = dc.Constants.RAW_DATA_CHAIN_SUFF
    return ret
