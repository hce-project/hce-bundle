#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging
import requests.exceptions

from dc_crawler.RequestsRedirectWrapper import RequestsRedirectWrapper
from app.Utils import varDump
import app.Consts as APP_CONSTS


def getLogger():
  # create logger
  logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  logger.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(ch)

  return logger


if __name__ == '__main__':

  logger = getLogger()

  url = 'https://ukranews.com/rss/news_all_uk.xml'
  method = 'GET'
  timeout = 10.0
  headers = {'Accept-Language':'en-US,en;q=0.8,en;q=0.6,us;q=0.4,us;q=0.2,ja;q=0.2', 'Accept-Encoding':'gzip, deflate', '--disable-setuid-sandbox':'', 'Connection':'close', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome 49.0.2623.87 Safari/537.36', 'Cache-Control':'no-cache', '--log-chrome-debug-log':'', 'Referer':u'http://ukranews.com/rss/news_all_uk.xml', '--allow-running-insecure-content':'', 'Pragma':'no-cache', '--user-data-dir-zip':'/tmp/custom_profile_fb_noimg50b.zip', '--allow-file-access-from-files':'', '--disable-web-security':''}
  allow_redirects = True
  proxy_setting = None
  auth = None
  data = None
  max_redirects = 10
  filters = None

  try:
    requestsRedirect = RequestsRedirectWrapper()
    impl_res = requestsRedirect.request(url=url,
                                        method=method,
                                        timeout=timeout,
                                        headers=headers,
                                        allowRedirects=allow_redirects,
                                        proxySetting=proxy_setting,
                                        auth=auth,
                                        data=data,
                                        maxRedirects=max_redirects,
                                        filters=filters)

    logger.debug("!!! impl_res.headers: %s", varDump(impl_res.headers))
    logger.debug("!!! impl_res.url: %s", str(impl_res.url))

  except requests.exceptions.RequestException, err:
    logger.error("!!! RequestException: %s", str(err))
  except Exception, err:
    logger.error("!!! Exception: %s", str(err))

