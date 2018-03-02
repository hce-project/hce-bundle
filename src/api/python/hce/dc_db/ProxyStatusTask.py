'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import copy
import collections

from dc_db.BaseTask import BaseTask
import dc_db.Constants as Constants
import dc.EventObjects
import app.SQLCriterions
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # ProxyStatusTask Class, implements Proxy Status task functionality
#
class ProxyStatusTask(BaseTask):

  # #Class constructor
  #
  def __init__(self):
    super(ProxyStatusTask, self).__init__()


  # #make all necessary actions to fetch Proxies from mysql db
  #
  # @param urls list of Proxies objects
  # @param queryCallback function for queries execution
  # @return list of fetching proxies
  def process(self, proxyStatuses, queryCallback):
    proxies = []
    for proxyStatus in proxyStatuses:
      localProxyStatuses = []
      if proxyStatus.siteId is None or proxyStatus.host is None and proxyStatus.criterions is not None:
        result = ProxyStatusTask.execCriterion(proxyStatus, queryCallback, proxyStatus.siteId)
        for elem in result:
          localProxy = copy.deepcopy(proxyStatus)
          # if localProxy.siteId is None:
          localProxy.siteId = elem["Site_Id"]
          # if localProxy.host is None:
          localProxy.host = elem["Host"]
          localProxyStatuses.append(localProxy)
      else:
        localProxyStatuses.append(proxyStatus)
      logger.debug(">>> len(localProxyStatuses) = " + str(len(localProxyStatuses)))
      for localProxy in localProxyStatuses:
        proxy = self.fetchProxy(localProxy, queryCallback)
        if proxy is not None:
          proxies.append(proxy)
    return proxies


  # #execCriterion fetches proxy DB records by criterions
  #
  # @param proxyStatus incoming proxyStatus element
  # @param queryCallback function for queries execution
  # @param siteId incoming siteId, may be None
  # @return list of fetching proxies
  @staticmethod
  def execCriterion(proxyStatus, queryCallback, siteId, additionWhere=None):
    ret = []
    PROXY_SELECT_TEMPLATE = "SELECT * FROM `sites_proxy`"
    criterionString = app.SQLCriterions.generateCriterionSQL(proxyStatus.criterions, additionWhere, siteId)
    if criterionString is not None and criterionString != "":
      query = PROXY_SELECT_TEMPLATE + criterionString
      res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)
      if isinstance(res, collections.Iterable):
        ret = res

    return ret


  # #fetchProxy fetches one proxy element
  #
  # @param queryCallback function for queries execution
  # @return Proxy object or None
  def fetchProxy(self, localProxy, queryCallback):
    ret = None
    if localProxy.siteId is not None and localProxy.host is not None:
      try:
        PROXY_FETCH_TEMPLATE = "SELECT * FROM `sites_proxy` WHERE `Site_Id` = '%s' AND `Host` = '%s'"
        query = PROXY_FETCH_TEMPLATE % (localProxy.siteId, localProxy.host)
        res = queryCallback(query, Constants.PRIMARY_DB_ID, Constants.EXEC_NAME)

        if isinstance(res, collections.Iterable) and len(res) > 0:
          ret = dc.EventObjects.Proxy(res[0]["Site_Id"], res[0]["Host"])
          ret.id = res[0]["Id"]
          ret.domains = res[0]["Domains"]
          ret.priority = res[0]["Priority"]
          ret.state = res[0]["State"]
          ret.countryCode = res[0]["CountryCode"]
          ret.countryName = res[0]["CountryName"]
          ret.regionCode = res[0]["RegionCode"]
          ret.regionName = res[0]["RegionName"]
          ret.cityName = res[0]["CityName"]
          ret.zipCode = res[0]["ZipCode"]
          ret.timeZone = res[0]["TimeZone"]
          ret.latitude = res[0]["Latitude"]
          ret.longitude = res[0]["Longitude"]
          ret.metroCode = res[0]["MetroCode"]
          ret.faults = res[0]["Faults"]
          ret.faultsMax = res[0]["FaultsMax"]
          ret.categoryId = res[0]["Category_Id"]
          ret.limits = res[0]["Limits"]
          ret.description = res[0]["Description"]
          ret.cDate = res[0]["CDate"]
          ret.uDate = res[0]["UDate"]
      except Exception as excp:
        logger.debug(">>> ProxyStatusTask.fetchProxy some exception = " + str(excp))
    return ret
