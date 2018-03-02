# -*- coding: utf-8 -*-
"""@package docstring
 @file scrapy_extractor.py
 @author Alexey <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""

import re
import json
import copy
import ConfigParser
import dc_processor.Constants as CONSTS
from dc_processor.base_extractor import BaseExtractor
from app.SelectorWrapper import SelectorWrapper
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401
from app.Url import Url

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #ScrapyExtractor class implements data extracting using Scrapy module with prepared XPathes/Css
#
class ScrapyExtractor(BaseExtractor):

  SELF_NAME = "Scrapy extractor"

  # Constants used in class
  TEMPLATE_FILE_RULE_XPATH = 'xpath'
  TEMPLATE_FILE_RULE_REPLACE = 'replace'
  TEMPLATE_FILE_RULE_EXCLUDE = 'exclude'

  DISABLE_XPATH_CHARS_LIST = [';', '#']

  # #class constructor
  #
  # @param config - incoming app config
  # @param templ - optionality dict with base set of extractor rules/xpathes
  # @param domain - optionality param, processing url domain
  # @param processorProperties - optionality param, incoming app processor properties
  # @param template - optionality param, incoming template set
  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    BaseExtractor.__init__(self, config, templ, domain, processorProperties)
    logger.debug("Properties: %s", varDump(self.properties))

    # set module rank from module's properties
    self.rankReading(self.__class__.__name__)

    self.closeVoid = None
    if processorProperties is not None and CONSTS.TAG_CLOSE_VOID_PROP_NAME in processorProperties and \
      processorProperties[CONSTS.TAG_CLOSE_VOID_PROP_NAME] is not None:
      self.closeVoid = int(processorProperties[CONSTS.TAG_CLOSE_VOID_PROP_NAME])

    self.keepAttributes = None
    if processorProperties is not None and CONSTS.TAG_KEEP_ATTRIBUTES_PROP_NAME in processorProperties and \
      processorProperties[CONSTS.TAG_KEEP_ATTRIBUTES_PROP_NAME] is not None:
      self.keepAttributes = {}
      for key in processorProperties[CONSTS.TAG_KEEP_ATTRIBUTES_PROP_NAME]:
        self.keepAttributes[key.lower()] = processorProperties[CONSTS.TAG_KEEP_ATTRIBUTES_PROP_NAME][key]

    if processorProperties is not None and CONSTS.TAG_MARKUP_PROP_NAME in processorProperties and \
      processorProperties[CONSTS.TAG_MARKUP_PROP_NAME] is not None:
      self.innerTextTagReplacers = {}
      for key in processorProperties[CONSTS.TAG_MARKUP_PROP_NAME]:
        self.innerTextTagReplacers[key.lower()] = processorProperties[CONSTS.TAG_MARKUP_PROP_NAME][key]
    else:
      self.innerTextTagReplacers = None

    self.name = self.SELF_NAME
    self.data["extractor"] = self.SELF_NAME
    self.sel = None
    self.resource = None
    # for post processing
    self.postReplace = {}
    self.postExclude = {}

    if processorProperties is not None and "SCRAPER_SCRAPY_PRECONFIGURED" in processorProperties:
      self.templates = self.generateTemplatesFromRowTemplates(json.loads(processorProperties\
                                                                         ["SCRAPER_SCRAPY_PRECONFIGURED"]), domain)
    else:
      self.templates = [{self.SELF_NAME + "_default": self.templateLoad(config, templ, domain)}]

    try:
      defaultConfigTemplate = config.get("Application", "default_template", None)
    except ConfigParser.NoOptionError:
      defaultConfigTemplate = None
    if defaultConfigTemplate is not None:
      logger.debug(">>> Extend Templates with config default template")
      tempTemplates = self.generateTemplatesFromRowTemplates(json.loads(defaultConfigTemplate), domain)
      if len(tempTemplates) > 0:
        newTemplates = []
        for templeteElemConfig in tempTemplates:
          for templeteElemProperty in self.templates:
            for templeteKeyProperty in templeteElemProperty:
              if templeteKeyProperty in templeteElemConfig:
                templeteElemConfig = None
                break
            if templeteElemConfig is None:
              break
          if templeteElemConfig is not None:
            newTemplates.append(templeteElemConfig)
        self.templates = self.templates + newTemplates
    self.blockedByXpathTags = []
    logger.debug("!!! INIT Template Domain: '%s'", str(domain))
#     logger.debug("!!! INIT Template: %s", str(self.templates))


  # #generateTemplatesFromRowTemplates method extract templates from incoming rowTemplates data
  #
  # @param rowTemplates - incoming rowTemplates
  # @return result - list of template dicts
  def generateTemplatesFromRowTemplates(self, rowTemplates, domain=None):
    ret = []
    try:
      if "sets" in rowTemplates:
        ret = rowTemplates["sets"]
        for elem in ret:
          for setName in elem:
            if isinstance(elem[setName], basestring):
              try:
                with open(elem[setName], "rb") as fd:
                  elem[setName] = json.loads(fd.read())
              except Exception as excp:
                logger.debug(">>> generateTemplatesFromRowTemplates element[%s] file/json operations error, %s",
                             setName, str(type(elem[setName])))
                elem[setName] = {}
            elif not isinstance(elem[setName], dict):
              logger.debug(">>> generateTemplatesFromRowTemplates element[%s] wrong type is %s", setName,
                           str(type(elem[setName])))
              elem[setName] = {}

            elem[setName] = self.templatePreparer(None, domain, elem[setName])
            break
    except Exception as excp:
      logger.debug(">>> Some error during generateTemplatesFromRowTemplates = " + str(excp))
    return ret


  # #templateLoad method which fills internal template dict with preparatory extractor rules/xpathes
  #
  # @param config - incoming app config
  # @param templ - optionality dict with base set of extractor rules/xpathes
  # @param domain - optionality param, processing url domain
  # @return result template dict
  def templateLoad(self, config, templ=None, domain=None):
    ret = {}
    defaultTemplate = None
    try:
      templateFile = config.get("Application", "template", None)
    except ConfigParser.NoOptionError:
      templateFile = None
    if templateFile:
      try:
        logger.debug("Read template from file. %s", templateFile)
        with open(templateFile, "rb") as fd:
          defaultTemplate = self.templatePreparer(fd.read(), domain, {})
      except Exception, err:
        logger.error("Error Read template from file. %s", str(err))

    if self.properties is not None and CONSTS.TEMPLATE_KEY not in self.properties:
      ret = self.templatePreparer(self.properties[CONSTS.TEMPLATE_KEY], domain, {})
      logger.debug("template: " + str(ret))
    elif templ is not None:
      logger.debug("template: %s", str(templ))
      if isinstance(templ, dict):
        ret = self.templatePreparer(None, domain, templ)
      else:
        ret = self.templatePreparer(templ, domain, {})

#       logger.debug("!!! ret template: %s ", str(ret))

      # merge default template and custom one
      if defaultTemplate is not None:
        logger.debug("merge default template and custom one")
        defaultTags = defaultTemplate.keys()
        customTags = ret.keys()
        logger.debug("tags in default template:\n%s\nin custom template:\n%s", str(defaultTags), str(customTags))
        for tag in defaultTags:
          if tag not in customTags:
            ret[tag] = defaultTemplate[tag]
            logger.debug("%s was replaced from custom template", str(tag))
    elif defaultTemplate is not None:
      ret = defaultTemplate
    else:
      logger.error("Error Read template.")
    return ret


  # #pasteLists pastes same elements in 2 incoming dicts
  #
  # @param lhs - incoming destination dict
  # @param rhs - incoming source dict
  def pasteLists(self, lhs, rhs):
#     logger.debug("lhs: %s, type: %s", str(lhs), str(type(lhs)))
#     logger.debug("rhs: %s, type: %s", str(rhs), str(type(rhs)))

    if isinstance(lhs, dict) and isinstance(rhs, dict):
      for elem in rhs:

        self.postReplace[elem] = []
        if elem in lhs and self.TEMPLATE_FILE_RULE_REPLACE in lhs[elem] and \
          isinstance(lhs[elem][self.TEMPLATE_FILE_RULE_REPLACE], dict):
          self.postReplace[elem].append(lhs[elem][self.TEMPLATE_FILE_RULE_REPLACE])
#           logger.debug("!!! lhs self.postReplace: %s", str(lhs[elem][self.TEMPLATE_FILE_RULE_REPLACE]))
#           logger.debug("!!! self.postReplace: %s", str(self.postReplace))

        if elem in rhs and self.TEMPLATE_FILE_RULE_REPLACE in rhs[elem] and \
          isinstance(rhs[elem][self.TEMPLATE_FILE_RULE_REPLACE], dict):
          self.postReplace[elem].append(rhs[elem][self.TEMPLATE_FILE_RULE_REPLACE])
#           logger.debug("!!! rhs self.postReplace: %s", str(rhs[elem][self.TEMPLATE_FILE_RULE_REPLACE]))
#           logger.debug("!!! self.postReplace: %s", str(self.postReplace))

        self.postExclude[elem] = []
        if elem in lhs and self.TEMPLATE_FILE_RULE_EXCLUDE in lhs[elem] and \
          isinstance(lhs[elem][self.TEMPLATE_FILE_RULE_EXCLUDE], list):
          self.postExclude[elem].extend(lhs[elem][self.TEMPLATE_FILE_RULE_EXCLUDE])

        if elem in rhs and self.TEMPLATE_FILE_RULE_EXCLUDE in rhs[elem] and \
          isinstance(rhs[elem][self.TEMPLATE_FILE_RULE_EXCLUDE], list):
          self.postExclude[elem].extend(rhs[elem][self.TEMPLATE_FILE_RULE_EXCLUDE])

#         logger.debug("!!! self.postExclude['%s']: %s", str(elem), str(self.postExclude[elem]))

        lXpathList = []
        rXpathList = []

        if elem in lhs and isinstance(lhs[elem], dict) and self.TEMPLATE_FILE_RULE_XPATH in lhs[elem] and isinstance(lhs[elem][self.TEMPLATE_FILE_RULE_XPATH], list):
          lXpathList = lhs[elem][self.TEMPLATE_FILE_RULE_XPATH]

        if elem in lhs and isinstance(lhs[elem], list):
          lXpathList = lhs[elem]

        if elem in rhs and isinstance(rhs[elem], dict) and self.TEMPLATE_FILE_RULE_XPATH in rhs[elem] and isinstance(rhs[elem][self.TEMPLATE_FILE_RULE_XPATH], list):
          rXpathList = rhs[elem][self.TEMPLATE_FILE_RULE_XPATH]

        if elem in rhs and isinstance(rhs[elem], list):
          rXpathList = rhs[elem]

#         logger.debug("!!! lXpathList: %s", varDump(lXpathList))
#         logger.debug("!!! rXpathList: %s", varDump(rXpathList))

        lhs[elem] = lXpathList + rXpathList
#         logger.debug("!!! lhs[elem]: %s", varDump(lhs[elem]))


  # #Common method of prepared templates extract
  #
  # @param jsonBuf - incoming json with templates
  # @param domains - domains list
  # @param globalTemplate - incoming templates
  # @return template dict, that corresponds incoming domainCrc or "*"
  def templatePreparer(self, jsonBuf, domains, globalTemplate):
    ret = {}
    if len(globalTemplate) == 0:
      try:
        globalTemplate = json.loads(jsonBuf)
      except Exception, err:
        logger.error(">>> Wrong json format. %s", str(err))

    if len(globalTemplate) > 0:
      try:
        if domains is not None:
#           logger.debug("!!! domains: '%s', type: %s", str(domains), str(type(domains)))
#           logger.debug("!!! globalTemplate: '%s'", str(globalTemplate))
#           logger.debug("!!! type(globalTemplate): '%s'", str(type(globalTemplate)))
          if isinstance(domains, basestring):
            domains = [domains]

          for domain in domains:
            for pattern in globalTemplate:
              try:
                searchPatterns = pattern.split()
                # logger.debug("!!! searchPatterns: '%s'", str(searchPatterns))
                found = False
                for searchPattern in searchPatterns:
                  if searchPattern != '*':
                    if re.search(searchPattern, domain, re.UNICODE) is not None:
                      logger.debug("!!! Found pattern: '%s'", str(pattern))
                      if isinstance(globalTemplate[pattern], dict):
                        ret = globalTemplate[pattern]
                        found = True
                        break

                if found:
                  break
              except Exception, err:
                logger.debug("Regular expression error: %s, pattern: '%s', domain: '%s'",
                             str(err), str(pattern), str(domain))

            # If was fail use old algorithm
            if len(ret) == 0 and domain in globalTemplate and isinstance(globalTemplate[domain], dict):
              ret = globalTemplate[domain]

        if domains is not None:
          for domain in domains:
            if len(ret) == 0:
              while domain.find(".") != -1:
                domain = domain[domain.find(".") + 1: len(domain)]
                if domain is not None and domain in globalTemplate:
                  self.pasteLists(ret, globalTemplate[domain])
              if domain is not None and domain in globalTemplate:
                self.pasteLists(ret, globalTemplate[domain])

        domain = "*"
        if domains is not None and domain in globalTemplate:
          self.pasteLists(ret, globalTemplate[domain])

      except Exception, err:
        ExceptionLog.handler(logger, err, 'Exception: ', (ret))

    for key, value in ret.items():
      if isinstance(value, list):
        removeList = []
        for elemXPath in value:
          if elemXPath != "" and elemXPath[0] in self.DISABLE_XPATH_CHARS_LIST:
            removeList.append(elemXPath)

        for removeElem in removeList:
          value.remove(removeElem)
          logger.debug("For '%s' found disabled xpath: %s", str(key), str(removeElem))

    return ret


  # #extractTag method extracts for concrete tag
  #
  # @param tagName - incoming tag name
  # @param result - incoming result object
  # @param textHandler - optionality param with text processing callback function
  # @param delimiter - optionality delimiter between extracted elements
  def extractTag(self, tagName, result, template, textHandler=None, delimiter=' '):
    try:
      if tagName in template:
        for path in template[tagName]:
#           logger.debug("!!! ENTER tagName: %s, xpath: '%s'", str(tagName), str(path))

          if tagName in self.blockedByXpathTags:
            break

          if path == "":
            if tagName not in result.blockedByXpathTags:
              result.blockedByXpathTags.append(tagName)
            break
          elif path == "none":
            if tagName not in self.blockedByXpathTags:
              self.blockedByXpathTags.append(tagName)
            break
          if textHandler is not None:
            conditions = None
            if self.tagsValidator is not None and self.name in self.tagsValidator and \
            tagName in self.tagsValidator[self.name]:
              conditions = self.tagsValidator[self.name][tagName]
            localValue = textHandler(self.sel.xpath(path), delimiter, delimiter, self.innerTextTagReplacers, conditions,
                                     keepAttributes=self.keepAttributes, baseUrl=self.resource.url,
                                     closeVoid=self.closeVoid, excludeNodes=self.postExclude[tagName] if tagName in self.postExclude else None)
          else:
            localValue = self.sel.xpath(path).extract()

#           if tagName == 'content_encoded':
#             logger.debug("!!! tagName: %s", str(tagName))
#             logger.debug("!!! xpath: %s", str(path))
#             logger.debug("!!! value: '%s'", str(localValue))


#           if tagName == 'title' or tagName == 'html_lang':
#             logger.debug("!!! tagName: %s", str(tagName))
#             logger.debug("!!! xpath: %s", str(path))
#             logger.debug("!!! value: '%s'", varDump(localValue))

          # apply post-processing
          if isinstance(self.postReplace, dict) and tagName in self.postReplace and \
            isinstance(self.postReplace[tagName], list) and localValue != "":
#             if len(localValue) > 0:
#               logger.debug("!!! localValue before: %s", varDump(localValue))
#               logger.info("POST PROCESSING FOR TAG '%s', len = %s", str(tagName), len(localValue))
            for postReplace in self.postReplace[tagName]:
              if isinstance(postReplace, dict):
                for pattern, repl in postReplace.items():
                  if isinstance(pattern, basestring) and isinstance(repl, basestring):
#                     logger.debug("!!! pattern: '%s', repl: '%s'", str(pattern), str(repl))
                    localValue = re.sub(pattern=pattern, repl=repl, string=localValue, flags=re.U + re.M + re.I + re.DOTALL)
#                     logger.debug("!!! localValue after replace: %s", varDump(localValue))

          if isinstance(localValue, basestring):
            localValue = localValue.decode('utf-8')

          if tagName == CONSTS.TAG_LINK:
            urlObj = Url(localValue)
            if urlObj.isValid():
              self.addTag(result=result, tag_name=tagName, tag_value=localValue, xpath=path)
          else:
            self.addTag(result=result, tag_name=tagName, tag_value=localValue, xpath=path)

    except Exception, err:
      ExceptionLog.handler(logger, err, 'Exception in ScrapyExtractor.extractTag:')


  # #extractTagsForOneTemplate method extract data by tags for one template and fills incoming result object
  #
  # @param resource - incoming raw data
  # @param result - incoming result object
  # @param template - current template
  # @return incoming result with additionally filled fields/tags
  def extractTagsForOneTemplate(self, resource, result, template):
    try:
      self.resource = resource
#       logger.debug("URL: %s \nresource.raw_html: %s ", self.resource.url, resource.raw_html[:255])
      self.sel = SelectorWrapper(text=resource.raw_html)

      # search engine parsing
#       logger.debug("Regular parsing")
      self.extractTag(CONSTS.TAG_TITLE, result, template, Utils.innerText)
      self.extractTag(CONSTS.TAG_AUTHOR, result, template, Utils.innerText)
      self.extractTag(CONSTS.TAG_PUB_DATE, result, template)
      self.extractTag(CONSTS.TAG_DESCRIPTION, result, template, Utils.innerText)
      self.extractTag(CONSTS.TAG_DC_DATE, result, template)
      self.extractTag(CONSTS.TAG_MEDIA, result, template, Utils.innerText, self.imgDelimiter)
      self.extractTag(CONSTS.TAG_LINK, result, template, Utils.innerText)
      self.extractTag(CONSTS.TAG_CONTENT_UTF8_ENCODED, result, template, Utils.innerText)

      # for path in template["enclosure"]]
      self.extractTag(CONSTS.TAG_KEYWORDS, result, template, Utils.innerText)
      # Add support of html_lang tag
      self.extractTag(CONSTS.HTML_LANG, result, template, Utils.innerText)

    except Exception as err:
      ExceptionLog.handler(logger, err, "Parse error:", (err))

    return result


  # #extractTags public method extract data by tags and fills incoming result object
  #
  # @param resource - incoming raw data
  # @param result - incoming result object
  # @return incoming result with additionally filled fields/tags
  def extractTags(self, resource, result):
    self.blockedByXpathTags = []
    localResults = []
    for templateDict in self.templates:
      for templateName in templateDict:
        localResult = copy.deepcopy(result)
        self.extractTagsForOneTemplate(resource, localResult, templateDict[templateName])
        localResults.append(localResult)
        break

    for localResult in localResults:
      result.mergeResults(localResult)

    return result
