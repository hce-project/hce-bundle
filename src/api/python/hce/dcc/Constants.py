'''
Created on Apr 10, 2014

@package: dc
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

APP_NAME = "dcc"
HELP_COMMAND_TEMPLATE = "Available commands are: "
DEFAULT_CONFIG_NAME1 = "./dtmc.ini"
DEFAULT_CONFIG_NAME2 = "/ect/dtmc.ini"
TCP_TIMEOUT = 10000
TCP_TIMEOUT_CONFIG_NAME = "timeout"
DTM_HOST = "clientHost"
DTM_PORT = "clientPort"
LOG_CONFIG_SECTION_NAME = "Application"
LOG_CONFIG_OPTION_NAME = "log"
COOKIE_MERGE_NAME = "MERGE_RESULTS"
TASKS = ["SITE_NEW",
         "SITE_UPDATE",
         "SITE_STATUS",
         "SITE_DELETE",
         "SITE_CLEANUP",
         "URL_NEW",
         "URL_STATUS",
         "URL_UPDATE",
         "URL_FETCH",
         "URL_DELETE",
         "URL_CLEANUP",
         "URL_CONTENT",
         "SITE_FIND",
         "SQL_CUSTOM",
         "BATCH",
         "URL_PURGE",
         "F_RECALC",
         "URL_VERIFY",
         "URL_AGE",
         "URL_PUT",
         "URL_HISTORY",
         "URL_STATS",
         "PROXY_NEW",
         "PROXY_UPDATE",
         "PROXY_DELETE",
         "PROXY_STATUS",
         "PROXY_FIND",
         "ATTRIBUTE_SET",
         "ATTRIBUTE_UPDATE",
         "ATTRIBUTE_DELETE",
         "ATTRIBUTE_FETCH"]
#Corresponds with the TASKS list position above
TASKS_OBJECTS = ["Site",
                 "SiteUpdate",
                 "SiteStatus",
                 "SiteDelete",
                 "SiteCleanup",
                 "URL",
                 "URLStatus",
                 "URLUpdate",
                 "URLFetch",
                 "URLDelete",
                 "URLCleanup",
                 "URLContent",
                 "SiteFind",
                 "CustomRequest",
                 "Batch",
                 "URLPurge",
                 "FieldRecalculatorObj",
                 "URLVerify",
                 "URLAge",
                 "URLPut",
                 "URLHistoryRequest",
                 "URLStatsRequest",
                 "Proxy",
                 "ProxyUpdate",
                 "ProxyDelete",
                 "ProxyStatus",
                 "ProxyFind",
                 "Attribute",
                 "AttributeUpdate",
                 "AttributeDelete",
                 "AttributeFetch"]

ERROR_STR1 = "Not present [--help] or [--command] mandatory args"
ERROR_STR2 = "Absent [--file] or [--fields] arg with [--commands] arg"
ERROR_STR3 = "[--command] arg's value not present in value's list"
ERROR_STR4 = "[--file] wrong filename"
ERROR_STR5 = "Wrong JSON format"
ERROR_STR6 = "DCC exception msg={0}"
ERROR_STR7 = "Network communicate timeout={0} mls"
ERROR_STR8 = "Wrong Response eventObject type for {0} must be {1}"
ERROR_STR9 = "Can't open config file, required argument --config=<config_file_name>"
ERROR_STR10 = "Can't find log-ini section in config file"
ERROR_STR11 = "Error while log initialize"
ERROR_STR12 = "Connection error"
ERROR_STR13 = "JSON serialize error"
ERROR_STR14 = "Object instance creation error"

ERROR_NOERROR = 0
ERROR_CONFIG_SECTION = 2
ERROR_ARGS1 = 2
ERROR_ARGS2 = 2
ERROR_BAD_TASK = 2
ERROR_NO_CONFIG = 2
ERROR_BAD_FILE_NAME = 1
ERROR_BAD_JSON = 1
ERROR_DCC = 1
ERROR_NETWORK = 1
ERROR_WRONG_RESPONSE = 1
ERROR_LOG_SECTION_ERROR = 1
ERROR_LOG_INIT = 1
ERROR_CONNECTION = 1
ERROR_EXCEPTION = 3
ERROR_JSON = 2
ERROR_OBJECT_CREATE = 4
ERROR_INITIALIZATION = 5

FILE_PROTOCOL_SIGNATURE = "file://"
OBJECT_MAX_INIT_ARGUMENTS = 10

