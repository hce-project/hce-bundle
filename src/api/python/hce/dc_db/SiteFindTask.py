'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import MySQLdb

import dc.EventObjects
import dc_db.Constants as Constants
from dc_db.SiteTask import SiteTask
from dc_db.SiteStatusTask import SiteStatusTask
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #sql query which find site by root url
GET_SITE_SQL_TEMPLATE = " SELECT * FROM %s WHERE `Id`='%s'"
GET_SITE_URLS_SQL_TEMPLATE = " SELECT `URL` FROM sites_urls WHERE `Site_Id`='%s'"
GET_SITE_PROPERTIES_SQL_TEMPLATE = " SELECT `Name`, `Value` FROM sites_properties WHERE `Site_Id`='%s'"
GET_SITE_FILTERS_SQL_TEMPLATE = " SELECT `Pattern`, `Type`, `Mode` FROM sites_filters WHERE `Site_Id`='%s'"

# @todo move to apropriate place
TASK_NOT_EXIST_ERR = 2020
TASK_NOT_EXISTS_ERR_MSG = "Duplicate site"


class SiteFindTask(SiteTask):


  # #constructor
  #
  # @param dcSiteTemplate path to sql template for dc_urls_* tables
  def __init__(self, dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir, dBDataTask, dcStatTemplates,
               dcLogTemplate, dcAttrTemplate):
    super(SiteFindTask, self).__init__(dcSiteTemplate, keyValueDefaultFile, keyValueStorageDir, dBDataTask,
                                       dcStatTemplates, dcLogTemplate, dcAttrTemplate)
    self.siteStatusTask = None


  # #make all necessary actions to update site into in mysql db
  #
  # @param siteUpdate instance of SiteUpdate object
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, siteFind, queryCallback):
    self.siteStatusTask = SiteStatusTask()
    sites = self.siteFind(siteFind, queryCallback)
    return sites


  # #
  #
  def loadSiteFromDB(self, siteFind, site_id, site, queryCallback):
    tableName = 'sites'
    tables = tableName
    if dc.EventObjects.SiteFind.CRITERION_TABLES in siteFind.criterions and \
      siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES] is not None and \
      siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES] != "":
      if tableName not in siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES]:
        tables = tableName + ", " + siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES]
      else:
        tables = siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES]

    query = GET_SITE_SQL_TEMPLATE % (tables, site_id["Site_Id"])
    # logger.debug("query: %s", str(query))
    site_row = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    logger.debug("Get site from sites: %s", str(site_row))
    for (key, value) in Constants.siteDict.items():
      if str(value)[:1] == "`":
        value = str(value)[1:-1]
      # logger.debug("key: %s; value: %s", str(key), str(value))
      logger.debug("site field: %s; table field: %s", str(site.__dict__[key]), str(site_row[0].get(value, None)))
      if key == "uDate":
        site.__dict__[key] = str(site_row[0].get(value, None))
      elif key == "tcDate":
        site.__dict__[key] = str(site_row[0].get(value, None))
      elif key == "tcDateProcess":
        site.__dict__[key] = str(site_row[0].get(value, None))
      elif key == "cDate":
        site.__dict__[key] = str(site_row[0].get(value, None))
      elif key == "recrawlDate":
        site.__dict__[key] = str(site_row[0].get(value, None))
      else:
        site.__dict__[key] = site_row[0].get(value, "a")
      # site.cDate = str(site_row[0]["CDate"])
    return site


  # #
  #
  def loadListOfSitesFromDB(self, siteFind, queryCallback):
    if siteFind.url is not None and (not siteFind.criterions):
      query = "SELECT `Site_Id` FROM sites_urls WHERE `URL` LIKE '" + MySQLdb.escape_string(siteFind.url) + "%' GROUP BY `Site_Id`"  # pylint: disable=E1101,C0301
    elif (siteFind.url is not None) and (siteFind.criterions is not None):
      additionCriterion = " `URL` LIKE '" + MySQLdb.escape_string(siteFind.url) + "%' "  # pylint: disable=E1101,C0301
      query = "SELECT `Site_Id` FROM sites_urls " + self.generateCriterionSQL(siteFind.criterions, additionCriterion)
    else:
      # Fix for tables list to use both "sites" and "sites_urls" tables
      tableName = "sites_urls"
      if ("WHERE" in siteFind.criterions) and (siteFind.criterions["WHERE"] is not None) and \
      (tableName in siteFind.criterions["WHERE"]):
        addTable = ", " + tableName
      else:
        addTable = ""

      sitesTableName = 'sites'
      if dc.EventObjects.SiteFind.CRITERION_TABLES in siteFind.criterions and \
        siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES] is not None and \
        siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES] != "":
        if sitesTableName not in siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES]:
          addTable = ", " + siteFind.criterions[dc.EventObjects.SiteFind.CRITERION_TABLES]

      query = "SELECT `Id` AS Site_Id FROM " + sitesTableName + addTable + self.generateCriterionSQL(siteFind.criterions)

    # logger.debug("query: %s", str(query))
    site_ids = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    logger.debug("List of Site_Id: %s", str(site_ids))

    return site_ids


  # #check if given site exist in current db
  #
  # @param siteId id of checking site
  # @param queryCallback function for queries execution
  # @return True if exist, or False
  def siteFind(self, siteFind, queryCallback):
    sites = []
    # get all UNIQ site id's with urls for given url
    site_ids = self.loadListOfSitesFromDB(siteFind, queryCallback)
    if hasattr(site_ids, "__iter__"):
      # for each site fill it fields
      for site_id in site_ids:
        site = dc.EventObjects.Site("")
        # load site from sites table
        self.loadSiteFromDB(siteFind, site_id, site, queryCallback)
        if SiteTask.FIELD_NAME_URLS not in siteFind.excludeList:
          site.urls = self.siteStatusTask.fillUrls(site, queryCallback)
        else:
          site.urls = None
        if SiteTask.FIELD_NAME_PROPERTIES not in siteFind.excludeList:
          site.properties = self.siteStatusTask.fillProperties(site, queryCallback)
        else:
          site.properties = None
        if SiteTask.FIELD_NAME_FILTERS not in siteFind.excludeList:
          site.filters = self.siteStatusTask.fillFilters(site, queryCallback)
        else:
          site.filters = None
        sites.append(site)

    return sites
