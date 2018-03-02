'''
HCE project, Python bindings, Distributed Tasks Manager application.
ExecutionEnvironmentManager object functional tests.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ConfigParser
import logging
import sys
import time

from app.BaseServerManager import BaseServerManager
import dtm.EventObjects
import dtm.ExecutionEnvironmentManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS


if __name__ == "__main__":
  logger = logging.getLogger()

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

if __name__ == "__main__":
  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"
  TTL = 7

  #Test ExecutionEnvironmentManager instantiation
  CONFIG_SECTION = "ExecutionEnvironmentManager"
  config = ConfigParser.RawConfigParser()
  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, "server", CONFIG_SECTION)
  config.set(CONFIG_SECTION, "clientTasksManager", "TasksManager")
  config.set(CONFIG_SECTION, "clientTasksManagerData", "TasksManagerData")
  config.set(CONFIG_SECTION, "DRCEHost", "localhost")
  config.set(CONFIG_SECTION, "DRCEPort", "5557")
  config.set(CONFIG_SECTION, "DRCETimeout", "1000")
  config.set(CONFIG_SECTION, "HCENodeAdminTimeout", "1000")


  print(sys.version)

  connectionBuilderLight = ConnectionBuilderLight()

  #Admin server connection sumulator
  adminServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)
  #TasksManager object server connection simulator
  tasksManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "TasksManager")
  #TasksManagerData object server connection simulator
  tasksManagerDataConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "TasksManagerData")

  time.sleep(1)

  #Create instance
  eem = dtm.ExecutionEnvironmentManager.ExecutionEnvironmentManager(config)

  print TEST_TITLE + eem.__class__.__name__ + TEST_TITLE_OBJECT, vars(eem)

  eem.setName(eem.__class__.__name__)
  eem.start()

  #Simulate ExecuteTask request
  eventBuilder = EventBuilder()
  executeTask = dtm.EventObjects.ExecuteTask(111)
  event = eventBuilder.build(DTM_CONSTS.EVENT_TYPES.EXECUTE_TASK, executeTask)
  eem.onExecuteTask(event)
  print "ExecuteTask event sent"

  time.sleep(TTL)

  eem.exit_flag = True

  print "Stopped after" + str(TTL) + " sec of run!"


