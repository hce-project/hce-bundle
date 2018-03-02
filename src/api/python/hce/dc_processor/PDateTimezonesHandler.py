# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
PDateTimezonesHandler Class content main functional calculate offset use timezones.

@package: dc_processor
@file PDateTimezonesHandler.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import datetime
import re
import time
import json
from app.DateTimeType import DateTimeType


# # Class PDateTimezonesProperties for save properties data
class PDateTimezonesProperties(object):
  # #Constructor
  def __init__(self, pattern, zoneTo, zoneFrom, condition):
    self.pattern = pattern
    self.zoneTo = zoneTo
    self.zoneFrom = zoneFrom
    self.condition = condition


# # Class DateTimeType for extract data
#
class PDateTimezonesHandler(object):
  # #Constans used in class
  PROPERTY_OPTION_PATTERN = 'pattern'
  PROPERTY_OPTION_ZONE_TO = 'zone_to'
  PROPERTY_OPTION_ZONE_FROM = 'zone_from'
  PROPERTY_OPTION_CONDITION = 'condition'
  # #Spetial value for 'zone_to'
  VALUE_ZONE_FROM_LOCAL = 'LOCAL'
  # #Constant of error messages
  ERROR_BAD_PARAMETER = 'Bad parameter'
  ERROR_LOAD_PROPERTIES = 'Load properties fail'
  ERROR_MANDATORY_FIELDS = 'Missed some mandatory fields'
  ERROR_WRONG_CONDITION = "Wrong '" + PROPERTY_OPTION_CONDITION + "' value"
  # #Constants used in class
  USE_PATTERN = 'Use pattern'

  patternListTimezoneOffset = [r'(?P<op>[+−-])(?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9])',
                               r'(?P<op>[+−-])(?P<hour>[0-9][0-9])(?P<min>[0-9][0-9])',
                               r'(?P<op>[+-])(?P<hour>\d{1,2})',
                               r'(?P<hour>[−][0-9][0-9])']
  # #Constants
  TRANSFORMATION_ALWAYS = 0  # always perform transformation
  TRANSFORMATION_TIMEZONE_DEFINED = 1  # only if source date has timezone defined;
  TRANSFORMATION_NO_TIMEZONE_DEFINED = 2  # only if source date has no timezone defined;
  TRANSFORMATION_TIMEZONE_EQUAL = 3  # only if the source date timezone equal with zone_from value;
  TRANSFORMATION_TIMEZONE_NOT_EQUAL = 4  # only if the source date timezone is not equal with zone_from value;
  # #Constructor
  def __init__(self):
    pass

  # #Loag properties json string
  #
  # @param propertyString - input property string
  # @param logger - instance of logger for log if necessary
  # @return list of PDateTimezonesProperties instancies
  @staticmethod
  def loadProperties(propertyString, logger=None):
    # variable for result
    properties = []
    try:
      obj = json.loads(propertyString)
      for elem in obj:
        if PDateTimezonesHandler.PROPERTY_OPTION_PATTERN in elem and \
          PDateTimezonesHandler.PROPERTY_OPTION_ZONE_TO in elem and \
          PDateTimezonesHandler.PROPERTY_OPTION_ZONE_FROM in elem and \
          PDateTimezonesHandler.PROPERTY_OPTION_CONDITION in elem:
          properties.append(PDateTimezonesProperties(elem[PDateTimezonesHandler.PROPERTY_OPTION_PATTERN],
                                                     elem[PDateTimezonesHandler.PROPERTY_OPTION_ZONE_TO],
                                                     elem[PDateTimezonesHandler.PROPERTY_OPTION_ZONE_FROM],
                                                     elem[PDateTimezonesHandler.PROPERTY_OPTION_CONDITION]))
        elif PDateTimezonesHandler.PROPERTY_OPTION_PATTERN in elem and \
          PDateTimezonesHandler.PROPERTY_OPTION_ZONE_TO in elem and \
          PDateTimezonesHandler.PROPERTY_OPTION_CONDITION in elem:
          properties.append(PDateTimezonesProperties(elem[PDateTimezonesHandler.PROPERTY_OPTION_PATTERN],
                                                     elem[PDateTimezonesHandler.PROPERTY_OPTION_ZONE_TO],
                                                     None,
                                                     elem[PDateTimezonesHandler.PROPERTY_OPTION_CONDITION]))
        else:
          if logger is not None:
            errorMessage = PDateTimezonesHandler.ERROR_MANDATORY_FIELDS + ': '
            if PDateTimezonesHandler.PROPERTY_OPTION_PATTERN not in elem:
              errorMessage += "'" + PDateTimezonesHandler.PROPERTY_OPTION_PATTERN + "',"

            if PDateTimezonesHandler.PROPERTY_OPTION_ZONE_TO not in elem:
              errorMessage += "'" + PDateTimezonesHandler.PROPERTY_OPTION_ZONE_TO + "',"

            if PDateTimezonesHandler.PROPERTY_OPTION_CONDITION not in elem:
              errorMessage += "'" + PDateTimezonesHandler.PROPERTY_OPTION_CONDITION + "',"

            logger.debug(errorMessage)

    except Exception, err:
      if logger is not None:
        logger.error(PDateTimezonesHandler.ERROR_LOAD_PROPERTIES + ': ' + str(err))

    return properties


  # # Transform datetime accord to url pattern, timezones and conditions
  #
  # @param dt - input datetime before transformation
  # @param utcOffset - input utcOffset if was detected
  # @param propertyString - input property string
  # @param urlString - url string for search use regular expression
  # @param logger - instance of logger for log if necessary
  # @return transformed datatime or None
  @staticmethod
  def transform(dt, utcOffset, propertyString, urlString, logger=None):
    # variable for result
    ret = None
    try:
      if not isinstance(dt, datetime.datetime):
        raise Exception(PDateTimezonesHandler.ERROR_BAD_PARAMETER + " 'Datatime'")

      if (not isinstance(propertyString, str) and not isinstance(propertyString, unicode)) or not propertyString:
        raise Exception(PDateTimezonesHandler.ERROR_BAD_PARAMETER + " 'propertyString'")

      if (not isinstance(urlString, str) and not isinstance(urlString, unicode)) or not urlString:
        raise Exception(PDateTimezonesHandler.ERROR_BAD_PARAMETER + " 'urlString'")

      # try load properties
      properties = PDateTimezonesHandler.loadProperties(propertyString, logger)
      # Transform each element
      for elem in properties:
        match = re.search(elem.pattern, urlString)
        if match:
          if logger is not None:
            logger.debug(PDateTimezonesHandler.USE_PATTERN + ": '" + str(elem.pattern) + "'")

          transformHandlers = {\
            PDateTimezonesHandler.TRANSFORMATION_ALWAYS:\
            PDateTimezonesHandler.transformationHandlerAlways, \
            PDateTimezonesHandler.TRANSFORMATION_TIMEZONE_DEFINED:\
            PDateTimezonesHandler.transformationHandlerTimezoneDefined, \
            PDateTimezonesHandler.TRANSFORMATION_NO_TIMEZONE_DEFINED:\
            PDateTimezonesHandler.transformationHandlerNoTimezoneDefined, \
            PDateTimezonesHandler.TRANSFORMATION_TIMEZONE_EQUAL:\
            PDateTimezonesHandler.transformationHandlerTimezoneEqual, \
            PDateTimezonesHandler.TRANSFORMATION_TIMEZONE_NOT_EQUAL:\
            PDateTimezonesHandler.transformationHandlerTimezoneNotEqual}

          if int(elem.condition) < len(transformHandlers) and  int(elem.condition) >= 0:
            # check value of zoneFrom
            if elem.zoneFrom is None:
              elem.zoneFrom = DateTimeType.getTimezone(dt)  # from datetime
            elif elem.zoneFrom == PDateTimezonesHandler.VALUE_ZONE_FROM_LOCAL:
              elem.zoneFrom = PDateTimezonesHandler.getLocalOffset()  # from local offset

            logger.debug('>>>>> d.isoformat: ' + str(dt.isoformat(' ')))
            logger.debug('>>>>> elem.zoneFrom: ' + str(elem.zoneFrom))
            logger.debug('>>>>> elem.zoneTo: ' + str(elem.zoneTo))
            logger.debug('>>>>> elem.condition = ' + str(elem.condition))

            # Make excution accord to different algorithms
            ret = transformHandlers[int(elem.condition)](dt, utcOffset, elem.zoneTo, elem.zoneFrom, logger)
            if ret is not None:
              if logger is not None:
                logger.debug('Exit from loop.')
              break
          else:
            if logger is not None:
              logger.debug(PDateTimezonesHandler.ERROR_WRONG_CONDITION + ': ' + str(elem.condition))

    except Exception, err:
      if logger is not None:
        logger.error(str(err))

    logger.debug("!!! ret: %s", str(ret))
    return ret


  # #Convert utcOffset to time instance
  #
  # @param utcOffset - input utcOffset if was detected
  # @param logger - instance of logger for log if necessary
  # @return operation, hour, minute
  @staticmethod
  def utcOffsetToNumeric(utcOffset, logger=None):
    # variable for result
    operation = None
    hour = 0
    minute = 0

    utcOffset = utcOffset.replace('−', '-')

    try:
      for pattern in PDateTimezonesHandler.patternListTimezoneOffset:
        match = re.search(pattern, utcOffset)
        if match:
          if 'op' in match.groupdict():
            if match.groupdict()['op'] == '-':
              operation = -1
            else:
              operation = 1

          if 'hour' in match.groupdict():
            hour = int(match.groupdict()['hour'])

            if operation is None:
              operation = 1

          if 'min' in match.groupdict():
            minute = int(match.groupdict()['min'])
          break

      if logger is not None:
        logger.debug('operation: ' + str(operation) + ' hour: ' + str(hour) + ' minute: ' + str(minute))

    except Exception, err:
      if logger:
        logger.debug(str(err))

    return operation, int(hour), int(minute)


  # #Get local timezone utc offset as string
  #
  # @param - None
  # @return string timezome
  @staticmethod
  def getLocalOffset():
    gmTime = time.gmtime()
    locTime = time.localtime()

    tmMinute = (gmTime.tm_hour * 60 + gmTime.tm_min) - (locTime.tm_hour * 60 + locTime.tm_min)
    hour = tmMinute // 60 * (-1)
    minute = tmMinute - tmMinute // 60 * 60
    # structTime = (time.strptime(str(hour) + ' ' + str(minute), "%H %M"))
    # return str(time.strftime('%H:%M', structTime))

    return str(hour) + ':' + str(minute)


  # # Compare two string contents offset data
  #
  # @param lhs - first string data
  # @param rhs - second string data
  # @param logger - instance of logger for log if necessary
  # @return True is equal and False otherwise
  @staticmethod
  def isEqualOffset(lhs, rhs, logger=None):
    # variable for result
    ret = False
    # extract lhs timezone offset
    lUtcOffset = DateTimeType.extractUtcOffset(lhs, logger)
    if lUtcOffset is not None:
      # extract rhs timezome offset
      rUtcOffset = DateTimeType.extractUtcOffset(rhs, logger)

      if rUtcOffset is not None:
        lOperation, lHour, lMinute = PDateTimezonesHandler.utcOffsetToNumeric(lUtcOffset, logger)
        rOperation, rHour, rMinute = PDateTimezonesHandler.utcOffsetToNumeric(rUtcOffset, logger)
        # compare extracter numeric values
        if lOperation and rOperation and lOperation == rOperation and lHour == rHour and lMinute == rMinute:
          ret = True

    return ret


  # # Transformation handler always perform
  #
  # @param dt - input datetime before transformation
  # @param utcOffset - input utcOffset if was detected
  # @param zoneTo - string defines zone to transform to
  # @param zoneFrom - string defines zone to transform from
  # @param logger - instance of logger for log if necessary
  # @return datetime instance
  @staticmethod
  def transformationHandlerAlways(dt, utcOffset, zoneTo, zoneFrom, logger=None): # pylint: disable=W0613,W0612
    # variable for result
    ret = None
    # local variables
    tZoneTo = datetime.timedelta(hours=0)
    tZoneFrom = datetime.timedelta(hours=0)
    opZoneFrom = 1

    zoneToOffset = DateTimeType.extractUtcOffset(zoneTo, logger)
    if zoneToOffset is not None:
      zoneTo = str(zoneToOffset)

    zoneFromOffset = DateTimeType.extractUtcOffset(zoneFrom, logger)
    if zoneFromOffset is not None:
      zoneFrom = str(zoneFromOffset)

    opZoneTo, hour, minute = PDateTimezonesHandler.utcOffsetToNumeric(zoneTo, logger)
    if opZoneTo is None:
      opZoneTo = 1

    if opZoneTo is not None:
      tZoneTo = datetime.timedelta(hours=hour, minutes=minute)

      if zoneFrom is None:
        tZoneFrom = datetime.timedelta(hours=0, minutes=0)
        opZoneFrom = 1
      else:
        opZoneFrom, hour, minute = PDateTimezonesHandler.utcOffsetToNumeric(zoneFrom, logger)
        if opZoneFrom is None:
          opZoneFrom = 1
        tZoneFrom = datetime.timedelta(hours=hour, minutes=minute)

    if logger is not None:
      logger.debug("!!! opZoneTo = %s, opZoneFrom = %s", str(opZoneTo), str(opZoneFrom))
      logger.debug("!!! tZoneTo = %s, tZoneFrom = %s", str(tZoneTo), str(tZoneFrom))

    if opZoneTo is not None and opZoneFrom is not None:
      if int(opZoneTo) >= 0 and int(opZoneFrom) >= 0:
        # ret = dt - (max(tZoneTo, tZoneFrom * (-1)) - min(tZoneTo, tZoneFrom * (-1)))
        ret = dt + tZoneFrom * (-1) + tZoneTo
        if logger is not None:
          logger.debug("!!! GOOD !!! ret = %s", str(ret))

      elif int(opZoneTo) < 0 and int(opZoneFrom) < 0:
        # ret = dt + (max(tZoneTo, tZoneFrom * (-1)) - min(tZoneTo, tZoneFrom * (-1)))
        ret = dt + tZoneFrom * (-1) + tZoneTo

      else:
        ret = dt + (abs(tZoneTo) + abs(tZoneFrom)) * opZoneTo
        # ret = dt + (tZoneFrom * (-1) + tZoneTo) * opZoneTo

    return ret


  # # Transformation handler if timezone defined
  #
  # @param dt - input datetime before transformation
  # @param utcOffset - input utcOffset if was detected
  # @param zoneTo - string defines zone to transform to
  # @param zoneFrom - string defines zone to transform from
  # @param logger - instance of logger for log if necessary
  # @return datetime instance
  @staticmethod
  def transformationHandlerTimezoneDefined(dt, utcOffset, zoneTo, zoneFrom, logger=None):
    # variable for result
    ret = None
    sourceTimeZone = DateTimeType.extractUtcOffset(utcOffset, logger, True)
    if sourceTimeZone is not None:
      ret = PDateTimezonesHandler.transformationHandlerAlways(dt, utcOffset, zoneTo, zoneFrom, logger)

    return ret


  # # Transformation handler if no timezone defined
  #
  # @param dt - input datetime before transformation
  # @param utcOffset - input utcOffset if was detected
  # @param zoneTo - string defines zone to transform to
  # @param zoneFrom - string defines zone to transform from
  # @param logger - instance of logger for log if necessary
  # @return datetime instance
  @staticmethod
  def transformationHandlerNoTimezoneDefined(dt, utcOffset, zoneTo, zoneFrom, logger=None):
    # variable for result
    ret = None
    sourceTimeZone = DateTimeType.extractUtcOffset(utcOffset, logger)
    if sourceTimeZone is None:
      ret = PDateTimezonesHandler.transformationHandlerAlways(dt, utcOffset, zoneTo, zoneFrom, logger)

    return ret


  # # Transformation handler if timezone equal
  #
  # @param dt - input datetime before transformation
  # @param utcOffset - input utcOffset if was detected
  # @param zoneTo - string defines zone to transform to
  # @param zoneFrom - string defines zone to transform from
  # @param logger - instance of logger for log if necessary
  # @return datetime instance
  @staticmethod
  def transformationHandlerTimezoneEqual(dt, utcOffset, zoneTo, zoneFrom, logger=None):
    # variable for result
    ret = None
    if PDateTimezonesHandler.isEqualOffset(utcOffset, zoneFrom):
      ret = PDateTimezonesHandler.transformationHandlerAlways(dt, utcOffset, zoneTo, zoneFrom, logger)

    return ret


  # # Transformation handler if timezone not equal
  #
  # @param dt - input datetime before transformation
  # @param utcOffset - input utcOffset if was detected
  # @param zoneTo - string defines zone to transform to
  # @param zoneFrom - string defines zone to transform from
  # @param logger - instance of logger for log if necessary
  # @return datetime instance
  @staticmethod
  def transformationHandlerTimezoneNotEqual(dt, utcOffset, zoneTo, zoneFrom, logger=None):
    # variable for result
    ret = None
    if not PDateTimezonesHandler.isEqualOffset(utcOffset, zoneFrom):
      ret = PDateTimezonesHandler.transformationHandlerAlways(dt, utcOffset, zoneTo, zoneFrom, logger)

    return ret


  # # Apply timezone
  #
  # @param dt - datetime instance
  # @param timezone - timezone as string for apply
  # @param logger - instance of logger for log if necessary
  # @return datetime instance after apply timezone offset
  @staticmethod
  def applyTimezone(dt, timezone, logger=None):
    utcOffset = DateTimeType.extractUtcOffset(timezone, logger, True)
    if logger is not None:
      logger.debug("timezone: '%s', utcOffset: %s", str(timezone), str(utcOffset))

    res = PDateTimezonesHandler.transformationHandlerAlways(dt, utcOffset, timezone, None, logger)
    if logger is not None:
      logger.debug("result: %s", str(res))

    if res is not None:
      dt = res

    return dt
