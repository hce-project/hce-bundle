'''
@package: dtm
@author igor, bgv
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import logging
from collections import namedtuple
from functools import partial
from datetime import datetime
import time
import copy
from app.BaseServerManager import BaseServerManager
from dbi.dbi import DBI
from dbi.dbi import DBIErr
from Constants import EVENT_TYPES, LOGGER_NAME
from TaskBackLogScheme import TaskBackLogScheme
from TaskLog import TaskLog
from TaskLogScheme import TaskLogScheme
from EventObjects import GeneralResponse, DeleteTask, TaskManagerFields, EEResponseData, FetchTaskData, Task
from EventObjects import DeleteTaskData, DeleteEEResponseData, AvailableTaskIds, GetTasksStatus
import dbi.Constants as dbi_consts
import app.SQLCriterions
import transport.Consts as consts
import dtm.Constants as DTM_CONSTS
import app.Utils as Utils  # pylint: disable=F0401
import pickle
import types
from app.Utils import ExceptionLog
from app.Utils import varDump
import sqlalchemy
from sqlalchemy import text

logger = logging.getLogger(LOGGER_NAME)

# tuple describes one step of processing sequence
TaskStep = namedtuple("TaskStep", "ok_callback err_callback desc eventNewTask")

# one processing sequence
TaskRecord = namedtuple("TaskRecord", "tasksteps event responseEventType")



# #@todo remore const in suitable place
STEP_SEND_TO_TASKS_DATA_MANAGER = 1
STEP_ADD_TO_INTERNAL_STRUCTURES = 2
STEP_SEND_TO_SCHEDULER = 3
STEP_UPDATE_STATE = 4

# #Class is used to inform about error of manipulating tasks
# which are not presented in TaskManager.tasksQueue
#
class TaskNoPresentErr(Exception):
  ERR_CODE = 101

  def __init__(self, message):
    Exception.__init__(self, message)



# #It is a main object that manages tasks
#
class TasksManager(BaseServerManager):

  # Configuration settings options names
  SERVER = "server"
  TASKS_DATA_MANAGER_CLIENT = "clientTasksDataManager"
  SCHEDULER_CLIENT = "clientScheduler"
  CONFIG_TIME_SLOT_PERIOD = "timeSlotPeriod"
  AUTO_CLEANUP_TIME_SLOT_PERIOD = "autoCleanUpSlotPeriod"

  VAR_TASKS_TOTAL = "tasks_total"
  VAR_TASKS_TOTAL_DEL = "tasks_total_del"
  VAR_TASKS_TIME_SUM = "tasks_time_sum"
  VAR_TASKS_TIME_COUNT = "tasks_time_count"
  VAR_TASKS_TIME_AVG = "tasks_time_avg"
  VAR_TASKS_TIME_MIN = "tasks_time_min"
  VAR_TASKS_TIME_MAX = "tasks_time_max"
  VAR_TASKS_ERRORS = "tasks_errors"
  VAR_TASKS_RETRIES = "tasks_retries"
  VAR_TASKS_RETRIES_DEL = "tasks_retries_del"
  VAR_TASKS_DELETE_TRIES = "tasks_delete_tries"

  # Tables list for cleanup
  CLEANUP_TABLES_LIST = ['task_back_log_scheme',
                         'tasks_data_table',
                         'scheduler_task_scheme',
                         'ee_responses_table',
                         'resources_table']

  # #constructor
  # initialise all connections and event handlers
  #
  def __init__(self, configParser, connectBuilderLight, pollerManager=None):
    super(TasksManager, self).__init__(pollerManager)

    self.cfg_section = self.__class__.__name__

    self.groupDeleteResponseEvent = None
    serverAddr = configParser.get(self.cfg_section, self.SERVER)
    tasksDataManagerAddr = configParser.get(self.cfg_section, self.TASKS_DATA_MANAGER_CLIENT)
    schedulerAddr = configParser.get(self.cfg_section, self.SCHEDULER_CLIENT)

    serverConnection = connectBuilderLight.build(consts.SERVER_CONNECT, serverAddr)
    tasksDataManagerConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, tasksDataManagerAddr)
    schedulerConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, schedulerAddr)

    self.addConnection(self.SERVER, serverConnection)
    self.addConnection(self.TASKS_DATA_MANAGER_CLIENT, tasksDataManagerConnection)
    self.addConnection(self.SCHEDULER_CLIENT, schedulerConnection)

    # server events
    self.setEventHandler(EVENT_TYPES.NEW_TASK, self.onNewTask)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK, self.onUpdateTask)
    self.setEventHandler(EVENT_TYPES.GET_TASK_STATUS, self.onGetTaskStatus)
    self.setEventHandler(EVENT_TYPES.FETCH_RESULTS_CACHE, self.onFetchResultsCache)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK, self.onDeleteTask)
    self.setEventHandler(EVENT_TYPES.GET_TASK_FIELDS, self.onGetTaskFields)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK_FIELDS, self.onUpdateTaskField)
    self.setEventHandler(EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS, self.onFetchAvailableTasks)
    # tasksDataManager, Scheduler events - new,update, delete
    self.setEventHandler(EVENT_TYPES.NEW_TASK_RESPONSE, self.onTasksManagerGeneralResponse)
    self.setEventHandler(EVENT_TYPES.SCHEDULE_TASK_RESPONSE, self.onTasksManagerGeneralResponse)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK_RESPONSE, self.onTasksManagerGeneralResponse)
    self.setEventHandler(EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE, self.onFetchResultResponse)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK_RESPONSE, self.onDeleteTaskResponse)
    self.setEventHandler(EVENT_TYPES.DELETE_EE_DATA_RESPONSE, self.onDeleteTaskResponse)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK_DATA_RESPONSE, self.onDeleteTaskResponse)
    self.setEventHandler(EVENT_TYPES.FETCH_TASK_DATA_RESPONSE, self.onFetchTaskDataResponse)


    # #@var tasksQueue
    # map task.id => task without files field
    self.tasksQueue = {}

    # #@var pendingTasks
    # contains all pending tasks in task manager (operation steps)
    # map event.uid => list of operations steps
    self.pendingTasks = {}

    # #@var dbi
    # db contains two tables log and backlog
    self.dbi = DBI(self.createDBIDict(configParser))

    # #@var fetchEvents
    # map event.uid => event
    self.fetchEvents = {}

    isClearOnStart = configParser.get(self.cfg_section, DTM_CONSTS.CLEAR_ON_START)
    self.cleanUpOnStart(isClearOnStart)

    # get time slot period
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(self.cfg_section,
                                                                             self.CONFIG_TIME_SLOT_PERIOD)
    if self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] is not None:
      self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] * 1000
    self.cleanUpTimeout = configParser.getint(self.cfg_section, self.AUTO_CLEANUP_TIME_SLOT_PERIOD)
    self.prevCleanUpTime = 0
    self.updateStatField(self.VAR_TASKS_TOTAL, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_TOTAL_DEL, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_TIME_SUM, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_TIME_COUNT, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_TIME_AVG, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_TIME_MIN, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_TIME_MAX, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_ERRORS, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_RETRIES, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_RETRIES_DEL, 0, self.STAT_FIELDS_OPERATION_INIT)
    self.updateStatField(self.VAR_TASKS_DELETE_TRIES, 0, self.STAT_FIELDS_OPERATION_INIT)


  # #cleanUpOnStart method cleanups tasks queue before start
  #
  # @isClearOnStart param - make cleanup or not
  def cleanUpOnStart(self, isClearOnStart):
    if isClearOnStart == "True":
      try:
        suspendedTasks = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=id")
        if hasattr(suspendedTasks, '__iter__') and len(suspendedTasks) > 0 and suspendedTasks[0] is not None:
          for task in suspendedTasks:
            logger.debug(">>> Start suspend task to delete id=%s", task.id)
            task.state = EEResponseData.TASK_STATE_FINISHED
            task.deleteTaskId = 0
            self.dbi.update(task, "id=%s" % str(task.id))

          for task in suspendedTasks:
            deleteObj = DeleteTask(task.id)
            delEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, deleteObj)
            self.onDeleteTask(delEvent)
      except DBIErr as err:
        logger.error(">>> Some DBI error in TasksManager.cleanUpOnStart [" + str(err.message) + "]")
      except Exception, err:
        logger.error("Exception: %s", str(err))


  # #onNewTask event handler
  #
  # @param event instance of Event object
  def onNewTask(self, event):
    try:
      operation_steps = self.createOperationSteps(event, EVENT_TYPES.NEW_TASK)
      logger.debug("Insert pendingTasks[] item " + str(event.uid))
      logger.debug("New Task event " + str(event.eventObj.id))
      dbiRecords = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=%s" % str(event.eventObj.id))
      if hasattr(dbiRecords, '__iter__') and len(dbiRecords) > 0 and dbiRecords[0] is not None:
        logger.debug("Task Id already exist")
        responseEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK_RESPONSE, GeneralResponse())
        responseEvent.uid = event.uid
        self.reply(event, responseEvent)
      else:
        self.pendingTasks[event.uid] = TaskRecord(operation_steps, event, EVENT_TYPES.NEW_TASK_RESPONSE)
        operation_steps[0].ok_callback()
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")
    self.checkCleanUp()


  # #creates operation steps for addition new task
  #
  # @param event instance of Event object
  # @return list of TaskStep objects
  def createOperationSteps(self, event, dataManagerEventType, onlyLastTwo=False):
    try:
      if not onlyLastTwo:
        dataManagerEvent = self.eventBuilder.build(dataManagerEventType, event.eventObj)
        dataManagerEvent.uid = event.uid
        ok_callback = partial(self.send, self.TASKS_DATA_MANAGER_CLIENT, dataManagerEvent)
        err_callback = None
        desc = STEP_SEND_TO_TASKS_DATA_MANAGER
        first = TaskStep(ok_callback, err_callback, desc, event)

        ok_callback = partial(self.addNewTaskData, event)
        err_callback = partial(self.cleanAfterDBIErr, event)
        desc = STEP_ADD_TO_INTERNAL_STRUCTURES
        second = TaskStep(ok_callback, err_callback, desc, event)

      newEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK, event.eventObj)
      newEvent.uid = event.uid

      ok_callback = partial(self.send, self.SCHEDULER_CLIENT, newEvent)
      err_callback = partial(self.newTaskRollback, event)
      desc = STEP_SEND_TO_SCHEDULER
      third = TaskStep(ok_callback, err_callback, desc, event)

      ok_callback = partial(self.finishNewTaskData, event)
      err_callback = partial(self.newTaskRollback, event)
      desc = STEP_UPDATE_STATE
      four = TaskStep(ok_callback, err_callback, desc, event)

    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")

    if onlyLastTwo:
      ret = [third, four]
    else:
      ret = [first, second, third, four]
    return ret



  # #creates new task procesing sequence
  #
  # @param event instance of Event object
  def addNewTaskData(self, event):
    try:
      logger.debug("New task data id = " + str(event.eventObj.id) + " type = " + str(type(event.eventObj)))
      newTask = event.eventObj
      newTask.files = None
      self.tasksQueue[newTask.id] = newTask
      taskLog = self.createTaskLog(newTask)
      taskLog.state = EEResponseData.TASK_STATE_NEW_DATA_STORED
      taskLog.cDate = datetime.now()
      taskLog.tries = 0
      taskLog.name = newTask.name
      taskLog.type = newTask.type
      if "time_max" in newTask.session:
        taskLog.pTimeMax = newTask.session["time_max"]
      if newTask.autoCleanupFields is not None:
        if "TTL" in newTask.autoCleanupFields and newTask.autoCleanupFields["TTL"] is not None:
          newTask.autoCleanupFields["TTL"] = newTask.autoCleanupFields["TTL"] + time.time()
        taskLog.autoCleanupFields = pickle.dumps(newTask.autoCleanupFields)
      if taskLog.deleteTaskId == None:
        self.updateStatField(self.VAR_TASKS_TOTAL, 1, self.STAT_FIELDS_OPERATION_ADD)
      else:
        self.updateStatField(self.VAR_TASKS_TOTAL_DEL, 1, self.STAT_FIELDS_OPERATION_ADD)
      self.dbi.insert(TaskBackLogScheme(taskLog))

      # go to the next step
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GENERAL_RESPONSE, GeneralResponse())
      responseEvent.uid = event.uid

      self.processOperationStep(responseEvent)

    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.addNewTaskData [" + str(err.message) + "]")
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GENERAL_RESPONSE, GeneralResponse(err.errCode, err.message))
      responseEvent.uid = event.uid
      self.processOperationStep(responseEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #finished processing new task sequence
  #
  # @param event instance of Event object
  def finishNewTaskData(self, event):
    try:
      newTask = event.eventObj
      taskLog = self.createTaskLog(newTask)
      taskLog.state = EEResponseData.TASK_STATE_NEW_SCHEDULED
      self.dbi.update(TaskBackLogScheme(taskLog), "id = %s" % newTask.id)

      responseEvent = self.eventBuilder.build(EVENT_TYPES.GENERAL_RESPONSE, GeneralResponse())
      responseEvent.uid = event.uid

      self.processOperationStep(responseEvent)

    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.finishNewTaskData [" + str(err.message) + "]")
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GENERAL_RESPONSE, GeneralResponse(err.errCode, err.message))
      responseEvent.uid = event.uid
      self.processOperationStep(responseEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #rollback all changes after scheduler error
  #
  # @param event instance of Event object
  def newTaskRollback(self, event):
    try:
      self.processSchedulerFailure(event)
      # #@todo disccuss rescheduling strategy
      self.cleanAfterDBIErr(event)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onUpdateTask event handler
  #
  # @param event instance of Event object
  def onUpdateTask(self, event):
    try:
      response = GeneralResponse()
      updateTask = event.eventObj
      self.checkTaskPresence(updateTask.id)

      # don't need to update backlog?? because we use only Task.id
      self.send(self.TASKS_DATA_MANAGER_CLIENT, event)
      updateTask.files = None
      self.tasksQueue[updateTask.id] = updateTask
      schedulerEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK, self.tasksQueue[updateTask.id])
      self.send(self.SCHEDULER_CLIENT, schedulerEvent)

    except TaskNoPresentErr as err:
      logger.error(err.message)
      response = GeneralResponse(TaskNoPresentErr.ERR_CODE, err.message)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")
    finally:
      responseEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK_RESPONSE, response)
      self.reply(event, responseEvent)



  # #getDeletedTask checks deleted task in kvdb storage
  #
  # @param taskLog - incoming deleted task taskLog
  # return exist deleteTask id or none
  def getDeletedTask(self, taskLog):
    ret = None
    try:
      dbiRecords = self.dbi.fetch(TaskBackLogScheme(TaskLog), "deleteTaskId=%s" % str(taskLog.id))
      if hasattr(dbiRecords, '__iter__') and len(dbiRecords) > 0 and dbiRecords[0] is not None:
        ret = dbiRecords[0].id
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.onDeleteTask [" + str(err) + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")

    return ret



  # #onDeleteTask event handler
  #
  # @param event instance of Event object
  def onDeleteTask(self, event):
    response = None
    try:
      # branch for multi-deleting
      if event.eventObj.deleteTaskId == DeleteTask.GROUP_DELETE:
        try:
          dbiRecords = self.dbi.fetch(TaskBackLogScheme(TaskLog), "deleteTaskId=0")
        except DBIErr as err:
          logger.error(">>> Some DBI error in TasksManager.onDeleteTask [" + str(err.message) + "]")
          response = GeneralResponse()
        else:
          if hasattr(dbiRecords, '__iter__') and len(dbiRecords) > 0 and dbiRecords[0] is not None:
            self.groupDeleteResponseEvent = event
            for record in dbiRecords:
              taskLog = self.createTaskLog(event.eventObj)
              taskLog.id = record.id
              if self.getDeletedTask(taskLog) is None:
                localDeleteObj = DeleteTask(taskLog.id)
                delObject = copy.copy(event.eventObj)
                delObject.deleteTaskId = taskLog.id
                delObject.id = localDeleteObj.id
                delEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, delObject)
                self.simpleDeleteTask(delEvent, None)
          else:
            response = GeneralResponse()
      # branch for simple-deleting
      else:
        response = self.simpleDeleteTask(event, EVENT_TYPES.DELETE_TASK_RESPONSE)
      if response != None:
        responseEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK_RESPONSE, response)
        self.reply(event, responseEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #makes delete Task operation for simple task
  #
  # @param event instance of Event object
  def simpleDeleteTask(self, event, responseEventType):
    response = None
    try:
      deleteTask = event.eventObj
      taskLog = self.createTaskLog(deleteTask)
      taskLog.id = deleteTask.deleteTaskId
      if self.getDeletedTask(taskLog) is None:
        dbiRecords = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=%s" % taskLog.id)
        if len(dbiRecords) > 0:
          operation_steps = self.createOperationSteps(event, EVENT_TYPES.NEW_TASK)
          logger.debug("Update pendingTasks[] item " + str(event.uid))
          self.pendingTasks[event.uid] = TaskRecord(operation_steps, event, responseEventType)
          operation_steps[0].ok_callback()
          self.updateStatField(self.VAR_TASKS_DELETE_TRIES, 1, self.STAT_FIELDS_OPERATION_ADD)
        else:
          raise DBIErr(dbi_consts.DBI_SUCCESS_CODE + 1, "Task id=" + str(taskLog.id) + " is absent in taskBackLog")
      else:
        raise DBIErr(dbi_consts.DBI_SUCCESS_CODE + 2, "Task id=" + str(taskLog.id) + " is deleted by other task")
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.simpleDeleteTask [" + str(err.message) + "]")
      response = GeneralResponse(GeneralResponse.ERROR_OK, err.message)
      response.statuses.append(err.errCode)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")
    return response



  # #sendGroupDeleteResponse looks records in kvdb and sends back response on group delete operation
  #
  def sendGroupDeleteResponse(self):
    try:
      if self.groupDeleteResponseEvent is not None:
        suspendedTasks = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=id")
        if not (hasattr(suspendedTasks, '__iter__') and len(suspendedTasks) > 0 and suspendedTasks[0] is not None):
          response = GeneralResponse()
          responseEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK_RESPONSE, response)
          self.reply(self.groupDeleteResponseEvent, responseEvent)
          logger.debug(">>> Send Group delete back")
          self.groupDeleteResponseEvent = None
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onGetTaskStatus event handler
  #
  # @param event instance of Event object
  def onGetTaskStatus(self, event):
    logger.debug("GetTaskStatus received: " + Utils.varDump(event))
    try:
      # #as discuss don't check states
      getTaskStatus = event.eventObj
      results = list()
      for taskId in getTaskStatus.ids:
        try:
          lookBackTaskLogScheme = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=%s" % taskId)
          # #always return list
          taskManagerFields = TaskManagerFields([taskId])
          if (hasattr(lookBackTaskLogScheme, '__iter__') and len(lookBackTaskLogScheme) > 0):
            # pylint: disable-msg=W0212
            taskManagerFields = self.createTaskManagerFields(lookBackTaskLogScheme[0]._getTaskLog())
            results.append(taskManagerFields)
          elif type(getTaskStatus.strategy) is types.DictType and GetTasksStatus.LOG_STRATEGY in \
          getTaskStatus.strategy and getTaskStatus.strategy[GetTasksStatus.LOG_STRATEGY] == GetTasksStatus.CHECK_LOG_YES:
            lookTaskLogScheme = self.dbi.fetch(TaskLogScheme(TaskLog), "id=%s" % taskId)
            if (hasattr(lookTaskLogScheme, '__iter__') and len(lookTaskLogScheme) > 0):
              for foundTask in lookTaskLogScheme:
                # pylint: disable-msg=W0212
                taskManagerFields = self.createTaskManagerFields(foundTask._getTaskLog())
                results.append(taskManagerFields)
        except DBIErr as err:
          logger.error(">>> Some DBI error in TasksManager.onGetTaskStatus [" + str(err.message) + "]")
          results.append(None)
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS_RESPONSE, results)
      self.reply(event, responseEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onFetchResultsCache event handler
  #
  # @param event instance of Event object
  def onFetchResultsCache(self, event):
    try:
      fetchResultsCacheTask = event.eventObj
      for taskId in fetchResultsCacheTask.ids:
        self.checkTaskPresence(taskId)
      # store events for reply
      self.fetchEvents[event.uid] = event
      self.send(self.TASKS_DATA_MANAGER_CLIENT, event)
    except TaskNoPresentErr as err:
      logger.error(err.message)
      response = GeneralResponse(TaskNoPresentErr.ERR_CODE, err.message)
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS_RESPONSE, response)
      self.reply(event, responseEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onGetTaskFields event handler
  #
  # @param event instance of Event object
  def onGetTaskFields(self, event):
    try:
      getTaskManagerFields = event.eventObj
      taskId = getTaskManagerFields.id

      taskManagerFields = TaskManagerFields([taskId])
      lookTaskLogScheme = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=%s" % taskId)
      if len(lookTaskLogScheme) > 0 and lookTaskLogScheme[0] is not None:
        # pylint: disable-msg=W0212
        taskManagerFields = self.createTaskManagerFields(lookTaskLogScheme[0]._getTaskLog())
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GET_TASK_FIELDS_RESPONSE, taskManagerFields)
      self.reply(event, responseEvent)
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.onGetTaskStatus [" + str(err.message) + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onUpdateTaskField event handler
  #
  # @param event instance of Event object
  def onUpdateTaskField(self, event):
    try:
      generalResponse = GeneralResponse()
      updateTaskFields = event.eventObj
      try:
        # Removing "host" and "port" fields from updateTaskFields.fields and check is state value to update valid
        updateTaskFields.fields = self.clearEmptyFields(updateTaskFields.fields, updateTaskFields.id)

        taskLog = self.createTaskLogFromDic(updateTaskFields.fields)
        taskLogBackScheme = self.dbi.update(TaskBackLogScheme(taskLog), "id=%s" % updateTaskFields.id)
        if taskLog.state == EEResponseData.TASK_STATE_SET_ERROR or taskLog.state == EEResponseData.TASK_STATE_CRASHED:
          self.updateStatField(self.VAR_TASKS_ERRORS, 1, self.STAT_FIELDS_OPERATION_ADD)
        if taskLog.state == EEResponseData.TASK_STATE_DELETED or taskLog.state == EEResponseData.TASK_STATE_TERMINATED:
          logger.debug("Delete task is deleted, call cleanUpTask() [%s]", str(taskLog.state))
          self.cleanUpTask(taskLogBackScheme)
          if "deleteTaskId" in updateTaskFields.fields and updateTaskFields.fields["deleteTaskId"] != None and \
          updateTaskFields.fields["deleteTaskId"] > 0:
            taskLogTerm = TaskLog()
            taskLogTerm.id = int(updateTaskFields.fields["deleteTaskId"])
            taskLogTerm.state = int(updateTaskFields.fields["deleteTaskState"])
            taskLogBackSchemeTerm = self.dbi.update(TaskBackLogScheme(taskLogTerm), "id=%s" % taskLogTerm.id)
            if taskLogTerm.state == EEResponseData.TASK_STATE_DELETED or \
              taskLogTerm.state == EEResponseData.TASK_STATE_TERMINATED:
              logger.debug("Task to delete is terminated, call cleanUpTask()")
              self.cleanUpTask(taskLogBackSchemeTerm)
            else:
              logger.debug("Task to delete is not terminated, state: " + str(taskLogTerm.state))
          else:
            logger.debug("Task to delete is None or Empty")
            generalResponse.errorCode = DeleteTask.RESPONSE_CODE_DRCE_ERROR
            generalResponse.errorMessage = "EEManager returns empty deleteTaskId"
          self.sendGroupDeleteResponse()
        elif taskLog.state == EEResponseData.TASK_STATE_SET_ERROR:
          logger.debug("Delete task by state=TASK_STATE_SET_ERROR, id = " + str(updateTaskFields.id))
          self.cleanUpTaskNetworkOperation(updateTaskFields.id, False)
          self.restoreTaskSteps(updateTaskFields.id)
        else:
          logger.debug("State is: " + str(taskLog.state))
          self.checkCleanUp(updateTaskFields.id)
      except DBIErr as err:
        logger.error(">>> Some DBI error in TasksManager.onUpdateTaskField [" + str(err.message) + "]")
        generalResponse.errorCode = DeleteTask.RESPONSE_CODE_DBI_ERROR
        generalResponse.errorMessage = ("DBIError=%s" % str(err.message))
      except Exception as err:
        ExceptionLog.handler(logger, err, "Exception:")
        generalResponse.errorCode = DeleteTask.RESPONSE_CODE_UNKNOWN_ERROR
        generalResponse.errorMessage = ("Unknown Error=%s" % str(err.message))
      responseEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK_FIELDS_RESPONSE, generalResponse)
      self.reply(event, responseEvent)

    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onFetchTaskDataResponse callback, receive response from TDM
  #
  # @param event - incoming event
  def onFetchTaskDataResponse(self, event):
    logger.debug("onFetchTaskDataResponse income id = " + str(event.eventObj.id))
    taskLog = TaskLog()
    isCleanUp = True
    try:
      if event.eventObj != None:
        if event.eventObj.strategy != None and Task.STRATEGY_RETRY in event.eventObj.strategy:
          tempBackTaskLogScheme = self.dbi.fetch(TaskBackLogScheme(taskLog), "id=%s" % event.eventObj.id)
          logger.debug("onFetchTaskDataResponse tempBackTaskLogScheme len = " + str(len(tempBackTaskLogScheme)))
          if type(tempBackTaskLogScheme) == types.ListType and len(tempBackTaskLogScheme) > 0 and \
          event.eventObj.strategy[Task.STRATEGY_RETRY] > (tempBackTaskLogScheme[0].tries + 1):
            isCleanUp = False
            self.updateStatField(self.VAR_TASKS_RETRIES, 1, self.STAT_FIELDS_OPERATION_ADD)
            if tempBackTaskLogScheme[0].deleteTaskId != 0:
              self.updateStatField(self.VAR_TASKS_DELETE_TRIES, 1, self.STAT_FIELDS_OPERATION_ADD)
              self.updateStatField(self.VAR_TASKS_RETRIES_DEL, 1, self.STAT_FIELDS_OPERATION_ADD)
      if isCleanUp:
        logger.debug("onFetchTaskDataResponse cleanup income id = " + str(event.eventObj.id))
        tempBackTaskLogScheme = TaskBackLogScheme(TaskLog())
        tempBackTaskLogScheme.id = event.eventObj.id
        self.cleanUpTask([tempBackTaskLogScheme])
        # self.updateTaskBackLogToSchedulerStep(event.eventObj.id, 1, EEResponseData.TASK_STATE_SET_ERROR)
      else:
        logger.debug("onFetchTaskDataResponse rescheduler income id = " + str(event.eventObj.id))
        self.updateTaskBackLogToSchedulerStep(event.eventObj.id, 1, EEResponseData.TASK_STATE_NEW_DATA_STORED)
        operation_steps = self.createOperationSteps(event, None, True)
        self.pendingTasks[event.uid] = TaskRecord(operation_steps, None, None)
        operation_steps[0].ok_callback()
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.onFetchTaskDataResponse [" + str(err) + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #restoreTaskSteps send FETCH_TASK_DATA request to the TDM
  #
  # @param taskId - task Id
  def restoreTaskSteps(self, taskId):
    try:
      logger.debug("restoreTaskSteps id = " + str(taskId))
      fetchTaskData = FetchTaskData(taskId)
      new_event = self.eventBuilder.build(EVENT_TYPES.FETCH_TASK_DATA, fetchTaskData)
      self.send(self.TASKS_DATA_MANAGER_CLIENT, new_event)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #statFieldsRecalculate method recalculates value for :"tasks_time_avg", "tasks_time_sum",
  #  "tasks_time_count", "tasks_time_min", "tasks_time_max" statistic fields
  #
  # @param taskLogScheme instance of TaskLogScheme object
  def statFieldsRecalculate(self, taskLogScheme):
    try:
      logger.debug(">>> Start static recalculationg")
      localDict = {}
      localDict[self.VAR_TASKS_TIME_MIN] = None
      localDict = self.getStatDataFields(localDict)
      if localDict is not None and self.VAR_TASKS_TIME_MIN in localDict and localDict[self.VAR_TASKS_TIME_MIN] \
      is not None:
        if taskLogScheme.pTime < localDict[self.VAR_TASKS_TIME_MIN] or localDict[self.VAR_TASKS_TIME_MIN] == 0:
          self.updateStatField(self.VAR_TASKS_TIME_MIN, taskLogScheme.pTime, self.STAT_FIELDS_OPERATION_SET)
      localDict = {}
      localDict[self.VAR_TASKS_TIME_MAX] = None
      localDict = self.getStatDataFields(localDict)
      if localDict is not None and self.VAR_TASKS_TIME_MAX in localDict and localDict[self.VAR_TASKS_TIME_MAX] \
      is not None:
        if taskLogScheme.pTime > localDict[self.VAR_TASKS_TIME_MAX]:
          self.updateStatField(self.VAR_TASKS_TIME_MAX, taskLogScheme.pTime, self.STAT_FIELDS_OPERATION_SET)

      self.updateStatField(self.VAR_TASKS_TIME_SUM, taskLogScheme.pTime, self.STAT_FIELDS_OPERATION_ADD)
      self.updateStatField(self.VAR_TASKS_TIME_COUNT, 1, self.STAT_FIELDS_OPERATION_ADD)
      localDict = {}
      localDict[self.VAR_TASKS_TIME_SUM] = None
      localDict[self.VAR_TASKS_TIME_COUNT] = None

      localDict = self.getStatDataFields(localDict)
      if localDict is not None and self.VAR_TASKS_TIME_SUM in localDict and localDict[self.VAR_TASKS_TIME_SUM] is not \
      None and self.VAR_TASKS_TIME_COUNT in localDict and localDict[self.VAR_TASKS_TIME_COUNT] is not None:
        self.updateStatField(self.VAR_TASKS_TIME_AVG, \
        localDict[self.VAR_TASKS_TIME_SUM] / localDict[self.VAR_TASKS_TIME_COUNT], self.STAT_FIELDS_OPERATION_SET)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #made all necessary manipulations to move to no active state
  #
  # @param taskBackLogScheme instance of TaskBackLogScheme object
  def cleanUpTask(self, taskBackLogScheme):
    if taskBackLogScheme is not None and len(taskBackLogScheme) > 0:
      # pylint: disable-msg=W0212
      try:
        taskBackLogScheme[0].fDate = datetime.now()
        taskLogScheme = TaskLogScheme(taskBackLogScheme[0]._getTaskLog())
        if taskLogScheme.pTime is not None:
          self.statFieldsRecalculate(taskLogScheme)
        try:
          customQuery = "select count(*) from %s where id = '%s'" \
                                              % (str(taskLogScheme.__tablename__), str(taskLogScheme.id))
          logger.debug("!!! customQuery: %s", str(customQuery))
          customResponse = self.dbi.sqlCustom(customQuery)
          logger.debug("!!! customResponse: %s", varDump(customResponse))
          if len(customResponse) > 0 and len(customResponse[0]) > 0 and int(customResponse[0][0]) > 0:
            logger.debug("!!! taskId = %s already exist. Try delete from table.", str(taskLogScheme.id))
            self.dbi.delete(taskLogScheme, "id=%s" % taskLogScheme.id)

          self.dbi.insert(taskLogScheme)
        except DBIErr as err:
          logger.error(">>> Some DBI error in TasksManager.cleanUpTask moving backlog/log " +
                       "operation [" + str(err.message) + "]")
        self.dbi.delete(taskBackLogScheme[0], "id=%s" % taskLogScheme.id)
        # Delete task from queue
        logger.debug("Delete from tasksQueue[] item " + str(taskLogScheme.id))
        self.cleanUpTaskNetworkOperation(taskLogScheme.id, True)
        self.checkTaskPresence(taskLogScheme.id)
        del self.tasksQueue[taskLogScheme.id]
      except TaskNoPresentErr as err:
        logger.error(err.message)
      except DBIErr as err:
        logger.error(">>> Some DBI error in TasksManager.cleanUpTask [" + str(err) + "]")
      except Exception as err:
        ExceptionLog.handler(logger, err, "Exception:")
    else:
      logger.error("The input taskBackLogScheme is None or empty: " + Utils.varDump(taskBackLogScheme))


  # #method cleanups tasks data in the paraller threads/modules
  #
  # @param taskId - task's id
  # @param delFromTDMData - bool, make TDM data deleting or not
  def cleanUpTaskNetworkOperation(self, taskId, delFromTDMData):
    try:
      deleteTask = DeleteTask(0, taskId)
      if delFromTDMData:
        deleteTaskData = DeleteTaskData(taskId)
      deleteEEResponseData = DeleteEEResponseData(taskId)
      if delFromTDMData:
        new_event = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK_DATA, deleteTaskData)
        self.send(self.TASKS_DATA_MANAGER_CLIENT, new_event)
      # Delete EE Data
      new_event = self.eventBuilder.build(EVENT_TYPES.DELETE_EE_DATA, deleteEEResponseData)
      self.send(self.TASKS_DATA_MANAGER_CLIENT, new_event)
      # Delete task
      new_event = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, deleteTask)
      self.send(self.SCHEDULER_CLIENT, new_event)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #tempBackTaskLogScheme method updates 2 fields (tries, state) in BackTaskLog table
  #
  # @param taskLog incoming taskLog object
  def updateTaskBackLogToSchedulerStep(self, localId, incr, newState):
    try:
      taskLog = TaskLog()
      tempBackTaskLogScheme = self.dbi.fetch(TaskBackLogScheme(taskLog), "id=%s" % localId)
      if hasattr(tempBackTaskLogScheme, '__iter__') and len(tempBackTaskLogScheme) > 0:
        tempBackTaskLogScheme[0].tries += incr
        tempBackTaskLogScheme[0].state = newState
        self.dbi.update(tempBackTaskLogScheme[0], "id=%s" % localId)
      else:
        logger.error("Error can't fetch record from TaskBackLog with task id = " + str(localId))
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onTasksManagerGeneralResponse event handler
  #
  # @param event instance of Event object
  def onTasksManagerGeneralResponse(self, event):
    try:
      logger.debug("onTasksManagerGeneralResponse, event:" + str(event.uid) + "\n" + Utils.varDump(event))
      self.processOperationStep(event)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #function process
  #
  # @param event instance of Event object
  def processOperationStep(self, event):
    try:
      generalResponse = event.eventObj
      if event.uid in self.pendingTasks:
        if generalResponse.errorCode == GeneralResponse.ERROR_OK:
          if len(self.pendingTasks[event.uid].tasksteps) > 1:
            if event.uid in self.pendingTasks:
              logger.debug("Update pendingTasks[] item " + str(event.uid))
            else:
              logger.debug("Insert pendingTasks[] item " + str(event.uid))
            self.pendingTasks[event.uid] = TaskRecord(self.pendingTasks[event.uid].tasksteps[1:],
                                               self.pendingTasks[event.uid].event,
                                               self.pendingTasks[event.uid].responseEventType)
            self.pendingTasks[event.uid].tasksteps[0].ok_callback()
          else:
            self.replyGeneralResponse(event)
            logger.debug("Delete 1 from pendingTasks[] item " + str(event.uid))
            del self.pendingTasks[event.uid]
        else:
          if self.pendingTasks[event.uid].tasksteps[0].err_callback:
            self.pendingTasks[event.uid].tasksteps[0].err_callback()
          self.replyGeneralResponse(event)
          logger.debug("Delete 2 from pendingTasks[] item " + str(event.uid))
          del self.pendingTasks[event.uid]
      else:
        logger.debug("processOperationStepr: pending event " + str(event.uid) + "  " + str(self.pendingTasks))

    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #send GeneralResponse reply event at the end of operation queue
  # or while get err response during execution the queue
  #
  # @param event instance of Event object
  def replyGeneralResponse(self, event):
    try:
      if self.pendingTasks[event.uid].responseEventType != None:
        generalResponse = event.eventObj
        responseEvent = self.eventBuilder.build(self.pendingTasks[event.uid].responseEventType, generalResponse)
        self.reply(self.pendingTasks[event.uid].event, responseEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onFetchResultResponse event handler
  #
  # @param event instance of Event object
  def onFetchResultResponse(self, event):
    try:
      if event.uid in self.fetchEvents:
        replyEvent = self.eventBuilder.build(EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE, event.eventObj)
        self.reply(self.fetchEvents[event.uid], replyEvent)
        logger.debug("Delete from fetchEvents[] item " + str(event.uid))
        del self.fetchEvents[event.uid]
      else:
        logger.error("onFetchResultResponse no such event.uid" + str(event.uid))
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  '''
  def checkDBIState(self):
    if self.dbi.getErrorCode() != dbi_consts.DBI_SUCCESS_CODE:
      logger.debug("DBI error:" + str(self.dbi.getErrorCode()) + " : " + self.dbi.getErrorMsg())
      raise DBIErr(self.dbi.getErrorCode(), self.dbi.getErrorMsg())
  '''


  # #creates taskLog object from EventObjects.Task object
  #
  # @param taskObj instance of EventObjects.Task object
  def createTaskLog(self, taskObj):
    taskLog = TaskLog()
    taskLog.id = taskObj.id
    if "deleteTaskId" in taskObj.__dict__:
      taskLog.deleteTaskId = taskObj.deleteTaskId
    return taskLog



  # #clean up allstructures after error in dbi object
  #
  def cleanAfterDBIErr(self, event):
    try:
      deleteTaskData = DeleteTaskData(event.eventObj.id)
      deleteEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK_DATA, deleteTaskData)
      logger.debug("Delete from tasksQueue[] item " + str(event.eventObj.id))
      del self.tasksQueue[event.eventObj.id]
      self.send(self.TASKS_DATA_MANAGER_CLIENT, deleteEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #check existence task in the manager(in processing mode)
  #
  def checkTaskPresence(self, taskId):
    if not taskId in self.tasksQueue:
      raise TaskNoPresentErr("The task is not present in tasksManager id=" + str(taskId))



  # #create TaskManagerFields object from TaslLog object
  #
  # @param taskLog instance of TaskLog object
  def createTaskManagerFields(self, taskLog):
    taskManagerFields = TaskManagerFields(taskLog.id)
    attributes = [attr for attr in dir(taskLog) if not attr.startswith('__') and not attr.startswith('_')]
    for attr in attributes:
      taskManagerFields.fields[attr] = getattr(taskLog, attr, None)
    return taskManagerFields



  # #create TaslLog objects and filling properties from imput dic
  #
  # @param fields instance of dic object
  def createTaskLogFromDic(self, fields):
    taskLog = TaskLog()
    for attr in [attr for attr in dir(taskLog) if not attr.startswith('__') and not attr.startswith('_')]:
      if attr in fields:
        setattr(taskLog, attr, fields[attr])
    return taskLog



  # #set empty fields to None ("host" and "port" field now)
  #
  # @param fields instance of dic object
  def clearEmptyFields(self, fields, taskId):
    ret = fields
    try:
      lookBackTaskLogScheme = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=%s" % taskId)
      if lookBackTaskLogScheme != None and len(lookBackTaskLogScheme) > 0 and lookBackTaskLogScheme[0] != None:
        if DTM_CONSTS.DRCE_FIELDS.HOST in dir(lookBackTaskLogScheme[0]) and \
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.HOST) != None and \
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.HOST) != "":
          ret[DTM_CONSTS.DRCE_FIELDS.HOST] = None
          logger.debug(str(DTM_CONSTS.DRCE_FIELDS.HOST) + " is not empty, set to None")
        if DTM_CONSTS.DRCE_FIELDS.PORT in dir(lookBackTaskLogScheme[0]) and \
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.PORT) != None and \
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.PORT) != "":
          ret[DTM_CONSTS.DRCE_FIELDS.PORT] = None
          logger.debug(str(DTM_CONSTS.DRCE_FIELDS.PORT) + " is not empty, set to None")

        # TODO: temporary fix for wrong update state from finished to in progress or from in progress to new
        if (ret[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_IN_PROGRESS and\
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.STATE) == EEResponseData.TASK_STATE_FINISHED) or\
          (ret[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_NEW and\
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.STATE) == EEResponseData.TASK_STATE_IN_PROGRESS) or\
          (ret[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_FINISHED and\
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.STATE) == \
                  EEResponseData.TASK_STATE_SCHEDULED_TO_DELETE) or\
          (ret[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_IN_PROGRESS and\
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.STATE) == \
                  EEResponseData.TASK_STATE_SCHEDULED_TO_DELETE) or\
          (ret[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_NEW and\
          getattr(lookBackTaskLogScheme[0], DTM_CONSTS.DRCE_FIELDS.STATE) == EEResponseData.TASK_STATE_FINISHED):
          ret = {}
          # pylint: disable-msg=W0212
          logger.debug("Aborted update with wrong state value for task " + str(taskId) + "\nfields to update: " + \
                       str(fields) + "\nfields in db: " + Utils.varDump(lookBackTaskLogScheme[0]._getTaskLog()))
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.clearEmptyFields [" + str(err) + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")

    return ret



  def processTasksDataManagerFailure(self, event):
    # discuss
    logger.debug("Event: " + str(event))



  def processSchedulerFailure(self, event):
    # discuss rescheduling strategy and etc
    # pass
    logger.debug("Event: " + str(event))



  # #onDeleteTaskResponse event handler
  #
  # @param event instance of Event object
  def onDeleteTaskResponse(self, event):
    # discuss
    # pass
    logger.debug("Event: " + str(event))



  # #onFetchAvailableTasks event handler
  # fetch oldest running tasks from DB
  # @param event instance of Event object
  def onFetchAvailableTasks(self, event):
    try:
      resultList = []
      tasksList = None
      try:
        additionWhere = ""
        SELECT_TEMPLATE_STR = "SELECT %s from %s%s"
        if event.eventObj.criterions is not None:
          additionWhere = app.SQLCriterions.generateCriterionSQL(event.eventObj.criterions)

        if event.eventObj.fetchAdditionalFields:
          tasksList = []
          clause = (SELECT_TEMPLATE_STR % ('*', event.eventObj.tableName, additionWhere))
        else:
          clause = (SELECT_TEMPLATE_STR % ('`id`', event.eventObj.tableName, additionWhere))

        logger.debug(">>> Get tasks SQL == " + clause)
        results = self.dbi.sql(TaskBackLogScheme(TaskLog), clause)
        # logger.debug(self.dbi)
        if len(results) > 0:
          for record in results:
            if len(resultList) >= event.eventObj.fetchNum:
              break
            resultList.append(record.id)
            if event.eventObj.fetchAdditionalFields:
              tasksList.append(record._getTaskLog())
        else:
          logger.debug("No tasks selected for auto check state")
      except DBIErr as err:
        logger.error(">>> Some DBI error in TasksManager.onFetchAvailableTasks [" + str(err.message) + "]")
      except Exception as err:
        ExceptionLog.handler(logger, err, "Exception:")
      res = AvailableTaskIds(resultList, tasksList)
      responseEvent = self.eventBuilder.build(EVENT_TYPES.AVAILABLE_TASK_IDS_RESPONSE, res)
      self.reply(event, responseEvent)

    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #deleteOnCleanUp method creates DeleteTask object and start tasks deleting process, on autoCleanUp event
  #
  # @param taskData - incoming tasks data (fetching from kvdb)
  # @param autoCleanupFields - tasks autoCleanUp fields
  def deleteOnCleanUp(self, taskData, autoCleanupFields):
    logger.debug(">>> Start cleanup taskId=" + str(taskData.id))
    try:
      self.checkTaskPresence(taskData.id)
      deleteObj = DeleteTask(taskData.id)
      if "DeleteType" in autoCleanupFields and autoCleanupFields["DeleteType"] is not None:
        deleteObj.action = autoCleanupFields["DeleteType"]
      if "DeleteRetries" in autoCleanupFields and autoCleanupFields["DeleteRetries"] is not None:
        deleteObj.strategy["RETRY"] = autoCleanupFields["DeleteRetries"]
      delEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, deleteObj)
      self.onDeleteTask(delEvent)
      logger.debug(">>> Clear autocleanup field taskId=" + str(taskData.id))
      taskData.autoCleanupFields = None
      self.dbi.update(taskData, "id=%s" % str(taskData.id))
    except TaskNoPresentErr as err:
      logger.error(err.message)
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.deleteOnCleanUp [" + str(err) + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #checkCleanUp method check tasks on autocleanup condition
  #
  def checkCleanUp(self, taskId=None):
    logger.debug(">>> Start cleanup method id=" + str(taskId))
    try:
      suspendedTasks = self.dbi.fetch(TaskBackLogScheme(TaskLog), "id=id")
      if hasattr(suspendedTasks, '__iter__'):
        for taskData in suspendedTasks:
          if taskData is not None and taskData.autoCleanupFields is not None and str(taskData.autoCleanupFields) != "":
            autoCleanupFields = pickle.loads(str(taskData.autoCleanupFields))
            if type(autoCleanupFields) == types.DictType:
              if taskData.id == taskId and "State" in autoCleanupFields and autoCleanupFields["State"] is not None and \
              autoCleanupFields["State"] == taskData.state:
                self.deleteOnCleanUp(taskData, autoCleanupFields)
                continue
              if "TTL" in autoCleanupFields and autoCleanupFields["TTL"] is not None and \
              autoCleanupFields["TTL"] < time.time():
                self.deleteOnCleanUp(taskData, autoCleanupFields)
      else:
        logger.debug(">>> End cleanup method [Bad kvdb fetching]")
    except DBIErr as err:
      logger.error(">>> Some DBI error in TasksManager.checkCleanUp [" + str(err.message) + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #function will call every time when ConnectionTimeout exception arrive
  #
  def on_poll_timeout(self):
    localTimestamp = time.time()
    if self.prevCleanUpTime + self.cleanUpTimeout < localTimestamp:
      self.checkCleanUp()
      self.prevCleanUpTime = localTimestamp


  # Cleanup dtm tables
  def cleanupTables(self):
    logger.debug("Cleanup tables started")

    for tableName in self.CLEANUP_TABLES_LIST:
      customQuery = "DELETE FROM %s WHERE 1" % tableName
      try:
        self.dbi.session.execute(text(customQuery))
        self.dbi.session.commit()

        logger.debug("Cleanup of '%s' successfully finished", tableName)

      except sqlalchemy.exc.SQLAlchemyError, err:
        self.dbi.session.rollback()
        logger.error("Cleanup of '%s' failed. %s", tableName, str(err))
      except Exception, err:
        logger.error("Cleanup of '%s' failed. %s", tableName, str(err))

    logger.debug("Cleanup tables finished")
