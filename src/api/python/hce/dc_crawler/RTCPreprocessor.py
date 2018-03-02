"""
HCE project,  Python bindings, Distributed Tasks Manager application.
RTCPreprocessor Class content main functional for preprocessor for realtime crawling.

@package: dc_crawler
@file RTCPreprocessor.py
@author Alex <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import sys
import os
import pickle
import logging.config
import ConfigParser

import argparse

from app.Utils import varDump
import app.Utils as Utils
import app.Consts as APP_CONSTS
import dc_crawler.Constants as DC_CRAWLER_CONSTS
from cement.core import foundation

APP_NAME = "RTCPreprocessor"

## RTCPreprocessor Class content main functional for preprocessor for realtime crawling,
# class inherits from foundation.CementApp
#
class RTCPreprocessor(foundation.CementApp):

  ## Constants error messages used in class
  MSG_ERROR_PARSE_CMD_PARAMS = "Error parse command line parameters."
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."

  ##Constans used in class
  DRCE_NODE_NUMBER = "DRCE_NODE_NUMBER"
  DRCE_NODES_TOTAL = "DRCE_NODES_TOTAL"

  ##Constans as numeric for exit code
  ERROR_EMPTY_ENV_VARS = 2

  ##Constans used options from config file
  PREPROCESSOR_OPTION_LOG = "log"

  # Mandatory
  class Meta(object):
    label = DC_CRAWLER_CONSTS.RTC_PREPROCESSOR_APP_NAME
    def __init__(self):
      pass

  ##constructor
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)

    self.logger = None
    self.batch = None
    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.pickled_object = None
    self.envVars = {self.DRCE_NODES_TOTAL: 1,
                    self.DRCE_NODE_NUMBER: 1}


  ## setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)


  ## run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # call initialization application
    self.__initApp()

    # call internal processing
    self.process()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  ##initialize application from config files
  #
  #@param - None
  #@return - None
  def __initApp(self):
    if self.pargs.config:
      self.__loadLogConfig(self.__loadAppConfig(self.pargs.config))
    else:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG)


  ##load application config file
  #
  #@param configName - name of application config file
  #@return - log config file name
  def __loadAppConfig(self, configName):
    #variable for result
    confLogFileName = ""

    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        confLogFileName = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, self.PREPROCESSOR_OPTION_LOG))

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return confLogFileName


  ##load log config file
  #
  #@param configName - name of log rtc-finalizer config file
  #@return - None
  def __loadLogConfig(self, configName):
    try:
      if isinstance(configName, str) and len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)

      #call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  def getBatchFromInput(self):
    self.pickled_object = sys.stdin.read()


  def cutBatch(self):
    self.batch = (pickle.loads(self.pickled_object))
    self.logger.info("Before id:%s items: %s", str(self.batch.id), str(len(self.batch.items)))
    self.logger.debug("self.batch: %s", varDump(self.batch))
    items = self.batch.items
    if len(items) > 1:
      splitted_items = self.split(self.batch.items, int(self.envVars[self.DRCE_NODES_TOTAL]))
      self.logger.debug("Input items: %s", str(self.batch.items))
      self.logger.debug("Splitted items: %s", str(splitted_items))
      self.batch.items = splitted_items[int(self.envVars[self.DRCE_NODE_NUMBER]) - 1]
      self.logger.debug("Output items: %s", str(self.batch.items))
    self.logger.debug("Output batch: %s", varDump(self.batch))
    self.pickled_object = pickle.dumps(self.batch)

    self.logger.info("After id:%s items: %s", str(self.batch.id), str(len(self.batch.items)))

  def split(self, arr, count):
    return [arr[i::count] for i in range(count)]


  def sendBatch(self):
    print self.pickled_object
    sys.stdout.flush()


  def getEnvVars(self):
    for key in self.envVars.keys():
      if key in os.environ and os.environ[key] != "":
        self.envVars[key] = os.environ[key]
        self.logger.debug("os.environ[%s]: set to <<%s>>" % (key, self.envVars[key]))
      else:
        self.logger.debug("os.environ[%s]: not set. Use default value: <<%s>>" % (key, self.envVars[key]))
        self.exitCode = self.ERROR_EMPTY_ENV_VARS


  def process(self):
    try:
      self.getBatchFromInput()
      self.getEnvVars()
      if self.exitCode != self.ERROR_EMPTY_ENV_VARS:
        self.logger.info("The batch possible will be reduced")
        self.cutBatch()
      else:
        self.logger.info("The batch will not be reduced")
      self.sendBatch()
    except Exception:
      self.exitCode = APP_CONSTS.EXIT_FAILURE

