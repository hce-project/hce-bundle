"""
HCE project, Python bindings, Crawler application.
FetcherPost module tests.

@package: dc
@file ftest_dc_FetcherPost.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2018 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import logging
import os
import sys
import json
import jsonpickle

import app.Consts as APP_CONSTS
from app.Utils import varDump
from dc_crawler.Fetcher import BaseFetcher
from dc_crawler.Fetcher import Response
from dc_crawler.FetcherPost import FetcherPost


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


def getFetcherResponse(fileName):
  #variable for result
  ret = None
  try:
    with open(fileName) as f:
      dataDict = json.load(f, encoding='utf-8')

      response = Response()      
      for name, value in dataDict.items():
        if hasattr(response, name):
          setattr(response, name, value)

      ret = response
  except Exception, err:
    sys.stderr.write("Extract fetcher response from '%s' failed. Error: %s" % (str(fileName), str(err)))
    
  return ret
  

def getInputData(fileName):
  # variable for result
  ret = None
  try:
    with open(fileName) as f:
      ret = json.load(f, encoding='utf-8')

  except Exception, err:
    sys.stderr.write("Extract input data collect from '%s' failed. Error: %s" % (str(fileName), str(err)))

  return ret


if __name__ == "__main__":
  ##Constants used in test
  fetcherResponseFile = './jsons/dc_fetcher_media_page_response.json'
  inputDataCollectProtocolFile = './jsons/dc_fetcher_media_page_input_data.json'
  # properties = {FetcherPost.PROPERTY_OPTION_ID_COLLECT_NAME:1, FetcherPost.PROPERTY_OPTION_PAGES_FILE:'/tmp/fb_pages.txt'}
  properties = {FetcherPost.PROPERTY_OPTION_DATA_SCRAPING_NAME:1}
  
  # create logger
  logger = getLogger()
  logger.debug("Logger created.")  

  response = getFetcherResponse(fetcherResponseFile)
  logger.debug("Input test response: %s", varDump(response))
  
  fetcherPost = FetcherPost(properties=properties, log=logger)
  logger.debug("FetcherPost created.")
  fetcherPost.data = getInputData(inputDataCollectProtocolFile)

  fetcherPost.process(response=response)
  logger.debug("Processing finished.")

  logger.debug("Result test response: %s", varDump(response))

