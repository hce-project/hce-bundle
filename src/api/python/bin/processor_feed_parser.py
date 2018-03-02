#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file processor_feed_parser.py
@author Oleksii, bgv <developers.hce@gmail.com>
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


import os
from dc_processor.ProcessorFeedParser import ProcessorFeedParser
import dc_processor.Constants as CONSTS
import app.Consts as APP_CONSTS


# That script create main application


app = None
exit_code = CONSTS.EXIT_SUCCESS

try:
  # create the app
  app = ProcessorFeedParser()
  # setup the application
  app.setup()
  app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='.ini file required',
                        required=True)
  # run the application
  app.run()

  exit_code = app.getExitCode()

  # log message about profiler
  if pr.errorMsg:
    app.logger.error(pr.errorMsg)

except Exception as err:
  sys.stderr.write(str(err))
  exit_code = CONSTS.EXIT_FAILURE
except:
  exit_code = APP_CONSTS.EXIT_FAILURE
finally:
  # stop profiling
  if pr:
    pr.stop()
  # close the app
  if app:
    app.close()

  sys.stdout.flush()
  os._exit(exit_code)
