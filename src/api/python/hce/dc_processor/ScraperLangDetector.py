# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
ScraperLangDetector Class content main functional detect lang.

@package: dc_processor
@file ScraperLangDetector.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import app.Utils as Utils
import dc_processor.Constants as CONSTS



class ScraperLangDetector(object):
  # # Constants used in class
  MSG_ERROR_LANG_DETECT = "Language detection failed. Error: %s"


  # # Properties options constants
  PROPERTY_OPTION_PREFIX = "prefix"
  PROPERTY_OPTION_SUFFIX = "suffix"
  PROPERTY_OPTION_TAGS = "tags"
  PROPERTY_OPTION_MAPS = "maps"
  PROPERTY_OPTION_SIZE = "size"

  DEFAULT_VALUE_OPTION_PREFIX = ""
  DEFAULT_VALUE_OPTION_SUFFIX = "_lang"
  DEFAULT_VALUE_OPTION_TAGS = []
  DEFAULT_VALUE_OPTION_MAPS = { "en": [ "fr", "nl", "ro", "af", "ca", "it", "da", "tl", "et", "cy", "sv", "id", "es"], \
                                "ja": [ "ja", "zh", "za" ], \
                                "ru": [ "ru", "uk" ], \
                                "pl": [ "pl" ], \
                                "de": [ "de" ] }
  DEFAULT_VALUE_OPTION_SIZE = 1024
  DEFAULT_VALUE_SUMMARY_LANG = "en"
  
  DEFAULT_VALUE_LANG_MAPPING = '*'
  
  DEFAULT_VALUE_TAGS_NAMES = [CONSTS.TAG_MEDIA, CONSTS.TAG_TITLE, CONSTS.TAG_LINK, CONSTS.TAG_DESCRIPTION, CONSTS.TAG_PUB_DATE, CONSTS.TAG_DC_DATE, \
                              CONSTS.TAG_AUTHOR, CONSTS.TAG_CONTENT_UTF8_ENCODED, CONSTS.TAG_KEYWORDS]

  TAGS_EXTENDED_VALUE_ALL = "*"
  TAGS_EXTENDED_VALUE_SUMMARY = "&"

  SCRAPER_RESULT_TAG_OPTION_DATA = "data"
  SCRAPER_RESULT_TAG_OPTION_LANG = "lang"
  SCRAPER_RESULT_TAG_OPTION_SUMMARY_LANG = "summary_lang"

  # # Initialization
  def __init__(self, scraperLangDetectProperty):
    self.prefix = self.DEFAULT_VALUE_OPTION_PREFIX
    self.suffix = self.DEFAULT_VALUE_OPTION_SUFFIX
    self.tagsList = self.DEFAULT_VALUE_OPTION_TAGS
    self.maps = self.DEFAULT_VALUE_OPTION_MAPS
    self.size = self.DEFAULT_VALUE_OPTION_SIZE
    self.detectedLangs = {}

    if isinstance(scraperLangDetectProperty, dict):
      # set prefix options
      if self.PROPERTY_OPTION_PREFIX in scraperLangDetectProperty:
        self.prefix = scraperLangDetectProperty[self.PROPERTY_OPTION_PREFIX]

      # set suffix options
      if self.PROPERTY_OPTION_SUFFIX in scraperLangDetectProperty:
        self.suffix = scraperLangDetectProperty[self.PROPERTY_OPTION_SUFFIX]

      # set tags options
      if self.PROPERTY_OPTION_TAGS in scraperLangDetectProperty:
        self.tagsList = scraperLangDetectProperty[self.PROPERTY_OPTION_TAGS]

      # set maps options
      if self.PROPERTY_OPTION_MAPS in scraperLangDetectProperty:
        self.maps = scraperLangDetectProperty[self.PROPERTY_OPTION_MAPS]

      # set size options
      if self.PROPERTY_OPTION_SIZE in scraperLangDetectProperty:
        self.size = int(scraperLangDetectProperty[self.PROPERTY_OPTION_SIZE])


  # # Make tag name use prefix and suffix
  #
  # @param tagName - tag name
  # @return result full tag name
  def __makeTagName(self, tagName):
    return self.prefix + tagName + self.suffix


  # # lang detect
  #
  # @param incomeBuf - income buffer data
  # @param convertToFullName - boolean flag convert to full name
  # @param log - logger instance
  # @return detected lang as string or None otherwise
  @staticmethod
  def langDetect(incomeBuf, convertToFullName=True, log=None):
    ret = None

    if incomeBuf is not None and incomeBuf != "":
      try:
        from langdetect import detect
        ret = detect(incomeBuf.decode('utf-8')).replace('-', ',')
      except Exception, err:
        if log is not None:
          log.error(ScraperLangDetector.MSG_ERROR_LANG_DETECT, str(err))
          log.debug(Utils.getTracebackInfo())

    return ret


  # # extract tags text data
  #
  # @param tagName - tag name
  # @param response  - scraper result instance
  # @return text data for tag name
  def __retTagsText(self, tagName, response):
    # variable for result
    ret = None

    if response is not None and tagName in response.tags:
      if isinstance(response.tags[tagName], basestring):
        ret = response.tags[tagName]

      elif isinstance(response.tags[tagName], dict) and \
        ScraperLangDetector.SCRAPER_RESULT_TAG_OPTION_DATA in response.tags[tagName]:
        if isinstance(response.tags[tagName][ScraperLangDetector.SCRAPER_RESULT_TAG_OPTION_DATA], basestring):
          ret = response.tags[tagName][ScraperLangDetector.SCRAPER_RESULT_TAG_OPTION_DATA]

        elif isinstance(response.tags[tagName][ScraperLangDetector.SCRAPER_RESULT_TAG_OPTION_DATA], list):
          ret = ""
          for elem in response.tags[tagName][ScraperLangDetector.SCRAPER_RESULT_TAG_OPTION_DATA]:
            ret += elem
            ret += ' '
          ret = ret.strip()

    return ret


  # # truncate buffer
  #
  # @param text - text buffer
  # @param log - logger instance
  # @return trancated text buffer
  def __truncateBuffer(self, text, log=None):
    # variable for result
    buff = text if len(text) <= self.size else text[:self.size]
    while len(buff) > 0:
      try:
        buff.decode('utf-8')
        break
      except Exception, err:
        buff = buff[:-1]
        if log is not None:
          log.debug("Decode buffer error: %s", str(err))

    buff = buff.decode('utf-8')
    if log is not None:
      log.debug("buffer len = %s was trancated to len = %s used limit = %s", str(len(text)), str(len(buff)), str(self.size))

    return buff


  # # set language field in tags
  #
  # @param text - text buffer
  # @param tagName - tag name
  # @param fieldName - field name
  # @param response - scraper result instance
  # @param log - logger instance
  # @return - None
  def __setLangField(self, text, tagName, fieldName, response, log=None):
    if text is not None:
      # truncate buffer by limit size
      text = self.__truncateBuffer(text, log)

      # detect language
      lang = ScraperLangDetector.langDetect(text, False, log)
      if log is not None:
        log.debug("for '%s' was detected '%s'", str(tagName), str(lang))

      if lang is not None and isinstance(response.tags[tagName], dict):
        lang = self.__langMapping(lang)
        response.tags[tagName][fieldName] = lang
        self.detectedLangs[tagName] = lang


  # # language mapping
  #
  # @param lang - language for mapping
  # @return language
  def __langMapping(self, lang):
    # variable for result
    ret = lang

    isExist = False
    for key, value in self.maps.items():
      isExist = self.__isExistValue(value, lang)
      if isExist:
        ret = key
        break

    if not isExist:
      default = None
      for key, value in self.maps.items():
        if self.__isExistValue(value, self.DEFAULT_VALUE_LANG_MAPPING):
          default = key

      if default is not None:
        ret = default

    return ret


  # # check exist value
  #
  # @param src - source list of strings for search
  # @param val - value for search
  # @return True if exist or False otherwise
  def __isExistValue(self, src, val):
    return len([s for s in src if val in s]) > 0


  # # main processing
  #
  # @param response - scraper result instance
  # @param log - logger instance
  # @return - None
  def process(self, response, log=None):
    if response is not None:
      # use all tags
      if isinstance(self.tagsList, basestring) and self.tagsList == self.TAGS_EXTENDED_VALUE_ALL or \
        isinstance(self.tagsList, list) and self.TAGS_EXTENDED_VALUE_ALL in self.tagsList:
        for tagName in response.tags:
          localTextValue = self.__retTagsText(tagName, response)
          self.__setLangField(localTextValue, tagName, self.SCRAPER_RESULT_TAG_OPTION_LANG, response, log)

      # use summary tags
      elif isinstance(self.tagsList, basestring) and self.tagsList == self.TAGS_EXTENDED_VALUE_SUMMARY or \
        isinstance(self.tagsList, list) and self.TAGS_EXTENDED_VALUE_SUMMARY in self.tagsList:
        localTextResult = None
        for tagName in response.tags:
          localTextResult = ""
          localTextValue = self.__retTagsText(tagName, response)
          if localTextValue is not None:
            localTextResult += localTextValue
            localTextResult += ' '
          localTextResult = localTextResult.strip()

        for tagName in response.tags:
          self.__setLangField(localTextResult, tagName, self.SCRAPER_RESULT_TAG_OPTION_SUMMARY_LANG, response, log)

      # use list tags
      elif isinstance(self.tagsList, list):    
        for tagName in self.tagsList:
          localTextValue = self.__retTagsText(tagName, response)
          self.__setLangField(localTextValue, tagName, self.SCRAPER_RESULT_TAG_OPTION_LANG, response, log)
          
          
  # # get detected lang for tags
  #
  # @param - None
  # @return dictionary lang tags and their values
  def getLangTags(self):
    # variable for result
    langTagsDict = {}

    for tagName, lang in self.detectedLangs.items():
      langTagsDict[self.__makeTagName(tagName)] = lang

    return langTagsDict


  # # get lang tags names
  #
  # @param - None
  # @return list of the lang tags names
  def getLangTagsNames(self):
    # variable for result
    langTagsNames = []

    tagsList = []

    if isinstance(self.tagsList, basestring) and self.tagsList == self.TAGS_EXTENDED_VALUE_ALL or \
      isinstance(self.tagsList, list) and self.TAGS_EXTENDED_VALUE_ALL in self.tagsList or \
      isinstance(self.tagsList, basestring) and self.tagsList == self.TAGS_EXTENDED_VALUE_SUMMARY or \
      isinstance(self.tagsList, list) and self.TAGS_EXTENDED_VALUE_SUMMARY in self.tagsList:
      tagsList = self.DEFAULT_VALUE_TAGS_NAMES

    elif isinstance(self.tagsList, list):
      tagsList = self.tagsList

    for tagName in tagsList:
      langTagsNames.append(self.__makeTagName(tagName))

    return langTagsNames


  # # get summary lang
  #
  # @param response - scraper result instance
  # @param log - logger instance
  # @return summary lang value as string
  def getSummaryLang(self, response, log=None):
    #variable for result
    summaryLang = self.DEFAULT_VALUE_SUMMARY_LANG

    if response is not None:
      for tagName, tagValue in response.tags.items():
        if isinstance(tagValue, dict) and self.SCRAPER_RESULT_TAG_OPTION_SUMMARY_LANG in tagValue:
          summaryLang = tagValue[self.SCRAPER_RESULT_TAG_OPTION_SUMMARY_LANG]
          if log is not None:
            log.debug("Summary lang '%s' was extracted from field '%s'", str(summaryLang), str(tagName))
          break

    return summaryLang
