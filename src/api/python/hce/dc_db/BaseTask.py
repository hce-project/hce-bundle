'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import time
import hashlib
import datetime
import dc_db.Constants as Constants
from dc_db.StatisticLogManager import StatisticLogManager
import dc.EventObjects
import app.SQLCriterions
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #Class contains operations common for all tasks
class BaseTask(object):

  # #check if given site exist in current db
  #
  # @param siteId id of checking site
  # @param queryCallback function for queries execution
  # @return True if exist, or False
  def isSiteExist(self, siteId, queryCallback, userId=None):
    retVal = False
    if siteId is not None:
      query = Constants.CHECK_TABLE_SQL_TEMPLATE % siteId
      if userId is not None:
        query += (Constants.CHECK_TABLE_SQL_ADDITION % str(userId))
      res = queryCallback(query, Constants.PRIMARY_DB_ID)
      if res is not None and len(res) > 0 and len(res[0]) > 0 and res[0][0] > 0:
        retVal = True  # first elem from first tuple

    return retVal


  # #Generates criterion string from urlFetch.criterions or urlUpdate.criterions fields
  #
  # @param criterions - incoming criterions
  # @param additionWhere - additions WHERE cause
  def generateCriterionSQL(self, criterions, additionWhere=None, siteId=None):
    return app.SQLCriterions.generateCriterionSQL(criterions, additionWhere, siteId)


  # #method returns ids elements fetching by criterions
  #
  # @param criterions - incoming criterions
  # @param queryCallback function for queries execution
  # @return site ids
  def fetchByCriterions(self, criterions, queryCallback):
    ids = []
    additionWhere = self.generateCriterionSQL(criterions)
    if additionWhere is not None and additionWhere != "":
      query = "SELECT `id` FROM `sites`" + additionWhere
      res = queryCallback(query, Constants.PRIMARY_DB_ID)
      if hasattr(res, '__iter__'):
        for elem in res:
          ids.append(elem[0])
    return ids


  # #Cross-app locking, based on MySQL db, locking
  #
  # @param mutexName - mutex name
  # @param queryCallback queryCallback function for queries execution
  # @param sleepTime timeout (in seconds) between lock tries
  # @param timeout - internal lock timeout
  def dbLock(self, mutexName, queryCallback, sleepTime=1, mutexLockTTL=Constants.DEFAULT_LOCK_TTL):
    logger.debug(">>> BaseTask Class. Lock start name=" + mutexName)
    LOCK_QUERY_TEMPLATE = "SELECT mutexLock('%s', %s, %s)"
    query = LOCK_QUERY_TEMPLATE % (mutexName, str(Constants.DB_LOCK_APPLICATION_ID), str(mutexLockTTL))
    res = queryCallback(query, Constants.PRIMARY_DB_ID)
    while res is not None and len(res) > 0 and res[0][0] == 0:
      time.sleep(sleepTime)
      res = queryCallback(query, Constants.PRIMARY_DB_ID)
    logger.debug(">>> BaseTask Class. Lock finish name=" + mutexName)


  # #Cross-app locking, based on MySQL db, unlocking
  #
  # @param mutexName - mutex name
  # @param queryCallback queryCallback function for queries execution
  def dbUnlock(self, mutexName, queryCallback):
    logger.debug(">>> BaseTask Class. Unlock start name=" + mutexName)
    LOCK_QUERY_TEMPLATE = "SELECT mutexUnlock('%s', %s)"
    query = LOCK_QUERY_TEMPLATE % (mutexName, str(Constants.DB_LOCK_APPLICATION_ID))
    queryCallback(query, Constants.PRIMARY_DB_ID)
    logger.debug(">>> BaseTask Class. Unlock finish name=" + mutexName)


  # #method makes insert query into dc_urls db
  #
  # @param siteId - site's id
  # @param localKeys - url's inserting keys
  # @param localValues - url's inserting localValues
  def createUrlsInsertQuery(self, siteId, localKeys, localValues):
    logger.debug(">>> Create Url Insert request")
    query = None
    tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    fieldValueString = Constants.createFieldsValuesString(localKeys, localValues)
    if fieldValueString is not None and fieldValueString != "":
      query = Constants.INSERT_COMMON_TEMPLATE % (tbName, fieldValueString)
    return query


  # #Makes url's copy from dc_sites to dc_urls sites
  #
  # @param siteId - site's id
  # @param queryCallback queryCallback function for queries execution
  def copyUrlsToDcUrls(self, siteId, queryCallback):
    logger.debug(">>> Urls copy operation")
    COPY_SELECT_SQL_TEMPLATE = "SELECT * FROM `sites_urls` WHERE `Site_Id`='%s'"
    query = COPY_SELECT_SQL_TEMPLATE % siteId
    res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    # logger.debug(">>> RES - " + str(type(res)))
    if res is not None:
      for urlRecord in res:
        logger.debug(">>> Urls copy operation KEY - " + str(urlRecord))
        localKeys = []
        localValues = []
        for keyRecord in urlRecord:
          for keySample in Constants.URLTableDict:
            if keyRecord == Constants.URLTableDict[keySample] and urlRecord[keyRecord] is not None:
              localKeys.append(keyRecord)
              if isinstance(urlRecord[keyRecord], basestring) or \
              isinstance(urlRecord[keyRecord], datetime.datetime):
#                 escapingStr = MySQLdb.escape_string(str(urlRecord[keyRecord])) ## remove in future
                escapingStr = Utils.escape(str(urlRecord[keyRecord]))
                localValues.append(("'" + escapingStr + "'"))
              else:
                localValues.append(str(urlRecord[keyRecord]))
              break
        logger.debug(">>> Urls copy operation LEN - " + str(len(localKeys)))
        if len(localKeys) > 0:
          query = self.createUrlsInsertQuery(siteId, localKeys, localValues)
          if query is not None:
            res = queryCallback(query, Constants.SECONDARY_DB_ID)

            if 'URLMd5' in urlRecord and urlRecord['URLMd5'] is not None:
              StatisticLogManager.addNewRecord(queryCallback, siteId, urlRecord['URLMd5'])
              if 'Status' in urlRecord and urlRecord['Status'] is not None:
                self.statisticLogUpdate(None, urlRecord['URLMd5'], siteId, urlRecord['Status'], queryCallback, True)


  # #updates statistic and logs databases
  #
  # @param urlObject instance of URL object
  # @param queryCallback function for queries execution
  def statisticLogUpdate(self, localObj, urlMd5, siteId, status, queryCallback, isInsert=False):
    if urlMd5 is not None:
      StatisticLogManager.addNewRecord(queryCallback, siteId, urlMd5)
      if isInsert:
        StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_INSERT, 1, siteId,
                                            urlMd5)
        StatisticLogManager.logUpdate(queryCallback, "LOG_INSERT", localObj, siteId, urlMd5)
      if status == dc.EventObjects.URL.STATUS_NEW:
        StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_NEW_STATUS, 1,
                                            siteId, urlMd5)
        StatisticLogManager.logUpdate(queryCallback, "LOG_NEW", localObj, siteId, urlMd5)
      elif status == dc.EventObjects.URL.STATUS_SELECTED_CRAWLING:
        StatisticLogManager.logUpdate(queryCallback, "LOG_SELECTED_CRAWLING", localObj, siteId, urlMd5)
      elif status == dc.EventObjects.URL.STATUS_CRAWLING:
        StatisticLogManager.logUpdate(queryCallback, "LOG_CRAWLING", localObj, siteId, urlMd5)
      elif status == dc.EventObjects.URL.STATUS_CRAWLED:
        StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_CRAWLED_STATUS, 1,
                                            siteId, urlMd5)
        StatisticLogManager.logUpdate(queryCallback, "LOG_CRAWLED", localObj, siteId, urlMd5)
      elif status == dc.EventObjects.URL.STATUS_SELECTED_PROCESSING:
        StatisticLogManager.logUpdate(queryCallback, "LOG_SELECTED_PROCESSING", localObj, siteId, urlMd5)
      elif status == dc.EventObjects.URL.STATUS_PROCESSING:
        StatisticLogManager.logUpdate(queryCallback, "LOG_PROCESSING", localObj, siteId, urlMd5)
      elif status == dc.EventObjects.URL.STATUS_PROCESSED:
        StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_PROCESSED_STATS, 1,
                                            siteId, urlMd5)
        StatisticLogManager.logUpdate(queryCallback, "LOG_PROCESSED", localObj, siteId, urlMd5)


  # #calculateMd5FormUrl returns url's Md5, calculates it before or gets UrlMd5 from url value
  #
  # @param url - incoming url
  # @param urlType - url's Md5 calculating type
  # @return url's Md5
  def calculateMd5FormUrl(self, url, urlType, useNormilize=False):
    ret = url
    if urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
      logger.debug("calculateMd5FormUrl url: %s", str(url))
# TODO: need to be refactored and usage of URL replaced with the MD5 taken from DB
#      if useNormilize:
#        localUrlObj = dc.EventObjects.URL(None, url)
#        ret = localUrlObj.urlMd5
#      else:
#        ret = hashlib.md5(url).hexdigest()
      del useNormilize
      ret = hashlib.md5(url).hexdigest()

    return ret


  # #readValueFromSiteProp reead value from site_properties tables
  #
  # @param siteId - site's id
  # @param propName - site property name
  # @param queryCallback - function for queries execution
  # @param urlMd5 - urls MD5 - addition property fetching criterion
  @staticmethod
  def readValueFromSiteProp(siteId, propName, queryCallback, urlMd5=None):
    ret = None
    query = "SELECT `Value` FROM `sites_properties` WHERE `Site_Id`='%s' AND `Name`='%s'"
    query = (query % (siteId, propName))
    if urlMd5 is not None:
      query += (" AND `URLMd5`='%s'" % urlMd5)
    query += " LIMIT 1"
    res = queryCallback(query, Constants.PRIMARY_DB_ID)
    if res is not None and len(res) > 0 and len(res[0]) > 0:
      ret = res[0][0]
    return ret
