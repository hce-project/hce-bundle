"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file ScraperInData.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


# #The ScraperInData class
#
#
class ScraperInData(object):


  def __init__(self,
               url,
               urlId,
               siteId,
               raw_content,
               template,
               filters,
               lastModified,
               timezone,
               batchId,
               dbMode,
               batch_item=None,
               processor_properties=None,
               output_format=None):
    self.url = url
    self.urlId = urlId
    self.siteId = siteId
    self.raw_content = raw_content
    self.template = template
    self.filters = filters
    self.lastModified = lastModified
    self.timezone = timezone
    self.batchId = batchId
    self.dbMode = dbMode
    self.batch_item = batch_item
    self.processor_properties = processor_properties
    self.output_format = output_format
