'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dc_db.BaseTask import BaseTask
# from dc_db.ProxyNewTask import ProxyNewTask
import dc_db.Constants as Constants
from dtm.EventObjects import GeneralResponse
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # ProxyUpdateTask Class, implements Proxy Update task functionality
#
class ProxyUpdateTask(BaseTask):


  # #Class constructor
  #
  def __init__(self):
    super(ProxyUpdateTask, self).__init__()


  # #make all necessary actions to update Proxies in mysql db
  #
  # @param urls list of ProxyUpdate objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, proxyUpdates, queryCallback):
    generalResponse = GeneralResponse()
    for proxyUpdate in proxyUpdates:
      status = False
#       if ProxyNewTask.lookProxyInDB(proxyUpdate, queryCallback):
      if self.updateProxy(proxyUpdate, queryCallback):
        status = True
      generalResponse.statuses.append(status)
    return generalResponse


  # #Method updateProxy updates proxy record in the db
  #
  # @param proxy - incoming proxy object
  # @param queryCallback ueryCallback function for queries execution
  # @return bool value, is current updateProxy was successful or wasn't
  def updateProxy(self, proxyUpdate, queryCallback):
    ret = False

    fields, values = Constants.getFieldsValuesTuple(proxyUpdate, Constants.ProxyTableDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values, Constants.proxyExcludeList)
    if fieldValueString is not None and fieldValueString != "":
      PROXY_UPDATE_TEMPLATE = "UPDATE `sites_proxy` SET %s WHERE `Site_Id` = '%s' AND `Host` = '%s'"
      query = PROXY_UPDATE_TEMPLATE % (fieldValueString, proxyUpdate.siteId, proxyUpdate.host)

      print query
      queryCallback(query, Constants.PRIMARY_DB_ID)
      ret = True
    return ret
