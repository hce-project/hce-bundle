# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
It's wrapper proxy functional with DB.

@package: dc_crawler
@file DBProxyWrapper.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import dbi.EventObjects
from dc.EventObjects import ProxyStatus
import app.Utils as Utils
import app.SQLCriterions

logger = Utils.MPLogger().getLogger()

class DBProxyWrapper(object):

  # #Constants used in class
  DEFAULT_LIMIT_VALUE = 50
  DEFAULT_SITE_ID_VALUE = '*'

  PROXY_STATE_DISABLED = 0
  PROXY_STATE_ENABLED = 1

  # # Constants template sql criterion
  TEMPLATE_WHERE_SELECT = "`State` = %s AND (`Site_Id` = '%s' OR `Site_Id` = '%s')"
  TEMPLATE_ORDER_SELECT = "`Priority`"

  PROXY_UPDATE_FAULTS_QUERY = "UPDATE `sites_proxy` SET `Faults`=`Faults` + %s WHERE `Host` = '%s'"
  PROXY_DISABLE_QUERY = "UPDATE `sites_proxy` SET `State`= '%s' WHERE `Host` = '%s' AND `FaultsMax` <> '0' \
  AND `Faults` >= `FaultsMax`"

  PROXY_DB_NAME = "dc_sites"

  # # Initialization of class
  #
  # @param dbWrapper - database access wrapper
  def __init__(self, dbWrapper):
    self.dbWrapper = dbWrapper


  # # get active proxies list
  #
  # @param siteId - site ID value for request
  # @param limitValue - value of limit for request
  # @return list of Proxy instances
  def getEnaibledProxies(self, siteId=DEFAULT_SITE_ID_VALUE, limitValue=DEFAULT_LIMIT_VALUE):
    # variable for result
    ret = None

    criterions = {}
    criterions[app.SQLCriterions.CRITERION_WHERE] = self.TEMPLATE_WHERE_SELECT % \
      (self.PROXY_STATE_ENABLED, str(siteId), self.DEFAULT_SITE_ID_VALUE)
    criterions[app.SQLCriterions.CRITERION_LIMIT] = str(limitValue)
    criterions[app.SQLCriterions.CRITERION_ORDER] = self.TEMPLATE_ORDER_SELECT

    proxyStatus = ProxyStatus(siteId=siteId, host=None, criterions=criterions)
    affectDB = self.dbWrapper.affect_db
    self.dbWrapper.affect_db = True
    ret = self.dbWrapper.proxyStatus(proxyStatus)
    self.dbWrapper.affect_db = affectDB

    return ret


  # # add faults to counter proxy state
  #
  # @param siteId - site ID value for request
  # @param proxyName - proxy host name
  # @param incrementSize - value for increment of faults counter
  # @return - None
  def addFaults(self, proxyName, incrementSize=1):
    if proxyName is not None:
      affectDB = self.dbWrapper.affect_db
      self.dbWrapper.affect_db = True

      # increment faults counter
      query = self.PROXY_UPDATE_FAULTS_QUERY % (incrementSize, proxyName)
      self.dbWrapper.customRequest(query, self.PROXY_DB_NAME, dbi.EventObjects.CustomRequest.SQL_BY_NAME)

      # disable proxy if necessary (overlimits max allowed value)
      query = self.PROXY_DISABLE_QUERY % (self.PROXY_STATE_DISABLED, proxyName)
      self.dbWrapper.customRequest(query, self.PROXY_DB_NAME, dbi.EventObjects.CustomRequest.SQL_BY_NAME)

      self.dbWrapper.affect_db = affectDB
