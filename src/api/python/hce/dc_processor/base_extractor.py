# coding: utf-8
"""@package docstring
 @file base_extractor.py
 @author Alexey, bgv <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""

import re
import json
import dc_processor.Constants as CONSTS
import dc_processor.scraper_result
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


# time execution limit
def signal_handler(signum, frame):
  del signum, frame
  logger.debug("Time execution limit was reached: %s seconds.", str(CONSTS.TIME_EXECUTION_LIMIT))
  raise Exception("Timed out!")


# Local class constants
ERR_MSG_ADJUST_PUB_DATE = "Error in adjustPubDate: "
ERR_MSG_ADJUST_MEDIA = "Error in adjustMedia: "
ERR_MSG_ADJUST_CONTENT_UTF8_ENCODED = "Error in adjustContentUTF8Encoded: "

ERR_MSG_OK = ""

EMPTY_DATE = ""

# Adjust publication date
# If incoming publication date is array just return one of them (first)
# @param dates publication date, extracted from content
def adjustPubDate(dates):
  # logger.debug("dates: %s", dates)
  pub_date = EMPTY_DATE
  try:
    # TODO: improve to return most appropriate
    # if dates and any(i.isdigit() for i in dates):
    if isinstance(dates, list) and len(dates):
      # pub_date = dates[0]
      pub_date = " ".join(dates)
    else:
      pub_date = dates
    if pub_date and len(dates) and not re.search(r'\d+', pub_date):
      pub_date = EMPTY_DATE
  except Exception as err:
    ExceptionLog.handler(logger, err, ERR_MSG_ADJUST_PUB_DATE)

  return pub_date


# Adjust data in media tag
# If media are PR (partial reference) adjust path
# @param medias media extracted from content
def adjustMedia(medias):
  return medias
  # valid_http_url = HttpUrl()
  # res = []
  # try:
  #  if isinstance(medias, list):
  #    for media in medias:
  #      if valid_http_url(media):
  #        res.append(media)
  # except Exception as err:
  #  logger.error(ERR_MSG_ADJUST_MEDIA + err.message)
  # return res


# Adjust data in content_encoded tag
# If content are non-meaningfull adjust it
# @param data content extracted from content
def adjustContentUTF8Encoded(data):
  return data


# Adjust data in content_encoded tag
# If content are non-meaningfull adjust it
# @param data content extracted from content
def adjustLink(data):
  if isinstance(data, list) and len(data) > 1:
    data = data[0]
  return data


def adjustNone(data):
  return data


# #The BaseExtractor class
# This is the base class for custom extractors
# Provide basic functionality such as add tag, etc.
class BaseExtractor(object):

  properties = None

  tag = {CONSTS.TAG_MEDIA: adjustMedia,
         CONSTS.TAG_CONTENT_UTF8_ENCODED: adjustContentUTF8Encoded,
         CONSTS.TAG_PUB_DATE: adjustPubDate,
         CONSTS.TAG_TITLE: adjustNone,
         CONSTS.TAG_LINK: adjustLink,
         CONSTS.TAG_DESCRIPTION: adjustNone,
         CONSTS.TAG_DC_DATE: adjustNone,
         CONSTS.TAG_AUTHOR: adjustNone,
         CONSTS.TAG_GUID: adjustNone,
         CONSTS.TAG_KEYWORDS: adjustNone,
         CONSTS.TAG_MEDIA_THUMBNAIL: adjustNone,
         CONSTS.TAG_ENCLOSURE: adjustNone,
         CONSTS.TAG_MEDIA_CONTENT: adjustNone,
         CONSTS.TAG_GOOGLE: adjustNone,
         CONSTS.TAG_GOOGLE_TOTAL: adjustNone,
         CONSTS.HTML_LANG: adjustNone
        }


  tagsMask = {CONSTS.TAG_MEDIA: 1,
              CONSTS.TAG_CONTENT_UTF8_ENCODED: 1 << 1, CONSTS.CONTENT: 1 << 1,
              CONSTS.TAG_PUB_DATE: 1 << 2, CONSTS.PUBLISHED: 1 << 2,
              CONSTS.TAG_TITLE: 1 << 3,

              CONSTS.TAG_LINK: 1 << 4,
              CONSTS.TAG_DESCRIPTION: 1 << 5,
              CONSTS.UPDATED_PARSED: 1 << 6,
              CONSTS.TAG_DC_DATE: 1 << 7,

              CONSTS.TAG_AUTHOR: 1 << 8,
              CONSTS.TAG_GUID: 1 << 9,
              CONSTS.TAG_KEYWORDS: 1 << 10,
              CONSTS.TAG_MEDIA_THUMBNAIL: 1 << 11,

              CONSTS.TAG_ENCLOSURE: 1 << 12,
              CONSTS.TAG_MEDIA_CONTENT: 1 << 13,
              CONSTS.TAG_GOOGLE: 1 << 14,
              CONSTS.TAG_GOOGLE_TOTAL: 1 << 15,

              CONSTS.HTML_LANG: 1 << 16,
              CONSTS.PARENT_RSS_FEED: 1 << 17,
              CONSTS.PARENT_RSS_FEED_URLMD5: 1 << 18,
              CONSTS.SUMMARY_DETAIL: 1 << 19,

              CONSTS.SUMMARY: 1 << 20,
              CONSTS.COMMENTNS: 1 << 21,
              CONSTS.TAGS: 1 << 22,
              CONSTS.UPDATED: 1 << 23,

              CONSTS.TAG_ORDER_NUMBER: 1 << 24,
              CONSTS.TAG_SOURCE_URL: 1 << 25
             }


  # # class constructor
  #
  def __init__(self, config, templ=None, domain=None, processorProperties=None):  # pylint: disable=W0612,W0613
    self.config = config
    self.processorProperties = processorProperties
    self.properties = None
    scraperPropFileName = self.config.get("Application", "property_file_name")

    if scraperPropFileName is not None:
      self.loadScraperProperties(scraperPropFileName)

    self.name = "Base extractor"
    self.rank = CONSTS.SCRAPER_RANK_INIT

    # support processing modes
    self.process_mode = CONSTS.PROCESS_ALGORITHM_REGULAR
    self.modules = {}

    self.data = {"extractor":"Base extractor", "data":"", "name":""}
    self.db_dc_scraper_db = None
    self.DBConnector = None
    if processorProperties is not None and "SCRAPER_TAG_ITEMS_DELIMITER" in processorProperties:
      self.imgDelimiter = processorProperties["SCRAPER_TAG_ITEMS_DELIMITER"]
    else:
      self.imgDelimiter = ' '
    self.tagsValidator = None
    if processorProperties is not None and "tagsValidator" in processorProperties:
      try:
        self.tagsValidator = json.loads(processorProperties["tagsValidator"], encoding='utf-8')
      except Exception as excp:
        ExceptionLog.handler(logger, excp, '>>> tagsValidator wronj json format', (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})


  def __str__(self):
    return "%s" % (self.name)


  def __repr__(self):
    return repr((self.name, self.rank))


  # #loadScraperProperties
  # loadScraperProperties loads scraper propeties from json file
  #
  # @param scraperPropFileName properties file name
  def loadScraperProperties(self, scraperPropFileName):
    if scraperPropFileName is not None:
      try:
        with open(scraperPropFileName, "rb") as fd:
          scraperProperies = json.loads(fd.read())
          self.properties = scraperProperies[self.__class__.__name__][CONSTS.PROPERTIES_KEY]
      except Exception as excp:
        logger.debug(">>> Some error with scraper property loads = " + str(excp))


  # # isTagNotFilled
  #
  def isTagNotFilled(self, result, tagName):
    ret = True
    if tagName in result.tags:
      if isinstance(result.tags[tagName], basestring):
        ret = (result.tags[tagName].strip() == "")
      elif isinstance(result.tags[tagName], list):
        if len(result.tags[tagName]) > 0:
          ret = False
      elif isinstance(result.tags[tagName], dict):
        if "data" in result.tags[tagName]:
          if isinstance(result.tags[tagName]["data"], basestring):
            ret = (result.tags[tagName]["data"].strip() == "")
          elif isinstance(result.tags[tagName]["data"], list):
            for elem in result.tags[tagName]["data"]:
              ret = (elem.strip() == "")
              if not ret:
                break

    return ret


  # # isTagValueNotEmpty
  #
  def isTagValueNotEmpty(self, tagValue):
    full = None
    if isinstance(tagValue, list):
      if len(tagValue) == 0:
        full = None
      else:
        full = tagValue
    else:
      full = tagValue
    return full


  # # tagValueElemValidate
  #
  def tagValueElemValidate(self, tagValueElem, conditionElem):
    ret = True
    if conditionElem["type"] == "include":
      ret = False
      if re.compile(conditionElem["RE"]).match(tagValueElem) is not None:
        ret = True
    elif conditionElem["type"] == "exclude":
      if re.compile(conditionElem["RE"]).match(tagValueElem) is not None:
        ret = False
    return ret


  # # tagValueValidate
  #
  def tagValueValidate(self, tagName, tagValue):
    ret = tagValue
    if self.tagsValidator is not None and self.name in self.tagsValidator and tagName in self.tagsValidator[self.name]:
      try:
        if isinstance(tagValue, list):
          ret = []
          for elem in tagValue:
            if self.tagValueElemValidate(elem, self.tagsValidator[self.name][tagName]):
              ret.append(elem)
          if len(ret) == 0:
            ret = None
        elif isinstance(tagValue, basestring):
          if not self.tagValueElemValidate(tagValue, self.tagsValidator[self.name][tagName]):
            ret = None
      except Exception as excp:
        ExceptionLog.handler(logger, excp, '>>> something wrong in tagValueValidate method', (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    return ret


  # # addTag
  #
  def addTag(self, result, tag_name, tag_value, xpath="", isDefaultTag=False, callAdjustment=True, tagType=None,
             allowNotFilled=False):
    ret = False
    if tag_name not in result.blockedByXpathTags:
      tag_value = self.tagValueValidate(tag_name, tag_value)
      if tag_value is not None:
        if callAdjustment:
          try:
            if tag_value and not isinstance(tag_value, list):
              pass
            if tag_value and isinstance(tag_value, list):
              pass
            tag_value = self.tag[tag_name](tag_value)
          except Exception as err:
            logger.debug('No tag name in result template: %s', str(err))

        result.errorCode = 0
        result.errorMessage = ERR_MSG_OK

        if (tag_name not in result.tags.keys() and self.isTagValueNotEmpty(tag_value) is not None) or \
          (self.isTagNotFilled(result, tag_name) and self.isTagValueNotEmpty(tag_value) is not None) or \
          allowNotFilled:
          data = {"extractor": "Base extractor", "data": "", "name": ""}
          data["data"] = tag_value
          data["name"] = tag_name
          data["xpath"] = xpath
          data["type"] = tagType
          data["lang"] = dc_processor.scraper_result.Result.TAGS_LANG_DEFAULT
          data["lang_suffix"] = dc_processor.scraper_result.Result.TAGS_LANG_SUFFIX_DEFAULT
          data["extractor"] = self.__class__.__name__
          result.tags[tag_name] = data
          if isDefaultTag and tag_name not in result.defaultTags:
            result.defaultTags.append(tag_name)
          ret = True

    else:
      logger.debug(">>> BaseExtractor.addTag, tags in break list; tag is = " + tag_name)
    return ret


  # # calculateMetrics
  #
  def calculateMetrics(self, response):
    try:
      for metric in response.metrics:
        logger.debug("response.tags:\n%s\nmetric:\n%s", varDump(response.tags), varDump(metric))
        metric.calculateMetricValue(response.tags)
    except Exception, err:
      ExceptionLog.handler(logger, err, CONSTS.MSG_ERROR_CALC_METRICS)
      raise err


  # # rankReading
  #
  def rankReading(self, exctractorName):
    wasSet = False
    if self.processorProperties is not None and exctractorName is not None and \
    CONSTS.RANK_KEY in self.processorProperties:
      try:
        rankProp = json.loads(self.processorProperties)
        if exctractorName in rankProp:
          self.rank = rankProp[exctractorName]
          wasSet = True
      except Exception:
        logger.debug(">>> Wrong json string in processorProperties[\"%s\"]", CONSTS.RANK_KEY)

    if not wasSet and self.properties is not None and CONSTS.RANK_KEY in self.properties:
      self.rank = self.properties[CONSTS.RANK_KEY]

    logger.debug(">>> Rank is : %s", str(self.rank))
