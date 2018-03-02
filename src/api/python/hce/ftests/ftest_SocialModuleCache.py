#!/usr/bin/python
# coding: utf-8


import os
import sys
import json
import base64
import logging
import ConfigParser
from dc.EventObjects import URL
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dc.EventObjects import URLContentResponse
from dc_postprocessor.SocialModuleCache import SocialModuleCache
from dc_postprocessor.PostProcessingApplicationClass import PostProcessingApplicationClass
import app.Consts as APP_CONSTS
from app.Utils import varDump
import app.Utils as Utils
from app.CacheDataStorage import CacheDataStorage


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


def getFileLogger():

  configFileName = '../ini/postprocessor_task_log-rt.ini'

  # read config
  logging.config.fileConfig(configFileName)

  # create logger
  log = Utils.MPLogger().getLogger()
  # log = logging.getLogger(APP_CONSTS.LOGGER_NAME)

  return log


if __name__ == '__main__':
  retval = os.getcwd()
  os.chdir('..')

  logger = getLogger()

  logConfigFileName = '../ini/postprocessor_task_log-rt.ini'
  configName = '../ini/postprocessor_task.ini'
  headerFileName = '../ini/crawler-task_headers.txt'

  postProcessingApplicationClass = PostProcessingApplicationClass()
  postProcessingApplicationClass.configParser = ConfigParser.RawConfigParser()
  postProcessingApplicationClass.configParser.optionxform = str
  readOk = postProcessingApplicationClass.configParser.read(configName)
  logger.debug("Read config: %s", str(readOk))

  postProcessingApplicationClass.configParser.set('SocialModule', 'executionLocal', 'cat %INPUT_FILE% > %OUTPUT_FILE%')
  postProcessingApplicationClass.configParser.set('SocialModule', 'executionType', 0)

  postProcessingApplicationClass.logger = logger

  siteId = 12345
  url = 'https://www.theguardian.com/us-news/2016/jan/05/obama-gun-control-executive-action-background-checks-licenses-gun-shows-mental-health-funding'
  urlObj = URL(siteId, url)

  processedContent = [{"title":"Tearful Obama tightens gun control and tells inactive Congress: 'We can't wait'",
                      "source_url": url,
                      "social_tw_posts":0,
                      "social_fb_posts":0}]

  processedContents = [base64.b64encode(json.dumps(processedContent))]
  urlContentResponse = URLContentResponse(url=url, processedContents=processedContents)
  urlObj.tagsCount = len(processedContent)

  batchItem = BatchItem(siteId=siteId, urlId=urlObj.urlMd5, urlObj=urlObj, urlContentResponse=urlContentResponse)
#   batchItem.properties = {"SOCIAL_RATE":json.dumps({"retries":2, "retries_delay":5, "retries_type":1, "interval":10, "lang":"en", "sentiment":1, "debug":1, "timeout":400, "social_list":{"tw":["https://www.twitter.com", "window.IFRAME_QUERY_URL=\"https://twitter.com/search?f=tweets&vertical=default&q=%25QUERY_STRING%25&src=typd\",window.IFRAME_CSCROLL_COUNT=10;window.IFRAME_MAX_TIME=350;window.IFRAME_SFIELD='source_url';", {"name":"tests", "sets":[{"name":"set1", "items":["1", "%MACRO_DATA%", "http://127.0.0.1/social.js", "!5:76:return window.IFRAME_DATA_READY;", "return window.MACRO_COLLECT;"], "repeat":1, "delay":0}], "result_type":0, "result_content_type":"text/json"}]} })}
#   batchItem.properties = {"SOCIAL_RATE": "{\"retries\":2, \"retries_delay\":10, \"retries_type\":1, \"interval\":10,\"lang\":\"en\", \"sentiment\":1, \"debug\":1, \"timeout\":400, \"social_list\":{\"tw\":[\"https:\/\/www.twitter.com\/\",\"window.IFRAME_QUERY_URL=\\\"https:\/\/twitter.com\/search?f=tweets&vertical=default&q=%25QUERY_STRING%25&src=typd\\\",window.IFRAME_CSCROLL_COUNT=10;window.IFRAME_MAX_TIME=360;window.IFRAME_SFIELD='source_url';\",{\"name\":\"tests\", \"sets\":[{\"name\":\"set1\", \"items\":[\"3\", \"%MACRO_DATA%\", \"http:\/\/127.0.0.1\/social.js\", \"!5:76:return window.IFRAME_DATA_READY;\", \"return window.MACRO_COLLECT;\"], \"repeat\":1, \"delay\":0}], \"result_type\":0, \"result_content_type\":\"text\/json\"}]} }"}
  batchItem.properties = {"SOCIAL_RATE": "{\"retries\":2, \"retries_delay\":5, \"retries_type\":1, \"interval\":10,\"lang\":\"en\", \"sentiment\":1, \"debug\":1, \"timeout\":400, \"social_list\":{\"tw\":[\"https:\/\/www.twitter.com\",\"window.IFRAME_QUERY_URL=\\\"https:\/\/twitter.com\/search?f=tweets&vertical=default&q=%25QUERY_STRING%25&src=typd\\\",window.IFRAME_CSCROLL_COUNT=100;window.IFRAME_MAX_TIME=350;window.IFRAME_SFIELD='source_url';\",{\"name\":\"tests\", \"sets\":[{\"name\":\"set1\", \"items\":[\"1\", \"%MACRO_DATA%\", \"http:\/\/127.0.0.1\/social.js\", \"!5:20:return window.IFRAME_DATA_READY;\", \"return window.MACRO_COLLECT;\"], \"repeat\":1, \"delay\":0}], \"result_type\":0, \"result_content_type\":\"text\/json\"}]} }"}
  batch = Batch(77777, [batchItem])

  logger.debug("Input batch: %s", varDump(batch))
  socialModuleCache = SocialModuleCache(postProcessingApplicationClass.getConfigOption, postProcessingApplicationClass.logger)
  socialModuleCache.init()
#   batch = socialModule.processBatch(batch)
#   logger.debug("Output batch: %s", varDump(batch))

  logger.debug("validationMap: %s", str(socialModuleCache.configOptions.validationMap))

  # logger.debug("Resolved url: %s", str(json.loads(base64.b64decode(batch.items[0].urlContentResponse.processedContents[0]))['link']))

  socialDataList = [{"social_tw_posts":0, "social_fb_posts":0}, {"social_tw_posts":0}, {"social_fb_posts":0}]
  for socialData in socialDataList:
    logger.info("Social data: %s is valid: %s", str(socialData), str(socialModuleCache.isValid(socialData)))

  itemsDataDict = CacheDataStorage.ItemsDataDict(socialModuleCache.configOptions.uniqueKeyName, socialModuleCache.configOptions.cachedFieldName)
  # itemsDataDict.add(urlmd5='123', socialData={"social_tw_posts":5, "social_tw_likes":45})
  # itemsDataDict.add(urlmd5='123', socialData={"social_fb_posts":0})
  itemsDataDict.add(urlmd5='125', socialData={"social_tw_posts":0, "social_fb_posts":0})
  socialModuleCache.saveSocialDataToDB(itemsDataDict)


  os.chdir(retval)


