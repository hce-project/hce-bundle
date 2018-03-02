'''
Created on Nov 19, 2015

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import logging
from scrapy.selector import Selector
from scrapy.selector import SelectorList

import app.Consts as APP_CONSTS


logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


# # SelectorWrapper implements wrapper for Selector module functionallity (xpath or css extraction)
#
class SelectorWrapper(Selector):

  # XPATH_DETECT_SYMBOL = '/'
  # SPECIAL_XPATHES = ["name()", "node()"]
  CSS_DETECT_SYMBOLS = ['.', '#']

  # #Class's constructor
  #
  # @param text incoming text buf with document (xml or html) structute
  def __init__(self, response=None, text=None, type=None, namespaces=None, _root=None, _expr=None):  # pylint: disable=W0622
    super(SelectorWrapper, self).__init__(response, text, type, namespaces, _root, _expr)


  # #Method xpath deliveries wrapper for Selector interface
  #
  # @param xpathStr - incoming xpath or css selector string
  # @return instance of SelectorWrapper which contains Selector with result of xpathStr appluing
  def xpath(self, xpathStr):
    retSelector = SelectorList([])
    if xpathStr is not None and isinstance(xpathStr, basestring) and len(xpathStr) > 0:
      # if xpathStr[0] == self.XPATH_DETECT_SYMBOL or xpathStr in self.SPECIAL_XPATHES:
      if xpathStr[0] in self.CSS_DETECT_SYMBOLS:
        retSelector = super(SelectorWrapper, self).css(xpathStr)
      else:
        retSelector = super(SelectorWrapper, self).xpath(xpathStr)
    else:
      retSelector = super(SelectorWrapper, self).xpath(xpathStr)

    return retSelector
