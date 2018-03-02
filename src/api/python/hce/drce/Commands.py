'''
Created on Feb 12, 2014

@author: igor, bgv
'''

import Consts as consts
from app.Utils import JsonSerializable

##Base command for all dre request command
#
class BaseRequest(object):

  ##constructor
  #
  #@param type  ctype of a command
  #@param cid - a command id
  def __init__(self, ctype, cid):
    super(BaseRequest, self).__init__()

    self.type = ctype
    #@var data
    #a member variable, hold command data
    self.data = dict()
    self.id = cid
    self.route = None
    self.task_type = 0


##wrapper for Session fields array of execute task
#
class Session(object):
  TMODE_SYNC = 1
  TMODE_ASYNC = 2

  TYPE_HOST_SHELL = 0
  TYPE_SSH = 1

  '''
  wrapper for Session fields array of execute task
  '''
  def __init__(self, tmode, ctype=TYPE_HOST_SHELL, maxExecutionTime=0):
    super(Session, self).__init__()

    self.type = ctype
    self.port = 0
    self.user = ""
    self.password = ""
    self.shell = ""
    self.environment = {}
    self.timeout = 0
    self.tmode = tmode
    self.time_max = maxExecutionTime
    self.home_directory = ""
    if tmode == self.TMODE_SYNC:
      self.cleanup = consts.TERMINATE_DATA_DELETE
    else:
      self.cleanup = consts.TERMINATE_DATA_SAVE


  def add_evn_pair(self, param_name, param_value):
    self.environment[param_name] = param_value



##wrapper for Limits fields array of execute task
#
class Limits(object):

  def __init__(self):
    super(Limits, self).__init__()

    self.proc_max = 0
    self.threads_max = 0
    self.cpu = 0
    self.rram_free = 0
    self.rram_free_min = 0
    self.vram_free = 0
    self.vram_free_min = 0
    self.disk_free = 0
    self.disk_free_min = 0



## wrapper for TaskExecuteStruct
#
class TaskExecuteStruct(object):

  def __init__(self):
    super(TaskExecuteStruct, self).__init__()

    self.session = Session(1, 0, 1200000)
    self.limits = Limits()
    self.command = ""
    self.input = ""
    self.files = list()


  ##simple wrapper for addion files fields
  #
  def add_files(self, name, data, action):
    self.files.append(dict({"name" : name,
                      "data" : data,
                      "action" : action}))



##wrapper for task response item
#
class ResponseItem(object):

  def __init__(self):
    super(ResponseItem, self).__init__()

    self.error_code = 0
    self.error_message = ""
    self.id = 0
    self.type = 0
    self.host = ""
    self.port = 0
    self.state = 0
    self.pid = 0
    self.stdout = ""
    self.stderror = ""
    self.exit_status = 0
    self.files = list()
    self.node = ""
    self.time = 0
    self.fields = dict()



##wrapper for task response
#
class TaskResponse(object):

  def __init__(self, items):
    super(TaskResponse, self).__init__()

    self.items = items



##wrapper for cover object
class DRCECover(object):

  def __init__(self, ttl, data):
    super(DRCECover, self).__init__()

    self.type = 2
    self.ttl = ttl
    self.data = data



##wrapper for task request
#
class TaskExecuteRequest(BaseRequest, JsonSerializable):

  def __init__(self, tId):
    super(TaskExecuteRequest, self).__init__(consts.EXECUTE_TASK, tId)

    self.data = TaskExecuteStruct()



##Check task request
#
class TaskCheckRequest(BaseRequest, JsonSerializable):

  def __init__(self, tId, info_type):
    super(TaskCheckRequest, self).__init__(consts.CHECK_TASK_STATE, tId)

    self.data = dict({"type" : info_type})



##Get task's data request
#
class TaskGetDataRequest(BaseRequest, JsonSerializable):

  def __init__(self, tId, info_type):
    super(TaskGetDataRequest, self).__init__(consts.GET_TASK_DATA, tId)

    self.data = dict({"type" : info_type})



##Terminate task request
#
class TaskTerminateRequest(BaseRequest, JsonSerializable):


  def __init__(self, tId):
    super(TaskTerminateRequest, self).__init__(consts.TERMINATE_TASK, tId)

    self.data = dict({"alg":consts.TERMINATE_ALGORITHM_DEFAULT,
                      "delay":1,
                      "repeat":1,
                      "signal":9,
                      "cleanup":consts.TERMINATE_DATA_DELETE
                     })



##Delete task request
#
class TaskDeleteRequest(BaseRequest, JsonSerializable):


  def __init__(self, tId):
    super(TaskDeleteRequest, self).__init__(consts.DELETE_TASK, tId)

