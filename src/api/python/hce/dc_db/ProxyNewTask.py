'''
@package: dc_db
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dc_db.BaseTask import BaseTask
import dc_db.Constants as Constants
from dtm.EventObjects import GeneralResponse
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # ProxyNewTask Class, implements Proxy New task functionality
#
class ProxyNewTask(BaseTask):


  # #Class constructor
  #
  def __init__(self):
    super(ProxyNewTask, self).__init__()


  # #Method lookProxyInDB looks current proxy in th db
  #
  # @param proxy - incoming proxy object
  # @param queryCallback ueryCallback function for queries execution
  # @return bool value, is current proxy in db or not
  @staticmethod
  def lookProxyInDB(proxy, queryCallback):
    ret = False
    FETCH_PROXY_SQL = "SELECT * FROM `sites_proxy` WHERE `Site_Id` = '%s' AND `Host` = '%s'"
    query = FETCH_PROXY_SQL % (proxy.siteId, proxy.host)
    res = queryCallback(query, Constants.PRIMARY_DB_ID)
    if hasattr(res, '__iter__') and len(res) > 0 and res[0] is not None:
      ret = True
    return ret


  # #make all necessary actions to add new Proxies into mysql db
  #
  # @param urls list of Proxies objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, proxies, queryCallback):
    ret = GeneralResponse()
    for proxy in proxies:
      if not ProxyNewTask.lookProxyInDB(proxy, queryCallback):
        if self.insertProxy(proxy, queryCallback):
          status = 0
        else:
          status = 1
      else:
        status = 2
      ret.statuses.append(status)
    return ret


  # #Method insertProxy inserts new proxy record in the db
  #
  # @param proxy - incoming proxy object
  # @param queryCallback ueryCallback function for queries execution
  # @return bool value, is current insertProxy was successful or wasn't
  def insertProxy(self, proxy, queryCallback):
    ret = False
    fields, values = Constants.getFieldsValuesTuple(proxy, Constants.ProxyTableDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values)
    if fieldValueString is not None and fieldValueString != "":
      query = Constants.INSERT_COMMON_TEMPLATE % ("sites_proxy", fieldValueString)
      queryCallback(query, Constants.PRIMARY_DB_ID)
      ret = True
    return ret
