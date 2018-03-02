# coding: utf-8
'''
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ctypes
from app.Utils import JsonSerializable
from app.Utils import getHash
from datetime import datetime
import json
import zlib
import time
import logging
import dtm.Constants as DTM_CONSTS
import app.SQLCriterions

from transport.IDGenerator import IDGenerator

logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)

##Task event object, defines the Task object fields
#
#The task object used to create task representation inside DTM application.
#This is a main data unit that is used by DTM inside to operate.
class Task(object):

  FILE_ACTION_CREATE_BEFORE = 1
  FILE_ACTION_DELETE_BEFORE = 2
  FILE_ACTION_READ_AFTER = 4
  FILE_ACTION_DELETE_AFTER = 8
  FILE_ACTION_BASE64_ENCODED = 2147483648

  STRATEGY_DATE = "DATE"
  STRATEGY_DATE_MAX = "DATE_MAX"
  STRATEGY_DATE_SHIFT = "DATE_SHIFT"
  STRATEGY_CPU = "CPU"
  STRATEGY_RAM_FREE = "RAM_FREE"
  STRATEGY_RAM = "RAM"
  STRATEGY_DISK_FREE = "DISK_FREE"
  STRATEGY_DISK = "DISK"
  STRATEGY_TIME = "TIME"
  STRATEGY_THREADS = "THREADS"
  STRATEGY_SDELAY = "SDELAY"
  STRATEGY_RDELAY = "RDELAY"
  STRATEGY_RETRY = "RETRY"
  STRATEGY_PRIORITY = "PRIORITY"
  STRATEGY_CPU_LOAD_MAX = "CPU_LOAD_MAX"
  STRATEGY_IO_WAIT_MAX = "IO_WAIT_MAX"
  STRATEGY_autoCleanupFields = "autoCleanupFields"

  STRATEGY_AUTOCLEANUP_TTL = "TTL"
  STRATEGY_AUTOCLEANUP_DELETE_TYPE = "DeleteType"
  STRATEGY_AUTOCLEANUP_DELETE_RETRIES = "DeleteRetries"
  STRATEGY_AUTOCLEANUP_SSTATE = "State"

  TASK_MODE_SYNCH = 1
  TASK_MODE_ASYNCH = 2

  TIME_MAX_DEFAULT = 60000

  TASK_TYPE_SHELL = 0
  TASK_TYPE_SSH = 1

  TYPE_DEFAULT = 0

  ##constructor
  #initialize task's fields
  #
  def __init__(self):
    ##@var id
    #The task Id
    self.id = None
    ##@var command
    #The task command line to execute inside EE.
    self.command = None
    ##@var input
    #The task cstdin stream buffer for EE process.
    self.input = None
    ##@var files
    #The task files items attached init
    self.files = []
    ##@var session
    #The task session items init
    self.session = {}
    ##@var strategy
    #The task strategy items init
    self.strategy = {}
    ##@var limits
    #The task limits init
    self.limits = {}
    ##@var autoCleanupFields
    #The task autoCleanupFields init
    self.autoCleanupFields = {}
    ##@var type
    #The task type init
    self.type = self.TYPE_DEFAULT
    ##@var name
    #The task name init
    self.name = ""


  ##Set the OS session variable for EE process.
  #
  #@param sessionVarName The session variable name.
  #@param sessionVarValue The session variable value.
  #@return nothing
  def setSessionVar(self, sessionVarName, sessionVarValue):
    self.session[sessionVarName] = sessionVarValue


  ##Set the strategy variable.
  #
  #@param strategyVarName The strategy variable name.
  #@param strategyVarValue The strategy variable value.
  #@return nothing
  def setStrategyVar(self, strategyVarName, strategyVarValue):
    self.strategy[strategyVarName] = strategyVarValue


  ##Set the file item. Appends file item to files container
  #
  #@param fileItem The file item for files container, format (fileName, byteStream, actionMask).
  #@return nothing
  def setFile(self, fileItem):
    self.files.append(fileItem)


  ##Set the limits variable.
  #
  #@param limitsVarName The limits variable name.
  #@param limitsVarValue The limits variable value.
  #@return nothing
  def setLimitsVar(self, limitsVarName, limitsVarValue):
    self.limits[limitsVarName] = limitsVarValue



##NewTask event object, defines the Task object fields
#
#The task object used to create new task representation inside DTM application.
#This is a main data unit that is used by DTM inside to operate.
class NewTask(Task):

  ##constructor
  #initialize task's fields
  #@param taskCommandLine The task's command line to execute in EE.
  #@param taskId The task's unique identifier, optional if omitted - generated as crc32 of the command.
  #
  def __init__(self, taskCommandLine, taskId=None, name=None):
    super(NewTask, self).__init__()
    ##@var id
    #The task Id
    if taskId is None:
      idGenerator = IDGenerator()
      #self.id = ctypes.c_ulong(zlib.crc32(idGenerator.get_connection_uid())).value
      #self.id = ctypes.c_uint32(zlib.crc32(idGenerator.get_connection_uid(), int(time.time()))).value
      self.id = getHash(idGenerator.get_connection_uid())
    else:
      self.id = taskId
    if name is not None:
      self.name = name
    ##@var command
    #The task command line to execute inside EE.
    self.command = taskCommandLine
    ##@var input
    #The task cstdin stream buffer for EE process.
    self.input = ""
    #Strategy priority init
    self.setStrategyVar(self.STRATEGY_PRIORITY, 1)
    #Session init
    self.setSessionVar("time_max", self.TIME_MAX_DEFAULT)
    self.setSessionVar("tmode", self.TASK_MODE_SYNCH)
    self.setSessionVar("type", self.TASK_TYPE_SHELL)
    self.setSessionVar("home_directory", "")
    self.setSessionVar("port", 0)
    self.setSessionVar("user", "")
    self.setSessionVar("password", "")
    self.setSessionVar("shell", "")
    self.setSessionVar("environment", {})
    self.setSessionVar("timeout", 0)


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##UpdateTask event object, for update task field operation
#
#The update task object used to update task representation inside DTM application.
class UpdateTask(Task):

  ##constructor
  #initialize task's fields
  #@param taskId The task's unique identifier.
  #
  def __init__(self, taskId):
    super(UpdateTask, self).__init__()
    ##@var id
    #The task Id
    self.id = taskId



##UpdateTaskFields event object, for update task fields operation
#
#The update task fields object used to update task fields of the TasksManager.
class UpdateTaskFields(object):

  ##constructor
  #initialize task's fields
  #@param taskId The task's unique identifier.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId
    ##@var fields
    #The task fields
    self.fields = {}



##GetTaskManagerFields event object, for get task fields values operation
#
#The get task manager fields object used to get task fields of the TasksManager event.
class GetTaskManagerFields(object):

  ##constructor
  #initialize task's fields
  #@param taskId The task's unique identifier.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId



##TaskManagerFields event object, for return task fields values
#
#The task manager fields object used to return task fields of the TasksManager response event.
class TaskManagerFields(object):

  ##constructor
  #initialize task's fields
  #@param taskId The task's unique identifier.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId
    ##@var fields
    #The task fields
    self.fields = {}


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##TasksStatus event object, returns task status operation
#
#The TasksStatus object contents task status inside DTM application.
class TasksStatus(object):


  def __init__(self):
    self.taskManagerFieldsList = []


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##GetTasksStatus event object, for check task status operation
#
#The GetTasksStatus object used to check task status inside DTM application.
class GetTasksStatus(object):

  LOG_STRATEGY = "CHECK_LOG"
  CHECK_LOG_YES = 1

  FILTER_CDATE_FROM = "CDATE_FROM"
  FILTER_CDATE_TO = "CDATE_TO"
  FILTER_SDATE_FROM = "SDATE_FROM"
  FILTER_SDATE_TO = "SDATE_TO"
  FILTER_RDATE_FROM = "RDATE_FROM"
  FILTER_RDATE_TO = "RDATE_TO"
  FILTER_FDATE_FROM = "FDATE_FROM"
  FILTER_FDATE_TO = "FDATE_TO"
  FILTER_INPROGRESS_TIME_FROM = "INPROGRESS_TIME_FROM"
  FILTER_INPROGRESS_TIME_TO = "INPROGRESS_TIME_TO"
  FILTER_INPROGRESS_TIME_MAX_FROM = "INPROGRESS_TIME_MAX_FROM"
  FILTER_INPROGRESS_TIME_MAX_TO = "INPROGRESS_TIME_MAX_TO"
  FILTER_INPROGRESS = "INPROGRESS"
  FILTER_SCHEDULED = "SCHEDULED"
  FILTER_RUNNING = "RUNNING"
  FILTER_FINISHED = "FINISHED"
  FILTER_TERMINATED = "TERMINATED"
  FILTER_CRASHED = "CRASHED"
  FILTER_RRAM_FROM = "RRAM_FROM"
  FILTER_RRAM_TO = "RRAM_TO"
  FILTER_VRAM_FROM = "VRAM_FROM"
  FILTER_VRAM_TO = "VRAM_TO"
  FILTER_CPU_FROM = "CPU_FROM"
  FILTER_CPU_TO = "CPU_TO"

  ##constructor
  #initialize task's fields
  #@param idsList The task Id list.
  #
  def __init__(self, idsList):
    ##@var ids
    #The task Ids list
    #self.ids = []
    self.ids = idsList
    ##@var filters
    #The filters criterion
    self.filters = {}
    ##@var strategy
    #The task strategy items attached
    self.strategy = {}


  ##Set the filter variable.
  #
  #@param filterVarName The filter variable name.
  #@param filterVarValue The filter variable value.
  #@return nothing
  def setFilterVar(self, filterVarName, filterVarValue):
    self.filters[filterVarName] = filterVarValue


  ##Set the strategy variable.
  #
  #@param strategyVarName The strategy variable name.
  #@param strategyVarValue The strategy variable value.
  #@return nothing
  def setStrategyVar(self, strategyVarName, strategyVarValue):
    self.strategy[strategyVarName] = strategyVarValue



##CheckTaskState event object, for check task status inside EE
#
#The CheckTaskState object used to get task status directly from EE.
class CheckTaskState(object):

  TYPE_SIMPLE = 1
  TYPE_FULL = 2

  ##constructor
  #initialize task's fields
  #@param taskId The task Id.
  #@param checkType The check type, specifies returned result object filling - simple brief or full.
  #
  def __init__(self, taskId, checkType=TYPE_SIMPLE):
    ##@var id
    #The task Id
    self.id = taskId
    ##@var type
    #The type of check
    self.type = checkType

  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##FetchTasksResults event object, for fetch task's results data from EE
#
#The FetchTasksResults object used to fetch task's results data from EE according with
#DRCE FO "Get task's data request".
class FetchTasksResults(object):

  TYPE_DELETE = 1
  TYPE_SAVE = 2

  ##constructor
  #initialize task's fields
  #@param taskId The task Id.
  #
  def __init__(self, taskId, fetchType=TYPE_DELETE):
    ##@var id
    #The task Id
    self.id = taskId
    ##@var type
    #The type of check
    self.type = fetchType

  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##FetchTasksResultsFromCache event object, for fetch task's results data from DTM application
#
#The FetchTasksResultsFromCache object used to fetch task's results data.
#To delete results data from cache - delete the task
class FetchTasksResultsFromCache(object):

  ##constructor
  #initialize task's fields
  #@param taskId The task Id.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.ids = taskId



##DeleteTask event object, to delete task from DTM application and from EE.
#
#The DeleteTask object used to completely delete all task(s)-related data inside DTM application and EE.
#If the task is in progress, it will be terminated and result data will be deleted.
class DeleteTask(Task):

  GROUP_DELETE = -1

  RESPONSE_CODE_DBI_ERROR = 1
  RESPONSE_CODE_UNKNOWN_ERROR = 2
  RESPONSE_CODE_DRCE_ERROR = 3

  TERMINATE_ALG_DEFAULT = 1
  TERMINATE_ALG_CUSTOM = 2

  TERMINATE_DELAY_DEFAULT = 1000
  TERMINATE_REPEAT_DEFAULT = 3

  TERMINATE_SIGTERM = 15
  TERMINATE_SIGKILL = 9

  ACTION_DELETE_TASK_DATA = 0
  ACTION_TERMINATE_TASK_AND_DELETE_DATA = 1
  ACTION_TERMINATE_TASK_ONLY = 2
  ACTION_DELETE_ON_DTM = 3

  DEFAULT_TASK_NAME = "DELETE"

  ##constructor
  #initialize task's fields
  #@param taskId The task Id to delete.
  #
  def __init__(self, deleteTaskId, taskId=None):
    super(DeleteTask, self).__init__()
    ##@var id
    #The task Id
    if taskId is None:
      idGenerator = IDGenerator()
      self.id = ctypes.c_uint32(zlib.crc32(idGenerator.get_connection_uid(), int(time.time()))).value
    else:
      self.id = taskId
    #Strategy priority init
    self.setStrategyVar(self.STRATEGY_PRIORITY, 1)
    #The task Id to delete, used for EE request TERMINATE task
    self.deleteTaskId = deleteTaskId
    ##@var alg
    #The algorithm of task termination in the EE.
    self.alg = self.TERMINATE_ALG_DEFAULT
    ##@var delay
    #The delay of task termination in the EE.
    self.delay = self.TERMINATE_DELAY_DEFAULT
    ##@var repeat
    #The repeat of task termination in the EE.
    self.repeat = self.TERMINATE_REPEAT_DEFAULT
    ##@var signal
    #The signal it is a UNIX signal used to terminate task process in the EE.
    self.signal = self.TERMINATE_SIGTERM
    ##@var host
    #The host name or IP address of task process HCE node in the EE.
    self.host = ""
    ##@var port
    #The TCP port of the HCE node admin interface for the  task process in the EE.
    self.port = 0
    # Action that will be performed on EEManager, default only delete task's data on EE and delete task on DTM
    # - this is possible only for tasks in proper state (that is not in active states)
    self.action = self.ACTION_DELETE_TASK_DATA
    ##@var strategy
    #The task strategy items init
    self.strategy = {}
    #TODO: possible find the way to define decorator
    #@property
    #def id(self):
    #  return self.id

    #@id.setter
    #def id(self, value):
    #  self.deleteTaskId = value
    self.name = self.DEFAULT_TASK_NAME

  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##ExecuteTask event object, to set task to execute on EE.
#
#The ExecuteTask object used to send list of task Ids to EEM.
class ExecuteTask(object):

  ##constructor
  #initialize task's field
  #@param taskId The task Id.
  #
  def __init__(self, taskId):
    ##@var ids
    #The task Id
    self.id = taskId



##GetScheduledTasks event object, to get tasks per time slot range from the Scheduler.
#
#The GetScheduledTasks object used to request tasks from the schedule.
class GetScheduledTasks(object):

  ##constructor
  #initialize task's field
  #@param idsList The task Id list.
  #
  def __init__(self, timeSlotSize):
    ##@var timeSlotSize, msec
    #The time slot size to get all tasks scheduled to run up to Now + timeSlotSize
    self.timeSlot = timeSlotSize



##GetScheduledTasksResponse event object, to return list of task from the Scheduler.
#
#The GetScheduledTasksResponse object used to return tasks.
class GetScheduledTasksResponse(object):

  ##constructor
  #initialize task's field
  #@param idsList The task Id list.
  #
  def __init__(self, idsList):
    ##@var ids
    #The task Ids list
    self.ids = idsList



##GeneralResponse event object, represents general state response for multipurpose usage
#
#The GeneralResponse object used to return unspecific common purpose response to get request status information
#or query the request acknowledgement.
class GeneralResponse(object):

  #General valid response value
  ERROR_OK = 0

  ##constructor
  #initialize response fields
  #@param idsList The task Id list.
  #
  def __init__(self, errorCode=ERROR_OK, errorMessage=""):
    ##@var errorCode
    #The errorCode of request operation, zero means success
    self.errorCode = errorCode
    ##@var errorMessage
    #The error message of request operation filled depends on
    self.errorMessage = errorMessage
    ##@var statuses
    #The list of statuses in case of request used for group of objects or actions
    self.statuses = []

  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##DeleteTaskData event object, to delete task's data in the storage.
#
#The DeleteTaskData object used to send request to delete task-related data.
class DeleteTaskData(object):

  ##constructor
  #initialize task id field
  #@param id task id.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId



##FetchEEResponseData event object, to fetch EE response data from the storage.
#
#The FetchEEResponseData object used to send request to the TaskDataManager.
class FetchEEResponseData(object):

  ##constructor
  #initialize task id field
  #@param id task id.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId



##DeleteEEResponseData event object, to delete EE response data from the storage.
#
#The DeleteEEResponseData object used to send request to the TaskDataManager.
class DeleteEEResponseData(object):

  ##constructor
  #initialize task id field
  #@param id task id.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId



##FetchTaskData event object, to fetch task data from the storage.
#
#The FetchTaskData object used to send request to the TaskDataManager.
class FetchTaskData(object):

  ##constructor
  #initialize task id field
  #@param id task id.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId



##EEResponseData event object, store task results data, returned from EE.
#
#The EEResponseData object used to represent tasks results data.
class EEResponseData(object):

  #Error codes
  ERROR_CODE_TIMEOUT = -1
  ERROR_CODE_OK = 0
  #ERROR_CODE_TASK_NOT_FOUND = -2
  ERROR_CODE_TASK_NOT_FOUND = 3
  ERROR_CODE_BAD_ID = 14

  #Error messages
  ERROR_MESSAGE_OK = ""
  ERROR_MESSAGE_TIMEOUT = "Request timeout reached!"
  ERROR_MESSAGE_TASK_NOT_FOUND = "Task not found in queue!"
  #Requests types
  REQUEST_TYPE_SET = 0
  REQUEST_TYPE_CHECK = 1
  REQUEST_TYPE_DELETE = 2
  REQUEST_TYPE_GET = 3
  #Task states
  TASK_STATE_FINISHED = 0
  TASK_STATE_IN_PROGRESS = 1
  TASK_STATE_NEW = 2
  TASK_STATE_NOT_FOUND = 3
  TASK_STATE_TERMINATED = 4
  TASK_STATE_CRASHED = 5
  TASK_STATE_SET_ERROR = 6
  TASK_STATE_UNDEFINED = 7
  TASK_STATE_TERMINATED_BY_DRCE_TTL = 11
  TASK_STATE_SCHEDULED_TO_DELETE = 100
  TASK_STATE_DELETED = 101
  TASK_STATE_NEW_DATA_STORED = 102
  TASK_STATE_NEW_SCHEDULED = 103
  TASK_STATE_CLEANED = 104
  TASK_STATE_NEW_JUST_CREATED = 105
  TASK_STATE_SCHEDULE_TRIES_EXCEEDED = 106
  TASK_STATE_RUN_TRIES_EXCEEDED = 107

  ##constructor
  #initialize response data fields
  #@param id task id.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId
    ##@var type
    #The request type
    self.type = self.REQUEST_TYPE_SET
    ##@var errorCode
    #The EE response errorCode
    self.errorCode = self.ERROR_CODE_OK
    ##@var errorMessage
    #The EE response error message
    self.errorMessage = self.ERROR_MESSAGE_OK
    ##@var requestTime
    #The EE request time
    self.requestTime = 0
    ##@var state
    #The task state
    self.state = self.TASK_STATE_FINISHED
    ##@var pId
    #The task process Id in EE
    self.pId = 0
    ##@var stdout
    #The task process stdout
    self.stdout = ""
    ##@var stderr
    #The task process stderr
    self.stderr = ""
    ##@var exitStatus
    #The task process exit status
    self.exitStatus = 0
    ##@var taskTime
    #The task execution time
    self.taskTime = 0
    ##@var nodeName
    #The task executor HCE node name in EE
    self.nodeName = ""
    ##@var nodeHost
    #The task executor HCE node host name
    self.nodeHost = ""
    ##@var nodePort
    #The task executor HCE node port
    self.nodePort = 0
    ##@var files
    #The files list attached to the task. Format of items the same as in NewTask object.
    self.files = []
    ##@var fields
    #The fields dict
    self.fields = {}

  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


  ##Set the file item. Appends file item to files container
  #
  #@param fileItem The file item for files container, format (fileName, byteStream, actionMask).
  #@return nothing
  def setFile(self, fileItem):
    self.files.append(fileItem)



##ScheduledTask event object, represents task's data fields in the Schedule container.
#
#The ScheduledTask object used to represent task's related data and for the Schedule container CRUD operations.
class ScheduledTask(object):

  STATE_PLANNED = 1
  STATE_INPROGRESS = 2
  STATE_CLOSED = 3

  ##constructor
  #initialize task data fields
  #@param id task id.
  #
  def __init__(self, taskId, rTime, rTimeMax, state, priority):
    ##@var id
    #The task Id
    self.id = taskId
    ##@var rTime
    #The time to run, msec. Zero means ASAP.
    self.rTime = rTime
    ##@var rTimeMax
    #The time to run max
    self.rTimeMax = rTimeMax
    ##@var state
    #The state of a task in the schedule
    self.state = state
    ##@var priority
    #The priority of the task in the schedule
    self.priority = priority



##UpdateScheduledTasks object used to represent task's related data update from the TasksManager to the Scheduler.
#
#
class UpdateScheduledTasks(object):

  ##constructor
  #initialize task data fields
  #@param scheduledTasks The ScheduledTasks object list.
  #
  def __init__(self, scheduledTasks=None):
    ##@var ids
    #The task Ids list
    self.tasks = []
    if scheduledTasks is not None:
      self.tasks = scheduledTasks



##GetScheduledTask event object, defines criterion to select tasks from the schedule.
#
#The GetScheduledTask object used to get tasks. If criterion field value is "None", it will not used
class GetScheduledTask(object):

  ##constructor
  #initialize criterion fields
  #@param id task id.
  #
  def __init__(self):
    ##@var taskIdMin
    #The task Id min
    self.taskIdMin = None
    ##@var taskIdMax
    #The task Id max
    self.taskIdMax = None
    ##@var rTimeMin
    #The time to run min
    self.rTimeMin = None
    ##@var rTimeMax
    #The time to run max
    self.rTimeMax = None
    ##@var state
    #The state of a task in the schedule
    self.state = ScheduledTask.STATE_PLANNED
    #The priority min
    self.priorityMin = None
    ##@var priorityMax
    #The priority max
    self.priorityMax = None



##Resource event object, represents resource's data fields .
#
#The Resource object used to represent task's related data and for the Schedule container CRUD operations.
class Resource(object):

  STATE_ACTIVE = 0
  STATE_UNDEFINED = 1
  STATE_INACTIVE = 2

  ##constructor
  #initialize resource data fields
  #@param nodeId node "host:port".
  #
  def __init__(self, nodeId):
    ##@var nodeId
    #The node host name + port string in format "host:port"
    self.nodeId = nodeId
    ##@var nodeName
    #The node name.
    self.nodeName = ""
    ##@var host
    #The node host
    self.host = ""
    ##@var port
    #The node port
    self.port = 0
    ##@var cpu
    #The node CPU LA, %
    self.cpu = 0
    ##@var io
    #The node io LA, %
    self.io = 0
    ##@var ramRU
    #The node resource RAM usage, byte
    self.ramRU = 0
    ##@var ramVU
    #The node virtual RAM usage, byte
    self.ramVU = 0
    ##@var ramR
    #The node resource RAM total, byte
    self.ramR = 0
    ##@var ramV
    #The node virtial RAM total, byte
    self.ramV = 0
    ##@var swap
    #The node swap total, byte
    self.swap = 0
    ##@var swapU
    #The node swap usage, byte
    self.swapU = 0
    ##@var disk
    #The node disk total, byte
    self.disk = 0
    ##@var diskU
    #The node disk usage, byte
    self.diskU = 0
    ##@var state
    #The node host state
    self.state = self.STATE_UNDEFINED
    ##@var uDate
    #The information update date
    self.uDate = datetime.now()
    #Number of CPU cores
    self.cpuCores = 0
    #Number of run threads
    self.threads = 0
    #Number of run processes
    self.processes = 0



##ResourcesAVG event object, represents summary of the EE resources utilization.
#
#The ResourcesAVG object represents resources utilization summary in %.
class ResourcesAVG(object):

  ##constructor
  #initialize resource AVG fields
  #
  def __init__(self):
    ##@var cpu
    #The node AVG CPU LA, %
    self.cpu = 0
    ##@var io
    #The node AVG io LA, %
    self.io = 0
    ##@var ramRU
    #The node AVG resource RAM usage, %
    self.ramRU = 0
    ##@var ramVU
    #The node AVG virtual RAM usage, %
    self.ramVU = 0
    ##@var ramR
    #The node AVG resource RAM usage, %
    self.ramR = 0
    ##@var ramV
    #The node AVG virtual RAM usage, %
    self.ramV = 0
    ##@var swap
    #The node AVG swap usage, %
    self.swap = 0
    ##@var disk
    #The node AVG disk usage, %
    self.disk = 0
    ##@var uDate
    #The information update date oldest
    self.uDate = 0
    #Number of CPU cores
    self.cpuCores = 0
    #Number of run threads
    self.threads = 0
    #Number of run processes
    self.processes = 0



##AdminStatData event object, for admin fetch stat fields and possible data from any threaded classes instances.
#Used for request and response.
#
class AdminStatData(object):

  FIELD_CLIENTS_LIST = "clients"

  ##constructor
  #initialize task's fields
  #@param className name of target class
  #@param statFieldsDic stat fields to fetch key is field name, if empty - all fields pairs returned
  #
  def __init__(self, className, statFieldsDic=None):
    ##@var id
    #The target class name, if None - all classes requested multicast way
    self.className = className
    ##@var fields
    #The stat fields to fetch, if empty - all fields pairs returned
    self.fields = {}
    if statFieldsDic is not None:
      self.fields = statFieldsDic


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##AdminConfigVars event object, for admin set or get config variables from any of threaded classes or application.
#
class AdminConfigVars(object):

  ##constructor
  #initialize task's fields
  #@param className name of target class
  #@param statFieldsList stat fields to fetch key is field name, if empty - all fields pairs returned
  #
  def __init__(self, className, configFieldsList=None):
    ##@var id
    #The target class name, if None - all classes requested multicast way
    self.className = className
    ##@var statFieldsList
    #The stat fields to fetch, if empty - all fields pairs returned
    self.fields = {}
    if configFieldsList is not None:
      self.fields = configFieldsList


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##AdminState event object, for admin manage change application state commands, like shutdown
#
class AdminState(object):

  STATE_NOP = 0
  STATE_READY = 1
  STATE_SHUTDOWN = 2
  STATE_SUSPEND = 3
  STATE_TRACE = 4
  STATE_TRANSACTION_ROLLBACK = 6
  STATE_ERROR = 7

  ##constructor
  #initialize task's fields
  #@param command the command code for state operation
  #@param className name of target class
  #
  def __init__(self, className, command):
    ##@var id
    #The target class name, if None - all classes requested multicast way
    self.className = className
    ##@var command
    #the command code for state operation
    self.command = command


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##AdminSuspend event object, for admin suspend command
#
class AdminSuspend(object):

  SUSPEND = 0
  RUN = 1

  ##constructor
  #initialize task's fields
  #@param command the command code for state operation
  #@param className name of target class
  #
  def __init__(self, suspendType=SUSPEND):
    ##@var type
    #Suspend operation type
    self.suspendType = suspendType


  def isSuspend(self):
    return self.suspendType == self.SUSPEND


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



##DeleteTaskResults event object, for delete task results from DTM application operation
#
#The DeleteTaskResults object used to completely delete the task-related data inside DTM application and EE.
class DeleteTaskResults(object):

  TASK_STATE_ERROR = 2000
  TASK_STATE_ERROR_MESSAGE = "Wrong task state to cleanup task's data!"
  TASK_NOT_FOUND_ERROR = 2001
  TASK_NOT_FOUND_ERROR_MESSAGE = "Task not found!"
  EMPRY_RAW_ERROR = 2002
  EMPRY_RAW_ERROR_MESSAGE = "Empty json raw!"
  DRCE_ERROR = 2003
  DRCE_ERROR_MESSAGE = "Some DRCE Error!"


  ##constructor
  #initialize task's fields
  #@param taskId The task's unique identifier.
  #
  def __init__(self, taskId):
    ##@var id
    #The task Id
    self.id = taskId



##FetchAvailabelTaskIds event object, for fetch available task id
class FetchAvailabelTaskIds(JsonSerializable):

  TABLE_NAME_DEFAULT = "task_back_log_scheme"

  ##constructor
  #initialize task's fields
  #@param fetchNum ids limit
  #@param fetchAdditionalFields means that we will extract addition fields from tasks kv-db database
  #@param criterions exctraction criterions
  def __init__(self, fetchNum, fetchAdditionalFields=False, criterions=None, tableName=TABLE_NAME_DEFAULT):
    super(FetchAvailabelTaskIds, self).__init__()
    self.criterions = criterions
    self.fetchNum = fetchNum
    self.fetchAdditionalFields = fetchAdditionalFields
    self.tableName = tableName
    self.fillCriterions()


  ##fillCriterions default initialize criterions method
  def fillCriterions(self):
    if self.criterions is None:
      self.criterions = {}
    if app.SQLCriterions.CRITERION_WHERE not in self.criterions or \
    self.criterions[app.SQLCriterions.CRITERION_WHERE] is None:
      self.criterions[app.SQLCriterions.CRITERION_WHERE] = "deleteTaskId = 0"
    if app.SQLCriterions.CRITERION_ORDER not in self.criterions or \
    self.criterions[app.SQLCriterions.CRITERION_ORDER] is None:
      self.criterions[app.SQLCriterions.CRITERION_ORDER] = "rDate"
    if app.SQLCriterions.CRITERION_LIMIT not in self.criterions or \
    self.criterions[app.SQLCriterions.CRITERION_LIMIT] is None:
      self.criterions[app.SQLCriterions.CRITERION_LIMIT] = self.fetchNum



##AvailableTaskIds event object, for return all available task id
class AvailableTaskIds(JsonSerializable):
  ##constructor
  #initialize task's fields
  #@param ids The sequence of all task ids
  #
  def __init__(self, ids, tasks=None):
    super(AvailableTaskIds, self).__init__()
    self.ids = ids
    self.tasks = tasks



##AvailableTaskIds event object, for return all available task id
class System(object):
  ##constructor
  #initialize task's fields
  #@param ids The sequence of all task ids
  #
  def __init__(self, stype=0, data=None):
    self.type = stype
    self.data = data


  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



from dbi.EventObjects import CustomRequest
from dbi.EventObjects import CustomResponse

