#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file scraper.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import ppath
from ppath import sys

# For profiling
import app.Profiler as Profiler


# Start profiling
pr = Profiler.Profiler()
if pr and pr.status > 0:
  pr.start()


import pickle
import os
import sys
from dc_processor.Scraper import Scraper
from dc_processor.Scraper import EXIT_SUCCESS
from dc_processor.Scraper import EXIT_FAILURE
import app.Consts as APP_CONSTS


# That script create main application


app = None
exit_code = EXIT_SUCCESS

try:
  # create the app
  app = Scraper()
  # setup the application
  app.setup()
  # add support command line arguments
  app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file', required=True)

  # run the application
  app.run()

  exit_code = app.getExitCode()

  # log message about profiler
  if pr.errorMsg and app.logger:
    app.logger.error(pr.errorMsg)

except Exception as err:
  sys.stderr.write(str(err) + '\n')
  exit_code = EXIT_FAILURE
except:
  exit_code = EXIT_FAILURE
finally:
  # stop profiling
  if pr:
    pr.stop()
  # close the app
  if app:
    app.close()

  sys.stdout.flush()
  os._exit(exit_code)
