'''
Created on Mar 19, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

APP_NAME = "dtmc"
DEFAULT_CONFIG_NAME1 = "./dtmc.ini"
DEFAULT_CONFIG_NAME2 = "/ect/dtmc.ini"
TCP_TIMEOUT = 10000
TCP_TIMEOUT_CONFIG_NAME = "timeout"
DTM_HOST = "clientHost"
DTM_PORT = "clientPort"
TASKS = ["NEW", "CHECK", "TERMINATE", "GET", "STATUS", "CLEANUP", "GET_TASKS"]
LOG_CONFIG_SECTION_NAME = "Application"
LOG_CONFIG_OPTION_NAME = "log"

ERROR_STR1 = "Not present [--help] or [--task] mandatory args"
ERROR_STR2 = "Absents [--file] arg with [--task] arg"
ERROR_STR3 = "[--task] arg's value not present in value's list"
ERROR_STR4 = "[--file] wrong filename"
ERROR_STR5 = "Wrong JSON format"
ERROR_STR6 = "DTMC exception msg={0}"
ERROR_STR7 = "Network communicate timeout={0} mls"
ERROR_STR8 = "Wrong Response eventObject type for {0} must be {1}"
ERROR_STR9 = "Not open Config file"
ERROR_STR10 = "Can't find log-ini section in config file"
ERROR_STR11 = "Error while log initialize"
ERROR_STR12 = "TCP Connection Error"
ERROR_STR13 = "Some Config section error"
ERROR_STR14 = "Unknown task"


ERROR_NOERROR = 0
ERROR_NO_CONFIG = 2
ERROR_ARGS1 = 2
ERROR_ARGS2 = 2
ERROR_BAD_TASK = 2
ERROR_CONFIG_SECTION = 2
ERROR_BAD_FILE_NAME = 1
ERROR_BAD_JSON = 1
ERROR_DTMC = 1
ERROR_NETWORK = 1
ERROR_WRONG_RESPONSE = 1
ERROR_LOG_SECTION_ERROR = 1
ERROR_LOG_INIT = 1
ERROR_CONNECTION = 1
ERROR_UNKNOWN_TASK = 1
