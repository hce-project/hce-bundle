# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
PostprocessorTask class derived from cement application and has main functional for postprocessing.

@package: dc_postprocessor
@file PostprocessorTask.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import importlib

from dc_postprocessor.PostProcessingApplicationClass import PostProcessingApplicationClass
import app.Consts as APP_CONSTS


# This object is a run at once application
class PostprocessorTask(PostProcessingApplicationClass):

  # Constants used in class
  CONFIG_OPTION_MODULES_IMPORT = 'modulesImport'
  CONFIG_OPTION_MODULES_ORDER = 'modulesOrder'

  PACKAGE_MAME = 'dc_postprocessor'

  # Constants of error messages
  ERROR_MSG_LOAD_CONFIG_OPTIONS = "Error load config options. Error: %s"
  ERROR_MSG_INSTANTIATE_MODULES = "Error instantiate modules. Error: %s"

  # Constant messages used in class
  MSG_PROCESSING_STARTED = "Postprocessing for batch ID = %s started."
  MSG_PROCESSING_FINISHED = "Postprocessing for batch ID = %s finished."

  # Mandatory
  class Meta(object):
    label = APP_CONSTS.POST_PROCESSOR_APP_NAME
    def __init__(self):
      # print self.label
      pass

  # Default initialization
  def __init__(self):
    PostProcessingApplicationClass.__init__(self)

#     self.logger = None
    self.modules = []
    self.modulesImport = None
    self.modulesOrder = None


  # # intialization application
  #
  # @param - None
  # @return - None
  def init(self):
    self.inputBatch()
    self.loadConfig()
    self.instantiateModules()


  # # setup application
  #
  # @param - None
  # @return - None
  def setup(self):
    PostProcessingApplicationClass.setup(self)


  # # run application
  #
  # @param - None
  # @return - None
  def run(self):
    PostProcessingApplicationClass.run(self)

    self.init()
    self.process()
    self.finalize()
    # finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  # # finalize application
  #
  # @param - None
  # @return - None
  def finalize(self):
    self.outputBatch()


  # # instantiate modules
  #
  # @param - None
  # @return - None
  def instantiateModules(self):
    for m in self.modulesImport:
      try:
        im = importlib.import_module(self.PACKAGE_MAME + '.' + m)
        mi = getattr(im, m)(self.getConfigOption, self.logger)
        mi.init()
        self.modules.append(mi)
      except Exception, err:
        self.logger.error(self.ERROR_MSG_INSTANTIATE_MODULES % str(err))


#   # #load log config file
#   #
#   # @return - None
#   def loadLogConfig(self, configName):
#
#     try:
#       if not isinstance(configName, str) or len(configName) == 0:
#         raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)
#
#       logging.config.fileConfig(configName)
#
#       # call rotation log files and initialization logger
#       self.logger = Utils.MPLogger().getLogger()
#       # self.logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
#
#     except Exception, err:
#       raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  # # load config options
  #
  # @param - None
  # @return - None
  def loadConfig(self):
    try:
#       self.loadLogConfig(self.getConfigOption(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, self.CONFIG_OPTION_LOG))


      self.modulesImport = self.getConfigOption(self.__class__.__name__, self.CONFIG_OPTION_MODULES_IMPORT).split(',')
      self.modulesOrder = self.getConfigOption(self.__class__.__name__, self.CONFIG_OPTION_MODULES_ORDER).split(',')

      self.modulesImport = [moduleName for moduleName in self.modulesImport if moduleName != ""]
      self.modulesOrder = [moduleName for moduleName in self.modulesOrder if moduleName != ""]

      self.logger.debug("self.modulesImport: %s", str(self.modulesImport))
      self.logger.debug("self.modulesOrder: %s", str(self.modulesOrder))

    except Exception, err:
      raise Exception(self.ERROR_MSG_LOAD_CONFIG_OPTIONS % str(err))


  # # main process block
  #
  # @param - None
  # @return - None
  def process(self):

    self.logger.debug(self.MSG_PROCESSING_STARTED, str(self.batch.id))
    # process batch execution
    for moduleName in self.modulesOrder:
      for moduleInstance in self.modules:
        # if isinstance(moduleInstance, moduleName):
        if moduleName in str(type(moduleInstance)):
          self.batch = moduleInstance.processBatch(self.batch)

    # process batch item execution
    for i in xrange(len(self.batch.items)):
      for moduleName in self.modulesOrder:
        for moduleInstance in self.modules:
          # if isinstance(moduleInstance, moduleName):
          if moduleName in str(type(moduleInstance)):
            self.batch.items[i] = moduleInstance.processBatchItem(self.batch.items[i])

    self.logger.debug(self.MSG_PROCESSING_FINISHED, str(self.batch.id))
