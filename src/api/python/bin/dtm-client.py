#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file dtm-client.py
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


from dtmc.DTMC import DTMC
import dtmc.DTMC
import os
import dtmc

from app.Consts import EXIT_SUCCESS
from app.Consts import EXIT_FAILURE
import app.Consts as APP_CONSTS


# That script create main application


app = None
exit_code = EXIT_SUCCESS

try:
  # create the app
  app = DTMC()
  # setup the application
  app.setup()
  # add support command line arguments
  app.args.add_argument("-c", "--config", action="store", required=True)
  app.args.add_argument("-t", "--task", action="store", required=True)
  app.args.add_argument("-f", "--file", action="store", required=True)
  app.args.add_argument("-task_id", "--id", action="store")

  # run the application
  app.run()

  exit_code = app.errorCode

  # log message about profiler
  if pr.errorMsg and dtmc.DTMC.logger:
    dtmc.DTMC.logger.error(pr.errorMsg)

except Exception as err:
  if dtmc.DTMC.logger:
    dtmc.DTMC.logger.error(str(err))
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
