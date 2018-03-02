"""
HCE project, Python bindings, Distributed Tasks Manager application.
Converter of the list of the URLs object from the URLFetch request to the DBTask.

@package: app
@file URLFetchToJsonDBTaskConvertor.py
@author Oleksii <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import sys
import logging.config
import ConfigParser
import json
from subprocess import Popen
from subprocess import PIPE
try:
  import cPickle as pickle
except ImportError:
  import pickle
from cement.core import foundation

import dc.Constants as DC_CONSTS
from dcc.DCCObjectsSerializator import DCCObjectsSerializator
from app.Utils import varDump
import app.Utils as Utils
import app.Consts as APP_CONSTS


# # URLFetchToJsonDBTaskConvertor Class content main functional for convert of the list of the URLs object
# from the URLFetch request to the DBTask, class inherits from foundation.CementApp
#
class UrlFetchToJsonDBTaskConvertor(foundation.CementApp):

  # # Constants used in class
  CMD_DEFAULT = "cd ~/hce-node-bundle/api/python/bin && ./db-task.py --c=../ini/db-task.ini"

  # # Constants error messages used in class
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."
  MSG_ERROR_EXIT_STATUS = "Exit failure. "

  MSG_DEBUG_INPUT_PICKLE = "Input pickle: "
  MSG_DEBUG_OUTPUT_PICKLE = "Output pickle: "
  MSG_DEBUG_SEND_PICKLE = "Send pickle. Done."

  MSG_INFO_PROCESSOR_EXIT_CODE = "Scraper exit_code: "
  MSG_INFO_PROCESSOR_OUTPUT = "Scraper output: "
  MSG_INFO_PROCESSOR_ERROR = "Scraper err: "

  # #Constans used options from config file
  URLS_FETCH_JSON_TO_DBTASK_OPTION_LOG = "log"
  URLS_FETCH_JSON_TO_DBTASK_OPTION_CMD = "cmd"


  # Mandatory
  class Meta(object):
    label = APP_CONSTS.URLS_FETCH_JSON_TO_DBTASK_APP_NAME
    def __init__(self):
      pass


  # #constructor
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)

    self.logger = None
    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.cmd = self.CMD_DEFAULT


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
      self.__loadLogConfig(self.__loadAppConfig(self.pargs.config))
    else:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG)


  # #load application config file
  #
  # @param configName - name of application config file
  # @return - log config file name
  def __loadAppConfig(self, configName):
    # variable for result
    confLogFileName = ""

    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        confLogFileName = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                                         self.URLS_FETCH_JSON_TO_DBTASK_OPTION_LOG))
        self.cmd = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                                  self.URLS_FETCH_JSON_TO_DBTASK_OPTION_CMD))

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return confLogFileName


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


  def getURLFetchJson(self):
    inputUrlFetchJson = sys.stdin.read()
    self.logger.debug(self.MSG_DEBUG_INPUT_PICKLE + '\n' + varDump(inputUrlFetchJson))

    return json.loads(inputUrlFetchJson)


  def createOutputPickle(self, inputUrlFetchJson):
    eventType = DC_CONSTS.EVENT_TYPES.URL_FETCH
    convertor = DCCObjectsSerializator()
    eventObj = convertor.URLFetchDeserialize(inputUrlFetchJson)
    self.logger.debug(self.MSG_DEBUG_OUTPUT_PICKLE + '\n' + str(eventObj))
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(eventType, eventObj)
    outputPickle = pickle.dumps(drceSyncTasksCoverObj)
    self.logger.debug(self.MSG_DEBUG_OUTPUT_PICKLE + '\n' + str(outputPickle))

    return outputPickle


  def sendToDbTask(self, outputPickle):
    process = Popen(self.cmd, stdout=PIPE, stdin=PIPE, shell=True, close_fds=True)
    (output, err) = process.communicate(input=outputPickle)
    self.exitCode = process.wait()
    self.logger.info(self.MSG_INFO_PROCESSOR_EXIT_CODE + str(self.exitCode) + '\n' + \
                self.MSG_INFO_PROCESSOR_OUTPUT + str(output) + '\n' + \
                self.MSG_INFO_PROCESSOR_ERROR + str(err) + '\n' + str(pickle.loads(output)))

    return output


  def sendPickle(self, output_pickle):
    sys.stdout.write(output_pickle)
    self.logger.debug(self.MSG_DEBUG_SEND_PICKLE)


  def process(self):

    self.logger.info('self.cmd: ' + str(self.cmd))
    try:
      # chain of necessary calls for processing
      self.sendPickle(self.sendToDbTask(self.createOutputPickle(self.getURLFetchJson())))
    except Exception, err:
      self.logger.error(self.MSG_ERROR_EXIT_STATUS + str(err))
      self.exitCode = APP_CONSTS.EXIT_FAILURE
