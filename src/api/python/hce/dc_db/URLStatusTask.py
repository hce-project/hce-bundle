'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dc_db.BaseTask import BaseTask
from dc_db import Constants
import dc.EventObjects
from app.Utils import UrlNormalizator
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process urlStatus event
class URLStatusTask(BaseTask):

  # #constructor
  #
  def __init__(self):
    pass


  # #make all necessary actions to get status of input URLs
  #
  # @param urlStatus list of URLStatus objects
  # @param queryCallback function for queries execution
  # @return list of URL objects
  def process(self, urlStatuses, queryCallback):
    urls = []
    for urlStatus in urlStatuses:
      # @todo add more complex case
      if self.isSiteExist(urlStatus.siteId, queryCallback):
        urls.extend(self.getURL(urlStatus, queryCallback))
    return urls


  # #select URL fields from url_siteId table and filled return object list list[URL]
  #
  # @param urlStatus object of UrlStatus type
  # @param queryCallback function for queries execution
  # @return list[URL]
  def getURL(self, urlStatus, queryCallback):
    URL_SELECT_SQL = "SELECT * FROM `%s` WHERE %s"
    tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlStatus.siteId
    WHERE_CLAUSE = "URL = '%s'"
    if urlStatus.urlType == dc.EventObjects.URLStatus.URL_TYPE_MD5:
      WHERE_CLAUSE = "URLMd5 = '%s'"
    query = URL_SELECT_SQL % (tableName, WHERE_CLAUSE % (urlStatus.url))
    res = queryCallback(query, Constants.SECONDARY_DB_ID, Constants.EXEC_NAME)

    urls = self.fillUrlsList(res, dc.EventObjects.URL, Constants.URLTableDict)
    return urls


  # #fill urls list in common format
  #
  # @param res - MySQL return SELECT * query
  # @param urlType - type of concret URL object's type
  # @return urlDict - concret URL dict
  def fillUrlsList(self, res, urlType, urlDict):
    ret = []
    if hasattr(res, '__iter__'):
      for row in res:
        if "Site_Id" in row and "URL" in row:
          url = urlType(siteId=row["Site_Id"], url=row["URL"], normalizeMask=UrlNormalizator.NORM_NONE)
          for field in urlDict.keys():
            if hasattr(url, field) and urlDict[field] in row:
              setattr(url, field, row[urlDict[field]])
          url.UDate = Constants.readDataTimeField("UDate", row)
          url.CDate = Constants.readDataTimeField("CDate", row)
          url.lastModified = Constants.readDataTimeField("LastModified", row)
          url.tcDate = Constants.readDataTimeField("TcDate", row)
          url.pDate = Constants.readDataTimeField("PDate", row)
          ret.append(url)
    else:
      logger.error(">>> SQL Select return NULL or not itereble")
    return ret
