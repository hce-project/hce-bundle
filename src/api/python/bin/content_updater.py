#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Content updater main functional.

@package: app
@file content_updater.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import ppath
from ppath import sys

import os
import sys
import app.Utils as Utils
import app.Consts as APP_CONSTS

from app.ContentUpdater import ContentUpdater


app = None
exit_code = APP_CONSTS.EXIT_FAILURE

if __name__ == "__main__":
  try:
    # create the app
    app = ContentUpdater()
    # setup the application
    app.setup()
    # add support command line arguments
    app.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file',
                          required=True)
    app.args.add_argument('-e', '--error', action='store', metavar='error_message', help='input error message',
                          required=False)

    # run the application
    app.run()

    # get exit code
    exit_code = app.exitCode

  except Exception, err:
    sys.stderr.write(str(err) + '\n')
    exit_code = APP_CONSTS.EXIT_FAILURE
  except:
    exit_code = APP_CONSTS.EXIT_FAILURE
  finally:
    # close the app
    if app:
      app.close()

    sys.stdout.flush()
    os._exit(exit_code)
