'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ConfigParser
from contextlib import closing
import MySQLdb.cursors
import MySQLdb as mdb
import dbi.EventObjects as dbi_event
import dc.EventObjects as dc_event
from dc.Constants import EVENT_TYPES, DRCESyncTasksCover
import dc_db.Constants as Constants
from dc_db.AttrSetTask import AttrSetTask
from dc_db.AttrFetchTask import AttrFetchTask
from dc_db.AttrUpdateTask import AttrUpdateTask
from dc_db.AttrDeleteTask import AttrDeleteTask
from dc_db.ProxyDeleteTask import ProxyDeleteTask
from dc_db.ProxyFindTask import ProxyFindTask
from dc_db.ProxyNewTask import ProxyNewTask
from dc_db.ProxyStatusTask import ProxyStatusTask
from dc_db.ProxyUpdateTask import ProxyUpdateTask
from dc_db.SiteTask import SiteTask
from dc_db.SiteCleanUpTask import SiteCleanUpTask
from dc_db.SiteDeleteTask import SiteDeleteTask
from dc_db.SiteUpdateTask import SiteUpdateTask
from dc_db.SiteStatusTask import SiteStatusTask
from dc_db.SiteFindTask import SiteFindTask
from dc_db.URLNewTask import URLNewTask
from dc_db.URLStatusTask import URLStatusTask
from dc_db.URLUpdateTask import URLUpdateTask
from dc_db.URLFetchTask import URLFetchTask
from dc_db.URLCleanupTask import URLCleanUpTask
from dc_db.URLDeleteTask import URLDeleteTask
from dc_db.URLContentTask import URLContentTask
from dc_db.SQLCustomTask import SQLCustomTask
from dc_db.URLPurgeTask import URLPurgeTask
from dc_db.FieldRecalculatorTask import FieldRecalculatorTask
from dc_db.URLVerifyTask import URLVerifyTask
from dc_db.URLAgeTask import URLAgeTask
from dc_db.DBDataTask import DBDataTask
from dc_db.URLPutTask import URLPutTask
from dc_db.URLHistoryTask import URLHistoryTask
from dc_db.URLStatsTask import URLStatsTask
from dc_db.StatisticLogManager import StatisticLogManager
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #dict to check event
eventCheckDict = dict({EVENT_TYPES.SITE_NEW: dc_event.Site,
                       EVENT_TYPES.SITE_UPDATE: dc_event.SiteUpdate,
                       EVENT_TYPES.SITE_STATUS: dc_event.SiteStatus,
                       EVENT_TYPES.SITE_DELETE: (dc_event.SiteDelete, list),
                       EVENT_TYPES.SITE_CLEANUP: (dc_event.SiteCleanup, list),
                       EVENT_TYPES.SITE_FIND: dc_event.SiteFind,
                       EVENT_TYPES.URL_NEW: list,
                       EVENT_TYPES.URL_UPDATE: list,
                       EVENT_TYPES.URL_STATUS: list,
                       EVENT_TYPES.URL_DELETE: list,
                       EVENT_TYPES.URL_FETCH: list,
                       EVENT_TYPES.URL_CLEANUP: list,
                       EVENT_TYPES.URL_CONTENT: list,
                       EVENT_TYPES.SQL_CUSTOM: dbi_event.CustomRequest,
                       EVENT_TYPES.URL_PURGE: list,
                       EVENT_TYPES.FIELD_RECALCULATE: list,
                       EVENT_TYPES.URL_VERIFY: list,
                       EVENT_TYPES.URL_AGE: list,
                       EVENT_TYPES.URL_PUT: list,
                       EVENT_TYPES.URL_HISTORY: list,
                       EVENT_TYPES.URL_STATS: list,
                       EVENT_TYPES.PROXY_NEW: list,
                       EVENT_TYPES.PROXY_UPDATE: list,
                       EVENT_TYPES.PROXY_DELETE: list,
                       EVENT_TYPES.PROXY_STATUS: list,
                       EVENT_TYPES.PROXY_FIND: list,
                       EVENT_TYPES.ATTR_SET: list,
                       EVENT_TYPES.ATTR_UPDATE: list,
                       EVENT_TYPES.ATTR_DELETE: list,
                       EVENT_TYPES.ATTR_FETCH: list})

# #sql query which checks existence of a table
CHECK_TABLE_SQL_TEMPLATE = " SELECT COUNT(*) FROM `sites` WHERE Id = '%s'"

class TasksManager(object):
  # Configuration settings options names
  DB_HOST = "db_host"
  DB_PORT = "db_port"
  DB_USER = "db_user"
  DB_PWD = "db_pwd"
  PRIMARY_DB = "primary_db"
  SECONDARY_DB = "secondary_db"
  THIRD_DB = "third_db"
  FOURTH_DB = "fourth_db"
  FIFTH_DB = "fifth_db"
  STAT_DB = "stat_db"
  LOG_DB = "log_db"
  ATT_DB = "att_db"
  STAT_DOMAINS_DB = "stat_domains_db"
  MUTEX_LOCK_TTL = "mutexLockTTL"
  SITE_TEMPLATE = "dc_site_template"
  KEY_VALUE_STORAGE_DIR = "key_value_storage_dir"
  KEY_VALUE_DEFAULT_FILE = "key_value_default_file"
  RAW_DATA_DIR = "raw_data_dir"
  CONTENT_STORAGE_TYPE = "content_storage_type"
  CONTENT_TEMPLATE = "dc_content_template"
  STAT_TEMPLATE = "dc_statistics_freq_template"
  LOG_TEMPLATE = "dc_statistics_log_template"
  ATTR_TEMPLATE = "dc_attribute_template"
  SITE_PROP_NAME_FREQ = "stats_freq_enabled"
  SITE_PROP_NAME_LOG = "stats_log_enabled"
  SQL_OPERATION_LIST = ["update", "insert", "delete", "drop"]


  # #constructor
  #
  # @param configParser config parser object
  def __init__(self, configParser, dbTaskMode=dc_event.Batch.DB_MODE_RW):
    self.dbTaskMode = dbTaskMode
    className = self.__class__.__name__
    # Get configuration settings
    dbHost = configParser.get(className, self.DB_HOST)
    dbPort = int(configParser.get(className, self.DB_PORT))
    dbUser = configParser.get(className, self.DB_USER)
    dbPWD = configParser.get(className, self.DB_PWD)
    dbPrimary = configParser.get(className, self.PRIMARY_DB)
    dbSecondary = configParser.get(className, self.SECONDARY_DB)
    dbThird = configParser.get(className, self.THIRD_DB)
    dbFourth = configParser.get(className, self.FOURTH_DB)
    dbFifth = configParser.get(className, self.FIFTH_DB)
    dbStat = configParser.get(className, self.STAT_DB)
    dbLog = configParser.get(className, self.LOG_DB)
    dbAtt = configParser.get(className, self.ATT_DB)
    dbStatDomains = configParser.get(className, self.STAT_DOMAINS_DB)

    try:
      self.mutexLockTTL = int(configParser.get(className, self.MUTEX_LOCK_TTL))
    except Exception:
      self.mutexLockTTL = Constants.DEFAULT_LOCK_TTL
    self.contentStorageType = int(configParser.get(className, self.CONTENT_STORAGE_TYPE))
    self.dbConnections = {}
    self.dbNames = {}

    self.dcSiteTemplate = configParser.get(className, self.SITE_TEMPLATE)
    self.dcStatTemplate = configParser.get(className, self.STAT_TEMPLATE)
    self.dcLogTemplate = configParser.get(className, self.LOG_TEMPLATE)
    self.dcAttrTemplate = configParser.get(className, self.ATTR_TEMPLATE)
    self.keyValueStorageDir = configParser.get(className, self.KEY_VALUE_STORAGE_DIR)
    self.rawDataDir = configParser.get(className, self.RAW_DATA_DIR)
    self.keyValueDefaultFile = configParser.get(className, self.KEY_VALUE_DEFAULT_FILE)
    self.dcContentTemplate = configParser.get(className, self.CONTENT_TEMPLATE)
    self.dbConnections[Constants.PRIMARY_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbPrimary, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbPrimary] = Constants.PRIMARY_DB_ID
    self.dbConnections[Constants.SECONDARY_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbSecondary, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbSecondary] = Constants.SECONDARY_DB_ID
    if dbThird is not None and dbThird != '':
      self.dbConnections[Constants.THIRD_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbThird, dbPort, use_unicode=True, charset='utf8')
      self.dbNames[dbThird] = Constants.THIRD_DB_ID
    else:
      logger.debug(">>> THIRD_DB_ID empty")
    if dbFourth is not None and dbFourth != '':
      self.dbConnections[Constants.FOURTH_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbFourth, dbPort, use_unicode=True, charset='utf8')
      self.dbNames[dbFourth] = Constants.FOURTH_DB_ID
    else:
      logger.debug(">>> FOURTH_DB_ID empty")
    if dbFifth is not None and dbFifth != '':
      self.dbConnections[Constants.FIFTH_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbFifth, dbPort, use_unicode=True, charset='utf8')
      self.dbNames[dbFifth] = Constants.FIFTH_DB_ID
    else:
      logger.debug(">>> FIFTH_DB_ID empty")
    self.dbConnections[Constants.STAT_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbStat, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbStat] = Constants.STAT_DB_ID
    self.dbConnections[Constants.LOG_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbLog, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbLog] = Constants.LOG_DB_ID
    self.dbConnections[Constants.LOG_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbLog, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbLog] = Constants.LOG_DB_ID
    self.dbConnections[Constants.ATT_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbAtt, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbAtt] = Constants.ATT_DB_ID
    self.dbConnections[Constants.STAT_DOMAINS_DB_ID] = mdb.connect(dbHost, dbUser, dbPWD, dbStatDomains, dbPort, use_unicode=True, charset='utf8')
    self.dbNames[dbStatDomains] = Constants.STAT_DOMAINS_DB_ID

    self.SQLErrorCode = Constants.EXIT_CODE_OK
    self.SQLErrorString = ""
    self.dBDataTask = DBDataTask(self.contentStorageType, self.keyValueDefaultFile, self.dcContentTemplate,
                                 self.keyValueStorageDir, self.rawDataDir)
    try:
      tmpVal = int(configParser.get(className, self.SITE_PROP_NAME_FREQ))
      StatisticLogManager.GLOBAL_FREQ_ENABLED = bool(tmpVal)
    except ConfigParser.NoOptionError:
      pass
    try:
      tmpVal = int(configParser.get(className, self.SITE_PROP_NAME_LOG))
      StatisticLogManager.GLOBAL_LOG_ENABLED = bool(tmpVal)
    except ConfigParser.NoOptionError:
      pass


  # #destructor
  #
  def __del__(self):
    for dbConnect in self.dbConnections.values():
      if dbConnect is not None:
        dbConnect.close()


  # #process input event
  #
  # @param drceSyncTasksCover instance of DRCESyncTasksCover
  # @return generalResponse instance of GeneralResponse object
  def process(self, drceSyncTasksCover):
    logger.info("Request eventType: %s, eventObject type: %s",
                str(drceSyncTasksCover.eventType), str(type(drceSyncTasksCover.eventObject)))
    if isinstance(drceSyncTasksCover.eventObject, list):
      if len(drceSyncTasksCover.eventObject) > 0:
        itemType = str(drceSyncTasksCover.eventObject[0])
      else:
        itemType = ""
      logger.info("Request eventObject items: %s, item type: %s", str(len(drceSyncTasksCover.eventObject)), itemType)
      # if isinstance(drceSyncTasksCover.eventObject, dc_event.URLFetch):
      # logger.debug('Event object: %s', varDump(drceSyncTasksCover.eventObject))

    self.checkInputData(drceSyncTasksCover)
    responseObject = None
    responseEvent = None
    if drceSyncTasksCover.eventType == EVENT_TYPES.SITE_DELETE:
      siteDeleteTask = SiteDeleteTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = siteDeleteTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.SITE_DELETE_RESPONSE
      self.SQLErrorCode = Constants.EXIT_CODE_OK

    elif drceSyncTasksCover.eventType == EVENT_TYPES.SITE_NEW:
      siteTask = SiteTask(self.dcSiteTemplate, self.keyValueDefaultFile, self.keyValueStorageDir, self.dBDataTask,
                          self.dcStatTemplate, self.dcLogTemplate, self.dcAttrTemplate, self)
      responseObject = siteTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.SITE_NEW_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.SITE_UPDATE:
      siteUpdateTask = SiteUpdateTask(self.dcSiteTemplate, self.keyValueDefaultFile, self.keyValueStorageDir,
                                      self.rawDataDir, self.dBDataTask, self.dcStatTemplate, self.dcLogTemplate,
                                      self.dcAttrTemplate)
      responseObject = siteUpdateTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.SITE_UPDATE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.SITE_CLEANUP:
      siteCleanUpTask = SiteCleanUpTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = siteCleanUpTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.SITE_CLEANUP_RESPONSE
      self.SQLErrorCode = Constants.EXIT_CODE_OK

    elif drceSyncTasksCover.eventType == EVENT_TYPES.SITE_STATUS:
      siteStatusTask = SiteStatusTask()
      responseObject = siteStatusTask.process(drceSyncTasksCover.eventObject, self.executeQuery)  # pylint:disable=R0204
      responseEvent = EVENT_TYPES.SITE_STATUS_RESPONSE

    # find site by root url and return list of siteId's with root urls
    elif drceSyncTasksCover.eventType == EVENT_TYPES.SITE_FIND:
      siteFindTask = SiteFindTask(self.dcSiteTemplate, self.keyValueDefaultFile, self.keyValueStorageDir,
                                  self.dBDataTask, self.dcStatTemplate, self.dcLogTemplate, self.dcAttrTemplate)
      responseObject = siteFindTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.SITE_FIND_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_NEW:
      urlNewTask = URLNewTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      urlNewTask.siteTask = SiteTask(self.dcSiteTemplate, self.keyValueDefaultFile, self.keyValueStorageDir,
                                     self.dBDataTask, self.dcStatTemplate, self.dcLogTemplate, self.dcAttrTemplate)
      responseObject = urlNewTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_NEW_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_STATUS:
      urlStatusTask = URLStatusTask()
      responseObject = urlStatusTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_STATUS_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_UPDATE:
      urlUpdateTask = URLUpdateTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlUpdateTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_UPDATE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_FETCH:
      urlFetchTask = URLFetchTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask, self.dcSiteTemplate,
                                  self.keyValueDefaultFile, self.dcStatTemplate, self.dcLogTemplate, self.mutexLockTTL)
      responseObject = urlFetchTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_FETCH_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_CONTENT:
      urlContentTask = URLContentTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask, self.dcSiteTemplate,
                                      self.keyValueDefaultFile, self.dcStatTemplate, self.dcLogTemplate)
      responseObject = urlContentTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_CONTENT_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_DELETE:
      urlDeleteTask = URLDeleteTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlDeleteTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_DELETE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_CLEANUP:
      urlCleanUpTask = URLCleanUpTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlCleanUpTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_CLEANUP_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.SQL_CUSTOM:
      sqlCustomTask = SQLCustomTask()
      responseObject = sqlCustomTask.process(drceSyncTasksCover.eventObject, self.executeQuery, self.backDBResolve)
      responseEvent = EVENT_TYPES.SQL_CUSTOM_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_PURGE:
      urlPurgeTask = URLPurgeTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlPurgeTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_PURGE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.FIELD_RECALCULATE:
      fieldRecalculatorTask = FieldRecalculatorTask()
      responseObject = fieldRecalculatorTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.FIELD_RECALCULATE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_VERIFY:
      urlVarifyTask = URLVerifyTask()
      responseObject = urlVarifyTask.process(drceSyncTasksCover.eventObject, self.executeQuery, self.backDBResolve)
      responseEvent = EVENT_TYPES.URL_VERIFY_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_AGE:
      urlAgeTask = URLAgeTask(self.keyValueStorageDir, self.rawDataDir, self.backDBResolve)
      responseObject = urlAgeTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_AGE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_PUT:
      urlPutTask = URLPutTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlPutTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_PUT_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_HISTORY:
      urlHistoryTask = URLHistoryTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlHistoryTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_HISTORY_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.URL_STATS:
      urlStatsTask = URLStatsTask(self.keyValueStorageDir, self.rawDataDir, self.dBDataTask)
      responseObject = urlStatsTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.URL_STATS_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.PROXY_NEW:
      proxyNewTask = ProxyNewTask()
      responseObject = proxyNewTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.PROXY_NEW_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.PROXY_UPDATE:
      proxyUpdateTask = ProxyUpdateTask()
      responseObject = proxyUpdateTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.PROXY_UPDATE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.PROXY_DELETE:
      proxyDeleteTask = ProxyDeleteTask()
      responseObject = proxyDeleteTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.PROXY_DELETE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.PROXY_STATUS:
      proxyStatusTask = ProxyStatusTask()
      responseObject = proxyStatusTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.PROXY_STATUS_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.PROXY_FIND:
      proxyFindTask = ProxyFindTask()
      responseObject = proxyFindTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.PROXY_FIND_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.ATTR_SET:
      attrSetTask = AttrSetTask()
      responseObject = attrSetTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.ATTR_SET_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.ATTR_UPDATE:
      attrUpdateTask = AttrUpdateTask()
      responseObject = attrUpdateTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.ATTR_UPDATE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.ATTR_DELETE:
      attrDeleteTask = AttrDeleteTask()
      responseObject = attrDeleteTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.ATTR_DELETE_RESPONSE

    elif drceSyncTasksCover.eventType == EVENT_TYPES.ATTR_FETCH:
      attrFetchTask = AttrFetchTask()
      responseObject = attrFetchTask.process(drceSyncTasksCover.eventObject, self.executeQuery)
      responseEvent = EVENT_TYPES.ATTR_FETCH_RESPONSE

    return self.createDRCESyncTasksCover(responseEvent, responseObject)


  # #executeQuery common entry point for SQL execution
  #
  # @param query query for execution
  # @param dbConnectionName MySQL connection Id
  # @executeType executeType - return set type
  # @returns fetching data or None
  def executeQuery(self, query, dbConnectionName, executeType=Constants.EXEC_INDEX, SQLErrorClear=False):
    ret = None
    if executeType == Constants.EXEC_INDEX:
      ret = self.executeQueryByIndex(query, dbConnectionName, SQLErrorClear)
    elif executeType == Constants.EXEC_NAME:
      ret = self.executeQueryByName(query, dbConnectionName, SQLErrorClear)
    return ret


  # #method performs common sql error handling
  #
  # @param err SQL exception class instance
  # @param dbConnectionName incoming dbConnection name
  # @param SQLErrorClear mean set errorCode or not
  def commonQueryErrorHandler(self, err, dbConnection, SQLErrorClear=False):
    dbConnection.rollback()
    self.SQLErrorString = "%s %s" % (err.args[0], err.args[1])
    if not SQLErrorClear:
      ExceptionLog.handler(logger, err, self.SQLErrorString)
      self.SQLErrorCode = Constants.EXIT_CODE_MYSQL_ERROR
    else:
      logger.debug(self.SQLErrorString)


  # #helper check sql query by allowed prefix in ReadOnly db-task mode
  #
  # @param query query for execution
  # @return bool value
  def checkQueryInReadOnly(self, query):
    ret = True
    if self.dbTaskMode & dc_event.Batch.DB_MODE_W == 0:
      low_query = query.lower()
      for elem in self.SQL_OPERATION_LIST:
        if low_query.startswith(elem):
          logger.debug(">>> QUERY = " + query)
          logger.debug(">>> NOT SUPPORT in read only mode")
          ret = False
          break
    return ret


  # #helper function for correct query execution
  #
  # @param query query for execution
  # @param dbConnectionName incoming dbConnection name
  # @param SQLErrorClear mean set errorCode or not
  def executeQueryByIndex(self, query, dbConnectionName, SQLErrorClear=False):
    ret = None
    if self.checkQueryInReadOnly(query):
      dbConnection = None
      if dbConnectionName in self.dbConnections:
        dbConnection = self.dbConnections[dbConnectionName]
      if dbConnection:
        try:
          with closing(dbConnection.cursor()) as cursor:
            # logger.debug(query)
            cursor.execute(query)
            dbConnection.commit()
            ret = cursor.fetchall()
        except mdb.Error as err:  # pylint: disable=E1101
          self.commonQueryErrorHandler(err, dbConnection, SQLErrorClear)
      else:
        logger.debug(">>> dbConnection Not Found = " + str(dbConnectionName))
    return ret


  # #helper function for correct query execution
  #
  # @param query query for execution
  # @param dbConnectionName incoming dbConnection name
  # @param SQLErrorClear mean set errorCode or not
  def executeQueryByName(self, query, dbConnectionName, SQLErrorClear=False):
    ret = None
    if self.checkQueryInReadOnly(query):
      dbConnection = None
      if dbConnectionName in self.dbConnections:
        dbConnection = self.dbConnections[dbConnectionName]
      if dbConnection:
        try:
          with closing(dbConnection.cursor(MySQLdb.cursors.DictCursor)) as cursor:
            # logger.debug(query)
            cursor.execute(query)
            dbConnection.commit()
            ret = cursor.fetchall()
        except mdb.Error as err:  # pylint: disable=E1101
          self.commonQueryErrorHandler(err, dbConnection, SQLErrorClear)
      else:
        logger.debug(">>> dbConnection Not Found = " + str(dbConnectionName))
    return ret


  # #check  conformity data in input DRCESyncTasksCover object
  #
  # @param drceSyncTasksCover instance of DRCESyncTasksCover
  def checkInputData(self, drceSyncTasksCover):
    for inputType in eventCheckDict:
      if drceSyncTasksCover.eventType is inputType:
        if isinstance(eventCheckDict[inputType], tuple):
          for localType in eventCheckDict[inputType]:
            if isinstance(drceSyncTasksCover.eventObject, localType):
              return True
        elif isinstance(drceSyncTasksCover.eventObject, eventCheckDict[inputType]):
          return True
    raise Exception("Incorrect types of  input data")


  # #helper function to build response as DRCESyncTasksCover object
  #
  # @param eventType type of response event
  # @param eventObject instance of returning object
  def createDRCESyncTasksCover(self, eventType, eventObject):
    return DRCESyncTasksCover(eventType, eventObject)


  # #gets dbName and returns internar db index
  #
  # @param dbName db name
  def backDBResolve(self, dbName):
    ret = None
    if dbName in self.dbNames:
      ret = self.dbNames[dbName]
    return ret

