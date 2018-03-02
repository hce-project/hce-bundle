'''
Created on Feb 13, 2014

@author: igor
'''

import json

from transport.Request import Request
from transport.Response import ResponseFormatErr
from transport.UIDGenerator import UIDGenerator
from drce.CommandConvertor import CommandConvertorError, TaskExecuteStructEncoder
from drce.Commands import DRCECover
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


# import base64
# #Exception which encapsulates errors related to convertatin operations
#
class CommandExecutorErr(Exception):

  def __init__(self, msg):
    Exception.__init__(self, msg)


# #Main point for execution commands related to the drce
# It hides all complexities of command execution
#
class CommandExecutor(object):


  # #constructor
  #
  # @param connection an instance of transport.Connection object
  # @param cmd_convertor an instance of CommandConvertor object
  def __init__(self, connection, cmd_convertor):
    self.connection = connection
    self.cmd_convertor = cmd_convertor
    # @var id_generator
    # a member variable, used to generate uid for messages
    self.id_generator = UIDGenerator()


  # #simple wrapper to explicit express operation of replace connection
  # add ability to execute commands on many connections
  #
  # @param connection an instance of transport.Connection object
  # @return None
  def replace_connection(self, connection):
    self.connection = connection



  # #execute Task*Request command
  #
  # because a connection is external dependence - doesn't catch it exceptions
  # @param command an instance of Task*Request object
  # @param timeout timeout in msec
  # @param ttl time of task live in msec
  # @param maxTries max tries to receive message, if zero and received message that is not the same id as requested
  #                it will be returned, if grater than zero than N tries to receive message will be performed. If
  #                timeout reached it breaks loop and exception raised
  # @return TaskResponse or throw CommandExecutorErr
  def execute(self, command, timeout=1000, ttl=30000, maxTries=100):
    if maxTries < 0:
      maxTries = 0

    try:
      logger.debug("command: %s", Utils.varDump(command, strTypeMaxLen=10000))
      cmd_json = self.cmd_convertor.to_json(command, logger)
      drce_cover_envelop = DRCECover(ttl, cmd_json)
      request = Request(self.id_generator.get_uid())
      request.add_data(json.dumps(drce_cover_envelop, cls=TaskExecuteStructEncoder))
      request.route = command.route
      request.task_type = command.task_type

      uid = request.get_uid()
      logger.debug("Send DRCE request msg Id:" + uid + ", route: " + str(request.route))

      self.connection.send(request, uid)

      for i in range(int(maxTries) + 1):
        response = self.connection.recv(timeout, uid)
        logger.debug("Received DRCE response msg Id:" + response.get_uid())
        if response.get_uid() == request.get_uid() or maxTries == 0:
          cover_envelop_response = json.loads(response.get_body())
          return self.cmd_convertor.from_json(cover_envelop_response["data"])
        else:
          logger.error("DRCE response msg Id:" + response.get_uid() + \
                       " not matched with the request msg Id:" + request.get_uid() + \
                       ", try: " + str(i))
    except (ResponseFormatErr, CommandConvertorError, KeyError, CommandExecutorErr) as err:
      logger.error("DRCE object model error: %s", str(err))
      raise CommandExecutorErr(str(err))
    except Exception as err:
      logger.error("General error: %s", str(err))
      raise CommandExecutorErr(str(err))

