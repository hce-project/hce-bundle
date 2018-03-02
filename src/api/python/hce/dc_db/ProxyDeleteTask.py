'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import copy
from dc_db.BaseTask import BaseTask
from dc_db.ProxyStatusTask import ProxyStatusTask
import dc_db.Constants as Constants
from dtm.EventObjects import GeneralResponse
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # ProxyDeleteTask Class, implements Proxy Delete task functionality
#
class ProxyDeleteTask(BaseTask):


  # #Class constructor
  #
  def __init__(self):
    super(ProxyDeleteTask, self).__init__()


  # #make all necessary actions to delete Proxies from mysql db
  #
  # @param proxyDeletes of ProxyDelete objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, proxyDeletes, queryCallback):
    generalResponse = GeneralResponse()
    for proxyDelete in proxyDeletes:
      localProxyDeletes = []
      if proxyDelete.siteId is None or proxyDelete.host is None and proxyDelete.criterions is not None:
        result = ProxyStatusTask.execCriterion(proxyDelete, queryCallback, proxyDelete.siteId)
        for elem in result:
          localProxy = copy.deepcopy(proxyDelete)
          if localProxy.siteId is None:
            localProxy.siteId = elem["Site_Id"]
          if localProxy.host is None:
            localProxy.host = elem["Host"]
          localProxyDeletes.append(localProxy)
      else:
        localProxyDeletes.append(proxyDelete)
      logger.debug(">>> len(localProxyStatuses) = " + str(len(localProxyDeletes)))
      for localProxy in localProxyDeletes:
        if self.deleteProxy(localProxy, queryCallback):
          generalResponse.statuses.append(True)
        else:
          generalResponse.statuses.append(False)
    return generalResponse


  # #deleteProxy deletes one proxy record from DB
  #
  # @param localProxy - incoming ProxyDelete object
  # @param queryCallback function for queries execution
  # @return True
  def deleteProxy(self, localProxy, queryCallback):
    DELETE_PROXY_TEMPLATE = "DELETE FROM `sites_proxy` WHERE `Site_Id` = '%s' AND `Host` = '%s'"
    query = DELETE_PROXY_TEMPLATE % (localProxy.siteId, localProxy.host)
    queryCallback(query, Constants.PRIMARY_DB_ID)
    return True
