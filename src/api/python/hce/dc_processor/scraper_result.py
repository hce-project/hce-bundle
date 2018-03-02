"""@package docstring
 @file scraper_result.py
 @author Alexey, bgv <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""
import json
import time
import copy
import dc_processor.Constants as CONSTS
from dc_processor.base_extractor import BaseExtractor
from app.Metrics import Metrics
from app.ContentHashCalculator import ContentHashCalculator
# from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()

class Result(object):

  TAGS_LANG_DEFAULT = "en"
  TAGS_LANG_SUFFIX_DEFAULT = "_language"

  def __init__(self, config, resId, metrics=None):
    self.name = "Scraper result object"
    if metrics is None:
      self.metrics = {}
    else:
      self.metrics = metrics
    self.data = {}
    self.tags = {}
    self.blockedByXpathTags = []
    self.defaultTags = []
    self.resId = resId
    if config is None:
      self.article_tags = []
    else:
      self.article_tags = [tag for tag in config.options("article_tags")]
    for tag in self.article_tags:
      self.tags[tag] = ""
    self.start = time.time()
    self.finish = self.start
    self.errorCode = CONSTS.ERROR_OK
    self.errorMessage = CONSTS.MSG_ERROR_OK
    self.tagsCount = 0
    self.tagsMask = 0


  def getEmptyTags(self):
    empty_tags = [key for key, value in self.tags.items() if key in self.article_tags and not value]
    return empty_tags


  def getFilledTags(self):
    filled_tags = [key for key, value in self.tags.items() if key in self.article_tags and value]
    return filled_tags


  def recalcTagMaskCount(self, container=None, altTagsMask=None):
    self.tagsCount = 0
    self.tagsMask = 0

    for key, value in self.tags.items():
      if value is not None and value != "":
        tag = {}
        for key in value:
          tag[key] = value[key]

        # set tag's mask only if tag is registered, also increment tags count.
        # Execute it functionaly if tag's value not default
        if tag["name"] not in self.defaultTags and "data" in value:
          realValueString = ""
          if isinstance(value["data"], basestring):
            realValueString = value["data"]
          elif isinstance(value["data"], list) and len(value["data"]) > 0:
            realValueString = value["data"][0]
          if realValueString is not None and realValueString.strip() != "":
            if altTagsMask is not None:
              if tag["name"] in altTagsMask:
                self.tagsMask = self.tagsMask | altTagsMask[tag["name"]]
            elif tag["name"] in BaseExtractor.tagsMask:
              self.tagsMask = self.tagsMask | BaseExtractor.tagsMask[tag["name"]]
            self.tagsCount += 1

        if container is not None:
          container.append(copy.copy(tag))


  def metricsPrecalculate(self):
    if len(self.metrics) > 0:
      Metrics.fillMetricModulesList()
      Metrics.metricsPrecalculate(self.metrics, self)


  def get(self):
    data = {}
    data["resId"] = self.resId
    data["tagList"] = []

    # Convert old format to new collection format
    data["tagList"].append([])

    self.recalcTagMaskCount(data["tagList"][0])

    self.data["data"] = data
    self.data["error_code"] = self.errorCode
    self.data["error_message"] = self.errorMessage
    self.data["time"] = "%s" % (self.finish - self.start)

    self.metrics = json.dumps(self.metrics)
    self.data["metrics"] = self.metrics
    
    return json.dumps(self.data, encoding='utf-8', ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":"))


  def mergeResults(self, result):
    # logger.debug(">>> incoming result: %s", varDump(result))
    for blockedTag in result.blockedByXpathTags:
      if blockedTag not in self.blockedByXpathTags:
        self.blockedByXpathTags.append(blockedTag)

#     logger.debug("!!! self.tags: %s", varDump(self.tags))
#     logger.debug("!!! result.tags: %s", varDump(result.tags))

    for tagName in result.tags:
      if tagName not in self.tags or not self.isTagFilled(tagName):
        self.tags[tagName] = result.tags[tagName]
        if tagName in result.defaultTags and tagName not in self.defaultTags:
          self.defaultTags.append(tagName)


  def getBestValue(self, items_list):
    tmp = [item for item in items_list if item != ""]
    response = ""
    # if more than one suggestions try to select best one
    if len(tmp) > 1:
      # for each tag own rule
      # for content_encoded select biggest text
      if tmp[0]["name"] == "content_encoded":
        response = max(tmp, key=lambda x: x["data"])
      # for any else apply the same rule
      else:
        response = max(tmp, key=lambda x: x["data"])
    # if only one suggestion return it
    elif len(tmp) > 0:
      response = tmp[0]
    # if no one suggestions return empty string
    else:
      response = ""
    return response


  def stripResult(self):
    removeKeys = []
    for key in self.tags:
      if isinstance(self.tags[key], basestring):
        self.tags[key] = self.tags[key].strip()
        if self.tags[key] == "":
          removeKeys.append(key)
      elif isinstance(self.tags[key], dict) and "data" in self.tags[key]:
        if isinstance(self.tags[key]["data"], basestring):
          self.tags[key]["data"] = self.tags[key]["data"].strip()
          if self.tags[key]["data"] == "":
            removeKeys.append(key)
        elif isinstance(self.tags[key]["data"], list) and len(self.tags[key]["data"]) > 0 and \
        isinstance(self.tags[key]["data"][0], basestring):
          self.tags[key]["data"][0] = self.tags[key]["data"][0].strip()
          if self.tags[key]["data"][0] == "":
            removeKeys.append(key)
        else:
          removeKeys.append(key)

    for key in removeKeys:
      if key in self.tags:
        logger.debug(">>> Remove " + key + " element because it empty")
        del self.tags[key]


  def isTagFilled(self, tagsName):
    ret = False
    if tagsName in self.tags:
      if isinstance(self.tags[tagsName], basestring):
        if self.tags[tagsName].strip() != "":
          ret = True
      elif isinstance(self.tags[tagsName], dict) and "data" in self.tags[tagsName]:
        if isinstance(self.tags[tagsName]["data"], basestring):
          if self.tags[tagsName]["data"].strip() != "":
            ret = True
        elif isinstance(self.tags[tagsName]["data"], list):
          for elem in self.tags[tagsName]["data"]:
            if isinstance(elem, basestring) and elem != "":
              ret = True
              break

    return ret


#   # # retTagsText
#   #
#   def retTagsText(self, tagName):
#     ret = None
#     if tagName in self.tags:
#       if isinstance(self.tags[tagName], basestring):
#         ret = self.tags[tagName]
#       elif isinstance(self.tags[tagName], dict) and "data" in self.tags[tagName]:
#         if isinstance(self.tags[tagName]["data"], basestring):
#           ret = self.tags[tagName]["data"]
#         elif isinstance(self.tags[tagName]["data"], list):
#           ret = ""
#           for elem in self.tags[tagName]["data"]:
#             ret += elem
#             ret += ' '
#           ret = ret.strip()
#     return ret
#
#
#   # # setLangField
#   #
#   def setLangField(self, text, tagName, fieldName, suffixName):
#
#     logger.info("Enter setLangField() text = '%s', tagName = '%s', fieldName = '%s', suffixName = '%s'",
#                 str(text), str(tagName), str(fieldName), str(suffixName))
#     if text is not None:
#       lang = ContentHashCalculator.langDetect(text, False)
#       logger.info("lang = '%s'", str(lang))
#       logger.info("self.tags[tagName] = '%s', type = %s", str(self.tags[tagName]), str(type(self.tags[tagName])))
#       if lang is not None and isinstance(self.tags[tagName], dict):
#         self.tags[tagName][fieldName] = lang
#         self.tags[tagName]["lang_suffix"] = suffixName
#
#         logger.info("self.tags[%s]: '%s'", str(tagName), str(self.tags[tagName]))
#
#
#   # # tagsLangDetecting
#   #
#   def tagsLangDetecting(self, scraperLangDetect):
#     if "tags" in scraperLangDetect and "suffix" in scraperLangDetect:
#       if isinstance(scraperLangDetect["tags"], basestring) and scraperLangDetect["tags"] == "*":
#         for tagName in self.tags:
#           localTextValue = self.retTagsText(tagName)
#           self.setLangField(localTextValue, tagName, "lang", scraperLangDetect["suffix"])
#       elif isinstance(scraperLangDetect["tags"], basestring) and scraperLangDetect["tags"] == "&":
#         localTextResult = None
#         for tagName in self.tags:
#           localTextResult = ""
#           localTextValue = self.retTagsText(tagName)
#           if localTextValue is not None:
#             localTextResult += localTextValue
#             localTextResult += ' '
#           localTextResult = localTextResult.strip()
#         for tagName in self.tags:
#           self.setLangField(localTextResult, tagName, "summary_lang", scraperLangDetect["suffix"])
#       elif isinstance(scraperLangDetect["tags"], list):
#         for tagName in scraperLangDetect["tags"]:
#           localTextValue = self.retTagsText(tagName)
#           self.setLangField(localTextValue, tagName, "lang", scraperLangDetect["suffix"])
