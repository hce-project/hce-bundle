'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import hashlib
import dc.EventObjects
from dtm.EventObjects import GeneralResponse
import dc_db.Constants as Constants
from dc_db.FieldRecalculator import FieldRecalculator
from dc_db.BaseTask import BaseTask
from dc_db.URLCleanupTask import URLCleanUpTask
from dc_db.StatisticLogManager import StatisticLogManager
from dc_db.AttrDeleteTask import AttrDeleteTask
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #process urlDelete event
class URLDeleteTask(BaseTask):


  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLDeleteTask, self).__init__()
    self.uRLCleanUpTask = URLCleanUpTask(keyValueStorageDir, rawDataDir, dBDataTask)
    self.recalculator = FieldRecalculator()
    self.urlMd5 = None
    # self.dBDataTask = dBDataTask


  # #make all necessary actions to delete urls data from db
  #
  # @param urlDelete list of URLDelete objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, urlDeletes, queryCallback):
    ret = GeneralResponse()
    for urlDelete in urlDeletes:
      if urlDelete.siteId == "":
        urlDelete.siteId = "0"
      if self.isSiteExist(urlDelete.siteId, queryCallback):
        try:
          localUrls = []
          if urlDelete.url is None:
            isUrlExtract = False
            if urlDelete.urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
              isUrlExtract = True
            localUrls = self.uRLCleanUpTask.extractUrlByCriterions(urlDelete.siteId, isUrlExtract,
                                                                   urlDelete.criterions, queryCallback)
          else:
            localUrls.append(urlDelete.url)
          logger.debug(">>> [URLDelete] localUrls size = " + str(len(localUrls)))
          for localUrl in localUrls:
            try:
              urlDelete.url = localUrl
              if urlDelete.delayedType == dc.EventObjects.NOT_DELAYED_OPERATION:
                self.uRLCleanUpTask.deleteFromDataStorage(urlDelete, queryCallback)
                self.uRLCleanUpTask.deleteFromRawStorage(urlDelete)
              elif urlDelete.delayedType == dc.EventObjects.DELAYED_OPERATION:
                self.copyUrlToDeleteDB(urlDelete, queryCallback)
              self.deleteFromMysqlDB(urlDelete, queryCallback)
              AttrDeleteTask.deleteUrlsAttributes(urlDelete.siteId, self.urlMd5, queryCallback)
              if self.urlMd5 is not None:
                StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_DELETE, 1,
                                                    urlDelete.siteId, self.urlMd5)
                StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_DELETED_STATE, 1,
                                                    urlDelete.siteId, self.urlMd5)
                StatisticLogManager.logUpdate(queryCallback, "LOG_DELETE", urlDelete, urlDelete.siteId, self.urlMd5)
            except Exception as ex:
              logger.debug(">>> [URLDelete] Some Type Exception [LOOP] = " + str(type(ex)) + " " + str(ex))
          ret.statuses.append(True)
          self.recalculator.commonRecalc(urlDelete.siteId, queryCallback)
        except Exception as excp:
          logger.debug(">>> [URLDelete] Some Type Exception = " + str(type(excp)) + " " + str(excp))
          ret.statuses.append(False)
      else:
        ret.statuses.append(False)

    return ret


  # #update data in mysql db
  #
  # @param urlDelete instance of URLDelete object
  # @param queryCallback function for queries execution
  def deleteFromMysqlDB(self, urlDelete, queryCallback):
    self.urlMd5 = self.calculateMd5FormUrl(urlDelete.url, urlDelete.urlType, True)
    SQL_CLAUSE = ("`URLMd5` = '%s'" % self.urlMd5)
    UPDATE_SQL_TEMPLATE = "DELETE FROM `%s` WHERE %s"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlDelete.siteId
    query = UPDATE_SQL_TEMPLATE % (tableName, SQL_CLAUSE)
    queryCallback(query, Constants.SECONDARY_DB_ID)


  # #update data in mysql db
  #
  # @param urlDelete instance of URLDelete or URLCleanup object
  # @param queryCallback function for queries execution
  def copyUrlToDeleteDB(self, urlDelete, queryCallback):
    if urlDelete.urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
      localMd5 = hashlib.md5(urlDelete.url).hexdigest()
    else:
      localMd5 = urlDelete.url
    SQL_COPY_QUERY_TEMPLATE = "INSERT INTO %s SELECT * FROM dc_urls.%s WHERE `URLMd5` = '%s'"
    tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlDelete.siteId
    # TODO: One more query for each delete request is too heavy for DB
    # query = Constants.SQL_CREATE_QUERY_TEMPLATE % (tbName, tbName)
    # queryCallback(query, Constants.FOURTH_DB_ID)
    query = SQL_COPY_QUERY_TEMPLATE % (tbName, tbName, localMd5)
    queryCallback(query, Constants.FOURTH_DB_ID, Constants.EXEC_INDEX, True)
