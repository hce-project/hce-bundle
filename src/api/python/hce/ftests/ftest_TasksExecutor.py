#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file ftest_TaskExecutor.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import ConfigParser
import logging

from dtm.TasksExecutor import TasksExecutor
from transport.ConnectionBuilderLight import ConnectionBuilderLight
  
logging.basicConfig(filename="../../log/dtmd.log") 
  
if __name__ == '__main__':
  config = ConfigParser.ConfigParser()
  config.read("../../ini/dtmd.ini")
  te = TasksExecutor(config, ConnectionBuilderLight())
  te.start()
