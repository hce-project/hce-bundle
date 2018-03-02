"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file DTMD.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import logging
import time
# import sys
import logging.config
import ConfigParser
from cement.core import foundation
from transport.ConnectionBuilderLight import ConnectionBuilderLight

from dtm.TasksExecutor import TasksExecutor  # pylint: disable=W0611
from dtm.ClientInterfaceService import ClientInterfaceService  # pylint: disable=W0611
from dtm.ExecutionEnvironmentManager import ExecutionEnvironmentManager  # pylint: disable=W0611
from app.AdminInterfaceServer import AdminInterfaceServer  # pylint: disable=W0611
from dtm.ResourcesManager import ResourcesManager  # pylint: disable=W0611
from dtm.TasksManager import TasksManager  # pylint: disable=W0611
from dtm.TasksDataManager import TasksDataManager  # pylint: disable=W0611
from dtm.ResourcesStateMonitor import ResourcesStateMonitor  # pylint: disable=W0611
from dtm.Scheduler import Scheduler  # pylint: disable=W0611
from dtm.TasksStateUpdateService import TasksStateUpdateService  # pylint: disable=W0611
import dtm.Constants as DTM_CONSTS
import app.Utils as Utils  # pylint: disable=F0401
from app.Utils import ExceptionLog
from app.Utils import varDump


APP_NAME = "dtmd"
START_APP_LOG_MSG = "Start dtm daemon."
STOP_APP_LOG_MSG = "Stop dtm daemon."
PID_FILE = "../../../run/dtm-daemon.pid"
APP_CONFIG_FILE = "../ini/dtm-daemon.ini"
LOG_CONFIG_FILE = "../ini/dtm-daemon_log.ini"
LOG_MSG_START_APP = "dtm-daemon start"
ERROR_LOAD_LOG_CONFIG_FILE = "Error loading logging config file. Exiting."
ERROR_LOAD_CONFIG = "Error loading config file. Exciting."


class DTMD(foundation.CementApp):

  CREATE_APP_DELAY = 0
  START_APP_DELAY = 0
  JOIN_APP_DELAY = 0


  class Meta(object):
    label = APP_NAME
    def __init__(self):
      pass


  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.logger = None
    self.threadObjs = None


  # #setup
  # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)


  # #run
  # run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # config section
    self.loadConfig()

    # load self.logger config file
    self.loadLogConfigFile()

    # load application sequence
    self.loadStartAppsSequence()

    # create threadObjs
    # strictly ordered sequence caused connection establishment order
    try:
      self.threadObjs = [self.createThreadObj(app_name) for app_name in self.threadObjs]
    except Exception, err:
      self.logger.error("Creation thread objects failed. Error: %s", str(err))
      raise err

    # run apps
    # strictly ordered
    try:
      [self.startThreadObj(app) for app in self.threadObjs]
    except Exception, err:
      self.logger.error("Starting thread objects failed. Error: %s", str(err))
      raise err

    # wait for stop
    # strictly ordered
    try:
      [self.joinThreadObj(app) for app in self.threadObjs]
    except Exception, err:
      self.logger.error("Joing thread objects failed. Error: %s", str(err))
      raise err


  # #createApp
  # create application's pool
  #
  # @param app_name application name which instance will be created
  # @return instance of created application
  def createThreadObj(self, app_name):
    app = None
    try:
      time.sleep(self.CREATE_APP_DELAY)
      self.logger.debug("Try to create instance of: %s", app_name)
      app = (app_name, eval(app_name)(self.config, ConnectionBuilderLight()))  #  pylint: disable=W0123
      app[1].setName(app[0])
      self.logger.debug("Instance of `%s` created!", app_name)
    except Exception as err:
      ExceptionLog.handler(self.logger, err, "Error to create `%s`: %s" % (str(app_name), str(err)), (err))
      raise err
    return app


  # #joinThreadObj
  # join threadObjs
  #
  # @param app_name application name which instance will be stopped
  # @return None
  def joinThreadObj(self, app):
    try:
      time.sleep(self.JOIN_APP_DELAY)
      self.logger.debug("Joing to `%s`", app[0])
      app[1].join()
    except Exception as err:
      ExceptionLog.handler(self.logger, err, "Error joing to `%s`" % str(app[0]), (err))
      raise err


  # #startApp
  # start application's pool
  #
  # @param app - application instance will be started
  def startThreadObj(self, app):
    #self.logger.debug("Input type(app) = %s", str(type(app)))
    try:
      time.sleep(self.START_APP_DELAY)
      self.logger.debug("Try to start `%s`", app[0])
      app[1].setName(app[0])
      app[1].start()
      self.logger.debug("`%s` started!", app[0])
    except Exception as err:
      ExceptionLog.handler(self.logger, err, "Error to start `%s`: %s" % (str(app[0]), str(err)), (err))
      raise err


  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      self.config = ConfigParser.ConfigParser()
      self.config.optionxform = str
      if self.pargs.config:
        self.config.read(self.pargs.config)
        # self.logger.debug("Load config from cli argument: " + self.pargs.config)
      else:
        self.config.read(APP_CONFIG_FILE)
        # self.logger.debug("Load config from default config file: " + APP_CONFIG_FILE)
    except:
      print ERROR_LOAD_CONFIG
      raise


  # #load application's start sequence
  # the sequence is the list of class names separated by commas
  # in "Application" section "instantiateSequence" option
  def loadStartAppsSequence(self):
    self.logger.debug("Load application's start sequence.")
    self.threadObjs = self.config.get("Application", "instantiateSequence").split(",")


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      log_conf_file = self.config.get("Application", "log")
      logging.config.fileConfig(log_conf_file)
      self.logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)
    except:
      print ERROR_LOAD_LOG_CONFIG_FILE
      raise


  # #close
  # close application
  def close(self):
    if self.logger is not None:
      self.logger.debug("dtm daemon is closed")
    # call base class run method
    foundation.CementApp.close(self)
