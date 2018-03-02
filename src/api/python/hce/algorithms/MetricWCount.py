# coding: utf-8  # pylint: disable-all

"""@package algorithms
  @file MetricWCount.py
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
import types
import re
import unicodedata
from BaseMetric import BaseMetric

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The MetricContentSize class, class that implements metric counters for words count Metric
#
class MetricWCount(BaseMetric):


  CHAR_CATEGORIES_LIST = ['Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nd', 'Nl', 'No']
  CHAR_NOT_LATIN_LIST = ['Lt', 'Lm', 'Lo']
  RE_SPLITTER = '\s'
  MIN_LATIN_WORD_LEN = 3

  W_TYPE_LATIN = 0
  W_TYPE_NOT_LATIN = 1
  W_TYPE_NUMBER = 2
  W_TYPE_BAD = 3


  # # class constructor
  #
  # @param name - metric's name
  def __init__(self, names):
    super(MetricWCount, self).__init__(names)


  # # internalCalculating methods makes internal content calculating
  #
  # @param dataDict
  # @param buf
  def internalCalculating(self, dataDict, buf):
    if type(buf) is types.StringType:
      buf = unicode(buf)
    words = re.split(self.RE_SPLITTER, buf, flags=re.LOCALE)
    for word in words:
      wType = self.W_TYPE_LATIN
      for ch in word:
        chCategory = unicodedata.category(ch)
        if chCategory in self.CHAR_CATEGORIES_LIST:
          if chCategory in self.CHAR_NOT_LATIN_LIST:
            wType = self.W_TYPE_NOT_LATIN
        else:
          wType = self.W_TYPE_BAD
          break
      if wType == self.W_TYPE_LATIN and len(word) < self.MIN_LATIN_WORD_LEN:
        wType = self.W_TYPE_BAD
      if wType != self.W_TYPE_BAD:
        dataDict["validWordsCount"] += 1
      dataDict["count"] += 1


  # # precalculate makes words count metrics precalculating
  #
  # @param result - param, that content calculating data in common format
  # @return precalculated data in common format
  def precalculate(self, result, metricName):
    ret = {"count": 0, "percent": 0, "validWordsCount": 0}
    for key in result.tags:
      if type(result.tags[key]) is types.DictType and "data" in result.tags[key]:
        if type(result.tags[key]["data"]) in types.StringTypes:
          self.internalCalculating(ret, result.tags[key]["data"])
        elif type(result.tags[key]["data"]) is types.ListType:
          for buf in result.tags[key]["data"]:
            self.internalCalculating(ret, buf)
    if ret["count"] > 0:
      ret["percent"] = ret["validWordsCount"] * 100 / ret["count"]
    ret = self.retForMultiNames(ret, metricName)
    return ret
