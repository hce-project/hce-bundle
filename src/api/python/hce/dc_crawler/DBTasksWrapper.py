'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dc_db.TasksManager import TasksManager as DBTasksManager
from dc_db.FieldRecalculator import FieldRecalculator as DBFieldRecalculator
import dc.Constants
import dc.EventObjects
import dbi.EventObjects
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


# #class DBTasksWrapper - wrapper for common db-task operations
#
# This object is a run at once application
class DBTasksWrapper(object):


  # #DBTasksWrapper's constructor
  #
  # cfgParser param - initialization config
  def __init__(self, cfgParser):
    self.dbTask = DBTasksManager(cfgParser)
    self.fieldRecalculator = DBFieldRecalculator()
    self.rid = 0
    self.affect_db = True


  # #simple Wrapper for dbTask.process method
  #
  def process(self, drceObject):
    return self.dbTask.process(drceObject)


  # #Recalculates common fields
  #
  def fieldsRecalculating(self, sites):
    if self.affect_db:
      fieldRecalculatingObjList = []
      for site in sites:
        fieldRecalculatingObjList.append(dc.EventObjects.FieldRecalculatorObj(site))
      drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.FIELD_RECALCULATE,
                                                   fieldRecalculatingObjList)
      retDRCE = self.dbTask.process(drceObject)
      del retDRCE


  # #Recalculates common fields
  #
  def collectedURLsRecalculating(self, siteId):
    if self.affect_db:
      self.fieldRecalculator.updateCollectedURLs(siteId, self.dbTask.executeQuery)


  # #customRequest wrapper for dbTask.SQLCustom task
  #
  # @param query - custom query string or list of queries
  # @param dbName - db name
  # @return sql response or None
  def customRequest(self, query, dbName, includeFieldsNames=dbi.EventObjects.CustomRequest.SQL_BY_INDEX):
    ret = None
    if self.affect_db:
      customObject = dbi.EventObjects.CustomRequest(self.rid, query, dbName)
      customObject.includeFieldsNames = includeFieldsNames
      drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.SQL_CUSTOM, customObject)
      retDRCE = self.dbTask.process(drceObject)
      if retDRCE.eventType == dc.Constants.EVENT_TYPES.SQL_CUSTOM_RESPONSE:
        if retDRCE.eventObject.rid == self.rid:
          if retDRCE.eventObject.errString is None:
            ret = retDRCE.eventObject.result
          else:
            logger.error("SQL_CUSTOM_RESPONSE >>> Resonse error = " + retDRCE.eventObject.errString)
        else:
          logger.error("SQL_CUSTOM_RESPONSE >>> Wrong response rid")
      else:
        logger.error("SQL_CUSTOM_RESPONSE >>> Wrong response type")
    return ret


  def urlUpdate(self, urlUpdateObject, criterionsWere=None, criterionsLimit=None, criterionsOrder=None):
    ret = 0
    if self.affect_db:
      if isinstance(urlUpdateObject, list):
        urlUpdateObjectList = urlUpdateObject
      else:
        urlUpdateObjectList = [urlUpdateObject]
        if criterionsWere is not None or criterionsLimit is not None or criterionsOrder is not None:
          urlUpdateObject.criterions = {}
        if criterionsWere is not None:
          urlUpdateObject.criterions[dc.EventObjects.URLFetch.CRITERION_WHERE] = criterionsWere
        if criterionsLimit is not None:
          urlUpdateObject.criterions[dc.EventObjects.URLFetch.CRITERION_LIMIT] = criterionsLimit
        if criterionsOrder is not None:
          urlUpdateObject.criterions[dc.EventObjects.URLFetch.CRITERION_ORDER] = criterionsOrder

      drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.URL_UPDATE, urlUpdateObjectList)
      retDRCE = self.dbTask.process(drceObject)
      if retDRCE.eventType == dc.Constants.EVENT_TYPES.URL_UPDATE_RESPONSE:
        if hasattr(retDRCE.eventObject.statuses, '__iter__') and len(retDRCE.eventObject.statuses) > 0 and \
        retDRCE.eventObject.statuses[0] is False:
          logger.error("URL_UPDATE_RESPONSE >>> Operation failure, look db-task log")
        ret = len([i for i in retDRCE.eventObject.statuses if i])
      else:
        logger.error("URL_UPDATE_RESPONSE >>> Wrong response type")
    return ret


  def urlStatus(self, urlStatusObject, useMd5Resolving=False):
    ret = []
    if self.affect_db:
      if useMd5Resolving:
        urlStatusObject.urlType = dc.EventObjects.URLStatus.URL_TYPE_MD5
      drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.URL_STATUS, [urlStatusObject])
      retDRCE = self.dbTask.process(drceObject)
      if retDRCE.eventType == dc.Constants.EVENT_TYPES.URL_STATUS_RESPONSE:
        ret = retDRCE.eventObject
      else:
        logger.error("URL_STATUS_RESPONSE >>> Wrong response type")
    return ret


  def urlContent(self, items):
    ret = None
    drceSyncTasksCoverObj = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.URL_CONTENT, items)
    retDRCE = self.dbTask.process(drceSyncTasksCoverObj)
    if retDRCE.eventType == dc.Constants.EVENT_TYPES.URL_CONTENT_RESPONSE:
      ret = retDRCE.eventObject
    else:
      logger.error("URL_CONTENT_RESPONSE >>> Wrong response type")
    return ret


  def putURLContent(self, urlPut_list):
    ret = None

    drceSyncTasksCoverObj = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.URL_PUT, urlPut_list)
    responseDRCESyncTasksCover = self.dbTask.process(drceSyncTasksCoverObj)
    if responseDRCESyncTasksCover.eventType == dc.Constants.EVENT_TYPES.URL_PUT_RESPONSE:
      for obj in responseDRCESyncTasksCover.eventObject:
        logger.debug("URL_PUT_RESPONSE: %s", varDump(obj))
    else:
      logger.error("URL_PUT_RESPONSE >>> Wrong response type")

    if responseDRCESyncTasksCover.eventType != dc.Constants.EVENT_TYPES.URL_PUT_RESPONSE:
      logger.error("URL_PUT_RESPONSE >>> Wrong response type")

    return ret


  def urlNew(self, urlNewObject):
    ret = 0
    if self.affect_db:
      if isinstance(urlNewObject, list):
        urlNewList = urlNewObject
      else:
        urlNewList = [urlNewObject]
      drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.URL_NEW, urlNewList)
      retDRCE = self.dbTask.process(drceObject)
      if retDRCE.eventType == dc.Constants.EVENT_TYPES.URL_NEW_RESPONSE:
        ret = len([i for i in retDRCE.eventObject.statuses if i == 0])
      else:
        logger.error("URL_NEW_RESPONSE >>> Wrong response type")
    return ret


  def siteNewOrUpdate(self, siteObject, properties=None, filters=None, siteId=None, stype=dc.EventObjects.SiteUpdate):
    ret = []
    if self.affect_db:
      if stype == dc.EventObjects.Site:
        reqType = dc.Constants.EVENT_TYPES.SITE_NEW
        respType = dc.Constants.EVENT_TYPES.SITE_NEW_RESPONSE
      elif stype == dc.EventObjects.SiteUpdate:
        reqType = dc.Constants.EVENT_TYPES.SITE_UPDATE
        respType = dc.Constants.EVENT_TYPES.SITE_UPDATE_RESPONSE
      if siteObject is None:
        if siteId is not None:
          siteObject = stype(siteId)
          if properties is not None:
            siteObject.properties = properties
          if filters is not None:
            siteObject.filters = filters
      if siteObject is not None:
        drceObject = dc.Constants.DRCESyncTasksCover(reqType, siteObject)
        retDRCE = self.dbTask.process(drceObject)
        logger.debug("SITE_NEW_UPDATE_RESPONSE  retDRCE: " + varDump(retDRCE))
        if retDRCE.eventType == respType:
          ret = retDRCE.eventObject.statuses
        else:
          logger.error("SITE_NEW_UPDATE_RESPONSE >>> Wrong response type")
      else:
        logger.error("SITE_NEW_UPDATE >>> siteObject is None!")
    return ret


  def siteStatus(self, siteStatusObject):
    ret = None
    if self.affect_db:
      if siteStatusObject is not None:
        drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.SITE_STATUS, siteStatusObject)
        retDRCE = self.dbTask.process(drceObject)
        if retDRCE.eventType == dc.Constants.EVENT_TYPES.SITE_STATUS_RESPONSE:
          ret = retDRCE.eventObject
        else:
          logger.error("SITE_STATUS_RESPONSE >>> Wrong response type")
      else:
        logger.error("SITE_STATUS >>> Not enough incoming data")
    return ret


  # # Proxy status operation
  #
  # @param proxyStatusObject - proxy object
  # @return result response
  def proxyStatus(self, proxyStatusObject):
    # variable for result
    ret = None
    if self.affect_db:
      if proxyStatusObject is None:
        logger.error("PROXY_STATUS: proxyObject is None!")
      else:
        if isinstance(proxyStatusObject, list):
          proxyStatusObjectList = proxyStatusObject
        else:
          proxyStatusObjectList = [proxyStatusObject]

        drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.PROXY_STATUS, proxyStatusObjectList)
        retDRCE = self.dbTask.process(drceObject)
        if retDRCE.eventType == dc.Constants.EVENT_TYPES.PROXY_STATUS_RESPONSE:
          ret = retDRCE.eventObject
        else:
          logger.error("PROXY_STATUS_RESPONSE: Wrong type of response object!")

    return ret


  # # Proxy update operation
  #
  # @param proxyUpdateObject - proxy update object
  # @return result response
  def proxyUpdate(self, proxyUpdateObject):
    # variable for result
    ret = None
    if self.affect_db:
      if proxyUpdateObject is not None:
        if isinstance(proxyUpdateObject, list):
          proxyUpdateObjectList = proxyUpdateObject
        else:
          proxyUpdateObjectList = [proxyUpdateObject]

        drceObject = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.PROXY_UPDATE, proxyUpdateObjectList)
        retDRCE = self.dbTask.process(drceObject)
        if retDRCE.eventType == dc.Constants.EVENT_TYPES.PROXY_UPDATE_RESPONSE:
          ret = retDRCE.eventObject
        else:
          logger.error("PROXY_UPDATE_RESPONSE >>> Wrong response type")
      else:
        logger.error("PROXY_UPDATE >>> Not enough incoming data")

    return ret


  # # put attributes operation
  #
  # @param attributesList - attributes list
  # @return - None
  def putAttributes(self, attributes):

    attributesList = attributes if isinstance(attributes, list) else [attributes]

    drceSyncTasksCoverObj = dc.Constants.DRCESyncTasksCover(dc.Constants.EVENT_TYPES.ATTR_SET, attributesList)
    responseDRCESyncTasksCover = self.dbTask.process(drceSyncTasksCoverObj)
    if responseDRCESyncTasksCover.eventType != dc.Constants.EVENT_TYPES.ATTR_SET_RESPONSE:
      logger.error("Operation 'ATTR_SET' has error: Wrong response type")
