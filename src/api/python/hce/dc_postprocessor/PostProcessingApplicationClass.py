# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Base template class from cement application for easy implementation derived classes.

@package: dc_postprocessor
@file PostProcessingApplicationClass.py
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

import sys
import logging.config
import ConfigParser
from cement.core import foundation

import app.Utils as Utils
import app.Consts as APP_CONSTS

POST_PROCESSING_APPLICATION_NAME = 'PostProcessingApplicationClass'

# This object is a run at once application
class PostProcessingApplicationClass(foundation.CementApp):
  # # Constants error messages
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."
  MSG_ERROR_MISSED_SECTION = "Missed mandatory section '%s'"

  # # Constants debug messages
  MSG_DEBUG_INPUT_PICKLE = "Input pickle: "
  MSG_DEBUG_INPUT_BATCH = "Input batch: "
  MSG_DEBUG_OUTPUT_BATCH = "Output batch: "
  MSG_DEBUG_OUTPUT_PICKLE = "Output pickle: "
  MSG_DEBUG_SEND_PICKLE = "Send pickle. Done."


  # # Constants use in class
  CONFIG_OPTION_LOG = "log"

  # Mandatory
  class Meta(object):
    label = POST_PROCESSING_APPLICATION_NAME
    def __init__(self):
      pass


  # #Constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.logger = None
    self.configParser = None
    self.inputFile = None
    self.batch = None


  # # setup application, necessary recall in derived classes
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)


  # # run application, necessary recall in derived classes
  #
  # @param - None
  # @return - None
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # call initialization application
    self.__initApp()


# #load log config file
  #
  # @return - None
  def __loadLogConfig(self, configName):

    try:
      if not isinstance(configName, str) or len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)

      # call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  # #load application config file
  #
  # @param configName - name of application config file
  # @return - instance of ConfigOptions class
  def __loadAppConfig(self, configName):
    # variable for result
    configParser = None
    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if not config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        raise Exception(self.MSG_ERROR_MISSED_SECTION % str(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME))

      # load logger config file and instantiate logger instance
      self.__loadLogConfig(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, self.CONFIG_OPTION_LOG))

      configParser = config
    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return configParser


  # #initialize application from config files
  #
  # @param - None
  # @return - None
  def __initApp(self):
    if self.pargs.config:
      # load app config
      self.configParser = self.__loadAppConfig(self.pargs.config)
      # load input file if necessary
      if self.pargs.inputFile:
        self.inputFile = str(self.pargs.inputFile)
    else:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG)


  # # get input pickle from stdin or input file
  #
  # @param - None
  # @return inputPickle - input pickle object
  def __getInputPickle(self):

    if self.inputFile is None:
      inputPickle = sys.stdin.read()
    else:
      f = open(self.inputFile, 'r')
      inputPickle = f.read()
      f.close()
      # self.logger.debug(self.MSG_DEBUG_INPUT_PICKLE + '\n' + str(inputPickle))

    return inputPickle


  # # unpikle input object
  #
  # @param inputPickle - input pickle object
  def __unpickleInput(self, inputPickle):
    inputBatch = pickle.loads(inputPickle)
    # self.logger.debug(self.MSG_DEBUG_INPUT_BATCH + Utils.varDump(inputBatch))

    return inputBatch


  # # create output pickle object
  #
  # @param outputBatch - output batch
  # @return outputPickle - output pickle object
  def __createOutputPickle(self, outputBatch):
    # self.logger.debug(self.MSG_DEBUG_OUTPUT_BATCH + str(outputBatch))
    outputPickle = pickle.dumps(outputBatch)
    # self.logger.debug(self.MSG_DEBUG_OUTPUT_PICKLE + str(outputPickle))

    return outputPickle


  # # send pickle to stdout
  #
  # @param outputPickle - output pickle object
  # @return - None
  def __sendPickle(self, outputPickle):
    sys.stdout.write(outputPickle)
    # self.logger.debug(self.MSG_DEBUG_SEND_PICKLE)


  # # extracting receive input batch object
  #
  # @param - None
  # @return - None
  def inputBatch(self):
    self.batch = self.__unpickleInput(self.__getInputPickle())


  # # sending result output batch object
  #
  # @param - None
  # @return - None
  def outputBatch(self):
    self.__sendPickle(self.__createOutputPickle(self.batch))


  # # get config option use config parser
  # @param sectionName -section name
  # @param optionName - option name
  # @param defaultValue - default value
  # @return optionValue - option value as is
  def getConfigOption(self, sectionName, optionName, defaultValue=None):
    # variable for result
    ret = defaultValue
    try:
      if self.configParser is not None:
        ret = self.configParser.get(sectionName, optionName)
    except Exception, err:
      raise Exception(str(err))

    return ret
