'''
HCE project, Python bindings, Distributed Tasks Manager application.
TasksStateUpdateService object and related classes definitions.
This object acts as listener of updates of tasks states inside DRCE Execution Environment.
The DRCE Functional objects callback connects to this service and send update message when task changes its state.
This call initiated by DRCE node FO watchdog.


@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


from datetime import datetime
import logging
import time
from app.BaseServerManager import BaseServerManager
from app.LogFormatter import LogFormatterEvent
from drce.CommandConvertor import CommandConvertor
from transport.Connection import ConnectionParams
from transport.ConnectionBuilder import ConnectionBuilder
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.IDGenerator import IDGenerator
from transport.Response import Response
from transport.UIDGenerator import UIDGenerator
import app.Utils as Utils  # pylint: disable=F0401
import dtm.EventObjects
import app.SQLCriterions

import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS

#Logger initialization
#logger = logging.getLogger(__name__)
logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)


##The TasksStateUpdateService class, is a listener of tasks state updates from DRCE FO of cluster nodes.
#
#TasksStateUpdateService object and related classes definitions.
#This object acts as listener of updates of tasks states inside DRCE Execution Environment.
#The DRCE Functional objects callback connects to this service and send update message when task changes its state.
#This call initiated by DRCE node FO watchdog.
#
class TasksStateUpdateService(BaseServerManager):

  #Configuration settings options names
  CONFIG_SERVER_HOST = "serverHost"
  CONFIG_SERVER_PORT = "serverPort"
  CONFIG_TASKS_MANAGER_CLIENT = "clientTasksManager"
  CONFIG_EE_MANAGER = "clientExecutionEnvironmentManager"
  CONFIG_CHECK_STATE_NUM = "checkStateNum"
  CONFIG_CHECK_STATE_INTERVAL = "checkStateInterval"
  CONFIG_FETCH_TASK_NUM = "checkStateTasks"

  ERROR_HCE_RESPONSE_PROCESSING_EXCEPTION = "Update request error, possible wrong json format!"
  ERROR_TASK_FIELDS_UPDATE = "Update of task fields response error."

  UPDATE_TYPE_TASK_STATE = 100
  UPDATE_TYPE_RESOURCES_STATE = 101

  ##constructor
  #initialize fields
  #
  #@param configParser config parser object
  #@param connectBuilderLight network transport connection builder light
  #@param connectionBuilder network transport connection builder
  def __init__(self, configParser, connectionBuilderLight=None, connectionBuilder=None):
    super(TasksStateUpdateService, self).__init__()
    self.expect_response = Response(["sock_identity", "id", "body"])

    #Instantiate the connection builder light if not set
    if connectionBuilderLight is None:
      connectionBuilderLight = ConnectionBuilderLight()
    #Instantiate the connection builder if not set
    if connectionBuilder is None:
      connectionBuilder = ConnectionBuilder(IDGenerator())

    className = self.__class__.__name__

    #Get configuration settings
    self.clientTasksManagerName = configParser.get(className, self.CONFIG_TASKS_MANAGER_CLIENT)
    self.serverHost = configParser.get(className, self.CONFIG_SERVER_HOST)
    self.serverPort = configParser.get(className, self.CONFIG_SERVER_PORT)
    self.clientExecutionEnvironmentManager = configParser.get(className, self.CONFIG_EE_MANAGER)

    #Create connections and raise bind or connect actions for correspondent connection type
    tasksManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT, self.clientTasksManagerName)
    tcpServerConnection = connectionBuilder.build(TRANSPORT_CONSTS.DATA_CONNECT_TYPE,
                                                  ConnectionParams(self.serverHost, self.serverPort),
                                                  TRANSPORT_CONSTS.SERVER_CONNECT)
    eeManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT,
                                                       self.clientExecutionEnvironmentManager)

    #Add connections to the polling set
    self.addConnection(self.clientTasksManagerName, tasksManagerConnection)
    self.addConnection(self.serverHost, tcpServerConnection)
    self.addConnection(self.clientExecutionEnvironmentManager, eeManagerConnection)

    #Set event handler for EXECUTE_TASK event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.UPDATE_TASK_FIELDS_RESPONSE, self.onUpdateTaskFieldsResponse)
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.SERVER_TCP_RAW, self.onTCPServerRequest)
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.AVAILABLE_TASK_IDS_RESPONSE, self.onReceiveAllTaskIds)

    #Initialize unique Id generator
    self.drceIdGenerator = UIDGenerator()
    #Initialize DRCE commands convertor
    self.drceCommandConvertor = CommandConvertor()

    #variables for auto send CheckState to EEManager
    ##@var lastCheckStateTs
    # timestamp of last send CheckState request
    self.lastCheckStateTs = 0
    self.checkStateInterval = configParser.getint(className, self.CONFIG_CHECK_STATE_INTERVAL)
    self.checkStateNum = configParser.getint(className, self.CONFIG_CHECK_STATE_NUM)
    self.fetchTaskNum = configParser.getint(className, self.CONFIG_FETCH_TASK_NUM)

    # Set connections poll timeout, defines period of tasks state checks
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = \
                   configParser.getint(className, self.POLL_TIMEOUT_CONFIG_VAR_NAME)

    ##@var taskIdsForCheckState
    #list of task ids for check state
    self.taskIdsForCheckState = []

    logger.debug("Construction finished!")



  ##onUpdateTaskFieldsResponse event handler
  #
  #@param event instance of Event object
  def onUpdateTaskFieldsResponse(self, event):
    #Get task Id from event
    generalResponse = event.eventObj
    #Log error
    if generalResponse.errorCode != dtm.EventObjects.GeneralResponse.ERROR_OK:
      logger.error(LogFormatterEvent(event, [], self.ERROR_TASK_FIELDS_UPDATE))

    logger.debug("Update tasks state response finished!")



  ##onTCPServerRequest handler of TCP server requests. Requests done by DRCE FO clients and send task state update,
  #according with DRCE FO response protocol specification
  #
  #@param event instance of Event object
  def onTCPServerRequest(self, event):
    logger.debug("Update request received!")

    #Get request raw buffer from eventObj and convert if to the DRCE response object
    rawDRCEJsonResponse = event.eventObj.get_body()
    try:
      #Convert DRCE jason protocol response to TaskResponse object
      taskResponse = self.drceCommandConvertor.from_json(rawDRCEJsonResponse)
      logger.debug("rawDRCEJsonResponse:\n" + str(rawDRCEJsonResponse) + "\nObject:\n" + Utils.varDump(taskResponse))
      #Update task data on TasksManager object
      self.processUpdateTaskFields(taskResponse)
    except Exception, e:
      logger.error(self.ERROR_HCE_RESPONSE_PROCESSING_EXCEPTION + " : " + str(e.message) + " : \n" + \
                   rawDRCEJsonResponse)

    logger.debug("TCP update request processing finished!")



  ##onReceiveAllTaskIds handler for receive running tasks from TasksManager
  #
  #@param event instance of Event object
  def onReceiveAllTaskIds(self, event):
    logger.debug("Available tasks list from TasksManager received, items " + str(len(event.eventObj.ids)))
    self.taskIdsForCheckState += event.eventObj.ids
    if len(self.taskIdsForCheckState) > 0:
      self.tryCheckTasksState()



  ##on_poll_timeout handler, now just send CheckState to EEManager
  def on_poll_timeout(self):
    logger.debug("Possible time to check state of tasks, interval " + str(self.checkStateInterval) + "!")
    if time.time() - self.lastCheckStateTs > self.checkStateInterval:
      logger.debug("Now time to check state of tasks, interval " + str(self.checkStateInterval) + "!")
      self.lastCheckStateTs = time.time()
      self.tryCheckTasksState()



  ##send CheckState message to EEManager
  #if don't have cached task id, then fetch from TasksManager
  def tryCheckTasksState(self):
    if self.taskIdsForCheckState:
      logger.debug("Tasks to check " + str(len(self.taskIdsForCheckState)))
      for taskId in self.taskIdsForCheckState[:self.checkStateNum]:
        req = dtm.EventObjects.CheckTaskState(taskId)
        event = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE, req)
        event.cookie = self.__class__.__name__
        self.send(self.clientExecutionEnvironmentManager, event)
        logger.debug("Task " + str(taskId) + " sent to check state to EEManager")
      self.taskIdsForCheckState = self.taskIdsForCheckState[self.checkStateNum:]
    else:
      logger.debug("Get available tasks list from TasksManager")
      req = dtm.EventObjects.FetchAvailabelTaskIds(self.fetchTaskNum)
      if req.criterions is not None:
        req.criterions[app.SQLCriterions.CRITERION_WHERE] = "deleteTaskId = 0 AND state < 100"
      event = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS, req)
      self.send(self.clientTasksManagerName, event)



  ##Send UpdateTasksData event to the TasksManager
  #
  #@param taskResponse The DRCE response data object
  def processUpdateTaskFields(self, taskResponse):
    #taskResponse is an instance of drce.Commands.TaskResponse
    #it may contains 0 or many response items
    if len(taskResponse.items) == 0:
      logger.error("Received empty update request from drce node!")
    else:
      # Tasks state update notification
      for resItem in taskResponse.items:
        # If no errors in response from EE
        # TODO: strange, in case of error still continue to use resItem object...
        if resItem.error_code != dtm.EventObjects.EEResponseData.ERROR_CODE_OK:
          logger.error("Update request item from node %s, error: %s :%s",
                       resItem.node, resItem.error_code, resItem.error_message)
        # Update task's fields object for the TasksManager
        updateTaskFields = dtm.EventObjects.UpdateTaskFields(resItem.id)
        # Fill fields to update
        updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST] = resItem.host
        updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT] = resItem.port

        if resItem.type == self.UPDATE_TYPE_RESOURCES_STATE:
          # Resources state update notification, the "state" field possible is not valid
          logger.debug("Resources state update notification")
          updateTaskFields.fields["state"] = None
        else:
          # Task state update notification, the "state" field is valid
          logger.debug("Task state update notification")
          updateTaskFields.fields["state"] = resItem.state

        updateTaskFields.fields["pId"] = resItem.pid
        updateTaskFields.fields["nodeName"] = resItem.node
        updateTaskFields.fields["pTime"] = resItem.time
        if resItem.state == dtm.EventObjects.EEResponseData.TASK_STATE_NEW:
          updateTaskFields.fields["rDate"] = datetime.now()
        else:
          if resItem.state == dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED:
            updateTaskFields.fields["fDate"] = datetime.now()
        #Fix due the TasksManager does not recognize UNDEFINED or TERMINATED state
        if resItem.state == dtm.EventObjects.EEResponseData.TASK_STATE_UNDEFINED or\
           resItem.state == dtm.EventObjects.EEResponseData.TASK_STATE_TERMINATED:
          updateTaskFields.fields["state"] = dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED

        if DTM_CONSTS.DRCE_FIELDS.URRAM in resItem.fields:
          updateTaskFields.fields["uRRAM"] = resItem.fields[DTM_CONSTS.DRCE_FIELDS.URRAM]
        if DTM_CONSTS.DRCE_FIELDS.UVRAM in resItem.fields:
          updateTaskFields.fields["uVRAM"] = resItem.fields[DTM_CONSTS.DRCE_FIELDS.UVRAM]
        if DTM_CONSTS.DRCE_FIELDS.UCPU in resItem.fields:
          updateTaskFields.fields["uCPU"] = resItem.fields[DTM_CONSTS.DRCE_FIELDS.UCPU]
        if DTM_CONSTS.DRCE_FIELDS.UTHREADS in resItem.fields:
          updateTaskFields.fields["uThreads"] = resItem.fields[DTM_CONSTS.DRCE_FIELDS.UTHREADS]

        #Create update event
        updateTaskFieldsEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.UPDATE_TASK_FIELDS, updateTaskFields)
        #Send update event to TasksManager
        self.send(self.clientTasksManagerName, updateTaskFieldsEvent)
        logger.debug("Update TasksManager fields for task " + str(resItem.id) + " finished!")

    logger.debug("Update TasksManager fields for all tasks finished!")
