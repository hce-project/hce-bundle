# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
FieldsSQLExpressionEvaluator Class content main functional of support
the SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER and SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR properties.

@package: app
@file FieldsSQLExpressionEvaluator.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import json
from app.Exceptions import DatabaseException
from app.Utils import varDump
import app.Utils as Utils


logger = Utils.MPLogger().getLogger()


class ContentEvaluator(object):

  # Constants the support names of objects in incoming json
  PROPERTY_WHERE_NAME = 'WHERE'  # name of a content, can be "RAW" at least;
  PROPERTY_WHAT_NAME = 'WHAT'  # regular expression defines what to replace;
  PROPERTY_WITH_NAME = 'WITH'  # string to replace with;
  PROPERTY_CONDITION_NAME = 'CONDITION'  # optional, the SQL expression to be executed with urls_<site_id> table;

  PROPERTY_WHERE_VALUE_RAW = 'RAW'

  # Other using constants
  DB_NAME = "dc_urls"
  QUERY_TEMPALATE = "SELECT * from urls_%s WHERE %s"

  # Constants of error messages
  ERROR_MSG_BAD_FORMAT = "Wrong format of input json: %s"
  ERROR_MSG_BAD_TYPE = "Wrong type of parameter '%s'"
  ERROR_MSG_BAD_DBWRAPPER = "DBWrapper instance is None"
  ERROR_MSG_MISSED_PARAMETER = "Missed parameter '%s'"
  ERROR_MSG_WRONG_PARAMETER = "Parameter '%s' has not support value '%s'"

  # # Constructor
  def __init__(self):
    pass


  # # Execute sql expression
  #
  # @param dbWrapper - DBWrapper instance
  # @param siteId - site ID
  # @param sqlExpression - sql expression
  # @return boolean result of execution
  @staticmethod
  def executeSqlExpression(dbWrapper, siteId, sqlExpression):
    # variable for result
    ret = False
    try:
      if not isinstance(sqlExpression, basestring):
        raise Exception(ContentEvaluator.ERROR_MSG_BAD_TYPE % ContentEvaluator.PROPERTY_CONDITION_NAME)

      if dbWrapper is None:
        raise Exception(ContentEvaluator.ERROR_MSG_BAD_DBWRAPPER)

      logger.debug('sqlExpression: %s', str(sqlExpression))
      sqlQuery = ContentEvaluator.QUERY_TEMPALATE % (str(siteId), str(sqlExpression))

      logger.debug("sqlQuery: " + str(sqlQuery))
      affectDB = dbWrapper.affect_db
      dbWrapper.affect_db = True
      customResponse = None
      try:
        customResponse = dbWrapper.customRequest(sqlQuery, ContentEvaluator.DB_NAME)
      except DatabaseException, err:
        logger.error("Bad query: " + str(sqlQuery))

      dbWrapper.affect_db = affectDB
      logger.debug("customResponse: " + str(customResponse))

      if customResponse is not None and len(customResponse) > 0 and len(customResponse[0]) > 0:
        ret = True

    except Exception, err:
      logger.error(str(err))

    return ret


  # # Execute replace content
  #
  # @param dbWrapper - DBWrapper instance
  # @param siteId - site ID
  # @param propertyString - property json string with rules for replace
  # @param contentData - content data for replace
  # @return content data after replacement
  @staticmethod
  def executeReplace(dbWrapper, siteId, propertyString, contentData):
    # variable for result
    ret = contentData
    try:
      propertyObjs = json.loads(propertyString)

      logger.debug("propertyObj: %s", varDump(propertyObjs))

      if not isinstance(propertyObjs, list):
        raise Exception(ContentEvaluator.ERROR_MSG_BAD_FORMAT % varDump(propertyObjs))

      for propertyObj in propertyObjs:
        try:
          if ContentEvaluator.PROPERTY_WHERE_NAME not in propertyObj:
            raise Exception(ContentEvaluator.ERROR_MSG_MISSED_PARAMETER % str(ContentEvaluator.PROPERTY_WHERE_NAME))
          else:
            if not isinstance(propertyObj[ContentEvaluator.PROPERTY_WHERE_NAME], basestring):
              raise Exception(ContentEvaluator.ERROR_MSG_BAD_TYPE % ContentEvaluator.PROPERTY_WHERE_NAME)

          if ContentEvaluator.PROPERTY_WHAT_NAME not in propertyObj:
            raise Exception(ContentEvaluator.ERROR_MSG_MISSED_PARAMETER % str(ContentEvaluator.PROPERTY_WHAT_NAME))
          else:
            if not isinstance(propertyObj[ContentEvaluator.PROPERTY_WHAT_NAME], basestring):
              raise Exception(ContentEvaluator.ERROR_MSG_BAD_TYPE % ContentEvaluator.PROPERTY_WHAT_NAME)

          if ContentEvaluator.PROPERTY_WITH_NAME not in propertyObj:
            raise Exception(ContentEvaluator.ERROR_MSG_MISSED_PARAMETER % str(ContentEvaluator.PROPERTY_WITH_NAME))
          else:
            if not isinstance(propertyObj[ContentEvaluator.PROPERTY_WITH_NAME], basestring):
              raise Exception(ContentEvaluator.ERROR_MSG_BAD_TYPE % ContentEvaluator.PROPERTY_WITH_NAME)

          if ContentEvaluator.PROPERTY_CONDITION_NAME in propertyObj and \
            not isinstance(propertyObj[ContentEvaluator.PROPERTY_CONDITION_NAME], basestring):
            raise Exception(ContentEvaluator.ERROR_MSG_BAD_TYPE % ContentEvaluator.PROPERTY_CONDITION_NAME)

          if propertyObj[ContentEvaluator.PROPERTY_WHERE_NAME] == ContentEvaluator.PROPERTY_WHERE_VALUE_RAW:
            ret = ContentEvaluator.executeReplaceRawContent(
                dbWrapper=dbWrapper,
                siteId=siteId,
                pattern=propertyObj[ContentEvaluator.PROPERTY_WHAT_NAME],
                repl=propertyObj[ContentEvaluator.PROPERTY_WITH_NAME],
                sqlExpression=propertyObj[ContentEvaluator.PROPERTY_CONDITION_NAME],
                contentData=contentData)
          else:
            raise Exception(ContentEvaluator.ERROR_MSG_WRONG_PARAMETER % \
                            (str(ContentEvaluator.PROPERTY_WHERE_NAME),
                             str(propertyObj[ContentEvaluator.PROPERTY_WHERE_NAME])))

        except Exception, err:
          logger.error(str(err))

    except Exception, err:
      logger.error(str(err))

    return ret


  # # Execute replace raw content
  #
  # @param dbWrapper - DBWrapper instance
  # @param siteId - site ID
  # @param pattern - pattern for regular expression
  # @param repl - result string to replace with
  # @param sqlExpression - sql expression
  # @param contentData - content data for replace
  # @return content data after replacement
  @staticmethod
  def executeReplaceRawContent(dbWrapper, siteId, pattern, repl, sqlExpression, contentData):
    # variable for result
    ret = contentData
    try:
      if sqlExpression == "":
        resSqlExpression = True
      else:
        resSqlExpression = ContentEvaluator.executeSqlExpression(dbWrapper, siteId, sqlExpression)

      logger.debug("resSqlExpression: %s", str(resSqlExpression))
      if resSqlExpression:
        ret = re.sub(pattern, repl, contentData)

      logger.debug("before replace len= %s, after replace len = %s", str(len(contentData)), str(len(ret)))
    except Exception, err:
      logger.error(str(err))

    return ret
