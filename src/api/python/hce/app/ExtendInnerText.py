'''
Created on Mar 28, 2014

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import types
import logging
import re
import app.Consts as APP_CONSTS
from app.SelectorWrapper import SelectorWrapper

logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


class ExtendInnerText(object):

  NONE_CLOSED_HTML_TAGS = ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link',
                           'meta', 'param', 'source', 'track', 'wbr']

  CANONIZATION_TAGS = ['href', 'src']

  MACRO_ATTRIBUTES = '%ATTRIBUTES%'
  
  PATTERN_CLOSE_VOID = r"<%s.*?(/)>"
  
  CLOSE_VOID_NOT_CLOSE=0
  CLOSE_VOID_CLOSE=1
  CLOSE_VOID_AUTO=2

  def __init__(self, tagReplacers=None, delimiter=' ', innerDelimiter=' ', REconditions=None, attrConditions=None,
               keepAttributes=None, baseUrl=None, closeVoid=None, excludeNodes=None):
    self.stripHtml = ''
    self.stripHtmlList = []
    self.errorString = ''
    self.delimiter = delimiter
    self.innerDelimiter = innerDelimiter
    self.REconditions = REconditions
    self.attrConditions = attrConditions
    self.tagReplacers = tagReplacers 
    self.keepAttributes = keepAttributes
    self.baseUrl = baseUrl
    self.closeVoid = closeVoid 
    self.excludeNodes = excludeNodes


  def nodeCallbackOpenHandler(self, nodeElem, level):  # pylint: disable=W0613
    openTagName = str(nodeElem.xpath("name()")[0].extract())

#     logger.info("self.tagReplacers: %s", str(self.tagReplacers))
#     logger.info("openTagName: %s", str(openTagName))
       
    if self.tagReplacers is None:

      if self.MACRO_ATTRIBUTES in openTagName:
        self.stripHtml += '<' + openTagName.replace(self.MACRO_ATTRIBUTES, self.extractAttributes(nodeElem, \
                          openTagName, self.keepAttributes, self.baseUrl)) + self.applyCloseVoid(nodeElem, openTagName) + '>'
      elif openTagName != "":
        self.stripHtml += '<' + openTagName + self.extractAttributes(nodeElem, openTagName, self.keepAttributes, \
                          self.baseUrl) + self.applyCloseVoid(nodeElem, openTagName) + '>'

#       logger.info("self.stripHtml1: %s", str(self.stripHtml))
    else:
      if openTagName in self.tagReplacers:
        self.stripHtml += self.tagReplacers[openTagName].replace(self.MACRO_ATTRIBUTES, \
                          self.extractAttributes(nodeElem, openTagName, self.keepAttributes, self.baseUrl))

#       logger.info("self.stripHtml2: %s", str(self.stripHtml))

#     logger.info("!!! nodeElem.xpath('name(@href)').extract() = %s", str(nodeElem.xpath('name(@href)').extract()))
#     logger.info("!!! nodeElem.xpath('@href').extract() = %s", str(nodeElem.xpath('@href').extract()))


  def nodeCallbackCloseHandler(self, nodeElem, level):  # pylint: disable=W0613
    closeTagName = str(nodeElem.xpath("name()")[0].extract())
#     logger.info("closeTagName: %s", str(closeTagName))
    if self.tagReplacers is None and closeTagName not in self.NONE_CLOSED_HTML_TAGS and closeTagName != "":
      self.stripHtml += '</' + closeTagName + '>'
    else:
      closeTag = "</" + closeTagName + ">"
      if (len(str(nodeElem.extract())) >= len(closeTag)) and \
      str(nodeElem.extract()).rfind(closeTag) == (len(str(nodeElem.extract())) - len(closeTag)):
        closeTagName = '/' + closeTagName
        if self.tagReplacers is not None and closeTagName in self.tagReplacers:
          self.stripHtml += self.tagReplacers[closeTagName]


  def textCallbackHandler(self, nodeElem, level, excludeTags): # pylint: disable=W0613
#     logger.debug("excludeTags: %s", str(excludeTags))

    buff = str(nodeElem.extract())
    if buff.strip() != "":
      for excludeTag in excludeTags:
        if excludeTag != "":
          pattern = '<' + excludeTag + '.*>'
          buff = re.sub(pattern=pattern, repl='', string=buff, flags=re.I + re.U + re.M)

      if self.tagReplacers is None:
        self.stripHtml += buff
      else:
        self.stripHtml += buff + self.innerDelimiter
#       self.stripHtml += str(nodeElem.extract()) + self.innerDelimiter


  def innerText(self, contentBuf, xPath, tagRemoves=None):
    self.stripHtml = ''
    self.errorString = ''
    if xPath is not None:
      if tagRemoves is None:
        tagRemoves = ['script', 'style', '']
      try:
        if isinstance(xPath, basestring):
          sel = SelectorWrapper(text=contentBuf)
          selectorElem = sel.xpath(xPath)
        else:
          selectorElem = xPath
        localBuf = ''

        for elem in selectorElem:
          if self.REconditions is not None:
            if (self.REconditions["type"] == "include" and re.compile(self.REconditions["RE"]).match(elem) is None) or \
            (self.REconditions["type"] == "exclude" and re.compile(self.REconditions["RE"]).match(elem) is not None):
              continue
          self.stripHtml = ''
          elemList = []
          elemList.append(elem)
          ExtendInnerText.traversalNodes(elemList, 0, self.nodeCallbackOpenHandler, self.nodeCallbackCloseHandler,
                                         self.textCallbackHandler, tagRemoves, self.attrConditions, self.excludeNodes)
          localBuf += self.stripHtml.strip(self.innerDelimiter)
          localBuf += self.delimiter

        self.stripHtml = localBuf.strip(self.delimiter)
      except Exception as excp:
        self.errorString = str(excp)
        logger.error("!!! Exception: %s", str(self.errorString))
        import app.Utils as Utils
        logger.info(Utils.getTracebackInfo())


  @staticmethod
  def checkElemAttributes(attrConditions, elem):
    ret = True
    if attrConditions is not None:
      if attrConditions["TYPE"] == "include":
        ret = False
      i = 1
      attrList = elem.xpath("@*")
      if len(attrList) > 0:
        for internalElem in attrList:
          for key in attrConditions:
            attrName = "".join(elem.xpath("name(@*[%s])" % str(i)).extract())
            if key != "type" and (key == "*" or key == attrName) and \
            re.compile(attrConditions[key]).match(internalElem.extract()):
              ret = not ret
              break
          i += 1
      elif "NO_ATTRIBUTES" in attrConditions:
        ret = True
    return ret


  @staticmethod
  def traversalNodes(elemList, level=0, nodeCallbackOpen=None, nodeCallbackClose=None, textCallback=None,
                     excludeTags=None, attrConditions=None, excludeNodes=None):
    if excludeTags is None:
      excludeTags = ['script', 'style', '']
    # print str(level) + " " + str(len(elemList))

#     logger.debug("elemList: %s", str(elemList))
#     logger.debug("excludeNodes: %s", str(excludeNodes))
    for elem in elemList:

      if not ExtendInnerText.checkElemAttributes(attrConditions, elem):
        continue
      
      if ExtendInnerText.isExcludeNode(excludeNodes, elem):
        continue

      if len(elem.xpath("name()")) > 0:
        if nodeCallbackOpen is not None and str(elem.xpath("name()")[0].extract()) not in excludeTags:
          nodeCallbackOpen(elem, level)
          
          
        if str(elem.xpath("name()")[0].extract()) not in excludeTags:
          ExtendInnerText.traversalNodes(elem.xpath("node()"), level + 1, nodeCallbackOpen, nodeCallbackClose,
                                         textCallback, excludeTags, attrConditions, excludeNodes)
        if nodeCallbackClose is not None and str(elem.xpath("name()")[0].extract()) not in excludeTags:
          nodeCallbackClose(elem, level)
      else:
        if textCallback is not None:
          textCallback(elem, level, excludeTags)


  def innerTextToList(self, contentBuf, xPath, tagRemoves=None):
    stripHtmlList = []
    self.stripHtml = ''
    self.errorString = ''
    if xPath is not None:
      if tagRemoves is None:
        tagRemoves = ['script', 'style', '']
      try:
        if isinstance(xPath, types.StringTypes):
          sel = SelectorWrapper(text=contentBuf)
          selectorElem = sel.xpath(xPath)
        else:
          selectorElem = xPath

        for elem in selectorElem:
          if self.REconditions is not None:
            if (self.REconditions["type"] == "include" and re.compile(self.REconditions["RE"]).match(elem) is None) or \
            (self.REconditions["type"] == "exclude" and re.compile(self.REconditions["RE"]).match(elem) is not None):
              continue
          self.stripHtml = ''
          elemList = []
          elemList.append(elem)
          ExtendInnerText.traversalNodes(elemList, 0, self.nodeCallbackOpenHandler, self.nodeCallbackCloseHandler,
                                         self.textCallbackHandler, tagRemoves, self.attrConditions, self.excludeNodes)

          stripHtmlList.append((self.stripHtml.strip(self.innerDelimiter) + self.delimiter).strip(self.delimiter))

        self.stripHtmlList = stripHtmlList
      except Exception as excp:
        self.errorString = str(excp)


  # extract attributes for tag
  #
  # @param nodeElem - node element
  # @param tagName - tag name
  # @param keepAttributes - dictionary with lists attributes for each tags
  # @param baseUrl - base url
  def extractAttributes(self, nodeElem, tagName, keepAttributes, baseUrl, htmlEntitiesEncode=True, urlEncode=True):
    # variable for result
    ret = ''

#     logger.info("!!! tagName = %s", str(tagName))
    import app.Utils
    if keepAttributes is not None and tagName in keepAttributes.keys():
      attrList = keepAttributes[tagName]
      values = []
      for attrName in attrList:
        value = nodeElem.xpath('@' + attrName).extract()
        logger.info("!!! for %s extracted: %s", str(attrName), str(value))
        if len(value) > 0 and value[0] != "":
          if attrName in self.CANONIZATION_TAGS:
            if urlEncode:
              value[0] = value[0].replace(' ', '%20')
              value[0] = value[0].replace('<', '%3C') # &lt;')
              value[0] = value[0].replace('>', '%3E') # &gt;')
              value[0] = value[0].replace('"', '%22') # &quot;')
          else:
            value[0] = value[0].replace('<', '&lt;')
            value[0] = value[0].replace('>', '&gt;')
            value[0] = value[0].replace('"', '&quot;')

            value[0] = app.Utils.urlNormalization(baseUrl, value[0])
#             logger.info("!!! After normalization: %s", str(value[0]))

          values.append(attrName + '="' + value[0].replace('\n', ' ').replace('"', '\\\"') + '"')

      # ret = "<" + tagName + ' ' + ' '.join(values) + '>'
      ret = ' ' + ' '.join(values)

#     logger.debug("!!! return: '%s'", str(ret))
    return ret


  # # apply close void
  #
  # @param nodeElem - node element
  # @param tagName - tag name
  # @return - string value accord to necessary algorithm
  def applyCloseVoid(self, nodeElem, tagName):
    # variable for result
    ret = ''
    
    if tagName in self.NONE_CLOSED_HTML_TAGS:
      closeVoid = self.CLOSE_VOID_NOT_CLOSE
      if self.closeVoid is not None:
        closeVoid = int(self.closeVoid) 
      
      if closeVoid == self.CLOSE_VOID_NOT_CLOSE:
        ret = ''
      elif closeVoid == self.CLOSE_VOID_CLOSE:   
        ret = '/'
      elif closeVoid == self.CLOSE_VOID_AUTO: 
#         logger.info("!!!!! BEFORE nodeElem.select()")
#         for sel in nodeElem.select('//*'):
#           logger.info("!!!!! sel: '%s'", str(sel.extract()))  
        
        logger.info("!!!!! nodeElem.extract(): '%s'", str(nodeElem.extract()))  
        pattern = self.PATTERN_CLOSE_VOID % str(tagName)
        logger.info("!!!!! pattern: '%s'", str(pattern)) 
        res = nodeElem.re(pattern)
        logger.info("!!!!! nodeElem.re(pattern): '%s'", str(res))
        if len(res) > 0:
          ret = '/'
    
    return ret    
    
    
  ## check is exlude node
  #
  # @param excludeNodes - dictionary with criterion for exclude
  # @param elem - element for check
  # @return True if necessary exclude or False otherwise
  @staticmethod
  def isExcludeNode(excludeNodes, elem):
    # variable for result
    ret = False
#     logger.debug("!!! excludeNodes: %s, type: %s", str(excludeNodes), str(type(excludeNodes)))

    if len(elem.xpath("name()")) > 0:
      nodeName = str(elem.xpath("name()")[0].extract())
#       logger.debug("!!! nodeName: %s, type: %s", str(nodeName), str(type(nodeName)))

      import app.Utils as Utils

      if isinstance(excludeNodes, list):
        for excludeNode in excludeNodes:
          if isinstance(excludeNode, dict):
            for tagName, attributes in excludeNode.items():
#               logger.debug("!!! tagName: %s, attributes: %s", str(tagName), str(attributes))
              if Utils.reMatch(tagName, nodeName, logger):
#                 logger.debug("tagName: %s == nodeName: %s", str(tagName), str(nodeName))
                if attributes is None:
                  logger.debug("Found exclude node rule for '%s' with attributes: %s", str(tagName), str(attributes))
                  ret = True
                  break

                if isinstance(attributes, dict):
                  for attrName, attrValue in attributes.items():
  #                   logger.debug("!!! attrName: %s, attrValue: %s", str(attrName), str(attrValue))
                    values = elem.xpath('@' + attrName).extract()
  #                   logger.debug("!!! values: %s" , str(values))

                    found = False
                    for value in values:
                      if Utils.reMatch(attrValue, value, logger):
                        logger.debug("Found exclude node rule for '%s' with attributes: %s", str(tagName), str(attributes))
                        found = True
                        break

                    if found:
                      ret = True
                      break

#     logger.info("ret: %s", str(ret))
    return ret
