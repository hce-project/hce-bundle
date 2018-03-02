"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file ContentCheck.py
@author scorp <developers.hce@gmail.com>
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import base64
import json
import collections
from app.Metrics import Metrics
import app.Utils as Utils  # pylint: disable=F0401

TmpObj = collections.namedtuple('TmpObj', 'metrics')

logger = Utils.MPLogger().getLogger()


# #The ContentCheck class, used for content related metrics, used in some modules like RTCFinalizer
#
class ContentCheck(object):

  CHECK_TYPE_SIMPLE = 0
  CHECK_TYPE_OR = 1
  CHECK_TYPE_AND = 2


  # # class constructor
  #
  def __init__(self):
    pass


  # # lookMetricsinContent static method, which finds metric structure in incoming processed content
  # (field of urlPutObj)
  #
  # @param urlPutObj - incoming urlPutObj
  # @return - bool value, is metric struct available or isn't
  @staticmethod
  def lookMetricsinContent(urlPutObj):
    ret = False
    try:
      dataBuf = base64.b64decode(urlPutObj.putDict["data"])
      if dataBuf is not None:
        dataElem = json.loads(dataBuf)
        if dataElem is not None and len(dataElem) > 0 and "metrics" in dataElem[0]:
          metricsBuf = dataElem[0]["metrics"]
          metrics = json.loads(metricsBuf)
          if metrics is not None and isinstance(metrics, dict):
            ret = True
    except Exception as excp:
      logger.debug(">>> Wrong content checking=" + str(excp))
    return ret


  # # checkUrlObj method check tagsCount, as urlObj field, with static value
  #
  # @param urlObj - incoming urlObj onject
  # @param checkType - check's type
  # @return - bool value, result of check
  def checkUrlObj(self, urlObj, checkType=CHECK_TYPE_SIMPLE):
    ret = True
    if checkType == self.CHECK_TYPE_SIMPLE:
      if urlObj.tagsCount <= 3:
        ret = False
    return ret


  # # checkUrlPutObj method check content by incoming metrics
  #
  # @param urlPutObj - incoming urlPutObj onject
  # @param checkType - check's type
  # @param metricProperty - incoming json with metric's limits for checking
  # @return - bool value, result of check
  def checkUrlPutObj(self, urlPutObj, checkType=CHECK_TYPE_SIMPLE, metricProperty=None):
    ret = True
    useMetricProperty = False
    try:
      dataBuf = base64.b64decode(urlPutObj.putDict["data"])
      if dataBuf is not None:
        dataElem = json.loads(dataBuf)
        if dataElem is not None:
          Metrics.fillMetricModulesList()
          metricsBuf = dataElem[0]["metrics"]
          metrics = json.loads(metricsBuf)
          if metrics is not None and isinstance(metrics, dict):
            localList = []
            localList.append(TmpObj(metrics=metrics))
            resObjs = []
            if metricProperty is not None:
              try:
                localMetricProperty = json.loads(metricProperty)
                for elem in localMetricProperty["contentMetrics"]:
                  localResObjs = Metrics.selectElementsByMetric(localList, elem["NAME"], elem["LIMIT_MAX"],
                                                                elem["LIMIT_MIN"])
                  if localMetricProperty["type"] == self.CHECK_TYPE_SIMPLE:
                    resObjs = localResObjs
                    break
                  elif localMetricProperty["type"] == self.CHECK_TYPE_OR:
                    resObjs += localResObjs
                  elif localMetricProperty["type"] == self.CHECK_TYPE_AND:
                    if len(localResObjs) == 0:
                      resObjs = localResObjs
                      break
                useMetricProperty = True
              except Exception as excp:
                logger.debug(">>> Wrong metric property = " + str(excp))
            if not useMetricProperty:
              if checkType == self.CHECK_TYPE_SIMPLE:
                resObjs = Metrics.selectElementsByMetric(localList, "TAGS_NUMBER", None, 3)
            if len(resObjs) == 0:
              ret = False
    except Exception as excp:
      logger.debug(">>> ContentCheck.checkUrlPutObj something wrong, err=" + str(excp))
    return ret
