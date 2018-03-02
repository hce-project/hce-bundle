#!/usr/bin/python


'''
HCE project, Python bindings, Distributed Crawler application.
Application level constants and enumerations.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ppath
from ppath import sys

import logging

from dc_processor.Scraper import Scraper  # pylint: disable-all
import app.Consts as APP_CONSTS  # pylint: disable-all


if __name__ == "__main__":
  input_date = sys.stdin.read()
  # input_date = unicode(input_date, errors='replace')
  # input_date = unicode(input_date, errors='ignore')
  input_date = input_date.decode("utf-8")
  scraper = Scraper()
  # print scraper.logger
  logging.config.fileConfig("../ini/scraper_log.ini")
  scraper.logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  # print scraper.logger

  # scraper.setup()
  print scraper.convertPubDateToRFC2822(input_date)
