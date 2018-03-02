"""
Created on Mar 17, 2015

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import copy
import time
import datetime
import dbi.EventObjects
from app.DateTimeType import DateTimeType
from app.Utils import varDump # pylint: disable=W0611
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


class Filters(object):

  DB_NAME = "dc_sites"
  REPLACE_MARKER = '%'
  ACTION_MULTIPLE = -1
  FILTER_SPLIT_PATTERN = '\r\n'

  FILTER_NAME_PATTERN = "Pattern"
  FILTER_NAME_SUBJECT = "Subject"
  FILTER_NAME_OP_CODE = "OperationCode"
  FILTER_NAME_STAGE = "Stage"
  FILTER_NAME_ACTION = "Action"
  FILTER_NAME_GROUP = "Group_Id"
  FILTER_NAME_STATE = "State"

  STAGE_COLLECT_URLS = 0
  STAGE_BEFORE_DOM_PRE = 1
  STAGE_AFTER_DOM_PRE = 2
  STAGE_AFTER_DOM = 3
  STAGE_AFTER_PROCESSOR = 4
  STAGE_ALL = 5
  STAGE_COLLECT_URLS_PROTOCOLS = 6
  STAGE_BEFORE_PROCESSOR = 7
  STAGE_REDIRECT_URL = 8

  # Constants select stage for STAGE_BEFORE_DOM_PRE
  SELECT_SUBJECT_RAW_CONTENT = 'RAW_CONTENT'
  SELECT_SUBJECT_HEADERS_ALL = 'HEADERS_ALL'
  SELECT_SUBJECT_LAST_MODIFIED = 'LAST_MODIFIED'

  LOGIC_OR = 0
  LOGIC_AND = 1

  # Constants for operation codes, implements in Filters.filterAll method body
  OC_RE = 0
  OC_EQ = 1
  OC_NOTEQ = 2
  OC_EQLESS = 3
  OC_EQMORE = 4
  OC_LESS = 5
  OC_MORE = 6
  OC_SQLE = 7

  # States of filters
  STATE_DISABLE = 0
  STATE_ENABLE = 1

  MACRO_CASE_ORIGINAL = 0
  MACRO_CASE_UPPER = 1
  MACRO_CASE_LOWER = 2

  # #Constructor
  #
  # @param filters - incoming filters, makes deepcopy inside class constructor
  # @param dbTaskWrapper - db-task wrapper (not used now)
  # @param siteId - used with db-task wrapper (not used now)
  # @param readMode - read mode
  # @param fields - dictionary values of support macro names ('PDATE' and other)
  # @param opCode - operation code
  # @param stage - stage of apply filter
  # @param selectSubject - select subject use select from DB
  def __init__(self, filters, dbTaskWrapper=None, siteId=None, readMode=0, fields=None, opCode=None, stage=None,
               selectSubject=None):
    self.patternCache = {}
    self.reFlags = re.M | re.U
    self.dbTaskWrapper = dbTaskWrapper
    self.siteId = siteId
    self.readMode = readMode
    self.fields = fields
    self.stage = stage

    self.filters = []

    if filters is not None:
      # if filters is not None istantiate self.filters directly
      self.readFiltersFromDict(filters, opCode, stage, selectSubject)
    # #else:
    # else fill self.filters from database, using dbTask and siteId params (make SiteStatusTask request)
    # Look CrawlerTask.readSiteFromDB method, return Site.filters field and parse it
    # #self.filters = []
    if dbTaskWrapper is not None and siteId is not None:
      self.readFiltersFromDB(dbTaskWrapper, siteId, readMode, opCode, stage, selectSubject)


  # # Read filters from dict generates internal filters from incoming filters list
  #
  # @param filters - incoming filters as list of dc.EventObjects.SiteFilter objects
  # @param opCode - operation code for select condition
  # @param stage - stage for select condition
  # @param selectSubject - select subject use select from DB
  # @return - None
  def readFiltersFromDict(self, filters, opCode=None, stage=None, selectSubject=None):
    self.filters = []
    for localFilter in filters:
      if opCode is not None and int(opCode) != int(localFilter.opCode):
        continue
      if stage is not None and int(stage) != int(localFilter.stage):
        continue

      if localFilter.state == 0:
        logger.debug("Filter: '" + str(localFilter.pattern) + "' skipped as DISABLE")
        continue

#       logger.debug('opCode: ' + str(opCode) + ' type: ' + str(type(opCode)))
#       logger.debug('stage: ' + str(stage) + ' type: ' + str(type(stage)))
#       logger.debug('localFilter.stage: ' + str(localFilter.stage) + ' type: ' + str(type(localFilter.stage)))
#       logger.debug('selectSubject: ' + str(selectSubject) + ' type: ' + str(type(selectSubject)) + \
#                    ' localFilter.subject: ' + str(localFilter.subject) + ' type: ' + str(type(localFilter.subject)))

      if int(localFilter.stage) == self.STAGE_BEFORE_DOM_PRE and \
        selectSubject is not None and len(localFilter.subject) > 0 and \
        selectSubject != localFilter.subject:
        logger.debug('!!!! Skipped !!!!! ')
        continue

      for pattern in localFilter.pattern.split(self.FILTER_SPLIT_PATTERN):
        localDict = {}
        localDict[self.FILTER_NAME_PATTERN] = pattern
        if localFilter.pattern.find(self.REPLACE_MARKER) == -1:
  #         logger.debug('Cache initialize key: ' + str(localFilter.pattern + str(self.reFlags)) + ' pattern: ' + \
  #                      str(localFilter.pattern))
          self.patternCache[str(localFilter.pattern + str(self.reFlags))] = re.compile(localFilter.pattern, self.reFlags)
        localDict[self.FILTER_NAME_SUBJECT] = localFilter.subject
        localDict[self.FILTER_NAME_OP_CODE] = localFilter.opCode
        localDict[self.FILTER_NAME_STAGE] = localFilter.stage
        localDict[self.FILTER_NAME_ACTION] = localFilter.action
        localDict[self.FILTER_NAME_GROUP] = localFilter.groupId
        localDict[self.FILTER_NAME_STATE] = localFilter.state
        self.filters.append(localDict)


  # #readFiltersFromDB read filters from DB (using SQLCustom request to db-task) for specific site
  #
  # @param dbTaskWrapper - db-task wrapper
  # @param siteId - site Id
  # @param readMode - read mode
  # @param opCode - operation code for select condition
  # @param stage - stage for select condition
  # @param selectSubject - select subject use select from DB
  def readFiltersFromDB(self, dbTaskWrapper, siteId, readMode, opCode=None, stage=None, selectSubject=None):
    # SQL_SELECT_TEMPLATE = "SELECT `Pattern`, `Subject`, `OperationCode`, `Stage`, `Action`, `Group_Id` " + \
    # "FROM `sites_filters` WHERE `Mode`='%s' AND `State`='1' AND `Site_Id`='%s'"
    SQL_SELECT_TEMPLATE = "SELECT * FROM `sites_filters` WHERE `Mode`='%s' AND `State`='1' AND `Site_Id`='%s'"
    query = SQL_SELECT_TEMPLATE % (str(readMode), str(siteId))

    if opCode is not None:
      query += (" AND `OperationCode`='%s'" % str(opCode))

    if stage is not None:
      query += (" AND `Stage`='%s'" % str(stage))

    if selectSubject is not None and int(stage) == self.STAGE_BEFORE_DOM_PRE:
      query += (" AND `Subject`='%s'" % str(selectSubject))

    logger.debug(">>> Filter start SQL Req: " + str(query))
    affectDB = dbTaskWrapper.affect_db
    dbTaskWrapper.affect_db = True
    customResponse = dbTaskWrapper.customRequest(query, self.DB_NAME, dbi.EventObjects.CustomRequest.SQL_BY_NAME)
    dbTaskWrapper.affect_db = affectDB
    logger.debug(">>> Filter end SQL Req: " + str(customResponse))
    if customResponse is not None:
      for i in xrange(len(customResponse)):
#         logger.debug("customResponse[%s] = %s", str(i), str(customResponse[i]))
        if customResponse[i] is not None:
          patterns = customResponse[i][self.FILTER_NAME_PATTERN].split(self.FILTER_SPLIT_PATTERN)
#           logger.debug("patterns: " + str(patterns))
          for pattern in patterns:
            elem = copy.copy(customResponse[i])
            elem[self.FILTER_NAME_PATTERN] = pattern
            self.filters.append(elem)

#       logger.debug("customResponse self.filters: " + str(self.filters))


  # #macroReplace makes macroreplacement in incoming pattern string by string from values dict
  #
  # @param pattern - incoming pattern string
  # @param values - dict with incoming old substrings (values.keys) and new substrings (values.values)
  # @param marker - additional prefix+suffix for values.keys
  # @param case - 0 - don not change name case, 1 - change to upper, 2 - change to lower
  # @return replacemented string
  def macroReplace(self, pattern, values, marker, case=MACRO_CASE_ORIGINAL):
#     logger.info('>>> macroReplace  values: ' + str(values) + ' pattern: ' + str(pattern))

    ret = copy.copy(pattern)
    for key in values:
      if values[key] is not None:
        if case == self.MACRO_CASE_UPPER:
          rkey = key.upper()
        elif case == self.MACRO_CASE_LOWER:
          rkey = key.lower()
        else:
          rkey = key
        ret = ret.replace(marker + rkey + marker, "'" + str(values[key]) + "'" if isinstance(values[key], basestring) \
                          else str(values[key]))

    return ret


  # #comparing values comparing method
  #
  # @param value1 - comparing value1
  # @param value2 - comparing value2
  # @param OCType - operation type
  # @return bool result of values comparing
  def comparing(self, value1, value2, OCType):
    ret = False
    # logger.debug("Value1:\n%s\nValue2:\n%s\nOCType:\n%s", str(value1), str(value2), str(OCType))
#     logger.debug("Value1:\n%s\nValue2:\n%s\nOCType:\n%s", str(value1[:255] + ' . . . '), str(value2), str(OCType))
    try:
      if OCType == self.OC_RE:
        # if str(value2 + str(self.reFlags)) in self.patternCache:
        #  pattern = self.patternCache[str(value2 + str(self.reFlags))]
        #  logger.debug("Use pattern '" + str(value2 + str(self.reFlags)) + "' from cache")
        # else:
        # #pattern = re.compile(value2, self.reFlags)
        # logger.debug("Use pattern '" + str(value2 + str(self.reFlags)) + "' without cache")
        # logger.debug('patternCache: ' + str(self.patternCache.keys()))
        # #if pattern.match(value1, self.reFlags) is not None:
        # #  ret = True

        if re.search(value2, value1, self.reFlags) is not None:
          ret = True

      elif OCType == self.OC_EQ:
        ret = (int(value1) == int(value2))
      elif OCType == self.OC_NOTEQ:
        ret = (int(value1) != int(value2))
      elif OCType == self.OC_EQLESS:
        ret = (int(value1) <= int(value2))
      elif OCType == self.OC_EQMORE:
        ret = (int(value1) >= int(value2))
      elif OCType == self.OC_LESS:
        ret = (int(value1) < int(value2))
      elif OCType == self.OC_MORE:
        ret = (int(value1) > int(value2))
      elif OCType == self.OC_SQLE:
        ret = self.checkSqlExpression(value2, None, self.fields)  # value2 content value of 'Pattern'
    except ValueError as exp:
      logger.debug(">>> Value error = " + str(exp))
    except Exception, err:
      logger.debug(">>> Common exception, OCType = " + str(OCType) + ", val1 = " + str(value1) + ", val2 = " \
                    + str(value2) + ", error: " + str(err))
#     logger.debug('comparing ret = ' + str(ret))
    return ret


  def searchFiltersWithStage(self, stage):
    ret = 0
    if self.filters is not None:
      for localFilter in self.filters:
        if localFilter[self.FILTER_NAME_STAGE] == stage:
          ret += 1
    return ret


  # # Check exists any filters with stage
  #
  # @param stage - stage of filtes
  # @return True - if exist filter with this stage, otherwise False
  def isExistStage(self, stage):
    # variable for result
    ret = False
    if self.filters is not None:
      for localFilter in self.filters:
        if localFilter[self.FILTER_NAME_STAGE] == stage:
          ret = True
          break

    return ret


  # # Check exists any filters with stage
  #
  # @param stage - stage of filters
  # @param opCode - operation code
  # @return True - if exist filter with this stage, otherwise False
  def isExist(self, stage, opCode):
    # variable for result
    ret = False
    if self.filters is not None:
      for localFilter in self.filters:
        if int(localFilter[self.FILTER_NAME_STAGE]) == int(stage) and \
          int(localFilter[self.FILTER_NAME_OP_CODE]) == int(opCode):
          ret = True
          break

    return ret


  # #filterAll method applyes all filters and return result
  #
  # @param stage - current stage, available stages looks above
  # @param value - replacement values (dict)
  # @param logic -
  # @param subject -
  # @param excludeIncludeMode - None - means any, >0 - include, else - exclude
  # @return bool result of values comparing
  def filterAll(self, stage, value, logic=LOGIC_AND, subject=None, excludeIncludeMode=None):
#     logger.debug('filterAll() enter...  filters count = ' + str(len(self.filters)) + '\nstage = ' + str(stage) + \
#                  # '\nvalue: ' + str(value) + \
#                  '\nlogic: ' + str(logic) + \
#                  '\nsubject: ' + str(subject[:255]) + \
#                  '\nexcludeIncludeMode: ' + str(excludeIncludeMode))
    if stage is None:
      stage = self.stage

    ret = []
#     localGroupDict = {}
    resValues = []
    for localFilter in self.filters:
      if int(localFilter[self.FILTER_NAME_STATE]) == self.STATE_ENABLE and \
      (stage == self.STAGE_ALL or localFilter[self.FILTER_NAME_STAGE] == self.STAGE_ALL or \
      localFilter[self.FILTER_NAME_STAGE] == stage) and ((excludeIncludeMode is None) or\
                                                         (int(excludeIncludeMode) == int(localFilter["Action"]))):
#         logger.debug('Use filter: %s', varDump(localFilter))

        if subject is not None and (localFilter[self.FILTER_NAME_SUBJECT] == "" or \
                                    localFilter[self.FILTER_NAME_SUBJECT] == self.SELECT_SUBJECT_RAW_CONTENT or \
                                    localFilter[self.FILTER_NAME_SUBJECT] == self.SELECT_SUBJECT_HEADERS_ALL or \
                                    localFilter[self.FILTER_NAME_SUBJECT] == self.SELECT_SUBJECT_LAST_MODIFIED):
          localStage = subject
        else:
          localStage = localFilter[self.FILTER_NAME_SUBJECT]

        #   make macroreplacement localFilter["Subject"] by correspond value from value param dict
        #   apply localFilter["Patter"] for previously getted result (result of macroreplacement)
        if localFilter[self.FILTER_NAME_PATTERN] is not None:
          localPattern = self.macroReplace(localFilter[self.FILTER_NAME_PATTERN], value, self.REPLACE_MARKER)

#           logger.info('>>> filterAll  macroReplace localPattern: ' + str(localPattern))
          localPattern = self.getGmtTime(localPattern, logger)
#           logger.info('>>> filterAll  getGmtTime localPattern: ' + str(localPattern))
#           logger.info('>>> filterAll  logic = ' + str(logic))

          if logic == self.LOGIC_OR:
          # Return ret = [x1, x2, ... xN] where (xN = +/- localFilter["Action"] value) of applying pattern
          # and +/- depend on corresponds filter for own "Pattern" or not.
          # for example:
          # we have 3 applying filters with localFilter["Action"] = {3, 4, 5} correspondingly,
          # 1th filter doesn't correspond own localFilter["Pattern"] , 2th and 3th - correspond
          # that we return ret = [-3, 4, 5]
            # if self.comparing(localStage, localPattern, localFilter[self.FILTER_NAME_OP_CODE]):
            #  localRes = localFilter[self.FILTER_NAME_ACTION]
            # else:
            #  localRes = localFilter[self.FILTER_NAME_ACTION] * self.ACTION_MULTIPLE

            localRes = int(self.comparing(localStage, localPattern, localFilter[self.FILTER_NAME_OP_CODE]))

#             logger.info('>>> localRes: ' + str(localRes))

#             if localFilter[self.FILTER_NAME_GROUP] in localGroupDict:
#               logger.info('>>> localFilter[self.FILTER_NAME_GROUP]: ' + str(localFilter[self.FILTER_NAME_GROUP]))
#               if localGroupDict[localFilter[self.FILTER_NAME_GROUP]] > 0:
#                 localGroupDict[localFilter[self.FILTER_NAME_GROUP]] = localRes
#             else:
#               localGroupDict[localFilter[self.FILTER_NAME_GROUP]] = localRes
#             # set result values
#             ret = localGroupDict.values()

            # add by alexv 22.06.2017
            resValues.append(localRes)
            ret = resValues

          elif logic == self.LOGIC_AND:
          # If all applying filters correspond own "Pattern"s that ret = [True], else ret = [False]
            if self.comparing(localStage, localPattern, localFilter[self.FILTER_NAME_OP_CODE]):
              ret = [True]
            else:
              ret = [False]
              break

    return ret


  # Method found value in existing filters ([self.FILTER_NAME_ACTION] field)
  # return bool result of finding
  def isExistInActions(self, value):
    ret = False
    for localFilter in self.filters:
      if localFilter is not None and localFilter[self.FILTER_NAME_ACTION] == value:
        ret = True
        break
    return ret


  # #Get GMT time from macros as string
  #
  # @param localPattern - input pattern as string
  # @param loggerIns - instance of logger
  # @return value of time as string
  def getGmtTime(self, localPattern, loggerIns):
    try:
      d = {"SHORTYEAR":"y", "YEAR":"Y", "MONTH":"m", "DAY":"d", "HOUR":"H", "MINUTE":"M", "SECOND":"S"}
      regex = re.compile("%@(SHORTYEAR|YEAR|MONTH|DAY|HOUR|MINUTE|SECOND)\\(([\\+|\\-]\\d{1,2})\\)%")
      matchArray = regex.findall(localPattern)

      for i in matchArray:
        ii = time.strftime("%" + d[i[0]], time.gmtime(time.time() + datetime.timedelta(hours=(+int(i[1]))).seconds))
        localPattern = localPattern.replace("%@" + i[0] + "(" + i[1] + ")%", ii)
    except Exception, err:
      loggerIns.error(str(err))

    return localPattern


  # #Check Sql expression operation
  #
  # @param value - sql expression
  # @param pubdate - date extracted on crawler
  # @param fields - dictionary values of support macro names ('PDATE' and other)
  # @return True if success, otherwise False
  def checkSqlExpression(self, pattern, pubdate=None, fields=None):
    # variable for result
    ret = False

    if self.dbTaskWrapper is None:
      ret = True
    else:
      if fields is None:
        logger.debug('pattern: ' + str(pattern))
        logger.debug('pubdate: ' + str(pubdate))

        if pubdate is not None:
          dt = DateTimeType.parse(pubdate, True, logger, False)
          if dt is not None:
            dateStr = "'" + dt.strftime("%Y-%m-%d %H:%M:%S") + "'"
            localPattern = self.macroReplace(pattern, {'PDATE':dateStr}, self.REPLACE_MARKER)
            logger.debug('localPattern: ' + str(localPattern))

            sqlQuery = "SELECT * FROM `sites_filters` WHERE `Mode`='%s' AND `State`='1' AND `Site_Id`='%s'" % \
            (str(self.readMode), str(self.siteId))

            if localPattern:
              sqlQuery += " AND " + localPattern

            logger.debug("sqlQuery: " + str(sqlQuery))

            customResponse = self.dbTaskWrapper.customRequest(sqlQuery, self.DB_NAME)
            logger.debug("customResponse: " + str(customResponse))
            if customResponse is not None:
              for elem in customResponse:
                if elem is not None:
                  logger.debug("elem: " + str(elem))

              ret = bool(len(customResponse) > 0)
      else:
        pattern = self.macroReplace(pattern, fields, self.REPLACE_MARKER, case=1)
        sqlQuery = 'SELECT ' + pattern
        logger.debug("sqlQuery: " + str(sqlQuery))
        affectDB = self.dbTaskWrapper.affect_db
        self.dbTaskWrapper.affect_db = True
        customResponse = self.dbTaskWrapper.customRequest(sqlQuery, self.DB_NAME)
        self.dbTaskWrapper.affect_db = affectDB
        logger.debug("customResponse: " + str(customResponse))
        if customResponse is not None and len(customResponse) > 0 and len(customResponse[0]) > 0 and \
          int(customResponse[0][0]) > 0:
          ret = True

    return ret
