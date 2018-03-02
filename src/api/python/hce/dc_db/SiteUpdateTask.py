'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import hashlib
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401
import app.SQLCriterions
from dtm.EventObjects import GeneralResponse
import dc_db.Constants as Constants
from dc_db.FieldRecalculator import FieldRecalculator
from dc_db.BaseTask import BaseTask
from dc_db.SiteTask import SiteTask
from dc_db.URLDeleteTask import URLDeleteTask

logger = Utils.MPLogger().getLogger()


# #sql query which checks existence of a table
# CHECK_TABLE_SQL_TEMPLATE = " SELECT COUNT(*) FROM sites WHERE Id = '%s'"

# @todo move to apropriate place
TASK_NOT_EXIST_ERR = 2020
TASK_NOT_EXISTS_ERR_MSG = "Site Id Not Found"


class SiteUpdateTask(SiteTask):


  # #constructor
  #
  # @param dcSiteTemplate path to sql template for dc_urls_* tables
  def __init__(self, dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir, rawDataDir, dBDataTask, dcStatTemplate,
               dcLogTemplate, dcAttrTemplate):
    super(SiteUpdateTask, self).__init__(dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir, dBDataTask,
                                         dcStatTemplate, dcLogTemplate, dcAttrTemplate)
    self.urlDeleteTask = URLDeleteTask(keyValueStorageDir, rawDataDir, dBDataTask)
    self.fieldRecalculator = FieldRecalculator()


  # #make all necessary actions to update site into in mysql db
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, siteUpdate, queryCallback):
    siteIds = []
    response = GeneralResponse()
    if siteUpdate.id is None:
      siteIds.extend(self.fetchByCriterions(siteUpdate.criterions, queryCallback))
    else:
      siteIds.append(siteUpdate.id)

    for siteId in siteIds:
      siteUpdate.id = siteId
      if super(SiteUpdateTask, self).isSiteExist(siteUpdate.id, queryCallback):
        self.updateSite(siteUpdate, queryCallback)
        self.updateSitesFilter(siteUpdate, queryCallback)
        self.updateSiteProperties(siteUpdate, queryCallback)
        sitePropValue = BaseTask.readValueFromSiteProp(siteUpdate.id, "UPDATE_NOT_INSERT_ROOT_URLS", queryCallback)
        if siteUpdate.updateType != dc.EventObjects.SiteUpdate.UPDATE_TYPE_UPDATE and\
          (sitePropValue is None or not bool(int(sitePropValue))) and siteUpdate.urls is not None:
          self.deleteRootUrlsFromURLsUrls(siteUpdate.id, queryCallback)
        elif siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_UPDATE and siteUpdate.urls is not None:
          self.updateURlsURL(siteUpdate.urls, siteId, queryCallback)
        self.updateSiteURL(siteUpdate, queryCallback)
        self.restartSite(siteUpdate, queryCallback)
        if siteUpdate.updateType != dc.EventObjects.SiteUpdate.UPDATE_TYPE_UPDATE and\
          (sitePropValue is None or not bool(int(sitePropValue))) and siteUpdate.urls is not None:
          logger.debug("Copy root URLs from dc_sites.site_urls table to dc_urls.urls_*")
          self.copyURLsFromSiteURlsToURLsURLs(siteUpdate.id, queryCallback)
        self.fieldRecalculator.updateSiteCleanupFields(siteId, queryCallback)
        response.statuses.append(GeneralResponse.ERROR_OK)
      else:
        response.statuses.append(TASK_NOT_EXIST_ERR)

    return response


  # # update data in sites table
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  def updateSite(self, siteUpdate, queryCallback):
    SQL_UPDATE_SITE_SQL_TEMPLATE = "UPDATE sites SET %s WHERE `Id` = '%s'"
    fields, values = Constants.getFieldsValuesTuple(siteUpdate, Constants.siteDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values, Constants.siteExcludeList)
    query = SQL_UPDATE_SITE_SQL_TEMPLATE % (fieldValueString, siteUpdate.id)
    logger.debug('>>> updateSite  query: ' + str(query))
    queryCallback(query, Constants.PRIMARY_DB_ID)


  # #update data in sites_filters table
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  def updateSitesFilter(self, siteUpdate, queryCallback):
    if siteUpdate.filters is not None:
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_APPEND:
        super(SiteUpdateTask, self).addSitesFilter(siteUpdate, queryCallback)
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_OVERWRITE:
        query = Constants.DEL_BY_ID_QUERY_TEMPLATE % ("sites_filters", siteUpdate.id)
        queryCallback(query, Constants.PRIMARY_DB_ID)
        super(SiteUpdateTask, self).addSitesFilter(siteUpdate, queryCallback)
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_UPDATE:
        super(SiteUpdateTask, self).updateSitesFilter(siteUpdate, queryCallback)


  # #update data in sites_properties table
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  def updateSiteProperties(self, siteUpdate, queryCallback):
    if siteUpdate.properties is not None:
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_APPEND:
        super(SiteUpdateTask, self).addSiteProperties(siteUpdate, queryCallback)
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_OVERWRITE:
        query = Constants.DEL_BY_ID_QUERY_TEMPLATE % ("sites_properties", siteUpdate.id)
        queryCallback(query, Constants.PRIMARY_DB_ID)
        super(SiteUpdateTask, self).addSiteProperties(siteUpdate, queryCallback)
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_UPDATE:
        super(SiteUpdateTask, self).updateSiteProperties(siteUpdate, queryCallback)


  # #update data in sites_urls table
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  def updateSiteURL(self, siteUpdate, queryCallback):
    if siteUpdate.urls is not None:
      site = dc.EventObjects.Site("")
      site.urls = siteUpdate.urls
      site.id = siteUpdate.id
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_APPEND:
        super(SiteUpdateTask, self).addSiteURLSites(site, queryCallback)
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_OVERWRITE:
        URL_TABLE_DEL_TEMPLATE = "DELETE FROM `sites_urls` WHERE `Site_Id` = '%s'"
        query = URL_TABLE_DEL_TEMPLATE % siteUpdate.id
        queryCallback(query, Constants.PRIMARY_DB_ID)
        super(SiteUpdateTask, self).addSiteURLSites(site, queryCallback)
      if siteUpdate.updateType == dc.EventObjects.SiteUpdate.UPDATE_TYPE_UPDATE:
        super(SiteUpdateTask, self).updateSiteURLSites(siteUpdate, queryCallback)


  # #update data in urls_ table
  #
  # @param urls objects list
  # @param queryCallback function for queries execution
  def updateURlsURL(self, urls, siteId, queryCallback):
    query = None
    urlMd5Defined = None
    for urlObject in urls:
      try:
        if urlObject is not None:
          if urlObject.url is not None:
            urlMd5 = hashlib.md5(urlObject.url).hexdigest()
          else:
            urlMd5 = None
          # Check is URL already exists with urlMd5 different from got to update
          if urlObject.urlMd5 is not None and urlObject.url is not None:
            query = str(Constants.URL_URL_SQL_SELECT_COUNT + "`URL`='%s' AND `URLMd5`<>'%s'") % \
                       (siteId, Utils.escape(urlObject.url), urlObject.urlMd5)
            r = queryCallback(query, Constants.SECONDARY_DB_ID)
            if r is None or (len(r) > 0) and len(r[0]) > 0 and r[0][0] > 0:
              logger.error("Root URL '%s' already exists in dc_urls.urls_%s !", str(urlObject.url), siteId)
              continue
          if urlObject.url is not None and urlObject.urlMd5 is None:
            urlMd5Defined = False
            urlObject.urlMd5 = urlMd5
          elif urlObject.urlMd5 is not None:
            urlMd5Defined = True
          else:
            urlMd5Defined = False
          fields, values = Constants.getFieldsValuesTuple(urlObject, Constants.URLTableDict)
          fieldValueString = Constants.createFieldsValuesString(fields, values)
          if urlMd5Defined is False and urlObject.url is not None:
            query = str(Constants.URL_URL_SQL_UPDATE + " `URL`='%s'") % (siteId, fieldValueString, urlObject.url)
          elif urlMd5Defined is True:
            query = str(Constants.URL_URL_SQL_UPDATE + " `URLMd5`='%s'") % (siteId, fieldValueString, urlObject.urlMd5)
          else:
            query = None
          if query is not None:
            queryCallback(query, Constants.SECONDARY_DB_ID)
          else:
            logger.error('No url or urlMd5 value in urlObject, update query not created!\n%s' + str(urlObject))
          # Additionally update the urlMd5 after URL update to synch them if urlMd5 not matched
          if urlMd5Defined and urlMd5 != urlObject.urlMd5:
            query = (Constants.URL_URL_SQL_UPDATE + " `URL`='%s'") % (siteId, 'URLMd5="' + str(urlMd5) + '"',
                                                                      Utils.escape(urlObject.url))
            logger.debug('Update old URLMd5 with new: %s for url: %s, query: %s', urlMd5, urlObject.url, str(query))
            queryCallback(query, Constants.SECONDARY_DB_ID)
      except Exception, err:
        logger.error("Error: %s, query:%s, urlMd5Defined: %s, urlObject.url: %s", str(err), str(query),
                     str(urlMd5Defined), str(urlObject.url))
        logger.error(Utils.getTracebackInfo())


  # #update data in sites_urls and sites tables
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  def restartSite(self, siteUpdate, queryCallback):
    if siteUpdate.state == siteUpdate.STATE_RESTART:
      UPDATE_SITE_SQL_QUERY = ("UPDATE `sites` SET `State`=%s, `UDate`=NOW(), " +
                               "`Iterations`=`Iterations`+1, `ErrorMask`=0, `Errors`=0 WHERE Id='%s'")
      query = UPDATE_SITE_SQL_QUERY % (str(dc.EventObjects.Site.STATE_ACTIVE), siteUpdate.id)
      queryCallback(query, Constants.PRIMARY_DB_ID)
      # TODO: need to remove the URLs from urls_ and then insert from sites_urls
      # siteUpdate.urls = []
      # SELECT_QUERY = "SELECT `URL` FROM `sites_urls` WHERE `Site_Id` = '%s'"
      # query = SELECT_QUERY % siteUpdate.id
      # res = queryCallback(query, Constants.PRIMARY_DB_ID)
      # if hasattr(res, '__iter__'):
      #  for row in res:
      #    siteUpdate.urls.append(dc.EventObjects.URL(siteUpdate.id, row[0]))
      # super(SiteUpdateTask, self).addSiteURLURLs(siteUpdate, queryCallback)


  # #deleteRootUrlsUrls method deletes all root urls from dc_urls dadabases[siteId's table]
  #
  # @param siteId current siteId
  # @param queryCallback function for queries execution
  def deleteRootUrlsFromURLsUrls(self, siteId, queryCallback):
    logger.debug("Delete all root URLs from dc_urls.urls_* table")
    urlDeleteObj = dc.EventObjects.URLDelete(siteId, None,
                                             reason=dc.EventObjects.URLDelete.REASON_SITE_UPDATE_ROOT_URLS)
    # whereCriterionStr = \
    #      "`URLMd5` IN (SELECT `URLMd5` FROM dc_sites.sites_urls WHERE `Site_Id` = '%s')" % siteId
    whereCriterionStr = "`ParentMd5`=''"
    urlDeleteObj.criterions = {app.SQLCriterions.CRITERION_WHERE : whereCriterionStr}
    self.urlDeleteTask.process([urlDeleteObj], queryCallback)


  # #moveURLsFromSiteURlsToDcURLs copies all root urls from sites_urls to the dc_urls
  #
  # @param siteId current siteId
  # @param queryCallback function for queries execution
  def copyURLsFromSiteURlsToURLsURLs(self, siteId, queryCallback):
    if len(Constants.URLTableDict) > 0:
      tbName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % siteId
      query = "INSERT IGNORE INTO `%s` ("
      query = query % tbName
      fields = ''
      for elem in Constants.URLTableDict.values():
        fields += elem
        fields += ','

      fields = fields[:-1]
      query += fields
      query += (") SELECT ")
      query += fields
      query += (" FROM dc_sites.sites_urls WHERE `Site_Id`='%s' GROUP BY `URLMd5`" % siteId)

      queryCallback(query, Constants.SECONDARY_DB_ID)
