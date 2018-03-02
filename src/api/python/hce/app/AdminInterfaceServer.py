'''
HCE project, Python bindings, Distributed Tasks Manager application.
AdminInterfaceServer object and related classes definitions.
This object acts as client-side admin interface.
It handles admin requests events. Most common admin events are: statistics data fetching from all threaded classes.
configuration parameters update and DTM application shutdown.


@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from app.BaseServerManager import BaseServerManager
from app.LogFormatter import LogFormatterEvent
import app.Consts as APP_CONSTS
import app.Utils as Utils  # pylint: disable=W0611
from app.Utils import ExceptionLog, varDump
from app.SystemCommandHandler import SystemCommandHandler
import dbi.Constants as DBI_CONSTANTS
from dbi.dbi import DBI
import dtm.Constants as DTM_CONSTS
import dtm.EventObjects
import transport.Consts as TRANSPORT_CONSTS
from transport.ConnectionBuilderLight import ConnectionBuilderLight


# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The AdminInterfaceServer class, admin user API to manage DTM application.
#
# This object acts as client-side admin interface.
# It handles admin requests events. Most common admin events are: statistics data fetching from all threaded classes.
# configuration parameters update and DTM application shutdown.
#
class AdminInterfaceServer(BaseServerManager):

  # Configuration settings options names
  CONFIG_SERVER_HOST = "serverHost"
  CONFIG_SERVER_PORT = "serverPort"

  ERROR_EVENT_NOT_FOUND = "Event not found in queue"

  VERSION_STRING_NAME = "VERSION"

  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(AdminInterfaceServer, self).__init__()

    # Admin server connection clients dic, format [className]=connect_identity
    self.adminServerClients = {}

    # #@var dbi
    # db contains two tables log and backlog
    try:
      self.dbi = DBI(self.createDBIDict(configParser))
    except Exception:
      self.dbi = None

    # Suspend responses list, identity and results dict
    self.onSuspendConnectionIds = {}
    self.onSuspendConnectionIdent = None
    self.onSuspendResponseDict = {}

    # TCP server events to client identity cross reference dic, format [event_id]=connect_identity
    self.tcpServerEventIdToConnectIdentity = {}

    # Instantiate the connection builder light if not set
    if connectionBuilderLight is None:
      connectionBuilderLight = ConnectionBuilderLight()

    className = self.__class__.__name__
    self.exit_flag = False

    # Get configuration settings
    self.serverHost = configParser.get(className, self.CONFIG_SERVER_HOST)
    self.serverPort = configParser.get(className, self.CONFIG_SERVER_PORT)

    # Create connections and raise bind or connect actions for correspondent connection type
    tcpServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                       self.serverHost + ":" + self.serverPort,
                                                       TRANSPORT_CONSTS.TCP_TYPE)
    adminServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                         BaseServerManager.ADMIN_CONNECT_ENDPOINT)

    # Add connections to the polling set
    self.addConnection(BaseServerManager.ADMIN_CONNECT_ENDPOINT, adminServerConnection)
    self.addConnection(self.serverHost, tcpServerConnection)

    # Set event handler for ADMIN_FETCH_STAT_DATA event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_FETCH_STAT_DATA, self.onAdminStatData)
    # Set event handler for ADMIN_FETCH_STAT_DATA_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, self.onAdminStatDataResponse)
    # Set event handler for ADMIN_STATE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_STATE, self.onAdminState)
    # Set event handler for ADMIN_STATE_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_STATE_RESPONSE, self.onAdminStateResponse)
    # Set event handler for ADMIN_GET_CONFIG_VARS event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_GET_CONFIG_VARS, self.onAdminGetConfigVars)
    # Set event handler for ADMIN_GET_CONFIG_VARS_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_GET_CONFIG_VARS_RESPONSE, self.onAdminGetConfigVarsResponse)
    # Set event handler for ADMIN_SET_CONFIG_VARS event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_SET_CONFIG_VARS, self.onAdminSetConfigVars)
    # Set event handler for ADMIN_SET_CONFIG_VARS_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_SET_CONFIG_VARS_RESPONSE, self.onAdminSetConfigVarsResponse)
    # Set event handler for ADMIN_SUSPEND event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_SUSPEND, self.onAdminSuspend)
    # Set event handler for ADMIN_SUSPEND_RESPONSE event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_SUSPEND_RESPONSE, self.onAdminSuspendResponse)
    # Set event handler for ADMIN_SYSTEM event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_SYSTEM, self.onAdminSystem)
    # Set event handler for ADMIN_SYSTEM event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.ADMIN_SQL_CUSTOM, self.onAdminSQLCustom)
    # Version string init in config vars
    self.configVars[self.VERSION_STRING_NAME] = APP_CONSTS.VERSION_STRING
    # Version string init in stat vars
    self.statFields[self.VERSION_STRING_NAME] = APP_CONSTS.VERSION_STRING

    logger.debug("__init__ finished!")



  # #onAdminState event handler, process state request from admin user API
  #
  # @param event instance of Event object
  def onAdminState(self, event):
    try:
      # get event object
      adminState = event.eventObj
      if adminState.className == self.__class__.__name__:
        # Process himself instance
        self.processOwnStateRequest(event)
      else:
        # Store event information in the queue
        self.tcpServerEventIdToConnectIdentity[event.uid] = event.connect_identity
        # Build new event with the same structure
        requestEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_STATE, adminState)
        # Set the same uid to have a possibility to identify the reply
        requestEvent.uid = event.uid
        if adminState.className in self.adminServerClients:
          # Set connect identity from registered clients
          requestEvent.connect_identity = self.adminServerClients[adminState.className]
          # Send event to the internal Admin connection for target class as third parameter
          self.send(BaseServerManager.ADMIN_CONNECT_ENDPOINT, requestEvent)
        else:
          logger.info("Class instance [" + adminState.className + "] not found ")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminStateResponse event handler, process state request response, send to TCP
  #
  # @param event instance of Event object
  def onAdminStateResponse(self, event):
    try:
      # Get event object
      adminState = event.eventObj
      if adminState.command == dtm.EventObjects.AdminState.STATE_READY:
        # Process READY state, remember  connection identity
        self.adminServerClients[adminState.className] = event.connect_identity
        logger.info("Class instance [" + adminState.className + "] registered!")
      else:
        # Create new event
        replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_STATE_RESPONSE, adminState)
        # Set reply event uid from source request event
        replyEvent.uid = event.uid
        # Set connect_identity from events dict by event.uid
        replyEvent.connect_identity = self.getConnectionIdentityByEvent(event)
        if replyEvent.connect_identity is not None:
          self.send(self.serverHost, replyEvent)
          logger.info("Response to admin client sent!")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminStatData event handler, process get stat data request from admin user API
  #
  # @param event instance of Event object
  def onAdminStatData(self, event):
    try:
      # get event object
      adminStatData = event.eventObj
      if adminStatData.className == self.__class__.__name__:
        # Process himself instance
        logger.debug("Process STAT request for himself!")
        self.processOwnStatDataRequest(event)
      else:
        if adminStatData.className in self.adminServerClients:
          logger.debug("Forward the STAT request for target class [" + adminStatData.className + "]!")
          # Store event information in the queue
          self.tcpServerEventIdToConnectIdentity[event.uid] = event.connect_identity
          # Build new event with the same structure
          requestEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_FETCH_STAT_DATA, adminStatData)
          # Set the same uid to have a possibility to identify the reply
          requestEvent.uid = event.uid
          # Set connect identity from registered clients
          requestEvent.connect_identity = self.adminServerClients[adminStatData.className]
          # Send event to the internal Admin connection for target class as third parameter
          self.send(BaseServerManager.ADMIN_CONNECT_ENDPOINT, requestEvent)
        else:
          # Received wrong class name, do nothing to push the timeout on client-side
          # TODO: Create right response with error message
          logger.debug("Requested STAT request for unregistered class [" + adminStatData.className + "]!")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminStatDataResponse event handler, process stat data request response from thread class, send to TCP
  #
  # @param event instance of Event object
  def onAdminStatDataResponse(self, event):
    try:
      # Get event object
      adminStatData = event.eventObj
      # Create new event
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, adminStatData)
      # Set reply event uid from source request event
      replyEvent.uid = event.uid
      # Set connect_identity from events dict by event.uid
      replyEvent.connect_identity = self.getConnectionIdentityByEvent(event)
      if replyEvent.connect_identity is not None:
        self.send(self.serverHost, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminGetConfigVars event handler, process get config vars request from admin user API
  #
  # @param event instance of Event object
  def onAdminGetConfigVars(self, event):
    try:
      # get event object
      adminConfigVars = event.eventObj
      if adminConfigVars.className == self.__class__.__name__:
        # Process himself instance
        logger.debug("Process GET_CONGIG_VARS request for himself!")
        self.processOwnGetConfigVarsRequest(event)
      else:
        if adminConfigVars.className in self.adminServerClients:
          # Store event information in the queue
          self.tcpServerEventIdToConnectIdentity[event.uid] = event.connect_identity
          # Build new event with the same structure
          requestEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_GET_CONFIG_VARS, adminConfigVars)
          # Set the same uid to have a possibility to identify the reply
          requestEvent.uid = event.uid
          # Set connect identity from registered clients
          requestEvent.connect_identity = self.adminServerClients[adminConfigVars.className]
          # Send event to the internal Admin connection for target class as third parameter
          self.send(BaseServerManager.ADMIN_CONNECT_ENDPOINT, requestEvent)
        else:
          logger.debug("Wrong name of target class [" + adminConfigVars.className + "]")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")



  # #onAdminGetConfigVarsResponse event handler, process get config vars request response from thread class, send to TCP
  #
  # @param event instance of Event object
  def onAdminGetConfigVarsResponse(self, event):
    try:
      # Get event object
      adminConfigVars = event.eventObj
      # Create new event
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_GET_CONFIG_VARS_RESPONSE, adminConfigVars)
      # Set reply event uid from source request event
      replyEvent.uid = event.uid
      # Set connect_identity from events dict by event.uid
      replyEvent.connect_identity = self.getConnectionIdentityByEvent(event)
      if replyEvent.connect_identity is not None:
        self.send(self.serverHost, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminSetConfigVars event handler, process set config vars request from admin user API
  #
  # @param event instance of Event object
  def onAdminSetConfigVars(self, event):
    try:
      # get event object
      adminConfigVars = event.eventObj
      if adminConfigVars.className == self.__class__.__name__:
        # Process himself instance
        logger.debug("Process SET_CONFIG_VARS request for himself!")
        self.processOwnSetConfigVarsRequest(event)
      else:
        if adminConfigVars.className in self.adminServerClients:
          # Store event information in the queue
          self.tcpServerEventIdToConnectIdentity[event.uid] = event.connect_identity
          # Build new event with the same structure
          requestEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SET_CONFIG_VARS, adminConfigVars)
          # Set the same uid to have a possibility to identify the reply
          requestEvent.uid = event.uid
          # Set connect identity from registered clients
          requestEvent.connect_identity = self.adminServerClients[adminConfigVars.className]
          # Send event to the internal Admin connection for target class as third parameter
          self.send(BaseServerManager.ADMIN_CONNECT_ENDPOINT, requestEvent)
        else:
          logger.debug("Wrong name of target class [" + adminConfigVars.className + "]!")
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminSetConfigVarsResponse event handler, process set config vars request response from thread class, send to TCP
  #
  # @param event instance of Event object
  def onAdminSetConfigVarsResponse(self, event):
    try:
      # Get event object
      adminConfigVars = event.eventObj
      # Create new event
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SET_CONFIG_VARS_RESPONSE, adminConfigVars)
      # Set reply event uid from source request event
      replyEvent.uid = event.uid
      # Set connect_identity from events dict by event.uid
      replyEvent.connect_identity = self.getConnectionIdentityByEvent(event)
      if replyEvent.connect_identity is not None:
        self.send(self.serverHost, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminSuspendResponse event handler, process client SUSPEND responses, send to TCP
  #
  # @param event instance of Event object
  def onAdminSuspendResponse(self, event):
    try:
      logger.debug(">>> SuspendResponse uid = " + str(event.uid))
      if event.uid in self.onSuspendConnectionIds:
        for key in self.adminServerClients.keys():
          if self.adminServerClients[key] == self.onSuspendConnectionIds[event.uid]:
            self.onSuspendResponseDict[key] = event.eventObj.errorMessage
        del self.onSuspendConnectionIds[event.uid]
        if len(self.onSuspendConnectionIds) == 0:
          responseObj = dtm.EventObjects.GeneralResponse(dtm.EventObjects.GeneralResponse.ERROR_OK, "All thread response")
          responseObj.statuses.append(self.onSuspendResponseDict)
          replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SUSPEND_RESPONSE, responseObj)
          replyEvent.connect_identity = self.onSuspendConnectionIdent
          if replyEvent.connect_identity is not None:
            self.send(self.serverHost, replyEvent)
            self.onSuspendConnectionIdent = None
            self.onSuspendResponseDict = {}
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #processOwnStateRequest process state request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def processOwnStateRequest(self, event):
    try:
      adminState = event.eventObj
      if adminState.command == dtm.EventObjects.AdminState.STATE_SHUTDOWN:
        # Reply the same object
        replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_STATE_RESPONSE, adminState)
        self.reply(event, replyEvent)
        logger.info("Has successfully shutdown!")
        # Shutdown himself
        self.exit_flag = True
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #processOwnStatDataRequest process stat data request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def processOwnStatDataRequest(self, event):
    try:
      adminStatData = event.eventObj
      fieldsListLen = len(adminStatData.fields)
      # Fill regular fields
      adminStatData.fields = self.getStatDataFields(adminStatData.fields)
      # Fill the FIELD_CLIENTS_LIST if defined in requested fields list or it is empty
      if dtm.EventObjects.AdminStatData.FIELD_CLIENTS_LIST in adminStatData.fields or fieldsListLen == 0:
        # Fill the clients list as classes names
        clientsList = []
        for key in self.adminServerClients.keys():
          clientsList.append(key)
        adminStatData.fields[dtm.EventObjects.AdminStatData.FIELD_CLIENTS_LIST] = clientsList
      # Reply the same object
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, adminStatData)
      self.reply(event, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #getConnectionIdentityByEvent get connect_identity by the event.uid from the tcpServerEventIdToConnectIdentity dict
  # and log error in case of key not present
  #
  # @param event instance of Event object
  # @ret connect_identity in case of success or None if event.uid is not present in
  # the tcpServerEventIdToConnectIdentity
  def getConnectionIdentityByEvent(self, event):
    connect_identity = None

    try:
      # Set connect identity from dic
      connect_identity = self.tcpServerEventIdToConnectIdentity.pop(event.uid)
    except Exception, e:
      logger.error(LogFormatterEvent(event, [], self.ERROR_EVENT_NOT_FOUND + " : " + str(e)))

    return connect_identity


  # #processOwnGetConfigVarsRequest process config vars request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def processOwnGetConfigVarsRequest(self, event):
    try:
      adminConfigVars = event.eventObj
      # Fill regular fields
      adminConfigVars.fields = self.getConfigVarsFields(adminConfigVars.fields)
      # Reply the same object
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_GET_CONFIG_VARS_RESPONSE, adminConfigVars)
      self.reply(event, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #processOwnSetConfigVarsRequest process set config vars request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def processOwnSetConfigVarsRequest(self, event):
    try:
      adminConfigVars = event.eventObj
      # Reply the same object
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SET_CONFIG_VARS_RESPONSE,
                                           self.setConfigVars(adminConfigVars))
      self.reply(event, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #processOwnSetConfigVarsRequest process suspend request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def onAdminSuspend(self, event):
    try:
      if len(self.onSuspendConnectionIds) > 0:
        responseObj = dtm.EventObjects.GeneralResponse(dtm.EventObjects.GeneralResponse.ERROR_OK,
                                                       ">>> Suspend already in progress")
        replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SUSPEND_RESPONSE, responseObj)
        replyEvent.connect_identity = event.connect_identity
        if replyEvent.connect_identity is not None:
          self.send(self.serverHost, replyEvent)
      else:
        suspendObj = event.eventObj
        for clientName in self.adminServerClients:
          self.onSuspendConnectionIdent = event.connect_identity
          # Build new event with the same structure
          requestEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SUSPEND, suspendObj)
          # Set connect identity from registered clients
          requestEvent.connect_identity = self.adminServerClients[clientName]
          # Store event information in the queue
          self.onSuspendConnectionIds[requestEvent.uid] = requestEvent.connect_identity
          # Send event to the internal Admin connection for target class as third parameter
          self.send(BaseServerManager.ADMIN_CONNECT_ENDPOINT, requestEvent)
          logger.debug(">>> SuspendRequest uid = " + str(requestEvent.uid))
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminSystem process request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def onAdminSystem(self, event):
    logger.debug(">>> onAdminSystem uid = " + str(event.uid))
    try:
      if event.eventObj.type is None:
        raise Exception('Wrong event data were got: ' + varDump(event))

      systemCommand = SystemCommandHandler(logger)
      errorCode = systemCommand.execute(event.eventObj.type, event.eventObj.data)
      errorMessage = ''
      if errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK:
        errorMessage = ">>> SystemCommand successfully finished"
      else:
        errorMessage = systemCommand.errorMsg

      responseObj = dtm.EventObjects.GeneralResponse(errorCode, errorMessage)
      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SYSTEM_RESPONSE, responseObj)
      replyEvent.connect_identity = event.connect_identity
      if replyEvent.connect_identity is not None:
        self.send(self.serverHost, replyEvent)

    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onAdminSQLCustom adminSQLCustom process request from admin user API to AdminInterfaceServer object
  #
  # @param event object
  def onAdminSQLCustom(self, event):
    logger.debug(">>> onAdminSQLCustom uid = " + str(event.uid))
    responseObj = dtm.EventObjects.CustomResponse(event.eventObj.rid, event.eventObj.query, "dtm")
    try:
      if self.dbi is not None:
        sqlResponse = self.dbi.sqlCustom(event.eventObj.query)
        responseObj.result = [dict(row) for row in sqlResponse]
        if self.dbi.errorCode != DBI_CONSTANTS.DBI_SUCCESS_CODE:
          responseObj.errString = self.dbi.errorMessage

      replyEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.ADMIN_SQL_CUSTOM_RESPONSE, responseObj)
      self.reply(event, replyEvent)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")
