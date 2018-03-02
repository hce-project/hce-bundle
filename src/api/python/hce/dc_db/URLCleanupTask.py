'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import os
import traceback
import sys
import shutil
from dc_db import FieldRecalculator
from dc_db import Constants
from dc_db.BaseTask import BaseTask
from dc_db.StatisticLogManager import StatisticLogManager
from dc_db.AttrDeleteTask import AttrDeleteTask
import dc.EventObjects
from app.Utils import PathMaker
import app.Utils as Utils  # pylint: disable=F0401
from dtm.EventObjects import GeneralResponse


logger = Utils.MPLogger().getLogger()


# #process urlCleanUp event
class URLCleanUpTask(BaseTask):


  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLCleanUpTask, self).__init__()
    self.keyValueStorageDir = keyValueStorageDir
    self.rawDataDir = rawDataDir
    self.recalculator = FieldRecalculator.FieldRecalculator()
    self.dBDataTask = dBDataTask
    self.urlMd5 = None


  # #make all necessary actions to delete urls data from db
  #
  # @param urlDelete list of URLDelete objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, urlCleanups, queryCallback):
    generalResponse = GeneralResponse()
    for urlCleanup in urlCleanups:
      # @todo add more complex case
      if urlCleanup.siteId == "":
        urlCleanup.siteId = "0"
      if self.isSiteExist(urlCleanup.siteId, queryCallback):
        try:
          localUrls = []
          if urlCleanup.url is None:
            localUrls = self.extractUrlByCriterions(urlCleanup.siteId, (urlCleanup.urlType == \
                                                    dc.EventObjects.URLStatus.URL_TYPE_URL), urlCleanup.criterions,
                                                    queryCallback)
          else:
            localUrls.append(urlCleanup.url)
          for localUrl in localUrls:
            urlCleanup.url = localUrl
            self.urlMd5 = self.calculateMd5FormUrl(urlCleanup.url, urlCleanup.urlType)
            StatisticLogManager.logUpdate(queryCallback, "LOG_URL_CLEANUP", urlCleanup, urlCleanup.siteId, self.urlMd5)
            if urlCleanup.delayedType == dc.EventObjects.NOT_DELAYED_OPERATION:
              # self.deleteFromKeyValue(urlCleanup)
              self.deleteFromDataStorage(urlCleanup, queryCallback)
              self.deleteFromRawStorage(urlCleanup)
            self.updateMysqlDB(urlCleanup, queryCallback, urlCleanup.siteId)
            if urlCleanup.delayedType == dc.EventObjects.DELAYED_OPERATION:
              self.copyUrlToDeleteDB(urlCleanup, queryCallback)

            # Call remove attributes
            AttrDeleteTask.deleteUrlsAttributes(urlCleanup.siteId, self.urlMd5, queryCallback)

          generalResponse.statuses.append(True)
          self.recalculator.commonRecalc(urlCleanup.siteId, queryCallback, \
                                         dc.EventObjects.FieldRecalculatorObj.PARTITION_RECALC)
        except Exception:
          generalResponse.statuses.append(False)
          type_, value_, traceback_ = sys.exc_info()  # pylint: disable=unused-variable
          stack = traceback.format_tb(traceback_)
          logger.error(str(stack.pop()))
      else:
        generalResponse.statuses.append(False)
    return generalResponse


  # @extractUrlByCriterions method makes sql request. using criterions and returns result
  #
  # @param siteId - incoming siteId for SQL request addition cause
  # @param criterions - incoming criterions for SQL request
  # @return urls list (fetched from criterions sql)
  def extractUrlByCriterions(self, siteId, isUrlExtract, criterions, queryCallback, dbName=Constants.SECONDARY_DB_ID,
                             tablePrefix=Constants.DC_URLS_TABLE_NAME_TEMPLATE):
    retUrls = []
    tableName = tablePrefix % siteId
    if isUrlExtract:
      SQLUrlExtractor = "SELECT `URL` FROM `%s`" % tableName
    else:
      SQLUrlExtractor = "SELECT `URLMd5` FROM `%s`" % tableName
    query = SQLUrlExtractor + self.generateCriterionSQL(criterions)
    res = queryCallback(query, dbName)
    if hasattr(res, '__iter__'):
      logger.debug(">>> Select URL len(res) = " + str(len(res)))
      for row in res:
        retUrls.append(row[0])

    return retUrls


  # Get site's fields
  #
  # @param siteId - incoming siteId for SQL request addition cause
  # @return fields list (fetched from criterions sql)
  def getSiteFields(self, siteId, queryCallback, dbName=Constants.PRIMARY_DB_ID):
    res = None

    query = "SELECT * FROM `dc_sites`.`sites` WHERE `Id` = '%s' LIMIT 1" % siteId
    res = queryCallback(query, dbName, Constants.EXEC_NAME)
    if len(res) > 0:
      res = res[0]

    return res


  # @todo urldelete - make base class
  # #delete data from key value db
  #
  # @param urlDelete instance of URLDelete object
  # @param queryCallback function for queries execution
  def deleteFromDataStorage(self, urlCleanup, queryCallback):
    # @todo try block + check table name
    ret = None
    if self.dBDataTask is not None:
      localUrlMd5 = self.calculateMd5FormUrl(urlCleanup.url, urlCleanup.urlType)
      dataDeleteRequest = dc.EventObjects.DataDeleteRequest(urlCleanup.siteId, localUrlMd5, None)
      ret = self.dBDataTask.process(dataDeleteRequest, queryCallback)
    return ret


  # #delete data from raw storage
  #
  # @param urlDelete instance of URLDelete object
  # @param queryCallback function for queries execution
  def deleteFromRawStorage(self, urlCleanup):
    localUrlMd5 = self.calculateMd5FormUrl(urlCleanup.url, urlCleanup.urlType)
    dataDir = self.rawDataDir + '/' + urlCleanup.siteId + '/' + PathMaker(localUrlMd5).getDir()
    logger.debug(">>> CLEANUP DIR = " + str(dataDir))
    if os.path.isdir(dataDir):
      try:
        shutil.rmtree(dataDir)
        hiLevelDir = dataDir[0: dataDir.rfind('/') if dataDir.rfind('/') >= 0 else len(dataDir)]
        if len(os.listdir(hiLevelDir)) == 0:
          shutil.rmtree(hiLevelDir)
      except OSError as ex:
        logger.debug(">>> [%s] Dir delete error - MSG [%s]", dataDir, str(ex.message))


  # #update data in mysql db
  #
  # @param urlCleanup instance of URLDelete or URLCleanup object
  # @param queryCallback function for queries execution
  # @param siteId Site Id
  def updateMysqlDB(self, urlCleanup, queryCallback, siteId):
    localState = urlCleanup.state if urlCleanup.state is not None else "state"
    localStatus = urlCleanup.status if urlCleanup.status is not None else "status"
    uDate = ''
    if localStatus == dc.EventObjects.URL.STATUS_NEW:
      sf = self.getSiteFields(siteId, queryCallback)
      if sf is not None and 'RecrawlPeriod' in sf:
        uDate = ", `UDate`=DATE_SUB(`UDate`,  INTERVAL %s MINUTE)" % sf['RecrawlPeriod']
    else:
      uDate = ", `UDate`=NOW()"
    sqlt = "UPDATE `%s` SET `TcDate`=NOW()%s, `state` = '%s', `status` = '%s' WHERE `URLMD5` = '%s' LIMIT 1"
    localUrlMd5 = self.calculateMd5FormUrl(urlCleanup.url, urlCleanup.urlType)
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlCleanup.siteId
    query = sqlt % (tableName, uDate, localState, localStatus, localUrlMd5)
    queryCallback(query, Constants.SECONDARY_DB_ID)


  # #update data in mysql db
  #
  # @param urlCleanup instance of URLDelete or URLCleanup object
  # @param queryCallback function for queries execution
  def copyUrlToDeleteDB(self, urlCleanup, queryCallback):
    SQL_COPY_QUERY_TEMPLATE = "INSERT INTO %s SELECT * FROM `dc_urls`.`%s` WHERE `URLMD5` = '%s'"
    tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlCleanup.siteId
    query = Constants.SQL_CREATE_QUERY_TEMPLATE % (tbName, tbName)
    queryCallback(query, Constants.FOURTH_DB_ID)
    query = SQL_COPY_QUERY_TEMPLATE % (tbName, tbName, self.urlMd5)
    queryCallback(query, Constants.FOURTH_DB_ID)
