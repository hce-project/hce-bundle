'''
HCE project, Python bindings, Distributed Tasks Manager application.
ExecutionEnvironmentManager object and related classes definitions.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


from datetime import datetime
import logging

import admin.NodeManagerRequest
from app.BaseServerManager import BaseServerManager
from app.LogFormatter import LogFormatterEvent
from drce.CommandConvertor import CommandConvertor
from drce.Commands import Session
from drce.Commands import TaskCheckRequest
from drce.Commands import TaskExecuteRequest
from drce.Commands import TaskExecuteStruct
from drce.Commands import TaskGetDataRequest
from drce.Commands import TaskTerminateRequest
from drce.Commands import TaskDeleteRequest
from drce.DRCEManager import ConnectionTimeout, TransportInternalErr, CommandExecutorErr
from drce.DRCEManager import DRCEManager
from drce.DRCEManager import HostParams
from dtm import EventObjects
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.UIDGenerator import UIDGenerator
import app.Utils as Utils  # pylint: disable=F0401
from EventObjects import EEResponseData
import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS
import drce.Consts as DRCE_CONSTS


# Logger initialization
# logger = logging.getLogger(__name__)
logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)


# #The ExecutionEnvironmentManager class, is a main interface of DTM application and Execution Environment.
#
# This object is a main interface of DTM application and Execution Environment that operates with Task units and executes
# requests to the DRCE Cluster and HCE node using both API levels. It supports complete DRCE protocol requests and
# process responses from DRCE cluster. Also, updates task's related data in the tasks data storage containers and
# TasksManager runtime data.
class ExecutionEnvironmentManager(BaseServerManager):

  # Configuration settings options names
  CONFIG_SERVER = "server"
  CONFIG_TASKS_MANAGER_CLIENT = "clientTasksManager"
  CONFIG_TASKS_MANAGER_DATA_CLIENT = "clientTasksDataManager"
  CONFIG_DRCE_HOST = "DRCEHost"
  CONFIG_DRCE_PORT = "DRCEPort"
  CONFIG_DRCE_TIMEOUT = "DRCETimeout"
  CONFIG_HCE_NODE_ADMIN_TIMEOUT = "HCENodeAdminTimeout"


  ERROR_MSG_DRCE_ROUTER_NEW_TASK = "DRCE Router request error!"
  ERROR_HCE_RESPONSE_PROCESSING_EXCEPTION = "HCE node Admin API response processing exception"
  ERROR_HCE_RESPONSE_PROCESSING_SPLIT = "HCE node Admin API response processing can't to split status code"
  ERROR_INSERT_EE_DATA = "Error insert EE response data operation"
  ERROR_UPDATE_TASKS_FIELDS = "Update tasks fields error"
  ERROR_WRONG_OBJECT_TYPE = "Wrong object type from TasksDataManager"
  ERROR_EE_RESPONSE_OBJECT_TYPE_OR_RESPONSE_ERROR = "EEResponseData object error or wrong response structure"
  ERROR_HCE_ADMIN_REQUEST_ERROR = "HCE Admin request error"

  ERROR_DELETE_TASK_RESULTS = 1
  ERROR_DELETE_TASK_RESULTS_MESSAGE = "Delete task results error of EE request response or TaskManager!"

  OPERATION_NEW_TASK = 0
  OPERATION_DELETE_TASK = 1
  OPERATION_CHECK_STATE = 2
  OPERATION_FETCH_RESULTS = 3

  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(ExecutionEnvironmentManager, self).__init__()

    # Instantiate the connection builder light if not set
    if connectionBuilderLight == None:
      connectionBuilderLight = ConnectionBuilderLight()

    className = self.__class__.__name__

    # Get configuration settings
    self.serverName = configParser.get(className, self.CONFIG_SERVER)
    self.clientTasksManagerName = configParser.get(className, self.CONFIG_TASKS_MANAGER_CLIENT)
    self.clientTasksDataManagerName = configParser.get(className, self.CONFIG_TASKS_MANAGER_DATA_CLIENT)

    # Create connections and raise bind or connect actions for correspondent connection type
    serverConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, self.serverName)
    tasksManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT, self.clientTasksManagerName)
    tasksDataManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT,
                                                              self.clientTasksDataManagerName)
    # Add connections to the polling set
    self.addConnection(self.serverName, serverConnection)
    self.addConnection(self.clientTasksManagerName, tasksManagerConnection)
    self.addConnection(self.clientTasksDataManagerName, tasksDataManagerConnection)

    # Set handlers
    # Set event handler for EXECUTE_TASK event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.EXECUTE_TASK, self.onExecuteTask)
    # Set event handler for CHECK_TASK_STATE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE, self.onCheckTaskState)
    # Set event handler for FETCH_TASK_RESULTS event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.FETCH_TASK_RESULTS, self.onFetchTaskResults)
    # Set event handler for FETCH_TASK_DATA_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.FETCH_TASK_DATA_RESPONSE, self.onFetchTaskDataResponse)
    # Set event handler for GET_TASK_FIELDS_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.GET_TASK_FIELDS_RESPONSE, self.onGetTaskManagerFieldsResponse)
    # Set event handler for INSERT_EE_DATA_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.INSERT_EE_DATA_RESPONSE, self.onInsertEEDataResponse)
    # Set event handler for UPDATE_TASK_FIELDS_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.UPDATE_TASK_FIELDS_RESPONSE, self.onUpdateTasksFieldsResponse)
    # Set event handler for DELETE_TASK_RESULTS event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.DELETE_TASK_RESULTS, self.onDeleteTaskResults)
    # Set event handler for DELETE_EE_DATA_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.DELETE_EE_DATA_RESPONSE, self.onDeleteEEDataResponse)

    # Initialize DRCE API
    self.drceHost = configParser.get(className, self.CONFIG_DRCE_HOST)
    self.drcePort = configParser.get(className, self.CONFIG_DRCE_PORT)
    self.drceTimeout = configParser.getint(className, self.CONFIG_DRCE_TIMEOUT)
    hostParams = HostParams(self.drceHost, self.drcePort)
    self.drceManager = DRCEManager()
    self.drceManager.activate_host(hostParams)
    self.drceIdGenerator = UIDGenerator()
    self.drceCommandConvertor = CommandConvertor()

    # Initialize HCE node Admin API
    self.hceNodeAdminTimeout = configParser.getint(className, self.CONFIG_HCE_NODE_ADMIN_TIMEOUT)
    self.hceNodeManagerRequest = admin.NodeManagerRequest.NodeManagerRequest()


  # #ExecuteTask event handler
  #
  # @param event instance of Event object
  def onExecuteTask(self, event):
    try:
      # Get task Id from event
      executeTasks = event.eventObj
      # Request TaskManagerData to get task's data
      fetchTaskData = EventObjects.FetchTaskData(executeTasks.id)
      fetchTaskDataEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.FETCH_TASK_DATA, fetchTaskData)
      # Send request FetchTaskData to TasksManager
      self.send(self.clientTasksDataManagerName, fetchTaskDataEvent)
      logger.info("Sent request FetchTaskData to TasksDataManager, id=" + str(executeTasks.id))
    except Exception as err:
      logger.error("Exception: " + str(err.message) + "\n" + Utils.getTracebackInfo())



  # #ExecuteTask event handler
  #
  # @param event instance of Event object
  def onFetchTaskDataResponse(self, event):
    try:
      # Get task Id from event
      obj = event.eventObj
      # Get unknown object type from event
      if type(obj) == EventObjects.NewTask:
        logger.info("New task processing started, id=" + str(obj.id))
        # Process NewTask action
        self.processNewTask(obj)
        logger.info("New task processing finished, id=" + str(obj.id))
      else:
        if type(obj) == EventObjects.DeleteTask:
          logger.info("Delete task processing started, id=" + str(obj.id))
          # Process DeleteTask
          # Make GetTaskManagerFields request
          self.sendGetTaskManagerFieldsRequest(obj.deleteTaskId, ("onFetchTaskDataResponse", obj))
          logger.debug("GetTaskManagerFields request sent, id=" + str(obj.id))
        else:
          logger.error("Wrong type received from TasksDataManager!")
          logger.error(LogFormatterEvent(event, [], self.ERROR_WRONG_OBJECT_TYPE + " [" + obj.__class__.__name__ + "]" +
                                         " received but [" + str(EventObjects.NewTask) + "] or [" +
                                         str(EventObjects.DeleteTask) + "] expected!"))
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #Send UpdateTasksData event to the TasksManager
  #
  # @param operationType is a name of action that is cause of task's fields update, can be OPERATION_NEW_TASK,
  #       OPERATION_DELETE_TASK, OPERATION_CHECK_STATE, OPERATION_FETCH_RESULTS
  # @param eeResponseDataObj The EE response data object
  # @param cookie is used for the event
  def processUpdateTaskFields(self, operationType, eeResponseData, cookie=None):
    logger.debug("eeResponseData:" + str(vars(eeResponseData)))
    # Update task's fields on TasksManager
    updateTaskFields = EventObjects.UpdateTaskFields(eeResponseData.id)
    # If no errors in response from EE
    if eeResponseData.errorCode == EEResponseData.ERROR_CODE_OK:
      logger.debug("EE returned OK result!")
      # Fill fields to update
      updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] = eeResponseData.state
      updateTaskFields.fields["pId"] = eeResponseData.pId
      updateTaskFields.fields["nodeName"] = eeResponseData.nodeName
      updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST] = eeResponseData.nodeHost
      updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT] = eeResponseData.nodePort
      if DTM_CONSTS.DRCE_FIELDS.URRAM in eeResponseData.fields:
        updateTaskFields.fields["uRRAM"] = eeResponseData.fields[DTM_CONSTS.DRCE_FIELDS.URRAM]
      if DTM_CONSTS.DRCE_FIELDS.UVRAM in eeResponseData.fields:
        updateTaskFields.fields["uVRAM"] = eeResponseData.fields[DTM_CONSTS.DRCE_FIELDS.UVRAM]
      if DTM_CONSTS.DRCE_FIELDS.UCPU in eeResponseData.fields:
        updateTaskFields.fields["uCPU"] = eeResponseData.fields[DTM_CONSTS.DRCE_FIELDS.UCPU]
      if DTM_CONSTS.DRCE_FIELDS.UTHREADS in eeResponseData.fields:
        updateTaskFields.fields["uThreads"] = eeResponseData.fields[DTM_CONSTS.DRCE_FIELDS.UTHREADS]
    else:
      logger.error("EE error returned!")
      if operationType == self.OPERATION_NEW_TASK:
        # For new task operation
        updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] = EEResponseData.TASK_STATE_SET_ERROR
        updateTaskFields.fields["sDate"] = datetime.now()
        if eeResponseData.type == EEResponseData.REQUEST_TYPE_SET:
          updateTaskFields.fields["rDate"] = updateTaskFields.fields["sDate"]
      else:
        # if hasattr(eeResponseData, "deleteTaskId"):
        if operationType == self.OPERATION_DELETE_TASK:
          # For DeleteTask action fake task Id
          updateTaskFields.fields["rDate"] = datetime.now()
          updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] = EEResponseData.TASK_STATE_TERMINATED
        else:
          # For all another operations
          if hasattr(eeResponseData, DTM_CONSTS.DRCE_FIELDS.STATE):
            # If EE returned state - set this state to update
            updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] = eeResponseData.state
          else:
            # If EE error, timeout or another kind and no state returned
            updateTaskFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] = EEResponseData.TASK_STATE_UNDEFINED
            logger.debug("No state field update, task Id: " + str(eeResponseData.id) + ", treated as UNDEFINED!")

    if operationType == self.OPERATION_DELETE_TASK:
      if hasattr(eeResponseData, "deleteTaskId"):
        updateTaskFields.fields["deleteTaskId"] = eeResponseData.deleteTaskId
      # If EE has not found task - push it to delete on TasksManager
      # if hasattr(eeResponseData, "deleteTaskState"):
      #  if eeResponseData.deleteTaskState == EEResponseData.TASK_STATE_NOT_FOUND:
      #    updateTaskFields.fields["deleteTaskState"] = EEResponseData.TASK_STATE_TERMINATED
      #  else:
      #    updateTaskFields.fields["deleteTaskState"] = eeResponseData.deleteTaskState
      if hasattr(eeResponseData, "deleteTaskState"):
        updateTaskFields.fields["deleteTaskState"] = EEResponseData.TASK_STATE_TERMINATED

    logger.debug("Fields to update:\n" + Utils.varDump(updateTaskFields))
    # Create update event
    updateTaskFieldsEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.UPDATE_TASK_FIELDS, updateTaskFields)
    if cookie is not None:
      updateTaskFieldsEvent.cookie = cookie
    # Send update event to TasksManager
    self.send(self.clientTasksManagerName, updateTaskFieldsEvent)
    logger.debug("Fields sent to update!")



  # #NewTasks action processor
  #
  # @param newTaskObj object
  def processNewTask(self, newTaskObj):
    # Prepare DRCE request object
    taskExecuteStruct = TaskExecuteStruct()
    taskExecuteStruct.command = newTaskObj.command
    taskExecuteStruct.files = newTaskObj.files
    taskExecuteStruct.input = newTaskObj.input
    # Set session
    taskExecuteStruct.session = Session(newTaskObj.session["tmode"], newTaskObj.session["type"],
                                             newTaskObj.session["time_max"])
    taskExecuteStruct.session.password = newTaskObj.session["password"]
    taskExecuteStruct.session.port = newTaskObj.session[DTM_CONSTS.DRCE_FIELDS.PORT]
    taskExecuteStruct.session.shell = newTaskObj.session["shell"]
    taskExecuteStruct.session.timeout = newTaskObj.session["timeout"]
    taskExecuteStruct.session.user = newTaskObj.session["user"]
    taskExecuteStruct.session.home_directory = newTaskObj.session["home_directory"]
    taskExecuteStruct.session.environment = newTaskObj.session["environment"]
    # Set limits
    taskExecuteStruct.limits = newTaskObj.limits
    # Create DRCE TaskExecuteRequest object
    taskExecuteRequest = TaskExecuteRequest(newTaskObj.id)
    # Set taskExecuteRequest fields
    taskExecuteRequest.data = taskExecuteStruct
    # If session has route field - set custom route
    if "route" in newTaskObj.session and newTaskObj.session["route"] is not None and newTaskObj.session["route"] != "":
      taskExecuteRequest.route = newTaskObj.session["route"]
    if "task_type" in newTaskObj.session and newTaskObj.session["task_type"] is not None and\
      newTaskObj.session["task_type"] != "":
      taskExecuteRequest.task_type = newTaskObj.session["task_type"]
    logger.debug("Sending task to DRCE router, id=" + str(newTaskObj.id) + ", route:" + str(taskExecuteRequest.route))
    # Send request to DRCE Cluster router
    response = self.sendToDRCERouter(taskExecuteRequest)
    logger.debug("Received from DRCE router, id=" + str(newTaskObj.id))
    # Convert response to EEResponse object
    eeResponseData = self.convertToEEResponse(response)
    logger.debug("Response body:\n" + Utils.varDump(response))
    logger.debug("eeResponseData object:\n" + Utils.varDump(eeResponseData))
    # Update task Id to set proper Id in case of request timed out and no task Id in response
    if eeResponseData.id == newTaskObj.id:
      # eeResponseData.id = newTaskObj.id
      # Update TaskFields in the TasksManager
      logger.debug("Process update TaskFields in the TasksManager, id=" + str(newTaskObj.id))
      self.processUpdateTaskFields(self.OPERATION_NEW_TASK, eeResponseData)
    else:
      logger.error("Wrong task Id= " + str(eeResponseData.id) + " returned from DRCE, expected id=" + \
                   str(newTaskObj.id) + ". TasksManager's fields not updated, task state not changed. Response:\n" +
                   Utils.varDump(eeResponseData))



  # #Send to send to DRCE Router transport router connection
  #
  # @param messageBody body of the message
  # @return EEResponseData object instance
  def sendToDRCERouter(self, request):
    logger.debug("DRCE router sending request\n" + Utils.varDump(request))
    # Try to execute request
    try:
      response = self.drceManager.process(request, self.drceTimeout)
    except (ConnectionTimeout, TransportInternalErr, CommandExecutorErr) as err:
      response = None
      logger.error(err)

    return response



  # #Converts DRCE TaskResponse object to the EEResponseData object
  #
  # @param response drce.Commands.TaskResponse object
  # @return EEResponseData object instance
  def convertToEEResponse(self, response):
    # Check response on validity, None if timeout reached
    if response is not None and len(response.items) > 0:
      eeR = EEResponseData(response.items[0].id)
      # Fill eeR with fields from the returned object from EE
      eeR.type = response.items[0].type
      eeR.errorCode = response.items[0].error_code
      eeR.errorMessage = response.items[0].error_message
      eeR.state = response.items[0].state
      eeR.pId = response.items[0].pid
      eeR.requestTime = response.items[0].time
      eeR.nodeHost = response.items[0].host
      eeR.nodePort = response.items[0].port
      eeR.nodeName = response.items[0].node
      eeR.stdout = response.items[0].stdout
      eeR.stderr = response.items[0].stderror
      eeR.exitStatus = response.items[0].exit_status
      eeR.taskTime = response.items[0].time
      eeR.files = response.items[0].files
      eeR.fields = response.items[0].fields
      logger.debug("To EEResponseData converted!")
    else:
      # Fill eeR with error state info if timeout reached
      eeR = EEResponseData(0)
      eeR.errorCode = EEResponseData.ERROR_CODE_TIMEOUT
      eeR.errorMessage = EEResponseData.ERROR_MESSAGE_TIMEOUT
      logger.error(self.ERROR_EE_RESPONSE_OBJECT_TYPE_OR_RESPONSE_ERROR)

    return eeR



  # #Converts raw HCE Admin API response to DRCE TaskResponse object
  #
  # @param rawResponse HCE Admin API response raw buffer
  # @return drce.Commands.TaskResponse object
  def convertToTaskResponse(self, rawResponse):
    taskResponse = None

    # Parse response status
    items = rawResponse.split(admin.Constants.COMMAND_DELIM)
    if len(items) > 1:
      # Convert DRCE jason protocol response to TaskResponse object
      try:
        taskResponse = self.drceCommandConvertor.from_json(items[1])
        logger.debug("To taskResponse converted!")
      except Exception, e:
        logger.error(self.ERROR_HCE_RESPONSE_PROCESSING_EXCEPTION + " : " + e.__doc__ + " : " + str(e.message))
    else:
      logger.error(self.ERROR_HCE_RESPONSE_PROCESSING_SPLIT)

    return taskResponse



  # #onCheckTaskState event handler
  #
  # @param event instance of Event object
  def onCheckTaskState(self, event):
    try:
      # Get event object
      checkTaskStateObj = event.eventObj
      # Get TaskManager fields
      self.sendGetTaskManagerFieldsRequest(checkTaskStateObj.id, ("onCheckTaskState", event))
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #onFetchTaskResults event handler
  #
  # @param event instance of Event object
  def onFetchTaskResults(self, event):
    try:
      # Get event object
      fetchTaskResultsObj = event.eventObj
      # Send the GetTaskManagerFields request
      self.sendGetTaskManagerFieldsRequest(fetchTaskResultsObj.id, ("onFetchTaskResults", event))
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #onDeleteTaskResults event handler
  #
  # @param event instance of Event object
  def onDeleteTaskResults(self, event):
    try:
      # Get event object
      deleteTaskResultsObj = event.eventObj
      # Send the GetTaskManagerFields request
      self.sendGetTaskManagerFieldsRequest(deleteTaskResultsObj.id, ("onDeleteTaskResults", event))
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #Send to EE transport node admin connection
  #
  # @param host HCE node host
  # @param port HCE node port
  # @param messageParameters HCE node Admin request message parameters string
  # @return the raw body of HCE Admin API response if success or empty string if not
  def sendToHCENodeAdmin(self, host, port, messageParameters):
    # Execute EE node admin request
    node = admin.Node.Node(host, port)
    params = [messageParameters]
    try:
      command = admin.Command.Command(admin.Constants.COMMAND_NAMES.DRCE,
                                      params,
                                      admin.Constants.ADMIN_HANDLER_TYPES.DATA_PROCESSOR_DATA,
                                      self.hceNodeAdminTimeout)
      requestBody = command.generateBody()
      message = {admin.Constants.STRING_MSGID_NAME : self.drceIdGenerator.get_uid(),
                 admin.Constants.STRING_BODY_NAME : requestBody}
      response = self.hceNodeManagerRequest.makeRequest(node, message, self.hceNodeAdminTimeout)
      logger.debug("Response from HCE node Admin received!")

      return response.getBody()
    except Exception, e:
      logger.error(self.ERROR_HCE_ADMIN_REQUEST_ERROR + " : " + str(e.message))
      return ""



  # #Send GetTaskManager request
  #
  # @param taskId task Id
  # @param cookieData data that will be copied from send event to reply
  def sendGetTaskManagerFieldsRequest(self, taskId, cookieData=None):
    # Get TaskManager fields
    # Prepare synch GetTaskFields request to the TasksManager
    getTaskManagerFieldsObj = EventObjects.GetTaskManagerFields(taskId)
    getTaskManagerFieldsEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.GET_TASK_FIELDS,
                                                        getTaskManagerFieldsObj)
    if cookieData is not None:
      getTaskManagerFieldsEvent.cookie = cookieData

    self.send(self.clientTasksManagerName, getTaskManagerFieldsEvent)
    logger.debug("GetTaskManagerFields sent!")



  # #processFetchTaskResult action
  #
  # @param event received from TasksManager
  def processFetchTaskResults(self, event):
    # Get event object
    taskManagerFields = event.eventObj

    # Check is task found
    if len(taskManagerFields.fields) > 0:
      # Check task state
      if taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_FINISHED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_CRASHED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_TERMINATED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_TERMINATED_BY_DRCE_TTL or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_NEW:
        fetchTaskResultsObj = event.cookie[1].eventObj
        # Prepare the messageBodyJson for DRCE request
        taskGetDataRequest = TaskGetDataRequest(fetchTaskResultsObj.id, fetchTaskResultsObj.type)
        messageBodyJson = self.drceCommandConvertor.to_json(taskGetDataRequest)

        logger.debug("(line 508) Call sendToHCENodeAdmin() use Host: '%s' and Port '%s'",
                     str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST]),
                     str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT]))

        rawResponse = self.sendToHCENodeAdmin(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST],
                                              taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT],
                                              messageBodyJson)
        eeResponseData = self.convertToEEResponse(self.convertToTaskResponse(rawResponse))
        logger.debug("Response received from EE for onFetchTaskResults!")
        if eeResponseData.errorCode == EEResponseData.ERROR_CODE_OK and \
           EEResponseData.TASK_STATE_FINISHED:
          # Update EEResponseDtata object in the TasksDataManager container
          logger.debug("Update EEResponseDtata object in the TasksDataManager container sent!")
          insertEEDataEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.INSERT_EE_DATA, eeResponseData)
          self.send(self.clientTasksDataManagerName, insertEEDataEvent)
          # Update TaskFields in the TasksManager
          logger.debug("Update TaskFields in the TasksManager!")
          self.processUpdateTaskFields(self.OPERATION_FETCH_RESULTS, eeResponseData)
      else:
        # Return state, requested operation can't to be done on DRCE cause task is not in proper state
        eeResponseData = EEResponseData(taskManagerFields.id)
        eeResponseData.state = taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE]
        logger.debug("Wrong task state " + str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE]) +
                     " for FetchTaskResults operation!")
    else:
      eeResponseData = EEResponseData(0)
      eeResponseData.state = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
      eeResponseData.errorCode = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
      eeResponseData.errorMessage = EEResponseData.ERROR_MESSAGE_TASK_NOT_FOUND
      eeResponseData.exitStatus = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
      logger.error("Empty mandatory fields received from TasksManager:\n%s", Utils.varDump(taskManagerFields))
    # Prepare check task reply event
    fetchTaskResultsReplyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE,
                                                         eeResponseData)
    self.reply(event.cookie[1], fetchTaskResultsReplyEvent)



  # #processCheckTaskState action
  #
  # @param event received from TasksManager
  def processCheckTaskState(self, event):
    # Get event object
    taskManagerFields = event.eventObj

    # Check is task found
    if len(taskManagerFields.fields) > 0 and taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST] is not None and\
      taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST] != "" and\
      taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT] is not None and\
      taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT] != "":

      # Check task state
      checkTaskStateObj = event.cookie[1].eventObj
      # Prepare the messageBodyJson for DRCE request
      taskCheckRequest = TaskCheckRequest(checkTaskStateObj.id, checkTaskStateObj.type)
      messageBodyJson = self.drceCommandConvertor.to_json(taskCheckRequest)
      # Make HCE node admin request
      logger.debug("Make HCE node admin request!")
      logger.debug("(line 566) Call sendToHCENodeAdmin() use Host: '%s' and Port '%s'",
                   str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST]),
                   str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT]))

      rawResponse = self.sendToHCENodeAdmin(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST],
                                            taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT],
                                            messageBodyJson)
      eeResponseData = self.convertToEEResponse(self.convertToTaskResponse(rawResponse))
      if eeResponseData.errorCode == EEResponseData.ERROR_CODE_OK:
        if eeResponseData.nodeHost == "" or eeResponseData.nodePort == "":
          logger.error(str(vars(eeResponseData)))
          logger.debug("Received Host or Port is empty!")
        # Update TaskFields in the TasksManager
        logger.debug("Update TaskFields in the TasksManager!")
        self.processUpdateTaskFields(self.OPERATION_CHECK_STATE, eeResponseData)
    else:
      eeResponseData = EEResponseData(taskManagerFields.id)
      eeResponseData.state = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
      eeResponseData.errorCode = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
      eeResponseData.errorMessage = EEResponseData.ERROR_MESSAGE_TASK_NOT_FOUND
      eeResponseData.exitStatus = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
      logger.error("Empty mandatory fields received from TasksManager:\n%s", Utils.varDump(taskManagerFields))
    # Prepare check task reply event
    checkTaskStateReplyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE_RESPONSE,
                                                       eeResponseData)
    self.reply(event.cookie[1], checkTaskStateReplyEvent)
    logger.debug("Check task reply event sent!")



  # #createTaskDeleteRequest creates and returns TaskTerminateRequest or TaskDeleteRequest objects
  #
  # @param deleteTaskObj - deleted tasks object
  def createTaskDeleteRequest(self, deleteTaskObj):
    ret = None
    if deleteTaskObj.action == EventObjects.DeleteTask.ACTION_DELETE_TASK_DATA:
      # Prepare DRCE request object for delete task's data
      ret = TaskDeleteRequest(deleteTaskObj.deleteTaskId)
    elif deleteTaskObj.action == EventObjects.DeleteTask.ACTION_TERMINATE_TASK_AND_DELETE_DATA:
      # Prepare DRCE request object for terminate task and delete it's data (default init)
      ret = TaskTerminateRequest(deleteTaskObj.deleteTaskId)
    else:
      # Prepare DRCE request object for terminate task and leave it's data
      ret = TaskTerminateRequest(deleteTaskObj.deleteTaskId)
      ret.data["cleanup"] = DRCE_CONSTS.TERMINATE_DATA_SAVE
    return ret


  # #checkDelTaskState check deleted task state
  #
  # @param state deleteed task state
  # return bool value -available task to delete or not
  def checkDelTaskState(self, state, action):
    ret = False
    if state == EEResponseData.TASK_STATE_FINISHED or\
       state == EEResponseData.TASK_STATE_CRASHED or\
       state == EEResponseData.TASK_STATE_TERMINATED or\
       state == EEResponseData.TASK_STATE_TERMINATED_BY_DRCE_TTL or\
       state == EEResponseData.TASK_STATE_DELETED or\
       state == EEResponseData.TASK_STATE_UNDEFINED or\
       state == EEResponseData.TASK_STATE_SET_ERROR or\
       state == EEResponseData.TASK_STATE_NOT_FOUND or\
       state == EEResponseData.TASK_STATE_SCHEDULE_TRIES_EXCEEDED or\
       action == EventObjects.DeleteTask.ACTION_TERMINATE_TASK_AND_DELETE_DATA:
      if action != EventObjects.DeleteTask.ACTION_DELETE_ON_DTM:
        ret = True
    return ret


  # #processDeleteTask action
  #
  # @param event received from TasksManager
  def processDeleteTask(self, event):
    # Get event object
    taskManagerFields = event.eventObj
    deleteTaskObj = event.cookie[1]

    # Check is task found
    if len(taskManagerFields.fields) > 0:
      eeResponseData = None
      deletedTasksState = taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] if \
                                  DTM_CONSTS.DRCE_FIELDS.STATE in taskManagerFields.fields else None
      # Check task data
      if taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST] is not None and\
        taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST] != "" and\
        taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT] is not None and\
        taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT] != "":
        if self.checkDelTaskState(deletedTasksState, deleteTaskObj.action):
          taskDeleteRequest = self.createTaskDeleteRequest(deleteTaskObj)
          messageBodyJson = self.drceCommandConvertor.to_json(taskDeleteRequest)
          logger.debug("Send TaskDeleteRequest to HCE node Admin API, taskId=" + str(deleteTaskObj.deleteTaskId))
          logger.debug("(line 657) Call sendToHCENodeAdmin() use Host: '%s' and Port '%s'",
                       str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST]),
                       str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT]))

          rawResponse = self.sendToHCENodeAdmin(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST],
                                                taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT],
                                                messageBodyJson)
          logger.debug("TaskDeleteequest rawResponse=[" + rawResponse + "]")
          if rawResponse != "":
            eeResponseData = self.convertToEEResponse(self.convertToTaskResponse(rawResponse))
            logger.debug("TaskDeleteRequest response taskId=" + str(deleteTaskObj.deleteTaskId) + \
                         ", state:" + str(eeResponseData.state) + \
                         ", exitStatus:" + str(eeResponseData.exitStatus) + \
                         ", stdout: " + eeResponseData.stdout + ", stderr:" + eeResponseData.stderr)
            eeResponseData.id = deleteTaskObj.id
            #!!!Replace the unsupported states like UNDEFINED or NOTFOUND to push to remove this tasks from TasksManager
            if eeResponseData.state != EEResponseData.TASK_STATE_IN_PROGRESS and\
               eeResponseData.state != EEResponseData.TASK_STATE_NEW:
              logger.debug("Task state was substituted from " + str(eeResponseData.state) + " to " + \
                           str(EEResponseData.TASK_STATE_DELETED) + ", taskId=" + str(deleteTaskObj.deleteTaskId))
            # eeResponseData.state = EEResponseData.TASK_STATE_DELETED
            # Substitute state for task to delete and deleted task
            eeResponseData.nodeName = ""
            eeResponseData.nodeHost = ""
            eeResponseData.nodePort = 0
            eeResponseData.state = EEResponseData.TASK_STATE_DELETED
            if eeResponseData.errorCode > 0:
              logger.debug("TaskDelete request response error:" + str(eeResponseData.errorCode) + " : " + \
                             eeResponseData.errorMessage)
              eeResponseData.state = EEResponseData.TASK_STATE_SET_ERROR
              eeResponseData.deleteTaskId = deleteTaskObj.deleteTaskId
              eeResponseData.deleteTaskState = None
            else:
              eeResponseData.deleteTaskId = deleteTaskObj.deleteTaskId
              eeResponseData.deleteTaskState = eeResponseData.state
          else:
            # Set state as TERMINATED to push the TasksManager to delete task's data on DTM, save the dat file in DRCE node
            eeResponseData = EEResponseData(deleteTaskObj.id)
            eeResponseData.deleteTaskId = deleteTaskObj.deleteTaskId
            eeResponseData.deleteTaskState = EEResponseData.TASK_STATE_DELETED
            eeResponseData.state = EEResponseData.TASK_STATE_DELETED
            logger.error("TaskDeleteRequest response fault, taskId=" + str(deleteTaskObj.deleteTaskId) + "!")
        else:
          eeResponseData = EEResponseData(deleteTaskObj.id)
          eeResponseData.deleteTaskId = deleteTaskObj.deleteTaskId
          if deleteTaskObj.action == EventObjects.DeleteTask.ACTION_DELETE_ON_DTM:
            eeResponseData.state = EEResponseData.TASK_STATE_DELETED
            eeResponseData.deleteTaskState = EEResponseData.TASK_STATE_DELETED
            logger.debug("Deleted task only on DTM")
#          eeResponseData.deleteTaskState = deletedTasksState
          else:
            eeResponseData.state = EEResponseData.TASK_STATE_SET_ERROR
            logger.debug("Deleted task " + str(eeResponseData.deleteTaskId) + " has bad[Not deleted state] " +
                        str(deletedTasksState) + " delete error")
      else:
        # Set state as TERMINATED to push the TasksManager to delete task's data on DTM, save the dat file in DRCE node
        msg = "Host or Port is empty! Set state as TERMINATED to push delete task, deleteTaskObj.id=" + \
              str(deleteTaskObj.id) + ", deleteTaskObj.deleteTaskId=" + str(deleteTaskObj.deleteTaskId)
        eeResponseData = EEResponseData(deleteTaskObj.id)
        eeResponseData.errorCode = EEResponseData.ERROR_CODE_TASK_NOT_FOUND
        eeResponseData.errorMessage = msg
        eeResponseData.deleteTaskId = deleteTaskObj.deleteTaskId
        eeResponseData.deleteTaskState = EEResponseData.TASK_STATE_TERMINATED
        eeResponseData.state = EEResponseData.TASK_STATE_TERMINATED
        logger.error(msg)

      if eeResponseData is not None:
        # Update TaskFields in the TasksManager
        self.processUpdateTaskFields(self.OPERATION_DELETE_TASK, eeResponseData)
        logger.debug("Update TaskFields in the TasksManager!")
    else:
      logger.error("Empty fields received from TasksManager for DeleteTask!")


  def createGeneralResponse(self, errCode, errMessage, errLog):
    generalResponseObj = EventObjects.GeneralResponse()
    generalResponseObj.errorCode = errCode
    generalResponseObj.errorMessage = errMessage
    logger.debug(errLog)
    return generalResponseObj


  # #processDeleteTaskResult action
  #
  # @param event received from TasksManager
  def processDeleteTaskResults(self, event):
    # Get event object
    taskManagerFields = event.eventObj
    # New General response event object for error case
    generalResponseObj = None
    hceNodeAdminRequestState = EEResponseData.ERROR_CODE_OK

    # Check is task found
    if len(taskManagerFields.fields) > 0:
      # Check task data
      if taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_FINISHED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_CRASHED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_TERMINATED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_TERMINATED_BY_DRCE_TTL or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_DELETED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_UNDEFINED or\
         taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE] == EEResponseData.TASK_STATE_NOT_FOUND:
        deleteTaskResultsObj = event.cookie[1].eventObj
        # Prepare the messageBodyJson for DRCE request
        logger.info("Send TaskGetDataRequest with DELETE data, taskId=" + str(deleteTaskResultsObj.id))
        # TODO: Use GetDataRequest to delete results, need to be replaced with native command later
        taskDeleteRequest = TaskDeleteRequest(deleteTaskResultsObj.id)
        messageBodyJson = self.drceCommandConvertor.to_json(taskDeleteRequest)

        logger.debug("(line 766) Call sendToHCENodeAdmin() use Host: '%s' and Port '%s'",
                     str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST]),
                     str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT]))

        rawResponse = self.sendToHCENodeAdmin(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.HOST],
                                              taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.PORT],
                                              messageBodyJson)
        logger.info("TaskDeleteResultsRequest rawResponse=[" + rawResponse + "]")
        if rawResponse != "":
          eeResponseData = self.convertToEEResponse(self.convertToTaskResponse(rawResponse))
          if eeResponseData.errorCode == EEResponseData.ERROR_CODE_OK:
            logger.info("Response received from EE")
          else:
            generalResponseObj = self.createGeneralResponse(EventObjects.DeleteTaskResults.DRCE_ERROR,
                                 EventObjects.DeleteTaskResults.DRCE_ERROR_MESSAGE,
                                 "DRCE error error=" + str(eeResponseData.errorCode))
        else:
          generalResponseObj = self.createGeneralResponse(EventObjects.DeleteTaskResults.EMPRY_RAW_ERROR,
                               EventObjects.DeleteTaskResults.EMPRY_RAW_ERROR_MESSAGE, "Empty rawResponse")
      else:
        # Return state, requested operation can't to be done on DRCE cause task is not in proper state
        generalResponseObj = self.createGeneralResponse(EventObjects.DeleteTaskResults.TASK_STATE_ERROR,
                             EventObjects.DeleteTaskResults.TASK_STATE_ERROR_MESSAGE,
                             "Wrong task state " + str(taskManagerFields.fields[DTM_CONSTS.DRCE_FIELDS.STATE]) +
                             ", can't cleanup!")
    else:
      generalResponseObj = self.createGeneralResponse(EventObjects.DeleteTaskResults.TASK_NOT_FOUND_ERROR,
                           EventObjects.DeleteTaskResults.TASK_NOT_FOUND_ERROR_MESSAGE,
                           "Empty fields from TasksManager for DeleteTaskResults, possible task not found!")
    # Send DELETE_EE_DATA request to the TasksDataManager
    if generalResponseObj == None:
      logger.debug("Send DELETE_EE_DATA request to the TasksDataManager!")
      deleteEEResponseDataObj = EventObjects.DeleteEEResponseData(taskManagerFields.id)
      deleteEEResponseDataEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_EE_DATA, deleteEEResponseDataObj)
      deleteEEResponseDataEvent.cookie = ("processDeleteTaskResults", event.cookie[1], hceNodeAdminRequestState)
      self.send(self.clientTasksDataManagerName, deleteEEResponseDataEvent)
      logger.debug("Sent request DeleteEEResponseDataObj to TasksDataManager!")
    else:
      deleteTaskResultsReplyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_TASK_RESULTS_RESPONSE,
                                                           generalResponseObj)
      self.reply(event.cookie[1], deleteTaskResultsReplyEvent)
      logger.info("Send response GeneralResponse to ClientInterfaceService!")



  # #onGetTaskManagerFieldsResponse event handler
  #
  # @param event instance of Event object
  def onGetTaskManagerFieldsResponse(self, event):
    try:
      if event.cookie is not None and event.cookie[0] == "onFetchTaskResults":
        # Continue the onFetchTaskResults handling
        self.processFetchTaskResults(event)

      if event.cookie is not None and event.cookie[0] == "onCheckTaskState":
        # Continue the onCheckTaskState handling
        self.processCheckTaskState(event)

      if event.cookie is not None and event.cookie[0] == "onFetchTaskDataResponse":
        # Continue DeleteTask
        self.processDeleteTask(event)

      if event.cookie is not None and event.cookie[0] == "onDeleteTaskResults":
        # Continue DeleteTask
        self.processDeleteTaskResults(event)
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #onInsertEEDataResponse event handler, process the response from the TasksDataManager object
  #
  # @param event instance of Event object
  def onInsertEEDataResponse(self, event):
    try:
      # Get task Id from event
      generalResponse = event.eventObj
      if generalResponse.errorCode != EventObjects.GeneralResponse.ERROR_OK:
        logger.error(LogFormatterEvent(event, [], self.ERROR_INSERT_EE_DATA))
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #onUpdateTasksFieldsResponse event handler, process the response from the TasksManager object
  #
  # @param event instance of Event object
  def onUpdateTasksFieldsResponse(self, event):
    try:
      # Get task Id from event
      generalResponse = event.eventObj
      if generalResponse.errorCode != EventObjects.GeneralResponse.ERROR_OK:
        logger.error(LogFormatterEvent(event, [], self.ERROR_UPDATE_TASKS_FIELDS))
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)



  # #onDeleteEEDataResponse event handler, process the response from the TasksDataManager object
  #
  # @param event instance of Event object
  def onDeleteEEDataResponse(self, event):
    try:
      # Get task Id from event
      generalResponse = event.eventObj
      if generalResponse.errorCode != EventObjects.GeneralResponse.ERROR_OK:
        logger.error(LogFormatterEvent(event, [], self.ERROR_UPDATE_TASKS_FIELDS))

      if event.cookie is not None and event.cookie[0] == "processDeleteTaskResults":
        # Continue the onDeleteTaskResults handling
        generalResponseObj = EventObjects.GeneralResponse()
        generalResponseObj.statuses = (event.cookie[2], generalResponse.errorCode)
        if generalResponse.errorCode != EventObjects.GeneralResponse.ERROR_OK or\
           event.cookie[2] != EEResponseData.ERROR_CODE_OK:
          generalResponseObj.errorCode = self.ERROR_DELETE_TASK_RESULTS
          generalResponseObj.errorMessage = self.ERROR_DELETE_TASK_RESULTS_MESSAGE
        # Prepare delete task results reply event for error case
        deleteTaskResultsReplyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_TASK_RESULTS_RESPONSE,
                                                             generalResponseObj)
        self.reply(event.cookie[1], deleteTaskResultsReplyEvent)
    except Exception as err:
      tbi = Utils.getTracebackInfo()
      logger.error("Exception: " + str(err.message) + "\n" + tbi)

