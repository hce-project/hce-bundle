'''
Created on Mar 19, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import logging
import logging.config
from DTMCObjectsSerializator import DTMCObjectsSerializator
from cement.core import foundation
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
from dtm.Constants import EVENT_TYPES as EVENT_TYPES
from app.Utils import JsonSerializable
import app.Exceptions as Exceptions
import transport.Consts
import dtm.EventObjects
import ConfigParser
import Constants as CONSTANTS
import json
import sys
import app.Utils as Utils
import app.Consts as APP_CONSTS
from app.Utils import ExceptionLog

# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
#logger = logging.getLogger(CONSTANTS.APP_NAME)


##DTMC Class contents main functional of DTMC application, class inherits from foundation.CementApp
#
class DTMC(foundation.CementApp):

  class Meta:  # pylint: disable=W0232, C1001
    label = CONSTANTS.APP_NAME


  ##constructor
  #initialise all class variable and recieve connectionBuilder as param(not mandatory)
  def __init__(self, connectionBuilder=None):
    foundation.CementApp.__init__(self)
    self.config = ConfigParser.ConfigParser()
    self.connectionBuilder = connectionBuilder
    self.localConnection = None
    self.eventBuilder = EventBuilder()
    self.dTMCObjectsSerializator = DTMCObjectsSerializator()
    self.errorCode = CONSTANTS.ERROR_NOERROR
    self.errorStr = ""


  ##fillError method
  #calls from error-code point from main processing (...from event handlers)
  #errorStr - external errorMessage
  #errorCode - external errorCode
  def fillError(self, errorStr, errorCode, isLogging=True):
    self.errorCode = errorCode
    self.errorStr = errorStr
    if isLogging:
      logger.error(self.errorStr)


  ##connectionInit method
  #initializes internal variables that containts network connections/communications
  def connectionInit(self):
    if self.connectionBuilder == None:
      self.connectionBuilder = ConnectionBuilderLight()
    host = str(self.config.get(CONSTANTS.APP_NAME, CONSTANTS.DTM_HOST))
    if len(host) > 1 and host[0] == "\"":
      host = host[1:]
    if host[-1] == "\"":
      host = host[0:-1]
    port = str(self.config.get(CONSTANTS.APP_NAME, CONSTANTS.DTM_PORT))
    addr = host + ":" + port
    self.localConnection = self.connectionBuilder.build(transport.Consts.CLIENT_CONNECT, addr,
                          transport.Consts.TCP_TYPE)


  ##taskProcessingDeserialize method
  #Reads task from file and deserializes it.
  #task - task arg
  #fileName - json filename
  #task_id - task id, seeetd by args
  def taskProcessingDeserialize(self, task, fileName, task_id):
    ffile = open(fileName, "r")
    data = ffile.read()
    ffile.close()
    jsonData = json.loads(data)
    self.dTMCObjectsSerializator = DTMCObjectsSerializator()
    eventObj = None
    if task == CONSTANTS.TASKS[0]:
      eventObj = self.dTMCObjectsSerializator.newDeserialize(jsonData)
      if task_id != None:
        eventObj.id = task_id
    elif task == CONSTANTS.TASKS[1]:
      eventObj = self.dTMCObjectsSerializator.checkDeserialize(jsonData)
    elif task == CONSTANTS.TASKS[2]:
      eventObj = self.dTMCObjectsSerializator.terminateDeserialize(jsonData)
    elif task == CONSTANTS.TASKS[3]:
      eventObj = self.dTMCObjectsSerializator.getDeserialize(jsonData)
    elif task == CONSTANTS.TASKS[4]:
      eventObj = self.dTMCObjectsSerializator.statusDeserialize(jsonData)
    elif task == CONSTANTS.TASKS[5]:
      eventObj = self.dTMCObjectsSerializator.cleanupDeserialize(jsonData)
    elif task == CONSTANTS.TASKS[6]:
      eventObj = self.dTMCObjectsSerializator.getTasksDeserialize(jsonData)
    return eventObj


  ##generateEmptyResponse method
  #If here was some critical error, we generate empty response here , instead real response
  #task - task arg
  def generateEmptyResponse(self, task):
    obj = None
    jsonString = None
    if task == None:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[0]:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[1]:
      obj = dtm.EventObjects.EEResponseData(0)
    elif task == CONSTANTS.TASKS[2]:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[3]:
      obj = dtm.EventObjects.EEResponseData(0)
    elif task == CONSTANTS.TASKS[4]:
      obj = []
    elif task == CONSTANTS.TASKS[5]:
      obj = dtm.EventObjects.GeneralResponse(0)
    elif task == CONSTANTS.TASKS[6]:
      obj = dtm.EventObjects.AvailableTaskIds([])
    else:
      obj = dtm.EventObjects.GeneralResponse()
      self.errorCode = CONSTANTS.ERROR_UNKNOWN_TASK
      self.errorStr = CONSTANTS.ERROR_STR14
    if type(obj) == type([]):
      jsonString = json.dumps(obj)
    else:
      obj.errorCode = self.errorCode
      obj.errorMessage = self.errorStr
      jsonString = obj.toJSON()
    return jsonString


  ##taskProcessingDeserialize method
  #Method serializes incoming task to the JSON string
  #task - task arg
  #eventObj - response event object
  def taskProcessingSerialize(self, task, eventObj):
    jsonString = None
    eventObjClassName = eventObj.__class__.__name__
    if task == CONSTANTS.TASKS[0]:
      if eventObjClassName != dtm.EventObjects.GeneralResponse().__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "GeneralResponse"))
    elif task == CONSTANTS.TASKS[1]:
      if eventObjClassName != dtm.EventObjects.EEResponseData(0).__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "EEResponseData"))
    elif task == CONSTANTS.TASKS[2]:
      if eventObjClassName != dtm.EventObjects.GeneralResponse().__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "GeneralResponse"))
    elif task == CONSTANTS.TASKS[3]:
      if eventObjClassName != dtm.EventObjects.EEResponseData(0).__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "EEResponseData"))
    elif task == CONSTANTS.TASKS[4]:
      if eventObjClassName != [].__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "list[]"))
      i = 0
      for listElement in eventObj:
        i += 1
        eventObjClassName = listElement.__class__.__name__
        #TODO: replace with isinstance() usage
        if eventObjClassName != dtm.EventObjects.TaskManagerFields(0).__class__.__name__:
          raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task,
                              "list(TaskManagerFields)[" + str(i) + "]"))
    elif task == CONSTANTS.TASKS[5]:
      if eventObjClassName != dtm.EventObjects.GeneralResponse().__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "GeneralResponse"))
    elif task == CONSTANTS.TASKS[6]:
      if eventObjClassName != dtm.EventObjects.AvailableTaskIds(0).__class__.__name__:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(task, "AvailableTaskIds"))
    if type(eventObj) == type([]):
      jsonString = json.dumps(eventObj, default=JsonSerializable.json_serial, sort_keys=True, indent=4)
    else:
      try:
        jsonString = eventObj.toJSON()
      except UnicodeDecodeError, err:
        ExceptionLog.handler(logger, err, "<-------------- DECODE Error ---------------->", (eventObj))

    return jsonString


  ##taskProcessingDeserialize method
  #Method serializes incoming task to the JSON string
  #task - task arg
  #eventObj - response event object
  def transportCommunications(self, task, eventObj):
    timeout = None
    retEvent = None
    ret = None
    try:
      timeout = self.config.get(CONSTANTS.APP_NAME, CONSTANTS.TCP_TIMEOUT_CONFIG_NAME)
    except ConfigParser.NoSectionError:
      timeout = CONSTANTS.TCP_TIMEOUT
    except ConfigParser.NoOptionError:
      timeout = CONSTANTS.TCP_TIMEOUT
    eventType = None
    if task == CONSTANTS.TASKS[0]:
      eventType = EVENT_TYPES.NEW_TASK
    elif task == CONSTANTS.TASKS[1]:
      eventType = EVENT_TYPES.CHECK_TASK_STATE
    elif task == CONSTANTS.TASKS[2]:
      eventType = EVENT_TYPES.DELETE_TASK
    elif task == CONSTANTS.TASKS[3]:
      eventType = EVENT_TYPES.FETCH_TASK_RESULTS
    elif task == CONSTANTS.TASKS[4]:
      eventType = EVENT_TYPES.GET_TASK_STATUS
    elif task == CONSTANTS.TASKS[5]:
      eventType = EVENT_TYPES.DELETE_TASK_RESULTS
    elif task == CONSTANTS.TASKS[6]:
      eventType = EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS
    event = self.eventBuilder.build(eventType, eventObj)
    self.localConnection.send(event)

    if self.localConnection.poll(timeout) == 0:
      self.fillError(CONSTANTS.ERROR_STR7.format(str(timeout)), CONSTANTS.ERROR_NETWORK)
    else:
      retEvent = self.localConnection.recv()
    if retEvent != None:
      ret = retEvent.eventObj
    return ret


  ##configReader method
  #Method try to read config file by prereared paths, return count of readed configs
  def configReader(self):
    configReadList = []
    if self.pargs.config == None:
      configReadList = self.config.read(CONSTANTS.DEFAULT_CONFIG_NAME1)
      if len(configReadList) == 0:
        configReadList = self.config.read(CONSTANTS.DEFAULT_CONFIG_NAME2)
    else:
      configReadList = self.config.read(self.pargs.config)
    return len(configReadList)


  ##load logging
  #load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    global logger  # pylint: disable=W0603
    try:
      logIniFileName = self.config.get(CONSTANTS.LOG_CONFIG_SECTION_NAME, CONSTANTS.LOG_CONFIG_OPTION_NAME)
      if logIniFileName != None:
        logging.config.fileConfig(logIniFileName)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
      self.errorStr = CONSTANTS.ERROR_STR10
      self.errorCode = CONSTANTS.ERROR_LOG_SECTION_ERROR
    except Exception, err:
      self.errorStr = CONSTANTS.ERROR_STR11 + ': ' + str(err)
      self.errorCode = CONSTANTS.ERROR_LOG_INIT
    logger = Utils.MPLogger().getLogger()


  ##setup method
  #Method calls before run application
  def setup(self):
    foundation.CementApp.setup(self)


  ##run method
  #Method contains main application functionality
  def run(self):
    foundation.CementApp.run(self)
    isHelpArg = False
    if '-h' in self.argv or '--help' in self.argv:
      isHelpArg = True
    eventObj = None
    retEventObj = None
    jsonBuf = None

    if self.configReader() > 0:
      self.loadLogConfigFile()

      if self.errorCode == CONSTANTS.ERROR_NOERROR:
        try:
          self.connectionInit()
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
          self.fillError(CONSTANTS.ERROR_STR13, CONSTANTS.ERROR_CONFIG_SECTION)
        except Exception:
          self.fillError(CONSTANTS.ERROR_STR12, CONSTANTS.ERROR_CONNECTION)
        else:
          if self.localConnection != None:
            if isHelpArg == False and self.pargs.task == None:
              self.fillError(CONSTANTS.ERROR_STR1, CONSTANTS.ERROR_ARGS1)
            elif self.pargs.task != None:
              if self.pargs.task in CONSTANTS.TASKS:
                if self.pargs.file != None:
                  try:
                    eventObj = self.taskProcessingDeserialize(self.pargs.task, self.pargs.file, self.pargs.id)
                  except IOError:
                    self.fillError(CONSTANTS.ERROR_STR4, CONSTANTS.ERROR_BAD_FILE_NAME)
                  except ValueError:
                    self.fillError(CONSTANTS.ERROR_STR5, CONSTANTS.ERROR_BAD_JSON)
                  except Exceptions.DeserilizeException as excp:
                    self.fillError(CONSTANTS.ERROR_STR6.format(excp.message), CONSTANTS.ERROR_DTMC)
                  if eventObj != None:
                    retEventObj = self.transportCommunications(self.pargs.task, eventObj)
                    if retEventObj != None:
                      try:
                        jsonBuf = self.taskProcessingSerialize(self.pargs.task, retEventObj)
                      except Exceptions.WrongEventObjectTypeException as excp:
                        self.fillError(excp.message, CONSTANTS.ERROR_WRONG_RESPONSE)
                else:
                  self.fillError(CONSTANTS.ERROR_STR2, CONSTANTS.ERROR_ARGS2)
              else:
                self.fillError(CONSTANTS.ERROR_STR3, CONSTANTS.ERROR_BAD_TASK)
          else:
            self.fillError(CONSTANTS.ERROR_STR12, CONSTANTS.ERROR_CONNECTION)
    else:
      self.fillError(CONSTANTS.ERROR_STR9, CONSTANTS.ERROR_NO_CONFIG, False)

    if jsonBuf == None:
      jsonBuf = self.generateEmptyResponse(self.pargs.task)
    sys.stdout.write(jsonBuf)
    # Finish logging
    logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  ##close method
  #Method calls after application run
  def close(self):
    foundation.CementApp.close(self)


