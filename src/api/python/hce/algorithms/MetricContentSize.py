# coding: utf-8  # pylint: disable-all

"""@package algorithms
  @file MetricContentSize.py
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
import unicodedata
import types
from BaseMetric import BaseMetric

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The MetricContentSize class, class that implements metric counters for contetn size Metric
#
class MetricContentSize(BaseMetric):

  CHAR_CATEGORIES_LIST = ['Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nd', 'Nl', 'No']

  # # class constructor
  #
  # @param name - metric's name
  def __init__(self, name):
    super(MetricContentSize, self).__init__(name)


  # # internalCalculating methods makes internal content calculating
  #
  # @param dataDict
  # @param buf
  def internalCalculating(self, dataDict, buf):
    if type(buf) is types.StringType:
      buf = unicode(buf)
    if type(buf) is types.UnicodeType:
      for ch in buf:
        if unicodedata.category(ch) in self.CHAR_CATEGORIES_LIST:
          dataDict["validCharsCount"] += 1
        dataDict["count"] += 1


  # # precalculate makes MetricTagsCount metrics precalculating
  #
  # @param result - param, that content calculating data in common format
  # @return precalculated data in common format
  def precalculate(self, result, metricName):
    ret = {"count": 0, "percent": 0, "validCharsCount": 0}
    for key in result.tags:
      if type(result.tags[key]) is types.DictType and "data" in result.tags[key]:
        if type(result.tags[key]["data"]) in types.StringTypes:
          self.internalCalculating(ret, result.tags[key]["data"])
        elif type(result.tags[key]["data"]) is types.ListType:
          for buf in result.tags[key]["data"]:
            self.internalCalculating(ret, buf)
    if ret["count"] > 0:
      ret["percent"] = ret["validCharsCount"] * 100 / ret["count"]
    ret = self.retForMultiNames(ret, metricName)
    return ret
