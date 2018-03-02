'''
Created on Feb 14, 2014

@author: igor
'''


from transport.ConnectionBuilder import ConnectionBuilder
from transport.IDGenerator import IDGenerator
import transport.Consts as consts


##Simple wrapper that hide all routines related to create and
#destroy connections
#
class ConnectionManager(object):


  ##constructor
  #
  def __init__(self):
    '''
    Constructor
    '''
    #@var builder
    #a member variable, holds a connection builder object
    self.builder = ConnectionBuilder(IDGenerator())


  ##create a data_connect_type connection
  #
  #@param connect params is transport.Connection.Connection_params
  #@return transport.Connection
  def create_connection(self, connect_params):
    return self.builder.build(consts.DATA_CONNECT_TYPE, connect_params)


  ##destroy connection
  #
  #@return None
  def destroy_connection(self, connection):
    connection.close()



