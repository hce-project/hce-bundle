'''
HCE project, Python bindings, Distributed Crawler application.
BatchTasksManagerRealTime object and related classes definitions.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ctypes
import zlib
import logging
import time
import threading

try:
  import cPickle as pickle
except ImportError:
  import pickle

from app.BaseServerManager import BaseServerManager
# from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401
from dc import EventObjects
import dc.Constants as DC_CONSTS
from drce.CommandConvertor import CommandConvertor
from drce.Commands import Session
from drce.Commands import TaskExecuteRequest
from drce.Commands import TaskExecuteStruct
from drce.DRCEManager import ConnectionTimeout, TransportInternalErr, CommandExecutorErr
from drce.DRCEManager import DRCEManager
from drce.DRCEManager import HostParams
import transport.Consts as TRANSPORT_CONSTS
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.IDGenerator import IDGenerator
from transport.UIDGenerator import UIDGenerator

# Logger initialization
logger = Utils.MPLogger().getLogger()
lock = threading.Lock()

# #The BatchTasksManagerRealTime class, is a crawling logic of DC application implemented for on demand requests.
#
# This object is a crawling batches algorithm of DC service for real time on demand crawling requests.
# It uses the DRCE protocol API to send asynchronous tasks directly to the hce-node cluster router
#
class BatchTasksManagerRealTime(BaseServerManager):

  DRCE_REDUCER_TTL = 3000000
  REQUEST_ERROR_OBJECT_TYPE = 1
  REQUEST_ERROR_URLS_COUNT = 2
  REQUEST_ERROR_THREADS_NUMBER_EXCEEDED = 3
  CONFIG_DRCE_REQUEST_ROUTING_DEFAULT = 1
  CONFIG_BATCH_MAX_ITERATIONS_DEFAULT = 2

  # Configuration settings options names
  CONFIG_SERVER = "server"

  CONFIG_DRCE_STARTER_NAME = "DRCEStarterName"
  CONFIG_DRCE_HOST = "DRCEHost"
  CONFIG_DRCE_PORT = "DRCEPort"
  CONFIG_DRCE_TIMEOUT = "DRCETimeout"
  CONFIG_DRCE_CRAWLER_APP_NAME = "DRCECrawlerAppName"
  CONFIG_BATCH_MAX_TIME = "BatchMaxExecutionTime"
  CONFIG_BATCH_MAX_URLS = "BatchMaxURLs"
  CONFIG_MAX_THREADS = "MaxThreads"
  CONFIG_POLLING_TIMEOUT = "PollingTimeout"
  CONFIG_DRCE_REQUEST_ROUTING = "DRCERequestRouting"
  CONFIG_BATCH_MAX_ITERATIONS = "BatchMaxIterations"

  REAL_TIME_CRAWL_THREAD_NAME_PREFIX = 'RtCrawl_'

  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(BatchTasksManagerRealTime, self).__init__()

    # Instantiate the connection builder light if not set
    if connectionBuilderLight is None:
      connectionBuilderLight = ConnectionBuilderLight()

    # Get configuration settings
    className = self.__class__.__name__
    self.serverName = configParser.get(className, self.CONFIG_SERVER)

    # Create connections and raise bind or connect actions for correspondent connection type
    serverConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT, self.serverName)
    self.setEventHandler(DC_CONSTS.EVENT_TYPES.BATCH, self.onEventsHandler)

    # Initialize DRCE API
    self.configVars[self.CONFIG_DRCE_TIMEOUT] = configParser.getint(className, self.CONFIG_DRCE_TIMEOUT)
    self.drceHost = configParser.get(className, self.CONFIG_DRCE_HOST)
    self.drcePort = configParser.get(className, self.CONFIG_DRCE_PORT)
    # self.drceManager = DRCEManager()
    # self.drceManager.activate_host(HostParams(self.drceHost, self.drcePort))
    self.drceIdGenerator = UIDGenerator()
    self.drceCommandConvertor = CommandConvertor()

    # Add connections to the polling set
    self.addConnection(self.serverName, serverConnection)

    # Max URLs per batch
    self.configVars[self.CONFIG_BATCH_MAX_URLS] = configParser.getint(className, self.CONFIG_BATCH_MAX_URLS)

    # Set crawler task app name
    self.configVars[self.CONFIG_DRCE_CRAWLER_APP_NAME] = configParser.get(className, self.CONFIG_DRCE_CRAWLER_APP_NAME)
    self.configVars[self.CONFIG_BATCH_MAX_TIME] = configParser.getint(className, self.CONFIG_BATCH_MAX_TIME)
    self.configVars[self.CONFIG_DRCE_STARTER_NAME] = configParser.get(className, self.CONFIG_DRCE_STARTER_NAME)
    self.configVars[self.CONFIG_MAX_THREADS] = configParser.getint(className, self.CONFIG_MAX_THREADS)
    if configParser.has_option(className, self.CONFIG_DRCE_REQUEST_ROUTING):
      self.configVars[self.CONFIG_DRCE_REQUEST_ROUTING] = configParser.getint(className,
                                                                              self.CONFIG_DRCE_REQUEST_ROUTING)
    else:
      self.configVars[self.CONFIG_DRCE_REQUEST_ROUTING] = self.CONFIG_DRCE_REQUEST_ROUTING_DEFAULT
    if configParser.has_option(className, self.CONFIG_BATCH_MAX_ITERATIONS):
      self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS] = configParser.getint(className,
                                                                              self.CONFIG_BATCH_MAX_ITERATIONS)
    else:
      self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS] = self.CONFIG_BATCH_MAX_ITERATIONS_DEFAULT

    # Batches counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TOTAL_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches that fault processing counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Batches urls total counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Fault batches urls total counter init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_FAULT_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Avg processing time init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TIME_AVG_NAME, 0, self.STAT_FIELDS_OPERATION_INIT)
    # Crawling batches real-time threads number init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, 0, self.STAT_FIELDS_OPERATION_SET)
    # Crawling batches real-time threads created total number init in stat vars
    self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_CREATED_COUNTER_NAME, 0, self.STAT_FIELDS_OPERATION_SET)

    # Total time of processing sum from all request
    self.totalTime = 0

    # Set connections poll timeout, defines period of HCE cluster monitoring cycle, msec
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_POLLING_TIMEOUT)


  # #Events wait timeout handler, for timeout state of the connections polling.
  # Executes update of workers threads stat counter
  #
  def on_poll_timeout(self):
    lock.acquire()
    # self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, threading.active_count(),
    #                     self.STAT_FIELDS_OPERATION_SET)
    # Correct the number of clients to fix some crashes
    # if self.statFields[DC_CONSTS.BATCHES_REALTIME_THREADS_NAME] > threading.active_count():
    #  self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, threading.active_count(),
    #                       self.STAT_FIELDS_OPERATION_SET)
    # Calc threads number
    n = 0
    main_thread = threading.currentThread()
    for t in threading.enumerate():
      if t is not main_thread and t.getName().startswith(self.REAL_TIME_CRAWL_THREAD_NAME_PREFIX):
        n += 1
    if self.statFields[DC_CONSTS.BATCHES_REALTIME_THREADS_NAME] > n:
      self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, n, self.STAT_FIELDS_OPERATION_SET)

    lock.release()



  # #onEventsHandler event handler
  #
  # @param event instance of Event object
  def onEventsHandler(self, event):
    self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TOTAL_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
    if isinstance(event.eventObj, EventObjects.Batch):
      if len(event.eventObj.items) > int(self.configVars[self.CONFIG_BATCH_MAX_URLS]):
        clientResponseObj = EventObjects.ClientResponse()
        clientResponseObj.errorCode = self.REQUEST_ERROR_URLS_COUNT
        clientResponseObj.errorMessage = "Wrong requested object type " + str(len(event.eventObj.items)) + \
                                         ", Batch expected."
      else:
        if self.configVars[self.CONFIG_MAX_THREADS] == 0:
          logger.info("Single thread processing started")
          # Process batch in single thread
          self.forkBatch(logging, event)
          return
        else:
          if self.configVars[self.CONFIG_MAX_THREADS] > 0:
            # if self.configVars[self.CONFIG_MAX_THREADS] > threading.active_count():
            if self.configVars[self.CONFIG_MAX_THREADS] > self.statFields[DC_CONSTS.BATCHES_REALTIME_THREADS_NAME]:
              # Process batch in separated thread
              logger.info("Forking new thread")
              self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_CREATED_COUNTER_NAME, 1,
                                   self.STAT_FIELDS_OPERATION_ADD)
              t1 = threading.Thread(target=self.forkBatch, args=(logging, event,))
              t1.setName(self.REAL_TIME_CRAWL_THREAD_NAME_PREFIX + \
                         str(self.statFields[DC_CONSTS.BATCHES_REALTIME_THREADS_CREATED_COUNTER_NAME]))
              t1.start()
              logger.info("New thread forked")
              # self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, threading.active_count(),
              #                     self.STAT_FIELDS_OPERATION_SET)
              return
            else:
              # Return overload error
              clientResponseObj = EventObjects.ClientResponse()
              clientResponseObj.errorCode = self.REQUEST_ERROR_THREADS_NUMBER_EXCEEDED
              lock.acquire()
              clientResponseObj.errorMessage = "Service overloaded, " + \
                                            str(self.statFields[DC_CONSTS.BATCHES_REALTIME_THREADS_NAME]) + " workers."
              logger.error(clientResponseObj.errorMessage)
              lock.release()
          else:
            # Return fake error
            clientResponseObj = EventObjects.ClientResponse()
            clientResponseObj.errorCode = self.REQUEST_ERROR_OBJECT_TYPE
            clientResponseObj.errorMessage = "STUB fake error response"
            logger.info(clientResponseObj.errorMessage)
    else:
      # Return error
      clientResponseObj = EventObjects.ClientResponse()
      clientResponseObj.errorCode = self.REQUEST_ERROR_OBJECT_TYPE
      clientResponseObj.errorMessage = "Wrong requested object type " + type(event.eventObj) + ", Batch expected."
      logger.error(clientResponseObj.errorMessage)

    # Send response with error to client
    self.sendClientResponse(event, clientResponseObj)

    # self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, threading.active_count(),
    #                     self.STAT_FIELDS_OPERATION_SET)



  # #forkBatch create thread, process batch request and return response to client application
  #
  # @param logging object instance
  # @param client request event
  # @return None if DRCE request execution okay or clientResponse object if some error happened
  # def forkBatch(self, event, loggerObj):
  def forkBatch(self, loggingObj, event):
    try:
      global logger  # pylint: disable=W0603
      lock.acquire()
      logger = loggingObj.getLogger(DC_CONSTS.LOGGER_NAME)
      self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
      lock.release()
      logger.info("THREAD_STARTED")
      logger.debug("event:\n%s", Utils.varDump(event))
      # Set start time
      t = time.time()
      # Set crawlerType to prevent wrong processing
      event.eventObj.crawlerType = EventObjects.Batch.TYPE_REAL_TIME_CRAWLER
      event.eventObj.dbMode = EventObjects.Batch.DB_MODE_R
      if event.eventObj.maxIterations > self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS]:
        event.eventObj.maxIterations = self.configVars[self.CONFIG_BATCH_MAX_ITERATIONS]
      # Prepare request
      lock.acquire()
      taskExecuteRequest = self.prepareDRCERequest(event.eventObj)
      lock.release()
      # Process send request
      clientResponseObj = self.processDRCERequest(taskExecuteRequest)
      logger.debug("ClientResponseObj object:\n" + Utils.varDump(clientResponseObj))
      lock.acquire()
      self.totalTime = self.totalTime + (time.time() - t)
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_TIME_AVG_NAME,
                           str(self.totalTime / float(1 + self.statFields[DC_CONSTS.BATCHES_CRAWL_COUNTER_TOTAL_NAME])),
                           self.STAT_FIELDS_OPERATION_SET)
      # Send response to client
      self.sendClientResponse(event, clientResponseObj)
      logger.info("THREAD_FINISHED")
      logger.debug("clientResponseObj:\n%s", Utils.varDump(clientResponseObj))
      lock.release()
    except Exception as err:
      msg = "Thread exception:" + str(err)
      lock.acquire()
      logger.error(msg)
      clientResponseObj = EventObjects.ClientResponse()
      clientResponseObj.errorCode = self.REQUEST_ERROR_OBJECT_TYPE
      clientResponseObj.errorMessage = msg
      self.sendClientResponse(event, clientResponseObj)
      lock.release()
    except:  # pylint: disable=W0702
      msg = "Unknown thread exception!"
      lock.acquire()
      logger.error(msg)
      clientResponseObj = EventObjects.ClientResponse()
      clientResponseObj.errorCode = self.REQUEST_ERROR_OBJECT_TYPE
      clientResponseObj.errorMessage = msg
      self.sendClientResponse(event, clientResponseObj)
      lock.release()
    # Decrement of counter of threads
    lock.acquire()
    self.updateStatField(DC_CONSTS.BATCHES_REALTIME_THREADS_NAME, 1, self.STAT_FIELDS_OPERATION_SUB)
    lock.release()



  # #sendClientResponse sends response to client by request event
  #
  # @param client request event
  # @return None if DRCE request execution okay or clientResponse object if some error happened
  def sendClientResponse(self, clientRequestEvent, clientResponseObj):
    # Prepare reply event
    replyEvent = self.eventBuilder.build(DC_CONSTS.EVENT_TYPES.BATCH_RESPONSE, clientResponseObj)
    # Send reply
    self.reply(clientRequestEvent, replyEvent)
    logger.info("Response to client sent")



  # #Prepare DRCE request
  #
  # @param eventType event type from Constants
  # @param eventObj instance of Event object
  # @return the TaskExecuteStruct object instance
  def prepareDRCERequest(self, eventObj):
    # Create DRCE task Id
    idGenerator = IDGenerator()
    taskId = ctypes.c_uint32(zlib.crc32(idGenerator.get_connection_uid(), int(time.time()))).value

    # Prepare DRCE request object
    taskExecuteStruct = TaskExecuteStruct()
    taskExecuteStruct.command = self.configVars[self.CONFIG_DRCE_CRAWLER_APP_NAME]
    if eventObj.id == 0:
      eventObj.id = taskId
    if eventObj.maxExecutionTime == 0:
      mt = self.configVars[self.CONFIG_BATCH_MAX_TIME]
    else:
      mt = eventObj.maxExecutionTime
      if int(mt) > int(self.configVars[self.CONFIG_DRCE_TIMEOUT] / 1000):
        mt = int(self.configVars[self.CONFIG_DRCE_TIMEOUT]) / 1000
    logger.debug("Custom max DRCE task execution set: %s", str(mt))
    taskExecuteStruct.input = pickle.dumps(eventObj)
    taskExecuteStruct.session = Session(Session.TMODE_SYNC, 0, int(mt) * 1000)
    taskExecuteStruct.session.shell = self.configVars[self.CONFIG_DRCE_STARTER_NAME]
    logger.debug("DRCE taskExecuteStruct:\n" + Utils.varDump(taskExecuteStruct))

    # Create DRCE TaskExecuteRequest object
    taskExecuteRequest = TaskExecuteRequest(taskId)
    # Set taskExecuteRequest fields
    taskExecuteRequest.data = taskExecuteStruct
    # Set route as resource-usage balancing if number of items in Batch is 1
    if len(eventObj.items) < 2:
      if self.configVars[self.CONFIG_DRCE_REQUEST_ROUTING] == 5:
        taskExecuteRequest.route = DC_CONSTS.DRCE_REQUEST_ROUTING_RESOURCE_USAGE
      if self.configVars[self.CONFIG_DRCE_REQUEST_ROUTING] == 1:
        taskExecuteRequest.route = DC_CONSTS.DRCE_REQUEST_ROUTING_ROUND_ROBIN
      if self.configVars[self.CONFIG_DRCE_REQUEST_ROUTING] == 0:
        taskExecuteRequest.route = DC_CONSTS.DRCE_REQUEST_ROUTING_MULTICAST
      if self.configVars[self.CONFIG_DRCE_REQUEST_ROUTING] == 4:
        taskExecuteRequest.route = DC_CONSTS.DRCE_REQUEST_ROUTING_RND

    logger.debug("DRCE taskExecuteRequest:\n" + Utils.varDump(taskExecuteRequest))

    return taskExecuteRequest



  # #Request action processor for DRCE DB cluster
  #
  # @param taskExecuteRequest object
  def processDRCERequest(self, taskExecuteRequest):

    logger.info("Sending sync task id:" + str(taskExecuteRequest.id) + " to DRCE router!")
    # Send request to DRCE Cluster router
    response = self.sendToDRCERouter(taskExecuteRequest)
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
      lock.acquire()
      self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
      lock.release()
    else:
      if len(response.items) == 0:
        clientResponse.errorCode = EventObjects.ClientResponse.STATUS_ERROR_EMPTY_LIST
        clientResponse.errorMessage = "Response error, empty list returned from DRCE, possible no one node in cluster!"
        logger.error(clientResponse.errorMessage)
        lock.acquire()
        self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
        lock.release()
      else:
        for item in response.items:
          # New ClientResponseItem object
          clientResponseItem = EventObjects.ClientResponseItem(None)
          # If some error in response item or cli application exit status
          if item.error_code > 0 or item.exit_status > 0:
            clientResponseItem.errorCode = clientResponseItem.STATUS_ERROR_DRCE
            clientResponseItem.errorMessage = "error_message=" + item.error_message + \
                                              ", error_code=" + str(item.error_code) + \
                                              ", exit_status=" + str(item.exit_status) + \
                                              ", stderror=" + str(item.stderror)
            logger.error(clientResponseItem.errorMessage)
            lock.acquire()
            self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
            lock.release()
          else:
            # Try to restore serialized response object from dump
            try:
              clientResponseItem.itemObject = pickle.loads(item.stdout)
              if clientResponseItem.itemObject is not None and isinstance(clientResponseItem.itemObject, list):
                urlContents = len(clientResponseItem.itemObject)
                lock.acquire()
                self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_NAME, urlContents,
                                     self.STAT_FIELDS_OPERATION_ADD)
                lock.release()
            except Exception as e:
              clientResponseItem.errorCode = EventObjects.ClientResponseItem.STATUS_ERROR_RESTORE_OBJECT
              clientResponseItem.errorMessage = EventObjects.ClientResponseItem.MSG_ERROR_RESTORE_OBJECT + "\n" + \
                                                str(e.message) + "\nstdout=" + str(item.stdout) + \
                                                ", stderror=" + str(item.stderror)
              logger.error(clientResponseItem.errorMessage)
              lock.acquire()
              self.updateStatField(DC_CONSTS.BATCHES_CRAWL_COUNTER_URLS_FAULT_NAME, 1, self.STAT_FIELDS_OPERATION_ADD)
              lock.release()
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
  # @return EEResponseData object instance
  def sendToDRCERouter(self, request):
    lock.acquire()
    drceManager = DRCEManager()
    drceManager.activate_host(HostParams(self.drceHost, self.drcePort))
    lock.release()

    logger.info("DRCE router sending with timeout=" + str(self.configVars[self.CONFIG_DRCE_TIMEOUT]) + \
                ", host:" + str(self.drceHost) + ", port:" + str(self.drcePort))
    # Try to execute request
    try:
      response = drceManager.process(request, self.configVars[self.CONFIG_DRCE_TIMEOUT], self.DRCE_REDUCER_TTL)
    except (ConnectionTimeout, TransportInternalErr, CommandExecutorErr) as err:
      response = None
      logger.error("DRCE router send error : " + str(err.message))

    logger.info("DRCE router sent!")

    lock.acquire()
    drceManager.clear_host()
    lock.release()

    return response

