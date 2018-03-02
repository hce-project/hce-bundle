'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import MySQLdb as mdb
from app.Utils import UrlNormalizator
import app.Utils as Utils  # pylint: disable=F0401
from dc_db.URLUpdateTask import URLUpdateTask
from dc_db.SiteUpdateTask import SiteUpdateTask
from dc_db.BaseTask import BaseTask
from dc_db.AttrFetchTask import AttrFetchTask
import dc_db.Constants as Constants
import dc.EventObjects

logger = Utils.MPLogger().getLogger()


# #process urlFetch event
class URLFetchTask(BaseTask):


  # #constructor
  #
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask, dcSiteTemplate, keyValueDefaultFile,
               dcStatTemplate, dcLogTemplate, mutexLockTTL=Constants.DEFAULT_LOCK_TTL):
    super(URLFetchTask, self).__init__()
    self.quantMaxUrls = 0
    self.localSiteList = []
    self.mutexLockTTL = mutexLockTTL
    self.uRLUpdateTask = URLUpdateTask(keyValueStorageDir, rawDataDir, dBDataTask)
    self.siteUpdateTask = SiteUpdateTask(dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir, rawDataDir,
                                         dBDataTask, dcStatTemplate, dcLogTemplate, None)


  # #make all necessary actions to fetch urls data from db,
  # also locks db mutex (if locking ) between URLFetch operation
  #
  # @param urlFetches list of URLFetch objects
  # @param queryCallback function for queries execution
  # @return list of URL objects
  def process(self, urlFetches, queryCallback):
    ret = []
    needToLock = False
    try:
      for urlFetch in urlFetches:
        needToLock = urlFetch.isLocking
        if needToLock:
          self.dbLock(Constants.FETCH_LOCK_NAME, queryCallback, urlFetch.lockIterationTimeout, self.mutexLockTTL)
        # @todo add more complex case
        if urlFetch.algorithm is None or urlFetch.algorithm == dc.EventObjects.URLFetch.DEFAULT_ALGORITHM:
          ret.extend(self.processSimple(urlFetch, self.uRLUpdateTask, queryCallback))
        elif urlFetch.algorithm == dc.EventObjects.URLFetch.PROPORTIONAL_ALGORITHM:
          ret.extend(self.processProportial(urlFetch, self.uRLUpdateTask, queryCallback))

        for url in ret:
          attributeNames = urlFetch.attributeNames if hasattr(urlFetch, 'attributeNames') else ['*']
          url.attributes = AttrFetchTask.fetchUrlsAttributesByNames(url.siteId,
                                                                    url.urlMd5,
                                                                    queryCallback,
                                                                    attributeNames)

        if needToLock:
          self.dbUnlock(Constants.FETCH_LOCK_NAME, queryCallback)
    except Exception, err:
      logger.error('Exception: %s', str(err))
      if needToLock:
        self.dbUnlock(Constants.FETCH_LOCK_NAME, queryCallback)
      raise
    except mdb.Error, err:  # pylint: disable=E1101
      logger.error('mdb.Error: %s', str(err))
      if needToLock:
        self.dbUnlock(Constants.FETCH_LOCK_NAME, queryCallback)
      raise
    except:
      logger.error('Unknown type error')
      if needToLock:
        self.dbUnlock(Constants.FETCH_LOCK_NAME, queryCallback)
      raise
    return ret


  # #processProportial propostial algo implementing
  #
  # @param urlFetch incoming UrlFetch object
  # @param queryCallback function for queries execution
  # @param uRLUpdateTask incoming URLUpdateTask object
  # @return list of site_ids object
  def processProportial(self, urlFetch, uRLUpdateTask, queryCallback):
    ret = []
    offset = 0
    if urlFetch.maxURLs is not None and urlFetch.maxURLs > 0:
      urlFetch.sitesList = self.fillSiteList(urlFetch.sitesList, queryCallback, urlFetch.sitesCriterions)
#     look sites from SiteList for clearing (month ... mins) sites limits
#     self.limitsClearing(urlFetch.sitesList, queryCallback):
      if len(urlFetch.sitesList) > 0:
        self.quantMaxUrls = urlFetch.maxURLs / len(urlFetch.sitesList)
        if self.quantMaxUrls < 1:
          self.quantMaxUrls = 1

        while len(ret) < urlFetch.maxURLs and len(urlFetch.sitesList) > 0:
          self.fillCriterionLimits(urlFetch, offset)
          self.localSiteList = []
          logger.debug(">>> Debug-1 = %s %s %s %s",
                       str(urlFetch.urlsCriterions[dc.EventObjects.URLFetch.CRITERION_LIMIT][0]),
                       str(urlFetch.urlsCriterions[dc.EventObjects.URLFetch.CRITERION_LIMIT][1]),
                       str(urlFetch.maxURLs),
                       str(self.quantMaxUrls))
          ret.extend(self.getURLFromURLTable(urlFetch, len(ret), queryCallback))
          urlFetch.sitesList = self.localSiteList
          offset += self.quantMaxUrls
      else:
        logger.debug(">>> UrlFetch proportional >>> Empty SiteList")
    self.updateUrl(ret, urlFetch, uRLUpdateTask, queryCallback)
    return ret


  # #fillCriterionLimits calculates new limit and insert ot the urlsCriterions
  #
  # @param urlFetch incoming UrlFetch object
  # @return list of site_ids object
  def fillCriterionLimits(self, urlFetch, offset):
    if urlFetch.urlsCriterions is None:
      urlFetch.urlsCriterions = {}
    urlFetch.urlsCriterions[dc.EventObjects.URLFetch.CRITERION_LIMIT] = [offset, self.quantMaxUrls]


  # #processSimple simple algo implementing
  #
  # @param urlFetch incoming UrlFetch object
  # @param queryCallback function for queries execution
  # @param uRLUpdateTask incoming URLUpdateTask object
  # @return list of site_ids object
  def processSimple(self, urlFetch, uRLUpdateTask, queryCallback):
    urlFetch.sitesList = self.fillSiteList(urlFetch.sitesList, queryCallback, urlFetch.sitesCriterions)
#   look sites from SiteList for clearing (month ... mins) sites limits
#   self.limitsClearing(urlFetch.sitesList, queryCallback):
    ret = self.getURLFromURLTable(urlFetch, 0, queryCallback)

    self.updateUrl(ret, urlFetch, uRLUpdateTask, queryCallback)
    return ret


  # #updateUrl updates urls from urls list
  #
  # @param urls incoming urls list
  # @param urlFetch incoming UrlFetch object
  # @param queryCallback function for queries execution
  # @param uRLUpdateTask incoming URLUpdateTask object
  # @return list of site_ids object
  def updateUrl(self, urls, urlFetch, uRLUpdateTask, queryCallback):
    if len(urls) > 0:
      if urlFetch.urlUpdate is not None:
        for localURL in urls:
          if localURL.urlMd5 is not None:
            urlUpdateList = []
            urlUpdateList.append(urlFetch.urlUpdate)
            urlUpdateList[0].urlMd5 = localURL.urlMd5
            urlUpdateList[0].siteId = localURL.siteId
            uRLUpdateTask.process(urlUpdateList, queryCallback)
          if urlFetch.urlUpdate.status is not None:
            localURL.status = urlFetch.urlUpdate.status


  # #Generates SQL String request for using in the fillSiteList method
  #
  # @param sitesCriterions - income sitesCriterions field
  # @param userId - income userId field
  # @return query string
  def fillSiteListSQLGenerate(self, sitesCriterions, userId=None):
    query = Constants.SELECT_SQL_TEMPLATE_SIMPLE % ("`Id`", "sites")
    additionQueryStr = ""
    additionWhereCause = ""
    if userId is not None:
      additionWhereCause += (Constants.CHECK_TABLE_SQL_ADDITION % str(userId))

    if sitesCriterions is None:
      if additionWhereCause != "":
        additionWhereCause += " AND "
      additionWhereCause += ("`state`=%d" % dc.EventObjects.Site.STATE_ACTIVE)

    if sitesCriterions is None:
      if additionWhereCause != "":
        additionQueryStr = " WHERE " + additionWhereCause
    else:
      if additionWhereCause == "":
        additionQueryStr = self.generateCriterionSQL(sitesCriterions)
      else:
        additionQueryStr = self.generateCriterionSQL(sitesCriterions, additionWhereCause)
    query += additionQueryStr

    return query


  # #get id from sites
  #
  # @parama incomeSiteList - income (from event) site list
  # @param queryCallback function for queries execution
  # @param sitesCriterions - income sitesCriterions field
  # @param userId - income userId field
  # @return list of site_ids object
  def fillSiteList(self, incomeSiteList, queryCallback, sitesCriterions, userId=None):
    ret = []
    newSiteList = []
    localSiteDict = {}
    query = self.fillSiteListSQLGenerate(sitesCriterions, userId)
    logger.debug("!!! query: %s", str(query))
    res = None
    try:
      res = queryCallback(query, Constants.PRIMARY_DB_ID)
      logger.debug("!!! res: %s", str(res))
    except mdb.Error, err:  # pylint: disable=E1101
      logger.error("Error: %s", str(err))

    if res is not None and hasattr(res, '__iter__'):
      for row in res:
        localSiteDict[row[0]] = row[0]
        newSiteList.append(row[0])

      if len(incomeSiteList) == 0:
        ret = newSiteList
      else:
        newSiteList = []
        for site in incomeSiteList:
          if site in localSiteDict:
            newSiteList.append(site)
        ret = newSiteList

    return ret


  # #static fillUrlObj method, create and fills URL object
  #
  # @param row db select row with URL fields
  # @return URL object
  @staticmethod
  def fillUrlObj(row):
    url = dc.EventObjects.URL(row["Site_Id"], row["URL"], normalizeMask=UrlNormalizator.NORM_NONE)
    for field in Constants.URLTableDict.keys():
      if hasattr(url, field) and Constants.URLTableDict[field] in row:
        setattr(url, field, row[Constants.URLTableDict[field]])
    url.UDate = Constants.readDataTimeField("UDate", row)
    url.CDate = Constants.readDataTimeField("CDate", row)
    url.lastModified = Constants.readDataTimeField("LastModified", row)
    url.tcDate = Constants.readDataTimeField("TcDate", row)
    url.pDate = Constants.readDataTimeField("PDate", row)
    return url


  # #get URL from URL db
  #
  # @param urlFetch instance of URLFetch object
  # @param queryCallback function for queries execution
  # @return list of URL object
  def getURLFromURLTable(self, urlFetch, globalLen, queryCallback):
    urls = []

    for siteId in urlFetch.sitesList:
      # Update site TcDate to push rotate sites list
      if urlFetch.siteUpdate is not None:
        urlFetch.siteUpdate.id = siteId
        self.siteUpdateTask.process(urlFetch.siteUpdate, queryCallback)
        logger.debug("Site %s updated", str(siteId))

      tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
      # Make criterion
      additionQueryStr = self.generateCriterionSQL(urlFetch.urlsCriterions, None, siteId)
      # Execute additional SQLs for criterion
      if urlFetch.CRITERION_SQL in urlFetch.urlsCriterions and len(urlFetch.urlsCriterions[urlFetch.CRITERION_SQL]) > 0:
        additionalSQLs = self.execAdditionalSQLs(urlFetch.urlsCriterions[urlFetch.CRITERION_SQL], siteId, queryCallback)
      else:
        additionalSQLs = {}
      # Substitute values from additional SQLs results in criterion
      for sql in additionalSQLs:
        additionQueryStr = additionQueryStr.replace("%" + sql + "%", additionalSQLs[sql])
      # Finally add criterion to query
      query = Constants.SELECT_SQL_TEMPLATE_SIMPLE % ("*", tableName)
      if len(additionQueryStr) > 0:
        query += " "
        query += additionQueryStr

      logger.debug('>>> getURLFromURLTable UrlFetchQuery: ' + str(query))
      # Execute query
      res = queryCallback(query, Constants.SECONDARY_DB_ID, Constants.EXEC_NAME)

      if not hasattr(res, '__iter__'):
        res = []

      logger.debug('>>> getURLFromURLTable len(res): ' + str(len(res)))

      # Add urlList truncating
      # res = self.limitsURLs(siteId, res, queryCallback):
      if self.quantMaxUrls > 0 and len(res) == self.quantMaxUrls:
        self.localSiteList.append(siteId)

      for row in res:
        if urlFetch.maxURLs is not None and urlFetch.maxURLs != 0 and urlFetch.maxURLs == globalLen:
          break
        if "Site_Id" in row and "URL" in row:
          urls.append(URLFetchTask.fillUrlObj(row))
          globalLen += 1
      if urlFetch.maxURLs is not None and urlFetch.maxURLs != 0 and urlFetch.maxURLs == globalLen:
        break

    logger.debug("Return urlsFetch count = %s", str(len(urls)))
    return urls


  # #get URL from URL db
  #
  # @param urlFetch instance of URLFetch object
  # @param queryCallback function for queries execution
  # @return list of URL object
  def execAdditionalSQLs(self, sqls, siteId, queryCallback):
    ret = {}
    for key in sqls:
      q = sqls[key].replace("%" + Constants.SITE_ID_NAME + "%", str(siteId))
      r = queryCallback(q, Constants.PRIMARY_DB_ID)
      if hasattr(r, '__iter__') and len(r) > 0 and r[0][0] != None:
        ret[key] = r[0][0]
      else:
        ret[key] = "NULL"

    logger.debug("Additional SQLs: %s", str(ret))

    return ret
