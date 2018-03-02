'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import copy
import hashlib
import dc.EventObjects
from dtm.EventObjects import GeneralResponse
import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
from dc_db.URLCleanupTask import URLCleanUpTask
from dc_db.StatisticLogManager import StatisticLogManager
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #process urlCleanUp event
class URLPurgeTask(BaseTask):

  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLPurgeTask, self).__init__()
    self.uRLCleanUpTask = URLCleanUpTask(keyValueStorageDir, rawDataDir, dBDataTask)
    self.dBDataTask = dBDataTask
    self.urlMd5 = None


  # #Looks available urls in getting table
  #
  # @param urlPurge base purge object
  # @param tbName table name
  # @param queryCallback function for queries execution
  # @return bool value
  def isAvailableUrls(self, urlPurge, tbName, queryCallback):
    ret = False
    localUrls = self.uRLCleanUpTask.extractUrlByCriterions(tbName[5:], True, urlPurge.criterions,
                                                           queryCallback, Constants.FOURTH_DB_ID)
    if localUrls is not None and len(localUrls) > 0:
      ret = True
    if ret:
      logger.debug(">>> Has urls by criterions, bdName = " + tbName)
    else:
      logger.debug(">>> Not content urls by criterions, bdName = " + tbName)
    return ret



  # #creates (read available tables from 'urls_deleted') and returns purges list
  #
  # @param urlPurge base purge object
  # @param siteLimits limitations on tables list
  # @param queryCallback function for queries execution
  # @return purges list
  def getAdditionPurges(self, urlPurge, siteLimits, queryCallback):
    ret = []
    if siteLimits is not None and hasattr(siteLimits, '__iter__') and len(siteLimits) >= 2 and int(siteLimits[0]) >= 0:
      query = "SHOW TABLES"
      res = queryCallback(query, Constants.FOURTH_DB_ID)
      if res is not None:
        startLimit = int(siteLimits[0])
        countLimit = int(siteLimits[1])
        if countLimit == dc.EventObjects.URLPurge.ALL_SITES:
          countLimit = len(res)
        i = startLimit
        for num in xrange(i, len(res)):
          if len(ret) >= countLimit:
            break
          if res[num] is not None and res[num][0] is not None and \
          self.isAvailableUrls(urlPurge, res[num][0], queryCallback):
            localPurge = copy.deepcopy(urlPurge)
            localPurge.siteId = res[num][0][5:]
            localPurge.url = None
            ret.append(localPurge)
    else:
      logger.error(">>> siteLimits field must be type of [x, x] and not None")
    return ret


  # #looks table exist in the urls_deleted tables
  #
  # @param siteId sites id of looking table
  # @param queryCallback function for queries execution
  # @return bool value
  def isDeleteTableExist(self, siteId, queryCallback):
    ret = False
    query = "SHOW TABLES"
    dbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
    res = queryCallback(query, Constants.FOURTH_DB_ID)
    logger.debug(">>> Delete tables = " + str(res))
    if res is not None and hasattr(res, '__iter__'):
      for table in res:
        if table is not None and hasattr(table, '__iter__') and dbName in table:
          ret = True
          break
    return ret


  # #make all necessary actions to purging urls data from db
  #
  # @param urlPurges list of URLPurge objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, urlPurges, queryCallback):
    generalResponse = GeneralResponse()

    newPurges = copy.deepcopy(urlPurges)
    for urlPurge in urlPurges:
      if urlPurge.siteId is None:
        logger.debug(">>> Site Limits = " + str(urlPurge.siteLimits))
        newPurges = newPurges + self.getAdditionPurges(urlPurge, urlPurge.siteLimits, queryCallback)

    if len(urlPurges) != len(newPurges):
      logger.debug(">>> Purges reassign")
      urlPurges = newPurges

    for urlPurge in urlPurges:
      # @todo add more complex case
      urlsCount = 0
      if urlPurge.siteId == "":
        urlPurge.siteId = "0"
      if self.isDeleteTableExist(urlPurge.siteId, queryCallback):
        try:
          localUrls = []
          if urlPurge.url is None:
            isUrlExtract = False
            logger.debug(">>> UrlType = " + str(urlPurge.urlType))
            if urlPurge.urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
              isUrlExtract = True
            localUrls = self.uRLCleanUpTask.extractUrlByCriterions(urlPurge.siteId, isUrlExtract, urlPurge.criterions,
                                                                   queryCallback, Constants.FOURTH_DB_ID)
          else:
            localUrls.append(urlPurge.url)
          logger.debug(">>> [PURGE] localUrls size = " + str(len(localUrls)))
          for localUrl in localUrls:
            try:
              urlPurge.url = localUrl
              if not self.checkUrlInDcUrls(urlPurge, queryCallback):
                self.uRLCleanUpTask.deleteFromDataStorage(urlPurge, queryCallback)
                self.uRLCleanUpTask.deleteFromRawStorage(urlPurge)
              self.deleteUrlDBField(urlPurge, queryCallback)
              if self.urlMd5 is not None:
                StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_PURGED_STATE, 1,
                                                    urlPurge.siteId, self.urlMd5)
              urlsCount = urlsCount + 1
            except Exception as ex:
              logger.debug(">>> [PURGE] Some Type Exception [LOOP] = " + str(type(ex)) + " " + str(ex))
        except Exception as ex:
          logger.debug(">>> [PURGE] Some Type Exception = " + str(type(ex)) + " " + str(ex))
      else:
        logger.debug(">>> [PURGE] Table not found, SiteId = " + str(urlPurge.siteId))

      generalResponse.statuses.append([urlPurge.siteId, urlsCount])
      logger.debug(">>> [PURGE] Rsult = " + str([urlPurge.siteId, urlsCount]))
    return generalResponse


  # #deletes url record from MySQL "urls_deleted" db
  #
  # @param urlDelete list of URLDelete objects
  # @param queryCallback function for queries execution
  def deleteUrlDBField(self, urlPurge, queryCallback):
    SQL_DELETE_TEMPLATE = "DELETE FROM %s WHERE `UrlMd5` = '%s'"
    dbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlPurge.siteId
    if urlPurge.urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
      self.urlMd5 = hashlib.md5(urlPurge.url).hexdigest()
    else:
      self.urlMd5 = urlPurge.url
    query = SQL_DELETE_TEMPLATE % (dbName, self.urlMd5)
    queryCallback(query, Constants.FOURTH_DB_ID)


  # #checkUrlInDcUrls method looks URL in main(DC_URLs) DB
  #
  # @param urlDelete list of URLDelete objects
  # @param queryCallback function for queries execution
  def checkUrlInDcUrls(self, urlPurge, queryCallback):
    ret = False
    SQL_DELETE_TEMPLATE = "SELECT url FROM %s WHERE `UrlMd5` = '%s' AND `tcDate` NOT IN " + \
                          "(SELECT `tcDate` FROM dc_urls_deleted.%s WHERE `UrlMd5` = '%s') LIMIT 1"
    dbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlPurge.siteId
    if urlPurge.urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
      urlMd5 = hashlib.md5(urlPurge.url).hexdigest()
    else:
      urlMd5 = urlPurge.url
    query = SQL_DELETE_TEMPLATE % (dbName, urlMd5, dbName, urlMd5)
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if res is not None and len(res) > 0:
      ret = True
    logger.debug(">>> [PURGE] checkUrlInDcUrls 'UrlMd5' = " + urlMd5)
    if ret:
      logger.debug(" has record in dc_urls")
    else:
      logger.debug(" DOESN'T has record in dc_urls")
    return ret
