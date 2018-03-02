# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Content updater tools main functional.

@package: app
@file ContentUpdater.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

try:
  import cPickle as pickle
except ImportError:
  import pickle

import json
import sys
import logging.config
import ConfigParser
from cement.core import foundation

from dc.EventObjects import Attribute
import dc.EventObjects as dc_event
from app.Utils import varDump
import app.Utils as Utils
import app.Consts as APP_CONSTS
from app.Utils import SQLExpression
from app.Utils import getTracebackInfo
from app.Exceptions import DatabaseException
from dc_crawler.DBTasksWrapper import DBTasksWrapper
import dc_db.Constants as DB_CONSTS


# This object is a run at once application
class ContentUpdater(foundation.CementApp):
  # # Constants error messages used in class
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."
  MSG_ERROR_MISSED_SECTION = "Missed mandatory section '%s'"
  MSG_ERROR_DATABASE_OPERATION = "Database operation has error: %s"
  MSG_ERROR_UPDATE_PROCESSED_CONTENTS = "Update processed contents has error: %s"

  MSG_DEBUG_INPUT_PICKLE = "Input pickle: "
  MSG_DEBUG_INPUT_UNPICKLED = "input unpickled: "
  MSG_DEBUG_OUTPUT_BATCH = "Output batch: "
  MSG_DEBUG_OUTPUT_PICKLE = "Output pickle: "
  MSG_DEBUG_SEND_PICKLE = "Send pickle. Done."

  ATTRIBUTE_ERROR_MESSAGE_NAME = 'errorMessage'

  # Mandatory
  class Meta(object):
    label = APP_CONSTS.CONTENT_UPDATER_APP_NAME
    def __init__(self):
      pass


  # # Internal class for social rate option from config
  class ConfigOptions(object):
    # # Constans used options from config file
    CONTENT_UPDATER_OPTION_LOG = "log"
    CONTENT_UPDATER_OPTION_DB_TASK_INI = "db_task_ini"

    def __init__(self, confLogFileName=None, dbTaskIniFile=None):
      self.confLogFileName = confLogFileName
      self.dbTaskIniFile = dbTaskIniFile


  # # Initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.logger = None
    self.dbWrapper = None
    self.errorMsg = None


  # # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)


  # # run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # call initialization application
    self.__initApp()

    # call internal processing
    self.process()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # #initialize application from config files
  #
  # @param - None
  # @return - None
  def __initApp(self):
    if self.pargs.config:
      # load app config
      configOptions = self.__loadAppConfig(self.pargs.config)

      # load log config
      self.__loadLogConfig(configOptions.confLogFileName)

      # set attribute values of application
      self.dbWrapper = self.__createDBTasksWrapper(configOptions.dbTaskIniFile)

    else:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG)

    if self.pargs.error:
      self.errorMsg = str(self.pargs.error)


  # #load application config file
  #
  # @param configName - name of application config file
  # @return - instance of ConfigOptions class
  def __loadAppConfig(self, configName):
    # variable for result
    configOptions = None
    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if not config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        raise Exception(self.MSG_ERROR_MISSED_SECTION % str(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME))

      configOptions = ContentUpdater.ConfigOptions(
          str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                         ContentUpdater.ConfigOptions.CONTENT_UPDATER_OPTION_LOG)),
          str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                         ContentUpdater.ConfigOptions.CONTENT_UPDATER_OPTION_DB_TASK_INI)))

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return configOptions


  # #load log config file
  #
  # @param configName - name of log rtc-finalizer config file
  # @return - None
  def __loadLogConfig(self, configName):
    try:
      if isinstance(configName, str) and len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)

      # call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  # # create dbtask wrapper instance
  #
  # @param configName - dbtask ini file
  # @return instance of DBTasksWrapper class
  def __createDBTasksWrapper(self, configName):
    # variable for result
    dbTasksWrapper = None
    try:
      if configName == "":
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      dbTasksWrapper = DBTasksWrapper(config)

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return dbTasksWrapper


  # # get input pickle from stdin
  #
  # @param - None
  # @return inputPickle - input pickle object
  def getInputPickle(self):
    inputPickle = sys.stdin.read()
    # self.logger.debug(self.MSG_DEBUG_INPUT_PICKLE + '\n' + str(inputPickle))

    return inputPickle


  # # unpikle input object
  #
  # @param inputPickle - input pickle object
  def unpickleInput(self, inputPickle):
    inputUnpickled = pickle.loads(inputPickle)
    # self.logger.debug(self.MSG_DEBUG_INPUT_UNPICKLED + varDump(inputUnpickled))

    return inputUnpickled


  # # create output pickle object
  #
  # @param outputBatch - output batch
  # @return outputPickle - output pickle object
  def createOutputPickle(self, outputBatch):
    # self.logger.debug(self.MSG_DEBUG_OUTPUT_BATCH + varDump(outputBatch))
    outputPickle = pickle.dumps(outputBatch)
    # self.logger.debug(self.MSG_DEBUG_OUTPUT_PICKLE + str(outputPickle))

    return outputPickle


  # # send pickle
  #
  # @param outputPickle - output pickle object
  # @return - None
  def sendPickle(self, outputPickle):
    sys.stdout.write(outputPickle)
    self.logger.debug(self.MSG_DEBUG_SEND_PICKLE)


  # # main process handler
  #
  # @param - None
  # @return None
  def process(self):
    try:
      inputBatchObj = self.unpickleInput(self.getInputPickle())

      if self.errorMsg is None:
        self.updateProcessedContents(inputBatchObj)
      else:
        self.updateAttributesOnly(inputBatchObj)

      self.sendPickle(self.createOutputPickle(inputBatchObj))
    except Exception, err:
      self.logger.error(str(err))
      self.exitCode = APP_CONSTS.EXIT_FAILURE


  # # update processed contents
  #
  # @param inputBatch - input batch
  # @return - None
  def updateProcessedContents(self, inputBatch):

    urlPuts = []
    attributes = []
    urlUpdateList = []

    self.logger.debug("The processing of batch Id = %s started", str(inputBatch.id))

    for batchItem in inputBatch.items:
      self.logger.debug("batchItem.siteId: %s", str(batchItem.siteId))
      self.logger.debug("batchItem.urlId: %s", str(batchItem.urlId))
#       self.logger.debug("batchItem.urlObj: %s", varDump(batchItem.urlObj, stringifyType=0))
#       self.logger.debug("batchItem.urlContentResponse: %s", varDump(batchItem.urlContentResponse))
      self.logger.debug("batchItem.urlObj.crawlingTime = %s", str(batchItem.urlObj.crawlingTime))
      self.logger.debug("batchItem.urlObj.processingTime = %s", str(batchItem.urlObj.processingTime))
      self.logger.debug("batchItem.urlObj.totalTime = %s", str(batchItem.urlObj.totalTime))

      if batchItem.urlContentResponse is not None:
        for processedContent in batchItem.urlContentResponse.processedContents:

          self.logger.debug("!!! processedContent: %s", varDump(processedContent, stringifyType=0))
          try:
            # create URLPut object
            putDict = {}
            putDict["id"] = batchItem.urlId
            putDict["data"] = processedContent
            putDict["cDate"] = SQLExpression("NOW()")

            urlPut = dc_event.URLPut(batchItem.siteId,
                                     batchItem.urlId,
                                     dc_event.Content.CONTENT_PROCESSOR_CONTENT,
                                     putDict)

            # accumulate URLPut objects
            urlPuts.append(urlPut)

          except Exception, err:
            self.logger.error(self.MSG_ERROR_UPDATE_PROCESSED_CONTENTS, str(err))
            self.logger.debug(getTracebackInfo())

        try:
#           self.logger.debug("type: %s, batchItem.urlContentResponse.attributes: %s",
#                             str(type(batchItem.urlContentResponse.attributes)),
#                             varDump(batchItem.urlContentResponse.attributes,
#                                     maxDepth=15))


          # accumulate attributes
          for attrJson in batchItem.urlContentResponse.attributes:
            attrDict = json.loads(attrJson)

#             self.logger.debug("type: %s, attrDict: %s", str(type(attrDict)), str(attrDict))

            attrValue = json.dumps(attrDict['value'], ensure_ascii=False, encoding='utf-8')

            attribute = Attribute(siteId=attrDict['siteId'],
                                  name=attrDict['name'],
                                  urlMd5=attrDict['urlMd5'],
                                  value=attrValue)

            attributes.append(attribute)

          if len(attributes) > 0:
            self.logger.debug("Made attributes: %s", varDump(attributes))

        except Exception, err:
          self.logger.error("Make attributes error: %s", str(err))
          self.logger.debug(getTracebackInfo())

        # update total time for batch item
        try:
          urlUpdateObj = dc_event.URLUpdate(batchItem.siteId, batchItem.urlId, dc_event.URLStatus.URL_TYPE_MD5)
          urlUpdateObj.totalTime = batchItem.urlObj.totalTime
          urlUpdateList.append(urlUpdateObj)

        except Exception, err:
          self.logger.error("Make url update object error: %s", str(err))
          self.logger.debug(getTracebackInfo())

    try:
      # execute database operations
      affectDB = self.dbWrapper.affect_db
      self.dbWrapper.affect_db = True
      self.dbWrapper.putURLContent(urlPuts)
      self.dbWrapper.putAttributes(attributes)
      self.dbWrapper.urlUpdate(urlUpdateList)
      self.dbWrapper.affect_db = affectDB

      self.logger.debug('Database operations executed...')

    except DatabaseException, err:
      self.logger.error(self.MSG_ERROR_DATABASE_OPERATION, str(err))
      self.logger.debug(getTracebackInfo())
    except Exception, err:
      self.logger.error(self.MSG_ERROR_DATABASE_OPERATION, str(err))
      self.logger.debug(getTracebackInfo())

    self.logger.debug("The processing of batch Id = %s finished", str(inputBatch.id))


  # # update attributes by error message
  #
  # @param inputBatch - input batch
  # @return - None
  def updateAttributesOnly(self, inputBatch):
    attributes = []

    for batchItem in inputBatch.items:
      self.logger.debug("batchItem: %s", varDump(batchItem))
      self.logger.debug("batchItem.urlContentResponse: %s", varDump(batchItem.urlContentResponse))

      try:
        # accumulate attributes
        attributes.append(Attribute(siteId=batchItem.siteId,
                                    name=self.ATTRIBUTE_ERROR_MESSAGE_NAME,
                                    urlMd5=batchItem.urlId,
                                    value=self.dbWrapper.dbTask.dbConnections[DB_CONSTS.PRIMARY_DB_ID].\
                                      escape_string(str(self.errorMsg))))

        self.logger.debug("Made attributes: %s", varDump(attributes))
      except Exception, err:
        self.logger.error("Make attributes error: %s", str(err))
        self.logger.debug(getTracebackInfo())

    try:
      # execute database operations
      affectDB = self.dbWrapper.affect_db
      self.dbWrapper.affect_db = True
      self.dbWrapper.putAttributes(attributes)
      self.dbWrapper.affect_db = affectDB

      self.logger.debug('Database operations executed...')

    except DatabaseException, err:
      self.logger.error(self.MSG_ERROR_DATABASE_OPERATION, str(err))
      self.logger.debug(getTracebackInfo())
