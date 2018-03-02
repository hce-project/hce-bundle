'''
Created on Mar 25, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
'''

import logging
#import logging.config
import json
import sys
import ConfigParser
from cement.core import foundation
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
from dtm.Constants import EVENT_TYPES as EVENT_TYPES
from DTMAObjectsFiller import DTMAObjectsFiller
import transport.Consts
import dtm.EventObjects
import DTMAExceptions
import Constants as CONSTANTS
import app.Consts as APP_CONSTS
import app.Utils as Utils


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
#logger = logging.getLogger(CONSTANTS.APP_NAME)


##DTMA Class contents main functional of DTMA application, class inherits from foundation.CementApp
#
class DTMA(foundation.CementApp):

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
    self.dTMAObjectsFiller = DTMAObjectsFiller()
    self.errorCode = CONSTANTS.ERROR_NOERROR
    self.errorStr = ""


  ##fillError method
  #calls from error-code point from main processing (...from event handlers)
  def fillError(self, errorStr, errorCode):
    self.errorCode = errorCode
    self.errorStr = errorStr
    logger.error(self.errorStr)


  ##connectionInit method
  #initializes internal variables that containts network connections/communications
  def connectionInit(self):
    if self.connectionBuilder is None:
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


  ##generateEmptyResponse method
  #If here was some critical error, we generate empty response here , instead real response
  def generateEmptyResponse(self, task):
    ret = []
    obj = None
    if task is None:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[0]:
      obj = dtm.EventObjects.AdminStatData("")
    elif task == CONSTANTS.TASKS[1]:
      obj = dtm.EventObjects.AdminConfigVars("")
    elif task == CONSTANTS.TASKS[2]:
      obj = dtm.EventObjects.AdminConfigVars("")
    elif task == CONSTANTS.TASKS[3]:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[4]:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[5]:
      obj = dtm.EventObjects.GeneralResponse()
    elif task == CONSTANTS.TASKS[6]:
      obj = dtm.EventObjects.CustomResponse(None, None, None)

    obj.errorCode = self.errorCode
    obj.errorMessage = self.errorStr
    ret.append(obj)
    return json.dumps([ret], default=lambda o: o.__dict__, sort_keys=True, indent=4)


  ##configReader method
  #Method try to read config file by prereared paths, return count of readed configs
  def configReader(self):
    configReadList = []
    if self.pargs.config is None:
      configReadList = self.config.read(CONSTANTS.DEFAULT_CONFIG_NAME1)
      if len(configReadList) == 0:
        configReadList = self.config.read(CONSTANTS.DEFAULT_CONFIG_NAME2)
    else:
      configReadList = self.config.read(self.pargs.config)
    return len(configReadList)


  ##checkAdditionalArgs method
  #Method checks additions mandatory argument's present
  def checkAdditionalArgs(self, cmd):
    ret = True
    if cmd in CONSTANTS.TASKS[1:3]:
      if self.pargs.fields is None or self.pargs.classes is None:
        self.fillError(CONSTANTS.ERROR_STR2, CONSTANTS.ERROR_ARGS2)
        ret = False
    elif cmd == CONSTANTS.TASKS[0] or cmd == CONSTANTS.TASKS[3]:
      if self.pargs.classes is None:
        optionName = [CONSTANTS.SERVER_CONFIG_OPTION_NAME, CONSTANTS.SERVER_CONFIG_OPTION_NAME2]\
                     [cmd == CONSTANTS.TASKS[3]]
        try:
          self.pargs.classes = str(self.config.get(CONSTANTS.SERVER_CONFIG_SECTION_NAME, optionName))
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
          self.fillError(CONSTANTS.ERROR_STR3.format(CONSTANTS.SERVER_CONFIG_SECTION_NAME, optionName),
                         CONSTANTS.ERROR_CONFIG_SECTION)
          ret = False
    return ret


  ##taskProcessingDeserialize method
  #Method serializes incoming task to the JSON string
  def transportCommunications(self, cmd, requestObjects):
    responses = []
    retEvent = None
    eventType = None
    timeout = None
    responseTuple = []
    emptyResponse = None
    try:
      timeout = self.config.get(CONSTANTS.APP_NAME, CONSTANTS.TCP_TIMEOUT_CONFIG_NAME)
    except ConfigParser.NoSectionError:
      timeout = CONSTANTS.TCP_TIMEOUT
    except ConfigParser.NoOptionError:
      timeout = CONSTANTS.TCP_TIMEOUT

    for requestObject in requestObjects:
      if cmd == CONSTANTS.TASKS[0]:
        eventType = EVENT_TYPES.ADMIN_FETCH_STAT_DATA
        emptyResponse = dtm.EventObjects.AdminStatData(requestObject.className)
      elif cmd == CONSTANTS.TASKS[1]:
        eventType = EVENT_TYPES.ADMIN_SET_CONFIG_VARS
        emptyResponse = dtm.EventObjects.AdminConfigVars(requestObject.className)
      elif cmd == CONSTANTS.TASKS[2]:
        eventType = EVENT_TYPES.ADMIN_GET_CONFIG_VARS
        emptyResponse = dtm.EventObjects.AdminConfigVars(requestObject.className)
      elif cmd == CONSTANTS.TASKS[3]:
        eventType = EVENT_TYPES.ADMIN_STATE
        emptyResponse = dtm.EventObjects.GeneralResponse()
      elif cmd == CONSTANTS.TASKS[4]:
        eventType = EVENT_TYPES.ADMIN_SUSPEND
        emptyResponse = dtm.EventObjects.GeneralResponse()
      elif cmd == CONSTANTS.TASKS[5]:
        eventType = EVENT_TYPES.ADMIN_SYSTEM
        emptyResponse = dtm.EventObjects.GeneralResponse()
      elif cmd == CONSTANTS.TASKS[6]:
        eventType = EVENT_TYPES.ADMIN_SQL_CUSTOM
        emptyResponse = dtm.EventObjects.CustomResponse(None, None, None)

      event = self.eventBuilder.build(eventType, requestObject)
      self.localConnection.send(event)
      if self.localConnection.poll(timeout) == 0:
        responseTuple = [emptyResponse, CONSTANTS.ERROR_NETWORK]
      else:
        retEvent = self.localConnection.recv()
        responseTuple = [retEvent.eventObj, CONSTANTS.ERROR_NOERROR]
      responses.append(responseTuple)
    return responses


  ##load logging
  #load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    global logger  # pylint: disable=W0603
    try:
      logIniFileName = self.config.get(CONSTANTS.LOG_CONFIG_SECTION_NAME, CONSTANTS.LOG_CONFIG_OPTION_NAME)
      if logIniFileName != None:
        logging.config.fileConfig(logIniFileName, disable_existing_loggers=False)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
      self.errorStr = CONSTANTS.ERROR_STR8
      self.errorCode = CONSTANTS.ERROR_LOG_SECTION_ERROR
    except Exception, err:
      self.errorStr = CONSTANTS.ERROR_STR10 + ': ' + str(err)
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
    requestObjects = None
    jsonBuf = None
    if self.configReader() > 0:
      self.loadLogConfigFile()

      if self.errorCode == CONSTANTS.ERROR_NOERROR:
        try:
          self.connectionInit()
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
          self.fillError(CONSTANTS.ERROR_STR3, CONSTANTS.ERROR_CONFIG_SECTION)
        if not isHelpArg and self.pargs.cmd is None:
          self.fillError(CONSTANTS.ERROR_STR1, CONSTANTS.ERROR_ARGS1)
        elif self.pargs.cmd is not None and self.pargs.cmd in CONSTANTS.TASKS and \
        self.checkAdditionalArgs(self.pargs.cmd):
          try:
            requestObjects = self.dTMAObjectsFiller.generateObjectsList(self.pargs.cmd, self.pargs.fields,
                                                                        self.pargs.classes)
            responseObjects = self.transportCommunications(self.pargs.cmd, requestObjects)
            jsonBuf = json.dumps(responseObjects, default=lambda o: o.__dict__, sort_keys=True, indent=4)
          except (DTMAExceptions.DTMAEmptyFields, DTMAExceptions.DTMANameValueException):
            self.fillError(CONSTANTS.ERROR_STR4, CONSTANTS.ERROR_FIELDS_ARG)
          except DTMAExceptions.DTMAEmptyClasses:
            self.fillError(CONSTANTS.ERROR_STR5, CONSTANTS.ERROR_CLASSES_ARG)
    else:
      self.errorStr = CONSTANTS.ERROR_STR9
      self.errorCode = CONSTANTS.ERROR_NO_CONFIG

    if jsonBuf is None:
      jsonBuf = self.generateEmptyResponse(self.pargs.cmd)
    sys.stdout.write(jsonBuf)
    # Finish logging
    logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  ##close method
  #Method calls after application run
  def close(self):
    foundation.CementApp.close(self)
