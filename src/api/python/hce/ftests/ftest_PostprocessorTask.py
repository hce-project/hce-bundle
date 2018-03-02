#!/usr/bin/python
# coding: utf-8

try:
  import cPickle as pickle
except ImportError:
  import pickle

import threading
import os
import sys
import ConfigParser
import base64
import logging
import json
import time
from subprocess import Popen
from subprocess import PIPE
from cement.core import foundation
from dc.EventObjects import URL
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dc.EventObjects import URLContentResponse
import app.Consts as APP_CONSTS
import app.Utils as Utils
from app.Utils import varDump
from dc_postprocessor.PostprocessorTask import PostprocessorTask
from dc_postprocessor.PostProcessingApplicationClass import PostProcessingApplicationClass
from dc_postprocessor.LinkResolver import LinkResolver


def getLogger():

  # create logger
  logger = logging.getLogger('console')
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


def getFileLogger():

  configName = '../ini/postprocessor_task_log-rt.ini'

  retval = os.getcwd()
  os.chdir('..')
  # read config
  logging.config.fileConfig(configName)

  # create logger
  log = Utils.MPLogger().getLogger()
  # log = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  os.chdir(retval)

  return log


# # execute command line command
#
# @param cmd - command line string
# @param inputStream - input stream to popen
# @return result object of execution and exit code
def executeCommand(cmd, inputStream=None, log=None):
  if log is not None:
    log.debug("Popen: %s", str(cmd))
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True)
  if isinstance(inputStream, basestring) and log is not None:
    log.debug("process.communicate(), len(inputStream)=" + str(len(inputStream)))
  (output, err) = process.communicate(input=inputStream)
  if log is not None:
    log.debug("Process std_error: %s", str(err))
    log.debug("Process output len =" + str(len(output)))
  exitCode = process.wait()
  if log is not None:
    log.debug("Process response exitCode: %s", str(exitCode))

  return output, exitCode


def generateBatch(id=0):
  siteId = id
  url = 'https://retrip.jp/external-link/?article_content_id=482406'
  urlObj = URL(siteId, url)

  processedContent = {'link':url}
  processedContents = [base64.b64encode(json.dumps(processedContent))]
  urlContentResponse = URLContentResponse(url=url, processedContents=processedContents)

  batchItem = BatchItem(siteId=siteId, urlId=urlObj.urlMd5, urlObj=urlObj, urlContentResponse=urlContentResponse)
  batchItem.properties = {"LINK_RESOLVE":{"method":{"retrip.jp/external-link":"GET"}}}
  # batchItem.properties = {}
  return Batch(id, batchItems=[batchItem])


def generateInputStream(id=0):
  return pickle.dumps(generateBatch(id=0))


def test(id=0, log=None):

  inputFile = '/tmp/input.tmp'
  outputFile = '/tmp/output.tmp'

  cmd = "cd ..; ../bin/postprocessor_task.py --config=../ini/postprocessor_task-rt.ini --inputFile=%s > %s" % (str(inputFile), str(outputFile))

  f = open(inputFile, 'w')
  f.write(generateInputStream())
  f.close()

  output, exitCode = executeCommand(cmd, log=log)

  if log is not None:
    log.debug("len(output) = %s", str(len(output)))
    log.debug("exitCode: %s", str(exitCode))
    log.debug("===Finish===")


def threadRun(id=0, log=None):

  sys.stdout.write("Thread ID = %s started.\n" % str(id))

  test(id=id, log=log)

  sys.stdout.write("Thread ID = %s stopped.\n" % str(id))


if __name__ == '__main__':

  logger = getLogger()
  # logger = getFileLogger()

  testCount = 5
  threadsList = []

  for i in xrange(testCount):
    threadsList.append(threading.Thread(target=threadRun, kwargs={'id':i, 'log':logger}))
    threadsList[-1].start()

  for i in xrange(testCount):
    threadsList[i].join()
  # #test(id=1, log=logger)
