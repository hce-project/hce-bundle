# coding: utf-8

"""@package docstring
  @file Filter.py
  @author Alexey <developers.hce@gmail.com>
  @author Madk <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2014 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
"""


import re
import datetime
import logging
import dc.Constants as DC_CONSTS


logger = logging.getLogger(DC_CONSTS.LOGGER_NAME)


STAGE_PROCESSING = 0
STAGE_BOFORE_PRE_PROCESSING = 1
STAGE_AFTER_PREPROCESSING = 2
STAGE_AFTER_PROCESSING = 3
STAGE_AFTER_PROCESSED = 4

SUBJECT_FIELD_NAME = 0
SUBJECT_FIELD_NAME_PATTERN = re.compile("%(.*)%")
SUBJECT_TAGS_KVDB = 1
SUBJECT_MACRO = 2
SUBJECT_MACRO_PATTERN = re.compile("@%(.*)%")

ACTION_ALLOW_INSERT = 1
ACTION_NOT_ALLOW_INSERT = -1
ACTION_NOT_URL_DELETE = 2
ACTION_URL_DELETE = -2

META_XPATH = "//meta"

PROCESSED_VALUE = "ProcessedValue"

CUR_YEAR_FULL = "%@CUR_YEAR_FULL%"
CUR_YEAR_SHORT = "%@CUR_YEAR_SHORT%"
CUR_MONTH = "%@CUR_MONTH%"
CUR_DAY = "%@CUR_DAY%"

CHARSET_PATTERN = re.compile("charset=([^;]*)")


'''
The filters class, which provide uniform filter functionality
'''
class Filters(object):

  '''
    constructor of the Filters Object
    @param filters list of all filters(rows of sites_filters)
    @param url the url data(one row of url_<SITE_MD5> table)
  '''
  def __init__(self, filters, url):
    self.filters = filters
    for filter_item in filters:
      if filter_item["Subject"].startswith(str(SUBJECT_FIELD_NAME)):
        field_name_match = SUBJECT_FIELD_NAME_PATTERN.search(filter_item["Subject"])
        if not field_name_match:
          logger.debug("Subject format %s not valid(cann't parse field name)")
          continue
        column_name = field_name_match.group(1)
        if column_name not in url:
          logger.debug("column name %s not exists on url table", column_name)
          continue
        filter_item[PROCESSED_VALUE] = filter_item["Subject"][2:].replace("%" + column_name + "%", url[column_name])


  '''
  '''
  def updateTagList(self, tags):
    for filter_item in self.filters:
      if filter_item["Subject"].startswith(str(SUBJECT_TAGS_KVDB)):
        filter_item[PROCESSED_VALUE] = tags


  '''
    update the fetch result
    @param res fetcher result
    @param dom the dom tree of the response
  '''
  def updateFetchResult(self, res, dom):
    for filter_item in self.filters:
      value = None
      if filter_item["Subject"].startswith(str(SUBJECT_MACRO)):
        macro_name_match = SUBJECT_MACRO_PATTERN.search(filter_item["Subject"])
        if not macro_name_match:
          logger.debug("Subject format %s not valid(cann't parse macro name)")
          continue
        macro_name = macro_name_match.group(1)
        if macro_name == "MIME_TYPE":
          value = res.headers["Content-Type"].split(";")[0]
        elif macro_name == "HEADER_CONTENT_TYPE":
          value = res.headers["Content-Type"].split(";")[0]
        elif macro_name == "META_CONTENT_TYPE":
          for meta_e in dom.xpath(META_XPATH):
            if "http-equiv" in meta_e.attrib and meta_e.attrib["http-equiv"].lower() == "content-type":
              value = meta_e.attrib['content'].split(";")[0]
              break
          else:
            logger.debug("cannt find META-CONTENT-TYPE")
        elif macro_name == "HEADER_CHARSET":
          value = res.headers
        elif macro_name == "META_CHARSET":
          for meta_e in dom.xpath(META_XPATH):
            if "charset" in meta_e.attrib:
              value = meta_e.attrib['content'].split(";")[0]
              break
            elif "content-type" in meta_e.attrib and meta_e.attrib["http-equiv"].tolower() == "content-type":
              if ";" in meta_e.attrib['content']:
                charset_match =  CHARSET_PATTERN.match(meta_e.attrib['content'].split(";")[1])
                if charset_match:
                  value = charset_match.group(1)
                  break
          else:
            logger.debug("cannt find META-CONTENT-TYPE")
        elif macro_name == "IP_ADDRESS":
          #TODO
          pass
      if value is not None:
        filter_item[PROCESSED_VALUE] = value  


  '''
    check all filters by for appropriate Stage
    @param stage the target stage(useless when all_stage is True)
    @param value the value to filter, will use expanded Subject when value is None(by default)
    @param all_stage whether apply filters of all stages
    @return action the first rejected Action value if have
            otherwise return the last Action value
  '''
  def filterAll(self, stage, value = None, all_stage = False):
    return_val = 0
    for filter_item in self.filters:
      if not all_stage and filter_item["Stage"] != stage:
        continue
      subject = filter_item["Subject"]
      
      if value is None:
        if PROCESSED_VALUE not in filter_item:
          continue
        value = filter_item[PROCESSED_VALUE]
      if re.compile(filter_item["Pattern"]).match(value):
        return_val = filter_item["Action"]
        if return_val < 0:
          # just return the negative values but save postive value and continue check 
          return return_val

    return return_val


    '''
    check filter one by one, but ignore unmatch stage items
    usage: for action in filters.filterOneByOne(stage1):
              do_some_thing()
              if some_condition:
                continue

    @param stage the target stage(useless when all_stage is True)
    @param value the value to filter, will use expanded Subject when value is None(by default)
    @param all_stage whether apply filters of all stages

    @return action generator

    '''
    def filterOneByOne(self, stage, value = None, all_stage = False):
      for filter_item in self.filters:
        if not all_stage and filter_item["Stage"] != stage:
          continue
        if value is None:
          if PROCESSED_VALUE not in filter_item:
            continue
          value = filter_item[PROCESSED_VALUE]
        if re.compile(filter_item["Pattern"]).match(value):
          yield filter_item["Action"]


    # if CUR_YEAR_FULL in pattern or \
    #   CUR_MONTH in pattern or \
    #   CUR_DAY in pattern:
    #   self.date = True
    # else:
    #   self.date = False
    # logger.debug("Initial pattern: <<%s>>", pattern)
    # pattern = pattern.replace(CUR_YEAR_FULL, datetime.datetime.now().strftime("%Y"))
    # pattern = pattern.replace(CUR_YEAR_SHORT, datetime.datetime.now().strftime("%y"))
    # pattern = pattern.replace(CUR_MONTH, datetime.datetime.now().strftime("%m"))
    # pattern = pattern.replace(CUR_DAY, datetime.datetime.now().strftime("%d"))
    # logger.debug("Pattern after replacing: <<%s>>", pattern)
    # self.type = type
    # self.pattern = re.compile(pattern)
