"""
@package: dc
@file CollectURLs.py
@author Scorp <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import copy
import json
import hashlib
import re
import lxml.html
try:
  import feedparser
except ImportError:
  feedparser = None

import app.Consts as APP_CONSTS
from app.Filters import Filters
# from app.Utils import UrlNormalizator
from app.Utils import urlNormalization
from app.UrlNormalize import UrlNormalize
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401
import dc_processor.Constants as PCONSTS
import dc.EventObjects
from dc_crawler.Fetcher import SeleniumFetcher
import dc_crawler.Constants as CRAWLER_CONSTS
from dc_crawler.HTTPRedirectResolver import HTTPRedirectResolver
from dc_crawler.CollectUrlsLimits import CollectUrlsLimits
from dc_crawler.UrlLimits import UrlLimits

logger = Utils.MPLogger().getLogger()


class CollectURLs(object):

  BINARY_CONTENT_TYPE_PATTERN = re.compile('(text)|(xml)', re.I)
  COLLECT_POST_DATA_NAME = "COLLECT_POST_DATA"
  COLLECT_POST_DATA = "1"
  DC_URLS_TABLE_PREFIX = "urls_"
  PATTERN_WITH_PROTOCOL = re.compile('[a-zA-Z]+:(//)?')
  DETECT_MIME_MAIN_CONTENT = "1"
  DETECT_MIME_COLLECTED_URL = "2"
  DETECT_MIME_TIMEOUT = 1


  def __init__(self, isAbortedByTTL=None):
    self.crawledResource = None
    self.url = None
    self.dom = None
    self.realUrl = None
    self.baseUrl = None
    self.processorName = None
    self.batchItem = None
    self.urlXpathList = None
    self.feedItems = None
    self.feed = None
    self.siteProperties = None
    self.site = None
    self.dbWrapper = None
    self.autoRemoveProps = None
    self.autoDetectMime = None
    self.processContentTypes = []
    self.postForms = None
    self.urlProcess = None
    self.robotsParser = None
    self.urlsXpathList = []
    self.isAbortedByTTL = (lambda: False) if isAbortedByTTL is None else isAbortedByTTL


  # #checkFieldsIsNone method checks all class's mandatory fields
  #
  def checkFieldsIsNone(self):
    excludeList = ['feedItems', 'feed', 'processorName', 'autoDetectMime', 'processContentTypes',
                   'postForms', 'robotsParser', 'dom', 'dbWrapper']
    for field in self.__dict__:
      if field not in excludeList and (not hasattr(self, field) or getattr(self, field) is None):
        msg = "Mandatory field must be initialized, field Name = " + field
        logger.error(msg)
        raise Exception(msg)


  # # process method
  #
  # @param httpCode - http code
  # @param readOnly - boolean flag read only
  # @param httpApplyHeaders - http headers for apply
  # @param proxyName - proxy name
  def process(self, httpCode, readOnly=False, httpApplyHeaders=None, proxyName=None):

    self.checkFieldsIsNone()
    if self.siteProperties is None:
      self.siteProperties = {}
    if self.processContentTypes is None:
      self.processContentTypes = []
    localSiteId = self.batchItem.siteId if self.batchItem.siteId else "0"
    nextStep = True
    useChains = False
    internalLinks, externalLinks = [], []
    maxURLsFromPage = 0
    params = []
    chainUrls = []
    formUrls = None
    formMethods = None
    formFields = None
    urlSet = set()

    logger.debug("!!! self.site.maxURLsFromPage = " + str(self.site.maxURLsFromPage))
    logger.debug("!!! self.url.maxURLsFromPage = " + str(self.url.maxURLsFromPage))

    if self.site is not None and self.site.maxURLsFromPage is not None:
      maxURLsFromPage = self.site.maxURLsFromPage

    if self.url is not None and self.url.maxURLsFromPage is not None and self.url.maxURLsFromPage > 0:
      maxURLsFromPage = self.url.maxURLsFromPage

    if nextStep and self.crawledResource is not None and \
    not self.BINARY_CONTENT_TYPE_PATTERN.search(self.crawledResource.content_type):
      nextStep = False

    # don't parse url for 4XX or 5XX response
    if nextStep and self.crawledResource is not None:
      code_type = int(self.crawledResource.http_code) / 100
      if code_type == 4 or code_type == 5:
        nextStep = False

    if nextStep and self.crawledResource is not None and not self.crawledResource.html_content:
      nextStep = False

    # if nextStep and self.dom is None:
    #  logger.debug("DOM is None")
    #  nextStep = False

    if nextStep:
      useChains = True
      if self.dom is not None:
        self.processProcessor(urlSet, self.dom, self.urlXpathList, self.batchItem.urlObj)
        formUrls, formMethods, formFields = self.extractFormURL(self.dom, self.siteProperties)
        urlSet.update(formUrls)
      else:
        logger.debug("DOM is None")

      if self.url.type == dc.EventObjects.URL.TYPE_SINGLE:
        logger.debug("URL type: single")
        nextStep = False

      if nextStep and self.crawledResource.dynamic_fetcher_result_type == \
        SeleniumFetcher.MACRO_RESULT_TYPE_URLS_LIST:
        ul = None
        try:
          ul = json.loads(self.crawledResource.html_content)
        except Exception, err:
          logger.error("Error deserialize macro data from result string: %s\n%s", str(err),
                       self.crawledResource.html_content)
        if ul is not None:
          logger.debug("Fill urlSet from macro results: %s items", str(len(ul)))
          if isinstance(ul, list):
            urlSet.update([u for u in ul if isinstance(u, basestring) and u != ''])

    if nextStep:
      if self.url.type == dc.EventObjects.URL.TYPE_CHAIN:
        logger.debug("URL type: chain")
        nextStep = False

    if nextStep:
      # (3) END
      urlTable = self.DC_URLS_TABLE_PREFIX + localSiteId
      self.urlProcess.urlTable = urlTable
      try:
        if self.siteProperties is not None and "RSS_FEED_ZERO_ITEM" in self.siteProperties and \
        int(self.siteProperties["RSS_FEED_ZERO_ITEM"]) == 1:
          if self.processorName == PCONSTS.PROCESSOR_FEED_PARSER or self.processorName == PCONSTS.PROCESSOR_RSS:
            self.feedElementsProcessing(self.url.urlMd5, httpCode, self.url.url, localSiteId, self.url, self.url.url,
                                        params, maxURLsFromPage, True)
      except ValueError:
        logger.debug(">>> Wrong \"RSS_FEED_ZERO_ITEM\" property's value")

      logger.debug("URLs candidates collected %s items:\n%s", str(len(urlSet)), str(urlSet))

      if self.site.maxURLs > 0 and len(urlSet) >= self.site.maxURLs:
        urlSet = set(list(urlSet)[:self.site.maxURLs])
        logger.debug("Site maxURLs = %s limit reached.", str(self.site.maxURLs))

      if self.site.maxResources > 0 and len(urlSet) >= self.site.maxResources:
        urlSet = set(list(urlSet)[:self.site.maxResources])
        logger.debug("Site maxResources = %s limit reached.", str(self.site.maxResources))

      countCnt = 0
      countErrors = 0
      for elemUrl in urlSet:

        if self.isAbortedByTTL():
          logger.debug("Aborted by TTL. All elements skipped.")
          break

        if elemUrl is None:
          logger.debug("Some url from urlSet is None, skipped.")
          continue

        elemUrl = elemUrl.strip()
        if elemUrl == '':
          logger.debug("Some url from urlSet is empty, skipped!")
          continue

        localUrl = elemUrl
        self.urlProcess.urlObj = self.url
        self.urlProcess.url = elemUrl
        self.urlProcess.dbWrapper = self.dbWrapper
        self.urlProcess.siteId = localSiteId
        retUrl, retContinue = self.urlProcess.processURL(self.realUrl, internalLinks, externalLinks, self.filtersApply,
                                                         None, self.baseUrl)
        if retUrl is not None:
          elemUrl = retUrl
          elemUrl = UrlNormalize.execute(siteProperties=self.siteProperties, base=self.baseUrl, url=elemUrl, supportProtocols=None, log=None)
        else:
          retContinue = True

        if retContinue:
          logger.debug("Candidate URL is not passed general checks, skipped: %s", str(elemUrl))
          continue

        # Apply filter to Url
        if not self.filtersApply(inputFilters=self.site.filters,
                                 subject=elemUrl,
                                 depth=self.url.depth,
                                 wrapper=self.dbWrapper,
                                 siteId=localSiteId):
          logger.debug("Candidate URL not matched filters, skipped.")
          continue
        else:
          logger.debug("Candidate URL matched filters.")

        # Check exist of the Url
        urlMd5 = hashlib.md5(elemUrl).hexdigest()
        self.urlProcess.url = elemUrl
        self.urlProcess.siteId = localSiteId
        self.urlProcess.urlTable = urlTable
        if self.urlProcess.isUrlExist(self.site.recrawlPeriod, urlMd5):
          logger.debug("Candidate URL %s already exist, skipped.", str(urlMd5))
          continue

        if self.site.maxURLs > 0:
          if httpCode == CRAWLER_CONSTS.HTTP_CODE_200:
            countCnt += 1
          else:
            countErrors += 1

          if self.dbWrapper is not None:
            currentCnt = self.urlProcess.readCurrentCnt(self.site.maxURLs)
            if currentCnt >= self.site.maxURLs or countCnt >= self.site.maxURLs or \
              (countCnt + countErrors) >= self.site.maxURLs:
              logger.debug("Site MaxURLs: %s limit is reached. countCnt = %s, currentCnt = %s",
                           str(self.site.maxURLs), str(countCnt), str(currentCnt))
              autoremovedURLs = self.urlProcess.autoRemoveURL(self.autoRemoveProps, self.site.recrawlPeriod, urlTable,
                                                              self.dbWrapper)
              if autoremovedURLs == 0:
                logger.debug("No one URL auto removed, candidate URL skipped!")
                continue
              else:
                logger.debug("%s URLs auto removed.", str(autoremovedURLs))

            if currentCnt >= self.site.maxResources or countCnt >= self.site.maxResources or \
              (countCnt + countErrors) >= self.site.maxResources:
              logger.debug("Site maxResources = %s limit is reached. countCnt = %s, currentCnt = %s",
                           str(self.site.maxResources), str(countCnt), str(currentCnt))
              autoremovedURLs = self.urlProcess.autoRemoveURL(self.autoRemoveProps, self.site.recrawlPeriod, urlTable,
                                                              self.dbWrapper)
              if autoremovedURLs == 0:
                logger.debug("No one URL auto removed, candidate URL skipped!")
                continue
              else:
                logger.debug("%s URLs auto removed.", str(autoremovedURLs))

        # detect collected url mime type and ignore non-match URL
        # (7) Detect collected url mime type and ignore non-match URL
        detectedMime = ''
        if self.autoDetectMime == self.DETECT_MIME_COLLECTED_URL and self.processContentTypes is not None:
          self.urlProcess.url = elemUrl
          detectedMime = self.urlProcess.detectUrlMime(self.siteProperties["CONTENT_TYPE_MAP"] if \
                                                       "CONTENT_TYPE_MAP" in self.siteProperties else None)
          if detectedMime not in self.processContentTypes:
            logger.debug("Candidate URL MIME type is not matched, skipped!")
            continue
        # (7) END

        if "ROBOTS_COLLECT" not in self.siteProperties or int(self.siteProperties["ROBOTS_COLLECT"]) > 0:
          logger.debug("Robots.txt obey mode is ON")
          if self.robotsParser and self.robotsParser.loadRobots(elemUrl, self.batchItem.siteId, httpApplyHeaders,
                                                                proxyName):
            isAllowed, retUserAgent = self.robotsParser.checkUrlByRobots(elemUrl, self.batchItem.siteId,
                                                                         httpApplyHeaders)
            if not isAllowed:
              logger.debug("URL " + elemUrl + " is NOT Allowed by user-agent:" + str(retUserAgent))
              self.urlProcess.updateURLForFailed(APP_CONSTS.ERROR_ROBOTS_NOT_ALLOW, self.batchItem)
              continue

        self.urlProcess.siteId = localSiteId
        depth = self.urlProcess.getDepthFromUrl(self.batchItem.urlId)

        # per project redirects resolving
        if "HTTP_REDIRECT_RESOLVER" in self.siteProperties and self.siteProperties["HTTP_REDIRECT_RESOLVER"] != "":
          logger.debug('!!!!!! HTTP_REDIRECT_RESOLVER !!!!! ')


          if "CONNECTION_TIMEOUT" in self.siteProperties:
            connectionTimeout = float(self.siteProperties["CONNECTION_TIMEOUT"])
          else:
            connectionTimeout = CRAWLER_CONSTS.CONNECTION_TIMEOUT

          tm = int(self.url.httpTimeout) / 1000.0
          if isinstance(self.url.httpTimeout, float):
            tm += float('0' + str(self.url.httpTimeout).strip()[str(self.url.httpTimeout).strip().find('.'):])

          proxies = {"http": "http://" + proxyName} if proxyName is not None else None

          auth = None
          if 'HTTP_AUTH_NAME' in self.siteProperties and 'HTTP_AUTH_PWD' in self.siteProperties:
            authName = self.siteProperties['HTTP_AUTH_NAME']
            authPwd = self.siteProperties['HTTP_AUTH_PWD']
            if authName is not None and authPwd is not None:
              auth = (authName, authPwd)

          postForms = {}
          for key in self.siteProperties.keys():
            if key.startswith('HTTP_POST_FORM_'):
              postForms[key[len('HTTP_POST_FORM_'):]] = self.siteProperties[key]
          postData = self.urlProcess.resolveHTTP(postForms, httpApplyHeaders)

          maxRedirects = HTTPRedirectResolver.RedirectProperty.DEFAULT_VALUE_MAX_REDIRECTS
          if 'HTTP_REDIRECTS_MAX' in self.siteProperties:
            maxRedirects = int(self.siteProperties['HTTP_REDIRECTS_MAX'])

          redirectResolver = HTTPRedirectResolver(propertyString=self.siteProperties["HTTP_REDIRECT_RESOLVER"],
                                                  fetchType=self.site.fetchType,
                                                  dbWrapper=self.dbWrapper,
                                                  siteId=localSiteId,
                                                  connectionTimeout=connectionTimeout)

          resUrl = redirectResolver.resolveRedirectUrl(url=elemUrl,
                                                       headers=httpApplyHeaders,
                                                       timeout=tm,
                                                       allowRedirects=True,
                                                       proxies=proxies,
                                                       auth=auth,
                                                       postData=postData,
                                                       maxRedirects=maxRedirects,
                                                       filters=self.site.filters)

          logger.debug("Resolved url: %s", str(resUrl))
          resUrl = UrlNormalize.execute(siteProperties=self.siteProperties, base=self.baseUrl, url=resUrl, supportProtocols=None, log=None)
          logger.debug("Normalized url: %s", str(resUrl))
          elemUrl = resUrl

        if elemUrl is not None:
          self.urlProcess.url = elemUrl
          self.urlProcess.siteId = localSiteId
          self.urlProcess.urlObj = self.url
          localUrlObj = self.urlProcess.createUrlObjForCollectURLs(urlMd5, formMethods, self.batchItem.urlId, depth,
                                                                   detectedMime, self.site.maxURLsFromPage)
          # update counters of external and internal links
          localUrlObj.linksI = len(internalLinks)
          localUrlObj.linksE = len(externalLinks)

          if self.processorName == PCONSTS.PROCESSOR_FEED_PARSER or self.processorName == PCONSTS.PROCESSOR_RSS:
            self.feedElementsProcessing(urlMd5, httpCode, elemUrl, localSiteId, localUrlObj, localUrl, params,
                                        maxURLsFromPage)
          else:
            params.append(localUrlObj)

    if useChains and "URL_CHAIN" in self.siteProperties and self.siteProperties["URL_CHAIN"] is not None:
      localChainDict = json.loads(self.siteProperties["URL_CHAIN"])
      depth = self.urlProcess.getDepthFromUrl(self.batchItem.urlId)
      if "url_pattern" in localChainDict:
        for elemUrl in urlSet:
          if elemUrl is None:
            logger.debug("Some url from urlSet is None")
            continue
          self.urlProcess.url = elemUrl
#           retUrl = self.urlProcess.simpleURLCanonize(self.realUrl)
#           if retUrl is None or not UrlNormalizator.isNormalUrl(retUrl):

          retUrl = urlNormalization(self.baseUrl, elemUrl)
          if retUrl is None:
            logger.debug("Bad url normalization, url: %s", retUrl)
            continue
          else:
            elemUrl = retUrl
          detectedMime = ''
          if self.autoDetectMime == self.DETECT_MIME_COLLECTED_URL and self.processContentTypes is not None:
            self.urlProcess.url = elemUrl
            detectedMime = self.urlProcess.detectUrlMime(self.siteProperties["CONTENT_TYPE_MAP"] if \
                                                         "CONTENT_TYPE_MAP" in self.siteProperties else None, \
                                                         self.batchItem.urlObj)
          urlMd5 = hashlib.md5(elemUrl).hexdigest()
          self.urlProcess.url = elemUrl
          self.urlProcess.siteId = localSiteId
          self.urlProcess.urlObj = self.url
          try:
            localUrlObj = self.urlProcess.\
                              createUrlObjForChain(localChainDict["url_pattern"], urlMd5, formMethods,
                                                   self.batchItem.urlId, depth, detectedMime, self.site.maxURLsFromPage)
            if localUrlObj is not None:
              chainUrls.append(copy.deepcopy(localUrlObj))
          except Exception as excp:
            logger.error("Error in URL_CHAIN deserialize, excp = " + str(excp))
    if len(urlSet) > 0 and len(params) == 0:
      logger.debug("Zero urls are collected for len(urlSet): %s", str(len(urlSet)))
    elif len(params) > 0:

      if APP_CONSTS.URL_LIMITS in self.siteProperties:
        logger.debug("!!! %s !!!", str(APP_CONSTS.URL_LIMITS))
        logger.debug("(B) params: %s", varDump(params))
        params = UrlLimits.applyLimits(properties=self.siteProperties[APP_CONSTS.URL_LIMITS], urlsList=params, log=logger)
        logger.debug("(A) params: %s", varDump(params))

      logger.debug("Collected and send to insert as new: %s", str(len(params)))
    if not readOnly:

      if self.dbWrapper is not None:
        self.dbWrapper.urlNew(params)
        self.dbWrapper.urlNew(chainUrls)
        self.urlProcess.updateTypeForURLObjects(chainUrls)
        self.dbWrapper.collectedURLsRecalculating(localSiteId)

    if formFields is not None and self.postForms is not None and self.dbWrapper is not None:
      fieldParams = self.getFieldParams(formFields, self.postForms, localSiteId)
      self.insertNewSiteProperties(fieldParams, self.dbWrapper, localSiteId)

    # logger.debug("Return from collectURLs:\n%s\n%s\n%s\n%s\n%s\n%s", str(nextStep), str(internalLinks),
    #             str(externalLinks), str(params), str(self.feedItems), str(chainUrls))

    return nextStep, internalLinks, externalLinks, params, self.feedItems, chainUrls


  # # feedElementsProcessing processed rss element
  #
  # @param urlMd5 - element url's urlMd5
  # @param httpCode - http code of http response
  # @param elemUrl - element url's url
  # @param localSiteId - siteId
  # @param localUrlObj - element's urlObj
  # @param localUrl - root element's url
  # @param params - element container (List type)
  # @param maxURLsFromPage - max URLs from page
  # @param rootFeed - bool param that specifyied use feed element from rss struture of entities element
  def feedElementsProcessing(self, urlMd5, httpCode, elemUrl, localSiteId, localUrlObj, localUrl, params,
                             maxURLsFromPage, rootFeed=False):

    if APP_CONSTS.COLLECT_URLS_LIMITS in self.siteProperties:
      logger.debug("!!! %s !!!", str(APP_CONSTS.COLLECT_URLS_LIMITS))
      maxURLsFromPage = CollectUrlsLimits.execute(properties=self.siteProperties[APP_CONSTS.COLLECT_URLS_LIMITS],
                                                  url=elemUrl,
                                                  optionsName=CollectUrlsLimits.MAX_URLS_FROM_PAGE,
                                                  default=maxURLsFromPage,
                                                  log=logger)
      logger.debug("Result maxURLsFromPage = %s", str(maxURLsFromPage))

    if maxURLsFromPage > 0 and len(self.feedItems) >= maxURLsFromPage:
      logger.debug("Site maxURLsFromPage = %s limit reached on %s number.",
                   str(maxURLsFromPage), str(len(self.feedItems)))
    else:
      if self.feed is not None:
        self.urlProcess.url = elemUrl
        self.urlProcess.siteId = localSiteId
        self.urlProcess.urlObj = localUrlObj
        localRet = self.urlProcess.fillRssFieldInUrlObj(localUrl, self.url.url, self.batchItem, self.processorName,
                                                        self.feed, rootFeed)
        self.urlProcess.urlObj = None
        if localRet is not None:
          localRet["urlMd5"] = urlMd5
          if localRet["urlObj"] is not None:
            localRet["urlObj"].httpCode = httpCode
            localRet["urlObj"].processingDelay = 0
            localRet["urlObj"].parentMd5 = self.url.urlMd5

            # logger.debug("localRet = %s", str(dict(localRet)))

            params.append(localRet["urlObj"])
            self.feedItems.append(localRet)
      else:
        logger.debug("self.feed is None!")

  # # processProcessor processed element from url's dom
  #
  # @param urlSet - incoming url's list (links from page)
  # @param dom - page's dom model
  # @param urlXpathList - applying xpath
  # @param urlObj - element of urlObject
  def processProcessor(self, urlSet, dom, urlXpathList, urlObj):
    if (self.processorName == PCONSTS.PROCESSOR_FEED_PARSER or self.processorName == PCONSTS.PROCESSOR_RSS) \
    and urlObj.type != dc.EventObjects.URL.TYPE_FETCHED:
      if feedparser is not None:
        try:
          self.feedItems = []
          # Add one more date parsing handler function to fix some wrong datetime format cases; added by bgv
          feedparser.registerDateHandler(self.feedparserParseDateFixes)

          # Remove handlers to process all tags as unknown to save their names unchanged
          if not (self.siteProperties is not None and "RSS_FEEDPARSER_MODE" in self.siteProperties and \
                  int(self.siteProperties["RSS_FEEDPARSER_MODE"]) > 0):
            import inspect
            # , "_start_guid"
            excludes = ["_start_rss", "_start_channel", "_start_feed", "_start_item", "_start_link",
                        "_start_admin_errorreportsto", "_start_admin_generatoragent", "_start_guid", "_start_id",
                        "_start_entry", "_start_enclosure"]
            for methodName, functionObject in inspect.getmembers(feedparser._FeedParserMixin, predicate=inspect.ismethod): # pylint: disable=W0612,W0212,C0301
              if methodName.startswith("_start_") and methodName not in excludes:
                delattr(feedparser._FeedParserMixin, methodName)  # pylint: disable=W0212
                endMethodName = methodName.replace("_start_", "_end_")
                if hasattr(feedparser._FeedParserMixin, endMethodName):  # pylint: disable=W0212
                  delattr(feedparser._FeedParserMixin, endMethodName)  # pylint: disable=W0212
            setattr(feedparser._FeedParserMixin, "_normalize_attributes", self._normalize_attributes)  # pylint: disable=W0212
            feedparser.FeedParserDict.keymap["guid"] = "guid"
            logger.debug("Feedparser in modified mode")
          else:
            logger.debug("Feedparser in native mode")

          self.feed = feedparser.parse(self.crawledResource.html_content)
          urlSet.update(entry.link for entry in self.feed.entries)
          # logger.debug("feed.entries: %s for url: %s\nfeed=\n%s\nurlSet:\n%s", str(len(self.feed.entries)),
          #             str(urlObj.url), str(dict(self.feed)), str(urlSet))
          if len(self.feed.entries) == 0:
            logger.debug("Zero entries in feed, self.crawledResource:\n%s", varDump(self.crawledResource))
            # logger.debug("self.processContentTypes: %s", str(self.processContentTypes))
            logger.debug("self.crawledResource.content_type = %s", str(self.crawledResource.content_type))
            if self.crawledResource.content_type == dc.EventObjects.URL.CONTENT_TYPE_TEXT_HTML:
              urlObj.errorMask |= APP_CONSTS.ERROR_MASK_SITE_UNSUPPORTED_CONTENT_TYPE
            
        except TypeError as err:
          logger.debug("WRONG CONTENT FOR URL <" + str(urlObj.url) + "> not rss feed. " + str(err.message))
        except Exception as err:
          logger.debug("SOME ERROR WITH rss feed parse " + str(err.message))
      else:
        logger.debug("feedparser module not found")
    # won't collect urls from rss feed resources
    elif self.processorName != PCONSTS.PROCESSOR_RSS:
      # Added support of urlXpathList as site's properties
      if len(urlXpathList) > 0:
        logger.debug("Site has COLLECT_URLS_XPATH_LIST property: %s", str(urlXpathList))
      else:
        # Set urls xpath list
        urlXpathList = {'sets': {'': self.urlsXpathList}}
        logger.debug("Site has no COLLECT_URLS_XPATH_LIST property, default xpath list used: %s", str(urlXpathList))
      if 'sets' in urlXpathList and isinstance(urlXpathList['sets'], dict):
        matchedSets = 0
        if 'date_format' in urlXpathList:
          dformat = str(urlXpathList['date_format'])
        else:
          dformat = '%Y-%m-%d %H:%M:%S'
        for rexpr in urlXpathList['sets']:
          if rexpr == '' or re.search(rexpr, urlObj.url) is not None:
            if 'mode' in urlXpathList and int(urlXpathList['mode']) == 1:
              xpathl = self.urlsXpathList + urlXpathList['sets'][rexpr]
            else:
              xpathl = urlXpathList['sets'][rexpr]
            matchedSets += 1
            for xpath in xpathl:
              xpath = self.evaluateDateMacro(xpath, dformat)
              elem = dom.xpath(xpath)
              elem_type = type(elem)
              if elem_type == list and len(elem) > 0 and hasattr(elem[0], "tail"):
                urlSet.update([el.tail for el in elem])
              elif elem_type == list and len(elem) > 0 and isinstance(elem[0], lxml.html.HtmlElement):
                urlSet.update([el.text for el in elem])
              else:
                urlSet.update(elem)
        if matchedSets == 0:
          logger.debug("Warning! No one xpath set matched URL %s, URLs not collected!", urlObj.url)
      else:
        logger.debug('Wrong COLLECT_URLS_XPATH_LIST property, `sets` key with dict() of re->xpath_list[] expected!' + \
                     ' Collect URLs aborted!')
    # logger.debug("urlSet: %s", str(urlSet))


  # #Evaluate date macro
  #
  # @param localPattern - input pattern as string
  # @param dateFromat - format for %@DATE... macro
  # @return string with date macro evaluated and replaced with values
  def evaluateDateMacro(self, localPattern, dateFromat):
    import time
    import datetime

    logger.debug("!!! evaluateDateMacro ENTER !!! localPattern = %s", str(localPattern))
    try:
      d = {'DATE':'', 'SHORTYEAR':'y', 'YEAR':'Y', 'MONTH':'m', 'DAY':'d', 'HOUR':'H', 'MINUTE':'M', 'SECOND':'S'}
      regex = re.compile("%@(SHORTYEAR|YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|DATE)\\(([\\+|\\-]\\d{1,2})\\)%")
      matchArray = regex.findall(localPattern)
      for i in matchArray:
        if i[0] == 'DATE':
          f = dateFromat
        else:
          f = '%' + d[i[0]]
        t = time.strftime(f, time.gmtime(time.time() + datetime.timedelta(hours=(+int(i[1]))).seconds))
        localPattern = localPattern.replace("%@" + i[0] + "(" + i[1] + ")%", t)
    except Exception, err:
      logger.error(str(err))

    logger.debug("!!! evaluateDateMacro LEAVE !!! localPattern = %s", str(localPattern))

    return localPattern


  # # extrace URL, form action, and fields from html dom
  #
  # @param dom the dom tree
  # @return form_urls    sequence of urls extracted
  # @return form_methods  dict of form methods, {form_action: form_method}
  # @return form_fields  dict of fields {field_name: field_value}
  def extractFormURL(self, dom, siteProperties):
    formUrls, formMethods, formFields = [], {}, {}
    if self.COLLECT_POST_DATA_NAME in siteProperties and \
    siteProperties['COLLECT_POST_DATA'] == self.COLLECT_POST_DATA:
      for form in dom.xpath("//form"):
        formAction = None
        formMethod = 'get'
        for attr in form.keys():
          if attr.lower() == "action":
            formAction = form.get(attr)
            formUrls.append(formAction)
          elif attr.lower() == "method":
            formMethod = form.get(attr)
        if not formAction:
          continue
        formMethods[formAction] = formMethod
        for field in form.getchildren():
          tagName, tagValue = None, ""
          for fieldTag in field.keys():
            if fieldTag.lower() == "name":
              tagName = field.get(fieldTag)
            elif fieldTag.lower() == "value":
              tagValue = field.get(fieldTag)
          if tagName:
            formFields[tagName] = tagValue
      logger.info("extracted form data, formUrls:%s, formMethods:%s, formFields:%s", \
      formUrls, formMethods, formFields)
    return formUrls, formMethods, formFields


  # # Applys filters and returns bool result
  #
  # @param inputFilters - input sites filters list
  # @param subject - subject for apply filter
  # @param depth - depth value
  # @param wrapper - DBTasksWrapper instance
  # @param siteId - site ID used with db-task wrapper
  # @param fields - dictionary values of support macro names ('PDATE' and other)
  # @param opCode - operation code
  # @param stage - stage of apply filter
  # @param selectSubject - select subject use select from DB
  # @param defaultValue - default value for result
  # @return True  if filter is good or False otherwise
  @staticmethod
  def filtersApply(inputFilters, subject, depth, wrapper, siteId, fields=None, opCode=Filters.OC_RE, \
                   stage=Filters.STAGE_COLLECT_URLS, selectSubject=None, defaultValue=False):
    ret = defaultValue
    fValue = Utils.generateReplacementDict()
    fValue.update({"MAX_DEPTH": str(depth)})

    if inputFilters is not None:
      for inputFilter in inputFilters:
        if inputFilter.stage == Filters.STAGE_ALL or inputFilter.stage == Filters.STAGE_REDIRECT_URL:
          inputFilter.stage = Filters.STAGE_COLLECT_URLS

#     logger.debug(">>> Filters() (2.1) fields: " + varDump(fields) + " inputFilters: " + varDump(inputFilters))
    localFilters = Filters(filters=inputFilters, dbTaskWrapper=wrapper, siteId=siteId, readMode=0, fields=fields,
                           opCode=opCode, stage=stage, selectSubject=selectSubject)

    # logger.debug(">>> before filter include = " + subject[:255] + ' . . . ')
    fResult = localFilters.filterAll(stage, fValue, Filters.LOGIC_OR, subject, 1)
    logger.debug(">>> filter result include - " + str(fResult))
    for elem in fResult:
#       logger.debug('elem = ' + str(elem) + ' type: ' + str(type(elem)))
      if elem > 0:
        ret = True
        break

    if ret is True:
      # logger.debug(">>> before filter exclude = " + subject[:255] + ' . . . ')
      fResult = localFilters.filterAll(stage, fValue, Filters.LOGIC_OR, subject, -1)
      logger.debug(">>> filter result exclude - " + str(fResult))
      for elem in fResult:
#         logger.debug('elem = ' + str(elem) + ' type: ' + str(type(elem)))
        if elem > 0:
          ret = False
          break

    logger.debug("Verdict: " + str(ret))
    return ret


  # #getFieldParams method fill and returns post forms
  #
  # formFields - post fields dict
  # postForms - post form list
  # siteId - site's id
  def getFieldParams(self, formFields, postForms, siteId):
    ret = []
    for fieldName, fieldValue in formFields.iteritems():
      if fieldName in postForms:
        continue
      logger.debug("field_name: %s", fieldName)
      logger.debug("field_value: %s", fieldValue)
      ret.append((siteId, "HTTP_POST_FORM_" + fieldName, fieldValue))
    return ret


  # #insertNewSiteProperties update Site (add new properties in correspond table)
  #
  # params - params list
  # wrapper - db-task wrapper
  # siteId - site's id
  def insertNewSiteProperties(self, params, wrapper, siteId):
    if siteId is not None and hasattr(params, '__iter__') and len(params) > 0:
      localSiteUpdate = dc.EventObjects.SiteUpdate(siteId)
      for attr in localSiteUpdate.__dict__:
        if hasattr(localSiteUpdate, attr):
          setattr(localSiteUpdate, attr, None)
      localSiteUpdate.updateType = dc.EventObjects.SiteUpdate.UPDATE_TYPE_APPEND
      localSiteUpdate.id = siteId
      localSiteUpdate.properties = []
      for param in params:
        newPropElem = {}
        newPropElem["siteId"] = param[0]
        newPropElem["name"] = param[1]
        newPropElem["value"] = param[2]
        localSiteUpdate.properties.append(newPropElem)
      wrapper.siteNewOrUpdate(localSiteUpdate, stype=dc.EventObjects.SiteUpdate)


  # #feedparserParseDateFixes method to fix date parsing for the feedparser
  #
  # @param aDateString the date string to parse
  def feedparserParseDateFixes(self, aDateString):
    ret = None
    ds = aDateString

    # Assumes that date format broken and contains the semicolon ":" in TZ like: "Wed, 19 Aug 2015 08:45:53 +01:00"
    parts = ds.split(' ')
    if ("+" in parts[len(parts) - 1] or "-" in parts[len(parts) - 1]) and ":" in parts[len(parts) - 1]:
      parts[len(parts) - 1] = parts[len(parts) - 1].replace(":", "")
      ds = " ".join(parts)
      # ret = feedparser._parse_date_rfc822(ds)
      ret = feedparser._parse_date(ds)  # pylint: disable=W0212

    return ret


  def _normalize_attributes(self, kv):
    return (kv[0], kv[1])
