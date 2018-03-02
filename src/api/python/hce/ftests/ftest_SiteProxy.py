'''
Created on Dec 1, 2015

@author: scorp
'''
import unittest
import copy
import ppath
from dc_crawler.ProxyResolver import ProxyResolver

class FakeDBWrapper(object):

  TEMPL_ELEMENT = {"Site_Id": None, "Host": None, "Domains": None, "Priority": None, "State": None, "Limits": None}
  TYPE = 0
  

  def customRequest(self, query, dbName):
    ret = []
    if self.TYPE == 0:
      elem = self.TEMPL_ELEMENT
      elem["Site_Id"] = "1"
      elem["Host"] = "ibm.com:9090"
      elem["Domains"] = None
      elem["Priority"] = 1
      elem["State"] = 1
      elem["Limits"] = None
      ret.append(copy.deepcopy(elem))
      elem["Site_Id"] = "1"
      elem["Host"] = "intel.com:11"
      elem["Domains"] = ["*"]
      elem["Priority"] = 2
      elem["State"] = 1
      elem["Limits"] = [10, 10]
      ret.append(copy.deepcopy(elem))
      elem["Site_Id"] = "1"
      elem["Host"] = "intel.com:22"
      elem["Domains"] = ["mazda.com"]
      elem["Priority"] = 1
      elem["State"] = 1
      elem["Limits"] = [10, 10]
      ret.append(copy.deepcopy(elem))
      elem["Site_Id"] = "1"
      elem["Host"] = "intel.com:44"
      elem["Domains"] = ["mazda.com"]
      elem["Priority"] = 0
      elem["State"] = 1
      elem["Limits"] = [1, 2, 3]
      ret.append(copy.deepcopy(elem))
    elif self.TYPE == 1:
      elem = self.TEMPL_ELEMENT
      elem["Site_Id"] = "1"
      elem["Host"] = "ibm.com:9090"
      elem["Domains"] = None
      elem["Priority"] = 1
      elem["State"] = 1
      elem["Limits"] = None
      ret.append(copy.deepcopy(elem))
      elem["Site_Id"] = "1"
      elem["Host"] = "intel.com:11"
      elem["Domains"] = ["*"]
      elem["Priority"] = 1
      elem["State"] = 1
      elem["Limits"] = [10, 10, 2]
      ret.append(copy.deepcopy(elem))
      elem["Site_Id"] = "1"
      elem["Host"] = "intel.com:22"
      elem["Domains"] = ["mazda.com"]
      elem["Priority"] = 1
      elem["State"] = 1
      elem["Limits"] = [10, 10, 2]
      ret.append(copy.deepcopy(elem))
      elem["Site_Id"] = "1"
      elem["Host"] = "intel.com:44"
      elem["Domains"] = ["www.latimes.com"]
      elem["Priority"] = 1
      elem["State"] = 1
      elem["Limits"] = [11, 12, 13]
      ret.append(copy.deepcopy(elem))
    return ret


class Test(unittest.TestCase):


  def test_01_ProxySimple(self):
    dbWrapper = FakeDBWrapper()
    siteId = "1"
    url = "http://www.latimes.com/local/lanow/la-me-ln-kamala-harris-lawsuit-car-donation-charities-20151201-story.html"
    siteProperties = {"HTTP_PROXY_HOST": "host.com", "HTTP_PROXY_PORT": "8989", "USER_PROXY": "{}"}
    proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
    result = proxyResolver.getProxy()
    self.assertTrue(result == ("host.com", "8989"))


  def test_02_ProxyPropertyMode(self):
    dbWrapper = FakeDBWrapper()
    siteId = "1"
    url = "http://www.latimes.com/local/lanow/la-me-ln-kamala-harris-lawsuit-car-donation-charities-20151201-story.html"
    siteProperties = {"USER_PROXY": "{\"source\": 0, \"file_path\": \"file11.json\", \"proxies\": " +
                      "{\"toxic.com:9000\" : {\"host\": \"toxic.com:9000\", \"domains\":[\"www.latimes.com\"]," +
                      "\"priority\": 44, \"limits\": null}, " +
                      "\"proxic.com:9000\" : {\"host\": \"proxic.com:9000\", \"domains\":[\"*\"]," +
                      "\"priority\": 11, \"limits\": null}, " +
                      "\"nosic.com:9000\" : {\"host\": \"nosic.com:9000\", \"domains\":[\"www.latimes.com\"]," +
                      "\"priority\": 1, \"limits\": null}}}"
                      }
    proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
    result = proxyResolver.getProxy()
    self.assertTrue(result == ("nosic.com", "9000"))


  def test_03_ProxyDBMode(self):
    dbWrapper = FakeDBWrapper()
    siteId = "1"
    url = "http://www.latimes.com/local/lanow/la-me-ln-kamala-harris-lawsuit-car-donation-charities-20151201-story.html"
    siteProperties = {"USER_PROXY": "{\"source\": 1, \"file_path\": \"file11.json\", \"proxies\": {}}"}
    proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
    result = proxyResolver.getProxy()
    self.assertTrue(result == ("ibm.com", "9090"))


  def test_04_ProxyLimits(self):
    dbWrapper = FakeDBWrapper()
    dbWrapper.TYPE = 1
    siteId = "1"
    url = "http://www.latimes.com/local/lanow/la-me-ln-kamala-harris-lawsuit-car-donation-charities-20151201-story.html"
    siteProperties = {"USER_PROXY": "{\"source\": 1, \"file_path\": \"file22.json\", \"proxies\": {}}"}
    proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
    result = proxyResolver.getProxy()
    self.assertTrue(result == ("intel.com", "11"))


  def test_05_ProxyLimitsExtend(self):
    dbWrapper = FakeDBWrapper()
    dbWrapper.TYPE = 1
    siteId = "1"
    url = "http://www.latimes.com/local/lanow/la-me-ln-kamala-harris-lawsuit-car-donation-charities-20151201-story.html"
    siteProperties = {"USER_PROXY": "{\"source\": 1, \"file_path\": \"file33.json\", \"proxies\": {}}"}
    proxyResolver = ProxyResolver(siteProperties, dbWrapper, siteId, url)
    result = proxyResolver.getProxy()
    self.assertTrue(result == ("intel.com", "44"))


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
