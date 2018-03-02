#!/usr/bin/python

import logging
import app.Consts as APP_CONSTS
from dc_crawler.UrlLimits import UrlLimits


def getLogger():
  # create logger
  log = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  log.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)

  return log


def testExecution(testData, siteProperties, log=None):
  resData = None
  if APP_CONSTS.URL_LIMITS in siteProperties:
    resData = UrlLimits.applyLimits(siteProperties[APP_CONSTS.URL_LIMITS], testData, log)

  return resData


testData = ["http://www.huffingtonpost.jp/news/lifestyle/",
            "http://www.huffingtonpost.jp/news/ebola-fever-jp/",
            "http://www.huffingtonpost.jp/news/technology/",
            "http://www.huffingtonpost.jp/news/mirainotsukurikata",
            "http://www.huffingtonpost.jp/news/career/",
            "http://www.huffingtonpost.jp/news/world/",
            "http://www.huffingtonpost.jp/news/japan-entertainment",
            "http://www.huffingtonpost.jp/news/workandlife",
            "http://www.huffingtonpost.jp/the-news/",
            "http://www.huffingtonpost.jp/news/politics/",
            "http://www.huffingtonpost.jp/news/hongkong-protests",
            "http://www.huffingtonpost.jp/news/ontake-mountain/",
            "http://www.huffingtonpost.jp/news/society/",
            "http://www.huffingtonpost.jp/news/sports/",
            "http://www.huffingtonpost.jp/news/business/"]

sitePropertiesList = [{'URL_LIMITS':[{"max_items":0}]},
                      {'URL_LIMITS':[{"max_items":2}]},
                      {'URL_LIMITS':[{"max_items":0, "offset":10}]},
                      {'URL_LIMITS':[{"max_items":2, "offset":0}]},
                      {'URL_LIMITS':[{"root_url_mask":["huffingtonpost.jp"], "content_type_mask":["html"], "max_items":10, "offset":0}]},
                      {'URL_LIMITS':[{"root_url_mask":["huffingtonpost.jp"], "content_type_mask":["html"], "max_items":0, "offset":10}]},
                      {'URL_LIMITS':[{"root_url_mask":["huffingtonpost.jp/the-news/"], "content_type_mask":["html"], "max_items":10, "offset":0}]},
                      {'URL_LIMITS':[{"root_url_mask":["huffingtonpost.jp/the-news/"], "content_type_mask":["html"], "max_items":0, "offset":10}]},
                      {'URL_LIMITS':[{"root_url_mask":["huffingtonpost.jp"], "content_type_mask":["xml"], "max_items":10}]},
                      {'URL_LIMITS':[{"root_url_mask":["huffingtonpost.jp"], "content_type_mask":["xml"], "max_items":0}]}]


logger = getLogger()

logger.debug("Input data len = %s", str(len(testData)))

# for siteProperties in sitePropertiesList:
#   resData = testExecution(testData, siteProperties, logger)
#   logger.debug("Output data len = %s", str(len(resData)))

resData = testExecution(testData, sitePropertiesList[5], logger)

logger.debug("Output data len = %s", str(len(resData)))

for url in resData:
  logger.debug("Result url: %s", str(url))


