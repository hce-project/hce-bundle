"""
HCE project, Python bindings, Crawler application.
Dynamic fetcher module tests.

@package: dc
@file ftest_dc_dynamic_fetcher.py
@author bgv <bgv.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 1.4.3
"""

import logging
import os
import json
import jsonpickle

from app.Utils import varDump
from dc_crawler.Fetcher import BaseFetcher


# create logger
logger = logging.getLogger('ftest_dc_dynamic_fetcher')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(thread)ld - %(threadName)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


if __name__ == "__main__":
  res = None

  print "CurDir:\n", os.path.dirname(os.path.realpath(__file__))
  loadHeaders = False
  headersDict = {}

  if loadHeaders:
    hdrs = None
    with open("../../ini/crawler-task_headers.txt", 'r') as f:
      hdrs = ''.join(f.readlines())
    for header in hdrs.splitlines():
      if not header:
        continue
      try:
        key, value = header[:header.index(':')].strip(), header[header.index(':') + len(':'):].strip()
      except Exception:
        print "header error:%s", header
        os.abort()
      headersDict[key] = value

  print "headersDict:\n", varDump(headersDict)

  allowRedirects = 1
  proxies = None
  authorization = None
  postData = None
  process_content_types = ["text/html"]
  maxResourceSize = 1024 * 1024
  maxHttpRedirects = 3
  fetchType = BaseFetcher.TYP_NORMAL
  localFilters = None
  urlObjDepth = 0
  url = 'https://www.google.co.jp/search?q=&gws_rd=cr' + \
        '###window.IFRAME_KWSRC="http://127.0.0.1/keywords_big.txt";window.IFRAME_KWSRC_FROM=0;window.IFRAME_KWSRC_N=2;'
  httpTimeout = 60000
  tm = int(httpTimeout) / 1000.0
  if isinstance(httpTimeout, float):
    tm += float('0' + str(httpTimeout).strip()[str(httpTimeout).strip().find('.'):])

  # Dynamic fetcher test
  headersDict = {'--disable-web-security':'', '--allow-running-insecure-content':''}
  macroCode = {"name":"tests",
               "sets":[{"name":"set1", "items":['', '', '', ''], "repeat":1, "delay":0}],
               "result_type":2,
               "result_content_type":"text/json",
               "result_fetcher_type":1}

  macroCode['sets'][0]['items'][0] = '1'
  macroCode['sets'][0]['items'][1] = \
  "\
  var s=window.document.createElement('script');\
  s.src='http://127.0.0.1/google-search1.js';\
  s.type='text/javascript';\
  window.document.head.appendChild(s);\
  "
  # macroCode['sets'][0]['items'][2] = '20'
  macroCode['sets'][0]['items'][2] = '!5:4:return window.IFRAME_DATA_READY;'
  macroCode['sets'][0]['items'][3] = \
  "\
  if(window.MACRO_COLLECT===undefined){\
    /*return [window.jQuery===undefined, window.MACRO_COLLECT===undefined];*/\
    return [];\
  }else{\
    return window.MACRO_COLLECT();\
  }\
  "
  fetchType = BaseFetcher.TYP_DYNAMIC
  # change current dir for webdriver executable run with path ./
  os.chdir("../../bin/")

  try:
    # Test of NORMAL (request lib based) fetcher
    res = BaseFetcher.get_fetcher(fetchType).open(url, timeout=tm, headers=headersDict,
                                                  allow_redirects=allowRedirects, proxies=proxies,
                                                  auth=authorization, data=postData, log=logger,
                                                  allowed_content_types=process_content_types,
                                                  max_resource_size=maxResourceSize,
                                                  max_redirects=maxHttpRedirects,
                                                  filters=localFilters, depth=urlObjDepth, macro=macroCode)

  except Exception, err:
    # logger.debug("Exception:\n%s", varDump(err))
    print "Exception:\n", varDump(err)

  # rd = varDump(res)
  rd = json.dumps(json.loads(jsonpickle.encode(res)), indent=2)
  # logger.debug("Result:\n%s", varDump(res))
  print "Result:\n", rd


