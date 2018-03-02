'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import hashlib
import logging
import Constants
import shutil
import dc.EventObjects
import MySQLdb
from BaseTask import BaseTask
from Constants import DC_URLS_TABLE_NAME_TEMPLATE
from dtm.EventObjects import GeneralResponse

logger = logging.getLogger(Constants.LOGGER_NAME)


# @todo move to apropriate place

class SiteTask(BaseTask):


  # #constructor
  #
  # @param dcSiteTemplate path to sql template for dc_urls_* tables
  def __init__(self, dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir):
    super(SiteTask, self).__init__()
    self.dcSiteTemplate = dcSiteTemplate
    self.keyValueDefaultFile = keyValueDefaultFile
    self.keyValueStorageDir = keyValueStorageDir


  # #make all necessary actions to add new site into mysql db
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, site, queryCallback):
    response = GeneralResponse()
    #if not self.isSiteExist(site.urls[0], queryCallback):
    if not self.isSiteExist(site.id, queryCallback, site.userId):
      self.addSite(site, queryCallback)
      self.addSitesFilter(site, queryCallback)
      self.addSiteProperties(site, queryCallback)
      self.createURLSitesFromTemplate(site, queryCallback)
      self.addSiteURLSites(site, queryCallback)
      self.addSiteURLURLs(site, queryCallback)
      self.addSiteInKVDB(site)
      response.statuses.append(site.id)
    else:
      response = GeneralResponse(Constants.TASK_DUBLICATE_ERR, Constants.TASK_DUBLICATE_ERR_MSG)
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
    for localFilter in site.filters:
      query = (Constants.SITE_FILTER_SQL_TEMPLATE % 
              (localFilter.siteId, str(localFilter.pattern), str(localFilter.type), str(localFilter.mode), str(localFilter.state),
                str(localFilter.stage), str(localFilter.subject), str(localFilter.action)))
      queryCallback(query, Constants.PRIMARY_DB_ID)



  # # update data in sites_filters table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def updateSitesFilter(self, site, queryCallback):
    for localFilter in site.filters:
      query = (Constants.SITE_FILTER_SQL_UPDATE % 
              (str(localFilter.pattern), localFilter.siteId, str(localFilter.type), str(localFilter.mode), str(localFilter.state)))
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
        if site.properties[field][0] != None:
          localDict["siteId"] = str(site.properties[field][0])
        else:
          localDict["siteId"] = site.id
        localDict["name"] = str(field)
        if site.properties[field][1] != None:
          localDict["value"] = str(site.properties[field][1])
        if site.properties[field][2] != None:
          localDict["urlMd5"] = str(site.properties[field][2])
      else:
        localDict["siteId"] = site.id
        localDict["name"] = str(field)
        localDict["value"] = str(site.properties[field])
    elif isinstance(site.properties, list) and isinstance(field, dict):
      localDict = field
    return localDict


  # # add data in sites_properties table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSiteProperties(self, site, queryCallback):
    if site.properties != None:
      localDict = {}
      query = None
      for field in site.properties:
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
    if site.properties != None:
      localDict = {}
      query = None
      for field in site.properties:
        query = None
        localDict = self.createPropDict(field, site)
        if "siteId" in localDict and localDict["siteId"] != None and "name" in localDict and localDict["name"] != None:
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
    for url in site.urls:
      query = Constants.SITE_URL_SQL_TEMPLATE % (site.id, MySQLdb.escape_string(url), site.userId)
      queryCallback(query, Constants.PRIMARY_DB_ID)


  # # update data in sites_urls table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def updateSiteURLSites(self, site, queryCallback):
    for url in site.urls:
      query = Constants.SITE_URL_SQL_UPDATE % (site.userId, site.id, MySQLdb.escape_string(url))
      queryCallback(query, Constants.PRIMARY_DB_ID)

  # # add data in dc_urls.url_site.id table
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def addSiteURLURLs(self, site, queryCallback):
    for url in site.urls:
      urlMD5 = hashlib.md5(url).hexdigest()
      if type(site) == type(dc.EventObjects.Site("")):
        DC_SITE_URL_SQL_TEMPLATE = ("INSERT INTO `%s` SET `Site_Id`='%s', `URL`='%s', `type`='%s', " +
                                    "`RequestDelay`='%s', `HTTPTimeout`='%s', `URLMD5`='%s'")
        query = DC_SITE_URL_SQL_TEMPLATE % ((DC_URLS_TABLE_NAME_TEMPLATE % site.id), site.id,
                                MySQLdb.escape_string(url), site.urlType, site.requestDelay, site.httpTimeout, urlMD5)
      else:
        DC_SITE_URL_SQL_TEMPLATE = ("INSERT INTO `%s` SET `Site_Id`='%s', `URL`='%s', `URLMD5`='%s')")
        query = DC_SITE_URL_SQL_TEMPLATE % ((DC_URLS_TABLE_NAME_TEMPLATE % site.id), site.id,
                                            MySQLdb.escape_string(url), urlMD5)
      queryCallback(query, Constants.SECONDARY_DB_ID)


  # # create new table in dc_urls db
  #
  # @param site instance of Site object
  # @param queryCallback function for queries execution
  def createURLSitesFromTemplate(self, site, queryCallback):
    template = open(self.dcSiteTemplate).read()
    query = template.replace("%SITE_ID%", str(site.id))
    queryCallback(query, Constants.SECONDARY_DB_ID)


  # # create empty file for Key-Value db
  #
  # @param site instance of Site object
  def addSiteInKVDB(self, site):
    keyValueFileName = self.keyValueStorageDir
    if keyValueFileName[-1] != '/':
      keyValueFileName += '/'
    keyValueFileName += (Constants.KEY_VALUE_FILE_NAME_TEMPLATE % site.id)
    shutil.copy(self.keyValueDefaultFile, keyValueFileName)
