#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
ScraperMultiItemsTask Class content main functional scrapering multi items.

@package: dc_processor
@file scraper_multi_items_task.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
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
from dc_processor.ScraperMultiItemsTask import ScraperMultiItemsTask
import app.Consts as APP_CONSTS


# That script create main scrapering multi items application


app = None
exit_code = APP_CONSTS.EXIT_SUCCESS

try:
  # create the app
  app = ScraperMultiItemsTask()
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
