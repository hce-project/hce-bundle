'''
Created on Feb 25, 2014

@author: igor, bgv
'''


import logging
import sys
import threading
import json
import os
import psutil

from datetime import datetime
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from app.PollerManager import PollerManager
from dtm.Constants import EVENT_TYPES  #@todo move the module in transport
from dtm.EventObjects import AdminState
from dtm.EventObjects import GeneralResponse
import dtm.Constants as DTM_CONSTS
from transport.Connection import ConnectionTimeout, TransportInternalErr
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
from transport.Response import Response
import transport.Consts as trasnport_consts


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


##This is app base class for management server connection end-points and parallel transport messages processing
#Provides main MOM transport for application architecture of parallel data processing
#
class BaseServerManager(threading.Thread):
  ADMIN_CONNECT_ENDPOINT = "Admin"
  ADMIN_CONNECT_CLIENT = "Admin"
  POLL_TIMEOUT_DEFAULT = 3000

  STAT_FIELDS_OPERATION_ADD = 0
  STAT_FIELDS_OPERATION_SUB = 1
  STAT_FIELDS_OPERATION_SET = 2
  STAT_FIELDS_OPERATION_INIT = 3

  POLL_TIMEOUT_CONFIG_VAR_NAME = "POLL_TIMEOUT"
  LOG_LEVEL_CONFIG_VAR_NAME = "LOG_LEVEL"

  STAT_DUMPS_DEFAULT_DIR = "/tmp/"
  STAT_DUMPS_DEFAULT_NAME = "%APP_NAME%_%CLASS_NAME%_stat_vars.dump"

  LOGGERS_NAMES = {APP_CONSTS.LOGGER_NAME, "dc", "dtm", "root", ""}

  ##constructor
  #
  def __init__(self, poller_manager=None, admin_connection=None, conectionLightBuilder=None, exceptionForward=False, \
               dumpStatVars=True):
    threading.Thread.__init__(self)

    logger.info("Thread-based class instance constructor begin!")

    self.dumpStatVars = dumpStatVars

    if poller_manager is None:
      self.poller_manager = PollerManager()
    else:
      self.poller_manager = poller_manager

    self.eventBuilder = EventBuilder()

    self.exit_flag = False
    self.pollTimeout = self.POLL_TIMEOUT_DEFAULT

    #map {"name":connection}
    self.connections = dict()
    #map {event_type:handler}
    self.event_handlers = dict()

    ##@var statFields
    #stat fields container
    self.statFields = dict()
    self.loadStatVarsDump()

    #Config fields container
    self.configVars = dict()

    #by default -add client admin connection
    conectLightBuilder = conectionLightBuilder
    admin_connect = admin_connection
    if conectLightBuilder is None:
      conectLightBuilder = ConnectionBuilderLight()
    if admin_connect is None:
      admin_connect = conectLightBuilder.build(trasnport_consts.CLIENT_CONNECT, self.ADMIN_CONNECT_ENDPOINT)

    self.addConnection(self.ADMIN_CONNECT_CLIENT, admin_connect)
    #Set event handler for ADMIN_STATE  event
    self.setEventHandler(EVENT_TYPES.ADMIN_STATE, self.onAdminState)
    self.setEventHandler(EVENT_TYPES.ADMIN_FETCH_STAT_DATA, self.onAdminFetchStatData)
    self.setEventHandler(EVENT_TYPES.ADMIN_GET_CONFIG_VARS, self.onAdminGetConfigVars)
    self.setEventHandler(EVENT_TYPES.ADMIN_SET_CONFIG_VARS, self.onAdminSetConfigVars)
    self.setEventHandler(EVENT_TYPES.ADMIN_SUSPEND, self.onAdminSuspend)
    self.sendAdminReadyEvent()
    #Set exception forwarding behavior, True - means forward exceptions farther, False - handle locally
    self.exceptionForward = exceptionForward
    #Init log level in config vars storage
    self.configVars[self.LOG_LEVEL_CONFIG_VAR_NAME] = self.getLogLevel()
    #Init start date in stat vars
    self.updateStatField(APP_CONSTS.START_DATE_NAME, datetime.now().__str__(), self.STAT_FIELDS_OPERATION_SET)
    logger.info("Thread-based class instance constructor end!")


  #@param name mane of connection
  #@param connection instance of Connection
  def addConnection(self, name, connection):
    self.initStatFields(name)
    self.connections[name] = connection


  ##set event handler
  #rewrite the current handler for eventType
  #
  #@param eventType type of processed events
  #@param handler handler to process events of eventType type
  def setEventHandler(self, eventType, handler):
    self.event_handlers[eventType] = handler


  ##send event
  #
  #@param connect_name of of a connection to which event will be send
  #@param event sending event
  def send(self, connect_name, event):
    try:
      logger.debug("Send to " + str(connect_name) + "\n" + self.createLogMsg(event))
      if self.is_connection_registered(connect_name):
        self.connections[connect_name].send(event)
        self.updateStatField(connect_name + "_send_cnt", 1)
        self.updateStatField(connect_name + "_send_bytes", sys.getsizeof(event))
      else:
        logger.error("Unregistered connection [" + str(connect_name) + "] network transport event!")
    except IOError as e:
      del e
    except EnvironmentError as e:
      del e
    except Exception, err:
      logger.error("Error `%s`", str(err))
    except:  # pylint: disable=W0702
      pass


  ##wrapper for sending event in reply for event
  #
  #@param event reason event
  #@param reply_evenr event sent in reply
  def reply(self, event, reply_event):
    reply_event.uid = event.uid
    reply_event.connect_identity = event.connect_identity
    reply_event.cookie = event.cookie
    self.send(event.connect_name, reply_event)


  ##poll function
  #polling connections
  #receive as multipart msg, the second argument is pickled pyobj
  def poll(self):
    connect_names = dict()
    timedout = False

    try:
      if self.POLL_TIMEOUT_CONFIG_VAR_NAME in self.configVars and \
         int(self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME]) > 0:
        timeout = int(self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME])
      else:
        timeout = self.pollTimeout
      #Try to poll all registered connections
      connect_names = self.poller_manager.poll(timeout)  # pylint: disable=R0204
    except ConnectionTimeout:
      timedout = True
    except TransportInternalErr as err:
      logger.error("ZMQ transport error: " + str(err.message))
    except IOError as e:
      del e
    except Exception as err:
      ExceptionLog.handler(logger, err, "Polling error:")

    if timedout is True:
      try:
        self.on_poll_timeout()
      except IOError as e:
        del e
      except EnvironmentError as e:
        del e
      except Exception as err:
        try:
          ExceptionLog.handler(logger, err, "Call of on_poll_timeout() error:")
        except IOError as e:
          del e
    else:
      #Read data from sockets of connections list returned
      for name in connect_names:
        try:
          if self.is_connection_registered(name):
            event = self.connections[name].recv()
            if isinstance(event, Response):
              #process data from Connection
              event = self.eventBuilder.build(EVENT_TYPES.SERVER_TCP_RAW, event)
            event.connect_name = name
            #Process received event
            self.process(event)
          else:
            logger.error("Unregistered connection [" + str(name) + "] network transport event!")
        except IOError as e:
          del e
        except EnvironmentError as e:
          del e
        except Exception as err:
          ExceptionLog.handler(logger, err, "Event processing error:")


  ##process event
  #call the event handler method that was set by user or on_unhandled_event method if not set
  #
  #@param event
  def process(self, event):
    try:
      try:
        logger.debug("Got " + self.createLogMsg(event))
      except IOError as e:
        del e

      self.updateStatField(event.connect_name + "_recv_cnt", 1)
      self.updateStatField(event.connect_name + "_recv_bytes", sys.getsizeof(event))
      if event.eventType in self.event_handlers:
        self.event_handlers[event.eventType](event)
      else:
        self.on_unhandled_event(event)
    except IOError as e:
      del e
    except EnvironmentError as e:
      del e


  def run(self):
    while not self.exit_flag:
      try:
        self.build_poller_list()
        self.poll()
        self.clear_poller()
      except IOError as e:
        del e
      except Exception, e:
        try:
          logger.error("Unhandled exception in thread-based class : " + str(e.message) + "\n" + \
                       Utils.getTracebackInfo())
          if self.exceptionForward:
            logger.error("Exception forwarded.")
            raise e
        except IOError as e:
          del e

    self.saveStatVarsDump()



  ##check is a connection was registered in a instance of BaseServerManager i
  #object
  #
  #@param name connection name
  #@return True is connection was registered, else - False
  def is_connection_registered(self, name):
    if name in self.connections:
      return True
    return False


  ##function will call every time when ConnectionTimeout exception arrive
  #
  def on_poll_timeout(self):
    pass


  ##function will call every time when arrive doesn't set handler for
  #event type of event.evenType
  #
  #@param event event which can't be processed
  def on_unhandled_event(self, event):
    logStr = "Got UNHANDLED EVENT\n" + self.createLogMsg(event)
    logger.debug(logStr)


  #common for all manager => in separate class
  def build_poller_list(self):
    for item in self.connections:
      self.poller_manager.add(self.connections[item], item)


  def clear_poller(self):
    for item in self.connections:
      self.poller_manager.remove(self.connections[item])


  ##onAdminState event handler
  #process admin SHUTDOWN command
  #
  #@param event instance of Event object
  def onAdminState(self, event):
    adminState = event.eventObj
    className = self.__class__.__name__
    response = AdminState(className, AdminState.STATE_SHUTDOWN)
    try:
      if adminState.command == AdminState.STATE_SHUTDOWN and adminState.className == className:
        logger.info("Has successfully shutdown!")
        self.exit_flag = True
      else:
        logger.error("Got unsupported admin command [" + str(adminState.command) + "] for " + str(adminState.className))
        response = AdminState(className, AdminState.STATE_ERROR)
    except IOError as e:
      del e

    responseEvent = self.eventBuilder.build(EVENT_TYPES.ADMIN_STATE_RESPONSE, response)
    self.reply(event, responseEvent)



  ##onAdminState event handler
  #process admin command
  #
  #@param event instance of Event object
  def onAdminFetchStatData(self, event):
    adminStatData = event.eventObj
    if adminStatData.className == self.__class__.__name__:
      adminStatData.fields = self.getStatDataFields(adminStatData.fields)
    else:
      err_msg = "Got wrong admin class name [" + adminStatData.className + "]"
      try:
        logger.error(err_msg + str(adminStatData.className))
      except IOError as e:
        del e

    responseEvent = self.eventBuilder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, adminStatData)
    self.reply(event, responseEvent)



  ##onAdminState event handler
  #process admin command
  #
  #@param event instance of Event object
  def onAdminSuspend(self, event):
    responseObj = GeneralResponse(GeneralResponse.ERROR_OK, (">>> Suspend Processed " + str(self.__class__.__name__)))

    try:
      logger.debug(">>> SUSPEND BASE processed class=" + str(self.__class__.__name__))
    except IOError as e:
      del e

    responseEvent = self.eventBuilder.build(EVENT_TYPES.ADMIN_SUSPEND_RESPONSE, responseObj)
    self.reply(event, responseEvent)


  ##getStatDataFields returns stat data from storage
  #
  #
  #@param fields list of requested fields names to get stat data, if empty or None - return all stat fields set
  def getStatDataFields(self, fields):
    if len(fields) == 0:
      fields = self.statFields
    else:
      for field_name in fields:
        if field_name in self.statFields:
          fields[field_name] = self.statFields[field_name]
    if isinstance(fields, dict):
      fields.update(self.getSystemStat())
    return fields


  ##getSystemStat returns stat data for system indicators: RAMV, RAMR and CPU
  #
  #
  #@return dict of stat fields
  def getSystemStat(self):
    fields = {'RAMV':0, 'RAMR':0, 'CPUU':0, 'CPUS':0, 'THREADS':0}
    try:
      py = psutil.Process(os.getpid())
      m = py.memory_info()
      fields['RAMV'] = m.vms
      fields['RAMR'] = m.rss
      c = py.cpu_times()
      fields['CPUU'] = c.user
      fields['CPUS'] = c.system
      fields['THREADS'] = py.num_threads()
    except Exception as e:
      del e

    return fields


  ##getConfigVarsFields returns config vars from storage
  #
  #
  #@param fields list of requested fields names to get config vars, if empty or None - return all fields set
  def getConfigVarsFields(self, fields):
    if len(fields) == 0 or "*" in fields:
      fields = self.configVars
    else:
      for field_name in fields:
        if field_name in self.configVars:
          fields[field_name] = self.configVars[field_name]

    return fields



  ##onAdminGetConfigVars event handler
  #process getConfigVars admin command, fill and return config vars array from internal storage
  #
  #@param event instance of Event object
  def onAdminGetConfigVars(self, event):
    getConfigVars = event.eventObj
    if getConfigVars.className == self.__class__.__name__:
      if len(getConfigVars.fields) > 0 and "*" not in getConfigVars.fields:
        for fieldName in getConfigVars.fields:
          if fieldName in self.configVars:
            getConfigVars.fields[fieldName] = self.configVars[fieldName]
          else:
            getConfigVars.fields[fieldName] = None
      else:
        getConfigVars.fields = self.configVars
    else:
      try:
        logger.error("Wrong admin class name [" + str(getConfigVars.className) + "]")
      except IOError as e:
        del e

    responseEvent = self.eventBuilder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE, getConfigVars)
    self.reply(event, responseEvent)



  ##onAdminSetConfigVars event handler
  #process setConfigVars admin command
  #
  #@param event instance of Event object
  def onAdminSetConfigVars(self, event):
    setConfigVars = event.eventObj
    responseEvent = self.eventBuilder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA_RESPONSE,
                                            self.setConfigVars(setConfigVars))
    self.reply(event, responseEvent)



  ##processSetConfigVars sets config vars in storage
  #
  #
  #@param setConfigVars instance of SetConfigVars object
  def setConfigVars(self, setConfigVars):
    if setConfigVars.className == self.__class__.__name__:
      for fieldName in setConfigVars.fields:
        if fieldName in self.configVars:
          if type(self.configVars[fieldName]) == type(setConfigVars.fields[fieldName]):  # pylint: disable=C0123
            self.configVars[fieldName] = setConfigVars.fields[fieldName]
            self.processSpecialConfigVars(fieldName, setConfigVars.fields[fieldName])
          else:
            setConfigVars.fields[fieldName] = None
        else:
          self.configVars[fieldName] = setConfigVars.fields[fieldName]
    else:
      try:
        logger.error("Wrong admin class name [" + str(setConfigVars.className) + "]")
      except IOError as e:
        del e

    return setConfigVars



  ##send ready event to notify adminInterfaceService
  #
  def sendAdminReadyEvent(self):
    className = self.__class__.__name__
    ready = AdminState(className, AdminState.STATE_READY)
    readyEvent = self.eventBuilder.build(EVENT_TYPES.ADMIN_STATE_RESPONSE, ready)
    self.send(self.ADMIN_CONNECT_CLIENT, readyEvent)



  ##from string message from event object
  #
  #@param event instance of Event object
  #@return log string
  def createLogMsg(self, event):
    logMsg = "event:\n" + str(vars(event)) + "\neventObj:\n"
    if event.eventObj and hasattr(event.eventObj, "__dict__"):
      logMsg = logMsg + str(vars(event.eventObj))
    else:
      logMsg = logMsg + str(event.eventObj)
    return logMsg



  ##add record in statFields
  #
  #@param connect_name mane of connection
  def initStatFields(self, connect_name):
    if connect_name + "_send_cnt" not in self.statFields:
      self.statFields[connect_name + "_send_cnt"] = 0
    if connect_name + "_recv_cnt" not in self.statFields:
      self.statFields[connect_name + "_recv_cnt"] = 0
    if connect_name + "_send_bytes" not in self.statFields:
      self.statFields[connect_name + "_send_bytes"] = 0
    if connect_name + "_recv_bytes" not in self.statFields:
      self.statFields[connect_name + "_recv_bytes"] = 0



  ##update values of stat field - default sum
  #
  #@param field_name name of updated field
  #@param value value to summarize
  def updateStatField(self, field_name, value, operation=STAT_FIELDS_OPERATION_ADD):
    if field_name in self.statFields:
      if operation == self.STAT_FIELDS_OPERATION_ADD:
        self.statFields[field_name] += int(value)
      elif operation == self.STAT_FIELDS_OPERATION_SUB:
        self.statFields[field_name] -= int(value)
      elif operation == self.STAT_FIELDS_OPERATION_SET:
        self.statFields[field_name] = value
    else:
      if operation == self.STAT_FIELDS_OPERATION_SET or operation == self.STAT_FIELDS_OPERATION_INIT:
        self.statFields[field_name] = value
      else:
        try:
          logger.error("Stat update: key is not valid " + field_name)
        except IOError as e:
          del e



  ##send ready event to notify adminInterfaceService
  #
  #@param name
  #@param value
  def processSpecialConfigVars(self, name, value):
    try:
      if name == self.LOG_LEVEL_CONFIG_VAR_NAME:
        #logger.setLevel(value)
        self.setLogLevel(value)
    except IOError as e:
      del e
    except Exception as err:
      try:
        ExceptionLog.handler(logger, err, "Exception:")
      except IOError as e:
        del e



  ##Get log level from first of existing loggers
  #
  #
  #@return log level
  def getLogLevel(self):
    level = None
    for name in logging.Logger.manager.loggerDict.keys():
      if isinstance(logging.Logger.manager.loggerDict[name], logging.Logger) and name in self.LOGGERS_NAMES:
        level = logging.Logger.manager.loggerDict[name].getEffectiveLevel()
        break
      else:
        pass

    return level



  ##Set log level for all loggers
  #
  #@param level of logging
  #@return log level
  def setLogLevel(self, level):
    for name in logging.Logger.manager.loggerDict.keys():
      if isinstance(logging.Logger.manager.loggerDict[name], logging.Logger) and name in self.LOGGERS_NAMES:
        logging.Logger.manager.loggerDict[name].setLevel(level)
    ll = logging.getLogger("")
    ll.setLevel(level)



  ##Save stat vars in json file
  #
  def saveStatVarsDump(self):
    if self.dumpStatVars:
      try:
        name = self.getStatVarsDumpFileName()
        with open(name, "w") as f:
          f.write(json.dumps(self.statFields, indent=4))
      except Exception as err:
        try:
          ExceptionLog.handler(logger, err, "Error save stat vars to file `" + name + "`: ")
        except IOError as e:
          del e



  ##Load stat vars in json file
  #
  def loadStatVarsDump(self):
    if self.dumpStatVars:
      try:
        name = self.getStatVarsDumpFileName()
        if os.path.exists(name):
          with open(name, 'r') as f:
            data = f.read()
            self.statFields = json.loads(str(data))
            #APP_CONSTS.START_DATE_NAME
            self.updateStatField(APP_CONSTS.START_DATE_NAME, datetime.now().__str__(), self.STAT_FIELDS_OPERATION_SET)
      except IOError as e:
        del e
      except Exception as err:
        try:
          ExceptionLog.handler(logger, err, "Error load stat vars from file `" + name + "`: ")
          logger.error(str(data))
        except IOError as e:
          del e



  ##Get stat vars file name
  #
  def getStatVarsDumpFileName(self):
    appName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    return self.STAT_DUMPS_DEFAULT_DIR + self.STAT_DUMPS_DEFAULT_NAME.replace("%APP_NAME%", appName).\
                                                                      replace("%CLASS_NAME%", self.__class__.__name__)


  # #create dict config (dict object)
  #
  def createDBIDict(self, configParser):
    # get section
    return dict(configParser.items(DTM_CONSTS.DB_CONFIG_SECTION))
