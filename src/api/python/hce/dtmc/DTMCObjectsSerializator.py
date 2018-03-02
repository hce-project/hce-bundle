'''
Created on Mar 19, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import app.Exceptions as Exceptions
import dtm.EventObjects
import app.Consts as APP_CONSTS
import logging
import types

# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)


##DTMCObjectsSerializator Class contents serialize/deserialize methods for incoming "DTMC" commands
#
class DTMCObjectsSerializator(object):

  def __init__(self):
    pass


  ##newDeserialize method, deserializes incoming jsonData to the NewTask object
  #jsonData - incoming json string
  def newDeserialize(self, jsonData):
    newObject = dtm.EventObjects.NewTask("")
    if "command" in jsonData:
      newObject.command = jsonData["command"]
    else:
      raise Exceptions.DeserilizeException("NEW.command json-field not found")
    if "id" in jsonData:
      newObject.id = int(jsonData["id"])
    else:
      raise Exceptions.DeserilizeException("NEW.id json-field not found")
    if "input" in jsonData:
      newObject.input = jsonData["input"]
    else:
      raise Exceptions.DeserilizeException("NEW.input json-field not found")
    if "files" in jsonData:
      if type(jsonData["files"]) != type([]):
        raise Exceptions.DeserilizeException("NEW.files not list type")
      newObject.files = jsonData["files"]
    else:
      raise Exceptions.DeserilizeException("NEW.files json-field not found")
    if "session" in jsonData:
      if type(jsonData["session"]) != type({}):
        raise Exceptions.DeserilizeException("NEW.session not dict type")
      if newObject.session == None:
        newObject.session = jsonData["session"]
      else:
        for key in jsonData["session"].keys():
          newObject.session[key] = jsonData["session"][key]
    else:
      raise Exceptions.DeserilizeException("NEW.session json-field not found")
    if "strategy" in jsonData:
      if type(jsonData["strategy"]) != type({}):
        raise Exceptions.DeserilizeException("NEW.strategy not dict type")
      if newObject.strategy == None:
        newObject.strategy = jsonData["strategy"]
      else:
        for key in jsonData["strategy"].keys():
          newObject.strategy[key] = jsonData["strategy"][key]
    else:
      raise Exceptions.DeserilizeException("NEW.strategy json-field not found")
    if "limits" in jsonData:
      if type(jsonData["limits"]) != type({}):
        raise Exceptions.DeserilizeException("NEW.limits not dict type")
      if newObject.limits == None:
        newObject.limits = jsonData["limits"]
      else:
        for key in jsonData["limits"].keys():
          newObject.limits[key] = jsonData["limits"][key]
    else:
      raise Exceptions.DeserilizeException("NEW.limits json-field not found")
    if "autoCleanupFields" in jsonData:
      if type(jsonData["autoCleanupFields"]) != type({}):
        raise Exceptions.DeserilizeException("NEW.autoCleanupFields not dict type")
      newObject.autoCleanupFields = jsonData["autoCleanupFields"]
    return newObject


  def checkDeserialize(self, jsonData):
    checkObject = None
    if "id" in jsonData:
#      checkObject.id = int(jsonData["id"])
      checkObject = dtm.EventObjects.CheckTaskState(int(jsonData["id"]))
    else:
      raise Exceptions.DeserilizeException("CHECK.id json-field not found")
    if "type" in jsonData:
      checkObject.type = int(jsonData["type"])
    else:
      raise Exceptions.DeserilizeException("CHECK.type json-field not found")
    return checkObject


  def terminateDeserialize(self, jsonData):
    deleteObject = None
    if "id" in jsonData:
#      deleteObject.id = int(jsonData["id"])
      deleteObject = dtm.EventObjects.DeleteTask(int(jsonData["id"]))
    else:
      raise Exceptions.DeserilizeException("TERMINATE.id json-field not found")
    if "alg" in jsonData:
      deleteObject.alg = int(jsonData["alg"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.alg json-field not found")
    if "delay" in jsonData:
      deleteObject.delay = int(jsonData["delay"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.delay json-field not found")
    if "repeat" in jsonData:
      deleteObject.repeat = int(jsonData["repeat"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.repeat json-field not found")
    if "signal" in jsonData:
      deleteObject.signal = int(jsonData["signal"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.signal json-field not found")
    if "host" in jsonData:
      deleteObject.host = str(jsonData["host"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.host json-field not found")
    if "port" in jsonData:
      deleteObject.port = int(jsonData["port"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.port json-field not found")
    if "action" in jsonData:
      deleteObject.action = int(jsonData["action"])
    else:
      raise Exceptions.DeserilizeException("TERMINATE.action json-field not found")
    if "strategy" in jsonData:
      if type(jsonData["strategy"]) != type({}):
        raise Exceptions.DeserilizeException("TERMINATE.strategy not dict type")
      if deleteObject.strategy == None:
        deleteObject.strategy = jsonData["strategy"]
      else:
        for key in jsonData["strategy"].keys():
          deleteObject.strategy[key] = jsonData["strategy"][key]
    return deleteObject


  def getDeserialize(self, jsonData):
    fetchObject = None
    if "id" in jsonData:
#      fetchObject.id = int(jsonData["id"])
      fetchObject = dtm.EventObjects.FetchTasksResults(int(jsonData["id"]))
    else:
      raise Exceptions.DeserilizeException("GET.id json-field not found")
    if "type" in jsonData:
      fetchObject.type = int(jsonData["type"])
    else:
      raise Exceptions.DeserilizeException("GET.type json-field not found")
    return fetchObject


  def statusDeserialize(self, jsonData):
    statusObject = None
    if "ids" in jsonData:
      if type(jsonData["ids"]) != type([]):
        raise Exceptions.DeserilizeException("STATUS.ids not list type")
      statusObject = dtm.EventObjects.GetTasksStatus(list(jsonData["ids"]))
    else:
      raise Exceptions.DeserilizeException("STATUS.ids json-field not found")
    if "filters" in jsonData:
      if type(jsonData["filters"]) != type({}):
        raise Exceptions.DeserilizeException("STATUS.filters not dict type")
      statusObject.filters = jsonData["filters"]
    else:
      raise Exceptions.DeserilizeException("STATUS.filters json-field not found")
    if "strategy" in jsonData:
      if type(jsonData["strategy"]) != type({}):
        raise Exceptions.DeserilizeException("STATUS.strategy not dict type")
      statusObject.strategy = jsonData["strategy"]
    else:
      raise Exceptions.DeserilizeException("STATUS.strategy json-field not found")
    return statusObject


  def cleanupDeserialize(self, jsonData):
    cleanupObject = None
    if "id" in jsonData:
      cleanupObject = dtm.EventObjects.DeleteTaskResults(int(jsonData["id"]))
    else:
      raise Exceptions.DeserilizeException("CLEANUP.id json-field not found")
    return cleanupObject


  def getTasksDeserialize(self, jsonData):
    getTasksObject = None
    if "fetchNum" in jsonData:
      getTasksObject = dtm.EventObjects.FetchAvailabelTaskIds(int(jsonData["fetchNum"]))
    else:
      raise Exceptions.DeserilizeException("GET_TASKS.fetchNum json-field not found")
    if "fetchAdditionalFields" in jsonData:
      getTasksObject.fetchAdditionalFields = bool(jsonData["fetchAdditionalFields"])
    if "tableName" in jsonData:
      getTasksObject.tableName = str(jsonData["tableName"])
    if "criterions" in jsonData and jsonData["criterions"] is not None:
      if type(jsonData["criterions"]) is not types.DictType:
        raise Exceptions.DeserilizeException("GET_TASKS.criterions has wrong type")
      if hasattr(getTasksObject.criterions, '__iter__'):
        getTasksObject.criterions.update(jsonData["criterions"])
      else:
        getTasksObject.criterions = jsonData["criterions"]
    return getTasksObject
