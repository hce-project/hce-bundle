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
import ppath
from ppath import sys

# For profiling
import app.Profiler as Profiler


# Start profiling
pr = Profiler.Profiler()
if pr and pr.status > 0:
  pr.start()


from dc_db.DBTask import DBTask
import dc_db.DBTask
import os

from app.Consts import EXIT_SUCCESS
from app.Consts import EXIT_FAILURE
import app.Consts as APP_CONSTS


app = None
exit_code = EXIT_SUCCESS

try:
  # create the app
  app = DBTask()
  # setup the application
  app.setup()
  # add support command line arguments
  app.args.add_argument("-c", "--config", action="store", required=True)

  # run the application
  app.run()

  exit_code = app.errorCode

  # log message about profiler
  if pr.errorMsg and dc_db.DBTask.logger:
    dc_db.DBTask.logger.error(pr.errorMsg)

except Exception as err:
  if dc_db.DBTask.logger:
    dc_db.DBTask.logger.error(str(err))
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

#-------------------------------------------------------------