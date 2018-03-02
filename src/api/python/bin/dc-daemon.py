#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file dc-daemon.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import ppath
from ppath import sys

from dc.DCD import DCD


#That script create main daemon application to run dtm


# create the app
app = None

try:
  app = DCD()
  # setup the application
  app.setup()
  app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file', required=True)
  app.args.add_argument('-n', '--name', action='store', metavar='app_name', help='application name')
  # run the application
  app.run()
  
except:
  raise
finally:
  # close the app
  app.close()
