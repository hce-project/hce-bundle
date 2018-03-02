'''
Created on Mar 05, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

try:
  import cPickle as pickle
except ImportError:
  import pickle

import ConfigParser
import logging

import transport.Consts
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
from app.BaseServerManager import BaseServerManager
from app.LogFormatter import LogFormatterEvent
from dbi.dbi import DBI
from dbi.dbi import DBIErr
from dtm.Constants import EVENT_TYPES as EVENT
from dtm.EEResponsesTable import EEResponsesTable
from dtm.EventObjects import GeneralResponse
from dtm.TasksDataTable import TasksDataTable
import dtm.Constants as CONSTANTS

logger = logging.getLogger(CONSTANTS.LOGGER_NAME)

##Class contents TasksDataManager module implementation
#
class TasksDataManager(BaseServerManager):


  TASK_DATA_MANAGER_SERV_NAME = "Server"
  TASK_DATA_MANAGER_SERV_CONFIG_NAME = "ServerName"


  ##constructor
  #initialise all class variable and recieve config as param
  def __init__(self, config, connectionBuilder=None):
    try:
      BaseServerManager.__init__(self)
      self.moduleName = self.__class__.__name__
      self.servIndex = 1
      self.eventBuilder = EventBuilder()
      self.setEventHandler(EVENT.NEW_TASK, self.onNewTask)
      self.setEventHandler(EVENT.FETCH_TASK_DATA, self.onFetchTask)
      self.setEventHandler(EVENT.UPDATE_TASK, self.onUpdateTask)
      self.setEventHandler(EVENT.DELETE_TASK_DATA, self.onDeleteTask)
      self.setEventHandler(EVENT.INSERT_EE_DATA, self.onInsertEEResponse)
      self.setEventHandler(EVENT.FETCH_EE_DATA, self.onFetchEEResponse)
      self.setEventHandler(EVENT.DELETE_EE_DATA, self.onDeleteEEResponse)
      self.connectionBuilder = connectionBuilder
      self.config = config
      self.dbi = None
      self.connectionInit()
      self.dbInit()
    except Exception, err:
      logger.error("__init__ failed. Error: %s", str(err))
    except:
      logger.error("__init__ failed. Unknown error.")

    logger.debug('__init__ finished!')


  ##connectionInit method
  #initializes internal inproc connection
  def connectionInit(self):
    try:
      if self.connectionBuilder is None:
        self.connectionBuilder = ConnectionBuilderLight()

      localConnection = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT, \
                        self.config.get(self.moduleName, self.TASK_DATA_MANAGER_SERV_CONFIG_NAME))
      self.addConnection(self.TASK_DATA_MANAGER_SERV_NAME + str(self.servIndex), localConnection)
      self.servIndex = self.servIndex + 1
    except ConfigParser.NoSectionError:
      logger.error(">>> TasksDataManager can't read config - Section Error")
    except ConfigParser.NoOptionError:
      logger.error(">>> TasksDataManager can't read config - Option Error")
    except Exception, err:
      logger.error("connectionInit failed. Error: %s", str(err))
    except:
      logger.error('Unknown error.')


  ##dbInit method
  #initializes internal database API
  def dbInit(self):
    if self.config != None:
      dic = None
      dic = dict(self.config.items(CONSTANTS.DB_CONFIG_SECTION))
      if dic != None:
        self.dbi = DBI(dic)


  ##dbiProcessing method
  #Method contains main processing with database API
  def dbiProcessing(self, data, eventType):
    # variable for result
    ret = None

    if eventType == EVENT.NEW_TASK:
      self.dbi.insert(data)
    elif eventType == EVENT.FETCH_TASK_DATA:
      ret = self.dbi.fetch(data, "id=%s" % data.id)
    elif eventType == EVENT.UPDATE_TASK:
      self.dbi.update(data, "id=%s" % data.id)
    elif eventType == EVENT.DELETE_TASK_DATA:
      self.dbi.delete(data, "id=%s" % data.id)
    elif eventType == EVENT.INSERT_EE_DATA:
      self.dbi.insert(data)
    elif eventType == EVENT.FETCH_EE_DATA:
      ret = self.dbi.fetch(data, "id=%s" % data.id)
    elif eventType == EVENT.DELETE_EE_DATA:
      self.dbi.delete(data, "id=%s" % data.id)

    return ret


  ## Get responce event type method
  #
  #@param eventType - event type
  #@return responce event type
  def getResponceEventType(self, eventType):
    #variable for result
    retEventType = EVENT.GENERAL_RESPONSE

    if eventType == EVENT.NEW_TASK:
      retEventType = EVENT.NEW_TASK_RESPONSE
    elif eventType == EVENT.FETCH_TASK_DATA:
      retEventType = EVENT.FETCH_TASK_DATA_RESPONSE
    elif eventType == EVENT.UPDATE_TASK:
      retEventType = EVENT.UPDATE_TASK_RESPONSE
    elif eventType == EVENT.DELETE_TASK_DATA:
      retEventType = EVENT.DELETE_TASK_DATA_RESPONSE
    elif eventType == EVENT.INSERT_EE_DATA:
      retEventType = EVENT.INSERT_EE_DATA_RESPONSE
    elif eventType == EVENT.FETCH_EE_DATA:
      retEventType = EVENT.FETCH_EE_DATA_RESPONSE
    elif eventType == EVENT.DELETE_EE_DATA:
      retEventType = EVENT.DELETE_EE_DATA_RESPONSE

    return retEventType


  ##eventProcessing method
  #Method contains main processing with incoming events
  def eventProcessing(self, event):
    try:
      serializeStr = pickle.dumps(event.eventObj)
      if event.eventType == EVENT.NEW_TASK or \
         event.eventType == EVENT.FETCH_TASK_DATA or \
         event.eventType == EVENT.UPDATE_TASK or \
         event.eventType == EVENT.DELETE_TASK_DATA:
        data = TasksDataTable()
      else:
        data = EEResponsesTable()
      data.id = event.eventObj.id
      data.data = serializeStr
      dbiRet = None
      retEventType = None

      retEventType = self.getResponceEventType(event.eventType)
      dbiRet = GeneralResponse()
      res = self.dbiProcessing(data, event.eventType)
      if res is not None and len(res) > 0 and res[0] != None and hasattr(res[0], 'data') and res[0].data != None:
        dbiRet = pickle.loads(str(res[0].data))

    except DBIErr as err:
      logger.error("DB error: %s", str(err))
      dbiRet.errorCode = err.errCode
      dbiRet.errorMessage = "Some DB error in TasksDataManager.eventProcessing [" + str(err) + "]"
    except Exception, err:
      logger.error("Error: %s", str(err))
      dbiRet.errorMessage = "Some error in TasksDataManager.eventProcessing [" + str(err) + "]"
    except:
      logger.error("Error: Unknown error.")
      dbiRet.errorMessage = "Some error in TasksDataManager.eventProcessing ['Unknown error']"

    retEvent = self.eventBuilder.build(retEventType, dbiRet)
    return retEvent


  ##eventProcessing method
  #Method contains main error processing for incoming events
  def badEventType(self, msg, event):
    errorStr = msg + str(event.eventType)
    logger.error(LogFormatterEvent(event, [], errorStr))
#    raise Exception(errorStr)


  ##Callbacks methods
  #Event callbacks
  def onNewTask(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [NEW_TASK_REQUEST] Handler start"))
      if event.eventType != EVENT.NEW_TASK:
        self.badEventType(">>> Wrong Event type [NEW_TASK_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [NEW_TASK_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))


  def onFetchTask(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [FETCH_TASK_REQUEST] Handler start"))
      if event.eventType != EVENT.FETCH_TASK_DATA:
        self.badEventType(">>> Wrong Event type [FETCH_TASK_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [FETCH_TASK_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))


  def onUpdateTask(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [UPDATE_TASK_REQUEST] Handler start"))
      if event.eventType != EVENT.UPDATE_TASK:
        self.badEventType(">>> Wrong Event type [UPDATE_TASK_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [UPDATE_TASK_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))


  def onDeleteTask(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [DELETE_TASK_DATA_REQUEST] Handler start"))
      if event.eventType != EVENT.DELETE_TASK_DATA:
        self.badEventType(">>> Wrong Event type [DELETE_TASK_DATA_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [DELETE_TASK_DATA_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))


  def onInsertEEResponse(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [INSERT_EE_REQUEST] Handler start"))
      if event.eventType != EVENT.INSERT_EE_DATA:
        self.badEventType(">>> Wrong Event type [INSERT_EE_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [INSERT_EE_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))


  def onFetchEEResponse(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [FETCH_EE_REQUEST] Handler start"))
      if event.eventType != EVENT.FETCH_EE_DATA:
        self.badEventType(">>> Wrong Event type [FETCH_EE_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [FETCH_EE_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))


  def onDeleteEEResponse(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [DELETE_EE_REQUEST] Handler start"))
      if event.eventType != EVENT.DELETE_EE_DATA:
        self.badEventType(">>> Wrong Event type [DELETE_EE_REQUEST] != ", event)
      self.reply(event, self.eventProcessing(event))
      logger.debug(LogFormatterEvent(event, [], ">>> TasksDataManager [DELETE_EE_REQUEST] Handler finish"))
    except Exception, err:
      logger.error(str(err))
