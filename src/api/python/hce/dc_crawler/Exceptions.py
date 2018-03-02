'''
Created on July 29, 2016

@package: dc_crawler
@file Exceptions.py
@author: Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

# # Exceptions module keepts exceptions for crawler module
class SyncronizeException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class CrawlerException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class InternalCrawlerException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class CrawlerFilterException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)
