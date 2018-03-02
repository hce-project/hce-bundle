"""@package docstring
 @file scraper_resource.py
 @author Alexey <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""


# import json


class Resource(object):


  def __init__(self, resource_set):
    self.url = resource_set["url"]
    self.raw_html = resource_set["raw_html"]
    self.site_id = resource_set["siteId"]
    self.res_id = resource_set["resId"]


  def __str__(self):
    return "%s" % (self.url)


  def __repr__(self):
    return repr((self.url, self.raw_html))
