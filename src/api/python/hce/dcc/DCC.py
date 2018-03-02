'''
Created on Apr 10, 2014

@package: dc
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import ConfigParser
import logging
import logging.config
import json
import sys
import time
from cement.core import foundation
import transport.Consts
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
import dc.EventObjects
from dc.Constants import EVENT_TYPES as EVENT_TYPES
import app.Consts as APP_CONSTS
import app.Utils as Utils  # pylint: disable=F0401
import app.Exceptions as Exceptions
from app.Utils import ExceptionLog
from app.Utils import varDump
import dcc.Constants as CONSTANTS
from dcc.DCCObjectsSerializator import DCCObjectsSerializator


# #DCC Class contents main functional of DCC application, class inherits from foundation.CementApp
#
class DCC(foundation.CementApp):

  # # Constants error messages used in class
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."

  ERROR_FILE_ERROR_MESSAGE_FIELD_NAME = 'errorMessage'
  ERROR_FILE_ERROR_CODE_FIELD_NAME = 'errorCode'

  class Meta:  # pylint: disable=W0232, C1001
    label = CONSTANTS.APP_NAME

  # #constructor
  # initialise all class variable and recieve connectionBuilder as param(not mandatory)
  def __init__(self, connectionBuilder=None):
    foundation.CementApp.__init__(self)
    # self.config = ConfigParser.ConfigParser()
    self.connectionBuilder = connectionBuilder
    self.localConnection = None
    self.eventBuilder = EventBuilder()
    self.errorCode = CONSTANTS.ERROR_NOERROR
    self.errorStr = ""
    self.sendEventType = None
    self.sendEventObject = None
    self.logger = None


  # #load application config file
  #
  # @param configName - name of application config file
  # @return - profiler config file name
  def __loadAppConfig(self, configName):
    # variable for result
    confLogFileName = ""
    timeout = CONSTANTS.TCP_TIMEOUT
    host = ''
    port = ''
    outputFileName = None
    errorFileName = None

    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        confLogFileName = str(config.get(CONSTANTS.LOG_CONFIG_SECTION_NAME, CONSTANTS.LOG_CONFIG_OPTION_NAME))

      if config.has_section(CONSTANTS.APP_NAME):
        timeout = config.get(CONSTANTS.APP_NAME, CONSTANTS.TCP_TIMEOUT_CONFIG_NAME)
        host = str(config.get(CONSTANTS.APP_NAME, CONSTANTS.DTM_HOST))
        port = str(config.get(CONSTANTS.APP_NAME, CONSTANTS.DTM_PORT))

      if hasattr(self.pargs, 'dcc_timeout') and self.pargs.dcc_timeout != None and \
      self.pargs.dcc_timeout.isdigit():
        timeout = int(self.pargs.dcc_timeout)

      if hasattr(self.pargs, 'dcc_clientHost') and self.pargs.dcc_clientHost != None:
        host = self.pargs.dcc_clientHost

      if hasattr(self.pargs, 'dcc_clientPort') and self.pargs.dcc_clientPort != None:
        port = self.pargs.dcc_clientPort

      if hasattr(self.pargs, 'output_file') and self.pargs.output_file != None:
        outputFileName = self.pargs.output_file

      if hasattr(self.pargs, 'error_file') and self.pargs.error_file != None:
        errorFileName = self.pargs.error_file

    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return confLogFileName, timeout, host, port, outputFileName, errorFileName


  # #load logger config file
  #
  # @param configName - name of logger config file
  # @return - None
  def __readLoggerConfig(self, configName):
    try:
      if isinstance(configName, str) and len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)
      # call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  # #fillError method
  # calls from error-code point from main processing (...from event handlers)
  # errorStr - external errorMessage
  # errorCode - external errorCode
  def fillError(self, errorStr, errorCode, isLogging=True):
    self.errorCode = errorCode
    self.errorStr = errorStr
    if isLogging:
      self.logger.error("Error msg: %s, error code: %s", str(self.errorStr), str(self.errorCode))
      self.logger.debug(Utils.getTracebackInfo())


  # #connectionInit method
  # initializes internal variables that containts network connections/communications
  #
  # @param host - host name value
  # @param port - port value
  def connectionInit(self, host, port):
    if self.connectionBuilder is None:
      self.connectionBuilder = ConnectionBuilderLight()

    if len(host) > 1 and host[0] == "\"":
      host = host[1:]
    if host[-1] == "\"":
      host = host[0:-1]

    addr = host + ":" + port
    self.localConnection = self.connectionBuilder.build(transport.Consts.CLIENT_CONNECT, addr,
                                                        transport.Consts.TCP_TYPE)


  # #generateEmptyResponse method
  # If here was some critical error, we generate empty response here , instead real response
  # task - task arg
  def generateEmptyResponse(self):
    obj = dc.EventObjects.ClientResponse([])
    obj.error_code = self.errorCode
    obj.error_message = self.errorStr
    return obj.toJSON()


  # #taskProcessingDeserialize method
  # Method serializes incoming task to the JSON string
  # @param task - task arg
  # @param eventObj - response event object
  # @param timeout - timeout value
  def transportCommunications(self, task, eventObj, timeout):
    retEvent = None
    ret = None
    eventType = None

    eventTypesList = [EVENT_TYPES.SITE_NEW, EVENT_TYPES.SITE_UPDATE, EVENT_TYPES.SITE_STATUS, EVENT_TYPES.SITE_DELETE,
                      EVENT_TYPES.SITE_CLEANUP, EVENT_TYPES.URL_NEW, EVENT_TYPES.URL_STATUS, EVENT_TYPES.URL_UPDATE,
                      EVENT_TYPES.URL_FETCH, EVENT_TYPES.URL_DELETE, EVENT_TYPES.URL_CLEANUP, EVENT_TYPES.URL_CONTENT,
                      EVENT_TYPES.SITE_FIND, EVENT_TYPES.SQL_CUSTOM, EVENT_TYPES.BATCH, EVENT_TYPES.URL_PURGE,
                      EVENT_TYPES.FIELD_RECALCULATE, EVENT_TYPES.URL_VERIFY, EVENT_TYPES.URL_AGE, EVENT_TYPES.URL_PUT,
                      EVENT_TYPES.URL_HISTORY, EVENT_TYPES.URL_STATS, EVENT_TYPES.PROXY_NEW, EVENT_TYPES.PROXY_UPDATE,
                      EVENT_TYPES.PROXY_DELETE, EVENT_TYPES.PROXY_STATUS, EVENT_TYPES.PROXY_FIND, EVENT_TYPES.ATTR_SET,
                      EVENT_TYPES.ATTR_UPDATE, EVENT_TYPES.ATTR_DELETE, EVENT_TYPES.ATTR_FETCH]

    try:
      eventType = eventTypesList[CONSTANTS.TASKS.index(task)]
    except ValueError:
      self.logger.error(">>> Task name not support = " + str(task))

    self.sendEventType = eventType
    self.sendEventObject = eventObj
    mergeVal = None
    try:
      if self.pargs.merge != None:
        mergeVal = bool((self.pargs.merge) > 0)

    except ValueError as err:
      pass

    event = self.eventBuilder.build(eventType, eventObj)
    if mergeVal != None:
      event.cookie = {}
      if mergeVal:
        event.cookie[CONSTANTS.COOKIE_MERGE_NAME] = 1
      else:
        event.cookie[CONSTANTS.COOKIE_MERGE_NAME] = 0
    self.localConnection.send(event)

    try:
      self.logger.debug("!!! Call 'pool' with 'timeout' = %s", str(timeout))
      if self.localConnection.poll(timeout) == 0:
        self.fillError(CONSTANTS.ERROR_STR7.format(str(timeout)), CONSTANTS.ERROR_NETWORK)
      else:
        retEvent = self.localConnection.recv()
      if retEvent != None:
        if hasattr(retEvent, 'eventObj'):
          ret = retEvent.eventObj
        else:
          self.fillError("retEvent hasn't 'eventObj', dump: %s", varDump(retEvent))
    except Exception as err:
      self.fillError("Error: " + str(err), CONSTANTS.ERROR_EXCEPTION)

    return ret


  # #commandProcessingDeserialize method
  # Reads task from file and deserializes it.
  # command - command arg
  # fileName - json filename
  def commandProcessingDeserialize(self, command, fileName):

    try:
      ffile = open(fileName, "r")
      data = ffile.read()
      ffile.close()

      jsonData = json.loads(data)
    except ValueError, err:
      self.logger.error("Deserialize error: %s, json: %s, fileName: '%s'", str(err), str(data), str(fileName))
      raise err

    dCCObjectsSerializator = DCCObjectsSerializator()
    eventObj = None

    if command == CONSTANTS.TASKS[0]:
      eventObj = dCCObjectsSerializator.siteNewDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[1]:
      eventObj = dCCObjectsSerializator.siteUpdateDeserialize(jsonData)  # pylint: disable=R0204
    elif command == CONSTANTS.TASKS[2]:
      eventObj = dCCObjectsSerializator.siteStatusDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[3]:
      eventObj = dCCObjectsSerializator.siteDeleteDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[4]:
      eventObj = dCCObjectsSerializator.siteCleanupDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[5]:
      eventObj = dCCObjectsSerializator.URLNewDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[6]:
      eventObj = dCCObjectsSerializator.URLStatusDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[7]:
      eventObj = dCCObjectsSerializator.URLUpdateDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[8]:
      eventObj = dCCObjectsSerializator.URLFetchDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[9]:
      eventObj = dCCObjectsSerializator.URLDeleteDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[10]:
      eventObj = dCCObjectsSerializator.URLCleanupDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[11]:
      eventObj = dCCObjectsSerializator.URLContentDeserialize(jsonData)
    # find site by root url
    elif command == CONSTANTS.TASKS[12]:
      # logger.debug("jsonData: %s", str(jsonData))
      eventObj = dCCObjectsSerializator.siteFindDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[13]:
      eventObj = dCCObjectsSerializator.SQLCustomDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[14]:
      eventObj = dCCObjectsSerializator.BatchDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[15]:
      eventObj = dCCObjectsSerializator.URLPurgeDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[16]:
      eventObj = dCCObjectsSerializator.FieldRecalculatorDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[17]:
      eventObj = dCCObjectsSerializator.URLVerifyDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[18]:
      eventObj = dCCObjectsSerializator.URLAgeDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[19]:
      eventObj = dCCObjectsSerializator.URLPutDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[20]:
      eventObj = dCCObjectsSerializator.URLHistoryDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[21]:
      eventObj = dCCObjectsSerializator.URLStatsDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[22]:
      eventObj = dCCObjectsSerializator.ProxyNewDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[23]:
      eventObj = dCCObjectsSerializator.ProxyUpdateDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[24]:
      eventObj = dCCObjectsSerializator.ProxyDeleteDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[25]:
      eventObj = dCCObjectsSerializator.ProxyStatusDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[26]:
      eventObj = dCCObjectsSerializator.ProxyFindDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[27]:
      eventObj = dCCObjectsSerializator.AttrSetDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[28]:
      eventObj = dCCObjectsSerializator.AttrUpdateDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[29]:
      eventObj = dCCObjectsSerializator.AttrDeleteDeserialize(jsonData)
    elif command == CONSTANTS.TASKS[30]:
      eventObj = dCCObjectsSerializator.AttrFetchDeserialize(jsonData)
    return eventObj


  # #commandListSerialize method
  # Method implements common serialize processing for list of elements
  # command - command arg
  # eventObj - response event object
  # eventObjClassName - list class name
  # listElementClassName - list element class name
  # excpString - exception substring
  def commandListSerialize(self, command, eventObj, eventObjClassName, listElementClassName, excpString):
    if eventObjClassName != [].__class__.__name__:
      raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(command, "list[]"))
    i = 0
    for listElement in eventObj:
      i += 1
      eventObjClassName = listElement.__class__.__name__
      if eventObjClassName != listElementClassName:
        raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(command, excpString + str(i) + "]"))


  # #commandProcessingSerialize method
  # Method serializes incoming task to the JSON string
  # command - command arg
  # eventObj - response event object
  def commandProcessingSerialize(self, command, eventObj):
    ret = None
    eventObjClassName = eventObj.__class__.__name__
    if eventObjClassName != dc.EventObjects.ClientResponse([]).__class__.__name__:
      raise Exceptions.WrongEventObjectTypeException(CONSTANTS.ERROR_STR8.format(command, "ClientResponse"))
    try:
      ret = eventObj.toJSON()
    except Exception, err:
      self.logger.error(">>> Serialize error %s %s", Utils.varDump(eventObj), str(err))
      self.fillError("Error: " + CONSTANTS.ERROR_STR13, CONSTANTS.ERROR_JSON)
    return ret


  # #setup method
  # Method calls before run application
  def setup(self):
    foundation.CementApp.setup(self)


  # #Command processing build object instance by command name
  # initialize fields with None value
  # @param objectName name of an object class
  #
  def commandProcessingBuild(self, objectName):
    objectInst = None

    for args in range(0, CONSTANTS.OBJECT_MAX_INIT_ARGUMENTS):
      try:
        # Iteratively try to create instance with mandatory constructor arguments
        if args > 0:
          argsList = ",".join(['None' for argsList in xrange(args)])
        else:
          argsList = ""
        # Try to create object instance by name
        self.logger.debug("Try to instantiate as: %s", "dc.EventObjects." + objectName + "(" + argsList + ")")
        objectInst = eval("dc.EventObjects." + objectName + "(" + argsList + ")")  # pylint: disable=W0123
        break
      except TypeError as exp:
        continue
      except Exception, err:
        self.logger.error("Create instance of `%s`: %s : type is `%s`",
                          str(objectName), str(err), str(type(objectInst)))
        raise Exceptions.DeserilizeException("Create instance of object error: " + str(err))

    # Fill with None value all fields
    try:
      for name in dir(objectInst):
        if not name.startswith('__'):
          setattr(objectInst, name, None)
    except Exception as exp:
      self.logger.error("Build object `%s`: %s", str(objectName), str(exp.message))
      raise Exceptions.DeserilizeException("Build object error: " + str(exp.message))

    return objectInst


  # #Command processing fill object instance attributes from fields set json
  # initialize fields with None value
  # @param objectInst object instance
  # @param fieldsJson fields json
  #
  def commandProcessingFill(self, objectInst, fieldsJson):
    try:
      # De-serialize fields set json
      fieldsDict = json.loads(fieldsJson)

      # Process load from file reference
      fieldsDict = self.dictFillFromFile(fieldsDict)
      self.logger.debug("fieldsDict: %s", str(fieldsDict))
      self.logger.debug("objectInst: %s", Utils.varDump(objectInst))
      self.logger.debug("mode: %s", self.pargs.mode)

      if isinstance(objectInst, list):
        newList = []
        # Set fields in object if it is list of objects
        for itemObj in objectInst:
          # logger.debug("Type of item is: %s", str(type(itemObj)))
          for name in dir(itemObj):
            if not name.startswith('__') and name in fieldsDict:
              self.setAttr(itemObj, name, fieldsDict[name], self.pargs.mode)
          newList.append(itemObj)
        objectInst = newList
      else:
        # Set fields in object if it is single
        for name in dir(objectInst):
          if not name.startswith('__') and name in fieldsDict:
            #  setattr(objectInst, name, fieldsDict[name])
            self.setAttr(objectInst, name, fieldsDict[name], self.pargs.mode)

    except Exception as err:
      ExceptionLog.handler(self.logger, err, "Fill object error:")
      self.logger.error("type: `%s`,\nfields: `%s`", str(type(objectInst)), str(fieldsJson))
      raise Exceptions.DeserilizeException("Fill object error: " + str(err))

    return objectInst


  # #Sets object attributes without inheritance overwrite or not
  #
  # @param obj object instance
  # @param name attribute name of object
  # @param valsDict dict of attribute values
  # @param mode 0 - not nested overwrite mode, 1 - nested overwrite, 2 - nested overwrite with append
  #
  def setAttr(self, obj, name, valsDict, mode):
    if mode is None or mode == "" or mode == "0" or (not hasattr(obj, name)):
      # Without nesting, only one first level of fields overwrite
      setattr(obj, name, valsDict)
    else:
      # With nesting support, overwrite and/or append
      objAttr = getattr(obj, name)
      # if hasattr(objAttr, '__class__'):
      if str(type(objAttr)).startswith('<class'):
        # If attribute is a class
        for name2 in dir(objAttr):
          if not name2.startswith('__'):
            # print str(name2) + " | " + str(valsDict)
            if isinstance(valsDict, dict) and name2 in valsDict:
              objAttr2 = getattr(objAttr, name2)
              # if hasattr(objAttr2, "__class__"):
              if str(type(objAttr2)).startswith('<class'):
                self.setAttr(objAttr, name2, valsDict[name2], mode)
              else:
                setattr(objAttr, name2, self.mergeDictList(objAttr, valsDict[name2], mode))
        setattr(obj, name, objAttr)
      else:
        # If attribute is not a class
        setattr(obj, name, self.mergeDictList(objAttr, valsDict, mode))


  # #Merges two dictionaries with nesting of levels
  #
  # @param iter1 dictionary or list to merge
  # @param iter2 dictionary or list to merge with
  # @param mode 0 - not nested overwrite mode, 1 - nested for dicts and overwrite for lists,
  # 2 - nested overwrite with append if not present for dicts and append for lists
  # If iter1 and iter2 is not the same types or not dict and list type - iter2 overwrites iter1 not nested way (mode 0),
  # and nested way (mode 1 and 2)
  #
  def mergeDictList(self, iter1, iter2, mode):
    retIter = None

    if isinstance(iter1, dict) and isinstance(iter2, dict):
      # Both iterable are dicts
      if mode is None or mode == "" or mode == "0":
        # Just overwrite with copy
        retIter = dict(iter2)
      else:
        # Init with source copy
        retIter = dict(iter1)
        # Process source items
        for key, value in iter2.iteritems():
          # If key exists in source and destination or mode 2 (need to be appended)
          if key in retIter or mode == "2":
            retIter[key] = self.mergeDictList(retIter[key], value, mode)
    else:
      if isinstance(iter1, list) and isinstance(iter2, list):
        # Both iterable are lists
        if mode is None or mode == "" or mode == "0" or mode == "1":
          # Just overwrite with copy
          retIter = list(iter2)  # pylint: disable=R0204
        else:
          # Init with source copy
          retIter = list(iter1)
          # Process source items
          for item in iter2:
            retIter.append(item)
      else:
        # Types of iter1 and iter2 are not the same
        if isinstance(iter2, dict):
          # Overwrite with dict copy
          retIter = dict(iter2)
        else:
          if isinstance(iter2, list):
            # Overwrite with list copy
            retIter = list(iter2)
          else:
            # Overwrite with copy of none iterable type or reference of the object
            retIter = iter2

    return retIter


  # #Command processing fill object instance attributes from fields set json
  # initialize fields with None value
  # @param objectInst object instance
  # @param fieldsJson fields json
  #
  def dictFillFromFile(self, d):
    for k, v in d.iteritems():
      if isinstance(v, dict):
        d[k] = self.dictFillFromFile(v)
      else:
        if (isinstance(v, str) or isinstance(v, unicode)) and v.startswith(CONSTANTS.FILE_PROTOCOL_SIGNATURE):
          self.logger.debug("File:%s", str(v[len(CONSTANTS.FILE_PROTOCOL_SIGNATURE):]))
          d[k] = open(v[len(CONSTANTS.FILE_PROTOCOL_SIGNATURE):], 'r').read()

    return d


  # #run method
  # Method contains main application functionality
  def run(self):
    foundation.CementApp.run(self)
    isHelpArg = False
    if '-h' in self.argv or '--help' in self.argv:
      isHelpArg = True
    eventObj = None
    retEventObj = None
    jsonBuf = None
    startTime = time.time()

    try:
      confLogFileName, timeout, host, port, outputFileName, errorFileName = self.__loadAppConfig(self.pargs.config)
      self.__readLoggerConfig(confLogFileName)

      self.logger.debug("!!! Dump pargs: %s", varDump(self.pargs))

      if '-v' in self.argv or '--verbose' in self.argv:
        self.logger.info("Started, args: %s", str(self.argv))

      if self.errorCode == CONSTANTS.ERROR_NOERROR:
        try:
          self.connectionInit(host, port)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
          self.fillError(CONSTANTS.ERROR_STR10, CONSTANTS.ERROR_CONFIG_SECTION)
        if isHelpArg is False and self.pargs.command is None:
          self.fillError(CONSTANTS.ERROR_STR1, CONSTANTS.ERROR_ARGS1)
        elif self.localConnection is None:
          self.fillError(CONSTANTS.ERROR_STR12, CONSTANTS.ERROR_CONNECTION)
        elif self.pargs.command != None:
          if self.pargs.command in CONSTANTS.TASKS:
            if self.pargs.file != None or self.pargs.fields != None:
              try:
                if self.pargs.file != None:
                  # De-serialize object from json file
                  eventObj = self.commandProcessingDeserialize(self.pargs.command, self.pargs.file)
                else:
                  # Dynamic object creation and initialize all fields with None
                  eventObj = self.commandProcessingBuild(
                      CONSTANTS.TASKS_OBJECTS[CONSTANTS.TASKS.index(self.pargs.command)])
                # Cover some fields with values from command line argument
                if self.pargs.fields != None:
                  # Fill some object's fields with values
                  eventObj = self.commandProcessingFill(eventObj, self.pargs.fields)
                  # logger.debug("resulted eventObj: %s", str(eventObj))
                  self.logger.debug("resulted eventObj: %s", Utils.varDump(eventObj))
              except IOError:
                self.fillError(CONSTANTS.ERROR_STR4, CONSTANTS.ERROR_BAD_FILE_NAME)
              except ValueError:
                self.fillError(CONSTANTS.ERROR_STR5, CONSTANTS.ERROR_BAD_JSON)
              except Exceptions.DeserilizeException as excp:
                self.fillError(CONSTANTS.ERROR_STR6.format(excp.message), CONSTANTS.ERROR_DCC)
              if eventObj != None:
                retEventObj = self.transportCommunications(self.pargs.command, eventObj, timeout)
                if retEventObj != None:
                  try:
                    jsonBuf = self.commandProcessingSerialize(self.pargs.command, retEventObj)
                  except Exceptions.WrongEventObjectTypeException as excp:
                    self.fillError(excp.message, CONSTANTS.ERROR_WRONG_RESPONSE)

              elif self.errorCode == CONSTANTS.ERROR_NOERROR:
                self.fillError(CONSTANTS.ERROR_STR14, CONSTANTS.ERROR_OBJECT_CREATE)
            else:
              self.fillError(CONSTANTS.ERROR_STR2, CONSTANTS.ERROR_ARGS2)
          else:
            self.fillError(CONSTANTS.ERROR_STR3, CONSTANTS.ERROR_BAD_TASK)
    except Exception, err:
      self.fillError(str(err), CONSTANTS.ERROR_INITIALIZATION, False)

    if jsonBuf is None:
      jsonBuf = self.generateEmptyResponse()

    if outputFileName is None:
      # output to stdout
      sys.stdout.write(jsonBuf)
      sys.stdout.flush()
    else:
      # output to output file
      self.writeToFile(outputFileName, jsonBuf)

    if errorFileName is not None:
      self.writeToFile(errorFileName, self.makeErrorFileContent())

    # self.pargs.verbose
    if '-v' in self.argv or '--verbose' in self.argv:
      self.logger.info("Finished, time: %s sec", str(time.time() - startTime))

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)



  # #close method
  # Method calls after application run
  def close(self):
    foundation.CementApp.close(self)


  # # Write to file some data
  #
  # @param fileName- file name
  # @param data - data string buffer
  # @return - None
  def writeToFile(self, fileName, data):
    try:
      if fileName is not None and isinstance(fileName, basestring) and fileName != "":
        f = open(fileName, 'w')
        f.write(data)
        f.close()
      else:
        raise Exception("Bad parameter 'fileName' = '%s'" % str(fileName))

    except Exception, err:
      self.logger.error("Write to file '%s' failed, error: '%s'", str(fileName), str(err))


  # # Make error file content
  # @param - None
  # @return json string
  def makeErrorFileContent(self):

    dataDict = {}
    dataDict[self.ERROR_FILE_ERROR_MESSAGE_FIELD_NAME] = self.errorStr
    dataDict[self.ERROR_FILE_ERROR_CODE_FIELD_NAME] = self.errorCode

    return json.dumps(dataDict)
