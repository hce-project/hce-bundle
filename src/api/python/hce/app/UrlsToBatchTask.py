"""
HCE project, Python bindings, Distributed Tasks Manager application.
Converter of the list of the URLs object from the URLFetch request to the Batch object.
Used for the processing batching as part of the regular processing on DC service.

@package: dc
@file UrlsToBatchTask.py
@author Oleksii, bgv <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import sys
import logging.config
import ConfigParser
import ctypes
import zlib
import time
try:
  import cPickle as pickle
except ImportError:
  import pickle
from cement.core import foundation

from transport.IDGenerator import IDGenerator
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
import dc.EventObjects as dc_event
from app.Utils import varDump
from app.Utils import getHash
import app.Utils as Utils
import app.Consts as APP_CONSTS



# # UrlsToBatchTask Class content main functional for convert of the list of the URLs object
# from the URLFetch request to the Batch object, class inherits from foundation.CementApp
#
class UrlsToBatchTask(foundation.CementApp):

  # #Constans as numeric for exit code
  STATUS_EMPTY_BATCH = 2

  # # Constants error messages used in class
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."

  MSG_ERROR_EXIT_STATUS = "Execution"
  MSG_DEBUG_INPUT_PICKLE = "Input pickle: "
  MSG_DEBUG_INPUT_UNPICKLE = "Input unpickle: "
  MSG_DEBUG_LEN_URL_LIST = "Input url list count: "
  MSG_DEBUG_INPUT_URL_LIST = "Append url: "
  MSG_DEBUG_UNIQ_URL_LIST = "Append uniq url: "
  MSG_DEBUG_OUTPUT_BATCH_ITEM = "Output batch item: "
  MSG_DEBUG_OUTPUT_BATCH = "Output batch: "
  MSG_DEBUG_OUTPUT_PICKLE = "Output pickle: "
  MSG_DEBUG_SEND_PICKLE = "Send pickle. Done."
  MSG_ERROR_UNKNOWN_EXCEPTION = "Unknown exception!"
  MSG_DEBUG_EMPTY_BATCH = "Empty Batch, exit code " + str(STATUS_EMPTY_BATCH)

  # #Constans used options from config file
  URLS_TO_BATCH_TASK_OPTION_LOG = "log"


  # Mandatory
  class Meta(object):
    label = APP_CONSTS.URLS_TO_BATCH_TASK_APP_NAME
    def __init__(self):
      pass


  # #constructor
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)

    self.logger = None
    self.exitCode = APP_CONSTS.EXIT_SUCCESS


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
                                         self.URLS_TO_BATCH_TASK_OPTION_LOG))

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



  def getInputPickle(self):
    input_pickle = sys.stdin.read()
    #self.logger.debug(self.MSG_DEBUG_INPUT_PICKLE + '\n' + str(input_pickle))

    return input_pickle


  def unpickleInput(self, input_pickle):
    #input_unpickled_obj = pickle.loads(input_pickle).eventObject
    input_unpickled = pickle.loads(input_pickle)
    self.logger.debug('>>> input_unpickled: ' + Utils.varDump(input_unpickled))

    input_unpickled_obj = input_unpickled.eventObject
    self.logger.debug(self.MSG_DEBUG_INPUT_UNPICKLE + '\n' + Utils.varDump(input_unpickled_obj))

    return input_unpickled_obj


  def loadListOfURLs(self, input_unpickled_obj):
    list_of_url_obj = input_unpickled_obj
    self.logger.info(self.MSG_DEBUG_LEN_URL_LIST + str(len(list_of_url_obj)))
    self.logger.debug(self.MSG_DEBUG_INPUT_URL_LIST + varDump(list_of_url_obj))

    return list_of_url_obj


  def getListOfUniqueURLs(self, list_of_url_obj):
    seen = set()
    list_of_uniq_urls = [url_obj for url_obj in list_of_url_obj if url_obj.urlMd5 not in seen and
                         not seen.add(url_obj.urlMd5)]
    self.logger.debug(self.MSG_DEBUG_UNIQ_URL_LIST + Utils.varDump(list_of_uniq_urls))

    return list_of_uniq_urls


  def createBatchId(self):
    idGenerator = IDGenerator()
    #batch_id = ctypes.c_uint32(zlib.crc32(idGenerator.get_connection_uid(), int(time.time()))).value
    batch_id = self.id = getHash(idGenerator.get_connection_uid())

    return batch_id


  def createBatchItems(self, list_of_uniq_urls):
    list_of_batch_items = []
    for url_obj in list_of_uniq_urls:
      url_obj.contentMask = dc_event.URL.CONTENT_STORED_ON_DISK
      site_id = url_obj.siteId
      url_id = url_obj.urlMd5
      batch_item = BatchItem(site_id, url_id, url_obj)
      self.logger.debug(self.MSG_DEBUG_OUTPUT_BATCH_ITEM + Utils.varDump(batch_item))
      list_of_batch_items.append(batch_item)

    return list_of_batch_items


  def createOutputBatch(self, batch_id, list_of_batch_items):
    output_batch = Batch(batch_id, list_of_batch_items)
    self.logger.info("Output batch id: %s, items: %s", str(output_batch.id), str(len(output_batch.items)))
    self.logger.debug(self.MSG_DEBUG_OUTPUT_BATCH + varDump(output_batch))

    return output_batch


  def createOutputPickle(self, output_batch):
    output_pickle = pickle.dumps(output_batch)
    #self.logger.debug(self.MSG_DEBUG_OUTPUT_PICKLE + str(output_pickle))

    return output_pickle


  def sendPickle(self, output_pickle):
    sys.stdout.write(output_pickle)
    self.logger.debug(self.MSG_DEBUG_SEND_PICKLE)


  def process(self):
    try:
      input_pickle = self.getInputPickle()
      input_unpickled_obj = self.unpickleInput(input_pickle)
      list_of_url_obj = self.loadListOfURLs(input_unpickled_obj)
#      list_of_uniq_urls = self.getListOfUniqueURLs(list_of_url_obj)
      list_of_uniq_urls = list_of_url_obj
      batch_id = self.createBatchId()

      self.logger.debug('>>> list_of_uniq_urls: ' + varDump(list_of_uniq_urls))

      list_of_batch_items = self.createBatchItems(list_of_uniq_urls)
      output_batch = self.createOutputBatch(batch_id, list_of_batch_items)
      output_pickle = self.createOutputPickle(output_batch)
      self.sendPickle(output_pickle)

      if len(output_batch.items) == 0:
        self.logger.debug(self.MSG_DEBUG_EMPTY_BATCH)
        self.exitCode = self.STATUS_EMPTY_BATCH

    except Exception:
      self.exitCode = APP_CONSTS.EXIT_FAILURE

