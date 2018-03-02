'''
HCE project, Python bindings, Distributed Crawler application.
SitesManager object and related classes definitions.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import time
import ctypes
import logging
import zlib
import threading
import json
import ConfigParser


# import pickle
try:
  import cPickle as pickle
except ImportError:
  import pickle

from app.BaseServerManager import BaseServerManager
import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from dc import EventObjects
from dc.Constants import EVENT_TYPES
import dc.Constants as DC_CONSTS
from drce.CommandConvertor import CommandConvertor
from drce.Commands import Session
from drce.Commands import TaskExecuteRequest
from drce.Commands import TaskExecuteStruct
from drce.DRCEManager import ConnectionTimeout, TransportInternalErr, CommandExecutorErr
from drce.DRCEManager import DRCEManager
from drce.DRCEManager import HostParams
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.IDGenerator import IDGenerator
from transport.UIDGenerator import UIDGenerator
import transport.Consts as TRANSPORT_CONSTS
from dbi.EventObjects import CustomRequest

# Logger initialization
logger = Utils.MPLogger().getLogger()
lock = threading.Lock()


# #The SitesManager class, is a main interface of DC application and distributed sites database.
#
# This object is a main interface of DC application and DRCE cluster that operates with distributed DB units
# It supports complete DRCE protocol requests and process responses from DRCE cluster.
#
class SitesManager(BaseServerManager):

  DRCE_REDUCER_TTL = 3000000
  SITE_PROPERTIES_RECRAWL_WHERE_NAME = "RECRAWL_WHERE"
  SITE_PROPERTIES_RECRAWL_DELETE_WHERE_NAME = "RECRAWL_DELETE_WHERE"
  SITE_PROPERTIES_RECRAWL_DELETE_NAME = "RECRAWL_DELETE"
  SITE_PROPERTIES_RECRAWL_OPTIMIZE_NAME = "RECRAWL_OPTIMIZE"

  SITE_PROPERTIES_RECRAWL_PERIOD_MODE_NAME = "RECRAWL_PERIOD_MODE"
  SITE_PROPERTIES_RECRAWL_PERIOD_MIN_NAME = "RECRAWL_PERIOD_MIN"
  SITE_PROPERTIES_RECRAWL_PERIOD_MAX_NAME = "RECRAWL_PERIOD_MAX"
  SITE_PROPERTIES_RECRAWL_PERIOD_STEP_NAME = "RECRAWL_PERIOD_STEP"
  SITE_RECRAWL_THREAD_NAME_PREFIX = 'ReCrawl_'

  # Configuration settings options names
  CONFIG_SERVER = "server"
  CONFIG_DRCE_HOST = "DRCEHost"
  CONFIG_DRCE_PORT = "DRCEPort"
  CONFIG_DRCE_TIMEOUT = "DRCETimeout"
  CONFIG_DRCE_DB_APP_NAME = "DRCEDBAppName"
  CONFIG_RECRAWL_SITES_MAX = "RecrawlSiteMax"
  CONFIG_RECRAWL_SITES_ITER_PERIOD = "RecrawlSiteIterationPeriod"
  CONFIG_RECRAWL_SITES_PERIOD_MODE = "RecrawlSitePeriodMode"
  CONFIG_RECRAWL_SITES_PERIOD_MIN = "RecrawlSitePeriodMin"
  CONFIG_RECRAWL_SITES_PERIOD_MAX = "RecrawlSitePeriodMax"
  CONFIG_RECRAWL_SITES_PERIOD_STEP = "RecrawlSitePeriodStep"
  CONFIG_RECRAWL_SITES_RECRAWL_DATE_EXP = "RecrawlSiteRecrawlDateExpression"
  CONFIG_RECRAWL_SITES_SELECT_CRITERION = "RecrawlSiteSelectCriterion"
  CONFIG_RECRAWL_SITES_SELECT_ORDER = "RecrawlSiteSelectOrder"
  CONFIG_RECRAWL_SITES_MAX_THREADS = "RecrawlSiteMaxThreads"
  CONFIG_RECRAWL_SITES_LOCK_STATE = "RecrawlSiteLockState"
  CONFIG_RECRAWL_SITES_OPTIMIZE = "RecrawlSiteOptimize"
  CONFIG_RECRAWL_SITES_DRCE_TIMEOUT = "RecrawlSiteDRCETimeout"
  CONFIG_RECRAWL_SITES_MODE = "RecrawlSiteMode"
  CONFIG_RECRAWL_DELAY_BEFORE = "RecrawlDelayBefore"
  CONFIG_RECRAWL_DELAY_AFTER = "RecrawlDelayAfter"
  CONFIG_POLLING_TIMEOUT = "PollingTimeout"
  CONFIG_DEFAULT_RECRAWL_UPDATE_CRITERION = "DefaultRecrawUpdatelCriterion"
  CONFIG_DEFAULT_RECRAWL_DELETE_OLD = "DefaultRecrawDeleteOld"
  CONFIG_DEFAULT_RECRAWL_DELETE_OLD_CRITERION = "DefaultRecrawDeleteOldCriterion"
  CONFIG_DRCE_ROUTE = "DRCERoute"
  CONFIG_PURGE_METHOD = "PurgeMethod"
  CONFIG_DRCE_NODES = "DRCENodes"
  CONFIG_COMMON_COMMANDS_THREADING_MODE = "CommonCommandsThreadingMode"

  DRCE_CONNECTIONS_POOL = "DRCEConnectionsPool"
  COMMON_COMMANDS_THREADING_SIMPLE = 0
  COMMON_COMMANDS_THREADING_MULTI = 1
  COMMON_COMMANDS_THREAD_NAME_PREFIX = 'Common_'

  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(SitesManager, self).__init__()

    # Sites re-crawl counter name for stat variables
    self.updateStatField(DC_CONSTS.SITES_RECRAWL_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Sites re-crawl sites updated counter name for stat variables
    self.updateStatField(DC_CONSTS.SITES_RECRAWL_UPDATED_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Sites re-crawl sites deleted counter name for stat variables
    self.updateStatField(DC_CONSTS.SITES_RECRAWL_DELETED_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Sites DRCE requests counter name for stat variables
    self.updateStatField(DC_CONSTS.SITES_DRCE_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)

    # Instantiate the connection builder light if not set
    if connectionBuilderLight is None:
      connectionBuilderLight = ConnectionBuilderLight()

    className = self.__class__.__name__

    # Get configuration settings
    self.serverName = configParser.get(className, self.CONFIG_SERVER)
    self.DRCEDBAppName = configParser.get(className, self.CONFIG_DRCE_DB_APP_NAME)

    # Create connections and raise bind or connect actions for correspondent connection type
    serverConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, self.serverName)

    # Add connections to the polling set
    self.addConnection(self.serverName, serverConnection)

    # Set handlers for all events of SITE and URL operations
    self.eventTypes = {EVENT_TYPES.SITE_NEW:EVENT_TYPES.SITE_NEW_RESPONSE,
                       EVENT_TYPES.SITE_UPDATE:EVENT_TYPES.SITE_UPDATE_RESPONSE,
                       EVENT_TYPES.SITE_STATUS:EVENT_TYPES.SITE_STATUS_RESPONSE,
                       EVENT_TYPES.SITE_DELETE:EVENT_TYPES.SITE_DELETE_RESPONSE,
                       EVENT_TYPES.SITE_CLEANUP:EVENT_TYPES.SITE_CLEANUP_RESPONSE,
                       EVENT_TYPES.SITE_FIND:EVENT_TYPES.SITE_FIND_RESPONSE,
                       EVENT_TYPES.URL_NEW:EVENT_TYPES.URL_NEW_RESPONSE,
                       EVENT_TYPES.URL_STATUS:EVENT_TYPES.URL_STATUS_RESPONSE,
                       EVENT_TYPES.URL_UPDATE:EVENT_TYPES.URL_UPDATE_RESPONSE,
                       EVENT_TYPES.URL_DELETE:EVENT_TYPES.URL_DELETE_RESPONSE,
                       EVENT_TYPES.URL_FETCH:EVENT_TYPES.URL_FETCH_RESPONSE,
                       EVENT_TYPES.URL_CLEANUP:EVENT_TYPES.URL_CLEANUP_RESPONSE,
                       EVENT_TYPES.URL_CONTENT:EVENT_TYPES.URL_CONTENT_RESPONSE,
                       EVENT_TYPES.SQL_CUSTOM:EVENT_TYPES.SQL_CUSTOM_RESPONSE,
                       EVENT_TYPES.URL_PUT:EVENT_TYPES.URL_PUT_RESPONSE,
                       EVENT_TYPES.URL_HISTORY:EVENT_TYPES.URL_HISTORY_RESPONSE,
                       EVENT_TYPES.URL_STATS:EVENT_TYPES.URL_STATS_RESPONSE,
                       EVENT_TYPES.PROXY_NEW:EVENT_TYPES.PROXY_NEW_RESPONSE,
                       EVENT_TYPES.PROXY_UPDATE:EVENT_TYPES.PROXY_UPDATE_RESPONSE,
                       EVENT_TYPES.PROXY_DELETE:EVENT_TYPES.PROXY_DELETE_RESPONSE,
                       EVENT_TYPES.PROXY_STATUS:EVENT_TYPES.PROXY_STATUS_RESPONSE,
                       EVENT_TYPES.PROXY_FIND:EVENT_TYPES.PROXY_FIND_RESPONSE,
                       EVENT_TYPES.ATTR_SET:EVENT_TYPES.ATTR_SET_RESPONSE,
                       EVENT_TYPES.ATTR_UPDATE:EVENT_TYPES.ATTR_UPDATE_RESPONSE,
                       EVENT_TYPES.ATTR_DELETE:EVENT_TYPES.ATTR_DELETE_RESPONSE,
                       EVENT_TYPES.ATTR_FETCH:EVENT_TYPES.ATTR_FETCH_RESPONSE}
    for ret in self.eventTypes:
      self.setEventHandler(ret, self.onEventsHandler)

    # Initialize DRCE API
    self.configVars[self.CONFIG_DRCE_TIMEOUT] = configParser.getint(className, self.CONFIG_DRCE_TIMEOUT)
    self.configVars[self.CONFIG_DRCE_ROUTE] = configParser.get(className, self.CONFIG_DRCE_ROUTE)
    try:
      self.configVars[self.CONFIG_DRCE_NODES] = configParser.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                                                                 self.CONFIG_DRCE_NODES)
    except ConfigParser.NoOptionError:
      self.configVars[self.CONFIG_DRCE_NODES] = 1
    self.drceHost = configParser.get(className, self.CONFIG_DRCE_HOST)
    self.drcePort = configParser.get(className, self.CONFIG_DRCE_PORT)
    hostParams = HostParams(self.drceHost, self.drcePort)
    self.drceManager = DRCEManager()
    self.drceManager.activate_host(hostParams)
    self.drceIdGenerator = UIDGenerator()
    self.drceCommandConvertor = CommandConvertor()

    # Init config vars storage for auto re-crawl
    self.configVars[self.CONFIG_RECRAWL_SITES_MAX] = configParser.getint(className, self.CONFIG_RECRAWL_SITES_MAX)
    self.configVars[self.CONFIG_RECRAWL_SITES_ITER_PERIOD] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_ITER_PERIOD)
    self.configVars[self.CONFIG_RECRAWL_SITES_RECRAWL_DATE_EXP] = \
                   configParser.get(className, self.CONFIG_RECRAWL_SITES_RECRAWL_DATE_EXP)
    self.configVars[self.CONFIG_RECRAWL_SITES_SELECT_CRITERION] = \
                   configParser.get(className, self.CONFIG_RECRAWL_SITES_SELECT_CRITERION)
    self.configVars[self.CONFIG_RECRAWL_SITES_SELECT_ORDER] = \
                   configParser.get(className, self.CONFIG_RECRAWL_SITES_SELECT_ORDER)
    self.configVars[self.CONFIG_RECRAWL_SITES_LOCK_STATE] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_LOCK_STATE)
    self.configVars[self.CONFIG_RECRAWL_SITES_OPTIMIZE] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_OPTIMIZE)
    self.configVars[self.CONFIG_RECRAWL_SITES_DRCE_TIMEOUT] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_DRCE_TIMEOUT)
    self.configVars[self.CONFIG_RECRAWL_DELAY_BEFORE] = configParser.getint(className, self.CONFIG_RECRAWL_DELAY_BEFORE)
    self.configVars[self.CONFIG_RECRAWL_DELAY_AFTER] = configParser.getint(className, self.CONFIG_RECRAWL_DELAY_AFTER)
    self.processRecrawlLastTs = time.time()

    # Set connections poll timeout, defines period of HCE cluster monitoring cycle, msec
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_POLLING_TIMEOUT)

    # Init default re-crawl update criterion
    self.configVars[self.CONFIG_DEFAULT_RECRAWL_UPDATE_CRITERION] = \
         configParser.get(className, self.CONFIG_DEFAULT_RECRAWL_UPDATE_CRITERION)

    # Init default re-crawl delete old URLs operation
    self.configVars[self.CONFIG_DEFAULT_RECRAWL_DELETE_OLD] = \
         configParser.getint(className, self.CONFIG_DEFAULT_RECRAWL_DELETE_OLD)
    # Init default re-crawl delete old URLs operation's criterion
    self.configVars[self.CONFIG_DEFAULT_RECRAWL_DELETE_OLD_CRITERION] = \
         configParser.get(className, self.CONFIG_DEFAULT_RECRAWL_DELETE_OLD_CRITERION)
    # Init default re-crawl threads max number
    self.configVars[self.CONFIG_RECRAWL_SITES_MAX_THREADS] = \
         configParser.getint(className, self.CONFIG_RECRAWL_SITES_MAX_THREADS)
    # Init re-crawl mode
    self.configVars[self.CONFIG_RECRAWL_SITES_MODE] = \
         configParser.getint(className, self.CONFIG_RECRAWL_SITES_MODE)

    # Init sites re-crawl queue
    self.recrawlSiteslQueue = {}
    # Init sites re-crawl threads counter
    self.updateStatField(DC_CONSTS.RECRAWL_THREADS_COUNTER_QUEUE_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Init sites re-crawl threads counter
    self.updateStatField(DC_CONSTS.RECRAWL_SITES_QUEUE_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Init sites re-crawl threads created counter
    self.updateStatField(DC_CONSTS.RECRAWL_THREADS_CREATED_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_SET)

    # Purge algorithm init
    self.configVars[self.CONFIG_PURGE_METHOD] = configParser.getint(className, self.CONFIG_PURGE_METHOD)

    # Recrawl period mode
    self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_MODE] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_PERIOD_MODE)
    self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_MIN] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_PERIOD_MIN)
    self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_MAX] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_PERIOD_MAX)
    self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_STEP] = \
                   configParser.getint(className, self.CONFIG_RECRAWL_SITES_PERIOD_STEP)

    # Init common operations variables
    # Init common threads created counter
    self.updateStatField(DC_CONSTS.COMMON_THREADS_CREATED_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Init sites re-crawl threads counter
    self.updateStatField(DC_CONSTS.COMMON_THREADS_COUNTER_QUEUE_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Common operations counter name for stat variables
    self.updateStatField(DC_CONSTS.COMMON_OPERATIONS_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)

    # Init DRCE connections pool and event types / commands assignment
    try:
      self.drceConnectionsPool = json.loads(configParser.get(className, self.DRCE_CONNECTIONS_POOL))
    except ConfigParser.NoOptionError:
      self.drceConnectionsPool = None
    except Exception as err:
      logger.error("Error de-serialize json of connection parameters for DRCE connections pool: %s", err)
      self.drceConnectionsPool = None

    # Init common commands threading model
    try:
      self.configVars[self.CONFIG_COMMON_COMMANDS_THREADING_MODE] = \
                      configParser.getint(className, self.CONFIG_COMMON_COMMANDS_THREADING_MODE)
    except ConfigParser.NoOptionError:
      self.configVars[self.CONFIG_COMMON_COMMANDS_THREADING_MODE] = self.COMMON_COMMANDS_THREADING_SIMPLE



  # #Events wait timeout handler, for timeout state of the connections polling. Executes periodical check of DTM tasks
  # and initiate the main crawling iteration cycle
  #
  def on_poll_timeout(self):
    logger.debug("Periodic iteration started.")
    try:
      # Process periodic re-crawling
      if self.configVars[self.CONFIG_RECRAWL_SITES_ITER_PERIOD] > 0 and\
        time.time() - self.processRecrawlLastTs > self.configVars[self.CONFIG_RECRAWL_SITES_ITER_PERIOD]:
        if self.configVars[self.CONFIG_RECRAWL_SITES_MODE] == 1:
          logger.debug("Now time to try to perform re-crawl, interval %s",
                       str(self.configVars[self.CONFIG_RECRAWL_SITES_ITER_PERIOD]))
          if self.configVars[self.CONFIG_RECRAWL_SITES_MAX_THREADS] > \
            self.statFields[DC_CONSTS.RECRAWL_THREADS_COUNTER_QUEUE_NAME]:
            self.processRecrawlLastTs = time.time()
            logger.info("Forking new recrawl thread")
            self.updateStatField(DC_CONSTS.RECRAWL_THREADS_CREATED_COUNTER_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            t1 = threading.Thread(target=self.processRecrawling, args=(logging,))
            t1.setName(self.SITE_RECRAWL_THREAD_NAME_PREFIX + \
                       str(self.statFields[DC_CONSTS.RECRAWL_THREADS_CREATED_COUNTER_NAME]))
            t1.start()
            logger.info("New recrawl thread forked")
          else:
            # Max threads limit reached
            logger.debug("Max recrawl threads limit reached %s",
                         str(self.configVars[self.CONFIG_RECRAWL_SITES_MAX_THREADS]))
        else:
          logger.debug("Re-crawl disabled!")
    except IOError as e:
      del e
    except Exception as err:
      Utils.ExceptionLog.handler(logger, err, "Exception:")

    logger.debug("Periodic iteration finished.")



  # #onEventsHandler event handler for all requests
  #
  # @param event instance of Event object
  def onEventsHandler(self, event):
    try:
      if self.configVars[self.CONFIG_COMMON_COMMANDS_THREADING_MODE] == self.COMMON_COMMANDS_THREADING_SIMPLE:
        logger.info("Common command in simple mode")
        # Call threa-safe handler direct way as simple single m-type hce-node cluster
        self.eventsHandlerTS(event, logging)
      else:
        # Call threa-safe handler multi-thread way as multi m-type hce-node cluster
        logger.info("Forking new common commands thread")
        self.updateStatField(DC_CONSTS.COMMON_THREADS_CREATED_COUNTER_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
        t2 = threading.Thread(target=self.eventsHandlerTS, args=(event, logging,))
        t2.setName(self.COMMON_COMMANDS_THREAD_NAME_PREFIX + \
                   str(self.statFields[DC_CONSTS.COMMON_THREADS_CREATED_COUNTER_NAME]))
        t2.start()
        logger.info("New common commands thread forked")
    except IOError as e:
      del e
    except Exception as err:
      Utils.ExceptionLog.handler(logger, err, "Exception:")

    self.on_poll_timeout()



  # #eventsHandlerThread thread-safe event handler for all requests
  #
  # @param event instance of Event object
  # @param loggingObj
  def eventsHandlerTS(self, event, loggingObj):
    global logger  # pylint: disable=W0603

    lock.acquire()
    logger = loggingObj.getLogger(DC_CONSTS.LOGGER_NAME)
    if self.configVars[self.CONFIG_COMMON_COMMANDS_THREADING_MODE] == self.COMMON_COMMANDS_THREADING_MULTI:
      self.updateStatField(DC_CONSTS.COMMON_THREADS_COUNTER_QUEUE_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
    self.updateStatField(DC_CONSTS.COMMON_OPERATIONS_COUNTER_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
    # Fix some fields values (limits) of event object using the nodes number if >1
    if self.configVars[self.CONFIG_DRCE_NODES] > 1:
      self.fixFields(event, self.configVars[self.CONFIG_DRCE_NODES])
    logger.debug("Request event:\n" + Utils.varDump(event))
    # Prepare DRCE request
    drceRequest = self.prepareDRCERequest(event.eventType, event.eventObj)
    if self.configVars[self.CONFIG_COMMON_COMMANDS_THREADING_MODE] == self.COMMON_COMMANDS_THREADING_MULTI:
      connectionParams, timeout = self.getDRCEConnectionParamsFromPool(event.eventType)
      persistentConnection = False
    else:
      connectionParams = None
      timeout = -1
      persistentConnection = True
    lock.release()

    # Send DRCE request
    clientResponseObj = self.processDRCERequest(drceRequest, persistentConnection, timeout, connectionParams)
    logger.debug("Response ClientResponseObj:\n" + Utils.varDump(clientResponseObj))

    lock.acquire()
    # Prepare reply event
    replyEvent = self.eventBuilder.build(self.eventTypes[event.eventType], clientResponseObj)

    # Append source event cookies because they will be copied to reply event
    if event.eventType == EVENT_TYPES.URL_CONTENT:
      if event.cookie is None:
        event.cookie = {}
      if isinstance(event.cookie, dict):
        event.cookie[EventObjects.URLFetch.CRITERION_ORDER] = []
        for urlContentRequestItem in event.eventObj:
          if urlContentRequestItem.urlFetch is not None and\
            EventObjects.URLFetch.CRITERION_ORDER in urlContentRequestItem.urlFetch.urlsCriterions:
            event.cookie[EventObjects.URLFetch.CRITERION_ORDER].append(
                        urlContentRequestItem.urlFetch.urlsCriterions[EventObjects.URLFetch.CRITERION_ORDER])  # pylint: disable=C0330
          else:
            event.cookie[EventObjects.URLFetch.CRITERION_ORDER].append("")
      if len(event.cookie) == 0:
        event.cookie = None

    if event.eventType == EVENT_TYPES.URL_FETCH:
      if event.cookie is None:
        event.cookie = {}
      if isinstance(event.cookie, dict):
        event.cookie[EventObjects.URLFetch.CRITERION_ORDER] = []
        for urlFetchRequestItem in event.eventObj:
          if EventObjects.URLFetch.CRITERION_ORDER in urlFetchRequestItem.urlsCriterions:
            event.cookie[EventObjects.URLFetch.CRITERION_ORDER].append(
                        urlFetchRequestItem.urlsCriterions[EventObjects.URLFetch.CRITERION_ORDER])  # pylint: disable=C0330
          else:
            event.cookie[EventObjects.URLFetch.CRITERION_ORDER].append("")
      if len(event.cookie) == 0:
        event.cookie = None

    # Send reply
    self.reply(event, replyEvent)
    logger.info("Reply sent")
    lock.release()

    lock.acquire()
    if self.configVars[self.CONFIG_COMMON_COMMANDS_THREADING_MODE] == self.COMMON_COMMANDS_THREADING_MULTI:
      self.updateStatField(DC_CONSTS.COMMON_THREADS_COUNTER_QUEUE_NAME, 1, self.STAT_FIELDS_OPERATION_SUB)
    lock.release()



  # #Get connection ((hots, port), timeout) tuple of tuples by the event type or tuple (None, -1)
  #
  # @param eventType event type from Constants
  # @return the tuple of tuples ((host, port), timeout) or tuple (None, -1)
  def getDRCEConnectionParamsFromPool(self, eventType):
    ret = (None, -1)

    if self.drceConnectionsPool is not None:
      try:
        for item in self.drceConnectionsPool:
          if eventType in self.drceConnectionsPool[item]:
            parts = item.split(':')
            if len(parts) > 2:
              ret = ((parts[0], int(parts[1])), int(parts[2]))
              logger.info("Connection options found for event %s: %s", str(eventType), str(ret))
              break
            else:
              logger.error("Wrong items number 'host:port:timeout' in DRCE connections pool key: %s", str(item))
      except Exception as err:
        logger.error("Error get DRCE connection parameters, possible wrong ini value for DRCE connections pool: %s\n%s",
                     err, str(self.drceConnectionsPool))

    return ret



  # #Prepare DRCE request
  #
  # @param eventType event type from Constants
  # @param eventObj instance of Event object
  # @return the TaskExecuteStruct object instance
  def prepareDRCERequest(self, eventType, eventObj):
    # Prepare DRCE request data
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(eventType, eventObj)
    # Prepare DRCE request object
    taskExecuteStruct = TaskExecuteStruct()
    taskExecuteStruct.command = self.DRCEDBAppName
    taskExecuteStruct.input = pickle.dumps(drceSyncTasksCoverObj)
    taskExecuteStruct.session = Session(Session.TMODE_SYNC)
    logger.debug("DRCE taskExecuteStruct:\n" + Utils.varDump(taskExecuteStruct))

    return taskExecuteStruct



  # #Request action processor for DRCE DB cluster
  #
  # @param taskExecuteStruct object
  # @param persistentDCREConnection use persistent single connection to the DRCE or new per each request, boolean
  # @param connectionParams - tuple (host, port) for additional m-type hce-node cluster
  def processDRCERequest(self, taskExecuteStruct, persistentDCREConnection=True, timeout=-1, connectionParams=None):
    lock.acquire()
    # Create DRCE TaskExecuteRequest object
    idGenerator = IDGenerator()
    taskId = ctypes.c_uint32(zlib.crc32(idGenerator.get_connection_uid(), int(time.time()))).value
    taskExecuteRequest = TaskExecuteRequest(taskId)
    if self.configVars[self.CONFIG_DRCE_ROUTE] != "":
      taskExecuteRequest.route = self.configVars[self.CONFIG_DRCE_ROUTE]
    # Set taskExecuteRequest fields
    taskExecuteRequest.data = taskExecuteStruct
    lock.release()

    logger.info("Sending sync task id:" + str(taskId) + " to DRCE router!")
    # Send request to DRCE Cluster router
    response = self.sendToDRCERouter(taskExecuteRequest, persistentDCREConnection, timeout, connectionParams)
    logger.info("Received response on sync task from DRCE router!")
    logger.debug("Response: %s", Utils.varDump(response))

    # Create new client response object
    clientResponse = EventObjects.ClientResponse()
    # Check response returned
    if response is None:
      clientResponse.errorCode = EventObjects.ClientResponse.STATUS_ERROR_NONE
      clientResponse.errorMessage = "Response error, None returned from DRCE, possible timeout " + \
                                    str(self.configVars[self.CONFIG_DRCE_TIMEOUT]) + " msec!"
      logger.error(clientResponse.errorMessage)
    else:
      if len(response.items) == 0:
        clientResponse.errorCode = EventObjects.ClientResponse.STATUS_ERROR_EMPTY_LIST
        clientResponse.errorMessage = "Response error, empty list returned from DRCE, possible no one node in cluster!"
        logger.error(clientResponse.errorMessage)
      else:
        for item in response.items:
          # New ClientResponseItem object
          clientResponseItem = EventObjects.ClientResponseItem(None)
          # If some error in response item or cli application exit status
          if item.error_code > 0 or item.exit_status > 0:
            clientResponseItem.errorCode = clientResponseItem.STATUS_ERROR_DRCE
            clientResponseItem.errorMessage = "Response item error error_message=" + item.error_message + \
                                              ", error_code=" + str(item.error_code) + \
                                              ", exit_status=" + str(item.exit_status) + \
                                              ", stderror=" + str(item.stderror)
            logger.error(clientResponseItem.errorMessage)
          else:
            # Try to restore serialized response object from dump
            try:
              drceSyncTasksCover = pickle.loads(item.stdout)
              clientResponseItem.itemObject = drceSyncTasksCover.eventObject
            except Exception as e:
              clientResponseItem.errorCode = EventObjects.ClientResponseItem.STATUS_ERROR_RESTORE_OBJECT
              clientResponseItem.errorMessage = EventObjects.ClientResponseItem.MSG_ERROR_RESTORE_OBJECT + "\n" + \
                                                str(e.message) + "\nstdout=" + str(item.stdout) + \
                                                ", stderror=" + str(item.stderror)
              logger.error(clientResponseItem.errorMessage)
          # Set all information fields in any case
          clientResponseItem.id = item.id
          clientResponseItem.host = item.host
          clientResponseItem.port = item.port
          clientResponseItem.node = item.node
          clientResponseItem.time = item.time
          # Add ClientResponseItem object
          clientResponse.itemsList.append(clientResponseItem)

    return clientResponse



  # #Send to send to DRCE Router transport router connection
  #
  # @param messageBody body of the message
  # @param persistentDCREConnection use persistent DRCE connection or new
  # @param connectionParams - tuple (host, port) for additional m-type hce-node cluster
  # @return EEResponseData object instance
  def sendToDRCERouter(self, request, persistentDCREConnection=True, timeout=-1, connectionParams=None):
    lock.acquire()
    if timeout == -1:
      timeout = int(self.configVars[self.CONFIG_DRCE_TIMEOUT])
    self.updateStatField(DC_CONSTS.SITES_DRCE_COUNTER_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
    if persistentDCREConnection:
      logger.info("DRCE router sending via persistent connection with timeout=%s", str(timeout))
      drceManager = self.drceManager
    else:
      drceManager = DRCEManager()
      if connectionParams is None:
        drceManager.activate_host(HostParams(self.drceHost, self.drcePort))
        logger.info("DRCE router sending via temporary connection with timeout=" + str(timeout) + \
                    ", and regular host:" + str(self.drceHost) + ", port:" + str(self.drcePort))
      else:
        logger.info("DRCE router sending via temporary connection with timeout=" + str(timeout) + \
                    ", and DRCE connections pool host:" + str(connectionParams[0]) + \
                    ", port:" + str(connectionParams[1]))
        drceManager.activate_host(HostParams(connectionParams[0], int(connectionParams[1])))
    lock.release()

    # Try to execute request
    try:
      response = drceManager.process(request, timeout, self.DRCE_REDUCER_TTL)
    except (ConnectionTimeout, TransportInternalErr, CommandExecutorErr) as err:
      response = None
      logger.error("DRCE router transport send error : " + str(err.message))
    except Exception as err:
      response = None
      logger.error("DRCE router common error : " + str(err.message))

    logger.info("DRCE router sent!")

    if not persistentDCREConnection:
      lock.acquire()
      drceManager.clear_host()
      lock.release()

    return response



  # #Process periodic auto re-crawling with new thread as method function
  # @param logging object instance
  #
  #
  def processRecrawling(self, loggingObj):
    try:
      global logger  # pylint: disable=W0603
      lock.acquire()
      logger = loggingObj.getLogger(DC_CONSTS.LOGGER_NAME)
      self.updateStatField(DC_CONSTS.RECRAWL_THREADS_COUNTER_QUEUE_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
      self.updateStatField(DC_CONSTS.SITES_RECRAWL_COUNTER_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
      lock.release()
      logger.info("RECRAWL_THREAD_STARTED")
      # Set timeout in msecs
      timeout = self.configVars[self.CONFIG_RECRAWL_SITES_DRCE_TIMEOUT] * 1000

      # Find sites that need to be re-crawled
      crit = {EventObjects.SiteFind.CRITERION_WHERE: self.configVars[self.CONFIG_RECRAWL_SITES_SELECT_CRITERION],
              EventObjects.SiteFind.CRITERION_ORDER: self.configVars[self.CONFIG_RECRAWL_SITES_SELECT_ORDER],
              EventObjects.SiteFind.CRITERION_LIMIT: str(self.configVars[self.CONFIG_RECRAWL_SITES_MAX])}
      siteFind = EventObjects.SiteFind(None, crit)
      logger.debug("Send DRCE request SITE_FIND")
      clientResponse = self.processDRCERequest(self.prepareDRCERequest(EVENT_TYPES.SITE_FIND, siteFind), False, timeout)
      logger.debug("clientResponse:" + Utils.varDump(clientResponse))

      lock.acquire()
      # Process results and create unique sites dict
      sites = self.getSitesFromClientResponseItems(clientResponse.itemsList)
      lock.release()

      sitesQueue = {}
      for siteId in sites.keys():
        if siteId in self.recrawlSiteslQueue:
          # Site is already in progress of recrawl by some thread
          logger.debug("Site %s is already in progress of recrawl by some thread", str(siteId))
          continue

        lock.acquire()
        # Push site item in to the cross-threading queue
        t1 = time.time()
        self.recrawlSiteslQueue[str(siteId)] = {"siteObj":sites[siteId], "time":t1}
        # Push Site item in to the local queue
        sitesQueue[str(siteId)] = {"time":t1}
        # Refresh stat queue size
        self.updateStatField(DC_CONSTS.RECRAWL_SITES_QUEUE_NAME, len(self.recrawlSiteslQueue),
                             self.STAT_FIELDS_OPERATION_SET)
        lock.release()

        urlUpdateList = []
        urlDeleteList = []
        logger.debug("Site selected for recrawl, site[" + str(siteId) + "]:\n" + Utils.varDump(sites[siteId]))
        # Save prev. site state to restore after re-crawl will be finished
        sitePrevState = sites[siteId].state
        # Update site including lock by state
        siteUpdate = EventObjects.SiteUpdate(siteId)
        siteUpdate.iterations = EventObjects.SQLExpression("Iterations+1")
        siteUpdate.tcDate = EventObjects.SQLExpression("Now()")
        siteUpdate.uDate = siteUpdate.tcDate
        if sites[siteId].recrawlPeriod > 0 and self.configVars[self.CONFIG_RECRAWL_SITES_RECRAWL_DATE_EXP] != "":
          # Set next re-crawl date if periodic re-crawl
          siteUpdate.recrawlDate = \
                                EventObjects.SQLExpression(self.configVars[self.CONFIG_RECRAWL_SITES_RECRAWL_DATE_EXP])
        else:
          # Disable re-crawl
          siteUpdate.recrawlDate = EventObjects.SQLExpression("NULL")
        if self.configVars[self.CONFIG_RECRAWL_SITES_LOCK_STATE] != "":
          # Set state to lock site
          siteUpdate.state = int(self.configVars[self.CONFIG_RECRAWL_SITES_LOCK_STATE])
        else:
          logger.debug("Site is not locked due empty string value of configuration parameter %s",
                       self.CONFIG_RECRAWL_SITES_LOCK_STATE)
        logger.debug("Update site request including lock state if configured, id=%s", str(siteId))
        # Update site fields
        clientResponse = self.processDRCERequest(self.prepareDRCERequest(EVENT_TYPES.SITE_UPDATE, siteUpdate), False,
                                                 timeout)
        logger.debug("Update site request done, id=%s", str(siteId))
        # Check responses on errors
        lock.acquire()
        self.logGeneralResponseResults(clientResponse)
        lock.release()

        if self.configVars[self.CONFIG_RECRAWL_DELAY_BEFORE] > 0:
          # Delay after set site state SUSPENDED
          logger.debug("Delay before, %s sec...", str(self.configVars[self.CONFIG_RECRAWL_DELAY_BEFORE]))
          time.sleep(self.configVars[self.CONFIG_RECRAWL_DELAY_BEFORE])

        # Prepare URLs update
        urlUpdate = EventObjects.URLUpdate(siteId, "")
        urlUpdate.url = None
        urlUpdate.urlMd5 = None
        urlUpdate.status = EventObjects.URLUpdate.STATUS_NEW
        crit = EventObjects.Site.getFromProperties(sites[siteId].properties, self.SITE_PROPERTIES_RECRAWL_WHERE_NAME)
        if crit is None or crit == "":
          crit = self.configVars[self.CONFIG_DEFAULT_RECRAWL_UPDATE_CRITERION]
          logger.debug("Default update criterion: " + str(crit))
        else:
          logger.debug("Custom site update criterion: " + str(crit))
        urlUpdate.criterions = {EventObjects.URLFetch.CRITERION_WHERE : crit}
        urlUpdateList.append(urlUpdate)
        # Delete old URLs from prev. re-crawling iteration
        if self.configVars[self.CONFIG_DEFAULT_RECRAWL_DELETE_OLD] > 0:
          sqlExpression = EventObjects.SQLExpression(self.configVars[self.CONFIG_DEFAULT_RECRAWL_DELETE_OLD_CRITERION])
          siteDelOld = EventObjects.Site.getFromProperties(sites[siteId].properties,
                                                           self.SITE_PROPERTIES_RECRAWL_DELETE_NAME)
          if siteDelOld is None or siteDelOld != "0":
            siteSqlExpression = EventObjects.Site.getFromProperties(sites[siteId].properties,
                                                                    self.SITE_PROPERTIES_RECRAWL_DELETE_WHERE_NAME)
            logger.debug("Site expression: " + str(siteSqlExpression))
            if siteSqlExpression is not None and siteSqlExpression != "":
              sqlExpression = siteSqlExpression
              logger.debug("Custom expression set: " + str(sqlExpression))
          else:
            logger.debug("Site delete old: " + str(siteDelOld))
          urlDelete = EventObjects.URLDelete(siteId, None, EventObjects.URLStatus.URL_TYPE_MD5,
                                             {EventObjects.URLFetch.CRITERION_WHERE:sqlExpression},
                                             reason=EventObjects.URLDelete.REASON_RECRAWL)
          urlDelete.urlType = None
          urlDelete.delayedType = self.configVars[self.CONFIG_PURGE_METHOD]
          logger.debug("Old URLs delete due re-crawl: " + Utils.varDump(urlDelete))
          urlDeleteList.append(urlDelete)
          logger.debug("URLDelete request, id=%s", str(siteId))
          # Delete old URLs from prev. re-crawling
          clientResponse = self.processDRCERequest(self.prepareDRCERequest(EVENT_TYPES.URL_DELETE, urlDeleteList),
                                                   False, timeout)
          logger.debug("URLDelete request done, id=%s", str(siteId))
          lock.acquire()
          self.updateStatField(DC_CONSTS.SITES_RECRAWL_DELETED_COUNTER_NAME, len(urlDeleteList),
                               self.STAT_FIELDS_OPERATION_ADD)
          # Check responses on errors
          self.logGeneralResponseResults(clientResponse)
          lock.release()

        # Optimize urls table
        optimize = EventObjects.Site.getFromProperties(sites[siteId].properties,
                                                       self.SITE_PROPERTIES_RECRAWL_OPTIMIZE_NAME)
        if (int(self.configVars[self.CONFIG_RECRAWL_SITES_OPTIMIZE]) == 1 and optimize is None) or int(optimize) == 1:
          sqlQuery = "OPTIMIZE TABLE `urls_" + str(siteId) + "`"
          logger.debug("CustomRequest query: %s", sqlQuery)
          customRequest = CustomRequest(1, sqlQuery, "dc_urls")
          # OPTIMIZE TABLE request
          customResponse = self.processDRCERequest(self.prepareDRCERequest(EVENT_TYPES.SQL_CUSTOM, customRequest),
                                                   False, timeout)
          logger.debug("CustomRequest request done, id=%s, customResponse:\n%s", str(siteId),
                       Utils.varDump(customResponse))

        # Auto tune RecrawlPeriod
        recrawlPeriod = self.recalculateRecrawlPeriod(sites[siteId])
        if recrawlPeriod is not None:
          siteUpdate.recrawlPeriod = recrawlPeriod

        # Update URLs to push them to start crawling
        clientResponse = self.processDRCERequest(self.prepareDRCERequest(EVENT_TYPES.URL_UPDATE, urlUpdateList), False,
                                                 timeout)
        lock.acquire()
        self.updateStatField(DC_CONSTS.SITES_RECRAWL_UPDATED_COUNTER_NAME, len(urlUpdateList),
                             self.STAT_FIELDS_OPERATION_ADD)
        # Check responses on errors
        self.logGeneralResponseResults(clientResponse)
        lock.release()

        if self.configVars[self.CONFIG_RECRAWL_DELAY_AFTER] > 0:
          # Delay after re-crawl processing done
          logger.debug("Delay after, %s sec...", str(self.configVars[self.CONFIG_RECRAWL_DELAY_AFTER]))
          time.sleep(self.configVars[self.CONFIG_RECRAWL_DELAY_AFTER])

        # Return site to previous state, i.e. unlock
        if self.configVars[self.CONFIG_RECRAWL_SITES_LOCK_STATE] != "":
          # Set state to unlock site
          siteUpdate.state = sitePrevState
          siteUpdate.iterations = None
          siteUpdate.tcDate = EventObjects.SQLExpression("Now()")
          siteUpdate.uDate = None
          siteUpdate.recrawlDate = None
          logger.debug("Unlock site request, id=%s", str(siteId))
          # Update site fields
          clientResponse = self.processDRCERequest(self.prepareDRCERequest(EVENT_TYPES.SITE_UPDATE, siteUpdate), False,
                                                   timeout)
          logger.debug("Unlock site request done, id=%s", str(siteId))
          # Check responses on errors
          lock.acquire()
          self.logGeneralResponseResults(clientResponse)
          lock.release()
        else:
          logger.debug("Site is not unlocked due empty string value of configuration parameter %s",
                       self.CONFIG_RECRAWL_SITES_LOCK_STATE)
      # lock.acquire()
      # self.totalTime = self.totalTime + (time.time() - t)
      # self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TIME_AVG_NAME,
      #                   str(self.totalTime / float(1 + self.statFields[DC_CONSTS.BATCHES_CRAWL_COUNTER_TOTAL_NAME])),
      #                   self.STAT_FIELDS_OPERATION_SET)
      # lock.release()
    except Exception as err:
      lock.acquire()
      logger.error("Recrawl thread exception:" + str(err))
      lock.release()
    except:  # pylint: disable=W0702
      lock.acquire()
      logger.error("Recrawl thread unknown exception!")
      lock.release()

    lock.acquire()
    # Remove processed sites from global the cross-threading queue
    tmpQueue = {}
    for siteId in self.recrawlSiteslQueue.keys():
      if siteId not in sitesQueue:
        # Accumulate only items that is not processed by this thread
        tmpQueue[str(siteId)] = self.recrawlSiteslQueue[str(siteId)]
    # Replace current queue with accumulated queue
    self.recrawlSiteslQueue = tmpQueue
    # Decrement of counter of threads
    self.updateStatField(DC_CONSTS.RECRAWL_THREADS_COUNTER_QUEUE_NAME, 1, self.STAT_FIELDS_OPERATION_SUB)
    # Refresh stat queue size
    self.updateStatField(DC_CONSTS.RECRAWL_SITES_QUEUE_NAME, len(self.recrawlSiteslQueue),
                         self.STAT_FIELDS_OPERATION_SET)
    logger.info("RECRAWL_THREAD_FINISHED")
    lock.release()



  # #Get sites dict {SiteId:Site} from the ClientResponse object items
  #
  # @param clientResponseItems The list of ClientResponseItem objects
  def getSitesFromClientResponseItems(self, clientResponseItems):
    batchItemsCounter = 0
    batchItemsTotalCounter = 0
    uniqueSitesDic = {}

    for item in clientResponseItems:
      if item.errorCode == EventObjects.ClientResponseItem.STATUS_OK:
        if isinstance(item.itemObject, list):
          for site in item.itemObject:
            batchItemsTotalCounter = batchItemsTotalCounter + 1
            if isinstance(site, EventObjects.Site):
              if str(site.id) not in uniqueSitesDic:
                uniqueSitesDic[str(site.id)] = site
                batchItemsCounter = batchItemsCounter + 1
              else:
                # Sum for counters fields
                uniqueSitesDic[str(site.id)].newURLs = uniqueSitesDic[str(site.id)].newURLs + site.newURLs
                uniqueSitesDic[str(site.id)].collectedURLs = uniqueSitesDic[str(site.id)].collectedURLs + \
                                                             site.collectedURLs
                uniqueSitesDic[str(site.id)].deletedURLs = uniqueSitesDic[str(site.id)].deletedURLs + site.deletedURLs
                uniqueSitesDic[str(site.id)].contents = uniqueSitesDic[str(site.id)].contents + site.contents
                uniqueSitesDic[str(site.id)].resources = uniqueSitesDic[str(site.id)].resources + site.resources
            else:
              logger.error("Wrong object type in the itemObject.item: " + str(type(site)) + \
                           " but 'Site' expected")
        else:
          logger.error("Wrong object type in the ClientResponseItem.itemObject: " + str(type(item.itemObject)) + \
                       " but 'list' expected")
      else:
        logger.debug("ClientResponseItem error: " + str(item.errorCode) + " : " + item.errorMessage)

    logger.debug("Unique sites: " + str(batchItemsCounter) + ", total sites: " + str(batchItemsTotalCounter))

    return uniqueSitesDic



  # #Recalculates the RecrawlPeriod value for the site if auto tune up is ON
  #
  # @param siteObj The Site object
  def recalculateRecrawlPeriod(self, siteObj):
    recrawlPeriod = None

    # Init per site settings
    mode = EventObjects.Site.getFromProperties(siteObj.properties, self.SITE_PROPERTIES_RECRAWL_PERIOD_MODE_NAME)
    if mode is None:
      mode = self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_MODE]
    else:
      mode = int(mode)
    minv = EventObjects.Site.getFromProperties(siteObj.properties, self.SITE_PROPERTIES_RECRAWL_PERIOD_MIN_NAME)
    if minv is None:
      minv = self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_MIN]
    else:
      minv = int(minv)
    maxv = EventObjects.Site.getFromProperties(siteObj.properties, self.SITE_PROPERTIES_RECRAWL_PERIOD_MAX_NAME)
    if maxv is None:
      maxv = self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_MAX]
    else:
      maxv = int(maxv)
    step = EventObjects.Site.getFromProperties(siteObj.properties, self.SITE_PROPERTIES_RECRAWL_PERIOD_STEP_NAME)
    if step is None:
      step = self.configVars[self.CONFIG_RECRAWL_SITES_PERIOD_STEP]
    else:
      step = int(step)

    logger.debug("RecrawlPeriod auto recalculate, siteId:%s, mode:%s, minv:%s, maxv:%s, step:%s", str(siteObj.id),
                 str(mode), str(minv), str(maxv), str(step))

    # If recrawl period recalculation mode is ON
    if mode > 0:
      logger.debug("RecrawlPeriod auto recalculate is ON, siteId:%s, current value:%s",
                   str(siteObj.id), str(siteObj.recrawlPeriod))
      # If not all URLS in state NEW are crawled or processed (siteObj.resources - means crawled but not processed)
      if siteObj.newURLs > 0 or siteObj.resources > 0:
        # If maximum value of period is not reached
        if siteObj.recrawlPeriod < maxv:
          # Increase period on step value
          recrawlPeriod = siteObj.recrawlPeriod + step
        else:
          logger.debug("Max value of RecrawlPeriod reached:%s", str(maxv))
      else:
        # If minimum value of period is not reached
        if siteObj.recrawlPeriod > minv:
          # Decrease the period on step value
          recrawlPeriod = siteObj.recrawlPeriod - step
        else:
          logger.debug("Min value of RecrawlPeriod reached:%s", str(minv))
      logger.debug("New RecrawlPeriod value for site %s is:%s", str(siteObj.id), str(recrawlPeriod))

    return recrawlPeriod



  # #Check the ClientResponse object with GeneralResponse objects in items list, log errors
  #
  # @param ClientResponse object
  def logGeneralResponseResults(self, clientResponse):
    if isinstance(clientResponse, EventObjects.ClientResponse):
      if clientResponse.errorCode > 0:
        logger.error("clientResponse.errorCode:" + str(clientResponse.errorCode) + ":" + clientResponse.errorMessage)
      for clientResponseItem in clientResponse.itemsList:
        if isinstance(clientResponseItem, EventObjects.ClientResponseItem):
          if clientResponseItem.errorCode != EventObjects.ClientResponseItem.STATUS_OK:
            logger.error("ClientResponseItem error: " + str(clientResponseItem.errorCode) + " : " + \
                         clientResponseItem.errorMessage + "\n" + Utils.varDump(clientResponseItem))
        else:
          logger.error("Wrong type: " + str(type(clientResponseItem)) + ", expected ClientResponseItem\n" + \
                       Utils.varDump(clientResponseItem))
    else:
      logger.error("Wrong type: " + str(type(clientResponse)) + ", expected ClientResponse\n" + \
                   Utils.varDump(clientResponse))



  # #Fix fields of the event object depends of operation type to reflect distributed structure if nodes>1
  #
  # @param event object
  # @param nodes number
  def fixFields(self, event, nodes):
    try:
      if (event.eventType == DC_CONSTS.EVENT_TYPES.SITE_NEW and isinstance(event.eventObj, EventObjects.Site)) or\
        (event.eventType == DC_CONSTS.EVENT_TYPES.SITE_UPDATE and isinstance(event.eventObj, EventObjects.SiteUpdate)):
        fieldsList = ["maxURLs", "maxResources", "maxErrors"]
        for fieldName in fieldsList:
          setattr(event.eventObj, fieldName, self.fixField(getattr(event.eventObj, fieldName), nodes, fieldName))
    except Exception, e:
      logger.error("Error %s", str(e))



  # #Fix field value with numeric divide with rounding to greater value
  #
  # @param value of the field
  # @param divider value
  # @param comment for log
  def fixField(self, value, divider, comment):
    if value is not None:
      d = int(divider)
      v = int(value)

      ret = int(int(v) / int(d))

      if ret < 1 and v > 0:
        ret = 1

      if ret * d < v:
        ret = ret + 1

      logger.debug("Initial value of field `%s` from %s was fixed to %s, divider %s", comment, str(value), str(ret),
                   str(divider))
    else:
      ret = value

    return ret

