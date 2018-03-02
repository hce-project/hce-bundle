'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc.EventObjects
import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
from dc_db.URLCleanupTask import URLCleanUpTask
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process URLHistoryTask task
class URLHistoryTask(BaseTask):

  SQL_LOG_TEMPLATE = "SELECT * FROM %s WHERE `URLMd5`='%s'"
  SQL_LOG_TEMPLATE_SHORT = "SELECT * FROM %s"

  # #constructor
  #
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLHistoryTask, self).__init__()
    self.uRLCleanUpTask = URLCleanUpTask(keyValueStorageDir, rawDataDir, dBDataTask)


  # #process - main class's execution point.
  #
  # @param urlHistories incoming urlHistories element (list of urlHistory)
  # @param queryCallback function for queries execution
  # @return uRLHistoryResponses element
  def process(self, urlHistories, queryCallback):
    uRLHistoryResponses = []
    for urlHistory in urlHistories:
      uRLHistoryResponse = None
      if urlHistory is not None:
        localMd5s = []
        if urlHistory.urlMd5 is None:
          if urlHistory.urlCriterions is not None:
            localMd5s = self.uRLCleanUpTask.extractUrlByCriterions(urlHistory.siteId, False,
                                                                      urlHistory.urlCriterions, queryCallback)
        else:
          localMd5s.append(urlHistory.urlMd5)
      logger.debug(">>> [URLHistoryTask] localUrls size = " + str(len(localMd5s)))
      for localMd5 in localMd5s:
        try:
          urlHistory.urlMd5 = localMd5
          res = self.fetchLogsFromDB(urlHistory, queryCallback, urlHistory.logCriterions)
          if uRLHistoryResponse is None:
            uRLHistoryResponse = dc.EventObjects.URLHistoryResponse([], urlHistory.siteId)
          if res is not None and len(res) > 0:
            uRLHistoryResponse.logRows.extend(res)
        except Exception as ex:
          logger.debug(">>> [URLHistoryTask] Some Type Exception = " + str(type(ex)) + " " + str(ex))
      uRLHistoryResponses.append(uRLHistoryResponse)
    return uRLHistoryResponses


  # #fetchLogsFromDB - method makes SQL response for fetching log data
  #
  # @param urlHistory element of urlHistory object
  # @param queryCallback function for queries execution
  # @param logCriterions addition criterion for sql request
  # @return SQL response element
  def fetchLogsFromDB(self, urlHistory, queryCallback, logCriterions=None):
    tableName = Constants.DC_LOG_TABLE_NAME_TEMPLATE % urlHistory.siteId
    if logCriterions is None:
      query = self.SQL_LOG_TEMPLATE % (tableName, urlHistory.urlMd5)
    else:
      additionWere = "`URLMd5` = '%s'"
      additionWere = (additionWere % urlHistory.urlMd5)
      query = self.SQL_LOG_TEMPLATE_SHORT % tableName
      query += self.generateCriterionSQL(logCriterions, additionWere)
    ret = queryCallback(query, Constants.LOG_DB_ID, Constants.EXEC_NAME)
    if ret is not None:
      for elem in ret:
        if "CDate" in elem:
          elem["CDate"] = str(elem["CDate"])
        if "ODate" in elem:
          elem["ODate"] = str(elem["ODate"])
    return ret
