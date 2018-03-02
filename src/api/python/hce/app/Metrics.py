"""@package app
  @file Metrics.py
  @author scorp <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2013 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
  """

import app.Utils as Utils  # pylint: disable=F0401
from algorithms.MetricTagsCount import MetricTagsCount
from algorithms.MetricWCount import MetricWCount
from algorithms.MetricContentSize import MetricContentSize

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The Metrics static class, is a interface for Metrics precalculating and estimation
#
class Metrics(object):

  AVAILABLE_METRICS = {}


  # # fillMetricModulesList internam method, that fills Metrics dict of one Metric class instance
  #
  # @param metricClass - type of metrics class
  # @param names - metric names, asssotiated with class
  @staticmethod
  def addMetricClassMetrics(metricClass, names):
    metricInstance = metricClass(names)
    for name in metricInstance.names:
      Metrics.AVAILABLE_METRICS[name] = metricInstance


  # # fillMetricModulesList fills dict of available Metrics objects
  #
  # @param additionFiller - incoming callback function, which extends of AVAILABLE_METRICS field with user metrics
  @staticmethod
  def fillMetricModulesList(additionFiller=None):
    Metrics.addMetricClassMetrics(MetricTagsCount, ["TAGS_NUMBER", "TAGS_NUMBER_PERCENT"])
    Metrics.addMetricClassMetrics(MetricWCount, ["WORDS_NUMBER", "WORDS_NUMBER_PERCENT"])
    Metrics.addMetricClassMetrics(MetricContentSize, ["CONTENT_SIZE", "CONTENT_SIZE_PERCENT"])
    if additionFiller is not None:
      additionFiller(Metrics.AVAILABLE_METRICS)


  # # metricsPrecalculate makes metrics precalculate and fills incoming requestMetrics dics
  #
  # @param requestMetrics - incoming dcis with needed metric names
  # @param result - param, that content calculating data in common format
  @staticmethod
  def metricsPrecalculate(requestMetrics, result):
    for key in requestMetrics:
      if key in Metrics.AVAILABLE_METRICS:
        try:
          requestMetrics[key] = Metrics.AVAILABLE_METRICS[key].precalculate(result, key)
        except Exception as excp:
          logger.debug(">>> Somthing wrong in metric precalculating, err = " + str(excp) + " key = " + str(key))
      else:
        logger.debug(">>> metricsPrecalculate. No request metric in available metrics dict, metric is = " + str(key))


  # # sortElementsByMetric resort incoming elements list, by precalculated metric data
  #
  # @param elements - incoming elements
  # @param metricName - name of using metric
  # @param metricParam - name of using metric param
  # @return - return resorted elements
  @staticmethod
  def sortElementsByMetric(elements, metricName):
    ret = elements
    if metricName in Metrics.AVAILABLE_METRICS:
      ret = Metrics.AVAILABLE_METRICS[metricName].sortElementsByMetric(elements, metricName)
    else:
      logger.debug(">>> sortElementsByMetric. No request metric in available metrics dict, metric is = " + metricName)
    return ret


  # # selectElementsByMetric selects elements that fit for metric limit value
  #
  # @param elements - incoming elements
  # @param metricName - name of using metric
  # @param metricParam - name of using metric param
  # @param metricParamLimit - limit value of using metric param
  # @return - return reselected elements
  @staticmethod
  def selectElementsByMetric(elements, metricName, metricLimitMax, metricLimitMin):
    ret = elements
    if metricName in Metrics.AVAILABLE_METRICS:
      ret = Metrics.AVAILABLE_METRICS[metricName].selectElementsByMetric(elements, metricName, metricLimitMax,
                                                                         metricLimitMin)
    else:
      logger.debug(">>> selectElementsByMetric. No request metric in available metrics dict, metric is = " + metricName)
    return ret
