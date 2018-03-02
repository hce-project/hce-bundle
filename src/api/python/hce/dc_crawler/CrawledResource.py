"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file CrawledResource.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from dc.EventObjects import URL
# #The CrawledResource class
#
#
class CrawledResource(object):


  def __init__(self):
    # rendered unicode content for dynamic fetcher
    self.html_content = ""
    self.binary_content = ""
    self.response_header = ""
    self.html_request = ""
    self.content_type = URL.CONTENT_TYPE_UNDEFINED
    self.charset = ""
    self.error_mask = 0
    self.crawling_time = 0
    self.http_code = 200
    self.bps = 0
    self.last_modified = ""
    self.etag = ""
    self.resource_changed = True
    # before rendered unicode content for dynamic fetcher
    self.meta_content = ""
    self.cookies = {}
    self.dynamic_fetcher_type = None
    self.dynamic_fetcher_result_type = None

