#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging
import logging.config
import ConfigParser
from sys import stdout
from sys import stderr
from app.Utils import varDump

import dc_crawler.DBTasksWrapper as DBTasksWrapper
from app.ContentEvaluator import ContentEvaluator

def getLogger():
  # create logger
  logger = logging.getLogger('hce')
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


def getDBWrapper():
  CONFIG_NAME = "../../ini/db-task.ini"
  cfgParser = ConfigParser.ConfigParser()
  cfgParser.read(CONFIG_NAME)
  return DBTasksWrapper.DBTasksWrapper(cfgParser)



logger = getLogger()
dbWrapper = getDBWrapper()

contentData = '****************<!--TEST-->*****************'

json = "[{\"WHERE\":\"RAW\", \"WHAT\":\"<!--(.*)-->\", \"WITH\":\" \", \"CONDITION\":\"ContentType='text/html'\"}]"

sqlExpression = "ContentType='text/html'"
siteId = '40d202ab0424bd4ff6768171befd98e4'
# siteId = '0'

# res = ContentEvaluator.executeSqlExpression(dbWrapper, siteId, sqlExpression)
# logger.debug('res:' + str(res))
# logger.debug("\n\n")

logger.debug("contentData: %s", varDump(contentData))
contentData = ContentEvaluator.executeReplace(dbWrapper, siteId, json, contentData)
logger.debug("")
logger.debug("contentData: %s", varDump(contentData))

