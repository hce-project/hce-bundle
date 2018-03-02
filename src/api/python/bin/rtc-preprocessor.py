#!/usr/bin/python

"""
HCE project,  Python bindings, Distributed Tasks Manager application.
RTCPreprocessor Class content main functional for preprocessor for realtime crawling.

@package: dc
@file RTCPreprocessor.py
@author Oleksii <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
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
import app.Utils as Utils
import app.Consts as APP_CONSTS

from dc_crawler.RTCPreprocessor import RTCPreprocessor


# That script create main rtc-preprocessor application


app = None
exit_code = APP_CONSTS.EXIT_FAILURE

if __name__ == "__main__":
  try:
    # create the app
    app = RTCPreprocessor()
    # setup the application
    app.setup()
    # add support command line arguments
    app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file',
                          required=True)

    # run the application
    app.run()

    # get exit code
    exit_code = app.exitCode

    # log message about profiler
    if pr.errorMsg and app.logger:
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
