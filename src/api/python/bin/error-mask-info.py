#!/usr/bin/python

"""
HCE project, Python bindings, Distributed Tasks Manager application.
error-mask-info.py - cli tool to decode error mask info and output to stdout.

@package: dc
@file error-mask-info.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import ppath
from ppath import sys

import json
import logging
import app.Utils as Utils
import app.Consts as CONSTS

logging.basicConfig(filename="../log/error-mask-info.log", filemode="w")
logger = logging.getLogger(CONSTS.LOGGER_NAME)
logger.setLevel("DEBUG")


MSG_ERROR_EXIT_STATUS = "Exit failure. "

MSG_DEBUG_INPUT_ERROR_MASK = "Input error mask: "
MSG_DEBUG_CONVERTED_MASKS = "Converted masks: "


STATUS_SUCCESS = 0
STATUS_FAILURE = 1

defined_masks = {
# CrawlerTask section
"CRAWLER-TASK-ERROR-BAD-URL" : CONSTS.ERROR_BAD_URL,
"CRAWLER-TASK-ERROR-REQUEST-TIMEOUT" : CONSTS.ERROR_REQUEST_TIMEOUT,
"CRAWLER-TASK-ERROR-HTTP-ERROR" : CONSTS.ERROR_HTTP_ERROR,
"CRAWLER-TASK-ERROR-EMPTY-RESPONSE" : CONSTS.ERROR_EMPTY_RESPONSE,
"CRAWLER-TASK-ERROR-WRONG-MIME" : CONSTS.ERROR_WRONG_MIME,
"CRAWLER-TASK-ERROR-CONNECTION-ERROR" : CONSTS.ERROR_CONNECTION_ERROR,
"CRAWLER-TASK-ERROR-PAGE-CONVERT-ERROR" : CONSTS.ERROR_PAGE_CONVERT_ERROR,
"CRAWLER-TASK-ERROR-ERROR-MACRO" : CONSTS.ERROR_MACRO,
"CRAWLER-TASK-ERROR-RESPONSE-SIZE-ERROR" : CONSTS.ERROR_RESPONSE_SIZE_ERROR,
"CRAWLER-TASK-ERROR-AUTH-ERROR" : CONSTS.ERROR_AUTH_ERROR,
"CRAWLER-TASK-ERROR-WRITE-FILE-ERROR" : CONSTS.ERROR_WRITE_FILE_ERROR,
"CRAWLER-TASK-ERROR-ROBOTS-NOT-ALLOW" : CONSTS.ERROR_ROBOTS_NOT_ALLOW,
"CRAWLER-TASK-ERROR-HTML-PARSE-ERROR" : CONSTS.ERROR_HTML_PARSE_ERROR,
"CRAWLER-TASK-ERROR-BAD-ENCODING" : CONSTS.ERROR_BAD_ENCODING,
"CRAWLER-TASK-ERROR-SITE-MAX-ERRORS" : CONSTS.ERROR_SITE_MAX_ERRORS,
"CRAWLER-TASK-ERROR-EMPTY-RESPONSE" : CONSTS.ERROR_EMPTY_RESPONSE,
"CRAWLER-TASK-ERROR_CRAWLER_FILTERS_BREAK" : CONSTS.ERROR_CRAWLER_FILTERS_BREAK,
"CRAWLER-TASK-ERROR-MAX-ALLOW-HTTP-REDIRECTS" : CONSTS.ERROR_MAX_ALLOW_HTTP_REDIRECTS,
"CRAWLER-TASK-ERROR-MAX-ALLOW-HTML-REDIRECTS" : CONSTS.ERROR_MAX_ALLOW_HTML_REDIRECTS,
"CRAWLER-TASK-ERROR-GENERAL-CRAWLER" : CONSTS.ERROR_GENERAL_CRAWLER,
"CRAWLER-TASK-ERROR-DTD-INVALID" : CONSTS.ERROR_DTD_INVALID,
"CRAWLER-TASK-ERROR-MACRO-DESERIALIZATION" : CONSTS.ERROR_MACRO_DESERIALIZATION,
"CRAWLER-TASK-ERROR-FETCH-AMBIGUOUS-REQUEST" : CONSTS.ERROR_FETCH_AMBIGUOUS_REQUEST,
"CRAWLER-TASK-ERROR-FETCH-CONNECTION-ERROR" : CONSTS.ERROR_FETCH_CONNECTION_ERROR,
"CRAWLER-TASK-ERROR-FETCH-HTTP-ERROR" : CONSTS.ERROR_FETCH_HTTP_ERROR,
"CRAWLER-TASK-ERROR-FETCH-INVALID-URL" : CONSTS.ERROR_FETCH_INVALID_URL,
"CRAWLER-TASK-ERROR-FETCH-TOO-MANY-REDIRECTS" : CONSTS.ERROR_FETCH_TOO_MANY_REDIRECTS,
"CRAWLER-TASK-ERROR-FETCH-CONNECTION-TIMEOUT" : CONSTS.ERROR_FETCH_CONNECTION_TIMEOUT,
"CRAWLER-TASK-ERROR-FETCH-READ-TIMEOUT" : CONSTS.ERROR_FETCH_READ_TIMEOUT,
"CRAWLER-TASK-ERROR-FETCH-TIMEOUT" : CONSTS.ERROR_FETCH_TIMEOUT,
"CRAWLER-TASK-FETCHER-INTERNAL-ERROR" : CONSTS.ERROR_FETCHER_INTERNAL,

# ProcessorTask section
"PROCESSOR-TASK-ERROR_MASK_SITE_MAX_RESOURCES_NUMBER" : CONSTS.ERROR_MASK_SITE_MAX_RESOURCES_NUMBER,
"PROCESSOR-TASK-ERROR_DATABASE_ERROR": CONSTS.ERROR_DATABASE_ERROR,
"PROCESSOR-TASK-ERROR_MASK_SITE_MAX_RESOURCES_SIZE" : CONSTS.ERROR_MASK_SITE_MAX_RESOURCES_SIZE,
"PROCESSOR-TASK-ERROR_MASK_SITE_UNSUPPORTED_CONTENT_TYPE" : CONSTS.ERROR_MASK_SITE_UNSUPPORTED_CONTENT_TYPE,
"PROCESSOR-TASK-ERROR_MASK_URL_ENCODING_ERROR" : CONSTS.ERROR_MASK_URL_ENCODING_ERROR,
"PROCESSOR-TASK-ERROR_MASK_SCRAPER_ERROR" : CONSTS.ERROR_MASK_SCRAPER_ERROR,
"PROCESSOR-TASK-ERROR_MASK_MISSED_RAW_CONTENT_ON_DISK" : CONSTS.ERROR_MASK_MISSED_RAW_CONTENT_ON_DISK,
"PROCESSOR-TASK-ERROR_RE_ERROR" : CONSTS.ERROR_RE_ERROR,
"PROCESSOR-TASK-ERROR_MANDATORY_TEMPLATE": CONSTS.ERROR_MANDATORY_TEMPLATE,
"PROCESSOR-TASK-ERROR_PROCESSOR_FILTERS_BREAK" : CONSTS.ERROR_PROCESSOR_FILTERS_BREAK,
"PROCESSOR-TASK-ERROR_MASK_SITE_STATE" : CONSTS.ERROR_MASK_SITE_STATE,
"PROCESSOR-TASK-ERROR_MAX_ITEMS" : CONSTS.ERROR_MAX_ITEMS,
"PROCESSOR-TASK-ERROR_MAX_URLS_FROM_PAGE" : CONSTS.ERROR_MAX_URLS_FROM_PAGE,
"PROCESSOR-TASK-ERROR_TEMPLATE_SOURCE" : CONSTS.ERROR_TEMPLATE_SOURCE,

# 2 - Crawler errors diapason
"CRAWLER-TASK-ERROR-RSS-EMPTY": CONSTS.ERROR_RSS_EMPTY,
"CRAWLER-TASK-ERROR-URLS-SCHEMA-EXTERNAL": CONSTS.ERROR_URLS_SCHEMA_EXTERNAL,
"CRAWLER-TASK-ERROR-NOT-EXIST-ANY-VALID-PROXY": CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY,
"CRAWLER-TASK-ERROR-FETCH-FORBIDDEN": CONSTS.ERROR_FETCH_FORBIDDEN,
"CRAWLER-TASK-ERROR-NO-TIME-WINDOW": CONSTS.ERROR_NO_TIME_WINDOW,
"ERROR_CRAWLER_FATAL_INITIALIZATION_PROJECT_ERROR": CONSTS.ERROR_CRAWLER_FATAL_INITIALIZATION_PROJECT_ERROR,
"ERROR_PROCESSOR_BATCH_ITEM_PROCESS": CONSTS.ERROR_PROCESSOR_BATCH_ITEM_PROCESS,
"ERROR_MAX_EXECUTION_TIME": CONSTS.ERROR_MAX_EXECUTION_TIME
}


def getErrorMask():
  error_mask = None
  if len(sys.argv) == 2:
    try:
      error_mask = int(sys.argv[1])
    except:
      print "error mask must be integer"
      sys.exit(2)
  else:
    print "Usage: ./error-mask-info.py <error mask>"
    sys.exit(2)
  logger.debug(MSG_DEBUG_INPUT_ERROR_MASK + '\n' + str(error_mask))
  return error_mask


def convertMask(error_mask):
  founded = False
  masks = {"errors":[]}
  logger.debug("defined_masks: %s", str(defined_masks))
  logger.debug("error_mask: %s", str(type(error_mask)))
  for key in defined_masks:
    if defined_masks[key] & error_mask:
      masks["errors"].append(key)
      founded = True
  if founded:
    logger.debug(MSG_DEBUG_CONVERTED_MASKS + '\n' + str(masks))
  else:
    print "Mask " + str(error_mask) + " not defined both CrawlerTask or ProcessorTask"
    masks = {}
  return json.dumps(masks)




if __name__ == "__main__":
  try:
    exit_status = STATUS_SUCCESS
    error_mask = getErrorMask()
    masks = convertMask(error_mask)
    print masks
  except Exception, err:
    tbi = Utils.getTracebackInfo()
    logger.error(MSG_ERROR_EXIT_STATUS + err.message + '\n' + tbi)
    exit_status = STATUS_FAILURE
  exit(exit_status)
