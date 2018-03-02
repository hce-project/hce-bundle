'''
@package: dtm
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import time
import datetime
import logging
import math
#import pickle
try:
  import cPickle as pickle
except ImportError:
  import pickle
from sqlalchemy.exc import  SQLAlchemyError

from app.BaseServerManager import BaseServerManager
from dbi.dbi import DBI
from dbi.dbi import DBIErr
from dtm.EventObjects import DeleteTask

from Constants import EVENT_TYPES
from EventObjects import ScheduledTask, GeneralResponse, Task, NewTask, GetScheduledTasksResponse, UpdateTaskFields
from EventObjects import EEResponseData
from SchedulerTask import SchedulerTask
from SchedulerTaskScheme import SchedulerTaskScheme
from TaskLog import TaskLog
from TaskBackLogScheme import TaskBackLogScheme
import dbi.dbi as row_dbi
import transport.Consts as consts
import dtm.Constants as DTM_CONSTS

##@todo starnge thing
#logger = logging.getLogger(__name__)
logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)

##Class is used to inform about logic error
#
#
class LogicErr(Exception):
  ERR_CODE = 1101

  def __init__(self, errCode, message):
    self.errCode = errCode
    Exception.__init__(self, message)



##The Scheduler object implements algorithms of tasks scheduling
#
class Scheduler(BaseServerManager):

  #@todo move to suitable place
  #operations errors
  OPERATION_ERR = 1024
  OPERATION_ERR_MSG = "Previous task operations is not finished"

  RESOURCES_EXCEED_ERR = 1025
  RESOURCES_EXCEED_ERR_MSG = "Resources are exceed"

  #Configuration settings options names
  SERVER = "server"
  RESOURCES_MANAGER_CLIENT = "clientResourcesManager"
  CLIENT_INTERFACE_SERVICE_CLIENT = "clientClientInterfaceService"
  TIME_SLOT_PERIOD = "timeSlotPeriod"
  MAX_TASKS = "maxTasksPerTimeSlot"


  ##constructor
  #initialise all connections and event handlers
  #
  def __init__(self, configParser, connectBuilderLight, pollerManager=None):
    super(Scheduler, self).__init__(pollerManager)

    self.cfg_section = self.__class__.__name__
    self.tasksToUpdate = list()

    serverAddr = configParser.get(self.cfg_section, self.SERVER)
    resourcesManagerAddr = configParser.get(self.cfg_section, self.RESOURCES_MANAGER_CLIENT)
    clientInterfaceServiceAddr = configParser.get(self.cfg_section, self.CLIENT_INTERFACE_SERVICE_CLIENT)
    self.maxTasks = int(configParser.get(self.cfg_section, self.MAX_TASKS))

    ##@var timeSlot
    #value of the timeSlot used in scheduling tasks
    self.timeSlot = int(configParser.get(self.cfg_section, self.TIME_SLOT_PERIOD))

    serverConnection = connectBuilderLight.build(consts.SERVER_CONNECT, serverAddr)
    resourcesManagerConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, resourcesManagerAddr)
    clientInterfaceServiceConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, clientInterfaceServiceAddr,
                                                                 real_connect=False)

    self.addConnection(self.SERVER, serverConnection)
    self.addConnection(self.RESOURCES_MANAGER_CLIENT, resourcesManagerConnection)
    self.addConnection(self.CLIENT_INTERFACE_SERVICE_CLIENT, clientInterfaceServiceConnection)

    #TasksManager events
    self.setEventHandler(EVENT_TYPES.SCHEDULE_TASK, self.onNewTask)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK, self.onUpdateTask)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK, self.onDeleteTask)
    self.setEventHandler(EVENT_TYPES.GET_SCHEDULED_TASKS, self.onGetSheduledTasks)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK_FIELDS_RESPONSE, self.onUpdateTaskFieldsResponse)

    #ResourcesManager
    self.setEventHandler(EVENT_TYPES.GET_AVG_RESOURCES_RESPONSE, self.onAVGResourcesResponse)

    ##@var waitResourcsEvent
    #map of events pending scheduling to get resources for this tasks
    #event.uid => event
    self.waitResourcesEvents = dict()

    ##@var waitResourcsTask
    #map of tasks pending scheduling to get resources for this tasks
    #task.id => True
    self.waitResourcesTasks = dict()

    ##@var dbi
    # db contains schedule table
    self.dbi = DBI(self.createDBIDict(configParser))

    isClearOnStart = configParser.get(self.cfg_section, DTM_CONSTS.CLEAR_ON_START)
    if isClearOnStart == "True":
      schedulerTask = SchedulerTask()
      schedulerTask.state = ScheduledTask.STATE_CLOSED
      try:
        self.dbi.update(SchedulerTaskScheme(schedulerTask), "id=id")
      except DBIErr as err:
        logger.error(">>> Some DBI error in Scheduler.__init__ [" + str(err) + "]")


  ##create dict config (dict object)
  #
  def createDBIDict(self, configParser):
    #get section
    return dict(configParser.items(DTM_CONSTS.DB_CONFIG_SECTION))


  ##onNewTask event handler
  #
  #@param event instance of Event object
  def onNewTask(self, event):
    task = event.eventObj
    try:
      response = GeneralResponse()
      if "DATE" in task.session:
        response = self.planTaskTimeToRun(task)
      else:
        self.checkCorrectTaskType(task)
        self.modifyTaskInSchedule(task)
        self.reschedulingTasks()

    except (DBIErr, LogicErr) as err:
      logger.error(">>> Some DBI error in Scheduler.onNewTask [" + str(err.message) + "]")
      response = GeneralResponse(err.errCode, err.message)
    except Exception, err:
      logger.error("Exception: %s", str(err))
    finally:
      responseEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK_RESPONSE , response)
      self.reply(event, responseEvent)



  #@todo for testing purpose
  def planTaskTimeToRun(self, task):
    # variable for result
    response = GeneralResponse()
    try:
      if "DATE" in task.session: # @todo only for test
        date_string = task.session["DATE"]
        plannedTime = self.getPlannedRunTime(date_string)
        leftBorderMs = int(math.floor(plannedTime / self.timeSlot)) * self.timeSlot
        rightBorderMs = leftBorderMs + self.timeSlot

        scheme = SchedulerTaskScheme(SchedulerTask())
        taskInSlotNumber = len(row_dbi.db.session.query(type(scheme)).filter(type(scheme).rTime <= rightBorderMs).\
        filter(type(scheme).rTime >= leftBorderMs).filter_by(state=ScheduledTask.STATE_PLANNED).all())
        logger.debug("taskInSlotNumber=" + str(taskInSlotNumber))

        #@todo add more complex condition for planning
        task.rtime = plannedTime
        self.modifyTaskInSchedule(task)

    except DBIErr as err:
      logger.error(">>> Some DBI error in Scheduler.planTaskTimeToRun [" + str(err) + "]")
      response = GeneralResponse(err.errCode, err.message)
    except Exception, err:
      logger.error("Exception: %s", str(err))
      response = GeneralResponse(errorMessage=str(err))

    return response


  ##onUpdateTask event handler
  #
  #@param event instance of Event object
  def onUpdateTask(self, event):
    try:
      updateTask = event.eventObj
      if updateTask.id not in self.waitResourcesTasks:
        self.onNewTask(event)
      else:
        self.sendOperationProcessingError(event)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##onDeleteTask event handler
  #
  #@param event instance of Event object
  def onDeleteTask(self, event):
    try:
      deleteTask = event.eventObj
      if deleteTask.id not in self.waitResourcesTasks:
        try:
          response = GeneralResponse()
          self.deleteTaskFromSchedule(deleteTask)
          self.reschedulingTasks()
        except DBIErr as err:
          logger.error(">>> Some DBI error in Scheduler.__init__ [" + str(err.message) + "]")
          response = GeneralResponse(err.errCode, err.message)
        except Exception, err:
          logger.error("Exception: %s", str(err))
          response = GeneralResponse(errorMessage=str(err))
        finally:
          responseEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK_RESPONSE , response)
          self.reply(event, responseEvent)
      else:
        self.sendOperationProcessingError(event)

    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##onGetSheduledTasks event handler
  #
  #@param event instance of Event object
  def onGetSheduledTasks(self, event):
    try:
      # get the current resources state
      self.addPendingEvent(event)
      getAVGResourcesEvent = self.eventBuilder.build(EVENT_TYPES.GET_AVG_RESOURCES, None)

      getAVGResourcesEvent.uid = event.uid
      self.send(self.RESOURCES_MANAGER_CLIENT, getAVGResourcesEvent)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##onAVGResourcesResponse event handler
  #
  #@param event instance of Event object
  def onAVGResourcesResponse(self, event):
    #get response on event sending in onGetSheduledTasks
    resourcesAVG = event.eventObj
    if event.uid in self.waitResourcesEvents:
      try:
        getScheduledTasks = self.waitResourcesEvents[event.uid].eventObj
        ids = list()

        #@todo add correct select condition
        scheduledTimeSlot = getScheduledTasks.timeSlot
        #get right border of current time slot
        curTime = self.getTimeSinceEpoch(datetime.datetime.now())
        rightBorderMs = int(math.floor(curTime / scheduledTimeSlot)) * scheduledTimeSlot + scheduledTimeSlot
        clause = "SELECT * FROM scheduler_task_scheme WHERE rTime < " + str(rightBorderMs) + " AND state=" + \
                 str(ScheduledTask.STATE_PLANNED) + " ORDER BY rTime ASC, priority DESC, tries DESC"
        if self.maxTasks > 0:
          clause = clause + " LIMIT " + str(self.maxTasks)
        scheme = SchedulerTaskScheme(SchedulerTask())
        taskSchemes = self.dbi.sql(scheme, clause)
        if hasattr(taskSchemes, '__iter__'):
          for taskScheme in taskSchemes:
            # pylint: disable-msg=W0212
            schedulerTask = taskScheme._getSchedulerTask()
            if schedulerTask.rTime > 0:
              rt = datetime.datetime.utcfromtimestamp(schedulerTask.rTime / 1000)
              rb = datetime.datetime.utcfromtimestamp(rightBorderMs / 1000)
              ct = datetime.datetime.utcfromtimestamp(curTime / 1000)
              logger.debug("Task " + str(schedulerTask.id) + " selected by rTime=" + str(rt) + \
                           ", rborder=" + str(rb) + ", now=" + str(ct))
            task_strategy = pickle.loads(str(schedulerTask.strategy))
            if self.isPossibleToRun(resourcesAVG, task_strategy):
              ids.append(schedulerTask.id)
              schedulerTask.state = ScheduledTask.STATE_INPROGRESS
              self.dbi.update(SchedulerTaskScheme(schedulerTask), "id=%s" % str(schedulerTask.id))
            else:
              logger.debug("Run isn't possible id=%s tries=%s", str(schedulerTask.id), str(schedulerTask.tries))
              schedulerTask.tries += 1
              schedulerTask.state = self.stateRecalculate(task_strategy, schedulerTask)
              if schedulerTask.state == ScheduledTask.STATE_CLOSED or \
                (Task.STRATEGY_SDELAY in task_strategy and task_strategy[Task.STRATEGY_RDELAY] == 0):
                self.tasksToUpdate.append(schedulerTask)
              else:
                schedulerTask.rTime = self.rTimeCalc(schedulerTask, task_strategy, True)
              self.dbi.update(SchedulerTaskScheme(schedulerTask), "id=%s" % str(schedulerTask.id))

              # update tries count in 'task_back_log_scheme' table
              taskLog = TaskBackLogScheme(TaskLog())._getTaskLog()
              taskLog.id = schedulerTask.id
              taskLog.tries = schedulerTask.tries
              self.dbi.update(TaskBackLogScheme(taskLog), "id=%s" % str(taskLog.id))
              #@todo maybe need some state for task isn't selected on execution
          if self.maxTasks > 0 and len(taskSchemes) == self.maxTasks:
            logger.debug(">>> Scheduled tasks limit reached LIMIT = " + str(self.maxTasks))

        getScheduledTasksResponse = GetScheduledTasksResponse(ids)
        responseEvent = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE , getScheduledTasksResponse)
        self.reply(self.waitResourcesEvents[event.uid], responseEvent)
        self.deletePendingEvent(event)
        self.taskUpdateProcess()

      except SQLAlchemyError as err:
        logger.critical(str(err))
        row_dbi.db.session.rollback()  # pylint: disable-all
      except DBIErr as err:
        logger.critical(">>> Some DBI error in Scheduler.onAVGResourcesResponse [" + str(err) + "]")
      except Exception, err:
        logger.error("Exception: %s", str(err))
    else:
      logger.error("get resourceAVG for non exist event " + str(event.uid))


  ##method handler for DeleteTskResponse event
  #
  def onUpdateTaskFieldsResponse(self, event):  # pylint: disable=W0613
    try:
      logger.debug("Task send update response, tasks len = " + str(len(self.tasksToUpdate)))
      if len(self.tasksToUpdate) > 0:
        del self.tasksToUpdate[0]
        self.taskUpdateProcess()
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##method start task delete process
  #
  #@param idsToDelete list tasks for deleting
  def taskUpdateProcess(self):
    try:
      if len(self.tasksToUpdate) > 0:
        updateTaskFields = UpdateTaskFields(self.tasksToUpdate[0].id)
        updateTaskFields.fields["state"] = EEResponseData.TASK_STATE_SCHEDULE_TRIES_EXCEEDED
        event = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK_FIELDS, updateTaskFields)
        self.send(self.CLIENT_INTERFACE_SERVICE_CLIENT, event)
        logger.debug("Task send to update id = " + str(self.tasksToUpdate[0].id))
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##method recalculates new value of rTime field
  #
  #@param schedulerTask incoming schedulerTask
  #@param task_strategy incoming strategy dict
  def rTimeCalc(self, schedulerTask, task_strategy, replanned):
    try:
      logger.debug("Old rTime=" + str(datetime.datetime.utcfromtimestamp(schedulerTask.rTime / 1000)))

      # Get NOW time
      ret = self.getTimeSinceEpoch()
      # logger.debug("Now time=" + str(datetime.datetime.utcfromtimestamp(ret / 1000)))
      if replanned:
        if Task.STRATEGY_RDELAY in task_strategy and int(task_strategy[Task.STRATEGY_RDELAY]) > 0:
          ret += int(task_strategy[Task.STRATEGY_RDELAY])
          logger.debug("New (RDELAY) rTime=" + str(datetime.datetime.utcfromtimestamp(ret / 1000)))
      else:
        if Task.STRATEGY_SDELAY in task_strategy and int(task_strategy[Task.STRATEGY_SDELAY]) > 0:
          ret += int(task_strategy[Task.STRATEGY_SDELAY])
          logger.debug("New (SDELAY) rTime=" + str(datetime.datetime.utcfromtimestamp(ret / 1000)))

      '''
      if Task.STRATEGY_RDELAY in task_strategy and int(task_strategy[Task.STRATEGY_RDELAY]) > 0:
        ret += int(task_strategy[Task.STRATEGY_RDELAY])
        logger.debug("New rTime=" + str(datetime.datetime.utcfromtimestamp(ret / 1000)))
      '''
    except Exception, err:
      logger.error("Exception: %s", str(err))

    return ret


  ##add pending event in all  auxiliary structures
  #
  #@param event instance of Event object
  def addPendingEvent(self, event):
    #task = event.eventObj
    #self.waitResourcesTasks[task.id] = True
    self.waitResourcesEvents[event.uid] = event


  ##delete pending event from all  auxiliary structures
  #
  #@param event instance of Event object
  def deletePendingEvent(self, event):
    #taskId = self.waitResourcesEvents[event.uid].eventObj.id
    #del self.waitResourcesTasks[taskId]
    del self.waitResourcesEvents[event.uid]


  ##recalcutes state field
  #
  #@param task_strategy task's strategies
  #@param schedulerTask task object
  def stateRecalculate(self, task_strategy, schedulerTask):
    ret = schedulerTask.state
    if Task.STRATEGY_RETRY in task_strategy and task_strategy[Task.STRATEGY_RETRY] <= schedulerTask.tries:
      ret = ScheduledTask.STATE_CLOSED
    return ret


  ##send operation processing error
  #
  #@param event instance of Event object
  def sendOperationProcessingError(self, event):
    try:
      response = GeneralResponse(self.OPERATION_ERR, self.OPERATION_ERR_MSG)
      responseEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK_RESPONSE , response)
      self.reply(event, responseEvent)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##delete task from schedule
  #
  #@param deleteTask instance of DeleteTask object
  def deleteTaskFromSchedule(self, deleteTask, schedulerTask=None):
    try:
      if schedulerTask == None:
        schedulerTask = SchedulerTask()
        schedulerTask.id = deleteTask.id
      self.dbi.delete(SchedulerTaskScheme(schedulerTask), "id=%s" % deleteTask.id)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##rescheduling schedule after all changes in schedule
  #
  def reschedulingTasks(self):
    #@todo implement strategy
    pass


  ## add task in schedule
  #
  #@param task instance of Task object
  def modifyTaskInSchedule(self, task):
    try:
      schedulerTask = SchedulerTask()
      schedulerTask.id = task.id
      schedulerTask.state = ScheduledTask.STATE_PLANNED
      schedulerTask.strategy = pickle.dumps(task.strategy)

      if hasattr(task, "rtime"): # @todo only for tests
        schedulerTask.rTime = task.rtime
      else:
        schedulerTask.rTime = self.rTimeCalc(schedulerTask, task.strategy, False)

      priority = 0
      if Task.STRATEGY_PRIORITY in task.strategy:
        priority = task.strategy[Task.STRATEGY_PRIORITY]
      schedulerTask.priority = priority
      if isinstance(task, (NewTask, DeleteTask)):
        self.dbi.insert(SchedulerTaskScheme(schedulerTask))
      else:
        self.dbi.update(SchedulerTaskScheme(schedulerTask), "id = %s" % schedulerTask.id)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##check that logic of requred operation corresponds with schedule state
  #prevent wrong operation(update absent task, insert the same task)
  #
  #@param task instance of Task inheritor
  def checkCorrectTaskType(self, task):
    result = self.dbi.fetch(SchedulerTaskScheme(SchedulerTask()), "id = %s" % task.id)
    if isinstance(task, (NewTask, DeleteTask)):
      if len(result) > 0:
        raise LogicErr(LogicErr.ERR_CODE, "Task is already in schedule")
    else:
      if len(result) == 0:
        raise LogicErr(LogicErr.ERR_CODE, "Task is wrong type:" + str(type(task)))


  ##Check is task possible to run by comparison of required limits and actual resources
  #
  #@param resourcesAVG instance of ResourcesAVG object
  #@param task instance of Task object
  #@return True if actual resource >=  required
  def isPossibleToRun(self, resourcesAVG, task_strategy):
    ret = True
    if ret and "CPU" in task_strategy and resourcesAVG.cpuCores > 0:
      if (resourcesAVG.threads / resourcesAVG.cpuCores) <= task_strategy["CPU"]:
        logger.error("CPU limit %s %s", str(resourcesAVG.threads / resourcesAVG.cpuCores),
                     str(task_strategy["CPU"]))
        ret = False

    if ret and "CPU_LOAD_MAX" in task_strategy:
      if resourcesAVG.cpu >= task_strategy["CPU_LOAD_MAX"]:
        logger.error("CPU_LOAD_MAX limit %s %s", str(resourcesAVG.cpu), str(task_strategy["CPU_LOAD_MAX"]))
        ret = False

    if ret and "IO_WAIT_MAX" in task_strategy:
      if resourcesAVG.io > task_strategy["IO_WAIT_MAX"]:
        logger.error("IO_WAIT_MAX limit %s %s", str(resourcesAVG.io), str(task_strategy["IO_WAIT_MAX"]))
        ret = False

    if ret and "RAM_FREE" in task_strategy:
      #logger.debug("FREE RAM: %s, LIMIT %s", str(resourcesAVG.ramR - resourcesAVG.ramRU), str(task_strategy["RAM_FREE"]))
      if resourcesAVG.ramR > 0 and resourcesAVG.ramRU > 0 and \
      (resourcesAVG.ramR - resourcesAVG.ramRU) < task_strategy["RAM_FREE"]:
        logger.error("RAM_FREE limit %s < %s", str(resourcesAVG.ramR - resourcesAVG.ramRU),
                     str(task_strategy["RAM_FREE"]))
        ret = False

    return ret


  ##get time since epoch in millisec
  #
  #@return numeric
  def getTimeSinceEpoch(self, date=None):
    if date is None:
      date = datetime.datetime.now()
    epoch = datetime.datetime.utcfromtimestamp(0)  #@todo move to init
    delta = date - epoch  #datetime.datetime.now() - epoch
    return int(((delta.days * 24 * 60 * 60 + delta.seconds) * 1000 + delta.microseconds / 1000.0))


  ##get planned run time
  #
  #@param date_string sting contains data in strict format
  #@return numeric
  def getPlannedRunTime(self, date_string):
    planed_time = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S,%f")
    return self.getTimeSinceEpoch(planed_time)

