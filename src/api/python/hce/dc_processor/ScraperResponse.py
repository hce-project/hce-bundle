"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file ScraperResponse.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


# #The ScraperInData class
#
#
class ScraperResponse(object):


  def __init__(self, TagsCount, TagsMask, pubdate, processedContent, errorMask=0):
    self.tagsCount = TagsCount
    self.tagsMask = TagsMask
    self.pubdate = pubdate
    self.processedContent = processedContent
    self.errorMask = errorMask
