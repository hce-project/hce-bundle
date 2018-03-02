# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
FieldsSQLExpressionEvaluator Class content main functional of support
the SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER and SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR properties.

@package: app
@file FieldsSQLExpressionEvaluator.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import json
import copy
import app.Consts as APP_CONSTS
from app.Utils import varDump
from app.DateTimeType import DateTimeType
from app.Exceptions import DatabaseException
import dc_db.Constants as DB_CONSTS

class FieldsSQLExpressionEvaluator(object):

  # Constants the support names of objects in incoming json
  OBJECT_NAME_SITE = 'Site'
  OBJECT_NAME_URL = 'URL'
  # Constants using macro case
  MACRO_CASE_ORIGINAL = 0
  MACRO_CASE_UPPER = 1
  MACRO_CASE_LOWER = 2
  # Constants support castomization types
  CAST_TYPE_TO_INTEGER = 0
  CAST_TYPE_TO_STRING = 1
  CAST_TYPE_TO_DATETIME = 2
  # Other using constants
  REPLACE_MARKER = '%'
  DB_NAME = "dc_sites"

  # # Constructor
  def __init__(self):
    pass

  # # Execute method
  #
  # @param siteProperties - properties of site
  # @param dbWrapper - instance of DBTasksWrapper for work with DB
  # @param siteObj - instance of Site
  # @param urlObj - instance of URL
  # @param logger - logger instance
  # @param propertyName - property name for current execution
  # @return - dict replaced fields
  @staticmethod
  def execute(siteProperties, dbWrapper, siteObj, urlObj, logger,
              propertyName=APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER):

    logger.debug("Execute enter.... property: '" + str(propertyName) + "' is exist = " + \
                 str(True if propertyName in siteProperties else False))
    # variable for result
    ret = {}
    if dbWrapper is not None:
      propertyList = None
      if siteProperties is not None and propertyName in siteProperties:
        try:
          propertyList = json.loads(siteProperties[propertyName])
        except Exception, err:
          logger.error("Load from site property error: %s, source: %s", str(err), str(propertyName))

        if propertyList is not None:
          for propertyStruct in propertyList:
            if FieldsSQLExpressionEvaluator.OBJECT_NAME_SITE in propertyStruct:
              # Evaluate for 'Site' object
              ret = FieldsSQLExpressionEvaluator.evaluateElement(dbWrapper, logger, siteObj, DB_CONSTS.siteDict,
                                                                 propertyStruct[FieldsSQLExpressionEvaluator.\
                                                                                OBJECT_NAME_SITE])
            elif FieldsSQLExpressionEvaluator.OBJECT_NAME_URL in propertyStruct:
              # Evaluate for 'URL' object
              ret = FieldsSQLExpressionEvaluator.evaluateElement(dbWrapper, logger, urlObj, DB_CONSTS.URLTableDict,
                                                                 propertyStruct[FieldsSQLExpressionEvaluator.\
                                                                                OBJECT_NAME_URL])
            else:
              logger.error("Not support name of object in inputted json")

    return ret


  # # Evaluate one element
  #
  # @param dbWrapper - instance of DBTasksWrapper for work with DB
  # @param logger - logger instance
  # @param obj - instance object for evaluate
  # @param fieldsDict - dict field names in Object and DB
  # @param objPropertyStruct - property structure of object for update
  # @return - dict replaced fields
  @staticmethod
  def evaluateElement(dbWrapper, logger, obj, fieldsDict, objPropertyStruct):
    logger.debug('evaluateElement enter.... \nobj: ' + varDump(obj) + '\nfieldsDict: ' + str(fieldsDict) + \
                  '\nobjPropertyStruct: ' + str(objPropertyStruct))
    # variable for result
    ret = {}
    if obj is not None:
      objFields = {}
      for key, value in obj.__dict__.items():
        if isinstance(value, basestring):
          # objFields[key.upper()] = MySQLdb.escape_string(str(value))  # pylint: disable=E1101
          objFields[key.upper()] = dbWrapper.dbTask.dbConnections[DB_CONSTS.PRIMARY_DB_ID].escape_string(str(value))
        else:
          objFields[key.upper()] = value

      logger.debug('objFields: %s', str(objFields))

      for fieldName, fieldValue in objPropertyStruct.items():
        logger.debug('fieldName: %s, fieldValue: %s', str(fieldName), str(fieldValue))
        for sqlExpression, valueType in fieldValue.items():
          logger.debug('sqlExpression: %s, valueType: %s', str(sqlExpression), str(valueType))
          sqlQuery = 'SELECT ' + \
          FieldsSQLExpressionEvaluator.macroReplace(sqlExpression, objFields,
                                                    FieldsSQLExpressionEvaluator.REPLACE_MARKER,
                                                    case=1)
          logger.debug("sqlQuery: " + str(sqlQuery))
          affectDB = dbWrapper.affect_db
          dbWrapper.affect_db = True
          customResponse = None
          try:
            customResponse = dbWrapper.customRequest(sqlQuery, FieldsSQLExpressionEvaluator.DB_NAME)
          except DatabaseException, err:
            logger.error("Bad query: " + str(sqlQuery))

          dbWrapper.affect_db = affectDB
          logger.debug("customResponse: " + str(customResponse))
          if customResponse is not None and len(customResponse) > 0 and len(customResponse[0]) > 0:
            result = None
            try:
              if valueType == FieldsSQLExpressionEvaluator.CAST_TYPE_TO_INTEGER:
                result = int(customResponse[0][0])
              elif valueType == FieldsSQLExpressionEvaluator.CAST_TYPE_TO_STRING:
                result = str(customResponse[0][0])  # pylint: disable=R0204
              elif valueType == FieldsSQLExpressionEvaluator.CAST_TYPE_TO_DATETIME:
                dt = DateTimeType.parse(customResponse[0][0])
                if dt is not None:
                  result = dt.strftime("%Y-%m-%d %H:%M:%S")
              else:
                logger.debug('Unknown type for cast: ' + str(valueType))

            except Exception, err:
              logger.error("Customization result by type failed, error: %s", str(err))

            logger.debug('result after cast: ' + str(result) + ' type: ' + str(type(result)))
            # Update field value
            if result is not None:
              for fieldObjName, fieldDBName in fieldsDict.items():
                if fieldDBName == fieldName and hasattr(obj, fieldObjName):
                  logger.debug("Found attribute '" + str(fieldObjName) + "' in object...")
                  ret[fieldObjName] = result

    return ret


  # # macroReplace makes macroreplacement in incoming pattern string by string from values dict
  #
  # @param pattern - incoming pattern string
  # @param values - dict with incoming old substrings (values.keys) and new substrings (values.values)
  # @param marker - additional prefix+suffix for values.keys
  # @param case - 0 - don not change name case, 1 - change to upper, 2 - change to lower
  # @return replacemented string
  @staticmethod
  def macroReplace(pattern, values, marker, case=MACRO_CASE_ORIGINAL):
    ret = copy.copy(pattern)
    for key in values:
      if values[key] is not None:
        if case == FieldsSQLExpressionEvaluator.MACRO_CASE_UPPER:
          rkey = key.upper()
        elif case == FieldsSQLExpressionEvaluator.MACRO_CASE_LOWER:
          rkey = key.lower()
        else:
          rkey = key
        ret = ret.replace(marker + rkey + marker, "'" + str(values[key]) + "'" if isinstance(values[key], basestring) \
                          else str(values[key]))

    return ret


  # # evaluate PDate using 'PDATE_TIME' site property
  #
  # @param siteProperties - properties of site
  # @param dbWrapper - instance of DBTasksWrapper for work with DB
  # @param urlObj - instance of URL
  # @param logger - logger instance
  # @param defaultPubdateValue - default value of pubdate
  # @return pubdate value
  @staticmethod
  def evaluatePDateTime(siteProperties, dbWrapper, urlObj, logger, defaultPubdateValue=None):
    logger.debug("evaluatePDateTime enter.... property: '" + str(APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME) + \
                 "' is exist = " + \
                 str(True if APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME in siteProperties else False))

    localUrlObj = copy.deepcopy(urlObj)
    # variable for result
    ret = defaultPubdateValue
    propertyList = None
    if siteProperties is not None and APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME in siteProperties:
      try:
        propertyList = json.loads(siteProperties[APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME])
        logger.debug("propertyList: " + varDump(propertyList) + " type: " + str(type(propertyList)))
      except Exception, err:
        logger.error("Load from site property '%s' has error: %s",
                     str(APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME), str(err))

      if propertyList is not None:
        for propertyStruct in propertyList:
          if "pattern" in propertyStruct and "value" in propertyStruct:
            pattern = propertyStruct["pattern"]
            value = propertyStruct["value"]

            logger.debug("pattern: " + str(pattern))
            logger.debug("value: " + str(value))
            logger.debug("localUrlObj.url: " + str(localUrlObj.url))
            if localUrlObj.pDate is None:
              localUrlObj.pDate = defaultPubdateValue

            # Check pattern apply to url
            if re.search(pattern, localUrlObj.url, re.UNICODE) is not None:
              objPropertyStruct = {DB_CONSTS.URLTableDict['pDate']:\
                                  {value:FieldsSQLExpressionEvaluator.CAST_TYPE_TO_STRING}}
              # Evaluate for 'URL' object
              resDict = FieldsSQLExpressionEvaluator.evaluateElement(dbWrapper, logger, localUrlObj, DB_CONSTS.URLTableDict,
                                                                     objPropertyStruct)
              logger.debug("!!! evaluatePDateTime resDict: %s", str(resDict))
              if "pDate" in resDict:
                rawDate = resDict["pDate"]
                if rawDate.isdigit():
                  logger.debug("!!! Return numeric value: " + str(rawDate))
                  d = DateTimeType(int(rawDate))
                  ret = d.getString()
                else:
                  logger.debug("!!! Return string value: " + str(rawDate))
                  # ret = rawDate
                  dt = DateTimeType.parse(rawDate, True, logger, False)
                  if dt is not None:
                    ret = dt.strftime("%Y-%m-%d %H:%M:%S")
                  else:
                    ret = rawDate
          else:
            logger.error("Not found mandatory fields for property '%s'", \
                         str(APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME))

    logger.debug("!!! evaluatePDateTime ret: %s", str(ret))

    return ret
