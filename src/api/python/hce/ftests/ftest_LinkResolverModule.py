#!/usr/bin/python
# coding: utf-8

import json
import base64
import ConfigParser
import logging
from dc.EventObjects import URL
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dc.EventObjects import URLContentResponse
from dc_postprocessor.LinkResolver import LinkResolver
from dc_postprocessor.PostProcessingApplicationClass import PostProcessingApplicationClass
import app.Consts as APP_CONSTS
from app.Utils import varDump

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

  configName = '../../ini/postprocessor_task.ini'
  headerFileName = '../../ini/crawler-task_headers.txt'

  postProcessingApplicationClass = PostProcessingApplicationClass()
  postProcessingApplicationClass.configParser = ConfigParser.ConfigParser()
  postProcessingApplicationClass.configParser.optionxform = str
  readOk = postProcessingApplicationClass.configParser.read(configName)
  logger.debug("Read config: %s", str(readOk))

  postProcessingApplicationClass.configParser.set('LinkResolver', 'headers_file', headerFileName)

  siteId = 12345
  url = 'http://127.0.0.1/test.html,https://retrip.jp/external-link/?article_content_id=482406'
  urlObj = URL(siteId, url)

  processedContent = {'link':url}
  processedContents = [base64.b64encode(json.dumps(processedContent))]
  urlContentResponse = URLContentResponse(url=url, processedContents=processedContents)

  batchItem = BatchItem(siteId=siteId, urlId=urlObj.urlMd5, urlObj=urlObj, urlContentResponse=urlContentResponse)
  batchItem.properties = {"LINK_RESOLVE":{"method":{"retrip.jp/external-link":"GET"}}}
  batch = Batch(1, [batchItem])

  logger.debug("Input batch: %s", varDump(batch))

  linkResolver = LinkResolver(logger, postProcessingApplicationClass.getConfigOption)
  linkResolver.init()
  for i in xrange(len(batch.items)):
    batch.items[i] = linkResolver.processBatchItem(batch.items[i])

  logger.debug("Output batch: %s", varDump(batch))

  logger.debug("Resolved url: %s", str(json.loads(base64.b64decode(batch.items[0].urlContentResponse.processedContents[0]))['link']))

