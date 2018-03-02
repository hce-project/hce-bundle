"""
@package: dc
@file ResourceProcess.py
@author Scorp <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import time
import datetime
import copy
import re
import magic
import tidylib
import lxml.html
import lxml.etree
import requests
import dc_crawler.Constants as CRAWLER_CONSTS
from dc_crawler.CrawledResource import CrawledResource
import app.Consts as APP_CONSTS
from app.Utils import SQLExpression
from app.DateTimeType import DateTimeType
from app.Utils import getTracebackInfo
import app.Utils as Utils  # pylint: disable=F0401
import dc.EventObjects as dc_event

logger = Utils.MPLogger().getLogger()


class ResourceProcess(object):

  RECOVER_IF_FAILED = "2"

  def __init__(self):
    self.dbWrapper = None
    self.batchItem = None
    self.resource = None
    self.urlObj = None


  # #checkFieldsIsNone method checks all class's mandatory fields
  #
  def checkFieldsIsNone(self, checkList):
    # for field in self.__dict__:
    #  if field in checkList and (not hasattr(self, field) or getattr(self, field) is None):
    #    raise Exception(">>> [ResourceProcess] Mandatory field must be initialized, field Name = " + field)
    for name in checkList:
      if not hasattr(self, name) or getattr(self, name) is None:
        raise Exception("Some mandatory field `%s` must be initialized!", name)


  # # Get codec value
  #
  # @param charset - charset name
  # @return codec name
  def getCodec(self, charset):
    # variable for result
    ret = None
    if isinstance(charset, basestring):
      charset = charset.split(',')[0]
      if charset in CRAWLER_CONSTS.standardEncodings.keys():
        ret = charset
      else:
        for codec, aliases in CRAWLER_CONSTS.standardEncodings.items():
          if aliases.find(charset) > -1 or aliases.find(charset.lower()) > -1:
            ret = codec
            break

    return ret


  # # Convert charset to utf-8 for response header
  # @param headers - resource http headers
  # @param charset - charset name
  # @return responseHeader - response header as string
  def convertCharset(self, headers, charset):
    # variable for result
    responseHeader = ''
    logger.debug("headers: %s, type: %s", str(headers), str(type(headers)))
    logger.debug("charset: %s, type: %s", str(charset), str(type(charset)))

    try:
      if isinstance(headers, requests.structures.CaseInsensitiveDict) and isinstance(charset, basestring):
        codec = self.getCodec(charset)
        logger.debug("codec: %s", str(codec))
        if codec is None:
          responseHeader = '\r\n'.join(['%s: %s' % (k, v) for k, v in headers.iteritems()])
        else:
          responseHeader = '\r\n'.join(['%s: %s' % (k.decode(codec).encode('utf-8'), v.decode(codec).encode('utf-8')) \
                                        for k, v in headers.iteritems()])
    except Exception, err:
      logger.error(str(err))

    return responseHeader


  # #calcLastModified - generates and returns lastModified string
  #
  # @param startTime - resource start time
  # @param res - resource object fetched from request lib
  # @param headers - resource http headers
  # @param crawledTime - resource crawled time
  # @param defaultIcrCrawlTime - default increment time
  # @returns valid or not valid checking bool value
  def generateResource(self, startTime, res, headers, crawledTime, defaultIcrCrawlTime, contentTypeMap=None):  # pylint: disable=W0613
    # use charset to improve encoding detect
    resource = CrawledResource()
    resource.meta_content = res.meta_res
    resource.crawling_time = int((crawledTime - startTime) * 1000)
    if res.content_size is not None and resource.crawling_time != 0:
      resource.bps = res.content_size / resource.crawling_time * 1000

    logger.info("crawling_time: %s, bps: %s", resource.crawling_time, resource.bps)
    resource.http_code = res.status_code
    logger.debug("headers is :%s", res.headers)
    localHeaders = {}
    if res.headers is not None:
      for elem in res.headers:
        localHeaders[elem.lower()] = res.headers[elem]

    logger.debug("!!! localHeaders = %s", str(localHeaders))
    logger.debug("!!! localHeaders.get('content-type', '') = %s", str(localHeaders.get('content-type', '')))

    # resource.content_type = localHeaders.get('content-type', 'text/html').split(';')[0]
    resource.content_type = localHeaders.get('content-type', 'text/xml').split(';')[0]

    # save cookies
    resource.cookies = res.cookies

    if res.encoding:
      logger.debug("!!! res.encoding = '%s'", str(res.encoding))
      if isinstance(res.encoding, basestring):
        resource.charset = res.encoding.split(',')[0]
      else:
        resource.charset = res.encoding
    else:
      resource.charset = "utf-8"

    if res.request is not None and hasattr(res.request, 'headers') and  res.request.headers is not None:
      resource.html_request = '\r\n'.join(['%s: %s' % (k, v) for k, v in res.request.headers.iteritems()])
    elif res.request is not None and isinstance(res.request, dict) and  'headers' in res.request and\
    res.request['headers'] is not None:
      resource.html_request = '\r\n'.join(['%s: %s' % (k, v) for k, v in res.request['headers'].iteritems()])
    else:
      resource.html_request = ""

    if res.headers is not None:
      try:
        resource.response_header = self.convertCharset(res.headers, resource.charset)
      except Exception, err:
        logger.error(str(err))
        logger.info(getTracebackInfo())

    resource.last_modified = self.calcLastModified(resource, res, defaultIcrCrawlTime)

    if contentTypeMap is not None and resource.content_type in contentTypeMap:
      logger.debug(">>> Mime type replaced from %s to %s", resource.content_type, contentTypeMap[resource.content_type])
      resource.content_type = copy.deepcopy(contentTypeMap[resource.content_type])
    logger.debug("request is: %s", resource.html_request)
    logger.debug("response is: %s", resource.response_header)

    return resource


  # #calcLastModified - generates and returns lastModified string
  #
  # @param resource - own resource object
  # @param res - resource object fetched from request lib
  # @param defaultIcrCrawlTime - incrementing time values
  # @returns lastModified string
  def calcLastModified(self, resource, res, defaultIcrCrawlTime):
    # variables for result
    lastModified = None
    self.checkFieldsIsNone(["urlObj"])
    try:
      if resource.http_code == 304:
        lastModified = self.urlObj.tcDate
        # ret = self.url["TcDate"]
      elif 'Last-Modified' in res.headers:
        d = DateTimeType.parse(res.headers['Last-Modified'], True, logger)
        if d is not None:
          lastModified = d.strftime('%Y-%m-%d %H:%M:%S')
      elif 'Date' in res.headers:
        d = DateTimeType.parse(res.headers['Date'], True, logger)
        if d is not None:
          lastModified = d.strftime('%Y-%m-%d %H:%M:%S')
      else:
        lastModified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() - defaultIcrCrawlTime))
      logger.debug("LastModified date:" + str(lastModified))
    except Exception, err:
      logger.debug('calcLastModified has fail conversation, using current datetime, err: ' + str(err))
    finally:
      if lastModified is None:
        d = DateTimeType.parse(datetime.datetime.today().isoformat())
        if d is not None:
          lastModified = d.strftime('%Y-%m-%d %H:%M:%S')

    return str(lastModified)


  # #addSiteSize update sites table to increase size
  #
  # @param size content size of this crawler
  def addSiteSize(self, size):
    if self.dbWrapper is not None:
      self.checkFieldsIsNone(["dbWrapper", "batchItem"])
      localSiteUpdate = dc_event.SiteUpdate(self.batchItem.siteId)
      for attr in localSiteUpdate.__dict__:
        if hasattr(localSiteUpdate, attr):
          setattr(localSiteUpdate, attr, None)
      localSiteUpdate.id = self.batchItem.siteId
      localSiteUpdate.tcDate = SQLExpression("NOW()")
      localSiteUpdate.size = SQLExpression(("`Size` + %s" % str(size)))
      self.dbWrapper.siteNewOrUpdate(localSiteUpdate)


  # #checkResourcesResponse checks resource's fields on valid
  #
  # @param res - current resource object, just fetched from request library
  # @param maxResourceSize - max resources size
  # @param updateSiteCallback - update site callback
  # @returns valid or not valid checking bool value
  def checkResourcesResponse(self, res, maxResourceSize, updateSiteCallback):
    ret = True
    self.checkFieldsIsNone(["resource"])
    resourceSize = res.content_size
    logger.debug("MaxResourceSize: " + str(maxResourceSize) + " ResourceSize: " + str(resourceSize))
    if resourceSize == 0 and self.resource.http_code / 100 != 3:
      self.resource.error_mask = APP_CONSTS.ERROR_EMPTY_RESPONSE
      updateSiteCallback(APP_CONSTS.ERROR_EMPTY_RESPONSE)
      ret = False
    elif maxResourceSize and resourceSize > maxResourceSize:
      self.resource.error_mask = APP_CONSTS.ERROR_RESPONSE_SIZE_ERROR
      updateSiteCallback(APP_CONSTS.ERROR_RESPONSE_SIZE_ERROR)
      logger.debug("Site MaxResourceSize limit overshooted.")
      ret = False
    else:
      self.resource.html_content = res.rendered_unicode_content
      self.resource.binary_content = res.str_content

    if ret and (res.status_code / 100 == 4 or res.status_code / 100 == 5):
      self.resource.error_mask = APP_CONSTS.ERROR_HTTP_ERROR
      # Add error mask about forbidden fetch
      if res.status_code == CRAWLER_CONSTS.HTTP_CODE_403:
        self.resource.error_mask = APP_CONSTS.ERROR_FETCH_FORBIDDEN

      updateSiteCallback(self.resource.error_mask)
      ret = False
    if ret:
      self.addSiteSize(resourceSize)
    return ret


  # #domParser generates DOM object and returns it
  #
  # @param html_recover - html recover type
  # @param res - incoming resource
  # @returns just generated dom object
  def domParser(self, htmlRecover, rendered_unicode_content, http_code, charset):
    ret = None

#     logger.debug("!!! domParser ENTER !!! http_code: %s, charset: '%s'\nrendered_unicode_content: %s",
#                  str(http_code), str(charset), str(rendered_unicode_content))
    if charset is None or charset == "":
      charset = 'utf-8'
    parser = lxml.etree.HTMLParser(encoding=charset)  # pylint: disable=E1101
    if http_code == CRAWLER_CONSTS.HTTP_CODE_304:
      ret = lxml.html.fromstring("<html></html>", parser=parser)
    else:
      try:
        rendered_unicode_content = rendered_unicode_content.decode(charset).encode('utf-8')
        ret = lxml.html.fromstring(rendered_unicode_content.decode('utf-8').encode(charset), parser=parser)
      except Exception, err:
        logger.debug("Wrong DOM model structure. Description: " + str(err))
        if htmlRecover is not None and htmlRecover == self.RECOVER_IF_FAILED:
          logger.debug("Try to fix DOM by tidylib.")
          tidy_content, errors = tidylib.tidy_document(rendered_unicode_content.decode('utf-8').encode(charset))
          logger.debug("tidylib errors: %s", str(errors))
          try:
            ret = lxml.html.fromstring(tidy_content, parser=parser)
          except Exception, err:
            logger.error('domParser error: ' + str(err))

    return ret


  # #mimeDetectByContent autodetect mime from incoming buffer
  #
  # @param crawledResource just crawler resource object
  # @returns autodetected mime or None
  def mimeDetectByContent(self, crawledResource, contentTypeMap=None, urlObj=None):  # pylint: disable=W0613
    ret = None
    if crawledResource.dynamic_fetcher_type:
      rawUnicodeContent = crawledResource.meta_content
    else:
      # rawUnicodeContent = crawledResource.html_content
      rawUnicodeContent = crawledResource.binary_content
    if rawUnicodeContent is not None:
      ret = magic.from_buffer(str(rawUnicodeContent), mime=True)
    if contentTypeMap is not None and ret in contentTypeMap:
      logger.debug(">>> Mime type replaced from %s to %s", ret, contentTypeMap[ret])
      ret = contentTypeMap[ret]
    return ret


  # [
  # {"url_expression":"regular_expression", "mode":mode_number, "url_types":[list_of_url_types], \
  # "url_parent":[list_of_parent_type], "content_types":[list_of_content_types]}
  # , ...]

  # #Check necessary of replace content type from map
  #
  # @param inputData - input data
  # @param urlObj - input urlObj
  # @return boolean value - True if necessary or False - otherwise
  @staticmethod
  def isAllowedReplaceMimeType(inputData=None, urlObj=None):
    logger.debug('>>> isAllowedReplaceMimeType enter....')
    # variable for result
    ret = False
    if inputData is not None:
      isOkElemList = []
      for element in inputData:
        logger.debug('>>> element: ' + str(element))

        if "url_expression" in element and urlObj is not None and urlObj.url is not None:
          logger.debug('>>> url: ' + str(urlObj.url))
          match = re.search(element["url_expression"], str(urlObj.url))
          if match is None:
            logger.debug('>>> url_expression fail')
            isOkElemList.append(False)
            continue
          else:
            logger.debug('>>> url_expression good')

        modeNumber = 0
        urlTypes = []
        urlParent = []
        contentTypes = []

        if "mode" in element:
          modeNumber = int(element["mode"])

        if "url_types" in element:
          urlTypes = element["url_types"]

        if "url_parent" in element:
          urlParent = element["url_parent"]

        if "content_types" in element:
          contentTypes = element["content_types"]

        logger.debug('>>> modeNumber: ' + str(modeNumber))
        logger.debug('>>> urlTypes: ' + str(urlTypes))
        logger.debug('>>> urlParent: ' + str(urlParent))
        logger.debug('>>> contentTypes: ' + str(contentTypes))


        logger.debug('>>>>> urlObj.contentType: ' + str(urlObj.contentType))

        if modeNumber == 0:
          pass
        elif modeNumber == 1 and urlObj.contentType != "":
          logger.debug('>>> mode (' + str(modeNumber) + ') fail, contentType: ' + str(urlObj.contentType))
          isOkElemList.append(False)
          continue
        elif modeNumber == 2 and urlObj.contentType not in urlTypes:
          logger.debug('>>> mode (' + str(modeNumber) + ') fail, contentType: ' + str(urlObj.contentType) + \
                       ' urlTypes: ' + str(urlTypes))
          isOkElemList.append(False)
          continue
        elif modeNumber == 3 and urlObj.contentType in urlTypes:
          logger.debug('>>> mode (' + str(modeNumber) + ') fail, contentType: ' + str(urlObj.contentType) + \
                       ' urlTypes: ' + str(urlTypes))
          isOkElemList.append(False)
          continue

        isOk = False
        if len(urlTypes) > 0:
          for urlType in urlTypes:
            if urlType == urlObj.type:
              isOk = True
        else:
          isOk = True

        if not isOk:
          logger.debug('>>> urlTypes fail: ' + str(urlTypes) + ' urlObj.type = ' + str(urlObj.type))
          isOkElemList.append(False)
          continue

        isOk = False
        if len(urlParent) > 0:
          for parentElem in urlParent:
            if parentElem == 0 and not urlObj.parentMd5:
              isOk = True
            elif parentElem == 1 and urlObj.parentMd5:
              isOk = True
        else:
          isOk = True

        if not isOk:
          logger.debug('>>> urlParent fail: ' + str(urlParent) + ' urlObj.parentMd5: ' + str(urlObj.parentMd5))
          isOkElemList.append(False)
          continue

        # all success
        isOkElemList.append(True)

      # Make result after loop
      logger.debug('isOkElemList: ' + str(isOkElemList))
      if True in isOkElemList:
        ret = True

    return ret
