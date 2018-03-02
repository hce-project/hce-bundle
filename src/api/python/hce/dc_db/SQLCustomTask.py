"""
@package: dc_db
@file SQLCustomTask.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import dbi.EventObjects
import app.Utils as Utils  # pylint: disable=F0401
from dc_db.BaseTask import BaseTask
import dc_db.Constants as Constants

logger = Utils.MPLogger().getLogger()


# #process SQLCustomTask task
class SQLCustomTask(BaseTask):

  # #constructor
  #
  def __init__(self):
    super(SQLCustomTask, self).__init__()


  # #make all necessary actions to makes sql custom request
  #
  # @param sqlRequest - instance of CustomRequest class
  # @param queryCallback - function for queries execution
  # @param bdResolveFunc - pointer to resolve DB external function
  # @return CustomResponse instance
  def process(self, sqlRequest, queryCallback, bdResolveFunc):
    # variable for result
    ret = dbi.EventObjects.CustomResponse(sqlRequest.rid, sqlRequest.query, sqlRequest.dbName)
    try:
      logger.debug("!!! SQL Custom request: %s", str(sqlRequest.query))

      if sqlRequest is None:
        raise Exception("Error: request object is None")

      if sqlRequest.query is None or \
      (not isinstance(sqlRequest.query, basestring) and not isinstance(sqlRequest.query, list)):
        raise Exception("Error: wrong type of sql request param (%s)", str(type(sqlRequest)))

      if isinstance(sqlRequest.query, basestring) and sqlRequest.query == "":
        raise Exception("Error: sql request is empty string")

      if isinstance(sqlRequest.query, list) and len(sqlRequest.query) == 0:
        raise Exception("Error: input list of sql requests is empty")

      if sqlRequest.dbName is None or \
      not isinstance(sqlRequest.dbName, basestring) or \
      sqlRequest.dbName == "":
        raise Exception("Error: wrong database name '%s'", str(sqlRequest.dbName))

      dbIndex = bdResolveFunc(sqlRequest.dbName)
      if dbIndex is None:
        raise Exception("Error: there isn't '%s' database connection", str(sqlRequest.dbName))

      isSingleQuery = True
      if isinstance(sqlRequest.query, basestring):
        queries = [sqlRequest.query]
      else:
        queries = sqlRequest.query
        isSingleQuery = False

      results = []
      for query in queries:
        # execute single request
        if sqlRequest.includeFieldsNames == dbi.EventObjects.CustomRequest.SQL_BY_INDEX:
          res = queryCallback(query, dbIndex)
        elif sqlRequest.includeFieldsNames == dbi.EventObjects.CustomRequest.SQL_BY_NAME:
          res = queryCallback(query, dbIndex, Constants.EXEC_NAME)

        if res is None:
          raise Exception("Error: wrong SQL request '%s'", str(query))

        # success execution
        results.append(res)

#       logger.debug("!!! SQL Custom results: '%s' ", Utils.varDump(results))
      if isSingleQuery and len(results) > 0:
        ret.result = results[0]
      else:
        ret.result = results

    except Exception, err:
      ret.errString = str(err)
      logger.debug("!!! SQL Custom request: %s", str(err))

    return ret
