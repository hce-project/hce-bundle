#!/usr/bin/python -O


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file dtm-daemon.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import ppath
from ppath import sys

import os
import sys

from dtm.DTMD import DTMD
import app.Consts as APP_CONSTS

# That script create main daemon application to run dtm


# create the app
app = DTMD()
exit_code = APP_CONSTS.EXIT_SUCCESS

try:
  # setup the application
  app.setup()
  app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file', required=True)
  app.args.add_argument('-l', '--log', action='store', metavar='log_file', help='log file')
  app.args.add_argument('-n', '--name', action='store', metavar='app_name', help='application name')
  # run the application
  app.run()
except Exception, err:
  sys.stderr.write(str(err))
  exit_code = APP_CONSTS.EXIT_FAILURE
except:
  sys.stderr.write('Unknown error.')
  exit_code = APP_CONSTS.EXIT_FAILURE
finally:
  # close the app
  app.close()

  sys.stdout.flush()
  os._exit(exit_code)
