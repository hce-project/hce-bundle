'''
Created on Nov 28, 2014

@author: scorp
'''
'''
@path ../../hce/anyDir/filtersExample.py
'''
import ppath# pylint: disable=W0611
import copy
from dc_crawler.DBTasksWrapper import DBTasksWrapper

# Example of Filters class interface (without implementation)
class Filters(object):

  STAGE_COLLECT_URLS = 0
  STAGE_BEFORE_DOM_PRE = 1
  STAGE_AFTER_DOM_PRE = 2
  STAGE_AFTER_DOM = 3
  STAGE_AFTER_PROCESSOR = 4
  
  LOGIC_OR = 0
  LOGIC_AND = 1
  
  # Constants for operation codes, implements in Filters.filterAll method body
  OC_RE = 0
  OC_EQ = 1
  OC_NOTEQ = 2
  OC_EQLESS = 3
  OC_EQMORE = 4
  OC_LESS = 5
  OC_MORE = 6
  

  def __init__(self, filters, dbTaskWrapper=None, siteId=None):
    if filters is not None:
      # if filters is not None istantiate self.filters directly
      self.filters = copy.deepcopy(filters)
    else:
      # else fill self.filters from database, using dbTask and siteId params (make SiteStatusTask request)
      # Look CrawlerTask.readSiteFromDB method, return Site.filters field and parse it
      pass


  def filterAll(self, stage, value, logic=LOGIC_AND):
    ret = []
    for localFilter in self.filters:
      if localFilter["Stage"] == stage:
        #   make macroreplacement localFilter["Subject"] by correspond value fron value param dict
        #   apply localFilter["Patter"] for previously getted result (result of macroreplacement)
        if logic == Filters.LOGIC_OR:
          # Return ret = [x1, x2, ... xN] where (xN = +/- localFilter["Action"] value) of applying pattern
          # and +/- depend on corresponds filter for own "Pattern" or not.
          # for example: 
          # we have 3 applying filters with localFilter["Action"] = {3, 4, 5} correspondingly,
          # 1th filter doesn't correspond own localFilter["Pattern"] , 2th and 3th - correspond
          # that we return ret = [-3, 4, 5]
          pass
        elif logic == Filters.LOGIC_AND:
          # If all applying filters correspond own "Pattern"s that ret = [True], else ret = [False]
          pass
        # else continue
    return ret



if __name__ == '__main__':
  # first type of Filters creating
  filters = [{"Pattern" : "text/xml", 
              "Subject" : "%ContentType%", 
              "Stage" : Filters.STAGE_BEFORE_DOM_PRE,
              "Action" : 2}]
  filtersObj = Filters(filters)
  # seconf type of Filters creating
  wrapper = None
  # creating wrapper, fill cfgParser before it 
  # cfgParser = ConfigParser.ConfigParser()
  # wrapper = DBTasksWrapper(cfgParser)
  siteId = "eb066c4d81c58ddf9dfdc1b713700949"
  filtersObj = Filters(None, wrapper, siteId)

  #examples of using and results
  filters = [{"Pattern" : "text/xml", "Subject" : "%ContentType%", "OperationCode" : Filters.OC_RE, 
              "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 1},
             {"Pattern" : "text/xml", "Subject" : "%ContentType%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_AFTER_DOM, "Action" : 2},
             {"Pattern" : "text/html", "Subject" : "%ContentType%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 3},
             {"Pattern" : "application/pdf", "Subject" : "%ContentType%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 4},
             {"Pattern" : "text/xml", "Subject" : "%ContentType%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 5},
             {"Pattern" : "text/xml", "Subject" : "%url%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_BEFORE_DOM_PRE, "Action" : 6}, 
             {"Pattern" : "text/xml and text/xml", "Subject" : "%url% and %ddl%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 7},
             {"Pattern" : "text/xml and text/xml", "Subject" : "%url% and %redirect%", "OperationCode" : Filters.OC_RE,
              "Stage" : Filters.STAGE_AFTER_PROCESSOR, "Action" : 8},]

  filtersObj = Filters(filters)
  #------------------------------------------------------------------------- Example 1
  value = {"ContentType": "text/xml", "url": "text/xml", "MDd5" : "test/xml"}

  result = filtersObj.filterAll(Filters.STAGE_AFTER_DOM, value, Filters.LOGIC_AND)
  result == [True]
  result = filtersObj.filterAll(Filters.STAGE_AFTER_DOM, value, Filters.LOGIC_OR)
  result == [2]

  #------------------------------------------------------------------------- Example 2
  value = {"ContentType": "application/dat", "url": "text/xml", "MDd5" : "test/xml"}

  result = filtersObj.filterAll(Filters.STAGE_AFTER_DOM, value, Filters.LOGIC_AND)
  result == []
  result = filtersObj.filterAll(Filters.STAGE_AFTER_DOM, value, Filters.LOGIC_OR)
  result == []

  #------------------------------------------------------------------------- Example 3
  value = {"ContentType": "text/xml", "url": "text/xml", "MDd5" : "test/xml"}

  result = filtersObj.filterAll(Filters.STAGE_BEFORE_DOM_PRE, value, Filters.LOGIC_AND)
  result == [False]
  result = filtersObj.filterAll(Filters.STAGE_BEFORE_DOM_PRE, value, Filters.LOGIC_OR)
  result == [1, -4, 5, 6]
  
  result = filtersObj.filterAll(Filters.STAGE_COLLECT_URLS, value, Filters.LOGIC_AND)
  result == []
  result = filtersObj.filterAll(Filters.STAGE_COLLECT_URLS, value, Filters.LOGIC_OR)
  result == []

  #------------------------------------------------------------------------- Example 4
  value = {"ContentType": "text/xml", "url": "text/xml", "ddl" : "test/xml"}
  
  result = filtersObj.filterAll(Filters.STAGE_AFTER_PROCESSOR, value, Filters.LOGIC_AND)
  result == [False]
  result = filtersObj.filterAll(Filters.STAGE_AFTER_PROCESSOR, value, Filters.LOGIC_OR)
  result == [3, 7, -8]
