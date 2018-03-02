'''
Created on Mar 13, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
from app.BaseServerManager import BaseServerManager
from dbi.dbi import DBI
from dbi.dbi import DBIErr
from Constants import EVENT_TYPES as EVENT
from EventObjects import GeneralResponse
from app.LogFormatter import LogFormatterEvent
from ResourcesTable import ResourcesTable
from ResourcesRecalculating import ResourcesRecalculating
import transport.Consts
import ConfigParser
import logging
import Constants as CONSTANTS

logger = logging.getLogger(CONSTANTS.LOGGER_NAME)


##Class contents ResourcesManager module implementation
#
class ResourcesManager(BaseServerManager):

  RESOURCE_MANAGER_SERV_NAME = "Server"
  RESOURCE_MANAGER_SERV_CONFIG_NAME = "ServerName"


  ##constructor
  #initialise all class variable and recieve config as param
  def __init__(self, config, connectionBuilder=None):
    BaseServerManager.__init__(self)
    self.moduleName = self.__class__.__name__
    self.servIndex = 1
    self.eventBuilder = EventBuilder()
    self.setEventHandler(EVENT.UPDATE_RESOURCES_DATA, self.onUpdateResourcesData)
    self.setEventHandler(EVENT.GET_AVG_RESOURCES, self.onGetAVGResources)
    self.connectionBuilder = connectionBuilder
    self.config = config
    self.dbi = None
    self.connectionInit()
    self.dbInit()
    self.resourcesRecalculating = ResourcesRecalculating()


  ##connectionInit method
  #initializes internal inproc connection
  def connectionInit(self):
    try:
      if self.connectionBuilder == None:
        self.connectionBuilder = ConnectionBuilderLight()

      localConnection = self.connectionBuilder.build(transport.Consts.SERVER_CONNECT, \
                        self.config.get(self.moduleName, self.RESOURCE_MANAGER_SERV_CONFIG_NAME))
      self.addConnection(self.RESOURCE_MANAGER_SERV_NAME + str(self.servIndex), localConnection)
      self.servIndex = self.servIndex + 1
    except ConfigParser.NoSectionError:
      logger.error(">>> ResourcesManager can't read config - Section Error")
    except ConfigParser.NoOptionError:
      logger.error(">>> ResourcesManager can't read config - Option Error")
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##dbInit method
  #initializes internal database API
  def dbInit(self):
    if self.config != None:
      dic = None
      dic = dict(self.config.items(CONSTANTS.DB_CONFIG_SECTION))
      if dic != None:
        self.dbi = DBI(dic)


  ##eventProcessing method
  #Method contains main error processing for incoming events
  #msg - incomig error message
  #event - incoming event
  def badEventType(self, msg, event):
    errorStr = msg + str(event.eventType)
    logger.error(LogFormatterEvent(event, [], errorStr))
#    raise Exception(errorStr)


  ##onUpdateResourcesData event handler method
  #Processing UPDATE_RESOURCES_DATA incoming request
  #event - incoming event
  def onUpdateResourcesData(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> ResourcesManager [UPDATE_RESOURCES_DATA] Handler start"))
      if event.eventType != EVENT.UPDATE_RESOURCES_DATA:
        self.badEventType(">>> Wrong Event type [UPDATE_RESOURCES_DATA] != ", event)
      response = GeneralResponse()
      wasUpdate = False
      for updateItem in event.eventObj:
        data = ResourcesTable(updateItem)
        try:
          self.dbi.insertOnUpdate(data, "id=%s" % data.nodeId)
        except DBIErr as ex:
          response.statuses.append(False)
          errorStr = ">>> Some DBI error in ResourcesManager.onUpdateResourcesData [" + str(ex) + "]"
          logger.error(LogFormatterEvent(event, [], errorStr))
        else:
          self.resourcesRecalculating.addUpdateResources(data)
          wasUpdate = True
          response.statuses.append(True)
      if wasUpdate:
        self.resourcesRecalculating.recalculate()
      retEventType = EVENT.UPDATE_RESOURCES_DATA_RESPONSE
      retEvent = self.eventBuilder.build(retEventType, response)
      self.reply(event, retEvent)
      logger.debug(LogFormatterEvent(event, [], ">>> ResourcesManager [UPDATE_RESOURCES_DATA] Handler finish"))
    except Exception, err:
      logger.error("Exception: %s", str(err))


  ##onGetAVGResources event handler method
  #Processing GET_AVG_RESOURCES incoming request
  #event - incoming event
  def onGetAVGResources(self, event):
    try:
      logger.debug(LogFormatterEvent(event, [], ">>> ResourcesManager [GET_AVG_RESOURCES] Handler start"))
      if event.eventType != EVENT.GET_AVG_RESOURCES:
        self.badEventType(">>> Wrong Event type [GET_AVG_RESOURCES] != ", event)
      resourcesAVG = self.resourcesRecalculating.getResourcesAVG()
      retEventType = EVENT.GET_AVG_RESOURCES_RESPONSE
      retEvent = self.eventBuilder.build(retEventType, resourcesAVG)
      self.reply(event, retEvent)
      logger.debug(LogFormatterEvent(event, [], ">>> ResourcesManager [GET_AVG_RESOURCES] Handler finish"))
    except Exception, err:
      logger.error("Exception: %s", str(err))
