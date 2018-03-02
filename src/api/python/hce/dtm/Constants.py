'''
HCE project, Python bindings, Distributed Tasks Manager application.
Application level constants and enumerations.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import app.Consts as APP_CONSTS

##Event types definition, used to unique identification events by inproc messaging transport
#
#
class EVENT_TYPES(object):
  #Request events
  NEW_TASK = 1
  UPDATE_TASK = 2
  DELETE_TASK_RESULTS = 3
  GET_TASK_STATUS = 4
  FETCH_TASK_RESULTS = 5
  FETCH_RESULTS_CACHE = 6
  DELETE_TASK = 7
  #TaskDataManager
  FETCH_TASK_DATA = 8
  INSERT_EE_DATA = 9
  DELETE_TASK_DATA = 10
  FETCH_EE_DATA = 11
  DELETE_EE_DATA = 12
  #ExecutionEnvironmentManager
  EXECUTE_TASK = 13
  DELETE_TASKS = 14
  CHECK_TASK_STATE = 15
  UPDATE_TASK_FIELDS = 17
  GET_TASK_FIELDS = 18
  #TasksExecutor
  GET_SCHEDULED_TASKS = 19
  #ResourcesStateMonitor
  UPDATE_RESOURCES_DATA = 20
  #ResourcesManager
  GET_AVG_RESOURCES = 21
  #TasksManager
  SCHEDULE_TASK = 22
  UPDATE_SCHEDULED_TASKS = 23
  #AdminInterfaceServer
  ADMIN_FETCH_STAT_DATA = 1024
  ADMIN_GET_CONFIG_VARS = 1025
  ADMIN_SET_CONFIG_VARS = 1026
  ADMIN_STATE = 1027
  ADMIN_SYSTEM = 1028
  ADMIN_SQL_CUSTOM = 1029
  SERVER_TCP_RAW = 28
  #TaskStateUpdateService
  FETCH_AVAILABLE_TASK_IDS = 30
  ADMIN_SUSPEND = 31

  #Response events
  GENERAL_RESPONSE = 100
  NEW_TASK_RESPONSE = 101
  UPDATE_TASK_RESPONSE = 102
  CHECK_TASK_STATE_RESPONSE = 103
  GET_TASK_STATUS_RESPONSE = 104
  FETCH_TASK_RESULTS_RESPONSE = 105
  DELETE_TASK_RESPONSE = 106
  #TaskDataManager
  FETCH_TASK_DATA_RESPONSE = 107
  INSERT_EE_DATA_RESPONSE = 108
  DELETE_TASK_DATA_RESPONSE = 109
  FETCH_EE_DATA_RESPONSE = 110
  DELETE_EE_DATA_RESPONSE = 111
  #ExecutionEnvironmentManager
  GET_TASK_FIELDS_RESPONSE = 112
  UPDATE_TASK_FIELDS_RESPONSE = 113
  #TaskExecutor
  GET_SCHEDULED_TASKS_RESPONSE = 114
  #ResourcesStateMonitor
  UPDATE_RESOURCES_DATA_RESPONSE = 115
  #ResourcesManager
  GET_AVG_RESOURCES_RESPONSE = 116
  #TasksManager
  SCHEDULE_TASK_RESPONSE = 117
  UPDATE_SCHEDULED_TASKS_RESPONSE = 118
  #ClientInterfaceService
  DELETE_TASK_RESULTS_RESPONSE = 119
  #AdminInterfaceServer
  ADMIN_FETCH_STAT_DATA_RESPONSE = 120
  ADMIN_GET_CONFIG_VARS_RESPONSE = 121
  ADMIN_SET_CONFIG_VARS_RESPONSE = 122
  ADMIN_STATE_RESPONSE = 123
  ADMIN_SQL_CUSTOM_RESPONSE = 124
  #TasksManager
  AVAILABLE_TASK_IDS_RESPONSE = 124
  ADMIN_SUSPEND_RESPONSE = 125

  ADMIN_SYSTEM_RESPONSE = 126


  ##constructor
  #initialize task's fields
  #
  def __init__(self):
    pass



##DRCE protocol fields names definition
#
#
class DRCE_FIELDS(object):
  #Request events
  ALG = "alg"
  DELAY = "delay"
  REPEAT = "repeat"
  SIGNAL = "signal"
  HOST = "host"
  PORT = "port"
  STATE = "state"
  URRAM = "TASK_RRAM"
  UVRAM = "TASK_VRAM"
  UCPU = "TASK_CPU"
  UTHREADS = "TASK_THREADS"


  ##constructor
  #initialize task's fields
  #
  def __init__(self):
    pass

#Logger name
#LOGGER_NAME = "dtm"
LOGGER_NAME = APP_CONSTS.LOGGER_NAME

CLEAR_ON_START = "ClearOnStart"

DB_CONFIG_SECTION = "DBData"

