'''
Implementation class HCEProfiler for python bindings to HCE cluster node.

@package: hce
@file Profiler.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import sys
import cProfile
import pstats
import StringIO
import ConfigParser
import logging.config
import argparse

import app.Consts as APP_CONSTS
import app.Utils as Utils
# For traceback
from app.Utils import tracefunc

# List of strings to be appended in to the final message for profiler records
messagesList = []


## Class which provides functionality for use profiling
class Profiler(object):

  ## Constants error messages used in class
  MSG_ERROR_PARSE_CMD_PARAMS = "Error parse command line parameters."
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."
  MSG_ERROR_WRONG_CONFIG_OPTION = "Wrong format option"
  MSG_ERROR_WRONG__OPTION_SORTBY = "Read wrong value of 'sortby' from config"

  ##Constans profiler options read from config
  PROFILER_OPTION_LOG = "log"
  PROFILER_OPTION_STATUS = "profile"
  PROFILER_OPTION_SORTBY = "sortby"
  PROFILER_OPTION_LIMIT = "limit"
  PROFILER_OPTION_TRACEBACK = "traceback"
  PROFILER_OPTION_TRACEBACK_LOGGER_MODE = "tracebackLoggerMode"

  ##Constans default values of profiler options
  PROFILER_OPTION_STATUS_DEFAULT = 0
  PROFILER_OPTION_SORTBY_DEFAULT = "cumulative"
  PROFILER_OPTION_LIMIT_DEFAULT = 1.0
  PROFILER_OPTION_TRACEBACK_DEFAULT = 0
  PROFILER_OPTION_TRACEBACK_LOGGER_MODE_DEFAULT = 1

  ##Constans allowed values of 'sortby'
  PROFILER_OPTION_SORTBY_ALLOWED_LIST = ['stdname', 'calls', 'time', 'cumulative']

  ##Constans for global message list of strings in the final message for profiler records
  MESSAGES_ITEMS_DELIMITER = ","

  ##Constans traceback config options (key - options name, value - default
  tracebackOptions = {'tracebackIdent':Utils.tracebackIdent,
                      'tracebackIdentFiller':Utils.tracebackIdentFiller,
                      'tracebackMessageCall':Utils.tracebackMessageCall,
                      'tracebackMessageExit':Utils.tracebackMessageExit,
                      'tracebackmessageDelimiter':Utils.tracebackmessageDelimiter,
                      'tracebackTimeMark':Utils.tracebackTimeMark,
                      'tracebackTimeMarkFormat':Utils.tracebackTimeMarkFormat,
                      'tracebackTimeMarkDelimiter':Utils.tracebackTimeMarkDelimiter,
                      'tracebackIncludeInternalCalls':Utils.tracebackIncludeInternalCalls,
                      'tracebackIncludeLineNumber':Utils.tracebackIncludeLineNumber,
                      'tracebackIncludeLineNumberDelimiter':Utils.tracebackIncludeLineNumberDelimiter,
                      'tracebackIncludeFileNumber':Utils.tracebackIncludeFileNumber,
                      'tracebackIncludeFileNumberDelimiter':Utils.tracebackIncludeFileNumberDelimiter,
                      'tracebackFunctionNameDelimiter':Utils.tracebackFunctionNameDelimiter,
                      'tracebackExcludeModulePath':Utils.tracebackExcludeModulePath,
                      'tracebackExcludeFunctionName':Utils.tracebackExcludeFunctionName,
                      'tracebackExcludeFunctionNameStarts':Utils.tracebackExcludeFunctionNameStarts,
                      'tracebackIncludeExitCalls':Utils.tracebackIncludeExitCalls,
                      'tracebackRecursionlimit':Utils.tracebackRecursionlimit,
                      'tracebackRecursionlimitErrorMsg':Utils.tracebackRecursionlimitErrorMsg,
                      'tracebackIncludeLocals':Utils.tracebackIncludeLocals,
                      'tracebackIncludeArg':Utils.tracebackIncludeArg,
                      'tracebackIncludeLocalsPrefix':Utils.tracebackIncludeLocalsPrefix,
                      'tracebackIncludeArgPrefix':Utils.tracebackIncludeArgPrefix,
                      'tracebackElapsedTimeDelimiter':Utils.tracebackElapsedTimeDelimiter,
                      'tracebackElapsedTimeFormat':Utils.tracebackElapsedTimeFormat,
                      'tracebackUnknownExceptionMsg':Utils.tracebackUnknownExceptionMsg}

  ##constructor
  def __init__(self):
    '''
    Constructor
    '''
    self.parser = None
    self.logger = None
    self.isStarted = False
    self.status = self.PROFILER_OPTION_STATUS_DEFAULT
    self.sortby = self.PROFILER_OPTION_SORTBY_DEFAULT
    self.limit = self.PROFILER_OPTION_LIMIT_DEFAULT
    self.traceback = self.PROFILER_OPTION_TRACEBACK_DEFAULT
    self.tracebackLoggerMode = self.PROFILER_OPTION_TRACEBACK_LOGGER_MODE_DEFAULT
    self.errorMsg = ""
    #create instance of profiler
    self.pr = cProfile.Profile()
    try:
      #load configuration files and initialization
      self.__loadAppConfig(self.__parseParams())
    except Exception, err:
      self.errorMsg = str(err)
      self.status = self.PROFILER_OPTION_STATUS_DEFAULT

    if self.traceback > 0:
      #used self.tracebackLoggerMode already reinit from config
      if self.tracebackLoggerMode > 0 and Utils.tracebackLogger is None:
        Utils.tracebackLogger = Utils.MPLogger().getLogger(APP_CONSTS.LOGGER_NAME_TRACEBACK)

      sys.settrace(tracefunc)


  ##initialize traceback options from config file
  #
  #@param config - config parser
  #@param section - section name
  #@return - None
  def __initTrackbackOptions(self, config, section):

    for key, value in self.tracebackOptions.items():
      opt = Utils.getConfigParameter(config, section, key, value)

      if opt and opt != value:
        try:
          exec('Utils.' + str(key) + '=' + str(opt))  # pylint: disable=W0122
        except Exception:
          raise Exception(self.MSG_ERROR_WRONG_CONFIG_OPTION + ': ' + str(key))


  ##load application config file
  #
  #@param configName - name of application config file
  #@return - profiler config file name
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
        confLogFileName = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, self.PROFILER_OPTION_LOG))

      if config.has_section(APP_CONSTS.CONFIG_PROFILER_SECTION_NAME):
        self.status = int(config.get(APP_CONSTS.CONFIG_PROFILER_SECTION_NAME, self.PROFILER_OPTION_STATUS))
        self.sortby = str(config.get(APP_CONSTS.CONFIG_PROFILER_SECTION_NAME, self.PROFILER_OPTION_SORTBY))
        self.limit = float(config.get(APP_CONSTS.CONFIG_PROFILER_SECTION_NAME, self.PROFILER_OPTION_LIMIT))
        self.traceback = int(config.get(APP_CONSTS.CONFIG_PROFILER_SECTION_NAME, self.PROFILER_OPTION_TRACEBACK))
        if self.traceback > 0:
          self.__initTrackbackOptions(config, APP_CONSTS.CONFIG_PROFILER_SECTION_NAME)
          if config.has_option(APP_CONSTS.CONFIG_PROFILER_SECTION_NAME, self.PROFILER_OPTION_TRACEBACK_LOGGER_MODE):
            self.tracebackLoggerMode = int(Utils.getConfigParameter(config, APP_CONSTS.CONFIG_PROFILER_SECTION_NAME,
                                                                    self.PROFILER_OPTION_TRACEBACK_LOGGER_MODE,
                                                                    self.PROFILER_OPTION_TRACEBACK_LOGGER_MODE_DEFAULT))
          else:
            pass
        else:
          pass

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    if self.sortby not in self.PROFILER_OPTION_SORTBY_ALLOWED_LIST:
      raise Exception(self.MSG_ERROR_WRONG__OPTION_SORTBY)

    return confLogFileName


  ##load log config file of prifiler
  #
  #@param configName - name of log profiler config file
  #@return - None
  def readConfig(self, configName):
    try:
      if isinstance(configName, str) and len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)
      #call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  ##parsing paramers
  #
  #@return - configName read from command line argument
  def __parseParams(self):
    configName = ""
    try:
      self.parser = argparse.ArgumentParser(description='Process command line arguments.', add_help=False)
      self.parser.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file')

      args = self.parser.parse_known_args()

      if args is None or args[0] is None or args[0].config is None:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      configName = str(args[0].config)

    except Exception, err:
      raise Exception(self.MSG_ERROR_PARSE_CMD_PARAMS + ' ' + str(err))

    return configName


  ##start profiling
  #
  #@return - None
  def start(self):
    if self.isStarted is False:
      self.pr.enable()
      self.isStarted = True


  ##stop profiling
  #
  #@return - None
  def stop(self):
    msgStr = self.MESSAGES_ITEMS_DELIMITER.join(messagesList)

    if self.isStarted is True and self.status > 0:
      self.isStarted = False
      self.pr.disable()
      s = StringIO.StringIO()
      ps = pstats.Stats(self.pr, stream=s).sort_stats(self.sortby)
      ps.print_stats(self.limit)

      #call rotation log files
      self.logger = Utils.MPLogger().getLogger(APP_CONSTS.LOGGER_NAME_PROFILER)
      #dump profile information to log
      if self.logger:
        self.logger.debug("%s\n%s", msgStr, str(s.getvalue()))
        self.logger.debug("%s", APP_CONSTS.LOGGER_DELIMITER_LINE)

    if self.traceback > 0:
      if Utils.tracebackLogger is None:
        #call rotation log files
        self.logger = Utils.MPLogger().getLogger(APP_CONSTS.LOGGER_NAME_TRACEBACK)
        #dump traceback information to log
        if self.logger:
          self.logger.debug("%s\n%s", msgStr, "\n".join(Utils.tracebackList))
          self.logger.debug("%s", APP_CONSTS.LOGGER_DELIMITER_LINE)

