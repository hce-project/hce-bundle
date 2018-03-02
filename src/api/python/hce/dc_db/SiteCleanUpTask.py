'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import os
import shutil
import tempfile
import traceback
import sys

import dc.EventObjects
from dc_db.BaseTask import BaseTask
import dc_db.Constants as Constants
from dc_db.FieldRecalculator import FieldRecalculator
from dc_db.StatisticLogManager import StatisticLogManager
from dtm.EventObjects import GeneralResponse  # pylint: disable=unused-import
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# template for key value file name
KEY_VALUE_FILE_NAME_TEMPLATE = "%s.db"
KEY_VALUE_FIELDS_FILE_NAME_TEMPLATE = "%s_fields.db"

# #class implemented all logic necessary to process SiteCleanUp request
#
class SiteCleanUpTask(BaseTask):


  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    self.keyValueStorageDir = keyValueStorageDir
    self.rawDataDir = rawDataDir
    self.errorCode = 0
    self.errorMessage = "OK"
    self.dBDataTask = dBDataTask
    self.fieldRecalculator = FieldRecalculator()


  # #make all necessary actions to cleanup al site data
  #
  # @param siteCleanup instance of SiteCleanup object
  # @param queryCallback function for quieries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, siteCleanups, queryCallback):
    ret = GeneralResponse()
    if not isinstance(siteCleanups, list):
      siteCleanups = [siteCleanups]

    for siteCleanup in siteCleanups:
      self.errorCode = 0
      self.errorMessage = "OK"
      if self.isSiteExist(siteCleanup.id, queryCallback):
        self.cleanUpMysqlStorage(siteCleanup, queryCallback)
        if siteCleanup.historyCleanUp == dc.EventObjects.SiteCleanup.HISTORY_CLEANUP_LOG or \
        siteCleanup.historyCleanUp == dc.EventObjects.SiteCleanup.HISTORY_CLEANUP_FULL:
          self.trancateArbitraryTable(Constants.DC_LOG_TABLE_NAME_TEMPLATE, siteCleanup, Constants.LOG_DB_ID,
                                      queryCallback)
        if siteCleanup.historyCleanUp == dc.EventObjects.SiteCleanup.HISTORY_CLEANUP_FULL:
          self.trancateArbitraryTable(Constants.DC_FREQ_TABLE_NAME_TEMPLATE, siteCleanup, Constants.STAT_DB_ID,
                                      queryCallback)
        if siteCleanup.delayedType == dc.EventObjects.NOT_DELAYED_OPERATION:
          self.cleanUpDBStorage(siteCleanup, KEY_VALUE_FILE_NAME_TEMPLATE, queryCallback)
          self.cleanUpDBStorage(siteCleanup, KEY_VALUE_FIELDS_FILE_NAME_TEMPLATE, queryCallback)
          self.cleanUpRawDataStorage(siteCleanup)
        self.cleanUpMysqlSiteTable(siteCleanup, queryCallback)
        if siteCleanup.moveURLs:
          self.copyUrlsToDcUrls(siteCleanup.id, queryCallback)
        self.fieldRecalculator.updateSiteCleanupFields(siteCleanup.id, queryCallback)

        # cleaunup attributes
        self.trancateArbitraryTable(Constants.DC_ATT_TABLE_NAME_TEMPLATE, siteCleanup, Constants.ATT_DB_ID,
                                    queryCallback)
      else:
        self.errorCode = Constants.EXIT_CODE_GLOBAL_ERROR
        self.errorMessage = (">>> Site id [%s] not found" % siteCleanup.id)

      ret.errorCode = self.errorCode
      ret.statuses.append(ret.errorCode)
      if ret.errorMessage is None or ret.errorMessage == "":
        ret.errorMessage = self.errorMessage
      else:
        ret.errorMessage += ("-" + self.errorMessage)

    return ret


  # #method updates record in static db
  #
  # @param sqlTemplate SQL template for URLMd5's extractor
  # @param siteCleanup instance of SiteCleanup object
  # @param queryCallback function for quieries execution
  def staticUpdate(self, sqlTemplate, siteCleanup, queryCallback):
    tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteCleanup.id
    query = sqlTemplate % tbName
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if res is not None:
      for elem in res:
        if elem[0] is not None:
          StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_DELETED_STATE, 1,
                                              siteCleanup.id, elem[0])


  # #cleanup all site data from mysql db
  #
  # @param siteCleanup instance of SiteCleanup object
  # @param queryCallback function for quieries execution
  def cleanUpMysqlStorage(self, siteCleanup, queryCallback):
    if siteCleanup.saveRootUrls:
      SQL_COPY_QUERY_TEMPLATE = "INSERT INTO %s SELECT * FROM dc_urls.%s WHERE dc_urls.%s.ParentMd5 != ''"
      SQL_DEL_QUERY_TEMPLATE = "DELETE FROM `%s` WHERE ParentMd5 != ''"
      self.staticUpdate("SELECT `URLMd5` FROM %s WHERE ParentMd5 != ''", siteCleanup, queryCallback)
    else:
      SQL_COPY_QUERY_TEMPLATE = "INSERT INTO %s SELECT * FROM dc_urls.%s"
      SQL_DEL_QUERY_TEMPLATE = "TRUNCATE TABLE `%s`"
      self.staticUpdate("SELECT `URLMd5` FROM %s", siteCleanup, queryCallback)
    tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteCleanup.id
    query = SQL_DEL_QUERY_TEMPLATE % tbName
    if siteCleanup.delayedType == dc.EventObjects.NOT_DELAYED_OPERATION:
      queryCallback(query, Constants.SECONDARY_DB_ID)
    elif siteCleanup.delayedType == dc.EventObjects.DELAYED_OPERATION:
      query = Constants.SQL_CREATE_QUERY_TEMPLATE % (tbName, tbName)
      queryCallback(query, Constants.FOURTH_DB_ID)
      if siteCleanup.saveRootUrls:
        query = SQL_COPY_QUERY_TEMPLATE % (tbName, tbName, tbName)
      else:
        query = SQL_COPY_QUERY_TEMPLATE % (tbName, tbName)
      queryCallback(query, Constants.FOURTH_DB_ID)
      query = SQL_DEL_QUERY_TEMPLATE % tbName
      queryCallback(query, Constants.SECONDARY_DB_ID)


  # #method trancate arbitrary table in specified db
  #
  # @param siteCleanup instance of SiteCleanup object
  # @param dbId specific db id
  # @param queryCallback function for quieries execution
  def trancateArbitraryTable(self, tablePrefix, siteCleanup, dbId, queryCallback):
    tbName = tablePrefix % siteCleanup.id
    SQL_TRUNCATE_QUERY_TEMPLATE = "TRUNCATE TABLE `%s`"
    query = SQL_TRUNCATE_QUERY_TEMPLATE % tbName
    queryCallback(query, dbId)


  # #sets empty values in `sites` table for some fields
  #
  # @param siteCleanup instance of SiteCleanup object
  # @param queryCallback function for quieries execution
  def cleanUpMysqlSiteTable(self, siteCleanup, queryCallback):
    CLEAR_SITE_RECORS_SQL = ("UPDATE `sites` SET TcDate=NOW(), Resources=0, Iterations=0, State=%s, " +
                             "ErrorMask=0, Errors=0, Contents=0, CollectedURLs=0 WHERE id = '%s'")
    query = CLEAR_SITE_RECORS_SQL % (str(siteCleanup.state), siteCleanup.id)
    queryCallback(query, Constants.PRIMARY_DB_ID)


  # #cleanup all site data from keyvalue db
  #
  # @param siteCleanup instance of SiteCleanup object
  def cleanUpDBStorage(self, siteCleanup, filesSuffix, queryCallback):
    ret = None
    if self.dBDataTask is not None:
      dataDeleteRequest = dc.EventObjects.DataDeleteRequest(siteCleanup.id, None, filesSuffix)
      ret = self.dBDataTask.process(dataDeleteRequest, queryCallback)
    return ret


  # #cleanup all site data from raw data storage
  #
  # @param siteCleanup instance of SiteCleanup object
  def cleanUpRawDataStorage(self, siteCleanup):
    try:
      tmpDirName = self.rawDataDir + "/" + os.path.basename(tempfile.NamedTemporaryFile().name)
      originDirName = self.rawDataDir + "/" + siteCleanup.id
      logger.debug(">>> originDir = %s", str(originDirName))
      os.rename(originDirName, tmpDirName)
      shutil.rmtree(tmpDirName)
    except Exception as err:
      type_, value_, traceback_ = sys.exc_info()
      logger.debug("type_ = %s, value_ = %s", str(type_), str(value_))
      stack = traceback.format_tb(traceback_)
      logger.debug("Error: %s\n%s", str(err), str(stack.pop()))
      logger.debug(">>> [cleanUpRawDataStorage] CURRENT DIR " + str(os.getcwd()))
#      self.errorCode = 2
#      self.errorMessage = (">>> cleanUpRawDataStorage Error")
