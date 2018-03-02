#!/usr/bin/python
# coding: utf-8


import logging
from dc_crawler.CollectUrlsLimits import CollectUrlsLimits
import app.Consts as APP_CONSTS

def getLogger():
  # create logger
  log = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  log.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)

  return log


if __name__ == '__main__':

  logger = getLogger()

  url = 'http://localhost.html'

  propertyDict = {"COLLECT_URLS_LIMITS":{".*":[["MaxURLSFromPage", 5]]}}

  maxUrlsFormPage = 10

  maxUrlsFormPage = CollectUrlsLimits.execute(properties=propertyDict['COLLECT_URLS_LIMITS'],
                                              url=url,
                                              optionsName=CollectUrlsLimits.MAX_URLS_FROM_PAGE,
                                              default=maxUrlsFormPage,
                                              log=logger)

  logger.info("maxUrlsFormPage = %s, type = %s", str(maxUrlsFormPage), str(type(maxUrlsFormPage)))
