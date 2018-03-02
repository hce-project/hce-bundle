'''
Created on Apr 2, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from cement.core import foundation
import logging
import Constants as CONSTANTS
import app.Utils as Utils
import sys
import app.Consts as APP_CONSTS


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


logging.basicConfig()
#logger = logging.getLogger(CONSTANTS.APP_NAME)


##JsonChecker Class contents main functional of JsonChecker application, class inherits from foundation.CementApp
#
class JsonChecker(foundation.CementApp):

  class Meta:
    label = CONSTANTS.APP_NAME


  ##constructor
  #initialise all class variable
  def __init__(self):
    foundation.CementApp.__init__(self)
    self.errorCode = CONSTANTS.ERROR_NOERROR
    self.errorStr = ""


  ##fillError method
  #calls from error-code point from main processing
  def fillError(self, errorStr, errorCode):
    self.errorCode = errorCode
    self.errorStr = errorStr
    logger.error(self.errorStr)


  ##readJSONValue method
  #Method reads json string from file and search alue by path
  def readJSONValue(self, fileName, path):
    fd = None
    value = None
    try:
      fd = open(fileName, 'r')
    except IOError:
      fd = None
    if fd != None:
      jsonString = fd.read()
      try:
        value = Utils.getPath(None, jsonString, path)
        value = str(value)
      except (ValueError):
        self.fillError(CONSTANTS.ERROR_STR3, CONSTANTS.ERROR_BAD_JSON)
      except (TypeError, KeyError, IndexError):
        self.fillError(CONSTANTS.ERROR_STR4, CONSTANTS.ERROR_PATH_NOT_FOUND)
    else:
      self.fillError(CONSTANTS.ERROR_STR2, CONSTANTS.ERROR_FILE)
    return value


  ##valueChecker method
  #Method compares incoming jsonValue with value, or find jsonValue in value
  #if value is value's list
  def valueChecker(self, jsonValue, value):
    isFind = False
    valueList = value.split(CONSTANTS.VALUE_SEPARATOR)
    for item in valueList:
      if item == jsonValue:
        isFind = True
        break
    if isFind == False:
      self.fillError(CONSTANTS.ERROR_STR5, CONSTANTS.ERROR_VALUE_NOT_FOUND)


  ##setup method
  #Method calls before run application
  def setup(self):
    foundation.CementApp.setup(self)
    self.args.add_argument("-path", "--path", action="store")
    self.args.add_argument("-value", "--value", action="store")
    self.args.add_argument("-file", "--file", action="store")


  ##run method
  #Method contains main application functionality
  def run(self):
    foundation.CementApp.run(self)
    jsonValue = None
    if self.pargs.path == None or self.pargs.file == None:
      self.fillError(CONSTANTS.ERROR_STR1, CONSTANTS.ERROR_ARG1)
    else:
      jsonValue = self.readJSONValue(self.pargs.file, self.pargs.path)
      if jsonValue != None and self.pargs.value != None:
        self.valueChecker(jsonValue, self.pargs.value)
    sys.exit(self.errorCode)


  ##close method
  #Method calls after application run
  def close(self):
    foundation.CementApp.close(self)
