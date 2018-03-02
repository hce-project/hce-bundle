#!/usr/bin/python

"""
HCE project,  Python bindings, DC service utility
Response extractor utility to extract fields from URL_CONTENT responses.

@package: dc
@file digest.py
@author bgv <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
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
import app.Utils as Utils
import app.Consts as APP_CONSTS

from app.ResponseExtractor import ResponseExtractor


app = None
exit_code = APP_CONSTS.EXIT_FAILURE

if __name__ == "__main__":
  try:
    # create the app
    app = ResponseExtractor()
    # setup the application
    app.setup()
    # run the application
    app.run()
    # get exit code
    exit_code = app.exitCode
    # log message about profiler
    if pr.errorMsg and app.logger is not None:
      app.logger.error(pr.errorMsg)
  except Exception as err:
    sys.stderr.write(str(err) + '\n')
    exit_code = APP_CONSTS.EXIT_FAILURE
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
