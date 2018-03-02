'''
HCE project, Python bindings, Distributed Crawler application.
BatchTasksManager object and related classes definitions.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import time
import ConfigParser
import json
import random

# import pickle
try:
  import cPickle as pickle
except ImportError:
  import pickle

import copy
from app.BaseServerManager import BaseServerManager
from app.Utils import SQLExpression, varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401
import dc.Constants as DC_CONSTS
from dc import EventObjects
from transport.ConnectionBuilderLight import ConnectionBuilderLight
import transport.Consts as TRANSPORT_CONSTS
import dtm.EventObjects
import dtm.Constants as DTM_CONSTS

# Logger initialization
logger = Utils.MPLogger().getLogger()


# #The BatchTasksManager class, is a main crawling logic of DC application.
#
# This object is a main crawling batches algorithms of DC application.
# It supports complete DTM protocol requests and process responses from DTM server, operates with tasks and monitors
# tasks state.
#
class BatchTasksManager(BaseServerManager):

  DTM_TASK_CHECK_STATE_METHOD_STATUS = 0
  DTM_TASK_CHECK_STATE_METHOD_STATE = 1
  CONFIG_BATCH_MAX_ITERATIONS_DEFAULT = 2

  BATCH_TASK_TYPE_ALL = 0
  BATCH_TASK_TYPE_CRAWL = 1
  BATCH_TASK_TYPE_PURGE = 2
  BATCH_TASK_TYPE_AGE = 3

  # Common configuration settings options names
  CONFIG_SERVER = "server"
  CONFIG_DTMD_HOST = "DTMDHost"
  CONFIG_DTMD_PORT = "DTMDPort"
  CONFIG_DTMD_TIMEOUT = "DTMDTimeout"
  CONFIG_SITES_MANAGER_CLIENT = "clientSitesManager"
  CONFIG_POLLING_TIMEOUT = "PollingTimeout"
  CONFIG_DRCE_CRAWLER_APP_NAME = "DRCECrawlerAppName"
  CONFIG_CRAWLED_URLS_STRATEGY = "CrawledURLStrategy"
  CONFIG_REGULAR_CRAWL_PERIOD = "RegularCrawlingPeriod"
  CONFIG_REGULAR_CRAWL_MODE = "RegularCrawlingMode"
  CONFIG_REGULAR_CRAWL_PROPAGATE_URLS = "RegularCrawlingPropagateURLs"
  # Crawling task DTM name
  CONFIG_TASK_DTM_NAME_CRAWLING = "BatchTaskDTMNameCrawl"
  # Purging task DTM name
  CONFIG_TASK_DTM_NAME_PURGING = "BatchTaskDTMNamePurge"
  # Aging task DTM name
  CONFIG_TASK_DTM_NAME_AGING = "BatchTaskDTMNameAging"
  # Crawling task DTM type
  CONFIG_TASK_DTM_TYPE_CRAWLING = "BatchTaskDTMTypeCrawl"
  # Purging task DTM type
  CONFIG_TASK_DTM_TYPE_PURGING = "BatchTaskDTMTypePurge"
  # Aging task DTM type
  CONFIG_TASK_DTM_TYPE_AGING = "BatchTaskDTMTypeAging"

  # Return URLs back state NEW configuration
  CONFIG_RET_URLS_MAX_NUMBER = "ReturnURLsMaxNumber"
  CONFIG_RET_URLS_PERIOD = "ReturnURLsPeriod"
  CONFIG_RET_URLS_TTL = "ReturnURLsTTL"
  CONFIG_RET_URLS_MODE = "ReturnURLsMode"

  # The incremental crawling configuration
  CONFIG_INCR_MIN_FREQ = "IncrMinFreq"
  CONFIG_INCR_MAX_DEPTH = "IncrMaxDepth"
  CONFIG_INCR_MAX_URL = "IncrMaxURLs"
  CONFIG_INCR_CRAWL_PERIOD = "IncrPeriod"
  CONFIG_INCR_CRAWL_MODE = "IncrMode"

  # The batch configuration
  CONFIG_BATCH_DEFAULT_MAX_TIME = "BatchDefaultMaxExecutionTime"
  CONFIG_BATCH_MAX_URLS = "BatchDefaultMaxURLs"
  CONFIG_BATCH_ORDER_BY_URLS = "BatchDefaultOrderByURLs"
  CONFIG_BATCH_MAX_TASKS = "BatchDefaultMaxTasks"
  CONFIG_BATCH_QUEUE_PERIOD = "BatchQueueProcessingPeriod"
  CONFIG_BATCH_QUEUE_TASK_TTL = "BatchQueueTaskTTL"
  CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD = "BatchQueueTaskCheckStateMethod"
  CONFIG_BATCH_DEFAULT_STARTER = "BatchTask_STARTER"
  CONFIG_BATCH_DEFAULT_CHECK_URLS_IN_ACTIVE_BATCHES = "BatchDefaultCheckURLsInActiveBatches"
  CONFIG_BATCH_MAX_ITERATIONS = "BatchMaxIterations"
  CONFIG_BATCH_FETCH_TYPE = "BatchDefaultFetchTypeOptions"
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

  # The purge algorithm configuration
  CONFIG_PURGE_PERIOD = "PurgePeriod"
  CONFIG_PURGE_MODE = "PurgeMode"
  CONFIG_PURGE_BATCH_DEFAULT_MAX_TIME = "PurgeBatchDefaultMaxExecutionTime"
  CONFIG_PURGE_BATCH_MAX_URLS = "PurgeBatchDefaultMaxURLs"
  CONFIG_PURGE_BATCH_QUEUE_TASK_TTL = "PurgeBatchQueueTaskTTL"
  CONFIG_PURGE_BATCH_DEFAULT_STARTER = "PurgeBatchTask_STARTER"
  CONFIG_DRCE_DB_APP_NAME = "DRCEDBAppName"
  CONFIG_PURGE_BATCH_MAX_TASKS = "PurgeBatchDefaultMaxTasks"

  # Aging config names
  CONFIG_AGING_PERIOD = "AgingPeriod"
  CONFIG_RESOURCE_AGING_MODE = "AgingMode"
  CONFIG_AGE_BATCH_DEFAULT_MAX_TIME = "AgingBatchDefaultMaxExecutionTime"
  CONFIG_AGE_BATCH_MAX_URLS_SITE = "AgingBatchDefaultMaxURLsSite"
  CONFIG_AGE_BATCH_MAX_URLS_TOTAL = "AgingBatchDefaultMaxURLsTotal"
  CONFIG_AGE_BATCH_MAX_SITES = "AgingBatchDefaultMaxSites"
  CONFIG_AGE_BATCH_QUEUE_TASK_TTL = "AgingBatchQueueTaskTTL"
  CONFIG_AGE_BATCH_DEFAULT_STARTER = "AgingBatchTask_STARTER"
  CONFIG_AGE_BATCH_MAX_TASKS = "AgingBatchDefaultMaxTasks"
  CONFIG_AGE_BATCH_URL_CRITERION = "AgingBatchURLsCriterion"
  CONFIG_AGE_BATCH_SITE_CRITERION = "AgingBatchSitesCriterion"

  BATCH_FETCH_TYPE_COOKIE_NAME = "FetchType"
  BATCH_ID_COOKIE_NAME = "batchId"


  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(BatchTasksManager, self).__init__()

    # Instantiate the connection builder light if not set
    if connectionBuilderLight is None:
      connectionBuilderLight = ConnectionBuilderLight()

    # Batches counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TOTAL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches in queue counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_QUEUE_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Batches that fault processing counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches that not empty counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FILLED_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches urls total counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Fault batches urls total counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling URL_FETCH requests counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling cancelled URL_FETCH requests counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_CANCELLED_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling delete task requests fault counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_DELETE_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling check task requests fault counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_CHECK_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling batches urls returned counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_RET_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling incremental URL_FETCH requests counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_INCR_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling batches fault TTL counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_TTL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches items/urls average counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_ITEMS_AVG_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches dynamic fetcher's batches counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FETCHER_DYNAMIC, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches static fetcher's batches counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FETCHER_STATIC, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches mixed static and dynamic fetcher's batches counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FETCHER_MIXED, 0, self.STAT_FIELDS_OPERATION_INIT)

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

    # Max execution time for batch
    self.configVars[self.CONFIG_BATCH_MAX_TIME] = configParser.getint(className, self.CONFIG_BATCH_MAX_TIME)
    # Remove unprocessed items for batch
    self.configVars[self.CONFIG_BATCH_REMOVE_UNPROCESSED_ITEMS] = \
      bool(configParser.getint(className, self.CONFIG_BATCH_REMOVE_UNPROCESSED_ITEMS))


    # Set connections poll timeout, defines period of HCE cluster monitoring cycle, msec
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_POLLING_TIMEOUT)
    # Configuration settings for incremental crawling
    self.configVars[DC_CONSTS.INCR_MIN_FREQ_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_INCR_MIN_FREQ)
    self.configVars[DC_CONSTS.INCR_MAX_DEPTH_CONFIG_VAR_NAME] = configParser.getint(className,
                                                                                    self.CONFIG_INCR_MAX_DEPTH)
    self.configVars[DC_CONSTS.INCR_MAX_URLS_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_INCR_MAX_URL)
    self.configVars[self.CONFIG_INCR_CRAWL_MODE] = configParser.getint(className, self.CONFIG_INCR_CRAWL_MODE)

    # Set crawler task app name
    self.configVars[self.CONFIG_DRCE_CRAWLER_APP_NAME] = configParser.get(className, self.CONFIG_DRCE_CRAWLER_APP_NAME)
    self.configVars[self.CONFIG_BATCH_DEFAULT_MAX_TIME] = \
      configParser.getint(className, self.CONFIG_BATCH_DEFAULT_MAX_TIME)

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

    # Set event handler for URL_FETCH_RESPONSE event
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.URL_FETCH_RESPONSE, self.onURLFetchResponse)
    # Set event handler for URL_UPDATE_RESPONSE event
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.URL_UPDATE_RESPONSE, self.onURLUpdateResponse)
    # Set event handler for URL_DELETE_RESPONSE event
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.URL_DELETE_RESPONSE, self.onURLDeleteResponse)
    # Set event handler for URL_NEW_RESPONSE event
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.URL_NEW_RESPONSE, self.onURLNewResponse)

    # Initialize the DTM tasks queue, the key is taskId, the value is the Batch object
    self.dtmTasksQueue = {}

    # Init config vars storage for return URLs selected for processing
    self.configVars[self.CONFIG_RET_URLS_MAX_NUMBER] = configParser.getint(className, self.CONFIG_RET_URLS_MAX_NUMBER)
    self.configVars[self.CONFIG_RET_URLS_PERIOD] = configParser.getint(className, self.CONFIG_RET_URLS_PERIOD)
    self.configVars[self.CONFIG_RET_URLS_TTL] = configParser.getint(className, self.CONFIG_RET_URLS_TTL)
    self.configVars[self.CONFIG_RET_URLS_MODE] = configParser.getint(className, self.CONFIG_RET_URLS_MODE)
    self.processSelectedURLsRetLastTs = time.time()

    # Incremental crawling init
    self.configVars[self.CONFIG_INCR_CRAWL_PERIOD] = configParser.getint(className, self.CONFIG_INCR_CRAWL_PERIOD)
    self.processIncrCrawlLastTs = time.time()

    # Crawled URLs strategy for batch
    self.configVars[self.CONFIG_CRAWLED_URLS_STRATEGY] = configParser.getint(className,
                                                                             self.CONFIG_CRAWLED_URLS_STRATEGY)
    # Batch default order by criterion to fetch URLs
    self.configVars[self.CONFIG_BATCH_ORDER_BY_URLS] = configParser.get(className, self.CONFIG_BATCH_ORDER_BY_URLS)

    # Batch default fetch type options
    try:
      self.configVars[self.CONFIG_BATCH_FETCH_TYPE] = configParser.get(className, self.CONFIG_BATCH_FETCH_TYPE)
      self.configVars[self.CONFIG_BATCH_FETCH_TYPE] = json.loads(self.configVars[self.CONFIG_BATCH_FETCH_TYPE])
    except ConfigParser.NoOptionError:
      self.configVars[self.CONFIG_BATCH_FETCH_TYPE] = {}

    # Max tasks in batch queue, if limit reached new batch tasks will not be started; zero means unlimited
    self.configVars[self.CONFIG_BATCH_MAX_TASKS] = configParser.getint(className, self.CONFIG_BATCH_MAX_TASKS)
    # Regular crawling init
    self.configVars[self.CONFIG_REGULAR_CRAWL_PERIOD] = configParser.getint(className, self.CONFIG_REGULAR_CRAWL_PERIOD)
    self.configVars[self.CONFIG_REGULAR_CRAWL_MODE] = configParser.getint(className, self.CONFIG_REGULAR_CRAWL_MODE)
    self.configVars[self.CONFIG_REGULAR_CRAWL_PROPAGATE_URLS] = \
                   configParser.getint(className, self.CONFIG_REGULAR_CRAWL_PROPAGATE_URLS)

    self.processRegularCrawlLastTs = time.time()
    # The batch queue processing init
    self.configVars[self.CONFIG_BATCH_QUEUE_PERIOD] = configParser.getint(className, self.CONFIG_BATCH_QUEUE_PERIOD)
    self.processBatchQueuelLastTs = time.time()
    # The batch queue task TTL, sec
    self.configVars[self.CONFIG_BATCH_QUEUE_TASK_TTL] = configParser.getint(className, self.CONFIG_BATCH_QUEUE_TASK_TTL)
    # The batch queue tasks state check method, see ini file comments
    self.configVars[self.CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD] = \
      configParser.getint(className, self.CONFIG_BATCH_QUEUE_TASK_CHECK_METHOD)

    # The tasks's strategy configuration parameters for DTM service load
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

    # The DRCE task starter name
    self.configVars[self.CONFIG_BATCH_DEFAULT_STARTER] = configParser.get(className, self.CONFIG_BATCH_DEFAULT_STARTER)

    # The auto cleanup fields
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL] = \
                   configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_TTL)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE] = \
                   configParser.getint(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_TYPE)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES] = \
                   configParser.get(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_DELETE_RETRIES)
    self.configVars[self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE] = \
                   configParser.get(className, self.CONFIG_BATCH_DEFAULT_STRATEGY_AUTOCLEANUP_STATE)

    # URLFetch requests counter init
    self.sendURLFetchRequestCounter = 0
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_REQUESTS_NAME, 0, self.STAT_FIELDS_OPERATION_SET)

    # Check URLs in active batches before add in to new batch init
    self.configVars[self.CONFIG_BATCH_DEFAULT_CHECK_URLS_IN_ACTIVE_BATCHES] = \
                   configParser.getint(className, self.CONFIG_BATCH_DEFAULT_CHECK_URLS_IN_ACTIVE_BATCHES)

    # Purge algorithm init
    self.configVars[self.CONFIG_PURGE_PERIOD] = configParser.getint(className, self.CONFIG_PURGE_PERIOD)
    self.configVars[self.CONFIG_PURGE_BATCH_DEFAULT_MAX_TIME] = \
                   configParser.getint(className, self.CONFIG_PURGE_BATCH_DEFAULT_MAX_TIME)
    self.configVars[self.CONFIG_PURGE_BATCH_MAX_URLS] = configParser.getint(className, self.CONFIG_PURGE_BATCH_MAX_URLS)
    self.configVars[self.CONFIG_PURGE_BATCH_QUEUE_TASK_TTL] = \
                   configParser.getint(className, self.CONFIG_PURGE_BATCH_QUEUE_TASK_TTL)
    self.configVars[self.CONFIG_PURGE_BATCH_DEFAULT_STARTER] = \
                   configParser.get(className, self.CONFIG_PURGE_BATCH_DEFAULT_STARTER)
    self.configVars[self.CONFIG_DRCE_DB_APP_NAME] = configParser.get(className, self.CONFIG_DRCE_DB_APP_NAME)
    self.configVars[self.CONFIG_PURGE_BATCH_MAX_TASKS] = \
                   configParser.getint(className, self.CONFIG_PURGE_BATCH_MAX_TASKS)
    self.configVars[self.CONFIG_PURGE_MODE] = configParser.getint(className, self.CONFIG_PURGE_MODE)

    # Purge batches in queue counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    self.processPurgeLastTs = time.time()
    # Purge total batches counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_TOTAL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Purge batches cancelled DRCE task requests counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_CANCELLED_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Purge batches DRCE task requests error counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_ERROR_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Purge batches DRCE task requests execution faults counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Purge batches DRCE task check state faults counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_CHECK_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)

    # Crawling task DTM name
    self.configVars[self.CONFIG_TASK_DTM_NAME_CRAWLING] = configParser.get(className,
                                                                           self.CONFIG_TASK_DTM_NAME_CRAWLING)
    # Purging task DTM name
    self.configVars[self.CONFIG_TASK_DTM_NAME_PURGING] = configParser.get(className,
                                                                          self.CONFIG_TASK_DTM_NAME_PURGING)
    # Crawling task DTM type
    self.configVars[self.CONFIG_TASK_DTM_TYPE_CRAWLING] = configParser.getint(className,
                                                                              self.CONFIG_TASK_DTM_TYPE_CRAWLING)
    # Purging task DTM type
    self.configVars[self.CONFIG_TASK_DTM_TYPE_PURGING] = configParser.getint(className,
                                                                             self.CONFIG_TASK_DTM_TYPE_PURGING)

    # Init default resource aging settings
    self.configVars[self.CONFIG_AGING_PERIOD] = configParser.getint(className,
                                                                    self.CONFIG_AGING_PERIOD)
    self.configVars[self.CONFIG_RESOURCE_AGING_MODE] = configParser.getint(className,
                                                                           self.CONFIG_RESOURCE_AGING_MODE)
    self.configVars[self.CONFIG_TASK_DTM_NAME_AGING] = configParser.get(className, self.CONFIG_TASK_DTM_NAME_AGING)
    self.configVars[self.CONFIG_TASK_DTM_TYPE_AGING] = configParser.getint(className, self.CONFIG_TASK_DTM_TYPE_AGING)
    self.configVars[self.CONFIG_AGE_BATCH_DEFAULT_MAX_TIME] = configParser.getint(className,
                                                                                  self.CONFIG_AGE_BATCH_DEFAULT_MAX_TIME)  #  pylint: disable=C0301
    self.configVars[self.CONFIG_AGE_BATCH_MAX_URLS_SITE] = configParser.getint(className,
                                                                               self.CONFIG_AGE_BATCH_MAX_URLS_SITE)
    self.configVars[self.CONFIG_AGE_BATCH_MAX_URLS_TOTAL] = configParser.getint(className,
                                                                                self.CONFIG_AGE_BATCH_MAX_URLS_TOTAL)
    self.configVars[self.CONFIG_AGE_BATCH_MAX_SITES] = configParser.getint(className, self.CONFIG_AGE_BATCH_MAX_SITES)
    self.configVars[self.CONFIG_AGE_BATCH_QUEUE_TASK_TTL] = configParser.getint(className,
                                                                                self.CONFIG_AGE_BATCH_QUEUE_TASK_TTL)
    self.configVars[self.CONFIG_AGE_BATCH_DEFAULT_STARTER] = configParser.get(className,
                                                                              self.CONFIG_AGE_BATCH_DEFAULT_STARTER)
    self.configVars[self.CONFIG_AGE_BATCH_MAX_TASKS] = configParser.getint(className, self.CONFIG_AGE_BATCH_MAX_TASKS)
    self.configVars[self.CONFIG_AGE_BATCH_URL_CRITERION] = configParser.get(className,
                                                                            self.CONFIG_AGE_BATCH_URL_CRITERION)
    self.configVars[self.CONFIG_AGE_BATCH_SITE_CRITERION] = configParser.get(className,
                                                                             self.CONFIG_AGE_BATCH_SITE_CRITERION)
    self.processAgingLastTs = time.time()

    # Age batches in queue counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Age total batches counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_TOTAL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Age batches cancelled DRCE task requests counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_CANCELLED_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Age batches DRCE task requests error counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_ERROR_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Age batches DRCE task requests execution faults counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Age batches DRCE task check state faults counter name for stat variables
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_CHECK_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)

    if configParser.has_option(className, self.CONFIG_BATCH_MAX_ITERATIONS):
      self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS] = configParser.getint(className,
                                                                              self.CONFIG_BATCH_MAX_ITERATIONS)
    else:
      self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS] = self.CONFIG_BATCH_MAX_ITERATIONS_DEFAULT



  # #Events wait timeout handler, for timeout state of the connections polling. Executes periodical check of DTM tasks
  # and initiate the main crawling iteration cycle
  #
  def on_poll_timeout(self):
    logger.debug("Periodic iteration started.")
    try:
      # Process regular crawl batching
      if self.configVars[self.CONFIG_REGULAR_CRAWL_PERIOD] > 0 and\
        time.time() - self.processRegularCrawlLastTs > self.configVars[self.CONFIG_REGULAR_CRAWL_PERIOD]:
        self.processRegularCrawlLastTs = time.time()
        if self.configVars[self.CONFIG_REGULAR_CRAWL_MODE] == 1:
          crawlTasks = self.getBatchTasksCount(self.BATCH_TASK_TYPE_CRAWL)
          logger.debug("URL_FETCH for regular crawling, now crawl tasks: %s, URLFetch counter:%s", str(crawlTasks),
                       str(self.sendURLFetchRequestCounter))
          # Process the first step of crawling iteration
          if self.configVars[self.CONFIG_BATCH_MAX_TASKS] > crawlTasks and\
             self.configVars[self.CONFIG_BATCH_MAX_TASKS] > self.sendURLFetchRequestCounter:
            self.sendURLFetchRequest()
            self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            self.sendURLFetchRequestCounter = self.sendURLFetchRequestCounter + 1
            self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_REQUESTS_NAME, 1,
                                 self.STAT_FIELDS_OPERATION_ADD)
          else:
            self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_CANCELLED_NAME, 1,
                                 self.STAT_FIELDS_OPERATION_ADD)
            logger.debug("Max crawl batch tasks %s>=%s in queue or URLFetch counter %s reached!",
                         str(crawlTasks), str(self.configVars[self.CONFIG_BATCH_MAX_TASKS]),
                         str(self.sendURLFetchRequestCounter))
        else:
          logger.debug("Regular crawling disabled!")

      # Process Batch queue
      if self.configVars[self.CONFIG_BATCH_QUEUE_PERIOD] > 0 and\
        time.time() - self.processBatchQueuelLastTs > self.configVars[self.CONFIG_BATCH_QUEUE_PERIOD]:
        self.processBatchQueuelLastTs = time.time()
        logger.debug("Process DTM tasks queue!")
        # Process the DTM tasks queue
        self.processDTMTasksQueue()

      # Process periodic selected for crawling URLs return
      if self.configVars[self.CONFIG_RET_URLS_PERIOD] > 0 and\
        time.time() - self.processSelectedURLsRetLastTs > self.configVars[self.CONFIG_RET_URLS_PERIOD]:
        if self.configVars[self.CONFIG_RET_URLS_MODE] == 1:
          logger.debug("Now time to perform URLs return, interval " + str(self.configVars[self.CONFIG_RET_URLS_PERIOD]))
          self.processSelectedURLsRetLastTs = time.time()
          self.processSelectedURLsReturn()
        else:
          logger.debug("URLs return for crawling disabled!")

      # TODO: Process incremental crawling (not tested)
      if self.configVars[self.CONFIG_INCR_CRAWL_PERIOD] > 0 and\
        time.time() - self.processIncrCrawlLastTs > self.configVars[self.CONFIG_INCR_CRAWL_PERIOD]:
        self.processIncrCrawlLastTs = time.time()
        logger.debug("URL_FETCH for incremental crawling iteration!")
        if self.configVars[self.CONFIG_INCR_CRAWL_MODE] == 1:
          # Process the first step of incremental crawling iteration
          self.sendIncrURLRequest()
        else:
          logger.debug("Incremental crawling disabled!")

      # Process aging resources batching
      if self.configVars[self.CONFIG_AGING_PERIOD] > 0 and\
        time.time() - self.processAgingLastTs > (int(self.configVars[self.CONFIG_AGING_PERIOD]) * 60):
        if self.configVars[self.CONFIG_RESOURCE_AGING_MODE] == 1:
          logger.debug("Now time to perform aging, interval %s", str(self.configVars[self.CONFIG_AGING_PERIOD]))
          self.processAgingLastTs = time.time()
          ageTasks = self.getBatchTasksCount(self.BATCH_TASK_TYPE_AGE)
          logger.debug("Age batching, tasks: %s!", str(ageTasks))
          if self.configVars[self.CONFIG_AGE_BATCH_MAX_TASKS] > ageTasks:
            if self.setAgeBatch():
              self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_NAME,
                                   self.getBatchTasksCount(self.BATCH_TASK_TYPE_AGE), self.STAT_FIELDS_OPERATION_SET)
              self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_TOTAL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            else:
              self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_ERROR_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
          else:
            self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_CANCELLED_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            logger.debug("Max age tasks %s reached", str(ageTasks))
        else:
          logger.debug("Resources aging disabled")

      # Process purge resources batching
      if self.configVars[self.CONFIG_PURGE_PERIOD] > 0 and\
        time.time() - self.processPurgeLastTs > (int(self.configVars[self.CONFIG_PURGE_PERIOD]) * 60):
        self.processPurgeLastTs = time.time()
        logger.debug("Now time to perform purging, interval %s", str(self.configVars[self.CONFIG_PURGE_PERIOD]))
        if self.configVars[self.CONFIG_PURGE_MODE] == 1:
          purgeTasks = self.getBatchTasksCount(self.BATCH_TASK_TYPE_PURGE)
          logger.debug("Purge batching, tasks: %s!", str(purgeTasks))
          if self.configVars[self.CONFIG_PURGE_BATCH_MAX_TASKS] > purgeTasks:
            if self.setPurgeBatch():
              self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_NAME,
                                   self.getBatchTasksCount(self.BATCH_TASK_TYPE_PURGE), self.STAT_FIELDS_OPERATION_SET)
              self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_TOTAL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            else:
              self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_ERROR_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
          else:
            self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_CANCELLED_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            logger.debug("Max purge tasks %s reached", str(purgeTasks))
        else:
          logger.debug("Purging disabled!")

    except IOError as e:
      del e
    except Exception as err:
      logger.error("Exception: " + str(err.message) + "\n" + Utils.getTracebackInfo())

    logger.debug("Periodic iteration finished.")



  # #Create new purge batch, send it to execute as asynchronous DRCE task and insert in to the batches queue
  #
  #
  def setPurgeBatch(self):
    ret = False

    try:
      crit = {EventObjects.URLPurge.CRITERION_LIMIT:str(self.configVars[self.CONFIG_PURGE_BATCH_MAX_URLS])}
      batchURLPurge = EventObjects.URLPurge(None, None, EventObjects.URLStatus.URL_TYPE_MD5, crit)
      # Process all sites from first listed by SHOW TABLES
      batchURLPurge.siteLimits = (0, EventObjects.URLPurge.ALL_SITES)
      taskId = self.sendBatchTaskToDTM(batchURLPurge)
      if taskId > 0:
        logger.debug("DTM purge batch was set, taskId=%s", str(taskId))
        # Insert the Batch object in to the queue
        batchURLPurge.queuedTs = time.time()
        batchURLPurge.crawlerType = EventObjects.Batch.TYPE_PURGE
        self.dtmTasksQueue[taskId] = batchURLPurge
        ret = True
      else:
        logger.error("Error send purge batch task to DTM!")

    except Exception as err:
      logger.error("Exception: " + str(err.message) + "\n" + Utils.getTracebackInfo())

    return ret



  # #Create new age batch, send it to execute as asynchronous DRCE task and insert in to the batches queue
  #
  #
  def setAgeBatch(self):
    ret = False

    try:
      # Set default criterions
      urlsCriterions = {EventObjects.URLAge.CRITERION_LIMIT:str(self.configVars[self.CONFIG_AGE_BATCH_MAX_URLS_SITE]),
                        EventObjects.URLAge.CRITERION_WHERE:str(self.configVars[self.CONFIG_AGE_BATCH_URL_CRITERION])}
      sitesCriterions = {EventObjects.URLAge.CRITERION_WHERE:str(self.configVars[self.CONFIG_AGE_BATCH_SITE_CRITERION])}

      batchURLAge = EventObjects.URLAge(urlsCriterions, sitesCriterions)
      batchURLAge.maxURLs = int(self.configVars[self.CONFIG_AGE_BATCH_MAX_URLS_TOTAL])
      batchURLAge.delayedType = EventObjects.DELAYED_OPERATION
      taskId = self.sendBatchTaskToDTM(batchURLAge)
      if taskId > 0:
        logger.debug("DTM age batch was set, taskId=%s", str(taskId))
        # Insert the Batch object in to the queue
        batchURLAge.queuedTs = time.time()
        batchURLAge.crawlerType = EventObjects.Batch.TYPE_AGE
        self.dtmTasksQueue[taskId] = batchURLAge
        ret = True
      else:
        logger.error("Error send age batch task to DTM!")

    except Exception as err:
      logger.error("Exception: " + str(err.message) + "\n" + Utils.getTracebackInfo())

    return ret



  # #onURLFetchResponse event handler
  #
  # @param event instance of Event object
  def onURLFetchResponse(self, event):
    try:
      if self.sendURLFetchRequestCounter > 0:
        self.sendURLFetchRequestCounter = self.sendURLFetchRequestCounter - 1
      if self.statFields[DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_REQUESTS_NAME] > 0:
        self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_REQUESTS_NAME, 1,
                             self.STAT_FIELDS_OPERATION_SUB)

      logger.debug("Reply received on URL fetch: %s", varDump(event))
      if event.cookie is not None and isinstance(event.cookie, dict):
        crawlerType = event.cookie.get('type', EventObjects.Batch.TYPE_NORMAL_CRAWLER)
        fetchType = event.cookie.get(self.BATCH_FETCH_TYPE_COOKIE_NAME, None)
        batchId = event.cookie.get(self.BATCH_ID_COOKIE_NAME, 0)
      else:
        crawlerType = EventObjects.Batch.TYPE_NORMAL_CRAWLER
        fetchType = None
        batchId = 0
      clientResponse = event.eventObj
      if clientResponse.errorCode == EventObjects.ClientResponse.STATUS_OK:
        if len(clientResponse.itemsList) > 0:
          if event.cookie is not None and\
            (isinstance(event.cookie, dict) and\
             EventObjects.Batch.OPERATION_TYPE_NAME in event.cookie and\
             (event.cookie[EventObjects.Batch.OPERATION_TYPE_NAME] == EventObjects.Batch.TYPE_NORMAL_CRAWLER or\
              event.cookie[EventObjects.Batch.OPERATION_TYPE_NAME] == EventObjects.Batch.TYPE_INCR_CRAWLER)):
            # Process response for main crawling URLFetch request
            batch = self.makeBatchFromClientResponseItems(clientResponse.itemsList, crawlerType, batchId)
            if len(batch.items) > 0:
              if self.configVars[self.CONFIG_REGULAR_CRAWL_PROPAGATE_URLS] and\
                isinstance(batch, EventObjects.Batch):
                # Execute URLNew and insert URLs from the Batch in CRAWLED state to stop redundant crawling
                self.sendURLNew(batch.items)
              maxExecutionTime = None
              if fetchType is not None and fetchType == EventObjects.Site.FETCH_TYPE_DYNAMIC:
                if 'dfetcher_BatchMaxExecutionTime' in self.configVars[self.CONFIG_BATCH_FETCH_TYPE]:
                  maxExecutionTime = self.configVars[self.CONFIG_BATCH_FETCH_TYPE]['dfetcher_BatchMaxExecutionTime']
              # Send New Batch task to DTM
              taskId = self.sendBatchTaskToDTM(batch, maxExecutionTime)
              if taskId > 0:
                logger.debug("DTM batch was set, taskId=%s", str(taskId))
                # Insert the Batch object in to the queue
                batch.queuedTs = time.time()
                if fetchType is not None and fetchType == EventObjects.Site.FETCH_TYPE_DYNAMIC:
                  if 'dfetcher_BatchQueueTaskTTL' in self.configVars[self.CONFIG_BATCH_FETCH_TYPE]:
                    ttl = self.configVars[self.CONFIG_BATCH_FETCH_TYPE]['dfetcher_BatchQueueTaskTTL']
                    batch.ttl = ttl
                self.dtmTasksQueue[taskId] = batch
                self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_QUEUE_NAME, len(self.dtmTasksQueue),
                                     self.STAT_FIELDS_OPERATION_SET)
              else:
                logger.error("Error send the Batch object to DTM!")
                if crawlerType == EventObjects.Batch.TYPE_NORMAL_CRAWLER:
                  # Update URLs state back to New to get possibility to select them next time
                  self.sendURLUpdate(batch.items, batch.id, False)
            else:
              logger.debug("There is no items in batch, cancelled!")
          else:
            # Process response for URLs return URLFetch request
            urls = self.getURLsCountFromClientResponseItems(clientResponse.itemsList)
            self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_RET_NAME, urls, self.STAT_FIELDS_OPERATION_ADD)
            logger.debug(str(urls) + " URLs returned back to state NEW because processing TTL exceed.")
        else:
          logger.debug("There is empty clientResponse.itemsList")
      else:
        logger.error("URLFetch response error: " + str(clientResponse.errorCode) + " : " + clientResponse.errorMessage)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")


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


  # #make the Batch object from the ClientResponse object items
  # @param clientResponseItems The list of ClientResponseItem objects
  # @param maxExecutionTime for the hce-node DRCE asynchronous task
  #
  def sendBatchTaskToDTM(self, batch, maxExecutionTime=None):
    taskId = 0
    # Prepare NewTask object
    if isinstance(batch, EventObjects.Batch):
      # Crawl batch
      appName = self.configVars[self.CONFIG_DRCE_CRAWLER_APP_NAME]
    else:
      # Purge or Age batch
      appName = self.configVars[self.CONFIG_DRCE_DB_APP_NAME]
    newTaskObj = dtm.EventObjects.NewTask(appName)
    # Set DRCE task name and type
    newTaskObj.setSessionVar("tmode", dtm.EventObjects.Task.TASK_MODE_ASYNCH)
    if isinstance(batch, EventObjects.Batch):
      # Crawl batch
      newTaskObj.setSessionVar("shell", self.configVars[self.CONFIG_BATCH_DEFAULT_STARTER])
      if maxExecutionTime is None:
        mt = int(self.configVars[self.CONFIG_BATCH_DEFAULT_MAX_TIME])
      else:
        mt = int(maxExecutionTime)
      newTaskObj.setSessionVar("time_max", mt * 1000)
      newTaskObj.name = self.configVars[self.CONFIG_TASK_DTM_NAME_CRAWLING]
      newTaskObj.type = self.configVars[self.CONFIG_TASK_DTM_TYPE_CRAWLING]
    else:
      if isinstance(batch, EventObjects.URLPurge):
        # Purge batch
        newTaskObj.setSessionVar("shell", self.configVars[self.CONFIG_PURGE_BATCH_DEFAULT_STARTER])
        newTaskObj.setSessionVar("time_max", int(self.configVars[self.CONFIG_PURGE_BATCH_DEFAULT_MAX_TIME]) * 1000)
        newTaskObj.name = self.configVars[self.CONFIG_TASK_DTM_NAME_PURGING]
        newTaskObj.type = self.configVars[self.CONFIG_TASK_DTM_TYPE_PURGING]
        # Set route round-robin to prevent default resource-usage balancing for purging tasks
        newTaskObj.setSessionVar("route", DC_CONSTS.DRCE_REQUEST_ROUTING_RND)
      else:
        # Age batch
        newTaskObj.setSessionVar("shell", self.configVars[self.CONFIG_AGE_BATCH_DEFAULT_STARTER])
        newTaskObj.setSessionVar("time_max", int(self.configVars[self.CONFIG_AGE_BATCH_DEFAULT_MAX_TIME]) * 1000)
        newTaskObj.name = self.configVars[self.CONFIG_TASK_DTM_NAME_AGING]
        newTaskObj.type = self.configVars[self.CONFIG_TASK_DTM_TYPE_AGING]
        # Set route round-robin to prevent default resource-usage balancing for aging tasks
        newTaskObj.setSessionVar("route", DC_CONSTS.DRCE_REQUEST_ROUTING_ROUND_ROBIN)
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
    # Set task Id
    if not hasattr(batch, 'id') or batch.id == 0:
      batch.id = newTaskObj.id
    else:
      newTaskObj.id = batch.id
    # Set task's input object string stream
    if isinstance(batch, EventObjects.Batch):
      newTaskObj.input = pickle.dumps(batch)
    else:
      if isinstance(batch, EventObjects.URLPurge):
        drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_PURGE, [batch])
      else:
        drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_AGE, [batch])
      newTaskObj.input = pickle.dumps(drceSyncTasksCoverObj)
    # Set task's event
    newTaskEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.NEW_TASK, newTaskObj)
    # Execute task
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



  # #make the Batch object from the ClientResponse object items

  # @param clientResponseItems The list of ClientResponseItem objects
  # @return the Batch object instance
  def makeBatchFromClientResponseItems(self, clientResponseItems, crawlerType, batchId=0):
    batch = EventObjects.Batch(batchId, None, crawlerType)
    batch.maxIterations = self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS]
    batch.maxExecutionTime = self.configVars[self.CONFIG_BATCH_MAX_TIME]
    batch.removeUnprocessedItems = self.configVars[self.CONFIG_BATCH_REMOVE_UNPROCESSED_ITEMS]
    batchItemsCounter = 0
    batchItemsTotalCounter = 0
    uniqueURLsCRCDic = {}
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TOTAL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)

    for item in clientResponseItems:
      if item.errorCode == EventObjects.ClientResponseItem.STATUS_OK:
        if isinstance(item.itemObject, list):
          for url in item.itemObject:
            batchItemsTotalCounter = batchItemsTotalCounter + 1
            if isinstance(url, EventObjects.URL):
              # Check is this URL under processing in another active batch
              if self.configVars[self.CONFIG_BATCH_DEFAULT_CHECK_URLS_IN_ACTIVE_BATCHES] > 0:
                batchTaskId = self.getBatchTaskIdByURL(url.siteId, url.urlMd5)
              else:
                batchTaskId = 0
              if batchTaskId == 0:
                url.batchId = batchId
                batchItem = EventObjects.BatchItem(url.siteId, url.urlMd5, url)
                itemId = str(url.siteId) + ":" + str(url.urlMd5)
                if itemId not in uniqueURLsCRCDic:
                  uniqueURLsCRCDic[itemId] = batchItem
                  logger.debug("Insert batchItem: %s", varDump(batchItem))
                  batch.items.append(batchItem)
                  batchItemsCounter = batchItemsCounter + 1
                  self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
              else:
                logger.debug("URL is under processing of batch %s, skipped from new batch", str(batchTaskId))
            else:
              logger.error("Wrong object type in the itemObject.item: " + str(type(url)) + \
                           " but 'URL' expected")
          if batchItemsCounter > 0:
            self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FILLED_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
        else:
          logger.error("Wrong object type in the ClientResponseItem.itemObject: " + str(type(item.itemObject)) + \
                       " but 'list' expected")
      else:
        logger.debug("ClientResponseItem error: " + str(item.errorCode) + " : " + item.errorMessage)

    logger.debug("Batch object created, items: " + str(batchItemsTotalCounter) + " total, " + str(batchItemsCounter) + \
                " added!")

    return batch



  # #Enumerate URLs number in the ClientResponse object items
  #
  # @param siteId The site Id md5
  # @param urlMd5 The URL Id md5
  # @return the batch Id if URL is under processing and zero if not
  def getBatchTaskIdByURL(self, siteId, urlMd5):
    batchTaskId = 0
    for taskId, taskBatch in self.dtmTasksQueue.items():
      if isinstance(taskBatch, EventObjects.Batch):
        for batchItem in taskBatch.items:
          if batchItem.siteId == siteId and batchItem.urlId == urlMd5:
            batchTaskId = taskId
            break
        if batchTaskId > 0:
          break

    return batchTaskId



  # #Enumerate URLs number in the ClientResponse object items
  #
  # @param clientResponseItems The list of ClientResponseItem objects
  # @return the unique URLs number
  def getURLsCountFromClientResponseItems(self, clientResponseItems, unique=True):
    batchItemsCounter = 0
    batchItemsTotalCounter = 0
    uniqueURLsCRCDic = {}

    for item in clientResponseItems:
      if item.errorCode == EventObjects.ClientResponseItem.STATUS_OK:
        if isinstance(item.itemObject, list):
          for url in item.itemObject:
            batchItemsTotalCounter = batchItemsTotalCounter + 1
            if isinstance(url, EventObjects.URL):
              itemId = str(url.siteId) + ":" + str(url.urlMd5)
              if itemId not in uniqueURLsCRCDic:
                uniqueURLsCRCDic[itemId] = 1
                batchItemsCounter = batchItemsCounter + 1
              else:
                uniqueURLsCRCDic[itemId] += 1
            else:
              logger.error("Wrong object type in the itemObject.item: " + str(type(url)) + \
                           " but 'URL' expected")
        else:
          logger.error("Wrong object type in the ClientResponseItem.itemObject: " + str(type(item.itemObject)) + \
                       " but 'list' expected")
      else:
        logger.debug("ClientResponseItem error: " + str(item.errorCode) + " : " + item.errorMessage)

    logger.debug("Unique URLs: " + str(batchItemsCounter) + ", total URLs: " + str(batchItemsTotalCounter))

    if unique:
      return batchItemsCounter
    else:
      return batchItemsTotalCounter



  # #Send URLFetch request
  #
  #
  def sendURLFetchRequest(self):
    # Process the first step of crawling iteration
    urlUpdate = EventObjects.URLUpdate(0, "", EventObjects.URLStatus.URL_TYPE_MD5, None,
                                       EventObjects.URL.STATUS_SELECTED_CRAWLING)
    urlUpdate.tcDate = SQLExpression("NOW()")
    newDTMTaskObj = dtm.EventObjects.NewTask('')
    urlUpdate.batchId = newDTMTaskObj.id
    limit = str(self.configVars[self.CONFIG_BATCH_MAX_URLS])
    fetchType = None
    fetcherCondition = ''
    if 'splitter' in self.configVars[self.CONFIG_BATCH_FETCH_TYPE]:
      random.seed()
      fetchType = int((random.random() + 1) > float(self.configVars[self.CONFIG_BATCH_FETCH_TYPE]['splitter'])) + 1
      fetcherCondition = ' AND `FetchType`=' + str(fetchType)
      if fetchType == EventObjects.Site.FETCH_TYPE_DYNAMIC and\
        'dfetcher_BatchDefaultMaxURLs' in self.configVars[self.CONFIG_BATCH_FETCH_TYPE]:
        limit = self.configVars[self.CONFIG_BATCH_FETCH_TYPE]['dfetcher_BatchDefaultMaxURLs']
    # Create URLFetch object with URLUpdate to update selected URLs state
    sitesCriterions = {EventObjects.URLFetch.CRITERION_WHERE: " `sites`.`State`=" + \
                       str(EventObjects.Site.STATE_ACTIVE) + \
                       " AND IFNULL((SELECT `Value` FROM `sites_properties` WHERE `Name`='MODES_FLAG') & 1, 1)<>0" + \
                       fetcherCondition
                      }
    urlCriterions = {EventObjects.URLFetch.CRITERION_WHERE: "`Status`=" + str(EventObjects.URL.STATUS_NEW) + \
                     " AND `State`=0",
                     EventObjects.URLFetch.CRITERION_ORDER: self.configVars[self.CONFIG_BATCH_ORDER_BY_URLS],
                     EventObjects.URLFetch.CRITERION_LIMIT: limit}
    siteUpdate = EventObjects.SiteUpdate(0)
    siteUpdate.tcDate = EventObjects.SQLExpression("Now()")
    urlFetch = EventObjects.URLFetch(None, urlCriterions, sitesCriterions, urlUpdate, siteUpdate)
    urlFetch.algorithm = EventObjects.URLFetch.PROPORTIONAL_ALGORITHM
    urlFetch.maxURLs = int(limit)
    urlFetchEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_FETCH, [urlFetch])
    urlFetchEvent.cookie = {EventObjects.Batch.OPERATION_TYPE_NAME: EventObjects.Batch.TYPE_NORMAL_CRAWLER,
                            self.BATCH_ID_COOKIE_NAME: urlUpdate.batchId}
    if fetchType is not None:
      urlFetchEvent.cookie[self.BATCH_FETCH_TYPE_COOKIE_NAME] = fetchType
    # Send request URLFetch to SitesManager
    self.send(self.clientSitesManagerName, urlFetchEvent)
    logger.debug("The URLFetch request to SitesManager sent!")

    if fetchType is not None and fetchType == EventObjects.Site.FETCH_TYPE_DYNAMIC:
      # Batches dynamic fetcher's batches counter init in stat vars
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FETCHER_DYNAMIC, 1, self.STAT_FIELDS_OPERATION_ADD)
    elif fetchType is not None and fetchType == EventObjects.Site.FETCH_TYPE_STATIC:
      # Batches static fetcher's batches counter init in stat vars
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FETCHER_STATIC, 1, self.STAT_FIELDS_OPERATION_ADD)
    else:
      # Batches mixed static and dynamic fetcher's batches counter init in stat vars
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FETCHER_MIXED, 1, self.STAT_FIELDS_OPERATION_ADD)



  # #Send URLFetch for incremental crawling request
  #
  #
  def sendIncrURLRequest(self):
    # add new state URL.STATUS_SELECTED_CRAWLING_INCREMENTAL and add it state for updating
    urlUpdate = EventObjects.URLUpdate(0, "", EventObjects.URLStatus.URL_TYPE_MD5, None,
                                       EventObjects.URL.STATUS_SELECTED_CRAWLING_INCREMENTAL)
    # Create URLFetch object
    conditionStr = ''' `Status` in (%s, %s, %s, %s) AND `Depth`<=%s \
    AND `State`=0 AND timediff(`TcDate`,`LastModified`)>=0 AND (NOW() - `TcDate`) > timediff(`TcDate`, `LastModified`)
    ''' % (EventObjects.URL.STATUS_CRAWLED, EventObjects.URL.STATUS_SELECTED_PROCESSING,
    EventObjects.URL.STATUS_PROCESSING, EventObjects.URL.STATUS_PROCESSED,  # pylint: disable=C0330
    self.configVars[DC_CONSTS.INCR_MAX_DEPTH_CONFIG_VAR_NAME])  # pylint: disable=C0330
    urlCriterions = {EventObjects.URLFetch.CRITERION_WHERE: conditionStr,
                     EventObjects.URLFetch.CRITERION_ORDER: "`Depth` ASC, `MRate` DESC, `UDate` DESC",
                     EventObjects.URLFetch.CRITERION_LIMIT:
                     str(self.configVars[DC_CONSTS.INCR_MAX_URLS_CONFIG_VAR_NAME])
                    }

    siteCriterions = {EventObjects.URLFetch.CRITERION_WHERE: "`State`=" + \
                     str(EventObjects.Site.STATE_ACTIVE) + "`ID` in (SELECT `Site_Id` FROM `sites_properties` " + \
                     "WHERE `Name`='INCREMENTAL_CRAWLING' AND `Value`='1') " + \
                     "AND IFNULL((SELECT `Value` FROM `sites_properties` WHERE `Name`='MODES_FLAG') & 1, 1)<>0"}  # pylint: disable=C0301
    siteUpdate = EventObjects.SiteUpdate(0)
    siteUpdate.tcDate = EventObjects.SQLExpression("Now()")
    urlFetch = EventObjects.URLFetch(None, urlCriterions, siteCriterions, urlUpdate, siteUpdate)
    urlFetch.algorithm = EventObjects.URLFetch.PROPORTIONAL_ALGORITHM
    urlFetch.maxURLs = self.configVars[DC_CONSTS.INCR_MAX_URLS_CONFIG_VAR_NAME]
    urlFetchEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_FETCH, [urlFetch])
    urlFetchEvent.cookie = {"type": EventObjects.Batch.TYPE_INCR_CRAWLER}
    # Send request URLFetch to SitesManager
    self.send(self.clientSitesManagerName, urlFetchEvent)
    logger.debug("The URLFetch for incremental crawler request to SitesManager sent!")
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URL_FETCH_INCR_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)



  # #Process selected for crawling URLs return request
  #
  #
  def processSelectedURLsReturn(self):
    # Update to NEW state to return URLs in to the queue
    urlUpdate = EventObjects.URLUpdate(0, "", EventObjects.URLStatus.URL_TYPE_MD5, None,
                                       EventObjects.URL.STATUS_NEW)
    # Create URLFetch object with URLUpdate to update selected URLs state
    sitesCriterions = {EventObjects.URLFetch.CRITERION_WHERE: "`State`=" + str(EventObjects.Site.STATE_ACTIVE)}
    urlCriterions = {EventObjects.URLFetch.CRITERION_WHERE: "`Status` IN (" + \
                     str(EventObjects.URL.STATUS_SELECTED_CRAWLING) + "," + \
                     str(EventObjects.URL.STATUS_CRAWLING) + "," + \
                     str(EventObjects.URL.STATUS_SELECTED_PROCESSING) + "," + \
                     str(EventObjects.URL.STATUS_PROCESSING) + ") AND DATE_ADD(UDate, INTERVAL " + \
                     str(self.configVars[self.CONFIG_RET_URLS_TTL]) + " MINUTE) < NOW()",
                     EventObjects.URLFetch.CRITERION_ORDER: "`UDate` ASC",
                     EventObjects.URLFetch.CRITERION_LIMIT: str(self.configVars[self.CONFIG_RET_URLS_MAX_NUMBER])}
    urlFetch = EventObjects.URLFetch(None, urlCriterions, sitesCriterions, urlUpdate)
    urlFetch.algorithm = EventObjects.URLFetch.PROPORTIONAL_ALGORITHM
    urlFetch.maxURLs = self.configVars[self.CONFIG_RET_URLS_MAX_NUMBER]
    urlFetchEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_FETCH, [urlFetch])
    urlFetchEvent.cookie = {EventObjects.Batch.OPERATION_TYPE_NAME: EventObjects.Batch.TYPE_URLS_RETURN}
    # Send request URLFetch to SitesManager
    self.send(self.clientSitesManagerName, urlFetchEvent)
    logger.debug("The URLFetch request to SitesManager sent!")



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
      # if eeResponseData is not None and type(eeResponseData) == type(dtm.EventObjects.EEResponseData(0)):
      if eeResponseData is not None and isinstance(eeResponseData, dtm.EventObjects.EEResponseData):
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
          logger.error("DTM getTasksStatus taskId=" + str(taskId) + " returned empty fields array in response:\n" + \
                       Utils.varDump(listTaskManagerFields))
      else:
        logger.error("DTM getTasksStatus taskId=" + str(taskId) + " returned wrong data:\n" + \
                     Utils.varDump(listTaskManagerFields))

    return taskState



  # #Process the DTM tasks queue
  #
  #
  def processDTMTasksQueue(self):
    tmpQueue = {}
    self.updateDTMTasksQueueCounters()
    itemsTotal = 0
    tasksWithItems = 0

    # Process the DTM tasks queue
    for taskId, taskBatch in self.dtmTasksQueue.items():
      if isinstance(taskBatch, EventObjects.Batch):
        if hasattr(taskBatch, 'ttl'):
          ttl = taskBatch.ttl
        else:
          ttl = self.configVars[self.CONFIG_BATCH_QUEUE_TASK_TTL]
      else:
        ttl = self.configVars[self.CONFIG_PURGE_BATCH_QUEUE_TASK_TTL]
      if hasattr(taskBatch, 'items'):
        items = len(taskBatch.items)
        tasksWithItems += 1
      else:
        items = 0
      itemsTotal += items
      logger.debug("Batch in queue type: %s, taskId: %s, ttl: %s, items: %s", str(type(taskBatch)), str(taskId),
                   str(ttl), str(items))
      batchState = self.getDTMTaskState(taskId)
      if batchState != None:
        logger.debug("Batch state: %s", str(batchState))
        if self.isDTMTaskDead(batchState, taskBatch.queuedTs, ttl):
          # Delete task in DTM and task's data in EE (DRCE)
          deleteTaskObj = dtm.EventObjects.DeleteTask(taskId)
          deleteTaskEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_TASK, deleteTaskObj)
          generalResponse = self.dtmdRequestExecute(deleteTaskEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
          logger.debug("DTM DeleteTask request finished, taskId=" + str(taskId))
          if generalResponse is not None:
            if generalResponse.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK:
              logger.debug("DTM task deleted, taskId=" + str(taskId))
              if batchState == dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED:
                logger.debug("batch:\n" + varDump(taskBatch) + "\n finished, taskId=" + str(taskId))
                self.processFinishedBatch(taskBatch)
              else:
                logger.debug("batch:" + varDump(taskBatch) + " not finished, state=" + str(batchState))
                self.finishDTMTaskFaultPostProcess(taskBatch)
            else:
              # Save this batch to check it later
              tmpQueue[taskId] = taskBatch
              logger.error("DTM delete task taskId=" + str(taskId) + ", error: " + str(generalResponse.errorCode) + \
                           " : " + generalResponse.errorMessage + ", generalResponse:" + varDump(generalResponse))
              self.deleteDTMTaskFaultCountersUpdate(taskBatch)
          else:
            # Save this batch to check it later
            tmpQueue[taskId] = taskBatch
            logger.error("DTM delete task error: wrong response or timeout, taskId=" + str(taskId) + " still in queue!")
        else:
          logger.debug("DTM task still alive Id=" + str(taskId) + " state=" + str(batchState))
          if time.time() - taskBatch.queuedTs > ttl:
            self.finishDTMTaskFaultPostProcess(taskBatch, taskId, ttl, False)
          else:
            # Save this batch to check it later
            tmpQueue[taskId] = taskBatch
            logger.debug("DTM task Id=" + str(taskId) + " still in queue")
      else:
        logger.error("DTM check task state error: wrong response or timeout, taskId=" + str(taskId) + "!")
        if time.time() - taskBatch.queuedTs > ttl:
          logger.error("DTM task Id=" + str(taskId) + " removed from queue by TTL:" + str(ttl))
        else:
          # Save this batch to check it later
          tmpQueue[taskId] = taskBatch
          self.checkDTMTaskFaultCountersUpdate(taskBatch)
          logger.error("DTM task Id=" + str(taskId) + " saved in queue.")

    self.dtmTasksQueue = tmpQueue
    self.updateDTMTasksQueueCounters(tasksWithItems, itemsTotal)


  # #Update DTM task fault counters for correspondent type of the task
  #
  #
  def finishDTMTaskFaultPostProcess(self, taskBatch, taskId=None, ttl=0, incrementFaultsCounter=True):
    if taskId is not None and taskId > 0:
      # Terminate task and delete it's data request
      deleteTaskObj = dtm.EventObjects.DeleteTask(taskId)
      deleteTaskObj.action = dtm.EventObjects.DeleteTask.ACTION_TERMINATE_TASK_AND_DELETE_DATA
      deleteTaskEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.DELETE_TASK, deleteTaskObj)
      generalResponse = self.dtmdRequestExecute(deleteTaskEvent, self.configVars[self.CONFIG_DTMD_TIMEOUT])
      logger.error("DTM task Id=" + str(taskId) + " terminated and removed from queue by TTL:" + str(ttl) + \
                   ", generalResponse=" + str(generalResponse) + ", batch=" + str(taskBatch))

    if isinstance(taskBatch, EventObjects.Batch):
      if incrementFaultsCounter:
        self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
        self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_FAULT_NAME, len(taskBatch.items),
                             self.STAT_FIELDS_OPERATION_ADD)
      if taskId is not None and taskId > 0 and incrementFaultsCounter:
        self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_TTL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
      # Send update URLs of not finished batch on all nodes to get possibility to crawl them next time
      self.sendURLUpdate(taskBatch.items, taskBatch.id, False)
    else:
      if isinstance(taskBatch, EventObjects.URLPurge):
        self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
      else:
        self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)



  # #Update DTM task fault counters for correspondent type of the task
  #
  #
  def checkDTMTaskFaultCountersUpdate(self, taskBatch):
    if isinstance(taskBatch, EventObjects.Batch):
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_CHECK_FAULT_NAME, 1,
                           self.STAT_FIELDS_OPERATION_ADD)
    else:
      if isinstance(taskBatch, EventObjects.URLPurge):
        self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_CHECK_FAULT_NAME, 1,
                             self.STAT_FIELDS_OPERATION_ADD)
      else:
        self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_CHECK_FAULT_NAME, 1,
                             self.STAT_FIELDS_OPERATION_ADD)



  # #Update DTM task fault counters for correspondent type of the task
  #
  #
  def deleteDTMTaskFaultCountersUpdate(self, taskBatch):
    if isinstance(taskBatch, EventObjects.Batch):
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_DELETE_FAULT_NAME, 1,
                           self.STAT_FIELDS_OPERATION_ADD)
    else:
      if isinstance(taskBatch, EventObjects.URLPurge):
        self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_DELETE_FAULT_NAME, 1,
                             self.STAT_FIELDS_OPERATION_ADD)
      else:
        self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_DELETE_FAULT_NAME, 1,
                             self.STAT_FIELDS_OPERATION_ADD)



  # #Check is DTM task alive by status code verification, returns True if yes or False if not
  #
  #
  def isDTMTaskDead(self, state, queuedTs, ttl):
    ret = False

    deadStates = [dtm.EventObjects.EEResponseData.TASK_STATE_FINISHED,
                  dtm.EventObjects.EEResponseData.TASK_STATE_CRASHED,
                  dtm.EventObjects.EEResponseData.TASK_STATE_TERMINATED,
                  dtm.EventObjects.EEResponseData.TASK_STATE_UNDEFINED,
                  dtm.EventObjects.EEResponseData.TASK_STATE_SET_ERROR,
                  dtm.EventObjects.EEResponseData.TASK_STATE_TERMINATED_BY_DRCE_TTL,
                  dtm.EventObjects.EEResponseData.TASK_STATE_SCHEDULE_TRIES_EXCEEDED
                 ]

    if state in deadStates or (state == dtm.EventObjects.EEResponseData.TASK_STATE_NEW_SCHEDULED and time.time() - queuedTs > ttl):
      ret = True

    return ret



  # #Update DTM tasks queue counters
  #
  #
  def updateDTMTasksQueueCounters(self, tasksWithItems=0, itemsTotal=0):
    # Update number of crawl batches
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_QUEUE_NAME,
                         self.getBatchTasksCount(self.BATCH_TASK_TYPE_CRAWL), self.STAT_FIELDS_OPERATION_SET)
    # Update number of purge batches
    self.updateStatField(DC_CONSTS.BATCHES_PURGE_COUNTER_NAME, self.getBatchTasksCount(self.BATCH_TASK_TYPE_PURGE),
                         self.STAT_FIELDS_OPERATION_SET)
    # Update number of age batches
    self.updateStatField(DC_CONSTS.BATCHES_AGE_COUNTER_NAME, self.getBatchTasksCount(self.BATCH_TASK_TYPE_AGE),
                         self.STAT_FIELDS_OPERATION_SET)
    logger.debug("Batches tasks in queue - total:%s, crawl:%s, purge:%s, age:%s", str(len(self.dtmTasksQueue)),
                 str(self.statFields[DC_CONSTS.BATCHES_CRAWL_COUNTER_QUEUE_NAME]),
                 str(self.statFields[DC_CONSTS.BATCHES_PURGE_COUNTER_NAME]),
                 str(self.statFields[DC_CONSTS.BATCHES_AGE_COUNTER_NAME]))

    if tasksWithItems > 0:
      # Update average number of items in queued batches
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_ITEMS_AVG_NAME,
                           itemsTotal / tasksWithItems, self.STAT_FIELDS_OPERATION_SET)



  # #Calculate number of batches
  #
  # @param batchType type of batches, crawl or purge
  #
  def getBatchTasksCount(self, batchType=BATCH_TASK_TYPE_CRAWL):
    ret = 0

    for taskId, taskBatch in self.dtmTasksQueue.items():  # pylint: disable=W0612
      if batchType == self.BATCH_TASK_TYPE_CRAWL:
        if isinstance(taskBatch, EventObjects.Batch):
          ret = ret + 1
      else:
        if batchType == self.BATCH_TASK_TYPE_PURGE:
          if isinstance(taskBatch, EventObjects.URLPurge):
            ret = ret + 1
        else:
          if batchType == self.BATCH_TASK_TYPE_AGE:
            if isinstance(taskBatch, EventObjects.URLAge):
              ret = ret + 1
          else:
            ret = ret + 1

    return ret



  # #Do some post batch processing after batch was successfully finished
  #
  # @param taskBatch the Batch object
  #
  def processFinishedBatch(self, taskBatch):
    if isinstance(taskBatch, EventObjects.Batch):
      if self.configVars[self.CONFIG_CRAWLED_URLS_STRATEGY] == 0:
        self.sendURLUpdate(taskBatch.items, taskBatch.id, True)
        logger.debug("Send update URLs from batch: %s for all foreign hosts by the Batch_Id", str(taskBatch.id))
      else:
        self.sendURLDelete(taskBatch.items, taskBatch.id)
        logger.debug("Send delete URLs from batch: %s for all foreign hosts by the Batch_Id", str(taskBatch.id))
    else:
      if isinstance(taskBatch, EventObjects.URLPurge):
        logger.debug("Purge batch: %s finished!", str(taskBatch.id))
      else:
        logger.debug("Age batch: %s finished!", str(taskBatch.id))



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
            # if type(retEvent.eventObj) == type(dtm.EventObjects.EEResponseData(0)) or\
            #  type(retEvent.eventObj) == type(dtm.EventObjects.GeneralResponse()) or\
            #  isinstance(retEvent.eventObj, list):
            if isinstance(retEvent.eventObj, dtm.EventObjects.EEResponseData) or\
              isinstance(retEvent.eventObj, dtm.EventObjects.GeneralResponse) or\
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
      # notRootURLExpr = " AND `ParentMd5`<>''"
      notRootURLExpr = ''
      # Set status value depends on update reason - crawled successfully or not
      if batchState is True:
        status = EventObjects.URL.STATUS_CRAWLED
        sqlExpression = SQLExpression("`URLMd5`='" + str(batchItem.urlId) + "' AND (" + \
                                      "(`Batch_Id`<>" + str(batchId) + " AND `Status`=" + \
                                      str(EventObjects.URL.STATUS_NEW) + ")" + \
                                      " OR (`Batch_Id`=" + str(batchId) + " AND `Status` IN (" + \
                                      str(EventObjects.URL.STATUS_SELECTED_CRAWLING) + "," + \
                                      str(EventObjects.URL.STATUS_SELECTED_CRAWLING_INCREMENTAL) + "))" + \
                                      ")" + notRootURLExpr)
      else:
        status = EventObjects.URL.STATUS_NEW
        sqlExpression = SQLExpression("`URLMd5`='" + str(batchItem.urlId) + "' AND `Status` IN (" +
                                      str(EventObjects.URL.STATUS_SELECTED_CRAWLING) + "," + \
                                      str(EventObjects.URL.STATUS_SELECTED_CRAWLING_INCREMENTAL) + ")" + \
                                      notRootURLExpr)

      urlUpdate = EventObjects.URLUpdate(batchItem.siteId, batchItem.urlId, EventObjects.URLStatus.URL_TYPE_MD5,
                                         None, status)
      urlUpdate.processed = 0
      urlUpdate.crawled = 0
      urlUpdate.criterions[EventObjects.URLFetch.CRITERION_WHERE] = sqlExpression
      logger.debug("batch: %s, URLUpdate: %s", str(batchId), varDump(urlUpdate))
      urlsList.append(urlUpdate)

    # Make URLUpdate event
    urlUpdateEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_UPDATE, urlsList)
    # Send request URLUpdate to SitesManager
    self.send(self.clientSitesManagerName, urlUpdateEvent)
    logger.debug("The URLUpdate request to SitesManager sent!")



  # #Send URL delete for batch URLs that is not crawled and stays in SELECTED_FOR_CRAWLING state (2)
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
                                         reason=EventObjects.URLDelete.REASON_SELECT_TO_CRAWL_TTL)
      logger.debug("URLDelete: " + varDump(urlDelete))
      urlsList.append(urlDelete)

    # Make URLDelete event
    urlDeleteEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_DELETE, urlsList)
    # Send request URLDelete to SitesManager
    self.send(self.clientSitesManagerName, urlDeleteEvent)
    logger.debug("The URLDelete request to SitesManager sent!")



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


  # #Send URLNew for batch URLs to insert them in state CRAWLED on all hosts to block redundant crawling
  #
  # @param batchItemsList List of BatchItem objects
  def sendURLNew(self, batchItemsList):
    urlsList = []
    # Prepare URLs list to insert
    for batchItem in batchItemsList:
      if isinstance(batchItem.urlObj, EventObjects.URL) and batchItem.urlObj.parentMd5 != '':
        urlObj = copy.deepcopy(batchItem.urlObj)
        urlObj.status = EventObjects.URL.STATUS_CRAWLED
        urlObj.crawled = 0
        urlObj.processed = 0
        urlObj.contentType = ''
        urlObj.charset = ''
        urlObj.batch_Id = 0
        urlObj.errorMask = 0
        urlObj.crawlingTime = 0
        urlObj.processingTime = 0
        urlObj.totalTime = 0
        urlObj.httpCode = 0
        urlObj.size = 0
        urlObj.linksI = 0
        urlObj.linksE = 0
        urlObj.freq = 0
        urlObj.depth = 0
        urlObj.rawContentMd5 = ""
        urlObj.eTag = ""
        urlObj.mRate = 0.0
        urlObj.mRateCounter = 0
        urlObj.contentMask = EventObjects.URL.CONTENT_EMPTY
        urlObj.tagsMask = 0
        urlObj.tagsCount = 0
        urlObj.pDate = SQLExpression("NULL")
        urlObj.urlUpdate = None
        # logger.debug("URLNew item: " + varDump(urlObj))
        logger.debug("URLNew item: %s, batchId: %s", urlObj.urlMd5, str(urlObj.batchId))
        urlsList.append(urlObj)

    if len(urlsList) > 0:
      # Make URLNew event
      urlNewEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_NEW, urlsList)
      # Send request URLNew to SitesManager
      self.send(self.clientSitesManagerName, urlNewEvent)
      logger.debug("The URLNew request to SitesManager sent!")



  # #onURLNewResponse event handler
  #
  # @param event instance of Event object
  def onURLNewResponse(self, event):
    try:
      logger.debug("Reply received on URL new.\n" + Utils.varDump(event))
      clientResponse = event.eventObj
      if clientResponse.errorCode == EventObjects.ClientResponse.STATUS_OK:
        if len(clientResponse.itemsList) > 0:
          for clientResponseItem in clientResponse.itemsList:
            if clientResponseItem.errorCode != EventObjects.ClientResponseItem.STATUS_OK:
              logger.error("URLNew response error: " + str(clientResponseItem.errorCode) + " : " + \
                           clientResponseItem.errorMessage + ", host:" + clientResponseItem.host + ", port:" + \
                           clientResponseItem.port + ", node:" + clientResponseItem.node + "!")
        else:
          logger.error("URLNew response empty list!")
      else:
        logger.error("URLNew response error:" + str(clientResponse.errorCode) + " : " + clientResponse.errorMessage)
    except Exception as err:
      ExceptionLog.handler(logger, err, "Exception:")
