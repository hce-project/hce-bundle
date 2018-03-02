#!/usr/bin/python


"""
HCE project,  Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file crawler-task.py
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


# import time
# s = time.time()
# Start profiling
pr = Profiler.Profiler()
# print "t1=" + str(time.time() - s)
# s = time.time()
if pr and pr.status > 0:
  pr.start()
# print "t1=" + str(time.time() - s)


import os
import sys
from dc_crawler.CrawlerTask import CrawlerTask
from time import sleep
from sys import argv
import app.Consts as APP_CONSTS


# That script create main crawler application


app = None
exit_code = APP_CONSTS.EXIT_SUCCESS

try:
  # create the app
  app = CrawlerTask()
  # setup the application
  app.setup()
  app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file', required=True)
  app.args.add_argument('-m', '--maxtime', action='store', metavar='max_time', help='max time execution', required=False)
  # run the application
  app.run()

  exit_code = app.exit_code

  # log message about profiler
  if pr.errorMsg:
    app.logger.error(pr.errorMsg)

except Exception, err:
  sys.stderr.write(str(err))
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
