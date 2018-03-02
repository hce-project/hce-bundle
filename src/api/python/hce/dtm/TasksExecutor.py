"""@package docstring
 @file TasksExecutor.py
 @author Oleksii <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""


import logging
import time

from app.BaseServerManager import BaseServerManager

from EventObjects import ExecuteTask
from EventObjects import GetScheduledTasks
import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS


#constant's section
CONFIG_SECTION = "TasksExecutor"


#Logger initialization
logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)
#logger = logging.getLogger("aspen")

##The Tasks Executor object
# Main job of this object is a selection of scheduled tasks
# from the schedule and send them to the ExecutionEnvironmentManager
# object to set them to the Execution Environment for execution
class TasksExecutor(BaseServerManager):

  CONFIG_TIME_SLOT_PERIOD = "timeSlotPeriod"
  STAT_SUSPEND_STATE = "suspendState"

  ##destructor
  #just in case
  #
  def __del__(self):
    pass


  ##constructor
  #initialise all connections and event handlers
  #
  def __init__(self, configParser, connectBuilderLight):
    # create clients
    super(TasksExecutor, self).__init__()

    # create clients
    executionEnvironmentManager = configParser.get(CONFIG_SECTION, "ExecutionEnvironmentManager")
    scheduler = configParser.get(CONFIG_SECTION, "Scheduler")

    # create client's connections
    executionEnvironmentManagerConnection = connectBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT,
                                                                      executionEnvironmentManager)
    schedulerConnection = connectBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT, scheduler)

    # create client's names
    self.executionEnvironmentManager = "executionEnvironmentManager"
    self.scheduler = "scheduler"

    # create connects
    self.addConnection(self.executionEnvironmentManager, executionEnvironmentManagerConnection)
    self.addConnection(self.scheduler, schedulerConnection)

    # create event handlers
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE, self.onSchedulerRoute)

    # I don't know what it is
    self.processEvents = dict()

    # get time slot period
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(CONFIG_SECTION,
                                                                             self.CONFIG_TIME_SLOT_PERIOD)

    # flag
    self.isReqSended = True

    self.old = None

    self.statFields[self.STAT_SUSPEND_STATE] = False


  ##handler to route all event to TaksManager
  #
  #@param even instance of Event object
  def onSchedulerRoute(self, event):
    scheduledTasks = event.eventObj
    for scheduledTask in scheduledTasks.ids:
      executeTask = ExecuteTask(scheduledTask)
      eem_event = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.EXECUTE_TASK, executeTask)
      self.send(self.executionEnvironmentManager, eem_event)
    # set flag to send requests to the scheduler
    diff = time.clock() - self.old
    delay = diff % self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME]
    time.sleep(delay / 1000.0)  # adjust delay in milliseconds
    self.isReqSended = True


  ##function will call every time when ConnectionTimeout exception arrive
  #
  def on_poll_timeout(self):
    # request has not been sent yet
    if not self.statFields[self.STAT_SUSPEND_STATE]:
      if self.isReqSended:
        self.old = time.clock()
        getScheduledTasks = GetScheduledTasks(self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME])
        scheduled_event = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.GET_SCHEDULED_TASKS, getScheduledTasks)
        self.send(self.scheduler, scheduled_event)
        self.isReqSended = False
      # request already has not been sent
      else:
        pass


  ##onAdminState event handler
  #process admin command
  #
  #@param event instance of Event object
  def onAdminSuspend(self, event):
    if event.eventObj is not None:
      self.statFields[self.STAT_SUSPEND_STATE] = event.eventObj.isSuspend()
    super(TasksExecutor, self).onAdminSuspend(event)
