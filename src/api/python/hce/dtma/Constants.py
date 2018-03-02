'''
Created on Mar 25, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

APP_NAME = "dtma"
SERVER_CONFIG_SECTION_NAME = "Server"
SERVER_CONFIG_OPTION_NAME = "instantiateSequence"
SERVER_CONFIG_OPTION_NAME2 = "shutdownSequence"
DEFAULT_CONFIG_NAME1 = "./dtma.ini"
DEFAULT_CONFIG_NAME2 = "/ect/dtma.ini"
TCP_TIMEOUT = 10000
TCP_TIMEOUT_CONFIG_NAME = "timeout"
DTM_HOST = "clientHost"
DTM_PORT = "clientPort"
TASKS = ["STAT", "SET", "GET", "STOP", "SUSPEND", "SYSTEM", "SQL_CUSTOM"]
FIELDS_SEPARATOR = ","
NAME_VALUE_SEPARATOR = ":"
LOG_CONFIG_SECTION_NAME = "Application"
LOG_CONFIG_OPTION_NAME = "log"

ERROR_STR1 = "Not present [--help] or [--cmd] mandatory args"
ERROR_STR2 = "Not present [--fields] or [--classes] mandatory args"
ERROR_STR3 = "Not found config [{0}.{1}] section"
ERROR_STR4 = "Bad or empty --fields arg"
ERROR_STR5 = "Bad or empty --classes arg"
ERROR_STR7 = "Network communicate timeout={0} mls"
ERROR_STR8 = "Can't find log-ini section in config file"
ERROR_STR9 = "Not open Config file"
ERROR_STR10 = "Error while log initialize"

ERROR_NOERROR = 0
ERROR_NO_CONFIG = 2
ERROR_ARGS1 = 2
ERROR_ARGS2 = 2
ERROR_CONFIG_SECTION = 2
ERROR_FIELDS_ARG = 2
ERROR_CLASSES_ARG = 2
ERROR_NETWORK = 1
ERROR_LOG_SECTION_ERROR = 1
ERROR_LOG_INIT = 1
