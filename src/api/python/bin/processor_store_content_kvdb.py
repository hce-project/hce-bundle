#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file processor_store_content_kvdb.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import ppath
from ppath import sys

import os
from dc_processor.ProcessorStoreContentKVDB import ProcessorStoreContentKVDB
from dc_processor.ProcessorStoreContentKVDB import EXIT_SUCCESS
from dc_processor.ProcessorStoreContentKVDB import EXIT_FAILURE


# That script create main crawler application


# create the app
app = ProcessorStoreContentKVDB()
exit_code = EXIT_SUCCESS

try:
  # setup the application
  app.setup()
  # run the application
  app.run()
  app.processBatch()
  exit_code = app.getExitCode()
except Exception as err:
  print err.message
  exit_code = EXIT_FAILURE
finally:
  # close the app
  app.close()
  os._exit(exit_code)
