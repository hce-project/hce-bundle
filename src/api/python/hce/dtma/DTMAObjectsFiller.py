'''
Created on Mar 26, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import logging
import json
import Constants as CONSTANTS
import DTMAExceptions
import dtm.EventObjects
import app.Consts as APP_CONSTS

# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)

##DTMCObjectsFiller Class contents serialize/deserialize methods for incoming "DTMA" commands
#
class DTMAObjectsFiller(object):


  def __init__(self):
    pass


  def generateStatObjects(self, fields, classes):
    ret = []
    names = []
    filedsList = []
    fieldsDict = {}
    if fields != None and len(fields) > 0:
      filedsList = fields.split(CONSTANTS.FIELDS_SEPARATOR)
      for field in filedsList:
        if len(field) > 0:
          fieldPair = field.split(CONSTANTS.NAME_VALUE_SEPARATOR)
          if len(fieldPair) >= 1:
            fieldsDict[fieldPair[0]] = None
    if len(classes) > 0:
      names = classes.split(CONSTANTS.FIELDS_SEPARATOR)
      for name in names:
        ret.append(dtm.EventObjects.AdminStatData(name, fieldsDict))
    else:
      raise DTMAExceptions.DTMAEmptyClasses("DTMAEmptyClasses [STAT]")
    return ret


  def generateSetObjects(self, fields, classes):
    ret = []
    classesList = []
    filedsList = []
    fieldsDict = {}
    if len(fields) > 0:
      filedsList = fields.split(CONSTANTS.FIELDS_SEPARATOR)
      for field in filedsList:
        fieldPair = field.split(CONSTANTS.NAME_VALUE_SEPARATOR)
        if len(fieldPair) < 2:
          raise DTMAExceptions.DTMANameValueException("wrong name-value format in --field arg [SET]")
        else:
          try:
            fieldsDict[fieldPair[0]] = eval(fieldPair[1])  # pylint: disable=eval-used
          except Exception:
            raise DTMAExceptions.DTMANameValueException("Wrong value type, for string use str('abcd') as value!")
      if len(classes) > 0:
        classesList = classes.split(CONSTANTS.FIELDS_SEPARATOR)
        for name in classesList:
          ret.append(dtm.EventObjects.AdminConfigVars(name, fieldsDict))
      else:
        raise DTMAExceptions.DTMAEmptyClasses("DTMAEmptyClasses [SET]")
    else:
      raise DTMAExceptions.DTMAEmptyFields("DTMAEmptyFields [SET]")

    return ret


  def generateGetObjects(self, fields, classes):
    ret = []
    classesList = []
    filedsList = []
    fieldsDict = {}
    if len(fields) > 0:
      filedsList = fields.split(CONSTANTS.FIELDS_SEPARATOR)
      for field in filedsList:
        if field != None and field != "":
          fieldsDict[field] = ""
      if len(classes) > 0:
        classesList = classes.split(CONSTANTS.FIELDS_SEPARATOR)
        for name in classesList:
          ret.append(dtm.EventObjects.AdminConfigVars(name, fieldsDict))
      else:
        raise DTMAExceptions.DTMAEmptyClasses("DTMAEmptyClasses [SET]")
    else:
      raise DTMAExceptions.DTMAEmptyFields("DTMAEmptyFields [SET]")
    return ret


  def generateStopObjects(self, classes):
    ret = []
    names = []
    if len(classes) > 0:
      names = classes.split(CONSTANTS.FIELDS_SEPARATOR)
      for name in names:
        ret.append(dtm.EventObjects.AdminState(name, dtm.EventObjects.AdminState.STATE_SHUTDOWN))
    else:
      raise DTMAExceptions.DTMAEmptyClasses("DTMAEmptyFields [Stop]")
    return ret


  def generateSuspendObject(self, fields):
    ret = []
    if fields is not None:
      if fields == "1":
        ret.append(dtm.EventObjects.AdminSuspend(dtm.EventObjects.AdminSuspend.SUSPEND))
      else:
        ret.append(dtm.EventObjects.AdminSuspend(dtm.EventObjects.AdminSuspend.RUN))
    return ret


  def generateSystemObject(self, fields):
    ret = []
    try:
      dataJson = json.loads(fields)
      ret.append(dtm.EventObjects.System(dataJson["type"], dataJson["data"]))
    except Exception:
      raise DTMAExceptions.DTMAEmptyFields("DTMAEmptyFields [SYSTEM]")
    return ret


  def generateSQLCustomObject(self, fields):
    ret = []
    try:
      dataJson = json.loads(fields)
      ret.append(dtm.EventObjects.CustomRequest(dataJson["id"], dataJson["sql"], None))
    except Exception:
      raise DTMAExceptions.DTMAEmptyFields("DTMAEmptyFields [SQL_CUSTOM]")
    return ret


  ##generateObjectsList method represents main income point of user call.
  #
  def generateObjectsList(self, cmd, fields, classes):
    objectList = []
    if cmd == CONSTANTS.TASKS[0]:
      objectList = self.generateStatObjects(fields, classes)
    elif cmd == CONSTANTS.TASKS[1]:
      objectList = self.generateSetObjects(fields, classes)
    elif cmd == CONSTANTS.TASKS[2]:
      objectList = self.generateGetObjects(fields, classes)
    elif cmd == CONSTANTS.TASKS[3]:
      objectList = self.generateStopObjects(classes)
    elif cmd == CONSTANTS.TASKS[4]:
      objectList = self.generateSuspendObject(fields)
    elif cmd == CONSTANTS.TASKS[5]:
      objectList = self.generateSystemObject(fields)
    elif cmd == CONSTANTS.TASKS[6]:
      objectList = self.generateSQLCustomObject(fields)
    return objectList
