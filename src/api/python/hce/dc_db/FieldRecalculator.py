'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc_db.Constants as Constants
import dc_db.FieldRecalculatorDefaultCriterions as DefCriterions
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #FieldRecalculator class makes come common processing of databse fields recalculation (using in Task classes)
class FieldRecalculator(object):

  def __init__(self):
    pass


  # #commonSiteRecalculate - common recalculate method
  #
  # @param queryCallback function for queries execution
  # @param additionCause additional SQL cause
  # @param fieldName - processing field name (of `sites` tables)
  # @param siteId - site id
  def commonSiteRecalculate(self, defaultCritName, fieldName, siteId, queryCallback):
    UPDATE_SQL_TEMPLATE = "UPDATE `sites` SET `%s`=(SELECT COUNT(*) FROM dc_urls.%s %s) WHERE `id` = '%s'"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    criterionsString = DefCriterions.getDefaultCriterions(defaultCritName, siteId, queryCallback)
    query = UPDATE_SQL_TEMPLATE % (fieldName, tableName, criterionsString, siteId)
    queryCallback(query, Constants.PRIMARY_DB_ID)

  # #siteResourcesRecalculate - recalculate sites.Resources field
  #
  def siteResourcesRecalculate(self, siteId, queryCallback):
    # self.commonSiteRecalculate(queryCallback, "State>3 AND Crawled>0", "Resources", siteId)
    # self.commonSiteRecalculate("Crawled>0 AND Size>0", "Resources", siteId, queryCallback)
    self.commonSiteRecalculate(DefCriterions.CRIT_RESOURCES, "Resources", siteId, queryCallback)


  # #siteContentsRecalculate - recalculate sites.Contents field
  #
  def siteContentsRecalculate(self, siteId, queryCallback):
    # self.commonSiteRecalculate(queryCallback, "State=7 AND Crawled>0 AND Processed>0", "Contents", siteId)
    self.commonSiteRecalculate(DefCriterions.CRIT_CONTENTS, "Contents", siteId, queryCallback)


  # updateCollectedURLs updates sites.CollectedURLs field
  #
  # @param siteId - siteId
  # @param queryCallback - callback sql function
  def updateCollectedURLs(self, siteId, queryCallback):
    QUERY_TEMPLATE = "UPDATE `sites` SET `CollectedURLs`=(SELECT count(*) FROM dc_urls.%s %s) WHERE `Id`='%s'"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    criterionsString = DefCriterions.getDefaultCriterions(DefCriterions.CRIT_CLURLS, siteId, queryCallback)
    query = QUERY_TEMPLATE % (tableName, criterionsString, siteId)
    queryCallback(query, Constants.PRIMARY_DB_ID)


  # updateNewURLs updates sites.newURLs field
  #
  # @param siteId - siteId
  # @param queryCallback - callback sql function
  def updateNewURLs(self, siteId, queryCallback):
    QUERY_TEMPLATE = "UPDATE `sites` SET `NewURLs`=(SELECT count(*) FROM dc_urls.%s %s) WHERE `Id`='%s'"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    criterionsString = DefCriterions.getDefaultCriterions(DefCriterions.CRIT_NURLS, siteId, queryCallback)
    query = QUERY_TEMPLATE % (tableName, criterionsString, siteId)
    queryCallback(query, Constants.PRIMARY_DB_ID)


  # updateErrors updates sites.Errors field
  #
  # @param siteId - siteId
  # @param queryCallback - callback sql function
  def updateErrors(self, siteId, queryCallback):
    QUERY_TEMPLATE = "UPDATE `sites` SET `Errors`=(SELECT count(*) FROM dc_urls.%s %s) WHERE `Id`='%s'"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    criterionsString = DefCriterions.getDefaultCriterions(DefCriterions.CRIT_ERRORS, siteId, queryCallback)
    query = QUERY_TEMPLATE % (tableName, criterionsString, siteId)
    queryCallback(query, Constants.PRIMARY_DB_ID)


  # updateDeletedURLs updates sites.deletedURLs field
  #
  # @param siteId - siteId
  # @param queryCallback - callback sql function
  def updateDeletedURLs(self, siteId, queryCallback):
    QUERY_TEMPLATE_SELECT = "SELECT count(*) FROM %s %s"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    criterionsString = DefCriterions.getDefaultCriterions(DefCriterions.CRIT_DURLS, siteId, queryCallback)
    query = QUERY_TEMPLATE_SELECT % (tableName, criterionsString)
    res = queryCallback(query, Constants.FOURTH_DB_ID, Constants.EXEC_INDEX, True)
    if res is not None and len(res) > 0 and len(res[0]) > 0:
      count = res[0][0]
      QUERY_TEMPLATE_UPDATE = "UPDATE `sites` SET `DeletedURLs`=%s WHERE `Id`='%s'"
      query = QUERY_TEMPLATE_UPDATE % (str(count), siteId)
      queryCallback(query, Constants.PRIMARY_DB_ID)


  # commonRecalc method makes all recalculations
  #
  # @param siteId - siteId
  # @param queryCallback - callback sql function
  # @param recalcType - full or partial recalculating
  def commonRecalc(self, siteId, queryCallback, recalcType=dc.EventObjects.FieldRecalculatorObj.FULL_RECALC):
    self.siteResourcesRecalculate(siteId, queryCallback)
    self.siteContentsRecalculate(siteId, queryCallback)
    if recalcType == dc.EventObjects.FieldRecalculatorObj.FULL_RECALC:
      self.updateCollectedURLs(siteId, queryCallback)
    self.updateNewURLs(siteId, queryCallback)
    self.updateDeletedURLs(siteId, queryCallback)
    self.updateSiteCleanupFields(siteId, queryCallback)


  # updateSiteCleanupFields recalculates some site's fields in SiteCleanUpTask operation
  #
  # @param siteId - siteId
  # @param queryCallback - callback sql function
  def updateSiteCleanupFields(self, siteId, queryCallback):
    QUERY_TEMPLATE = "UPDATE `sites` SET `Size`=%s, `Errors`=%s, `ErrorMask`=%s, `AVGSpeed`=%s WHERE `Id`='%s'"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    localSize = "`Size`"
    localErrors = "`Errors`"
    localErrorMask = "`ErrorMask`"
    localSpeed = "`AVGSpeed`"
    TMP_QUERY_TEMPLATE = "SELECT SUM(`Size`) FROM %s WHERE " + DefCriterions.CRIT_CRAWLED_THIS_NODE
    query = TMP_QUERY_TEMPLATE % tableName
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if res is not None and len(res) > 0 and res[0] is not None and len(res[0]) > 0 and res[0][0] is not None:
      localSize = str(res[0][0])
    TMP_QUERY_TEMPLATE = "SELECT COUNT(*) FROM %s WHERE `errorMask` > 0 AND " + DefCriterions.CRIT_CRAWLED_THIS_NODE
    query = TMP_QUERY_TEMPLATE % tableName
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if res is not None and len(res) > 0 and res[0] is not None and len(res[0]) > 0 and res[0][0] is not None:
      localErrors = str(res[0][0])
    TMP_QUERY_TEMPLATE = "SELECT BIT_OR(`errorMask`) FROM %s WHERE " + DefCriterions.CRIT_CRAWLED_THIS_NODE
    query = TMP_QUERY_TEMPLATE % tableName
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if res is not None and len(res) > 0 and res[0] is not None and len(res[0]) > 0 and res[0][0] is not None:
      localErrorMask = str(res[0][0])
    TMP_QUERY_TEMPLATE = "SELECT AVG(`size`/`crawlingTime`*1000) FROM %s WHERE `crawlingTime` > 0 AND " + \
                         DefCriterions.CRIT_CRAWLED_THIS_NODE
    query = TMP_QUERY_TEMPLATE % tableName
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if res is not None and len(res) > 0 and res[0] is not None and len(res[0]) > 0 and res[0][0] is not None:
      localSpeed = str(res[0][0])
    query = QUERY_TEMPLATE % (localSize, localErrors, localErrorMask, localSpeed, siteId)
    queryCallback(query, Constants.PRIMARY_DB_ID)
