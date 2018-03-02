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


from dtma.DTMA import DTMA
import dtma.DTMA
import os
import sys
import logging.config

from app.Consts import EXIT_SUCCESS
from app.Consts import EXIT_FAILURE
import app.Consts as APP_CONSTS


# That script create main crawler application


app = None
exit_code = EXIT_SUCCESS

try:
  # create the app
  app = DTMA()

  # setup the application
  app.setup()
  # add support command line arguments
  app.args.add_argument("-c", "--config", action="store", required=True)
  app.args.add_argument("-cmd", "--cmd", action="store", required=True)
  app.args.add_argument("-fields", "--fields", action="store")
  app.args.add_argument("-classes", "--classes", action="store")

  # run the application
  app.run()

  exit_code = app.errorCode

  # log message about profiler
  if pr.errorMsg and dtma.DTMA.logger:
    dtma.DTMA.logger.error(pr.errorMsg)

except Exception as err:
  if dtma.DTMA.logger:
    dtma.DTMA.logger.error(str(err))
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

