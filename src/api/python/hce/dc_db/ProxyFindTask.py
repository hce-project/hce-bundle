'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dc_db.BaseTask import BaseTask
from dc_db.ProxyStatusTask import ProxyStatusTask
from dc_db.SiteTask import SiteTask
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # ProxyFindTask Class, implements Proxy Find task functionality
#
class ProxyFindTask(BaseTask):


  # #Class constructor
  #
  def __init__(self):
    super(ProxyFindTask, self).__init__()


  # #make all necessary actions to finding and returning Proxies from mysql db
  #
  # @param urls list of Proxies objects
  # @param queryCallback function for queries execution
  # @return list of finding proxies
  def process(self, proxyFinds, queryCallback):
    ret = []
    for proxyFind in proxyFinds:
      localSiteIds = []
      if proxyFind.siteId is None:
        if proxyFind.siteCriterions is not None and len(proxyFind.siteCriterions) > 0:
          localSiteIds = SiteTask.execSiteCriterions(proxyFind.siteCriterions, queryCallback)
        else:
          localSiteIds.append(None)
      else:
        localSiteIds.append(proxyFind.siteId)
      for localSiteId in localSiteIds:
        ret += self.fetchProxy(proxyFind, queryCallback, localSiteId)
    return ret


  # #fetchProxy method exctacts, using criterions, and returns list of Proxy objects
  #
  # @param proxyFind incoming ProxyFind object
  # @param queryCallback function for queries execution
  # @param localSiteId incoming sitesId, may be None
  # @return list of Proxy objects
  def fetchProxy(self, proxyFind, queryCallback, localSiteId):
    ret = []
    if localSiteId is None:
      additionWhere = None
    else:
      additionWhere = "`Site_Id` = '%s'" % localSiteId
    result = ProxyStatusTask.execCriterion(proxyFind, queryCallback, localSiteId, additionWhere)
    if hasattr(result, '__iter__'):
      for elem in result:
        localProxy = dc.EventObjects.Proxy(elem["Site_Id"], elem["Host"])
        localProxy.id = elem["Id"]
        localProxy.domains = elem["Domains"]
        localProxy.priority = elem["Priority"]
        localProxy.state = elem["State"]
        localProxy.countryCode = elem["CountryCode"]
        localProxy.countryName = elem["CountryName"]
        localProxy.regionCode = elem["RegionCode"]
        localProxy.regionName = elem["RegionName"]
        localProxy.cityName = elem["CityName"]
        localProxy.zipCode = elem["ZipCode"]
        localProxy.timeZone = elem["TimeZone"]
        localProxy.latitude = elem["Latitude"]
        localProxy.longitude = elem["Longitude"]
        localProxy.metroCode = elem["MetroCode"]
        localProxy.faults = elem["Faults"]
        localProxy.faultsMax = elem["FaultsMax"]
        localProxy.categoryId = elem["Category_Id"]
        localProxy.limits = elem["Limits"]
        localProxy.description = elem["Description"]
        localProxy.cDate = elem["CDate"]
        localProxy.uDate = elem["UDate"]
        ret.append(localProxy)
    return ret
