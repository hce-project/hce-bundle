'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import hashlib
import copy
import MySQLdb
from dateutil.parser import parse
import dc.EventObjects
import app.SQLCriterions
import app.Utils as Utils  # pylint: disable=F0401
from app.Utils import SQLExpression
from dtm.EventObjects import GeneralResponse
from dc_db.BaseTask import BaseTask
from dc_db.Constants import DC_URLS_TABLE_NAME_TEMPLATE
import dc_db.Constants as Constants
from dc_db.StatisticLogManager import StatisticLogManager
from dc_db.SiteDeleteTask import SiteDeleteTask

logger = Utils.MPLogger().getLogger()


# @todo move to apropriate place

class SiteTask(BaseTask):

  FIELD_NAME_URLS = "urls"
  FIELD_NAME_PROPERTIES = "properties"
  FIELD_NAME_FILTERS = "filters"


  # #constructor
  #
  # @param dcSiteTemplate path to sql template for dc_urls_* tables
  def __init__(self, dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir, dBDataTask, dcStatTemplates,
               dcLogTemplate, dcAttrTemplate, tasksManager=None):
    super(SiteTask, self).__init__()
    self.dcSiteTemplate = dcSiteTemplate
    self.keyValueDefaultFile = keyValueDefaultFile
    self.keyValueStorageDir = keyValueStorageDir
    self.dBDataTask = dBDataTask
    self.dcStatTemplates = dcStatTemplates
    self.dcLogTemplate = dcLogTemplate
    self.dcAttrTemplate = dcAttrTemplate
    if self.dBDataTask is not None:
      self.siteDeleteTask = SiteDeleteTask(keyValueStorageDir, self.dBDataTask.rawDataDir, dBDataTask)
    else:
      self.siteDeleteTask = None
    self.tasksManager = tasksManager


  # #make all necessary actions to add new site into mysql db
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, site, queryCallback):
    response = GeneralResponse()
    # if not self.isSiteExist(site.urls[0], queryCallback):
    if not self.isSiteExist(site.id, queryCallback, site.userId):
      self.addSite(site, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.addSitesFilter(site, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.addSiteProperties(site, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.createTableFromTemplate(site, self.dcSiteTemplate, Constants.SECONDARY_DB_ID, queryCallback)
      # Create the same structure as for urls_<site_id> but without an unique key
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.createTableFromTemplate(site, self.dcSiteTemplate, Constants.FOURTH_DB_ID, queryCallback,
                                     {'PRIMARY KEY':'KEY'})
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.createTableFromTemplate(site, self.dcStatTemplates, Constants.STAT_DB_ID, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.createTableFromTemplate(site, self.dcLogTemplate, Constants.LOG_DB_ID, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.createTableFromTemplate(site, self.dcAttrTemplate, Constants.ATT_DB_ID, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.addSiteURLSites(site, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        if site.moveURLs:
          self.addSiteURLURLs(site, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        self.addSiteInKVDB(site, queryCallback)
      if self.tasksManager is None or self.tasksManager.SQLErrorCode == Constants.EXIT_CODE_OK:
        response.statuses.append(site.id)
      else:
        logger.debug(">>> Was some sql error while SITE_NEW operation start SiteDelete/rollback")
        self.siteDelete(site, queryCallback)
        response = GeneralResponse(Constants.TASK_SQL_ERR, Constants.TASK_SQL_ERR_MSG)
        response.statuses.append(None)
    else:
      response = GeneralResponse(Constants.TASK_DUPLICATE_ERR, Constants.TASK_DUPLICATE_ERR_MSG)
      response.statuses.append(None)

    return response


  # # add data in sites table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSite(self, site, queryCallback):
    fields, values = Constants.getFieldsValuesTuple(site, Constants.siteDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values)
    if len(fieldValueString) > 0:
      query = Constants.INSERT_COMMON_TEMPLATE % ("sites", fieldValueString)
      queryCallback(query, Constants.PRIMARY_DB_ID)
    else:
      pass


  # # add data in sites_filters table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSitesFilter(self, site, queryCallback):
    if site.filters is not None:
      for localFilter in site.filters:
        if localFilter is not None:
          localUDate = "NULL"
          if localFilter.uDate is not None:
            localUDate = str(localFilter.uDate)
          query = (Constants.SITE_FILTER_SQL_TEMPLATE %
                   (Utils.escape(str(localFilter.siteId)), Utils.escape(str(localFilter.pattern)),
                    Utils.escape(str(localFilter.subject)), str(localFilter.opCode),
                    str(localFilter.stage), str(localFilter.action), localUDate, str(localFilter.type),
                    str(localFilter.mode), str(localFilter.state), str(localFilter.groupId)))
          queryCallback(query, Constants.PRIMARY_DB_ID)



  # # update data in sites_filters table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def updateSitesFilter(self, site, queryCallback):
    if site.filters is not None:
      for localFilter in site.filters:
        if localFilter is not None:
          localUDate = "`UDate`"
          if localFilter.uDate is not None:
            localUDate = "'" + str(localFilter.uDate) + "'"
          query = (Constants.SITE_FILTER_SQL_UPDATE %
                   (Utils.escape(str(localFilter.pattern)), Utils.escape(str(localFilter.subject)),
                    str(localFilter.opCode), str(localFilter.stage),
                    str(localFilter.action), localUDate, str(localFilter.groupId),
                    Utils.escape(str(localFilter.siteId)),
                    str(localFilter.type), str(localFilter.mode), str(localFilter.state)))
          queryCallback(query, Constants.PRIMARY_DB_ID)


  # # creates site properties dict
  #
  # @field - incoming site properties field
  # @site - incomig site
  # @return created site properties dict
  def createPropDict(self, field, site):
    localDict = {}
    if isinstance(site.properties, dict):
      if isinstance(site.properties[field], list):
        if site.properties[field][0] is not None:
          localDict["siteId"] = str(site.properties[field][0])
        else:
          localDict["siteId"] = site.id
        localDict["name"] = str(field)
        if site.properties[field][1] is not None:
          localDict["value"] = str(site.properties[field][1])
        if site.properties[field][2] is not None:
          localDict["urlMd5"] = str(site.properties[field][2])
      else:
        localDict["siteId"] = site.id
        localDict["name"] = str(field)
        localDict["value"] = str(site.properties[field])
    elif isinstance(site.properties, list) and isinstance(field, dict):
      localDict = field

    if "uDate" in localDict and localDict["uDate"] is not None:
      if self.isIsoFormatDate(localDict["uDate"]):
        logger.debug("!!! localDict[\"uDate\"] has ISO format datetime: " + str(localDict["uDate"]))
        localDict["uDate"] = "'" + str(localDict["uDate"]) + "'"
      else:
        logger.debug("!!! localDict[\"uDate\"] has not ISO format datetime: " + str(localDict["uDate"]))
        localDict["uDate"] = SQLExpression(localDict["uDate"])

    if "cDate" in localDict and localDict["cDate"] is not None:
      if self.isIsoFormatDate(localDict["cDate"]):
        logger.debug("!!! localDict[\"cDate\"] has ISO format datetime: " + str(localDict["cDate"]))
        localDict["cDate"] = "'" + str(localDict["cDate"]) + "'"
      else:
        logger.debug("!!! localDict[\"cDate\"] has not ISO format datetime: " + str(localDict["cDate"]))
        localDict["cDate"] = SQLExpression(localDict["cDate"])

    return localDict


  # # Check format date value
  #
  # @param dateValue - incoming datetime value
  # @return True - if it string content right datetime in iso format, othrwise False
  def isIsoFormatDate(self, dateValue):
    # value for result
    ret = False
    if isinstance(dateValue, basestring):
      try:
        parse(dateValue)
        ret = True
      except Exception, err:
        logger.debug("value '" + str(dateValue) + "' has not ISO format, try parse error: " + str(err))

    return ret


  # # add data in sites_properties table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSiteProperties(self, site, queryCallback):
    if site.properties is not None:
      localDict = {}
      query = None
      for field in site.properties:
        if field is not None:
          query = None
          localDict = self.createPropDict(field, site)
          fields, values = Constants.getFieldsValuesTuple(localDict, Constants.propDict)
          if len(fields) > 0 and len(fields) == len(values):
            fieldValueString = Constants.createFieldsValuesString(fields, values)
            query = Constants.INSERT_COMMON_TEMPLATE % ("sites_properties", fieldValueString)
            queryCallback(query, Constants.PRIMARY_DB_ID)


  # # update data in sites_properties table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def updateSiteProperties(self, site, queryCallback):
    if site.properties is not None:
      localDict = {}
      query = None
      for field in site.properties:
        if field is not None:
          query = None
          localDict = self.createPropDict(field, site)
          if "siteId" in localDict and localDict["siteId"] is not None and "name" in localDict and \
          localDict["name"] is not None:
            fields, values = Constants.getFieldsValuesTuple(localDict, Constants.propDict)
            if len(fields) > 0 and len(fields) == len(values):
              fieldValueString = Constants.createFieldsValuesString(fields, values)
              query = Constants.SITE_PROP_SQL_UPDATE % (fieldValueString, localDict["siteId"], localDict["name"])
              queryCallback(query, Constants.PRIMARY_DB_ID)
          else:
            logger.debug("Site.Properties \"SiteId\" or \"name\" fields are empty")


  # # add data in sites_urls table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSiteURLSites(self, site, queryCallback):
    for urlObject in site.urls:
      if urlObject is not None:
        fields, values = Constants.getFieldsValuesTuple(urlObject, Constants.SiteURLTableDitct)
        fieldValueString = Constants.createFieldsValuesString(fields, values)
        query = Constants.SITE_URL_SQL_TEMPLATE % fieldValueString
        queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_INDEX, True)


  # # update data in sites_urls table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def updateSiteURLSites(self, site, queryCallback):
    query = None
    urlMd5Defined = False
    for urlObject in site.urls:
      try:
        if urlObject is not None:
          if urlObject.url is not None:
            urlMd5 = hashlib.md5(urlObject.url).hexdigest()
          else:
            urlMd5 = None
          # Check is URL already exists with urlMd5 different from got to update
          if urlObject.urlMd5 is not None and urlObject.url is not None:
            query = str(Constants.SITE_URL_SQL_SELECT_COUNT + "`URL`='%s' AND `URLMd5`<>'%s'") % \
                       (Utils.escape(urlObject.url), urlObject.urlMd5)
            r = queryCallback(query, Constants.PRIMARY_DB_ID)
            if r is None or (len(r) > 0) and len(r[0]) > 0 and r[0][0] > 0:
              logger.error("Root URL '%s' already exists in dc_sites.sites_urls!", str(urlObject.url))
              continue
          if urlObject.url is not None and urlObject.urlMd5 is None:
            urlMd5Defined = False
            urlObject.urlMd5 = urlMd5
          elif urlObject.urlMd5 is not None:
            urlMd5Defined = True
          else:
            urlMd5Defined = False
          fields, values = Constants.getFieldsValuesTuple(urlObject, Constants.SiteURLTableDitct)
          fieldValueString = Constants.createFieldsValuesString(fields, values)
          if urlMd5Defined is False and urlObject.url is not None:
            query = str(Constants.SITE_URL_SQL_UPDATE + " AND `URL`='%s'") % (fieldValueString, site.id, urlObject.url)
          elif urlMd5Defined is True:
            query = str(Constants.SITE_URL_SQL_UPDATE + " AND `URLMd5`='%s'") % (fieldValueString, site.id,
                                                                                 urlObject.urlMd5)
          else:
            query = None
          if query is not None:
            queryCallback(query, Constants.PRIMARY_DB_ID)
          else:
            logger.error('No url or urlMd5 value in urlObject, update query not created!\n%s' + str(urlObject))
          # Additionally update the urlMd5 after URL update to synch them if urlMd5 not matched
          if urlMd5Defined and urlObject.url is not None and urlMd5 != urlObject.urlMd5:
            query = (Constants.SITE_URL_SQL_UPDATE + "AND `URL`='%s'") % ('URLMd5="' + str(urlMd5) + '"', site.id,
                                                                          Utils.escape(urlObject.url))
            logger.debug('Update old URLMd5 with new: %s for site: %s, url: %s, query: %s', urlMd5, str(site.id),
                         urlObject.url, str(query))
            queryCallback(query, Constants.PRIMARY_DB_ID)
      except Exception, err:
        logger.error("Error: %s, query:%s, urlMd5Defined: %s, urlObject.url: %s", str(err), str(query),
                     str(urlMd5Defined), str(urlObject.url))
        logger.error(Utils.getTracebackInfo())

      self.statisticLogUpdate(site, urlObject.urlMd5, site.id, urlObject.status, queryCallback)


  # # add data in dc_urls.url_site.id table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSiteURLURLs(self, site, queryCallback):
    for urlObject in site.urls:
      urlMD5 = hashlib.md5(urlObject.url).hexdigest()
      StatisticLogManager.addNewRecord(queryCallback, site.id, urlMD5)
      if isinstance(site, dc.EventObjects.Site):
        localURLObject = copy.copy(urlObject)
        localURLObject.siteId = site.id
        if site.urlType is not None:
          localURLObject.type = site.urlType
        if site.requestDelay is not None:
          localURLObject.requestDelay = site.requestDelay
        if site.httpTimeout is not None:
          localURLObject.httpTimeout = site.httpTimeout
        localURLObject.urlMd5 = urlMD5
        DC_SITE_URL_SQL_TEMPLATE = "INSERT IGNORE INTO `%s` SET %s"
        fields, values = Constants.getFieldsValuesTuple(localURLObject, Constants.URLTableDict)
        fieldValueString = Constants.createFieldsValuesString(fields, values)
        query = DC_SITE_URL_SQL_TEMPLATE % ((DC_URLS_TABLE_NAME_TEMPLATE % site.id), fieldValueString)
      else:
        DC_SITE_URL_SQL_TEMPLATE = ("INSERT IGNORE INTO `%s` SET `Site_Id`='%s', `URL`='%s', `URLMD5`='%s'")
        query = DC_SITE_URL_SQL_TEMPLATE % ((DC_URLS_TABLE_NAME_TEMPLATE % site.id), site.id,
                                            MySQLdb.escape_string(urlObject.url), urlMD5)  # pylint: disable=E1101
      queryCallback(query, Constants.SECONDARY_DB_ID)


  # # create new table in dc_urls db
  #
  # @param site instance of Site object
  # @param template path to the current create table template file
  # @param dbId current database id
  # @param replaceDic strings dict() to replace key with value in template
  # @param queryCallback function for queries execution
  def createTableFromTemplate(self, site, template, dbId, queryCallback, replaceDic=None):
    try:
      if replaceDic is None:
        replaceDic = {}
      fTemplate = open(template).read()
      for rFrom in replaceDic:
        fTemplate = fTemplate.replace(rFrom, replaceDic[rFrom])
      query = fTemplate.replace("%SITE_ID%", str(site.id))
      queryCallback(query, dbId)
    except Exception, err:
      logger.error("DB error: %s\nquery: %s", str(err), template)


  # # create empty file for Key-Value db
  #
  # @param site instance of Site object
  # @param queryCallback callback for sql requests
  def addSiteInKVDB(self, site, queryCallback):
    ret = None
    if self.dBDataTask is not None:
      dataCreateRequest = dc.EventObjects.DataCreateRequest(site.id, None, None)
      ret = self.dBDataTask.process(dataCreateRequest, queryCallback)
    return ret


  # # makes roolback operation for current site if SITE_NEW operating got fault
  #
  # @param site instance of Site object
  # @param queryCallback callback for sql requests
  def siteDelete(self, site, queryCallback):
    if self.siteDeleteTask is not None:
      siteDelete = dc.EventObjects.SiteDelete(site.id)
      self.siteDeleteTask.process(siteDelete, queryCallback)


  # #execSiteCriterion method extract sites ids by siteCriterions
  #
  # @param criterions - criterions dict
  # @param queryCallback function for queries execution
  # @return list of appropriate site's ids
  @staticmethod
  def execSiteCriterions(criterions, queryCallback):
    ret = []
    SITE_CRITERION_TEMPLATE = "SELECT `Id` FROM `sites`"
    additionWhere = app.SQLCriterions.generateCriterionSQL(criterions, None)
    if additionWhere is not None and additionWhere != "":
      query = SITE_CRITERION_TEMPLATE + additionWhere
      result = queryCallback(query, Constants.PRIMARY_DB_ID)
      if hasattr(result, '__iter__'):
        ret = [elem[0] for elem in result]
    return ret
