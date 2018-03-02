"""
@package: dc
@file RobotsParser.py
@author Scorp <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import requests
import dc_crawler.OwnRobots as OwnRobots
import app.Utils as Utils  # pylint: disable=F0401
from app.LFSDataStorage import LFSDataStorage

logger = Utils.MPLogger().getLogger()

# #The RobotsParser performs parsing robots.txt file and checking current url by it rule.
#
class RobotsParser(object):

  ROBOTS_PATTERN = re.compile(r'(https?://[^/]+).*', re.I)
  USER_AGENT_HEADER_NAME = "User-Agent"
  HTTP_OK_CODE = 200

  # #RobotsParser class constructor
  #
  # @param headers sets default value for user-agent http header
  def __init__(self, headers=None, isCacheUsing=False, robotsFileDir=None):
    self.localParser = None
    self.headers = ["*"]
    self.robotsFileDir = None
    self.cacheElement = None
    self.cacheElementKeys = None
    self.localCrawlerDataStorage = None
    self.initFiends(headers, isCacheUsing, robotsFileDir)


  # #initFiends makes class fields initialization (not default)
  #
  # @param headers - external header initialization
  # @param isCacheUsing - bool value use internal cache ot not
  # @param robotsFileDir - path to cache file storage
  def initFiends(self, headers=None, isCacheUsing=False, robotsFileDir=None):
    if headers is None:
      self.headers = ["*"]
    else:
      self.headers = headers
    self.robotsFileDir = robotsFileDir
    if isCacheUsing:
      self.localCrawlerDataStorage = LFSDataStorage()
    else:
      self.localCrawlerDataStorage = None


  # #loadRobots method loads robots.txt file for current domain (sets in the url param)
  #
  # @param url, urls that contains domain for robots.txt fetching
  # @param siteId - Site ID
  # @param additionHeaders - addition headers
  # @param proxyName - proxy host and port as string (sample: '127.0.0.1:80')
  # @return bool value - was robots.txt successful opened or wasn't
  def loadRobots(self, url, siteId=None, additionHeaders=None, proxyName=None):
    if additionHeaders is None:
      additionHeaders = {}
    contentBuf = None
    if self.localCrawlerDataStorage is not None and self.robotsFileDir is not None and siteId is not None:
      host = Utils.UrlParser.getDomain(url)
      if host is not None:
        self.cacheElement = self.localCrawlerDataStorage.loadElement(self.robotsFileDir, host, siteId)
        if self.cacheElement is not None:
          self.cacheElementKeys = None
          cek = self.localCrawlerDataStorage.fetchLowFreqHeaders(fileStorageElements=self.cacheElement,
                                                                 fileCacheOnly=True)
          if len(cek) > 0 and cek[0][0] == "robots.txt":
            self.cacheElementKeys = cek[0]
            contentBuf = self.cacheElementKeys[1]
    if contentBuf is None:
      robotsUrl = self.ROBOTS_PATTERN.sub(r'\1/robots.txt', url)
      logger.info(">>> robotsUrl: " + robotsUrl)
      try:
        if proxyName is not None and proxyName:
          response = requests.get(robotsUrl, headers=additionHeaders, allow_redirects=True,
                                  proxies={"http": "http://" + proxyName})
        else:
          response = requests.get(robotsUrl, headers=additionHeaders, allow_redirects=True)
        if response is not None and response.status_code == self.HTTP_OK_CODE:
          contentBuf = response.content
        else:
          logger.info(">>> robots.txt loading error, response is None or status_code not 200")
      except Exception as excp:
        logger.info(">>> robots.txt loading error = " + str(excp))

    if contentBuf is not None:
      self.localParser = OwnRobots.RobotExclusionRulesParser()
      self.localParser.parse(contentBuf)
    return not self.localParser is None


  # #checkUrlByRobots check incoming url in preloaded robots.txt
  #
  # @param headers
  # @return is collect successfully
  def checkUrlByRobots(self, url, siteId=None, headers=None):
    isAllowed = True
    retUserAgent = None
    if self.localParser is not None:
      if headers is not None and self.USER_AGENT_HEADER_NAME in headers and \
      headers[self.USER_AGENT_HEADER_NAME] is not None:
        self.headers = [headers[self.USER_AGENT_HEADER_NAME]]
        self.headers.append("*")

      for userAgent in self.headers:
        retUserAgent = userAgent
        isAllowed = self.localParser.is_allowed(userAgent, url)
        if not isAllowed:
          break
      if not isAllowed and self.USER_AGENT_HEADER_NAME in self.headers:
        retUserAgent = self.headers[self.USER_AGENT_HEADER_NAME]

      if self.localCrawlerDataStorage is not None and siteId is not None and \
      self.cacheElement is not None and self.cacheElementKeys is not None:
        host = Utils.UrlParser.getDomain(url)
        if host is not None:
          self.cacheElement[self.cacheElementKeys[0]][self.cacheElementKeys[1]] += 1
          self.localCrawlerDataStorage.saveElement(self.robotsFileDir, host, siteId, self.cacheElement)
    return isAllowed, retUserAgent
