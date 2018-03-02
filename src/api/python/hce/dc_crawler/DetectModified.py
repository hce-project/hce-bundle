"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file DetectModified.py
@author Scorp <developers.hce@gmail.com>
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import json
import hashlib
import rfc822
import time
# import datetime
# from email.Utils import formatdate  # pylint: disable=E0611,E0401

import app.Utils as Utils  # pylint: disable=F0401
from dc_crawler.Fetcher import BaseFetcher
import dc.EventObjects as dc_event

logger = Utils.MPLogger().getLogger()


class NotModifiedException(Exception):
  def __init__(self, message, httpCode):
    Exception.__init__(self, message)

    self.httpCode = httpCode


# #class implemented all logic necessary for "Resource Not Modified" detecting
#
class DetectModified(object):

  MODE_DISABLED = 0
  MODE_ONE_REQUEST = 1
  MODE_TWO_REQUESTS = 2

  ALGO_AUTO = 0
  ALGO_IF_NOT_MATCH = 1
  ALGO_IF_MOFIFIED_SINCE = 2
  ALGO_HEAD = 3

  COMPARE_AUTO = 0
  COMPARE_DATE = 1
  COMPARE_CRC32 = 2
  COMPARE_RAW_CONTENT = 3

  BEHAVIOR_DEFAULT = 0
  BEHAVIOR_CRAWLED_STATUS = 1
  BEHAVIOR_PROCESSED_STATUS = 2
  BEHAVIOR_SAVE_UDATE = 3


  # #class constructor
  #
  # @param modifiedSettingsStr contains string with values for internal algorithm
  def __init__(self, modifiedSettingsStr):
    try:
      self.modifiedSettings = json.loads(modifiedSettingsStr)
    except Exception:
      self.modifiedSettings = None
    self.lastModified = None
    self.eTags = None
    self.isResourceNotChanged = False
    self.prevContentLen = None
    self.prevContentMd5 = None
    self.prevContentDate = None


  # #generateETagsString method pastes all elements from eTags into one string
  #
  # @param eTags contains list of e-tags
  # @return resulting string
  def generateETagsString(self, eTags):
    ret = ""
    if eTags is not None:
      if isinstance(eTags, list):
        # for eTag in eTags:
        #  ret += '"'
        #  ret += str(eTag)
        #  ret += '",'
        # ret = ret.strip(',')
        ret = '","'.join(eTags)
      elif isinstance(eTags, basestring):
        ret = eTags
      ret = '"' + ret + '"'
    return ret


  def headersClearing(self, httpParams):
    dellKeys = []
    for key in httpParams["httpHeader"]:
      if key.lower() == "if-none-match" or key.lower() == "if-modified-since":
        dellKeys.append(key)
    for elem in dellKeys:
      del httpParams["httpHeader"][elem]


  def makeHTTPRequest(self, fetchType, httpParams):
    ret = None
    self.isResourceNotChanged = False
    if self.modifiedSettings is not None:
    #  logger.debug(">>> httpParams = " + str(httpParams))
    #  logger.debug(">>> expiredData = " + str(self.lastModified))
    #  logger.debug(">>> algorithm = " + str(self.modifiedSettings["algorithm"]))
      if httpParams is None:
        httpParams = {}

      self.headersClearing(httpParams)

      localMethod = "get"
      if self.modifiedSettings["algorithm"] == self.ALGO_AUTO:
        if self.eTags is not None and self.eTags is not "":
          eTagsString = self.generateETagsString(self.eTags)
          httpParams["httpHeader"]["if-none-match"] = eTagsString

        if self.lastModified is not None:
          httpParams["httpHeader"]["if-modified-since"] = self.lastModified

      elif self.modifiedSettings["algorithm"] == self.ALGO_IF_NOT_MATCH:
        if self.eTags is not None and self.eTags is not "":
          eTagsString = self.generateETagsString(self.eTags)
          httpParams["httpHeader"]["if-none-match"] = eTagsString

      elif self.modifiedSettings["algorithm"] == self.ALGO_IF_MOFIFIED_SINCE:
        if self.lastModified is not None:
          httpParams["httpHeader"]["if-modified-since"] = self.lastModified

      elif self.modifiedSettings["algorithm"] == self.ALGO_HEAD:
        if self.modifiedSettings["mode"] == self.MODE_ONE_REQUEST:
          raise Exception(">>> Error [algorithm == 3 and mode == 1] not compatible !!!")
        localMethod = "head"

      ret = BaseFetcher.get_fetcher(fetchType).open(httpParams["url"],
                                                    timeout=httpParams["httpTimeout"],
                                                    headers=httpParams["httpHeader"],
                                                    allow_redirects=httpParams["allowHttpRedirects"],
                                                    proxies=httpParams["proxies"], auth=httpParams["auth"],
                                                    data=httpParams["postData"], log=logger,
                                                    allowed_content_types=httpParams["processContentTypes"],
                                                    max_resource_size=httpParams["maxResourceSize"],
                                                    max_redirects=httpParams["maxHttpRedirects"],
                                                    method=localMethod)

    if ret is not None:
      self.resourceComparing(ret)
      if not self.isResourceNotChanged and self.modifiedSettings["mode"] == self.MODE_TWO_REQUESTS:
        self.headersClearing(httpParams)
        ret = BaseFetcher.get_fetcher(fetchType).open(httpParams["url"],
                                                      timeout=httpParams["httpTimeout"],
                                                      headers=httpParams["httpHeader"],
                                                      allow_redirects=httpParams["allowHttpRedirects"],
                                                      proxies=httpParams["proxies"], auth=httpParams["auth"],
                                                      data=httpParams["postData"], log=logger,
                                                      allowed_content_types=httpParams["processContentTypes"],
                                                      max_resource_size=httpParams["maxResourceSize"],
                                                      max_redirects=httpParams["maxHttpRedirects"])

    # if ret is not None and ret.request is not None and ret.request.headers is not None:
    #  logger.debug(">>> requests headers = " + str(ret.request.headers))

    return ret


  def resourceComparing(self, res):
    self.isResourceNotChanged = False
    if self.modifiedSettings["compare"] == self.COMPARE_AUTO:
      if res.status_code == 304:
        self.isResourceNotChanged = True
    elif self.modifiedSettings["compare"] == self.COMPARE_DATE:
      if "last-modified" in res.headers and self.prevContentDate is not None:
        try:
          resDate = time.mktime(rfc822.parsedate(res.headers["last-modified"]))
          prevResDate = time.mktime(rfc822.parsedate(self.prevContentDate))
          if resDate <= prevResDate:
            self.isResourceNotChanged = True
        except Exception:
          raise Exception(">>> Bad data format - resDate -" + str(res.headers["last-modified"]) + " or prevResDate -" +
                          str(self.prevContentDate))
    elif self.modifiedSettings["compare"] == self.COMPARE_CRC32:
      if res.rendered_unicode_content is not None and \
      hashlib.md5(res.rendered_unicode_content).hexdigest() == self.prevContentMd5:
        self.isResourceNotChanged = True
    elif self.modifiedSettings["compare"] == self.COMPARE_RAW_CONTENT:
      if res.rendered_unicode_content is not None and len(res.rendered_unicode_content) == self.prevContentLen:
        self.isResourceNotChanged = True


#  def raiseExceptionIfNotModified(self):
#    if self.isResourceNotChanged and self.modifiedSettings is not None and \
#    self.modifiedSettings["behavior"] in [self.BEHAVIOR_CRAWLED_STATUS, self.BEHAVIOR_PROCESSED_STATUS, \
#                                          self.BEHAVIOR_SAVE_UDATE]:
#      raise NotModifiedException("Detect resource not modified state")


  def getBehaviour(self):
    if self.modifiedSettings is not None:
      return self.modifiedSettings["behavior"]
    else:
      return None


  # # Check not modified property
  #
  # @return True - if is not modify and otherwise False
  def isNotModified(self):
    # variable for result
    ret = False
    logger.debug("!!! isNotModified() enter ... self.isResourceNotChanged = " + str(bool(self.isResourceNotChanged)))

    if self.isResourceNotChanged and self.modifiedSettings is not None and \
    self.modifiedSettings["behavior"] in [self.BEHAVIOR_DEFAULT, \
                                          self.BEHAVIOR_CRAWLED_STATUS, \
                                          self.BEHAVIOR_PROCESSED_STATUS, \
                                          self.BEHAVIOR_SAVE_UDATE]:
      ret = True

    logger.debug("!!! isNotModified() leave ... ret = " + str(bool(ret)))
    return ret


  # #notModifiedStateProcessing process resource in case of "not modified" state
  #
  # @param siteId - resource's siteId
  # @param url - resource's url
  # @param dbWrapper - database wrapper instance
  # @param defaultStatus - default status
  # @param defaultUpdateUDate - default updateUDate
  # @return status and updateUDate
  def notModifiedStateProcessing(self, siteId, url, dbWrapper, defaultStatus=dc_event.URL.STATUS_CRAWLED,
                                 defaultUpdateUDate=True):
    # variables for result
    status = defaultStatus
    updateUDate = defaultUpdateUDate
    if self.isResourceNotChanged:
      status = dc_event.URL.STATUS_UNDEFINED
      updateUDate = False
      if self.getBehaviour() == self.BEHAVIOR_CRAWLED_STATUS:
        status = dc_event.URL.STATUS_CRAWLED
      elif self.getBehaviour() == self.BEHAVIOR_PROCESSED_STATUS:
        urlContentObj = dc_event.URLContentRequest(siteId, url, dc_event.URLContentRequest.CONTENT_TYPE_PROCESSED)
        urlContentResponse = dbWrapper.urlContent([urlContentObj])
        if len(urlContentResponse.processedContents) > 0:
          status = dc_event.URL.STATUS_PROCESSED
      elif self.getBehaviour() == self.BEHAVIOR_SAVE_UDATE:
        updateUDate = True

    return status, updateUDate
