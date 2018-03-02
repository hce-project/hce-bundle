'''
@package: dtm
@author igor, bgv
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import logging
from app.BaseServerManager import BaseServerManager
from Constants import EVENT_TYPES, LOGGER_NAME
from EventObjects import GeneralResponse
from EventObjects import DeleteTask
import transport.Consts as consts

logger = logging.getLogger(LOGGER_NAME)

CONFIG_SECTION = "ClientInterfaceService"

##The gateway  for dmt client  communications
#
class ClientInterfaceService(BaseServerManager):

  SERVER_TCP = "server_tcp"
  SERVER_INPROC = "server"
  CONFIG_SERVER_HOST = "serverHost"
  CONFIG_SERVER_PORT = "serverPort"
  TASKS_MANAGER_CLIENT = "clientTasksManager"
  EXECUTION_ENVIRONMENT_MANAGER_CLINET = "clientExecutionEnvironmentManager"

  ##constructor
  #initialise all connections and event handlers
  #@param configParser config parser object
  #@param connectBuilderLight instance of ConnectBuilderLight object
  #
  def __init__(self, configParser, connectBuilderLight):
    '''
    Constructor
    '''
    super(ClientInterfaceService, self).__init__()

    self.beforeStop = False
    self.cfg_section = self.__class__.__name__

    serverAddrInproc = configParser.get(self.cfg_section, self.SERVER_INPROC)
    serverHost = configParser.get(CONFIG_SECTION, self.CONFIG_SERVER_HOST)
    serverPort = configParser.get(CONFIG_SECTION, self.CONFIG_SERVER_PORT)
    serverAddrTcp = serverHost + ":" + str(serverPort)
    clientTaskManager = configParser.get(CONFIG_SECTION, self.TASKS_MANAGER_CLIENT)
    clientExecutionEnvironmentManager = configParser.get(CONFIG_SECTION, self.EXECUTION_ENVIRONMENT_MANAGER_CLINET)

    serverConnectionInproc = connectBuilderLight.build(consts.SERVER_CONNECT, serverAddrInproc)
    serverConnectionTcp = connectBuilderLight.build(consts.SERVER_CONNECT, serverAddrTcp, consts.TCP_TYPE)
    taskManagerConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, clientTaskManager)
    eeManagerConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, clientExecutionEnvironmentManager)

    self.addConnection(self.SERVER_TCP, serverConnectionTcp)
    self.addConnection(self.SERVER_INPROC, serverConnectionInproc)
    self.addConnection(self.TASKS_MANAGER_CLIENT, taskManagerConnection)
    self.addConnection(self.EXECUTION_ENVIRONMENT_MANAGER_CLINET, eeManagerConnection)

    self.setEventHandler(EVENT_TYPES.NEW_TASK, self.onTaskManagerRoute)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK, self.onTaskManagerRoute)
    self.setEventHandler(EVENT_TYPES.GET_TASK_STATUS, self.onTaskManagerRoute)
    self.setEventHandler(EVENT_TYPES.FETCH_RESULTS_CACHE, self.onTaskManagerRoute)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK, self.onTaskManagerRoute)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK_FIELDS, self.onTaskManagerRoute)
    self.setEventHandler(EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS, self.onTaskManagerRoute)

    self.setEventHandler(EVENT_TYPES.CHECK_TASK_STATE, self.onEEManagerRoute)
    self.setEventHandler(EVENT_TYPES.FETCH_TASK_RESULTS, self.onEEManagerRoute)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK_RESULTS, self.onEEManagerRoute)

    self.setEventHandler(EVENT_TYPES.NEW_TASK_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.CHECK_TASK_STATE_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.GET_TASK_STATUS_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.DELETE_TASK_RESULTS_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.UPDATE_TASK_FIELDS_RESPONSE, self.onDTMClientRoute)
    self.setEventHandler(EVENT_TYPES.AVAILABLE_TASK_IDS_RESPONSE, self.onDTMClientRoute)

    #map of incoming event, which are in processing
    # event.uid => event without eventObj field
    self.processEvents = dict()


  ##handler to route all event to TaksManager
  #
  #@param even instance of Event object
  def onTaskManagerRoute(self, event):
    if not self.beforeStop:
      if event.eventType == EVENT_TYPES.DELETE_TASK and event.eventObj.deleteTaskId == DeleteTask.GROUP_DELETE:
        self.beforeStop = True
      self.send(self.TASKS_MANAGER_CLIENT, event)
      self.registreEvent(event)
    else:
      defaultObject = GeneralResponse(GeneralResponse.ERROR_OK, "DTM in prestopped state")
      responseEvent = self.eventBuilder.build(EVENT_TYPES.GENERAL_RESPONSE, defaultObject)
      self.reply(event, responseEvent)



  ##handler to route all event to EEManager
  #
  #@param even instance of Event object
  def onEEManagerRoute(self, event):
    self.send(self.EXECUTION_ENVIRONMENT_MANAGER_CLINET, event)
    self.registreEvent(event)


  ##handler to route all response event to DTMClient
  #
  #@param even instance of Event object
  def onDTMClientRoute(self, event):
    try:
      request_event = self.getRequestEvent(event)
      self.reply(request_event, event)
      self.unregisteEvent(request_event)
    except KeyError as err:
      logger.error(str(err.message))


  ##add event in map of processing events
  #
  #@param even instance of Event object
  def registreEvent(self, event):
    event.eventObj = None
    self.processEvents[event.uid] = event


  ##get request event from processEvents map
  #@param event instance of Event  object
  #@return event instance of Event object
  def getRequestEvent(self, event):
    return self.processEvents[event.uid]


  ##delete event in map of processing events
  #
  #@param even instance of Event object
  def unregisteEvent(self, event):
    del self.processEvents[event.uid]
