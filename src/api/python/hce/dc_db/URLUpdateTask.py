'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dtm.EventObjects import GeneralResponse
import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
from dc_db.StatisticLogManager import StatisticLogManager
from dc_db.URLPutTask import URLPutTask
from dc_db.AttrUpdateTask import AttrUpdateTask
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process urlUpdate event
class URLUpdateTask(BaseTask):

  # #constructor
  #
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLUpdateTask, self).__init__()
    self.urlPutTask = URLPutTask(keyValueStorageDir, rawDataDir, dBDataTask)


  # #make all necessary actions to get update urls data in db
  #
  # @param urlUpdates list of URLUpdate objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, urlUpdates, queryCallback):
    ret = GeneralResponse()
    status = False
    for urlUpdate in urlUpdates:
      status = False
      if urlUpdate.siteId == "":
        urlUpdate.siteId = "0"
      if not hasattr(urlUpdate, "urlMd5"):
        urlUpdate.fillMD5(urlUpdate.url, urlUpdate.type)
      if self.isSiteExist(urlUpdate.siteId, queryCallback):
        self.statisticUpdate(urlUpdate, queryCallback)
        status = self.updateURL(urlUpdate, queryCallback)
        if status and urlUpdate.attributes is not None and len(urlUpdate.attributes) > 0:
          self.attributesUpdate(urlUpdate.attributes, queryCallback)
      ret.statuses.append(status)
      if "urlPut" in urlUpdate.__dict__ and urlUpdate.urlPut is not None:
        self.urlPutOperation(urlUpdate, urlUpdate.urlPut, queryCallback)
    return ret


  # #update records in statistic and log db
  #
  # @param urlUpdate instance of URLUpdate object
  # @param queryCallback function for queries execution
  def statisticUpdate(self, urlUpdate, queryCallback):
    prevStatus = None
    SQL_SELECT_STATUS_TEMPLATE = "SELECT `Status` FROM `%s` WHERE `URLMD5` = '%s'"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlUpdate.siteId
    query = SQL_SELECT_STATUS_TEMPLATE % (tableName, urlUpdate.urlMd5)
    ret = queryCallback(query, Constants.SECONDARY_DB_ID)
    if ret is not None and len(ret) > 0 and len(ret[0]) > 0 and ret[0][0] is not None:
      prevStatus = int(ret[0][0])
    StatisticLogManager.statisticUpdate(queryCallback, Constants.StatFreqConstants.FREQ_UPDATE, 1,
                                        urlUpdate.siteId, urlUpdate.urlMd5)
    StatisticLogManager.logUpdate(queryCallback, "LOG_UPDATE", urlUpdate, urlUpdate.siteId, urlUpdate.urlMd5)
    if prevStatus is None or prevStatus != urlUpdate.status:
      self.statisticLogUpdate(urlUpdate, urlUpdate.urlMd5, urlUpdate.siteId, urlUpdate.status, queryCallback)


  # #update url in db
  #
  # @param urlUpdate instance of URLUpdate object
  # @param queryCallback function for queries execution
  def updateURL(self, urlUpdate, queryCallback):
    ret = False
    SQL_UPDATE_URLSITE_TEMPLATE = "UPDATE IGNORE `%s` SET %s"
    if urlUpdate.eTag is not None:
      urlUpdate.eTag = urlUpdate.eTag.strip("\"'")
    fields, values = Constants.getFieldsValuesTuple(urlUpdate, Constants.URLTableDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values, Constants.urlExcludeList)
    if fieldValueString and len(fieldValueString) > 0:
      tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlUpdate.siteId
      query = SQL_UPDATE_URLSITE_TEMPLATE % (tableName, fieldValueString)
      additionWhere = None
      if urlUpdate.urlMd5 is not None:
        additionWhere = ("`URLMD5` = '%s'" % urlUpdate.urlMd5)
      additionQueryStr = self.generateCriterionSQL(urlUpdate.criterions, additionWhere)
      if len(additionQueryStr) > 0:
        query += " "
        query += additionQueryStr
      queryCallback(query, Constants.SECONDARY_DB_ID)
      ret = True
    return ret


  # #makes URLPutTask operation
  #
  # @param urlObject instance of URL or URLUpdate object
  # @param urlPutObject instance of URLPut object
  # @param queryCallback function for queries execution
  def urlPutOperation(self, urlObject, urlPutObject, queryCallback):
    if urlPutObject.siteId is None and urlObject.siteId is not None:
      urlPutObject.siteId = urlObject.siteId
      logger.debug(">>> URLPut.siteId is None and set to the = " + urlPutObject.siteId)
    if urlPutObject.urlMd5 is None and urlObject.urlMd5 is not None:
      urlPutObject.urlMd5 = urlObject.urlMd5
      logger.debug(">>> URLPut.urlMd5 is None and set to the = " + urlPutObject.urlMd5)
    logger.debug(">>> Call internal URLPut")
    self.urlPutTask.process([urlPutObject], queryCallback)


  # #updatesAttributes
  #
  # @param attributes list of AttributeUpdate objects
  # @param queryCallback function for queries execution
  def attributesUpdate(self, attributes, queryCallback):
    logger.debug(">>> URLUpdateTask.attributesUpdate (len) = " + str(len(attributes)))
    attrUpdateTask = AttrUpdateTask()
    res = attrUpdateTask.process(attributes, queryCallback)
    logger.debug(">>> URLUpdateTask.attributesUpdate (res) == " + str(res))
