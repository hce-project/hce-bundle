# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
SocialModule is a module class and has a main functional for call social task module.

@package: dc_postprocessor
@file SocialModule.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

try:
  import cPickle as pickle
except ImportError:
  import pickle

import re
import os
import json
import time
import copy
import base64
import getpass
import tempfile
import ConfigParser
from subprocess import Popen
from subprocess import PIPE
from multiprocessing.dummy import Pool as ThreadPool

from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dc_postprocessor.PostProcessingModuleClass import PostProcessingModuleClass
from dc_postprocessor.SocialModuleCache import SocialModuleCache
from dc_crawler.DBTasksWrapper import DBTasksWrapper
from dc_crawler.DBProxyWrapper import DBProxyWrapper
from dc_crawler.UserProxyJsonWrapper import UserProxyJsonWrapper
from app.Utils import InterruptableThread


# This object is a run at once module for call social task module.
class SocialModule(PostProcessingModuleClass):

  # # Constants for property 'SOCIAL_RATE'
  SOCIAL_RATE_PROPERTY_NAME = 'SOCIAL_RATE'
  USER_PROXY_PROPERTY_NAME = 'USER_PROXY'
  PARAM_USER_PROXY = 'user_proxy'

  # # Constans used options from config file
  OPTION_EXECUTION_LOCAL = 'executionLocal'
  OPTION_EXECUTION_REMOTE = 'executionRemote'
  OPTION_EXECUTION_TYPE = 'executionType'
  OPTION_DB_TASK_INI = 'db_task_ini'
  OPTION_BATCH_ITEMS_COUNT = "batchItemsCount"
  OPTION_USAGE_CACHE = "usageCache"

  DEFAULT_VALUE_BATCH_ITEMS_COUNT = 1

  EXECUTION_TYPE_LOCAL = 0
  EXECUTION_TYPE_REMOTE = 1
  EXECUTION_TYPE_DEFAULT = EXECUTION_TYPE_LOCAL

  USAGE_CACHE_DEFAULT = True

  # Constants used in class
  TMP_INPUT_FILE_NAME = 'in'
  TMP_OUTPUT_FILE_NAME = 'out'
  TMP_FILE_NAMES_LIST = [TMP_INPUT_FILE_NAME, TMP_OUTPUT_FILE_NAME]

  # Constants of used macro
  MACRO_INPUT_FILE = '%INPUT_FILE%'
  MACRO_OUTPUT_FILE = '%OUTPUT_FILE%'
  MACRO_USER_NAME = '%USER_NAME%'
  MACRO_NETWORKS = '%NETWORKS%'

  # pattern for search of social tags
  PATTERN_SEARCH_SOCIAL_TAG = 'social_(.*)_.*'

  # Constants of error messages
  ERROR_MSG_INITIALIZATION_CALLBACK = "Error initialization of callback function for get config options."
  ERROR_MSG_INITIALIZATION_LOGGER = "Error initialization of self.logger."
  ERROR_MSG_EXECUTION_TYPE = "Wrong execution type ( %s ) was got from config file."
  ERROR_MSG_EXECUTION_CMD_EMPTY = "Execution command line is empty."
  ERROR_MSG_CREATION_DBTASK_WRAPPER = "Creation DBTaskWrapper failed. Error: %s"
  ERROR_MSG_LOAD_USER_PROXY = "Load parameter '" + PARAM_USER_PROXY + "' from site property failed. Error: %s"


  # Default initialization
  def __init__(self, getConfigOption=None, log=None):
    PostProcessingModuleClass.__init__(self, getConfigOption, log)

    self.cmd = None
    self.dbWrapper = None
    self.batchItemsCount = self.DEFAULT_VALUE_BATCH_ITEMS_COUNT
    self.usageCache = self.USAGE_CACHE_DEFAULT
    self.socialModuleCache = SocialModuleCache(configOptionsExtractor=getConfigOption, log=log, delayInit=True)


  # # initialization
  #
  # @param - None
  # @return - None
  def init(self):
    if self.getConfigOption is None:
      raise Exception(self.ERROR_MSG_INITIALIZATION_CALLBACK)

    if self.logger is None:
      raise Exception(self.ERROR_MSG_INITIALIZATION_LOGGER)

    self.cmd = self.__getCmd()
    self.dbWrapper = self.__getDBWrapper()
    self.batchItemsCount = int(self.getConfigOption(sectionName=self.__class__.__name__, optionName=self.OPTION_BATCH_ITEMS_COUNT))
    self.logger.debug("Use batch items count = %s", str(self.batchItemsCount))

    self.usageCache = bool(int(self.getConfigOption(sectionName=self.__class__.__name__, optionName=self.OPTION_USAGE_CACHE)))
    self.logger.debug("Usage cache = %s", str(self.usageCache))


  # # get DBTasksWrapper instance
  #
  # @param - None
  # @return DBTasksWrapper instance
  def __getDBWrapper(self):
    # variable for result
    ret = None
    try:
      configParser = ConfigParser.ConfigParser()
      configParser.read(self.getConfigOption(sectionName=self.__class__.__name__, optionName=self.OPTION_DB_TASK_INI))
      ret = DBTasksWrapper(configParser)
    except Exception, err:
      raise Exception(self.ERROR_MSG_CREATION_DBTASK_WRAPPER % str(err))

    return ret


  # # get comamnd line use parameter from config file
  #
  # @param - None
  # @return - command line options as string
  def __getCmd(self):
    # variable for result
    ret = None
    executionType = int(self.getConfigOption(sectionName=self.__class__.__name__,
                                             optionName=self.OPTION_EXECUTION_TYPE,
                                             defaultValue=self.EXECUTION_TYPE_DEFAULT))

    if executionType == self.EXECUTION_TYPE_LOCAL:
      ret = self.getConfigOption(sectionName=self.__class__.__name__,
                                 optionName=self.OPTION_EXECUTION_LOCAL,
                                 defaultValue='')

    elif executionType == self.EXECUTION_TYPE_REMOTE:
      ret = self.getConfigOption(sectionName=self.__class__.__name__,
                                 optionName=self.OPTION_EXECUTION_REMOTE,
                                 defaultValue='')

    else:
      raise Exception(self.ERROR_MSG_EXECUTION_TYPE % str(executionType))

    if ret == "":
      raise Exception(self.ERROR_MSG_EXECUTION_CMD_EMPTY)

    return ret


  # # execute command line command
  #
  # @param cmd - command line string
  # @param inputStream - input stream to popen
  # @return result object of execution and exit code
  def executeCommand(self, cmd, inputStream=''):
    self.logger.debug("Popen: %s", str(cmd))
    process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True, executable='/bin/bash')
    self.logger.debug("process.communicate(), len(inputStream)=" + str(len(inputStream)))
    (output, err) = process.communicate(input=inputStream)
    self.logger.debug("Process std_error=: %s", str(err))
    self.logger.debug("Process output len=:" + str(len(output)))
    exitCode = process.wait()
    self.logger.debug("Process response exitCode: %s", str(exitCode))

    return output, exitCode


  # # create temporary files
  #
  # @param - None
  # @return dict of handlers temporary files (key - name, value -handler)
  def __createTemporaryFiles(self):
    # variable for result
    files = {}
    for name in self.TMP_FILE_NAMES_LIST:
      files[name] = tempfile.NamedTemporaryFile(delete=False)

    return files


  # # remove temporary files
  #
  # @param tempFiles - temporary files dictionary
  # @return - None
  def __removeTemporaryFiles(self, tempFiles):
    if isinstance(tempFiles, dict):
      for f in tempFiles.values():
        if f is not None and os.path.isfile(f.name):
          os.unlink(f.name)


  # # make input file
  #
  # @param tempFiles - list handles of temporary files
  # @param inputBatch - input batch instance
  # @return - None
  def __makeInputFile(self, tempFiles, inputBatch):

    if isinstance(tempFiles, dict) and self.TMP_INPUT_FILE_NAME in tempFiles:
      tempFiles[self.TMP_INPUT_FILE_NAME].write(pickle.dumps(inputBatch))
      tempFiles[self.TMP_INPUT_FILE_NAME].close()


  # # read output file
  #
  # @param tempFiles - list handles of temporary files
  # @return extracted batch object
  def __readOutputFile(self, tempFiles):
    # variable for result
    ret = None
    if tempFiles[self.TMP_OUTPUT_FILE_NAME] is not None:
      ret = pickle.loads(tempFiles[self.TMP_OUTPUT_FILE_NAME].read())
      tempFiles[self.TMP_OUTPUT_FILE_NAME].close()

    return ret


  # # make command line for social task
  #
  # @param tempFiles - list handles of temporary files
  # @param templateCmdLine - template of cmd
  # @return command line string ready for execution
  def __makeCmdLine(self, tempFiles, templateCmdLine):
    # variable for result
    ret = templateCmdLine

    # set temporary file names
    if isinstance(tempFiles, dict):

      if tempFiles[self.TMP_INPUT_FILE_NAME] is not None:
        ret = re.sub(pattern=self.MACRO_INPUT_FILE, repl=tempFiles[self.TMP_INPUT_FILE_NAME].name, string=ret, flags=re.I + re.U)

      if tempFiles[self.TMP_OUTPUT_FILE_NAME] is not None:
        ret = re.sub(pattern=self.MACRO_OUTPUT_FILE, repl=tempFiles[self.TMP_OUTPUT_FILE_NAME].name, string=ret, flags=re.I + re.U)

      ret = re.sub(pattern=self.MACRO_NETWORKS, repl="''", string=ret, flags=re.I + re.U)
      ret = re.sub(pattern=self.MACRO_USER_NAME, repl=getpass.getuser(), string=ret, flags=re.I + re.U)

    return ret


  # # fill user proxy data each batch item
  #
  # @param batchItem - batch item for update
  # @return - None
  def __fillUserProxyData(self, batchItem):

    if self.PARAM_USER_PROXY in batchItem.properties[self.SOCIAL_RATE_PROPERTY_NAME]:
      try:
        socialRateProperties = json.loads(batchItem.properties[self.SOCIAL_RATE_PROPERTY_NAME])

        if self.PARAM_USER_PROXY in socialRateProperties:
          self.logger.debug("!!! user_proxy: %s", str(socialRateProperties[self.PARAM_USER_PROXY]))
          userProxyJsonWrapper = UserProxyJsonWrapper(socialRateProperties[self.PARAM_USER_PROXY])
          self.logger.debug("!!! source: %s", str(userProxyJsonWrapper.getSource()))
          self.logger.debug("!!! proxies: %s", str(userProxyJsonWrapper.getProxies()))

          if userProxyJsonWrapper.getSource() == UserProxyJsonWrapper.SOURCE_DATABASE:
            self.logger.debug("Getting proxies list from DB.")

            self.logger.debug("!!! batchItem.siteId: %s", str(batchItem.siteId))

            proxyWrapper = DBProxyWrapper(self.dbWrapper)
            proxiesList = proxyWrapper.getEnaibledProxies(batchItem.siteId)
            self.logger.debug("!!! type: %s, proxiesList: %s", str(type(proxiesList)), str(proxiesList))

            userProxyJsonWrapper.addProxyList(proxiesList)
            userProxyJsonWrapper.setSource(UserProxyJsonWrapper.SOURCE_PROPERTY)
            self.logger.debug("!!! userProxyJsonWrapper.getProxies(): %s", str(userProxyJsonWrapper.getProxies()))
            self.logger.debug("!!! userProxyJsonWrapper.getSource(): %s", str(userProxyJsonWrapper.getSource()))

            batchItem.properties[self.SOCIAL_RATE_PROPERTY_NAME] = json.dumps(socialRateProperties)

      except Exception, err:
        self.logger.error(self.ERROR_MSG_LOAD_USER_PROXY, str(err))

      self.logger.debug("!!! batchItem.properties: %s", str(batchItem.properties))


    return batchItem


  # # check social data in cache
  #
  # @param batchItemsList - input batch items list
  # @param socialModuleCache - SocialModuleCache
  # @return truncated batch items list
  def checkSocialDataInCache(self, batchItemsList):
    # variable for result
    batchItems = []

    if self.usageCache and len(batchItemsList) > 0:
      self.socialModuleCache.init()
      self.logger.debug("Cache initialized. Ready for usage.")

      self.socialModuleCache.removeObsoleteCachedData()
      self.logger.debug("Obsolete data from cache was removed.")

      for batchItem in batchItemsList:
        if isinstance(batchItem, BatchItem):
          try:
            cachedData = self.socialModuleCache.getCachedlDataFromDB(urlmd5=batchItem.urlId)
#             self.logger.info("cachedData: %s, type: %s", str(cachedData), str(type(cachedData)))

            if self.socialModuleCache.isValid(cachedData):
              self.socialModuleCache.itemsDataDict.add(urlmd5=batchItem.urlId, socialData=cachedData)
            else:
              batchItems.append(batchItem)

          except Exception, err:
            self.logger.error(str(err))

      self.logger.debug("Found cached data for %s elements.", str(self.socialModuleCache.itemsDataDict.getSize()))
    else:
      batchItems = batchItemsList

    return batchItems


  # # Get social data from processed content
  #
  # @param processedContent - processed content as dictionary
  # @return social data dictionary
  def getSocialData(self, processedContent):
    # variable for result
    socialData = {}
    if isinstance(processedContent, dict):
      for key, value in processedContent.items():
        if re.search(pattern=self.PATTERN_SEARCH_SOCIAL_TAG, string=key, flags=re.U+re.I) is not None:
          socialData[key] = value

    return socialData


  # # Save social data in cache storage
  #
  # @param batchItem - batch item instance
  # @return batch item instance
  def saveSocialDataInCache(self, batchItem):
    if self.usageCache:
      if isinstance(batchItem, BatchItem) and batchItem.urlContentResponse is not None and isinstance(batchItem.urlContentResponse.processedContents, list):
        try:
          cachedData = self.socialModuleCache.getCachedlDataFromDB(urlmd5=batchItem.urlId)
#           self.logger.info("cachedData: %s", str(cachedData))

          for k in range(len(batchItem.urlContentResponse.processedContents)):
            processedContents = json.loads(base64.b64decode(batchItem.urlContentResponse.processedContents[k]), encoding='utf-8')
#             self.logger.debug("!!! processedContents: %s" , str(processedContents))
            if isinstance(processedContents, list):
              for i in range(len(processedContents)):
                if isinstance(processedContents[i], dict):
                  mergedData = self.socialModuleCache.mergeSocialData(cachedData, self.getSocialData(processedContents[i]))
                  if len(mergedData) > 0:
                    self.logger.debug("Save merged data to DB: %s" , str(mergedData))
                    # save social data to DB
                    self.socialModuleCache.setCachedDataToDB(urlmd5=batchItem.urlId,
                                                             url=None if batchItem.urlObj is None else batchItem.urlObj.url,
                                                             socialData=mergedData)
                    # update processed content by merged social data
                    processedContents[i].update(mergedData)

              # update url content responce object
              batchItem.urlContentResponse.processedContents[k] = base64.b64encode(json.dumps(processedContents, encoding='utf-8'))

        except Exception, err:
          self.logger.error(str(err))

    return batchItem


  # # Update by cached data
  #
  # @param batchItemsList - input batch items list
  # @return updated batch items list
  def updateByCachedData(self, batchItemsList):
    # variable for result
    batchItems = []

    if self.usageCache and len(batchItemsList) > 0:
      for batchItem in batchItemsList:
        if isinstance(batchItem, BatchItem) and batchItem.urlContentResponse is not None and isinstance(batchItem.urlContentResponse.processedContents, list):
          try:
            cachedData = self.socialModuleCache.itemsDataDict.getCachedData(urlmd5=batchItem.urlId)
#             self.logger.info("cachedData: %s, type: %s", str(cachedData), str(type(cachedData)))

            if isinstance(cachedData, dict) and len(cachedData) > 0:
              for k in range(len(batchItem.urlContentResponse.processedContents)):
                processedContents = json.loads(base64.b64decode(batchItem.urlContentResponse.processedContents[k]), encoding='utf-8')
#                 self.logger.debug("!!! processedContents: %s" , str(processedContents))
                if isinstance(processedContents, list):
                  for i in range(len(processedContents)):
                    if isinstance(processedContents[i], dict):
                      # update processed content by merged social data
                      processedContents[i].update(cachedData)

                # update url content responce object
                batchItem.urlContentResponse.processedContents[k] = base64.b64encode(json.dumps(processedContents, encoding='utf-8'))

              self.logger.debug("Apply from cache data for %s", str(batchItem.urlId))

          except Exception, err:
            self.logger.error(str(err))

          batchItems.append(batchItem)

      self.logger.debug("Updated from cache DB %s elements.", str(self.socialModuleCache.itemsDataDict.getSize()))
    else:
      batchItems = batchItemsList

    return batchItems


  # # process batch item interface method
  #
  # @param batchObj - batch instance
  # @return - None
  def processBatch(self, batch):
    started = time.time()

    if isinstance(batch, Batch):
      localBatchItems = []
      # accumulate batch items for send to social task processing
      for i in xrange(len(batch.items)):
        if self.SOCIAL_RATE_PROPERTY_NAME in batch.items[i].properties and batch.items[i].urlObj is not None and batch.items[i].urlObj.tagsCount > 0:
          localBatchItems.append(self.__fillUserProxyData(batch.items[i]))

      # check social data in cache storage
      localBatchItems = self.checkSocialDataInCache(localBatchItems)

      if len(localBatchItems) > 0:
        self.logger.debug("Accumulated %s items from %s total for send to SocialTask", str(len(localBatchItems)), str(len(batch.items)))
        batches = []
        # split accord to batch items count
        itemsList = [localBatchItems[i:i + self.batchItemsCount] for i  in range(0, len(localBatchItems), self.batchItemsCount)]
        for batchItems in itemsList:
          localBatch = Batch(batchId=batch.id)
          localBatch.items = batchItems
          batches.append(localBatch)

        # execution parallel
        foundCount = 0
        pool = ThreadPool(len(batches))
        results = pool.map(self.executeSocialTask, batches)
        pool.close()
        pool.join()
        self.logger.debug("Recieved %s batches", str(len(results)))
        # update batch items after processing of the social task
        for i in xrange(len(batch.items)):
          for localBatch in results:
            for batchItem in localBatch.items:
              if batch.items[i].urlId == batchItem.urlId and batch.items[i].siteId == batchItem.siteId:
                # save social data in cache if necessary
                batch.items[i] = self.saveSocialDataInCache(batchItem)
                self.logger.debug("Found result for %s", str(batch.items[i].urlId))
                foundCount += 1

        self.logger.debug("Found results for %s items, spend time = %s sec.", str(foundCount), str(int(time.time() - started)))

      # update by cached data
      batch.items = self.updateByCachedData(batch.items)
    else:
      self.logger.error("Input object has type: %s", str(type(batch)))

    return batch


  # # Execute social task processing
  #
  # @param inputBatch - input batch instance
  # @return output batch object
  def executeSocialTask(self, inputBatch):
    # variable for result
    ret = inputBatch
    tempFiles = self.__createTemporaryFiles()
    self.logger.debug("!!! tempFiles: %s", str(tempFiles))
    try:
      if self.cmd is None or self.cmd == "":
        raise Exception(self.ERROR_MSG_EXECUTION_CMD_EMPTY)

      self.__makeInputFile(tempFiles, inputBatch)

      self.logger.debug("!!! template cmd: %s", str(self.cmd))
      cmd = self.__makeCmdLine(tempFiles, self.cmd)
      self.logger.debug("!!! execute cmd: %s", str(cmd))

      output, exitCode = self.executeCommand(cmd)
      self.logger.debug("!!! output: %s", str(output))

      if int(exitCode) == 0:
        ret = self.__readOutputFile(tempFiles)

    except Exception, err:
      self.logger.error(str(err))
    finally:
      self.__removeTemporaryFiles(tempFiles)

    return ret
