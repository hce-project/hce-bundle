#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging
from cement.core import foundation

from dc_postprocessor.PostProcessingApplicationClass import PostProcessingApplicationClass
from app.Utils import varDump
import app.Consts as APP_CONSTS


def getLogger():
  # create logger
  logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  logger.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(ch)

  return logger


class TestApplication(PostProcessingApplicationClass):

  # Mandatory
  class Meta(object):
    label = 'TestApplication'
    def __init__(self):
      pass

  def __init__(self, logger=None):
    PostProcessingApplicationClass.__init__(self, logger)


  def setup(self):
    PostProcessingApplicationClass.setup(self)


  def run(self):
    PostProcessingApplicationClass.run(self)
    self.init()
    self.process()
    self.finalize()
    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  def init(self):
    self.loadConfig()
    self.inputBatch()


  def process(self):
    pass


  def loadConfig(self):
    pass


  def finalize(self):
    self.outputBatch()

if __name__ == '__main__':

  logger = getLogger()
  app = None
  try:
    # create the app
    app = TestApplication(logger)
    # setup the application
    app.setup()
    # add support command line arguments
    app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file',
                          required=False)
    app.args.add_argument('-i', '--inputFile', action='store', metavar='input_pickle_file', help='input pickle file',
                          required=False)

    # run the application
    app.run()

    # get exit code
    exit_code = app.exitCode

  except Exception, err:
    logger.error("Exception: %s", str(err))
    exit_code = APP_CONSTS.EXIT_FAILURE
  except:
    logger.error('Unknown exception')
    exit_code = APP_CONSTS.EXIT_FAILURE

  logger.debug("exit_code = %s", str(exit_code))

