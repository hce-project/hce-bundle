'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from app.Utils import JsonSerializable
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


class CustomRequest(JsonSerializable):

  # #constructor
  # initialize fields
  # @param rid - request id
  # @param query - custom query string
  # @param dbName - db name
  #
  SQL_BY_INDEX = 0
  SQL_BY_NAME = 1

  def __init__(self, rid, query, dbName):
    super(CustomRequest, self).__init__()
    self.rid = rid
    self.query = query
    self.dbName = dbName
    self.includeFieldsNames = self.SQL_BY_INDEX



class CustomResponse(JsonSerializable):

  # #constructor
  # initialize fields
  # @param rid - request id
  # @param query - custom query string
  # @param dbName - db name
  #
  def __init__(self, rid, query, dbName):
    super(CustomResponse, self).__init__()
    self.rid = rid
    self.query = query
    self.dbName = dbName
    self.result = tuple()
    self.errString = None
