# coding: utf-8  # pylint: disable-all

"""@package algorithms
  @file BaseMetric.py
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

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The BaseMetric class, class that implements common methods for all Metrics classes
#
class BaseMetric(object):


  # # class constructor
  #
  # @param name - metric's name
  def __init__(self, names):
    self.names = names


  # # retForMultiNames return simple value for multi-returns
  #
  # @param retDict - incoming return dict with 2 mandatory keys "count" and "persent"
  # @param metricName - neededs metric name
  # @return - return simple return element
  def retForMultiNames(self, retDict, metricName):
    ret = 0
    if len(self.names) > 0 and metricName == self.names[0]:
      ret = retDict["count"]
    elif len(self.names) > 1 and metricName == self.names[1]:
      ret = retDict["percent"]
    else:
      ret = 0
    return ret


  # # sortElementsByMetric resort incoming elements list, by precalculated metric data
  #
  # @param elements - incoming elements
  # @param metricParam - name of using metric param
  # @return - return resorted elements
  def sortElementsByMetric(self, elements, metricName):
    localElemsWithMetric = []
    localElemsWithoutMetric = []
    for element in elements:
      if hasattr(element, "metrics") and metricName in element.metrics and metricName in self.names:
        localElemsWithMetric.append(element)
      else:
        localElemsWithoutMetric.append(element)
    if len(localElemsWithMetric) > 0:
      localElemsWithMetric.sort(key=lambda x: x.metrics[metricName], reverse=True)
    ret = localElemsWithMetric + localElemsWithoutMetric
    return ret


  # # selectElementsByMetric selects elements that fit for metric limit value
  #
  # @param elements - incoming elements
  # @param metricParam - name of using metric param
  # @param metricParamLimit - limit value of using metric param
  # @return - return reselected elements
  def selectElementsByMetric(self, elements, metricName, metricLimitMax, metricLimitMin):
    ret = []
    for element in elements:
      if hasattr(element, "metrics") and metricName in element.metrics and metricName in self.names:
        if element.metrics[metricName] >= metricLimitMin:
          if metricLimitMax is None or element.metrics[metricName] <= metricLimitMax:
            ret.append(element)
    return ret
