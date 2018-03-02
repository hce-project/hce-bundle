'''
HCE project, Python bindings, Distributed Tasks Manager application.
TasksStateUpdateService object functional tests.

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
import dtm.TasksStateUpdateService
from transport.ConnectionBuilderLight import ConnectionBuilderLight

import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS


if __name__ == "__main__":
  logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)
  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"
  TTL = 60000 * 60

  #Test TasksStateUpdateService instantiation
  CONFIG_SECTION = "TasksStateUpdateService"
  config = ConfigParser.RawConfigParser()
  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, "clientTasksManager", "TasksManager")
  config.set(CONFIG_SECTION, "serverHost", "127.0.0.1")
  config.set(CONFIG_SECTION, "serverPort", "5500")
  config.set(CONFIG_SECTION, "clientExecutionEnvironmentManager", "ExecutionEnvironmentManager")
  config.set(CONFIG_SECTION, "checkStateInterval", "10")
  config.set(CONFIG_SECTION, "checkStateTasks", "20")

  #Dependent objects creation
  connectionBuilderLight = ConnectionBuilderLight()
  #Admin server connection simulator
  adminServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)
  #TasksManager connection simulator
  serverConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "TasksManager")
  #ExecutionEnvironmentManager connection simulator
  serverConnection2 = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "ExecutionEnvironmentManager")

  #Create instance
  tsus = dtm.TasksStateUpdateService.TasksStateUpdateService(config)
  print TEST_TITLE + tsus.__class__.__name__ + TEST_TITLE_OBJECT, vars(tsus)
  tsus.setName(tsus.__class__.__name__)
  tsus.start()
  time.sleep(TTL)
  tsus.exit_flag = True

  print "Stopped after" + str(TTL) + " sec of run!"


