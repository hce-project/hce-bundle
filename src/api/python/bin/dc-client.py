#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file dc-client.py
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


from dcc.DCC import DCC
import dcc.DCC
import os
import sys
import logging.config

from app.Consts import EXIT_SUCCESS
from app.Consts import EXIT_FAILURE
import app.Consts as APP_CONSTS
import dcc.Constants as CONSTANTS

# That script create main application


app = None
exit_code = EXIT_SUCCESS

try:
  # create the app
  app = DCC()
  # setup the application
  app.setup()
  # add support command line arguments
  app.args.add_argument("-c", "--config", action="store", metavar='config_file', help='config ini-file', required=True)
  additionHelpStr = CONSTANTS.HELP_COMMAND_TEMPLATE + str(CONSTANTS.TASKS)
  app.args.add_argument("-cmd", "--command", action="store", metavar='command', help=additionHelpStr)
  app.args.add_argument("-f", "--file", action="store", metavar='file name')
  app.args.add_argument("-mrg", "--merge", action="store", metavar='merge')
  app.args.add_argument("-ff", "--fields", action="store", metavar='fields')
  app.args.add_argument("-mode", "--mode", action="store", metavar='mode')
  app.args.add_argument("-v", "--verbose", action="store", metavar='verbose')
  app.args.add_argument("-dcc_timeout", "--dcc_timeout", action="store", metavar='timeout value')
  app.args.add_argument("-dcc_clientHost", "--dcc_clientHost", metavar='client host')
  app.args.add_argument("-dcc_clientPort", "--dcc_clientPort", metavar='client port')
  app.args.add_argument("-o", "--output_file", action="store", metavar='output file name')
  app.args.add_argument("-e", "--error_file", action="store", metavar='error file name')


  # run the application
  app.run()

  exit_code = app.errorCode

  # log message about profiler
  if pr.errorMsg and dcc.DCC.logger:
    dcc.DCC.logger.error(pr.errorMsg)

except Exception as err:
  if dcc.DCC.logger:
    dcc.DCC.logger.error(str(err))
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
