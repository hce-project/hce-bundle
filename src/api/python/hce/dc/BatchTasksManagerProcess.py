'''
HCE project, Python bindings, Distributed Crawler application.
BatchTasksManagerProcess object and related classes definitions.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import time
try:
  import cPickle as pickle
except ImportError:
  import pickle

import dc.Constants as DC_CONSTS
from dc import EventObjects
from transport.ConnectionBuilderLight import ConnectionBuilderLight
import transport.Consts as TRANSPORT_CONSTS
import dtm.EventObjects
import dtm.Constants as DTM_CONSTS
from app.BaseServerManager import BaseServerManager
from app.Utils import SQLExpression, varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The BatchTasksManager class, is a main crawling logic of DC application.
#
# This object is a main crawling batches algorithms of DC application.
# It supports complete DTM protocol requests and process responses from DTM server, operates with tasks and monitors
# tasks state.
#
class BatchTasksManagerProcess(BaseServerManager):

  DTM_TASK_CHECK_STATE_METHOD_STATUS = 0
  DTM_TASK_CHECK_STATE_METHOD_STATE = 1

  # Configuration settings options names
  CONFIG_SERVER = "server"
  CONFIG_DTMD_HOST = "DTMDHost"
  CONFIG_DTMD_PORT = "DTMDPort"
  CONFIG_DTMD_TIMEOUT = "DTMDTimeout"
  CONFIG_POLLING_TIMEOUT = "PollingTimeout"
  CONFIG_SITES_MANAGER_CLIENT = "clientSitesManager"

  CONFIG_DRCE_PROCESSOR_APP_NAME = "DRCEProcessorAppName"
  CONFIG_DRCE_DB_APP_NAME = "DRCEDBAppName"
  CONFIG_PROCESS_PERIOD = "ProcessingPeriod"
  CONFIG_PROCESS_MODE = "ProcessingMode"

  CONFIG_BATCH_DEFAULT_MAX_TIME = "BatchDefaultMaxExecutionTime"
  CONFIG_BATCH_MAX_URLS = "BatchDefaultMaxURLs"
  CONFIG_BATCH_ORDER_BY_URLS = "BatchDefaultOrderByURLs"
  CONFIG_BATCH_MAX_TASKS = "BatchDefaultMaxTasks"
  CONFIG_BATCH_QUEUE_PERIOD = "BatchQueueProcessingPeriod"
  CONFIG_BATCH_QUEUE_TASK_TTL = "BatchQueueTaskTTL"
  CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD = "BatchQueueTaskCheckStateMethod"
  CONFIG_BATCH_DEFAULT_STARTER = "BatchTask_STARTER"
  CONFIG_BATCH_WHERE_URLS = "BatchDefaultWhereURLs"
  CONFIG_BATCH_WHERE_SITES = "BatchDefaultWhereSites"
  CONFIG_BATCH_MAX_TIME = "BatchMaxExecutionTime"
  CONFIG_BATCH_REMOVE_UNPROCESSED_ITEMS = "RemoveUnprocessedBatchItems"

  # The tasks's strategy configuration parameters for DTM service
  CONFIG_BATCH_DEFAULT_STRATEGY_IO_WAIT_MAX = "BatchTask_IO_WAIT_MAX"
  CONFIG_BATCH_DEFAULT_STRATEGY_CPU_LOAD_MAX = "BatchTask_CPU_LOAD_MAX"
  CONFIG_BATCH_DEFAULT_STRATEGY_RAM_FREE_MIN = "BatchTask_RAM_FREE_MIN"
  CONFIG_BATCH_DEFAULT_STRATEGY_STRATEGY_RDELAY = "BatchTask_RDELAY"
  CONFIG_BATCH_DEFAULT_STRATEGY_RETRY = "BatchTask_RETRY"
  CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL = "BatchTask_autocleanup_TTL"
  CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE = "BatchTask_autocleanup_DeleteType"
  CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES = "BatchTask_autocleanup_DeleteRetries"
  CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE = "BatchTask_autocleanup_State"

  # Processing task DTM name
  CONFIG_TASK_DTM_NAME_PROCESS = "BatchTaskDTMNameProcess"
  # Processing task DTM type
  CONFIG_TASK_DTM_TYPE_PROCESS = "BatchTaskDTMTypeProcess"


  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(BatchTasksManagerProcess, self).__init__()

    # Instantiate the connection builder light if not set
    if connectionBuilderLight is None:
      connectionBuilderLight = ConnectionBuilderLight()

    # Batches counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_TOTAL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches in queue counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_QUEUE_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Batches that fault processing counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches that not empty counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_FILLED_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches urls total counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_URLS_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Fault batches urls total counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_URLS_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Processing delete task requests fault counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_DELETE_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Processing check task requests fault counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_CHECK_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Processing batches fault TTL counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_FAULT_TTL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Processing batches cancelled counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_CANCELLED_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)

    # Get configuration settings
    className = self.__class__.__name__
    self.serverName = configParser.get(className, self.CONFIG_SERVER)
    self.clientSitesManagerName = configParser.get(className, self.CONFIG_SITES_MANAGER_CLIENT)
    # Configuration settings for DTMD server interaction
    self.configVars[self.CONFIG_DTMD_HOST] = configParser.get(className, self.CONFIG_DTMD_HOST)
    self.configVars[self.CONFIG_DTMD_PORT] = configParser.get(className, self.CONFIG_DTMD_PORT)
    self.configVars[self.CONFIG_DTMD_TIMEOUT] = configParser.getint(className, self.CONFIG_DTMD_TIMEOUT)

    # Max URLs per batch
    self.configVars[self.CONFIG_BATCH_MAX_URLS] = configParser.getint(className, self.CONFIG_BATCH_MAX_URLS)
    # Set connections poll timeout, defines period of HCE cluster monitoring cycle, msec
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_POLLING_TIMEOUT)
    # Set crawler task app name
    self.configVars[self.CONFIG_DRCE_PROCESSOR_APP_NAME] = \
      configParser.get(className, self.CONFIG_DRCE_PROCESSOR_APP_NAME)
    self.configVars[self.CONFIG_BATCH_DEFAULT_MAX_TIME] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_MAX_TIME)

    # #TODO experemental
    # Max execution time for batch
    self.configVars[self.CONFIG_BATCH_MAX_TIME] = configParser.getint(className, self.CONFIG_BATCH_MAX_TIME)
    # Remove unprocessed items for batch
    self.configVars[self.CONFIG_BATCH_REMOVE_UNPROCESSED_ITEMS] = \
      configParser.getint(className, self.CONFIG_BATCH_REMOVE_UNPROCESSED_ITEMS)

    # Create connections and raise bind or connect actions for correspondent connection type
    serverConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, self.serverName)
    sitesManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT, self.clientSitesManagerName)

    # Init the DTMD connection
    self.dtmdConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT,
                                                       self.configVars[self.CONFIG_DTMD_HOST] + ":" + \
                                                       self.configVars[self.CONFIG_DTMD_PORT],
                                                       TRANSPORT_CONSTS.TCP_TYPE)

    # Add connections to the polling set
    self.addConnection(self.serverName, serverConnection)
    self.addConnection(self.clientSitesManagerName, sitesManagerConnection)

    # Set event handler for URL_UPDATE_RESPONSE event
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.URL_UPDATE_RESPONSE, self.onURLUpdateResponse)
    # Set event handler for URL_DELETE_RESPONSE event
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.URL_DELETE_RESPONSE, self.onURLDeleteResponse)

    # Initialize the DTM tasks queue, the key is taskId, the value is the Batch object
    self.dtmTasksQueue = {}

    # Processing init
    self.configVars[self.CONFIG_DRCE_DB_APP_NAME] = configParser.get(className, self.CONFIG_DRCE_DB_APP_NAME)
    self.configVars[self.CONFIG_PROCESS_PERIOD] = configParser.getint(className, self.CONFIG_PROCESS_PERIOD)
    self.processProcessingLastTs = time.time()

    # The Batch default order by criterion to fetch URLs
    self.configVars[self.CONFIG_BATCH_ORDER_BY_URLS] = configParser.get(className, self.CONFIG_BATCH_ORDER_BY_URLS)
    # The Batch max tasks in batch queue, if limit reached new batch tasks will not be started; zero means unlimited
    self.configVars[self.CONFIG_BATCH_MAX_TASKS] = configParser.getint(className, self.CONFIG_BATCH_MAX_TASKS)
    # The Batch queue processing init
    self.configVars[self.CONFIG_BATCH_QUEUE_PERIOD] = configParser.getint(className, self.CONFIG_BATCH_QUEUE_PERIOD)
    self.processBatchQueuelLastTs = time.time()
    # The Batch queue task TTL, sec
    self.configVars[self.CONFIG_BATCH_QUEUE_TASK_TTL] = configParser.getint(className, self.CONFIG_BATCH_QUEUE_TASK_TTL)
    # The Batch queue tasks state check method, see ini file comments
    self.configVars[self.CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD] = \
      configParser.getint(className, self.CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD)
    # The Batch DRCE task starter name
    self.configVars[self.CONFIG_BATCH_DEFAULT_STARTER] = configParser.get(className, self.CONFIG_BATCH_DEFAULT_STARTER)
    # The Batch tasks's strategy configuration parameters for DTM service load
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_IO_WAIT_MAX] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_IO_WAIT_MAX)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_CPU_LOAD_MAX] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_CPU_LOAD_MAX)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_RAM_FREE_MIN] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_RAM_FREE_MIN)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_STRATEGY_RDELAY] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_STRATEGY_RDELAY)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_RETRY] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_RETRY)
    # The Batch DRCE tasks auto cleanup fields
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL] = \
                   configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE] = \
                   configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES] = \
                   configParser.get(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE] = \
                   configParser.get(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE)
    # The Batch default where criterion to fetch URLs
    self.configVars[self.CONFIG_BATCH_WHERE_URLS] = configParser.get(className, self.CONFIG_BATCH_WHERE_URLS)
    # The Batch default where criterion to fetch Sites
    self.configVars[self.CONFIG_BATCH_WHERE_SITES] = configParser.get(className, self.CONFIG_BATCH_WHERE_SITES)

    # Init the config processing mode and runtime values
    self.configVars[self.CONFIG_PROCESS_MODE] = configParser.getint(className, self.CONFIG_PROCESS_MODE)

    # Processing task DTM name
    self.configVars[self.CONFIG_TASK_DTM_NAME_PROCESS] = configParser.get(className, self.CONFIG_TASK_DTM_NAME_PROCESS)
    # Processing task DTM type
    self.configVars[self.CONFIG_TASK_DTM_TYPE_PROCESS] = configParser.getint(className,
                                                                             self.CONFIG_TASK_DTM_TYPE_PROCESS)



  # #Events wait timeout handler, for timeout state of the connections polling. Executes periodical check of DTM tasks
  # and initiate the main processing batching iteration cycle
  #
  def on_poll_timeout(self):
    logger.debug("Periodic iteration started.")
    try:
      # Process the Processing batch
      if self.configVars[self.CONFIG_PROCESS_PERIOD] > 0 and\
        time.time() - self.processProcessingLastTs > self.configVars[self.CONFIG_PROCESS_PERIOD]:
        self.processProcessingLastTs = time.time()
        if self.configVars[self.CONFIG_PROCESS_MODE] == 1:
          logger.debug("Processing batch cycle iteration started")
          if self.configVars[self.CONFIG_BATCH_MAX_TASKS] > len(self.dtmTasksQueue):
            if self.setProcessBatch():
              self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_TOTAL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
          else:
            self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_CANCELLED_NAME, 1,
                                 self.STAT_FIELDS_OPERATION_ADD)
            logger.debug("Max processing batch tasks %s in queue reached, new batch is not created!",
                         str(len(self.dtmTasksQueue)))
        else:
          logger.debug("Processing batch disabled!")

      # Process the DRCE Batch tasks queue
      if self.configVars[self.CONFIG_BATCH_QUEUE_PERIOD] > 0 and\
        time.time() - self.processBatchQueuelLastTs > self.configVars[self.CONFIG_BATCH_QUEUE_PERIOD]:
        self.processBatchQueuelLastTs = time.time()
        logger.debug("Process DTM tasks queue!")
        # Process the DTM tasks queue
        self.processDTMTasksQueue()

    except IOError as e:
      del e
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")

    logger.debug("Periodic iteration finished.")



  # #Create new process batch, send it to execute as asynchronous DRCE task and insert in to the batches queue
  #
  #
  def setProcessBatch(self):
    ret = False

    try:
      # Create the URLUpdate object to set in progress of processing state for selected URLs
      urlUpdate = EventObjects.URLUpdate(0, "", EventObjects.URLStatus.URL_TYPE_MD5, None,
                                         EventObjects.URL.STATUS_SELECTED_PROCESSING)
      urlUpdate.tcDate = SQLExpression("NOW()")
      # Create URLFetch object with URLUpdate to update selected URLs state
      sCrit = "IFNULL((SELECT `Value` FROM `sites_properties` WHERE `Name`='PROCESS_WHERE_SITES'), " + \
              self.configVars[self.CONFIG_BATCH_WHERE_SITES] + ")"
      sitesCriterions = {EventObjects.URLFetch.CRITERION_WHERE: sCrit,
                         EventObjects.URLFetch.CRITERION_ORDER:"Priority DESC, TcDateProcess ASC"}
      uCrit = "IFNULL(%PROCESS_WHERE_URLS%, " + self.configVars[self.CONFIG_BATCH_WHERE_URLS] + ")"
      urlCriterions = {EventObjects.URLFetch.CRITERION_WHERE: uCrit,
                       EventObjects.URLFetch.CRITERION_ORDER: self.configVars[self.CONFIG_BATCH_ORDER_BY_URLS],
                       EventObjects.URLFetch.CRITERION_LIMIT: str(self.configVars[self.CONFIG_BATCH_MAX_URLS]),
                       EventObjects.URLFetch.CRITERION_SQL: {
                           "PROCESS_WHERE_URLS": "SELECT `Value` FROM `dc_sites`.`sites_properties` WHERE " + \
                         "`Name`='PROCESS_WHERE_URLS' AND `Site_Id`=\"%SITE_ID%\" LIMIT 1"  # pylint: disable=C0301
                       }
                      }
      siteUpdate = EventObjects.SiteUpdate(0)
      siteUpdate.tcDateProcess = EventObjects.SQLExpression("Now()")
      urlFetch = EventObjects.URLFetch(None, urlCriterions, sitesCriterions, urlUpdate, siteUpdate)
      urlFetch.algorithm = EventObjects.URLFetch.PROPORTIONAL_ALGORITHM
      urlFetch.maxURLs = self.configVars[self.CONFIG_BATCH_MAX_URLS]
      taskId = self.sendBatchTaskToDTM(urlFetch)
      if taskId > 0:
        logger.debug("DTM process batch was set, taskId=%s", str(taskId))
        # Insert the Batch object in to the queue
        urlFetch.QueuedTs = time.time()
        urlFetch.crawlerType = EventObjects.Batch.TYPE_PROCESS
        self.dtmTasksQueue[taskId] = urlFetch
        self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_QUEUE_NAME, len(self.dtmTasksQueue),
                             self.STAT_FIELDS_OPERATION_SET)
        ret = True
      else:
        logger.error("Error send process batch task to DTM!")

    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")

    return ret



  # #make the Batch object from the ClientResponse object items
  # @param clientResponseItems The list of ClientResponseItem objects
  #
  def sendBatchTaskToDTM(self, batch):
    taskId = 0
    # Prepare NewTask object
    appName = self.configVars[self.CONFIG_DRCE_DB_APP_NAME]
    newTaskObj = dtm.EventObjects.NewTask(appName)
    newTaskObj.name = self.configVars[self.CONFIG_TASK_DTM_NAME_PROCESS]
    newTaskObj.type = self.configVars[self.CONFIG_TASK_DTM_TYPE_PROCESS]
    newTaskObj.setSessionVar("tmode", dtm.EventObjects.Task.TASK_MODE_ASYNCH)
    newTaskObj.setSessionVar("shell", self.configVars[self.CONFIG_BATCH_DEFAULT_STARTER])
    newTaskObj.setSessionVar("time_max", int(self.configVars[self.CONFIG_BATCH_DEFAULT_MAX_TIME]) * 1000)
    newTaskObj.setSessionVar("task_type", int(newTaskObj.type))
    # Configure task's strategy
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_IO_WAIT_MAX] > 0:
      newTaskObj.setStrategyVar(dtm.EventObjects.Task.STRATEGY_IO_WAIT_MAX,
                                self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_IO_WAIT_MAX])
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_CPU_LOAD_MAX] > 0:
      newTaskObj.setStrategyVar(dtm.EventObjects.Task.STRATEGY_CPU_LOAD_MAX,
                                self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_CPU_LOAD_MAX])
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_RAM_FREE_MIN] > 0:
      newTaskObj.setStrategyVar(dtm.EventObjects.Task.STRATEGY_RAM_FREE,
                                self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_RAM_FREE_MIN])
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_STRATEGY_RDELAY] > 0:
      newTaskObj.setStrategyVar(dtm.EventObjects.Task.STRATEGY_RDELAY,
                                self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_STRATEGY_RDELAY])
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_RETRY] > 0:
      newTaskObj.setStrategyVar(dtm.EventObjects.Task.STRATEGY_RETRY,
                                self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_RETRY])
    # Set auto cleanup fields
    autoCleanupFields = {}
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL] > -1:
      autoCleanupFields[dtm.EventObjects.Task.STRATEGY_AUTOCLEANUP_TTL] = \
                       int(self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL]) * 1000
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE] > -1:
      autoCleanupFields[dtm.EventObjects.Task.STRATEGY_AUTOCLEANUP_DELETE_TYPE] = \
                       self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE]
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES] > -1:
      autoCleanupFields[dtm.EventObjects.Task.STRATEGY_AUTOCLEANUP_DELETE_RETRIES] = \
                       self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES]
    if self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE] > -1:
      autoCleanupFields[dtm.EventObjects.Task.STRATEGY_AUTOCLEANUP_SSTATE] = \
                       self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE]
    if len(autoCleanupFields) > 0:
      newTaskObj.setStrategyVar(dtm.EventObjects.Task.STRATEGY_autoCleanupFields, autoCleanupFields)
    batch.id = newTaskObj.id
    drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_FETCH, [batch])
    newTaskObj.input = pickle.dumps(drceSyncTasksCoverObj)
    newTaskEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.NEW_TASK, newTaskObj)
    generalResponse = self.dtmdRequestExecute(newTaskEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
    if generalResponse is not None:
      if generalResponse.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK:
        # New crawling Batch task set successfully
        taskId = newTaskObj.id
      else:
        # Some error of task operation
        logger.error("DTM set batch task error: " + str(generalResponse.errorCode) + " : " + \
                     generalResponse.errorMessage + ", statuses:" + varDump(generalResponse))
    else:
      logger.error("DTM set batch task response error, possible timeout!")

    # TODO: return the Task Id any case error or not to check it state later
    taskId = newTaskObj.id

    return taskId



  # #Get the DTM task state by involving one of two methods on DTM service
  #
  # @param taskId Id of DTM task
  def getDTMTaskState(self, taskId):
    taskState = None

    if self.configVars[self.CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD] == self.DTM_TASK_CHECK_STATE_METHOD_STATUS:
      # Check the task status on DRCE EE hce-node
      logger.debug("Check state of taskId=" + str(taskId))
      checkTaskStateObj = dtm.EventObjects.CheckTaskState(taskId)
      checkStateEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.CHECK_TASK_STATE, checkTaskStateObj)
      eeResponseData = self.dtmdRequestExecute(checkStateEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
      logger.debug("DTM CheckTaskState request finished, taskId=" + str(taskId))
      if eeResponseData is not None and type(eeResponseData) == type(dtm.EventObjects.EEResponseData(0)):
        taskState = eeResponseData.state
    else:
      # Get task status on DTM service
      logger.debug("Get status of taskId=" + str(taskId))
      getTasksStatusObj = dtm.EventObjects.GetTasksStatus([taskId])
      getTasksStatusEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.GET_TASK_STATUS, getTasksStatusObj)
      listTaskManagerFields = self.dtmdRequestExecute(getTasksStatusEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
      logger.debug("DTM getTasksStatus request finished, taskId=" + str(taskId))
      if listTaskManagerFields is not None and isinstance(listTaskManagerFields, list):
        if len(listTaskManagerFields) > 0:
          taskState = listTaskManagerFields[0].fields["state"]
        else:
          # Set TASK_STATE_FINISHED state to push task to delete from queue
          taskState = dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED
      else:
        logger.error("DTM getTasksStatus taskId=" + str(taskId) + " returned wrong data:\n" + \
                     Utils.varDump(listTaskManagerFields))

    return taskState



  # #Process the DTM tasks queue
  #
  #
  def processDTMTasksQueue(self):
    tmpQueue = {}

    logger.debug("Process batch tasks in queue:" + str(len(self.dtmTasksQueue)))
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_QUEUE_NAME, len(self.dtmTasksQueue),
                         self.STAT_FIELDS_OPERATION_SET)

    # Process the DTM tasks queue
    for taskId, taskBatch in self.dtmTasksQueue.items():
      ttl = self.configVars[self.CONFIG_BATCH_QUEUE_TASK_TTL]
      batchState = self.getDTMTaskState(taskId)
      if batchState != None:
        logger.debug("Process batch state " + str(batchState) + ", Id=" + str(taskId))
        if batchState == dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED or\
           batchState == dtm.EventObjects.EEResponseData.TASK_STATE_CRASHED or\
           batchState == dtm.EventObjects.EEResponseData.TASK_STATE_TERMINATED or\
           batchState == dtm.EventObjects.EEResponseData.TASK_STATE_UNDEFINED or\
           batchState == dtm.EventObjects.EEResponseData.TASK_STATE_SET_ERROR or\
           batchState == dtm.EventObjects.EEResponseData.TASK_STATE_SCHEDULE_TRIES_EXCEEDED:
          # Delete task in DTM and task's data in EE (DRCE)
          deleteTaskObj = dtm.EventObjects.DeleteTask(taskId)
          deleteTaskEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_TASK, deleteTaskObj)
          generalResponse = self.dtmdRequestExecute(deleteTaskEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
          logger.debug("DTM DeleteTask request finished, taskId=" + str(taskId))
          if generalResponse is not None:
            if generalResponse.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK:
              logger.debug("DTM task deleted, taskId=" + str(taskId))
              # if batchState == dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED:
              if self.isDTMTaskDead(batchState):
                logger.debug("batch:\n" + varDump(taskBatch) + "\n finished, taskId=" + str(taskId))
                self.processFinishedBatch(taskBatch)
              else:
                self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
                logger.debug("batch:" + varDump(taskBatch) + " not finished, state= " + str(batchState))
                # TODO: Send update URLs of not finished batch on all nodes to get possibility to process them next time
                # self.sendURLUpdate(taskBatch.items, taskBatch.id, False)
            else:
              # Save this batch to check it later
              tmpQueue[taskId] = taskBatch
              self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_DELETE_FAULT_NAME, 1,
                                   self.STAT_FIELDS_OPERATION_ADD)
              logger.error("DTM delete task taskId=" + str(taskId) + " error: " + str(generalResponse.errorCode) + \
                           " : " + generalResponse.errorMessage + ", statuses:" + varDump(generalResponse))
          else:
            # Save this batch to check it later
            tmpQueue[taskId] = taskBatch
            self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_DELETE_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            logger.error("DTM delete task error: wrong response or timeout, taskId=" + str(taskId) + "!")
        else:
          logger.debug("DTM task Id=" + str(taskId) + " state=" + str(batchState))
          if time.time() - taskBatch.QueuedTs > ttl:
            # Terminate task and delete it's data request
            deleteTaskObj = dtm.EventObjects.DeleteTask(taskId)
            deleteTaskObj.action = dtm.EventObjects.DeleteTask.ACTION_TERMINATE_TASK_AND_DELETE_DATA
            deleteTaskEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_TASK, deleteTaskObj)
            generalResponse = self.dtmdRequestExecute(deleteTaskEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
            logger.error("DTM task Id=" + str(taskId) + " terminated and removed from queue by TTL:" + str(ttl))
            # TODO: Send update URLs of not finished batch on all nodes to get possibility to crawl them next time
            # self.sendURLUpdate(taskBatch.items, taskBatch.id, False)
            self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_FAULT_TTL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
          else:
            # Save this batch to check it later
            tmpQueue[taskId] = taskBatch
            logger.debug("DTM task Id=" + str(taskId) + " still in queue")
      else:
        logger.error("DTM check task state error: wrong response or timeout, taskId=" + str(taskId) + "!")
        if time.time() - taskBatch.QueuedTs > ttl:
          logger.error("DTM task Id=" + str(taskId) + " removed from queue by TTL:" + str(ttl))
        else:
          # Save this batch to check it later
          tmpQueue[taskId] = taskBatch
          self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_CHECK_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
          logger.error("DTM task Id=" + str(taskId) + " saved in queue.")

    self.dtmTasksQueue = tmpQueue
    self.updateStatField(DC_CONSTS.BATCHES_PROCESS_COUNTER_QUEUE_NAME, len(self.dtmTasksQueue),
                         self.STAT_FIELDS_OPERATION_SET)
    logger.debug("The DTM tasks queue processing finished, batch tasks in queue " + str(len(self.dtmTasksQueue)))



  # #Check is DTM task alive by status code verification, returns True if yes or False if not
  #
  #
  def isDTMTaskDead(self, state):
    ret = False
    if state == dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED or\
       state == dtm.EventObjects.EEResponseData.TASK_STATE_CRASHED or\
       state == dtm.EventObjects.EEResponseData.TASK_STATE_TERMINATED or\
       state == dtm.EventObjects.EEResponseData.TASK_STATE_UNDEFINED or\
       state == dtm.EventObjects.EEResponseData.TASK_STATE_SET_ERROR or\
       state == dtm.EventObjects.EEResponseData.TASK_STATE_TERMINATED_BY_DRCE_TTL or\
       state == dtm.EventObjects.EEResponseData.TASK_STATE_SCHEDULE_TRIES_EXCEEDED:
      ret = True

    return ret



  # #Do some post batch processing after batch was successfully finished
  #
  # @param taskBatch the Batch object
  #
  def processFinishedBatch(self, taskBatch):
    # if self.configVars[self.CONFIG_CRAWLED_URLS_STRATEGY] == 0:
    #  self.sendURLUpdate(taskBatch.items, taskBatch.id, True)
    #  logger.debug("Send update URLs from batch for all foreign hosts by the Batch_Id")
    # else:
    #  self.sendURLDelete(taskBatch.items, taskBatch.id)
    #  logger.debug("Send delete URLs from batch for all foreign hosts by the Batch_Id")
    pass
    # TODO: update or delete URLs from returned batch



  # #Execute DTMD task request
  #
  # @param requestEvent The request event to send to DTMD
  # @param timeout The DTMD request timeout
  #
  def dtmdRequestExecute(self, requestEvent, timeout, maxTries=100):
    ret = None
    if maxTries < 0:
      maxTries = 0

    try:
      # Send DTMD request
      self.dtmdConnection.send(requestEvent)

      for i in range(maxTries + 1):
        # Poll DTMD connection
        if self.dtmdConnection.poll(int(timeout)) == 0:
          logger.error("DTMD request timeout reached " + str(timeout) + "!")
          break
        else:
          # Recv DTMD response
          retEvent = self.dtmdConnection.recv()
          if retEvent != None:
            # Get response object
            if type(retEvent.eventObj) == type(dtm.EventObjects.EEResponseData(0)) or\
              type(retEvent.eventObj) == type(dtm.EventObjects.GeneralResponse()) or\
              isinstance(retEvent.eventObj, list):
              if retEvent.uid == requestEvent.uid:
                ret = retEvent.eventObj
                break
              else:
                logger.error("DTMD returned wrong object uid: " + str(retEvent.uid) + " but " + \
                             str(requestEvent.uid) + " expected, iteration " + str(i) + "!")
            else:
              logger.error("DTMD returned wrong object type: " + str(type(retEvent.eventObj)) + "!")
          else:
            logger.error("DTMD returned None event!")
    except Exception, e:
      logger.error("DTMD request execution exception: " + e.message + "!")

    logger.debug("The DTMD request finished!")

    return ret



  # #Send URL update for batch URLs
  #
  # @param batchItemsList List of BatchItem objects
  # @param batchId the Batch Id
  # @param batchState state of batch operation False - means return URLs to New state, True - means set crawled state
  def sendURLUpdate(self, batchItemsList, batchId, batchState):
    urlsList = []

    # Prepare URLs list to update
    for batchItem in batchItemsList:
      # Set state value depends on update reason - crawled successfully or not
      if batchState is True:
        status = EventObjects.URL.STATUS_CRAWLED
        sqlExpression = SQLExpression("`URLMd5`='" + str(batchItem.urlId) + "' AND `Batch_Id` <>" + str(batchId) + \
                                      " AND `Status` NOT IN (" + str(EventObjects.URL.STATUS_CRAWLED) + \
                                      "," + str(EventObjects.URL.STATUS_SELECTED_PROCESSING) + ")")
      else:
        status = EventObjects.URL.STATUS_NEW
        sqlExpression = SQLExpression("`URLMd5`='" + str(batchItem.urlId) + "' AND `Status` IN (" +
                                      str(EventObjects.URL.STATUS_SELECTED_CRAWLING) + "," + \
                                      str(EventObjects.URL.STATUS_SELECTED_CRAWLING_INCREMENTAL) + ")")

      urlUpdate = EventObjects.URLUpdate(batchItem.siteId, batchItem.urlId, EventObjects.URLStatus.URL_TYPE_MD5,
                                         None, status)
      urlUpdate.criterions[EventObjects.URLFetch.CRITERION_WHERE] = sqlExpression
      logger.debug("URLUpdate: " + varDump(urlUpdate))
      urlsList.append(urlUpdate)

    # Make URLUpdate event
    urlUpdateEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_UPDATE, urlsList)
    # Send request URLUpdate to SitesManager
    self.send(self.clientSitesManagerName, urlUpdateEvent)
    logger.debug("The URLUpdate request to SitesManager sent!")



  # #Send URL delete for batch URLs that is not processed and stays in SELECTED_FOR_PROCESS state (5)
  #
  # @param batchItemsList List of BatchItem objects
  # @param batchId Id of the batch
  def sendURLDelete(self, batchItemsList, batchId):
    urlsList = []

    # Prepare URLs list to delete
    for batchItem in batchItemsList:
      sqlExpression = SQLExpression("`ParentMd5`<>'' AND `URLMd5`='" + str(batchItem.urlId) + "' AND `Batch_Id`<>" + \
                                     str(batchId))
      urlDelete = EventObjects.URLDelete(batchItem.siteId, None, EventObjects.URLStatus.URL_TYPE_URL,
                                         {EventObjects.URLFetch.CRITERION_WHERE:sqlExpression,
                                          EventObjects.URLFetch.CRITERION_LIMIT:1},
                                         reason=EventObjects.URLDelete.REASON_SELECT_TO_PROCESS_TTL)
      logger.debug("URLDelete: " + varDump(urlDelete))
      urlsList.append(urlDelete)

    # Make URLDelete event
    urlDeleteEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_DELETE, urlsList)
    # Send request URLDelete to SitesManager
    self.send(self.clientSitesManagerName, urlDeleteEvent)
    logger.debug("The URLDelete request to SitesManager sent!")



  # #onURLUpdateResponse event handler
  #
  # @param event instance of Event object
  def onURLUpdateResponse(self, event):
    try:
      logger.debug("Reply received on URL update.")
      clientResponse = event.eventObj
      if clientResponse.errorCode == EventObjects.ClientResponse.STATUS_OK:
        if len(clientResponse.itemsList) > 0:
          for clientResponseItem in clientResponse.itemsList:
            if clientResponseItem.errorCode != EventObjects.ClientResponseItem.STATUS_OK:
              logger.error("URLUpdate response error: " + str(clientResponseItem.errorCode) + " : " + \
                           clientResponseItem.errorMessage + ", host:" + clientResponseItem.host + ", port:" + \
                           clientResponseItem.port + ", node:" + clientResponseItem.node + "!")
        else:
          logger.error("URLUpdate response empty list!")
      else:
        logger.error("URLUpdate response error:" + str(clientResponse.errorCode) + " : " + clientResponse.errorMessage)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


  # #onURLDeleteResponse event handler
  #
  # @param event instance of Event object
  def onURLDeleteResponse(self, event):
    try:
      logger.debug("Reply received on URL delete.")
      clientResponse = event.eventObj
      if clientResponse.errorCode == EventObjects.ClientResponse.STATUS_OK:
        if len(clientResponse.itemsList) > 0:
          for clientResponseItem in clientResponse.itemsList:
            if clientResponseItem.errorCode != EventObjects.ClientResponseItem.STATUS_OK:
              logger.error("URLDelete response error: " + str(clientResponseItem.errorCode) + " : " + \
                           clientResponseItem.errorMessage + ", host:" + clientResponseItem.host + ", port:" + \
                           clientResponseItem.port + ", node:" + clientResponseItem.node + "!")
        else:
          logger.error("URLDelete response empty list!")
      else:
        logger.error("URLDelete response error:" + str(clientResponse.errorCode) + " : " + clientResponse.errorMessage)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")

