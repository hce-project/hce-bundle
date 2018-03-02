'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
from dc_db.URLDeleteTask import URLDeleteTask
from dc_db.StatisticLogManager import StatisticLogManager
import dc.EventObjects
from dtm.EventObjects import GeneralResponse
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process URLAgeTask event
class URLAgeTask(BaseTask):


  # #constructor
  #
  # @param keyValueStorageDir path to keyValue storage work dir
  # @param rawDataDir path to raw data dir
  def __init__(self, keyValueStorageDir, rawDataDir, backDBResolve):
    super(URLAgeTask, self).__init__()
    self.uRLDeleteTask = URLDeleteTask(keyValueStorageDir, rawDataDir, backDBResolve)
    self.urlsSelectDict = {}
    self.gloablLoopExit = False
    self.curUrlsCount = 0


  # #makes real UrlDelte operation
  #
  # @param queryCallback - sql execute callback function
  def urlDeleteOperation(self, queryCallback):
    urlsDeleteObjs = []
    localUrlDelete = None
    for siteId in self.urlsSelectDict:
      for urlMd5 in self.urlsSelectDict[siteId]:
        localUrlDelete = dc.EventObjects.URLDelete(siteId, urlMd5, reason=dc.EventObjects.URLDelete.REASON_AGING)
        localUrlDelete.urlType = dc.EventObjects.URLStatus.URL_TYPE_MD5
        localUrlDelete.delayedType = self.urlsSelectDict[siteId][urlMd5]
        urlsDeleteObjs.append(localUrlDelete)
        StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_AGED_STATE, 1,
                                            siteId, urlMd5)
    if len(urlsDeleteObjs) > 0:
      logger.debug(">>> URLAge started URLDelete count = " + str(len(urlsDeleteObjs)))
      self.uRLDeleteTask.process(urlsDeleteObjs, queryCallback)


  # #addElemInLocalDict added new element in localDict, checks limits
  #
  # @param siteId - site'd Id
  # @param UrlMd5 -url's Md5
  # @return urlLimit -global urls limit
  # @return delayedType - delayed type (using in URLDelete operation)
  def addElemInLocalDict(self, siteId, UrlMd5, urlLimit, delayedType):
    if siteId not in self.urlsSelectDict:
      self.urlsSelectDict[siteId] = {}
    if UrlMd5 in self.urlsSelectDict[siteId]:
      logger.debug(">>> " + siteId + "." + UrlMd5 + " Already selected")
    else:
      if self.curUrlsCount < urlLimit:
        self.urlsSelectDict[siteId][UrlMd5] = delayedType
        logger.debug(">>> " + siteId + "." + UrlMd5 + " Added")
        self.curUrlsCount += 1
      else:
        logger.debug(">>> UrlLimit reached = " + str(urlLimit))


  # #make all necessary actions to aging urls data from db
  #
  # @param urlDelete list of URLDelete objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, urlAges, queryCallback):
    self.curUrlsCount = 0
    generalResponse = GeneralResponse()
    self.urlsSelectDict = {}
    URL_SELECT_TEMPL = "SELECT `UrlMd5` FROM %s"
    for urlAge in urlAges:
      defaultUrlsCriterions = urlAge.urlsCriterions[dc.EventObjects.URLAge.CRITERION_WHERE]
      if self.gloablLoopExit:
        break
      query = "SELECT `Id` FROM `sites`"
      sitesCriterionStr = self.generateCriterionSQL(urlAge.sitesCriterions)
      if len(sitesCriterionStr) > 0:
        query += " " + sitesCriterionStr
      sitesRes = queryCallback(query, Constants.PRIMARY_DB_ID)
      if sitesRes is not None:
        for sitesElem in sitesRes:
          if self.gloablLoopExit:
            break
          if sitesElem is not None and len(sitesElem) > 0:
            # StatisticLogManager.logUpdate(queryCallback, "LOG_URL_AGING", urlAge, sitesElem[0], "")
            # Get the alternate URLs select criterion from the sites_properties table
            queryAltURLsCrit = \
              "SELECT `Value` FROM `sites_properties` WHERE `Site_Id`='%s' AND `Name`='AGING_URL_CRITERION' LIMIT 1"\
              % sitesElem[0]
            altURLsCritRes = queryCallback(queryAltURLsCrit, Constants.PRIMARY_DB_ID)
            criterionsSubstituted = False
            if altURLsCritRes is not None:
              for altURLsCritItem in altURLsCritRes:
                if altURLsCritItem is not None and len(altURLsCritItem) > 0:
                  # Overwrite criterion WHERE with value from dc_sites.sites_properties
                  urlAge.urlsCriterions[dc.EventObjects.URLAge.CRITERION_WHERE] = altURLsCritItem[0]
                  criterionsSubstituted = True
            if not criterionsSubstituted:
              urlAge.urlsCriterions[dc.EventObjects.URLAge.CRITERION_WHERE] = defaultUrlsCriterions
            # Make criterion for URLs select
            tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % sitesElem[0]
            query = URL_SELECT_TEMPL % tableName
            urlsCriterionStr = self.generateCriterionSQL(urlAge.urlsCriterions, None, sitesElem[0])
            if len(urlsCriterionStr) > 0:
              query += " " + urlsCriterionStr
            # Select URLs
            urlsRes = queryCallback(query, Constants.SECONDARY_DB_ID)
            for urlsRes in urlsRes:
              if self.gloablLoopExit:
                break
              if urlsRes is not None and len(urlsRes) > 0:
                self.addElemInLocalDict(sitesElem[0], urlsRes[0], urlAge.maxURLs, urlAge.delayedType)
                StatisticLogManager.logUpdate(queryCallback, "LOG_URL_AGING", urlAge, sitesElem[0], urlsRes[0])
    if len(self.urlsSelectDict) > 0:
      self.urlDeleteOperation(queryCallback)
    return generalResponse
