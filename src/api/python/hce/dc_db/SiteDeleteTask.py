'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc_db.SiteCleanUpTask as SiteCleanUpTask
import dc_db.Constants as Constants
import SiteTask
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401
from dtm.EventObjects import GeneralResponse

logger = Utils.MPLogger().getLogger()


# #class implemented all logic necessary to process SiteDelete request
#
class SiteDeleteTask(SiteCleanUpTask.SiteCleanUpTask):


  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(SiteDeleteTask, self).__init__(keyValueStorageDir, rawDataDir, dBDataTask)
    self.dBDataTask = dBDataTask


  # #cleanup all site data from mysql db
  #
  # @param siteDelete instance of SiteDelete object
  # @param queryCallback function for quieries execution
  def process(self, siteDeletes, queryCallback):
    ret = GeneralResponse()
    if not isinstance(siteDeletes, list):
      siteDeletes = [siteDeletes]

    for siteDelete in siteDeletes:
      localIds = []
      if siteDelete.id is None:
        localIds = SiteTask.SiteTask.execSiteCriterions(siteDelete.criterions, queryCallback)
      else:
        localIds.append(siteDelete.id)
      logger.debug(">>> SiteDeleteTask, ids are = " + str(localIds))

      for localId in localIds:
        self.errorCode = 0
        self.errorMessage = "OK"
        siteDelete.id = localId
        self.dropURLTable(siteDelete, queryCallback)
        self.dropArbitraryTable(Constants.DC_FREQ_TABLE_NAME_TEMPLATE, siteDelete, Constants.STAT_DB_ID, queryCallback)
        self.dropArbitraryTable(Constants.DC_LOG_TABLE_NAME_TEMPLATE, siteDelete, Constants.LOG_DB_ID, queryCallback)
        self.dropArbitraryTable(Constants.DC_ATT_TABLE_NAME_TEMPLATE, siteDelete, Constants.ATT_DB_ID, queryCallback)
        self.removeSiteRecord(siteDelete, queryCallback)
        self.clearRelatedTables(siteDelete, queryCallback)

        # the rest as in  SiteCleanUpTask
        if siteDelete.delayedType == dc.EventObjects.NOT_DELAYED_OPERATION:
          super(SiteDeleteTask, self).cleanUpDBStorage(siteDelete, SiteCleanUpTask.KEY_VALUE_FILE_NAME_TEMPLATE,
                                                       queryCallback)
          super(SiteDeleteTask, self).cleanUpDBStorage(siteDelete, SiteCleanUpTask.KEY_VALUE_FIELDS_FILE_NAME_TEMPLATE,
                                                       queryCallback)
          super(SiteDeleteTask, self).cleanUpRawDataStorage(siteDelete)
        ret.errorCode = self.errorCode
        ret.statuses.append(ret.errorCode)
        if ret.errorMessage is None or ret.errorMessage == "":
          ret.errorMessage = self.errorMessage
        else:
          ret.errorMessage += ("-" + self.errorMessage)

    return ret


  # #drops urls_Site_Id table
  #
  # @param siteDelete instance of SiteDelete object
  # @param queryCallback function for quieries execution
  def dropURLTable(self, siteDelete, queryCallback):
    SQL_DROP_QUERY_TEMPLATE = "DROP TABLE IF EXISTS `%s`"
    tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteDelete.id
    query = SQL_DROP_QUERY_TEMPLATE % tbName
    queryCallback(query, Constants.SECONDARY_DB_ID)
    queryCallback(query, Constants.FOURTH_DB_ID)


  # #method drops arbitrary table in specified db
  #
  # @param siteCleanup instance of SiteCleanup object
  # @param dbId specific db id
  # @param queryCallback function for quieries execution
  def dropArbitraryTable(self, tablePrefix, siteDelete, dbId, queryCallback):
    tbName = tablePrefix % siteDelete.id
    SQL_DROP_QUERY_TEMPLATE = "DROP TABLE IF EXISTS `%s`"
    query = SQL_DROP_QUERY_TEMPLATE % tbName
    queryCallback(query, dbId)


  # #deletes related records from `sites` table
  #
  # @param siteDelete instance of SiteDelete object
  # @param queryCallback function for quieries execution
  def removeSiteRecord(self, siteDelete, queryCallback):
    DELETE_SITE_SQL_QUERY = "DELETE FROM `sites` WHERE id = '%s'"
    query = DELETE_SITE_SQL_QUERY % siteDelete.id
    queryCallback(query, Constants.PRIMARY_DB_ID)


  # #deletes related records from `sites_urls`, `sites_filters` and `sites_properties` tables
  #
  # @param siteDelete instance of SiteDelete object
  # @param queryCallback function for quieries execution
  def clearRelatedTables(self, siteDelete, queryCallback):
    tebleList = ["`sites_urls`", "`sites_filters`", "`sites_properties`"]
    DELETE_SITE_SQL_QUERY = "DELETE FROM %s WHERE Site_Id = '%s'"
    for tableName in tebleList:
      query = DELETE_SITE_SQL_QUERY % (tableName, siteDelete.id)
      queryCallback(query, Constants.PRIMARY_DB_ID)
