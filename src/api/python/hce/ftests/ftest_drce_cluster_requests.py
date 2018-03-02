'''
Created on Mar 21, 2014

@author: igor
'''

import logging

from drce.DRCEManager import DRCEManager, HostParams
from drce.Commands import TaskExecuteRequest
import app.Consts as APP_CONSTS

def getLogger():
  # create logger
  log = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  log.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)

  return log


if __name__ == '__main__':

  logger = getLogger()

  timeout = 1000
  request_id = "1"
  host_params = HostParams("127.0.0.1", 5630)
  task_execute_request = TaskExecuteRequest(request_id)
  task_execute_request.data.command = 'ls -l'

  drceManager = DRCEManager()
  drceManager.activate_host(host_params)

  taskResponse = drceManager.process(task_execute_request, timeout)

  logger.info("response item count = %s", str(len(taskResponse.items)))
  for item in taskResponse.items:
      print item.__dict__

  logger.info("OK")
