'''
Created on Mar 18, 2015

@author: scorp
'''
import ppath

import unittest
import ConfigParser
import os
try:
  import cPickle as pickle
except ImportError:
  import pickle
import dc_crawler.DBTasksWrapper as DBTasksWrapper
from app.Filters import Filters

CMD_SNEW_FILTERS = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new_filters.dat")


filtersTmp1 = [{"Pattern" : "%ContentType%", "Subject" : "text/xml", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 1},
           {"Pattern" : "%ContentType%", "Subject" : "text/xml", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_AFTER_DOM, "Action" : 2},
           {"Pattern" : "%ContentType%", "Subject" : "text/html", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 3},
           {"Pattern" : "%ContentType%", "Subject" : "application/pdf", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 4},
           {"Pattern" : "%ContentType%", "Subject" : "text/xml", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 5},
           {"Pattern" : "%url%", "Subject" : "text/xml", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 6},
           {"Pattern" : "%url% and %ddl%", "Subject" : "text/xml and text/xml", "OperationCode" : Filters.OC_RE,
            "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 7},
           {"Pattern" : "%url% and %redirect%", "Subject" : "text/xml and text/xml",
            "OperationCode" : Filters.OC_RE, "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 8}]

class Test(unittest.TestCase):

  CFG_NAME = "../../ini/db-task.ini"
  CONST_SITE_ID = "65f5d740b25e73d4c63d9f06e8f15b90"

  def setUp(self):
    cfgParser = ConfigParser.ConfigParser()
    cfgParser.read(self.CFG_NAME)
    #self.wrapper = DBTasksWrapper.DBTasksWrapper(cfgParser)


  def tearDown(self):
    pass


  def execCommand(self, command, step):
    obj = None
    print ">>> Start = " + str(command)
    fd = os.popen(command)
    if fd:
      localStr = fd.read()
      fd.close()
      print ">>> Finish = " + str(command)
      try:
        obj = pickle.loads(localStr)
      except EOFError:
        self.assertTrue(False, "Step%s >>> Invalid return data" % str(step))
    else:
      print ">>> Bad FD " +  + str(command)
    return obj


  def commonAssert_01(self, localFilters):
    value = {"ContentType": "text/xml", "url": "text/xml", "MDd5" : "test/xml"}

    result = localFilters.filterAll(Filters.STAGE_AFTER_DOM, value, Filters.LOGIC_AND)
    self.assertTrue(result == [True], ">>> Test01_A BAD")
    result = localFilters.filterAll(Filters.STAGE_AFTER_DOM, value, Filters.LOGIC_OR)
    self.assertTrue(result == [2], ">>> Test01_B BAD")
    
    
  def commonAssert_02(self, localFilters):
    value = {"ContentType": "application/dat", "url": "text/xml", "MDd5" : "test/xml"}

    result = localFilters.filterAll(Filters.STAGE_AFTER_DOM_PRE, value, Filters.LOGIC_AND)
    self.assertTrue(result == [], ">>> Test02_A BAD")
    result = localFilters.filterAll(Filters.STAGE_AFTER_DOM_PRE, value, Filters.LOGIC_OR)
    self.assertTrue(result == [], ">>> Test02_B BAD")


  def commonAssert_03(self, localFilters):
    value = {"ContentType": "text/xml", "url": "text/xml", "MDd5" : "test/xml"}

    result = localFilters.filterAll(Filters.STAGE_BEFORE_DOM_PRE, value, Filters.LOGIC_AND)
    self.assertTrue(result == [False], ">>> Test03_A BAD")
    result = localFilters.filterAll(Filters.STAGE_BEFORE_DOM_PRE, value, Filters.LOGIC_OR)
    self.assertTrue(result == [1, -4, 5, 6], ">>> Test03_B BAD")
  
    result = localFilters.filterAll(Filters.STAGE_COLLECT_URLS, value, Filters.LOGIC_AND)
    self.assertTrue(result == [], ">>> Test03_C BAD")
    result = localFilters.filterAll(Filters.STAGE_COLLECT_URLS, value, Filters.LOGIC_OR)
    self.assertTrue(result == [], ">>> Test03_D BAD")


  def commonAssert_04(self, localFilters):
    value = {"ContentType": "text/html", "url": "text/xml", "ddl" : "test/xml"}
    
    result = localFilters.filterAll(Filters.STAGE_AFTER_PROCESSOR, value, Filters.LOGIC_AND)
    self.assertTrue(result == [False], ">>> Test04_A BAD")
    result = localFilters.filterAll(Filters.STAGE_AFTER_PROCESSOR, value, Filters.LOGIC_OR)
    self.assertTrue(result == [3, -7, -8], ">>> Test04_B BAD")


  def test_01(self):
    localFilters = Filters(filtersTmp1)
    self.commonAssert_01(localFilters)

  def test_02(self):
    localFilters = Filters(filtersTmp1)
    self.commonAssert_02(localFilters)


  def test_03(self):
    localFilters = Filters(filtersTmp1)
    self.commonAssert_03(localFilters)


  def test_04(self):
    localFilters = Filters(filtersTmp1)
    self.commonAssert_04(localFilters)

  
  '''
  def test_05(self):
    self.execCommand(CMD_SNEW_FILTERS, 0)
    localFilters = Filters(None, self.wrapper, self.CONST_SITE_ID)
    self.commonAssert_01(localFilters)


  def test_06(self):
    localFilters = Filters(None, self.wrapper, self.CONST_SITE_ID)
    self.commonAssert_02(localFilters)


  def test_07(self):
    localFilters = Filters(None, self.wrapper, self.CONST_SITE_ID)
    self.commonAssert_03(localFilters)


  def test_08(self):
    localFilters = Filters(None, self.wrapper, self.CONST_SITE_ID)
    self.commonAssert_04(localFilters)
  '''


  def test_09(self):
    localUrl = "http://pbn.com/Brown-and-URI-slip-Bryant-and-RIC-gain-in-2015-08-college-rankings,99822"
    localFilters = [{"Pattern" : "http://pbn.com/(.*)-%CUR_YEAR_FULL%-%CUR_MONTH_FULL%(.*)", "Subject" : localUrl,
            "OperationCode" : Filters.OC_RE, "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 1},
                    {"Pattern" : "http://pbn.com/(.*)-%CUR_YEAR_FULL%-%CUR_MONTH_FULL%(.*)", "Subject" : localUrl,
            "OperationCode" : Filters.OC_RE, "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 2},
                    {"Pattern" : "http://pbn.com/(.*)-%ANY_DATA%(.*)", "Subject" : localUrl,
            "OperationCode" : Filters.OC_RE, "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 3},
                    {"Pattern" : "%DEPTH%", "Subject" : "10",
            "OperationCode" : Filters.OC_EQMORE, "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 4},]
    localFilters = Filters(localFilters)

    value = {"ContentType": "text/xml", "url": "text/xml", "CUR_YEAR_FULL": "2015", "CUR_MONTH_FULL": "08",
             "DEPTH": "1"}

    result = localFilters.filterAll(Filters.STAGE_AFTER_PROCESSOR, value, Filters.LOGIC_OR)
    print result


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()