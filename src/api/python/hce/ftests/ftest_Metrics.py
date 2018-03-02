#coding: utf-8
'''
Created on Nov 6, 2015

@author: scorp
'''
import ppath
import unittest
import copy
from app.Metrics import Metrics
from dc_processor.scraper_result import Result

class Test(unittest.TestCase):


  def __init__(self, methodName='runTest'):
    unittest.TestCase.__init__(self, methodName)
    Metrics.fillMetricModulesList()
    self.result = Result(None, "a1")
    self.fillResultData()


  def fillResultData(self):
    data = {}
    data["data"] = ["", u"test1 43 35../ 3./утка"]
    data["name"] = "tagA"
    data["xpath"] = "//"
    data["extractor"] = ""
    self.result.tags[data["name"]] = data
    data = {}
    data["data"] = ["", u"test1 43 35../ 3./утка", u"FINISH him. !!! ehf"]
    data["name"] = "tagB"
    data["xpath"] = "//"
    data["extractor"] = ""
    self.result.tags[data["name"]] = data
    data = {}
    data["data"] = [""]
    data["name"] = "tagC"
    data["xpath"] = "//"
    data["extractor"] = ""
    self.result.tags[data["name"]] = data


  def test_01_MetricInit(self):
    print ">>> testMetricInit start"
    self.assertTrue(len(Metrics.AVAILABLE_METRICS) == 6, ">>> Metrics.AVAILABLE_METRICS Size != 6")
    self.assertTrue("METRIC_TAGS_COUNT" in Metrics.AVAILABLE_METRICS,
                    ">>> METRIC_TAGS_COUNT not in Metrics.AVAILABLE_METRICS")
    self.assertTrue("METRIC_TAGS_COUNT_PERCENT" in Metrics.AVAILABLE_METRICS,
                    ">>> METRIC_TAGS_COUNT_PERCENT not in Metrics.AVAILABLE_METRICS")
    self.assertTrue("METRIC_WORDS_COUNT" in Metrics.AVAILABLE_METRICS,
                    ">>> METRIC_WORDS_COUNT not in Metrics.AVAILABLE_METRICS")
    self.assertTrue("METRIC_WORDS_COUNT_PERCENT" in Metrics.AVAILABLE_METRICS,
                    ">>> METRIC_WORDS_COUNT_PERCENT not in Metrics.AVAILABLE_METRICS")
    self.assertTrue("METRIC_CONTENT_SIZE" in Metrics.AVAILABLE_METRICS,
                    ">>> METRIC_CONTENT_SIZE not in Metrics.AVAILABLE_METRICS")
    self.assertTrue("METRIC_CONTENT_SIZE_PERCENT" in Metrics.AVAILABLE_METRICS,
                    ">>> METRIC_CONTENT_SIZE_PERCENT not in Metrics.AVAILABLE_METRICS")


  def test_02_MetricTagsCount(self):
    print ">>> test_02_MetricTagsCount start"
    metricResult = {"METRIC_TAGS_COUNT" : None, "METRIC_TAGS_COUNT_PERCENT" : None}
    Metrics.metricsPrecalculate(metricResult, self.result)
    self.assertTrue(metricResult["METRIC_TAGS_COUNT"] == 2, ">>> test_02_MetricTagsCount METRIC_TAGS_COUNT != 2")
    self.assertTrue(metricResult["METRIC_TAGS_COUNT_PERCENT"] == 66,
                    ">>> test_02_MetricTagsCount METRIC_TAGS_COUNT_PERCENT != 66")


  def test_03_MetricContentSize(self):
    print ">>> test_03_MetricContentSize start"
    metricResult = {"METRIC_TAGS_COUNT" : None, "METRIC_TAGS_COUNT_PERCENT" : None,
                    "METRIC_WORDS_COUNT": None, "METRIC_WORDS_COUNT_PERCENT": None}
    Metrics.metricsPrecalculate(metricResult, self.result)
    self.assertTrue(metricResult["METRIC_WORDS_COUNT"] > 0, ">>> test_03_MetricContentSize METRIC_WORDS_COUNT <= 0")
    self.assertTrue(metricResult["METRIC_WORDS_COUNT_PERCENT"] > 0 and \
                    metricResult["METRIC_WORDS_COUNT_PERCENT"] < 100,
                    ">>> test_03_MetricContentSize METRIC_WORDS_COUNT_PERCENT <= 0 or > 100")


  def test_04_MetricWCount(self):
    print ">>> test_04_MetricWCount start"
    metricResult = {"METRIC_TAGS_COUNT" : None, "METRIC_TAGS_COUNT_PERCENT" : None,
                    "METRIC_WORDS_COUNT": None, "METRIC_WORDS_COUNT_PERCENT": None,
                    "METRIC_CONTENT_SIZE": None, "METRIC_CONTENT_SIZE_PERCENT": None}
    Metrics.metricsPrecalculate(metricResult, self.result)
    self.assertTrue(metricResult["METRIC_CONTENT_SIZE"] > 0, ">>> test_04_MetricWCount METRIC_CONTENT_SIZE <= 0")
    self.assertTrue(metricResult["METRIC_CONTENT_SIZE_PERCENT"] > 0 and \
                    metricResult["METRIC_CONTENT_SIZE_PERCENT"] < 100,
                    ">>> test_04_MetricWCount METRIC_CONTENT_SIZE_PERCENT <= 0 or > 100")


  def test_05_MetricWCountSort(self):
    print ">>> test_05_MetricWCountSort start"
    resutlList = []
    resutlList.append(Result(None, "a0"))
    resutlList.append(Result(None, "a1"))
    resutlList.append(Result(None, "a2"))
    resutlList.append(Result(None, "a3"))
    resutlList.append(Result(None, "a4"))
    metricResult = {"METRIC_WORDS_COUNT": None, "METRIC_WORDS_COUNT_PERCENT": None,
                    "METRIC_CONTENT_SIZE": None, "METRIC_CONTENT_SIZE_PERCENT": None}
    resutlList[0].metrics = copy.deepcopy(metricResult)
    resutlList[1].metrics = copy.deepcopy(metricResult)
    metricResult["METRIC_TAGS_COUNT"] = None
    metricResult["METRIC_TAGS_COUNT_PERCENT"] = None
    resutlList[2].metrics = copy.deepcopy(metricResult)
    metricResult["METRIC_TAGS_COUNT"] = 10
    metricResult["METRIC_TAGS_COUNT_PERCENT"] = 5
    resutlList[3].metrics = copy.deepcopy(metricResult)
    metricResult["METRIC_TAGS_COUNT"] = 2
    metricResult["METRIC_TAGS_COUNT_PERCENT"] = 5
    resutlList[4].metrics = copy.deepcopy(metricResult)
    for elem in resutlList:
      print str(elem.resId)
    print ">>>>>>>>>>>><<<<<<<<<<<<"
    newElems = Metrics.sortElementsByMetric(resutlList, "METRIC_TAGS_COUNT")
    for elem in newElems:
      print str(elem.resId)


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
