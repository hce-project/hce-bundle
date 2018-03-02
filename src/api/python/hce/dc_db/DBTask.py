#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file db-task.py
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

try:
  import cPickle as pickle
except ImportError:
  import pickle

import os
import sys
import ConfigParser
import logging.config
import MySQLdb
from cement.core import foundation
#import dc.EventObjects as dc_event
#from dc.Constants import DRCESyncTasksCover
import dc_db.Constants as Constants
from dc_db.TasksManager import TasksManager
#from dc_db.Constants import LOGGER_NAME  # pylint: disable=F0401

import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from app.Utils import ExceptionLog
from app.Exceptions import DatabaseException


#logger = logging.getLogger(LOGGER_NAME)


def exceptionLogging(abortStr):
  sys.stderr.write(abortStr)


class DBTask(foundation.CementApp):


  class Meta(object):
    label = Constants.APP_NAME
    def __init__(self):
      pass


  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.errorCode = Constants.EXIT_CODE_OK
    self.errorStr = ""


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

    if self.pargs.config is not None:
      try:
        drceSyncTasksCoverPickled = sys.stdin.read()

        if not os.path.isfile(self.pargs.config):
          raise Exception('Config file %s not found' % self.pargs.config)
        cfgParser = ConfigParser.ConfigParser()
        cfgParser.read(self.pargs.config)

        # init loggers
        logging.config.fileConfig(cfgParser.get("TasksManager", "log_cfg"))

        # Logger initialization
        logger = Utils.MPLogger().getLogger()
        #logger.debug("Receved object:\n" + str(drceSyncTasksCoverPickled) + "\n")

        dbTask = TasksManager(cfgParser)

        ##drceSyncTasksCoverPickled = sys.stdin.read()
        if len(drceSyncTasksCoverPickled) == 0 or drceSyncTasksCoverPickled[-1] != '\x2E':
          drceSyncTasksCoverPickled += '\x2E'

        drceSyncTasksCover = pickle.loads(drceSyncTasksCoverPickled)
        responseDRCESyncTasksCover = dbTask.process(drceSyncTasksCover)
        sys.stdout.write(pickle.dumps(responseDRCESyncTasksCover))
        sys.stdout.flush()

        if dbTask.SQLErrorCode != Constants.EXIT_CODE_OK:
          logger.error("Exited with dbTask.SQLErrorCode=" + str(dbTask.SQLErrorCode))
          #sys.stderr.write("Exited with dbTask.SQLErrorCode=" + str(dbTask.SQLErrorCode) + "\n" +
          #                 "dbTask.SQLErrorMessage=\"" + dbTask.SQLErrorString + "\"\n")


          # log message about profiler
          logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)
          # stop profiling
          self.errorCode = dbTask.SQLErrorCode
          raise DatabaseException(dbTask.SQLErrorString)
          ##return
        else:
          # log message about profiler
          logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)
      except MySQLdb.OperationalError as err:  # pylint: disable=E1101
        ExceptionLog.handler(logger, err, "Aborted cause exception! MySQLdb.OperationalError:")
        exceptionLogging("Aborted cause exception! MySQLdb.OperationalError {%s}\n" % str(err))
        self.errorCode = Constants.EXIT_CODE_GLOBAL_ERROR
      except MySQLdb.Error as err:  # pylint: disable=E1101
        ExceptionLog.handler(logger, err, "Aborted cause exception! Error %d: %s" % (err.args[0], err.args[1]))
        exceptionLogging("Aborted cause exception! Error %d: %s" % (err.args[0], err.args[1]))
        self.errorCode = Constants.EXIT_CODE_GLOBAL_ERROR
      except DatabaseException, err:
        ExceptionLog.handler(logger, err, "Aborted cause exception! ")
        exceptionLogging("Aborted cause exception! {%s}\n" % str(err))
        self.errorCode = Constants.EXIT_CODE_MYSQL_ERROR
      except Exception as err:
        ExceptionLog.handler(logger, err, "Aborted cause exception! ")
        exceptionLogging("Aborted cause exception! {%s}\n" % str(err))
        self.errorCode = Constants.EXIT_CODE_GLOBAL_ERROR
      except:  # pylint: disable=W0702
        ExceptionLog.handler(logger, None, "Unknown exception")
        # log message about profiler
        logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)
        # stop profiling
        sys.stdout.flush()
        self.errorCode = APP_CONSTS.EXIT_FAILURE
        return
    else:
      logger.error("Invalid command line arguments. To help - python ./db_task.py -h")
      sys.stderr.write("Invalid command line arguments. To help - python ./db_task.py -h")

      # log message about profiler
      logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)
      # stop profiling
      sys.stdout.flush()
      self.errorCode = Constants.EXIT_CODE_CONFIG_ERROR


  # #close
  # close application
  def close(self, code=None):  # pylint: disable=W0221,W0613
    sys.stdout.flush()
    self.errorCode = Constants.EXIT_CODE_OK
    foundation.CementApp.close(self)
