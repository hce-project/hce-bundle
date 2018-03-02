# coding: utf-8  # pylint: disable-all

"""@package algorithms
  @file MetricTagsCount.py
  @author scorp <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2013 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
  """

import logging

import app.Consts as APP_CONSTS
import app.Utils as Utils  # pylint: disable=F0401
from BaseMetric import BaseMetric

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The MetricTagsCount class, class that implements metric counters for tags Metric
#
class MetricTagsCount(BaseMetric):


  # # class constructor
  #
  # @param name - metric's name
  def __init__(self, names):
    super(MetricTagsCount, self).__init__(names)


  # # precalculate makes MetricTagsCount metrics precalculating
  #
  # @param result - param, that content calculating data in common format
  # @return precalculated data in common format
  def precalculate(self, result, metricName):
    ret = {"count": 0, "percent": 0}
    for key in result.tags:
      if result.isTagFilled(key):
        ret["count"] += 1
    if len(result.tags) > 0:
      ret["percent"] = ret["count"] * 100 / len(result.tags)
    ret = self.retForMultiNames(ret, metricName)
    return ret
