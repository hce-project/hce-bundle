'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

# import dc_processor.Constants as Constants
from app.SelectorWrapper import SelectorWrapper
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

class TemplateExtractorXPathPreparing(object):

  def __init__(self, innerTextTagReplacers=None, attrConditions=None):
    self.innerTextTagReplacers = innerTextTagReplacers
    self.attrConditions = attrConditions


  # #resolveDelimiter method resolves content delimiter bases on path["delimiter"] value
  #
  # @param path - path container from incoming json
  # @param defautlDelimiter - incoming default delimiter
  # @return just resolved delimiter
  def resolveDelimiter(self, path, properties, defautlDelimiter=" "):
    ret = defautlDelimiter
    if "delimiter" in path and path["delimiter"]:
      ret = path["delimiter"]
    elif "SCRAPER_TAG_ITEMS_DELIMITER" in properties:
      ret = properties["SCRAPER_TAG_ITEMS_DELIMITER"]
    elif path["type"] == "text" or path["type"] == "html":
      ret = ' '
    else:
      ret = ','
    return ret


  # #resolveInnerDelimiter method resolves content innerDelimiter bases on path["delimiter"] value
  #
  # @param path - path container from incoming json
  # @param defautlDelimiter - incoming default delimiter
  # @return just resolved delimiter
  def resolveInnerDelimiter(self, path, properties, defautlDelimiter=" "):
    ret = defautlDelimiter
    if "delimiter_sub_items" in path and path["delimiter_sub_items"]:
      ret = path["delimiter_sub_items"]
    elif "SCRAPER_TAG_ITEMS_INNER_DELIMITER" in properties:
      ret = properties["SCRAPER_TAG_ITEMS_INNER_DELIMITER"]
    elif path["type"] == "text" or path["type"] == "html":
      ret = ' '
    else:
      ret = ','
    return ret


  # #process main class's functional method
  #
  # @param path - path container from incoming json
  # @param sel - incoming x-path selector
  # @param delimiter - delimiter used for processing
  # @param innerDelimiter - inner delimiter used for processing
  # @param innerTextFunc - function pointer used innerText extraction algorithm
  # @return tuple of extracted (xpath, xpathValue) elements
  def process(self, path, sel, delimiter=' ', innerDelimiter=' ', innerTextFunc=Utils.innerText):
    xpath = None
    xpathValue = None
    # Added new template type specification
    #---> "text" rule type.
    if path["type"] == "text":
      localXpath = sel.xpath(path["target"])
      xpathValue = innerTextFunc(localXpath, delimiter, innerDelimiter, self.innerTextTagReplacers, None,
                                 self.attrConditions)
      xpath = path["target"]
    #---> "datetime" rule type.
    elif path["type"] == "datetime":
      xpath, xpathValue = self.getXpathValueForDTime(path["target"], sel, innerTextFunc)
      logger.info(">>> final XPath = " + str(xpathValue))
    #---> "image" rule type.
    elif path["type"] == "image":
      logger.info(">>> img format = " + str(path["format"]))
      if path["target"][0] not in SelectorWrapper.CSS_DETECT_SYMBOLS:
        if path["format"] == "URL":
          if path["target"].find('/@') == -1:
            localXPathPattern = '/@%s'
            subXPathesList = ['src', 'srcset', 'image-src']
            xpath, xpathValue = Utils.getFirstNotEmptySubXPath(path["target"], sel, localXPathPattern, subXPathesList)
        elif path["format"] == "DATA":
          pass
        elif path["format"] == "ALT":
          xpath = path["target"] + "/@alt"
        elif path["format"] == "TITLE":
          xpath = path["target"] + "/@title"
    #---> "html" rule type.
    elif path["type"] == "html":
      pass
    #---> "link" rule type.
    elif path["type"] == "link":
      if path["target"][0] not in SelectorWrapper.CSS_DETECT_SYMBOLS:
        formatName = path["format"]
        if len(formatName.split(',')) > 1:
          formatName = formatName.split(',')[1]
        if formatName == "email-text":
          isEmail = False
          if not Utils.isTailSubstr(path["target"], "/@href"):
            localXpath = path["target"] + "/@href"
            xpathValue = sel.xpath(localXpath).extract()
            for xpathValueElem in xpathValue:
              if isinstance(xpathValueElem, basestring) and xpathValueElem.find("mailto:") >= 0:
                isEmail = True
                break
          if isEmail:
            localXpath = sel.xpath(path["target"])
            xpathValue = innerTextFunc(localXpath, delimiter, innerDelimiter, self.innerTextTagReplacers, None,
                                       self.attrConditions)
          else:
            xpathValue = []
          xpath = path["target"]
        else:
          if not Utils.isTailSubstr(path["target"], "/@href"):
            xpath = path["target"] + "/@href"
    #---> "attribute" rule type.
    elif path["type"] == "attribute":
      if path["format"] == "":
        xpathValue = []
      else:
        splittedFormatString = path["format"].split(',')
        attrName = None
        if len(splittedFormatString) >= 2:
          attrName = splittedFormatString[1]
        else:
          attrName = splittedFormatString[0]
        if path["target"].rfind(attrName) == -1 or \
        (len(path["target"]) - len(attrName)) != path["target"].rfind(attrName):
          xpath = path["target"]
          xpath += "/@"
          xpath += attrName
    if xpath is None:
      xpath = path["target"]

    if xpathValue is None:
      try:
        xpathValue = sel.xpath(xpath).extract()
      except Exception as excp:
        logger.info(">>> Common xPath extractor exception=" + str(excp))
        xpathValue = []

    return xpath, xpathValue


  # #getXpathValueForDTime special method af data extracting in datatime cases
  #
  # @param initXpath - initial element's xPath
  # @param sel - incoming selector
  # @param innerTextFunc - function pointer used innerText extraction algorithm
  # @return tuple of extracted (xpath, xpathValue) elements
  def getXpathValueForDTime(self, initXpath, sel, innerTextFunc=Utils.innerText):
    xpath = initXpath
    localXpath = sel.xpath(xpath)
    logger.info(">>> Datetime | Meta extraction")
    xpathValue = self.extractXpathFromSelectorList(localXpath, "@content", \
                                                   lambda elem: elem.extract().find("<meta") == 0)
    if len(xpathValue) == 0:
      logger.info(">>> Datetime | any tag @datetime argument extraction")
      xpathValue = self.extractXpathFromSelectorList(localXpath, "@datetime", \
                                                     lambda elem: elem.extract().find("<time") == 0)
      if len(xpathValue) == 0:
        logger.info(">>> Datetime | inner Text Extraction")
        localStr = innerTextFunc(localXpath, ' ', ' ', self.innerTextTagReplacers, None, self.attrConditions)
        if localStr != '':
          xpathValue = [localStr]
    return xpath, xpathValue


  # #extractXpathFromSelectorList returns first xPath in case of selector List
  #
  # @param sList - incoming selectors list
  # @param localXpath - incoming xPath
  # @param lambdaCall - boolean lambda call for checking elements in sList
  # @return extracted xPath
  def extractXpathFromSelectorList(self, sList, localXpath, lambdaCall):
    ret = []
    for elem in sList:
      if lambdaCall(elem):
        ret = elem.xpath(localXpath).extract()
        if len(ret) > 1 and any(True for ch in ret if ch >= '0' and ch <= '9'):
          ret = [ret[0]]
          break
    return ret
