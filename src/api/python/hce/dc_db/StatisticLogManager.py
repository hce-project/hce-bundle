'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc_db.Constants as Constants
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #StatisticLogManager central point of Statistics and Log databases update
#
class StatisticLogManager(object):

  SITE_PROP_NAME_FREQ = "STATS_FREQ_ENABLED"
  SITE_PROP_NAME_LOG = "STATS_LOG_ENABLED"
  GLOBAL_FREQ_ENABLED = False
  GLOBAL_LOG_ENABLED = False


  # #isStatisticEnabled return bool value - is freq or log static enabled (for site)
  #
  # @param queryCallback - sql callback function
  # @param siteId - site's id
  @staticmethod
  def isStatisticEnabled(queryCallback, siteId, defValue, propName):
    from dc_db.BaseTask import BaseTask
    ret = defValue
    tempValue = BaseTask.readValueFromSiteProp(siteId, propName, queryCallback)
    if tempValue is not None:
      ret = bool(int(tempValue))
    return ret


  # #statisticUpdate updates statistic database fileds
  #
  # @param queryCallback - sql callback function
  # @param siteId - site's id
  # @param URLMd5 - url's MD5
  @staticmethod
  def addNewRecord(queryCallback, siteId, URLMd5):
    if queryCallback is not None:
      SQL_INSERT_TEMPLAE = "INSERT IGNORE INTO `%s` SET `URLMd5`= '%s'"
      if StatisticLogManager.isStatisticEnabled(queryCallback, siteId, StatisticLogManager.GLOBAL_FREQ_ENABLED,
                                                StatisticLogManager.SITE_PROP_NAME_FREQ):
        tbName = Constants.DC_FREQ_TABLE_NAME_TEMPLATE % siteId
        query = SQL_INSERT_TEMPLAE % (tbName, URLMd5)
        queryCallback(query, Constants.STAT_DB_ID)
      else:
        logger.debug(">>> Statistic Freq Disabled, SiteId=" + siteId)
    else:
      logger.error(">>> addNewRecord error, queryCallback is None")


  # #statisticUpdate updates statistic database fileds
  #
  # @param queryCallback - sql callback function
  # @param freqName - name of updates field (look dc_db.Constants.StatFreqConstants class)
  # @param addValue - integer value for addition
  # @param siteId - site's id
  # @param URLMd5 - url's MD5
  @staticmethod
  def statisticUpdate(queryCallback, freqName, addValue, siteId, URLMd5):
    if StatisticLogManager.isStatisticEnabled(queryCallback, siteId, StatisticLogManager.GLOBAL_FREQ_ENABLED,
                                              StatisticLogManager.SITE_PROP_NAME_FREQ):
      if queryCallback is not None:
        if freqName in Constants.StatFreqConstants.__dict__.values():
          FREQ_UPDATE_SQL_TEMPLATE = "UPDATE `%s` SET `%s`=`%s`+%s, `MDate`=NOW() WHERE `URLMd5`='%s'"
          tbName = Constants.DC_FREQ_TABLE_NAME_TEMPLATE % siteId
          query = FREQ_UPDATE_SQL_TEMPLATE % (tbName, freqName, freqName, str(addValue), URLMd5)
          queryCallback(query, Constants.STAT_DB_ID)
        else:
          logger.error(">>> statisticUpdate error = " + str(freqName) + " Statistic Freq field not support !")
      else:
        logger.error(">>> statisticUpdate error, queryCallback is None")
    else:
      logger.debug(">>> Statistic Freq Disabled, SiteId=" + siteId)


  # #logUpdate updates log database fileds
  #
  # @param queryCallback - sql callback function
  # @param opName - type of operation (look dc_db.Constants.logOperationsDict dict)
  # @param logObject - current logging object (may be None)
  # @param siteId - site's id
  # @param URLMd5 - url's MD5
  # @param opDate - operation's data
  @staticmethod
  def logUpdate(queryCallback, opName, logObject, siteId, URLMd5, opDate="NOW()"):
    if StatisticLogManager.isStatisticEnabled(queryCallback, siteId, StatisticLogManager.GLOBAL_LOG_ENABLED,
                                              StatisticLogManager.SITE_PROP_NAME_LOG):
      if queryCallback is not None:
        if opName in Constants.logOperationsDict:
          LOG_INSERT_SQL_TEMPLATE = "INSERT INTO `%s` SET `URLMd5`='%s', `OpCode`=%s, `Object`='%s', `ODate`=%s"
          tbName = Constants.DC_LOG_TABLE_NAME_TEMPLATE % siteId
          objectStr = ""
          if logObject is not None:
            try:
              objectStr = logObject.toJSON()
#               objectStr = MySQLdb.escape_string(objectStr)
              objectStr = Utils.escape(objectStr)
            except Exception as ex:
              logger.debug(">>> logUpdate Object to JSON error = " + str(ex))
          if opDate != "NOW()":
            opDate = ("'" + opDate + "'")
          query = LOG_INSERT_SQL_TEMPLATE % (tbName, URLMd5, str(Constants.logOperationsDict[opName]), objectStr,
                                             opDate)
          queryCallback(query, Constants.LOG_DB_ID)
        else:
          logger.error(">>> logUpdate error = " + str(opName) + " Log field not support !")
      else:
        logger.error(">>> logUpdate error, queryCallback is None")
    else:
      logger.debug(">>> Statistic Log Disabled, SiteId=" + siteId)
