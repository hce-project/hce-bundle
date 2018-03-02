'''
HCE project, Python bindings, Distributed Tasks Manager application.
AdminInterfaceServer object functional tests.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ConfigParser

import dtm.AdminInterfaceServer
from transport.ConnectionBuilderLight import ConnectionBuilderLight

import transport.Consts as TRANSPORT_CONSTS


if __name__ == "__main__":
  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"

  #Test TasksStateUpdateService instantiation
  CONFIG_SECTION = "AdminInterfaceServer"
  config = ConfigParser.RawConfigParser()
  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, "server", "Admin")
  config.set(CONFIG_SECTION, "serverHost", "localhost")
  config.set(CONFIG_SECTION, "serverPort", "5502")

  #Create instance
  ais = dtm.AdminInterfaceServer.AdminInterfaceServer(config)

  print TEST_TITLE + ais.__class__.__name__ + TEST_TITLE_OBJECT, vars(ais)
  ais.exit_flag = True

