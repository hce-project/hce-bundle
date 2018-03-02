'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc_db.Constants as Constants
from dc_db.URLStatusTask import URLStatusTask
from dc_db.SiteTask import SiteTask
from dc_db import FieldRecalculator
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #process siteStatus event
class SiteStatusTask(object):


  # #constructor
  #
  def __init__(self):
    self.urlStatusTask = URLStatusTask()


  # #make all necessary actions to get site status
  #
  # @param siteStatus instance of SiteStatus object
  # @param queryCallback function for queries execution
  # @return instance of Site object
  def process(self, siteStatus, queryCallback):
    # recalculation site values
    recalculator = FieldRecalculator.FieldRecalculator()
    recalculator.commonRecalc(siteStatus.id, queryCallback)

    site = dc.EventObjects.Site("")
    localSQLCause = ("`Id` = '%s'" % siteStatus.id)
    query = Constants.SELECT_SQL_TEMPLATE % ("sites", localSQLCause)
    res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    # add filling from other tables(filters, urls, ...)
    if hasattr(res, '__iter__') and len(res) > 0:
      for row in res:
        for field in Constants.siteDict.keys():
          if hasattr(site, field) and Constants.siteDict[field] in row:
            setattr(site, field, row[Constants.siteDict[field]])
        site.uDate = Constants.readDataTimeField("UDate", row)
        site.tcDate = Constants.readDataTimeField("TcDate", row)
        site.tcDateProcess = Constants.readDataTimeField("TcDateProcess", row)
        site.cDate = Constants.readDataTimeField("CDate", row)
        site.recrawlDate = Constants.readDataTimeField("RecrawlDate", row)
      if SiteTask.FIELD_NAME_URLS not in siteStatus.excludeList:
        site.urls = self.fillUrls(siteStatus, queryCallback)
      else:
        site.urls = None

      logger.debug('>>>  siteStatus.excludeList: ' + str(siteStatus.excludeList))

      if SiteTask.FIELD_NAME_PROPERTIES not in siteStatus.excludeList:
        site.properties = self.fillProperties(siteStatus, queryCallback)
        # logger.debug('>>>  site.properties: ' + str(site.properties))
      else:
        site.properties = None
        # logger.debug('>>>  site.properties: ' + str(site.properties))

      if SiteTask.FIELD_NAME_FILTERS not in siteStatus.excludeList:
        site.filters = self.fillFilters(siteStatus, queryCallback)
      else:
        site.filters = None
    else:
      site.state = dc.EventObjects.Site.STATE_NOT_FOUND
    return site


  # #Extracts and returns urls, selected from databse
  #
  # @param siteStatus instance of SiteStatus object
  # @param queryCallback function for queries execution
  # @return urls list
  def fillUrls(self, siteUpdate, queryCallback):
    URL_SQL_QUERY = "SELECT * FROM `sites_urls` WHERE `Site_Id` = '%s'"
    query = URL_SQL_QUERY % siteUpdate.id
    res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    urls = self.urlStatusTask.fillUrlsList(res, dc.EventObjects.SiteURL, Constants.SiteURLTableDitct)
    return urls


  # #Extracts and returns filters, selected from databse
  #
  # @param siteStatus instance of SiteStatus object
  # @param queryCallback function for queries execution
  # @return filters list
  def fillFilters(self, siteUpdate, queryCallback):
    filters = []
    localFilter = None
    GET_FILTERS_SQL_QUERY = "SELECT * FROM `sites_filters` WHERE Site_Id = '%s'"
    query = GET_FILTERS_SQL_QUERY % siteUpdate.id
    res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    if hasattr(res, '__iter__'):
      for row in res:
        if Constants.filterDict["siteId"] in row and row[Constants.filterDict["siteId"]] is not None and \
        Constants.filterDict["pattern"] in row and row[Constants.filterDict["pattern"]] is not None:
          localFilter = dc.EventObjects.SiteFilter(row[Constants.filterDict["siteId"]],
                                                   row[Constants.filterDict["pattern"]])
          for elem in Constants.filterDict.keys():
            if Constants.filterDict[elem] in row and hasattr(localFilter, elem):
              setattr(localFilter, elem, row[Constants.filterDict[elem]])
          localFilter.uDate = Constants.readDataTimeField("UDate", row)
          localFilter.cDate = Constants.readDataTimeField("CDate", row)
          filters.append(localFilter)
    else:
      logger.error("fillFilters return None")
    return filters


  # #Extracts and returns properties, selected from databse
  #
  # @param siteStatus instance of SiteStatus object
  # @param queryCallback function for queries execution
  # @return properties dict
  def fillProperties(self, siteUpdate, queryCallback):
    properties = []
    GET_PROPERTIES_SQL_QUERY = "SELECT * FROM `sites_properties` WHERE Site_Id = '%s'"
    query = GET_PROPERTIES_SQL_QUERY % siteUpdate.id
    res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
    if hasattr(res, '__iter__'):
      for row in res:
        prop = {}
        for elem in Constants.propDict.keys():
          if Constants.propDict[elem] in row:
            prop[elem] = row[Constants.propDict[elem]]
        if len(prop.keys()) > 0:
          localDate = Constants.readDataTimeField("UDate", row)
          if localDate is not None:
            prop["uDate"] = localDate
          localDate = Constants.readDataTimeField("CDate", row)
          if localDate is not None:
            prop["cDate"] = localDate
          properties.append(prop)
    else:
      logger.error("fillProperties return None")
    return properties
