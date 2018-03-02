'''
HCE project, Python bindings, Distributed Tasks Manager application.
ResourcesStateMonitor object functional tests.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ConfigParser
import logging
import logging.config
import os
import time
import sys

from app.BaseServerManager import BaseServerManager
import dtm.ResourcesStateMonitor
from transport.ConnectionBuilderLight import ConnectionBuilderLight

import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS


#Logger init
if __name__ == "__main__":
  logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)
  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  #logging.config.fileConfig('/home/bgv/workspace_py/zmq_test/src/0/log1.cfg')




  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"
  TTL = 7

  #Test ExecutionEnvironmentManager instantiation
  CONFIG_SECTION = "ResourcesStateMonitor"
  config = ConfigParser.RawConfigParser()
  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, "clientResourcesManager", "ResourcesManager")
  config.set(CONFIG_SECTION, "HCENodeAdminTimeout", "10000")
  config.set(CONFIG_SECTION, "PollingTimeout", "5000")
  config.set(CONFIG_SECTION, "FetchResourcesStateDRCEJsonFile", "../../ini/res_fetch_drce.json")
  config.set(CONFIG_SECTION, "HCEClusterSchemaFile", "../../ini/hce_cluster_schema.json")


  print os.path.abspath(os.curdir)

  connectionBuilderLight = ConnectionBuilderLight()

  #Admin server connection sumulator
  adminServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)
  #ResourceManager object server connection simulator
  resourceManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, "ResourcesManager")

  #time.sleep(1)

  #Create instance
  rsm = dtm.ResourcesStateMonitor.ResourcesStateMonitor(config)

  print TEST_TITLE + rsm.__class__.__name__ + TEST_TITLE_OBJECT, vars(rsm)

  rsm.setName(rsm.__class__.__name__)
  rsm.start()

  time.sleep(TTL)

  rsm.exit_flag = True

  print "Stopped after" + str(TTL) + " sec of run!"
