#!/usr/bin/python


"""
  HCE project, Python bindings, Processor Manager application.
  Event objects definitions.
  
  @package: dc
  @file crawling-optimiser.py
  @author Oleksii <developers.hce@gmail.com>
  @link: http://hierarchical-cluster-engine.com/
  @copyright: Copyright &copy; 2013-2014 IOIX Ukraine
  @license: http://hierarchical-cluster-engine.com/license/
  @since: 0.1
  """


# crontab -e
# */5 * * * * cd ~/hce-node-bundle/api/python/ftests && ./crawling-optimiser.py -s=rss


import ppath
from ppath import sys

# For profiling
import app.Profiler as Profiler


# Start profiling
pr = Profiler.Profiler()
if pr and pr.status > 0:
  pr.start()


import os
from dc_co.CrawlingOptimiser import CrawlingOptimiser
import app.Consts as APP_CONSTS


# That script create main application


app = None
exit_code = APP_CONSTS.EXIT_SUCCESS

try:
  # create the app
  app = CrawlingOptimiser()
  # setup the application
  app.setup()
  # run the application
  app.run()

  exit_code = app.exit_code

  # log message about profiler
  if pr.errorMsg:
    app.logger.error(pr.errorMsg)

except Exception as err:
  sys.stderr.write(str(err))
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
