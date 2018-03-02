'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import copy
import dc.EventObjects
import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
from dc_db.URLCleanupTask import URLCleanUpTask
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process URLHistoryTask task
class URLStatsTask(BaseTask):

  SQL_STATS_TEMPLATE = "SELECT * FROM %s WHERE `URLMd5`='%s'"

  # #constructor
  #
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLStatsTask, self).__init__()
    self.uRLCleanUpTask = URLCleanUpTask(keyValueStorageDir, rawDataDir, dBDataTask)


  # #process - main class's execution point.
  #
  # @param urlStatses incoming urlStatses element (list of urlStats)
  # @param queryCallback function for queries execution
  # @return uRLStatsResponses element
  def process(self, urlStatses, queryCallback):
    uRLStatsResponses = []
    for urlStats in urlStatses:
      uRLStatsResponse = None
      localMd5s = []
      if urlStats is not None:
        if urlStats.urlMd5 is None:
          if urlStats.urlCriterions is not None and len(urlStats.urlCriterions) > 0:
            localMd5s = self.uRLCleanUpTask.extractUrlByCriterions(urlStats.siteId, False,
                                                                   urlStats.urlCriterions, queryCallback)
          if urlStats.statsCriterions is not None:
            statsMd5s = []
            if urlStats.urlCriterions is None or len(urlStats.urlCriterions) == 0:
              statsMd5s = self.uRLCleanUpTask.extractUrlByCriterions(urlStats.siteId,
                                                                     False,
                                                                     urlStats.statsCriterions, queryCallback,
                                                                     Constants.STAT_DB_ID,
                                                                     Constants.DC_FREQ_TABLE_NAME_TEMPLATE)
            else:
              SQL_WHERE_TMPL = "`UrlMd5` = '%s'"
              statsCriterionCopy = copy.deepcopy(urlStats.statsCriterions)
              for localMd5 in localMd5s:
                urlStats.statsCriterions = copy.deepcopy(statsCriterionCopy)
                if dc.EventObjects.URLFetch.CRITERION_WHERE in urlStats.statsCriterions \
                and urlStats.statsCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] is not None:
                  urlStats.statsCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] = ' AND ' + \
                  (SQL_WHERE_TMPL % localMd5)
                else:
                  urlStats.statsCriterions[dc.EventObjects.URLFetch.CRITERION_WHERE] = (SQL_WHERE_TMPL % localMd5)
                statsMd5s += self.uRLCleanUpTask.extractUrlByCriterions(urlStats.siteId,
                                                                        False,
                                                                        urlStats.statsCriterions,
                                                                        queryCallback,
                                                                        Constants.STAT_DB_ID,
                                                                        Constants.DC_FREQ_TABLE_NAME_TEMPLATE)
            localMd5s = statsMd5s

#           '''
#           if urlStats.urlCriterions is not None:
#             urlsMd5s = self.uRLCleanUpTask.extractUrlByCriterions(urlStats.siteId, False,
#                         urlStats.urlCriterions, queryCallback)
#
#           if urlStats.statsCriterions is not None:
#             statsMd5s = self.uRLCleanUpTask.extractUrlByCriterions(urlStats.siteId, False,
#                         urlStats.statsCriterions, queryCallback, Constants.STAT_DB_ID,
#                         Constants.DC_FREQ_TABLE_NAME_TEMPLATE)
#           if len(statsMd5s) > 0 and len(urlsMd5s) > 0:
#             localMd5s = [x for x in statsMd5s if x in urlsMd5s]
#           elif len(statsMd5s) > 0:
#             localMd5s = statsMd5s
#           elif len(urlsMd5s) > 0:
#             localMd5s = urlsMd5s
#           '''
        else:
          localMd5s.append(urlStats.urlMd5)
      logger.debug(">>> [URLStatsTask] localUrls size = " + str(len(localMd5s)))
      for localMd5 in localMd5s:
        try:
          urlStats.urlMd5 = localMd5
          res = self.fetchStatsFromDB(urlStats, queryCallback)
          if uRLStatsResponse is None:
            uRLStatsResponse = dc.EventObjects.URLStatsResponse([], urlStats.siteId)
          if res is not None and len(res) > 0:
            uRLStatsResponse.freqRows.extend(res)
        except Exception as ex:
          logger.debug(">>> [URLStatsTask] Some Type Exception = " + str(type(ex)) + " " + str(ex))
      uRLStatsResponses.append(uRLStatsResponse)

    return uRLStatsResponses


  # #fetchStatsFromDB - method makes SQL response for fetching stats data
  #
  # @param urlStats element of URLStats object
  # @param queryCallback function for queries execution
  # @return SQL response element
  def fetchStatsFromDB(self, urlStats, queryCallback):
    tableName = Constants.DC_FREQ_TABLE_NAME_TEMPLATE % urlStats.siteId
    query = self.SQL_STATS_TEMPLATE % (tableName, urlStats.urlMd5)
    ret = queryCallback(query, Constants.STAT_DB_ID, Constants.EXEC_NAME)
    if ret is not None:
      for elem in ret:
        if "CDate" in elem:
          elem["CDate"] = str(elem["CDate"])
        if "MDate" in elem:
          elem["MDate"] = str(elem["MDate"])
    return ret
