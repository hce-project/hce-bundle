'''
Created on Feb 5, 2014

@author: igor, bgv
'''

import json
import base64

from Commands import ResponseItem
from Commands import Session, Limits
from Commands import TaskExecuteRequest
from Commands import TaskResponse, DRCECover

import app.Utils as Utils  # pylint: disable=F0401


##Exception which inform about errors which appeared during
#parsing procedure of drce message protocol
class CommandConvertorError(Exception):

  def __init__(self, msg):
    Exception.__init__(self, msg)



##Helper class is used for correct encoding in json format
#from TaskExecuteStruct object
class TaskExecuteStructEncoder(json.JSONEncoder):
# pylint: disable=E0202
  def default(self, obj):

    if isinstance(obj, DRCECover):
      return obj.__dict__

    return obj.__dict__



##Helper class is used for correct encoding in json format
#from Task*Request object
class TaskExecuteRequestEncoder(json.JSONEncoder):
# pylint: disable=E0202
  def default(self, obj):

    if isinstance(obj, TaskExecuteRequest):
      return obj.__dict__

    if isinstance(obj, Session):
      return obj.__dict__

    if isinstance(obj, Limits):
      return obj.__dict__

    return obj.__dict__



##Helper class is used for correct decoding data from json format
#in TaskResponse
class TaskResponseDecoder(json.JSONDecoder):

  ##decoding function
  #
  #@param json_string input json string
  #@return TaskResponse
  def decode(self, json_string, _w=json.decoder.WHITESPACE.match):
    default_obj = super(TaskResponseDecoder, self).decode(json_string, _w)
    items = list()

    for response_item in default_obj:
      response = ResponseItem()
      response.error_code = response_item["error_code"]
      response.error_message = response_item["error_message"]
      response.id = response_item["id"]
      response.type = response_item["type"]
      response.host = response_item["host"]
      response.port = response_item["port"]
      response.state = response_item["state"]
      response.pid = response_item["pid"]
      response.stdout = response_item["stdout"]
      response.stderror = response_item["stderror"]
      response.exit_status = response_item["exit_status"]
      response.files = self.__process_files(response_item["files"])
      response.node = response_item["node"]
      response.time = response_item["time"]
      response.fields = response_item["fields"]

      items.append(response)

    task_response = TaskResponse(items)
    return task_response



  ##parse result_item files files
  #
  #@return list of files
  def __process_files(self, files_list):
    files = []
    for item in files_list:
      files.append({"name":item["name"],
                  "data":item["data"],
                  "action":item["action"]})
    return files



##Convertor which used to convert  Task*Reques to json
#and  TaskResponse from json
#
class CommandConvertor_old(object):
  '''
  Convert Request to json and restore Response from json
  '''

  ##convert from Task*Reques object to json string
  #
  #@param command an instance of Task*Reques object
  #@return json string or throw  CommandConvertorError
  def to_json(self, command):
    try:
      cmd_json = None
      if isinstance(command, TaskExecuteRequest):
        cmd_json = json.loads(json.dumps(command, cls=TaskExecuteRequestEncoder))  #return
      else:
        cmd_json = json.loads(json.dumps(command.__dict__))  #return

      data = cmd_json["data"]
      data_json = json.dumps(data)

      cmd_json["data"] = base64.b64encode(data_json)
      cmd_json = json.dumps(cmd_json)

      return cmd_json

    except (TypeError, ValueError) as err:
      raise CommandConvertorError("convert to json " + err.message)


  ##convert from json string to TaskResponse
  #
  #@param json_string json string
  #@return TaskResponse or throw CommandConvertorError
  def from_json(self, json_string):
    try:
      drceResponseObj = json.loads(json_string, cls=TaskResponseDecoder)
      for item in drceResponseObj.items:
        #For each item in DRCE response base64decode encoded fields
        item.stderror = base64.b64decode(item.stderror)
        item.stdout = base64.b64decode(item.stdout)
      return drceResponseObj
    except (ValueError, KeyError, TypeError) as err:
      raise CommandConvertorError("convert from json " + err.message)



##Convertor which used to convert  Task*Reques to json
#and  TaskResponse from json
#
class CommandConvertor(object):
  '''
  Convert Request to json and restore Response from json
  '''

  ##convert from Task*Reques object to json string
  #
  #@param cmdObj an instance of Task*Request object
  #@return json string or throw  CommandConvertorError
  def to_json(self, taskRequestObj, log=None):
    cmd_json = None
    try:
      cmd_json = taskRequestObj.toJSON()
#       if log is not None:
#         log.debug("!!! cmd_json: %s", cmd_json)

      cmd_json = json.loads(cmd_json)

      if "data" in cmd_json:
        data_json = json.dumps(cmd_json["data"])
      else:
        raise CommandConvertorError("convert to json error, \"data\" field not found!")

      cmd_json["data"] = base64.b64encode(data_json)
      cmd_json = json.dumps(cmd_json)

      return cmd_json

    except (TypeError, ValueError) as err:
      raise CommandConvertorError("convert to json error : " + str(err) + "\n" + Utils.varDump(taskRequestObj) + '\n' + Utils.getTracebackInfo() + \
                                  "\ncmd_json: " + Utils.varDump(cmd_json) + "\ntaskRequestObj: " + Utils.varDump(taskRequestObj))


  ##convert from json string to TaskResponse
  #
  #@param json_string json string
  #@return TaskResponse or throw CommandConvertorError
  def from_json(self, json_string):
    try:
      drceResponseObj = json.loads(json_string, cls=TaskResponseDecoder)
      for item in drceResponseObj.items:
        #For each item in DRCE response base64decode encoded fields
        item.stderror = base64.b64decode(item.stderror)
        item.stdout = base64.b64decode(item.stdout)
      return drceResponseObj
    except (ValueError, KeyError, TypeError) as err:
      raise CommandConvertorError("convert from json " + err.message)

