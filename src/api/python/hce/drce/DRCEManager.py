'''
Created on Feb 14, 2014

@author: igor
'''

import logging
from collections import namedtuple

from transport.Connection import ConnectionParams, ConnectionTimeout
from transport.Connection import TransportInternalErr

from drce.CommandConvertor import CommandConvertor
from drce.CommandExecutor import CommandExecutor, CommandExecutorErr
from drce.ConnectionManager import ConnectionManager

import app.Consts as APP_CONSTS
# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)

# #High level users class. May contains various info
#
HostParams = namedtuple("HostParams", "host port")


# # Class which provides base functionality for processing drce tasks(commands)
#
# For customisation of behaviour implement hook* methods
class DRCEManager(object):


  # #constructor
  def __init__(self):
    '''
    Constructor
    '''
    # @var connection
    # a member variable, holds current connection,
    # will be used in inheritance classes
    self.connection = None
    # @var connect_params
    # a member variable, holds current connect_params
    # will be used in inheritance classes
    self.connect_params = None
    self.connect_manager = ConnectionManager()
    self.cmd_executor = CommandExecutor(self.connection, CommandConvertor())


  # #create connection for a host
  #
  # @param   host_params an instance  HostParams
  # @return None
  def activate_host(self, host_params):
    con_params = ConnectionParams(host_params.host, host_params.port)
    self.connection = self.connect_manager.create_connection(con_params)
    self.connect_params = con_params
    self.cmd_executor.replace_connection(self.connection)


  # #free resources related to self.connection object
  #
  # @return None
  def clear_host(self):
    self.connect_manager.destroy_connection(self.connection)
    self.connection = None
    self.connect_params = None
    self.cmd_executor.replace_connection(self.connection)


  # #process command
  #
  # #by default - all throws are raised up (propagate out)
  # @param commans  one from Commands.taskrequest*
  # @param timeout  max wait time for processing command
  # @param ttl time of task live
  # @return  TaskResponse
  def process(self, command, timeout=3000, ttl=300000):
    try:
      return self.cmd_executor.execute(command, timeout, ttl)
    except ConnectionTimeout as err:
      self.timeout_hook(err, command, timeout)
    except TransportInternalErr as err:
      self.transport_err_hook(err, command, timeout)
    except CommandExecutorErr as err:
      self.executor_err_hook(err, command, timeout)

  # #function will be called when raises ConnectionTimeout
  #
  # @param connection_timeout an instance of ConnectionTimeout
  # @param command the current processing command
  # @param timeout timeout related to the command
  # @return re-raise  connection_timeout
  # pylint: disable=W0612
  def timeout_hook(self, connection_timeout, command, timeout):
    del command, timeout
    raise connection_timeout


  # #function will be called when raises TransportInternalErr
  #
  # @param transport_internal_err an instance of TransportInternalErr
  # @param command the current processing command
  # @param timeout timeout related to the command
  # @return re-raise  transport_internal_err
  def transport_err_hook(self, transport_internal_err, command, timeout):
    del command, timeout
    raise transport_internal_err


  # #function will be called when raises CommandExecutorError
  #
  # @param command_executor_err an instance of CommandExecutorError
  # @param command the current processing command
  # @param timeout timeout related to the command
  # @return re-raise  command_executor_err
  def executor_err_hook(self, command_executor_err, command, timeout):
    del command, timeout
    raise command_executor_err
