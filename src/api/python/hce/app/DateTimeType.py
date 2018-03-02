# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
DateTimeType Class content main functional extract of datetime.

@package: dc_processor
@file DateTimeType.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import time
import copy
from datetime import tzinfo
import datetime

# from dateutil.parser import parserinfo
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.tz import gettz
from dateutil import parser

from app.Utils import getTracebackInfo

try:
  from app.Utils import ExceptionLog  # pylint: disable=E0401
except:  # pylint: disable=W0702
  ExceptionLog = None

import DateTimeTimezones  # pylint: disable=W0403



# # Class OffsetTzInfo for calculate offset
class OffsetTzInfo(tzinfo):
  # #Constructor
  def __init__(self, isNegative=False, hours=0, minutes=0):
    self.isNegative = isNegative
    self.hours = hours
    self.minutes = minutes
    super(OffsetTzInfo, self).__init__()

  # #Method utcoffset inheritor from interface of base class
  def utcoffset(self, dt):  # pylint: disable=W0613
    ret = datetime.timedelta(hours=self.hours, minutes=self.minutes)
    if self.isNegative:
      ret = (-1) * ret
    return ret

  # #Method dst inheritor from interface of base class
  def dst(self, dt):  # pylint: disable=W0613
    return datetime.timedelta(0)

  # #Method tzname inheritor from interface of base class
  def tzname(self, dt):  # pylint: disable=W0613
    ret = '{:%H:%M}'.format(datetime.time(hour=self.hours, minute=self.minutes))
    if self.isNegative:
      ret = '−' + ret
    else:
      ret = '+' + ret
    return "UTC" + ret


# # Class DateTimeType for extract data
#
class DateTimeType(object):
  # #Constans used in class
  MIN_ALLOWED_YEAR = 2000
  MIN_ALLOWED_LEN_FOR_DATEUTILS = 10
  ISO_SEP = ' '
  BAD_SIMBOLS = '=(),|@`'
  TAG_NAMES = ['pubdate', 'dc_date']

  LANG_ENG = "ENG"
  LANG_RUS = "RUS"
  LANG_UKR = "UKR"
  LANG_GER = "GERMAN"
  LANG_JAP = "JAPAN"

  wordsListEng = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec', \
                  u'Year', u'Today', u'Yesterday', u'Day before yesterday', u'year', u'month', u'day', u'hour', \
                  u'minute']
  wordsListRus = [u'Янв', u'Февр', u'Мар', u'Апр', u'Май', u'Июнь', u'Июль', u'Авг', u'Сент', u'Окт', u'Нояб', \
                  u'Дек', u'Сегодня', u'Вчера', u'Поза вчера', u'Июня', u'Июля']
  wordsListUkr = [u'Сiч', u'Лют', u'Бер', u'Квiт', u'Трав', u'Черв', u'Лип', u'Серп', u'Вер', u'Жовт', u'Лист', \
                  u'Груд', u'Рік', u'Сьогодні', u'Вчора', u'Позавчора']
  wordsListGer = [u'März', u'Mai', u'Juni', u'Juli', u'Sept', u'Okt', u'Dez', u'Jahr', u'Heute', u'Gestern', \
                  u'Vorgestern', u'Uhr']
  wordsListJap = [u'一月', u'二月', u'三月', u'四月', u'五月', u'六月', u'七月', u'八月', u'九月', u'十月', u'十一月', \
                  u'十二月', u'年', u'今日', u'イエスタデイ', u'おととい', u'月', u'日', u'時', u'分', u'付', u'更新']

  monthListEng = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']
  monthListRus = [u'Янв', u'Февр', u'Март', u'Апр', u'Май', u'Июнь', u'Июль', u'Авг', u'Сент', u'Окт', u'Нояб', u'Дек']
  monthListUkr = [u'Сiч', u'Лют', u'Бер', u'Квiт', u'Трав', u'Черв', u'Лип', u'Серп', u'Вер', u'Жовт', u'Лист', u'Груд']
  monthListGer = [u'Jan', u'Feb', u'März', u'Apr', u'Mai', u'Juni', u'Juli', u'Aug', u'Sept', u'Okt', u'Nov', u'Dez']
  monthListJap = [u'一月', u'二月', u'三月', u'四月', u'五月', u'六月', u'七月', u'八月', u'九月', u'十月', u'十一月', u'十二月']
  monthListRusBad = [u'Янв', u'Февр', u'Март', u'Апр', u'Май', u'Июня', u'Июля', u'Авг', u'Сент', u'Окт', u'Нояб', \
                     u'Дек']

  dayStateEng = [u'Today', u'Yesterday', u'Day before yesterday']
  dayStateRus = [u'Сегодня', u'Вчера', u'Поза вчера']
  dayStateUkr = [u'Сьогодні', u'Вчора', u'Позавчора']
  dayStateGer = [u'Heute', u'Gestern', u'Vorgestern']
  dayStateJap = [u'今日', u'イエスタデイ', u'おととい']
  dayStateRusStr = ['Сегодня', 'Вчера', 'Поза вчера']
  dayStateUkrStr = ['Сьогодні', 'Вчора', 'Позавчора']

  LANG_DICT = {LANG_ENG: wordsListEng, LANG_RUS: wordsListRus, LANG_UKR: wordsListUkr, LANG_GER: wordsListGer, \
               LANG_JAP: wordsListJap}

  MONTH_DICT = {LANG_ENG: monthListEng, LANG_RUS: monthListRus, LANG_UKR: monthListUkr, LANG_GER: monthListGer, \
               LANG_JAP: monthListJap, LANG_RUS: monthListRusBad}

  DAY_STATE_DICT = {LANG_ENG: dayStateEng, LANG_RUS: dayStateRus, LANG_UKR: dayStateUkr, LANG_GER: dayStateGer, \
               LANG_JAP: dayStateJap, LANG_RUS: dayStateRusStr, LANG_UKR: dayStateUkrStr}

  patternListDate = [r'(?P<mon>[ 1][0-9]) (?P<day>[ 0123][0-9]) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\d{1,2})/(?P<day>[ 0123][0-9])/(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\d{1,2})/(?P<day>[0-9])/(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\d{1,2})-(?P<day>[0-9][0-9])-(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\d{1,2})/(?P<day>[0123][0-9])/(?P<short_year>[0-9][0-9])',
                     r'(?P<mon>\d{1,2})/(?P<day>[0-9])/(?P<short_year>[0-9][0-9])',
                     r'(?P<mon>[A-Z][a-z][a-z]) (?P<day>[ 0123][0-9]) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>[A-Z][a-z][a-z]) (?P<day>[0-9]) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\w+) (?P<day>[0-9]) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\w+) (?P<day>[ 0123][0-9]) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\w+) (?P<day>[0-9])(\w{2}) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\w+) (?P<day>[ 0123][0-9])(\w{2}) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\W+) (?P<day>\d{2})(\w{2}) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\w+) (?P<day>\d{1,2})(\W+\d{1,2}) (?P<year>\d{4})',
                     r'(?P<mon>\w+). (?P<day>\d{1,2}) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9][0-9]) (?P<mon>\w+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9][0-9]) (?P<mon>\W+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<year>[0-9][0-9][0-9][0-9]) (?P<mon>[0-1][0-9]) (?P<day>[0123][0-9])',
                     r'(?P<year>[0-9][0-9][0-9][0-9])-(?P<mon>[0-1][0-9])-(?P<day>[0123][0-9])',
                     r'(?P<year>[0-9][0-9][0-9][0-9])/(?P<mon>[0-1][0-9])/(?P<day>[0123][0-9])',
                     r'(?P<year>[0-9][0-9][0-9][0-9])/(?P<mon>[0-9])/(?P<day>[0123][0-9])',
                     r'(?P<year>[0-9][0-9][0-9][0-9])\.(?P<mon>[0-1][0-9])\.(?P<day>[0123][0-9])',
                     r'(?P<year>[0-9][0-9][0-9][0-9])(?P<mon>[0-1][0-9])(?P<day>[0123][0-9])',
                     r'(?P<day>[0-9][0-9])(\w{2}) (?P<mon>\w+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9])(\w{2}) (?P<mon>\w+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9]) (?P<mon>\w+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9]) (?P<mon>\W+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9][0-9])/(?P<mon>[0-9][0-9])/(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9][0-9]).(?P<mon>[0-9][0-9]).(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>\d{2})/(?P<mon>[0-9][0-9])/(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>\d{2})/(?P<mon>\d+})/(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>\d{1,2})\.(?P<mon>\d{1,2})\.(?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>\d{1,2})\. (?P<mon>\w+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>\d{1,2})\. (?P<mon>\W+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<day>[0-9][0-9]) (?P<mon>\w+)',
                     r'(?P<day>[0-9][0-9]) (?P<mon>\W+)',
                     r'(?P<day>[0-9]) (?P<mon>\w+)',
                     r'(?P<day>[0-9]) (?P<mon>\W+)',
                     r'(?P<mon>\d{1,2})\.(?P<day>[0123][0-9])\.(?P<short_year>[0-9][0-9])',
                     r'(?P<mon>\d{1,2})\.(?P<day>[0-9])\.(?P<short_year>[0-9][0-9])',
                     r'(?P<day>[0123][0-9])\.(?P<mon>[01][0-9])\.(?P<short_year>[0-9][0-9])',
                     r'(?P<mon>\w+) (?P<year>[0-9][0-9][0-9][0-9])',
                     r'(?P<mon>\w+) (?P<day>\d{1,2})',
                     r'(?P<mon>\W+) (?P<day>\d{1,2})']

  patternListTime = [r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}):(?P<sec>\d{2}) (?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}):(?P<sec>\d{2}) (?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}):(?P<sec>\d{2})(?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}):(?P<sec>\d{2})(?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}) (?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}) (?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2})(?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2})(?P<tf>[PpAaMm]{2})',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}):(?P<sec>[0-9][0-9])',
                     r'(?P<hour>[ 0-9][0-9])(?P<min>\d{2}) GMT',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{2}) GMT',
                     r'(?P<hour>[ 0-9][0-9]):(?P<min>\d{1,2})']

  patternListTimezoneOffset = [r'(?P<offset>[+-][0-9][0-9]:[0-9][0-9])',
                               r'(?P<offset>[+-][0-9][0-9][0-9][0-9])',
                               r'(?P<offset>[+-]\d{1,2})',
                               r'(?P<offset>[−][0-9][0-9])']

  patternListUtcTimezones = [r'(?P<hours>[0-9][0-9]):(?P<minutes>[0-9][0-9])',
                             r'(?P<hours>[0-9][0-9])']

  # #Constant of error messages
  ERROR_INPUT_PARAMS = 'Error initialization by input parameters.'
  ERROR_FORMAT_STRING_TYPE = 'Format string is not string.'
  ERROR_DATA_STRING_TYPE = 'Data string is not string.'
  ERROR_BAD_INPUT_DATA = 'Bad inputted data.'

  # #Constructor
  #
  # @param dataString - data string for extract datatime, can be as timestamp or string with data for extract
  # @param formatString - format string for formatting data
  def __init__(self, dataString=None, formatString=None):
    self.datetime = None
    self.isError = False
    self.errorMsg = ''

    try:
      self.datetime = self.__initDataTime(dataString, formatString)

    except Exception, err:
      raise Exception(self.ERROR_INPUT_PARAMS + ' ' + str(err))


  # # initialization of datatime
  #
  # @param dataString - data string for extract datatime, can be as timestamp or string with data for extract
  # @param formatString - format string for formatting data
  # @return datatime - extracted datatime or None
  def __initDataTime(self, dataString=None, formatString=None):
    # variable for result
    ret = None
    if dataString is not None and isinstance(dataString, int):
      ret = datetime.datetime.fromtimestamp(dataString)
    elif dataString is not None and formatString is not None:
      # validate of input type of format string
      if not isinstance(formatString, str):
        raise Exception(self.ERROR_FORMAT_STRING_TYPE)
      else:
        pass
      # validate of input type of data string
      if not isinstance(dataString, str):
        raise Exception(self.ERROR_DATA_STRING_TYPE)
      else:
        pass
      # input types checked and can be used
      ret = datetime.datetime.strptime(dataString, formatString)
    elif dataString is None and formatString is None:
      pass
    else:
      raise Exception(self.ERROR_BAD_INPUT_DATA)

    return ret


  # # Return datatime as timestamp
  #
  # @param - None
  # @return datatime as timestamp
  def getInt(self):
    # variable for result
    ret = None
    try:
      ret = int((self.datetime - datetime.datetime.fromtimestamp(0)).total_seconds())
    except Exception, err:
      self.isError = True
      self.errorMsg = str(err)
      ret = None

    return ret


  # # Return datatime as string
  #
  # @param - formatString - format string for formatting data
  # @return datatime as timestamp
  def getString(self, formatString=None):
    # variable for result
    ret = None

    try:
      if formatString is None:
        ret = self.datetime.isoformat(self.ISO_SEP)
      else:
        if not isinstance(formatString, str):
          raise Exception(self.ERROR_FORMAT_STRING_TYPE)
        else:
          ret = self.datetime.strftime(formatString)
    except Exception, err:
      self.isError = True
      self.errorMsg = str(err)
      ret = None

    return ret


  # # Intendification of lang
  #
  # @param inputStr - string for detection of lang
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return constant of lang name
  @staticmethod
  def getLang(inputStr, logger=None, isExtendLog=False):
    ret = None
    found = False
    langDict = DateTimeType.LANG_DICT
    try:
      dataString = inputStr
      try:
        dataString = unicode(inputStr, 'utf-8', 'ignore')
      except Exception, err:
        if logger and isExtendLog:
          logger.debug("getLang: '" + str(err) + "'")
          logger.info(getTracebackInfo())

      for key in langDict.keys():
        for word in langDict[key]:
          if dataString.lower().find(word) > -1 or dataString.lower().find(word.lower()) > -1:
            ret = key
            found = True
            break
        if found:
          break

    except Exception, err:
      if logger and isExtendLog:
        logger.debug("getLang: '" + str(err) + "'")
        logger.info(getTracebackInfo())
      ret = DateTimeType.LANG_ENG

    return ret


  # # Intendification of lang
  #
  # @param inputStr - string for detection of lang
  # @param logger - logger instance
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return constant of month number if found
  @staticmethod
  def getMonthNumber(inputStr, logger, isExtendLog=False):
    if logger and isExtendLog:
      logger.debug("getMonthNumber inputStr: '" + inputStr + "' type: " + str(type(inputStr)))

    ret = None
    inputStr = inputStr.strip()

    if len(inputStr) < 3 and inputStr.isdigit():
      ret = int(inputStr)
    else:
      found = False
      monthDict = DateTimeType.MONTH_DICT

      for key in monthDict.keys():
        # if logger and isExtendLog:
        #  logger.debug("key: '" + str(key) + "'")

        monthNumber = 0
        for months in monthDict[key]:
          monthNumber = monthNumber + 1
          month = months.lower()
          inputMonth = inputStr
          try:
            inputMonth = inputStr.decode('utf-8')
          except UnicodeError, err:
            if logger is not None and isExtendLog:
              logger.debug("Operation decode'utf-8' has error: " + str(err))

          # if logger and isExtendLog:
          #  logger.debug(inputMonth.lower() + ' <=> ' + month)

          if inputMonth.lower().find(month) > -1 or month.lower().find(inputMonth.lower()) > -1:
            ret = monthNumber
            found = True
            break
        if found:
          break

    return ret


  # # Exctract english date from string
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractDateEng(inputStr, useCurrentYear, logger=None, isExtendLog=False):
    pubdate = DateTimeType.intelligentExtractor(inputStr, useCurrentYear, logger, isExtendLog, DateTimeType.LANG_ENG)
    if pubdate is None:
      pubdate = DateTimeType.extractDateCommon(inputStr, useCurrentYear, logger, isExtendLog)

    return pubdate


  # # Exctract russian date from string
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractDateRus(inputStr, useCurrentYear, logger=None, isExtendLog=False):
    pubdate = DateTimeType.intelligentExtractor(inputStr, useCurrentYear, logger, isExtendLog, DateTimeType.LANG_RUS)
    if pubdate is None:
      pubdate = DateTimeType.extractDateCommon(inputStr, useCurrentYear, logger, isExtendLog)

    return pubdate

  # # Exctract ukrainian date from string
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractDateUkr(inputStr, useCurrentYear, logger=None, isExtendLog=False):
    pubdate = DateTimeType.intelligentExtractor(inputStr, useCurrentYear, logger, isExtendLog, DateTimeType.LANG_UKR)
    if pubdate is None:
      pubdate = DateTimeType.extractDateCommon(inputStr, useCurrentYear, logger, isExtendLog)

    return pubdate


  # # Exctract german date from string
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractDateGerman(inputStr, useCurrentYear, logger=None, isExtendLog=False):
    pubdate = DateTimeType.intelligentExtractor(inputStr, useCurrentYear, logger, isExtendLog, DateTimeType.LANG_GER)
    if pubdate is None:
      pubdate = DateTimeType.extractDateCommon(inputStr, useCurrentYear, logger, isExtendLog)

    return pubdate


  # # Exctract japan date from string
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractDateJapan(inputStr, useCurrentYear, logger=None, isExtendLog=False):
    # replace japanise simbols
    inputStr = DateTimeType.replaceJapanSimbols(inputStr, logger, isExtendLog)

    # extract data
    pubdate = DateTimeType.intelligentExtractor(inputStr, useCurrentYear, logger, isExtendLog, DateTimeType.LANG_JAP)

    if pubdate is None:
      match = re.search(r'[0-9]', inputStr)
      if match:
        try:
          pubdate = DateTimeType.convertPubDateToRFC2822(inputStr, logger, isExtendLog)
        except Exception, err:
          if logger and isExtendLog:
            logger.debug('extractDateJapan: ' + str(err))

    if pubdate is None:
      pubdate = DateTimeType.extractDateFromHeiseiPeriod(inputStr, logger, isExtendLog)

    if pubdate is None:
      pubdate = DateTimeType.extractDateCommon(inputStr, useCurrentYear, logger, isExtendLog)

    return pubdate


  # # static method for parse
  #
  # @param dataString - string for parse
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datetime or None
  @staticmethod
  def parse(dataString, useCurrentYear=True, logger=None, isExtendLog=False):
    # variable for result
    ret = None
    if logger is not None and isExtendLog:
      logger.debug("inputStr: '" + dataString + "'")

    if DateTimeType.isAllowedInputString(dataString, logger, isExtendLog):
      if len(dataString) >= int(DateTimeType.MIN_ALLOWED_LEN_FOR_DATEUTILS):
        try:
          if not DateTimeType.isUtf8CodePage(dataString, logger, isExtendLog):
            dataString = DateTimeType.changeCodePageToAscii(dataString, logger, isExtendLog)

          if logger is not None and isExtendLog:
            logger.debug("try use 'dateutil'")

          ret = parser.parse(dataString)
          if ret is not None:
            # utc_zone = gettz('UTC')
            # ret = ret.astimezone(utc_zone)
            # ret = ret.replace(tzinfo=None)
            # print ret.isoformat(' ')
            if logger is not None and isExtendLog:
              logger.debug("'dateutil' return: " + str(ret.isoformat(DateTimeType.ISO_SEP)))
            ret = ret.replace(microsecond=0)
        except Exception, err:  # pylint: disable=W0702
          if logger is not None and isExtendLog:
            logger.debug("'dateutil' can not parse: " + str(err))
          try:
            normalizedString = DateTimeType.normalizeTimezone(dataString, logger, isExtendLog)
            if dataString != normalizedString:
              if logger is not None and isExtendLog:
                logger.debug("retry parsing use 'dateutil'")
              ret = parser.parse(normalizedString)
              if ret is not None and logger is not None and isExtendLog:
                logger.debug("'dateutil' return: " + str(ret.isoformat(DateTimeType.ISO_SEP)))
          except Exception, err:
            if logger is not None and isExtendLog:
              logger.debug("'dateutil' can not parse: " + str(err))

      if ret is None:
        # Intendification of lang
        langType = DateTimeType.getLang(dataString, logger, isExtendLog)

        if logger is not None and isExtendLog:
          logger.debug('lang type detected as: ' + str(langType))

        if langType == DateTimeType.LANG_ENG:
          # extract english date
          ret = DateTimeType.extractDateEng(dataString, useCurrentYear, logger, isExtendLog)
        elif langType == DateTimeType.LANG_RUS:
          # extract russian date
          ret = DateTimeType.extractDateRus(dataString, useCurrentYear, logger, isExtendLog)
        elif langType == DateTimeType.LANG_UKR:
          # extract ukrainian date
          ret = DateTimeType.extractDateUkr(dataString, useCurrentYear, logger, isExtendLog)
        elif langType == DateTimeType.LANG_GER:
          # extract germany date
          ret = DateTimeType.extractDateGerman(dataString, useCurrentYear, logger, isExtendLog)
        elif langType == DateTimeType.LANG_JAP:
          # extract japan date
          ret = DateTimeType.extractDateJapan(dataString, useCurrentYear, logger, isExtendLog)
        else:
          ret = DateTimeType.extractDateCommon(dataString, useCurrentYear, logger, isExtendLog)

    if ret is not None and ret.tzinfo is None:
      timezoneName = DateTimeType.extractUtcTimezoneName(dataString, logger, isExtendLog)
      utcZone = gettz(timezoneName)
      # logger.debug("utcZone: " + str(utcZone))
      # logger.debug("timezoneName: " + str(timezoneName))
      if utcZone is not None:
        ret = ret.replace(tzinfo=utcZone)
      else:
        ret = DateTimeType.applyUtcTimezone(ret, timezoneName, DateTimeTimezones.timezonesDict, logger, isExtendLog)

    if logger is not None and isExtendLog:
      if ret is not None:
        logger.debug('result pubdate: ' + str(ret.isoformat(DateTimeType.ISO_SEP)))
      else:
        logger.debug('result pubdate: NONE')

    return ret


  # # Apply UTC timezone use tzInfo to datetime object
  #
  # @param dt - datetime instance
  # @param tzName - name of timezone
  # @param timezonesDict - dictionary with timezones
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return datetime instance, already modified if success
  @staticmethod
  def applyUtcTimezone(dt, tzName, timezonesDict=DateTimeTimezones.timezonesDict, logger=None, isExtendLog=False):  # pylint: disable=W0102
    if logger is not None and isExtendLog:
      logger.debug("applyUtcTimezone enter ...")

    if dt is not None and tzName in timezonesDict and len(timezonesDict[tzName]) > 1:
      rawOffset = timezonesDict[tzName][1]

      isNegative = False
      if '−' in rawOffset or '-' in rawOffset:
        isNegative = True
      if logger is not None and isExtendLog:
        logger.debug("isNegative: " + str(isNegative))

      for pattern in DateTimeType.patternListUtcTimezones:
        match = re.search(pattern, rawOffset)
        if match:
          hours = 0
          if 'hours' in match.groupdict():
            hours = int(match.groupdict()['hours'])

          minutes = 0
          if 'minutes' in match.groupdict():
            minutes = int(match.groupdict()['minutes'])

          if logger is not None and isExtendLog:
            logger.debug("hours: " + str(hours) + " minutes: " + str(minutes))

          tzInfo = OffsetTzInfo(isNegative, hours, minutes)
          dt = dt.replace(tzinfo=tzInfo)
          if logger is not None and isExtendLog:
            logger.debug("tzname: " + str(dt.tzname()))
          break

    return dt


  # #Split datetime and timezone string
  #
  # @param dt - datetime instance
  # @return datetime instance without tzInfo and timezone string
  @staticmethod
  def split(dt):
    timezone = ''
    if dt is not None:
      timezone = dt.strftime('%z')
      dt = dt.replace(tzinfo=None)

    return dt, timezone


  # #Get timezone string
  #
  # @param dt - datetime instance
  # @return timezone string
  @staticmethod
  def getTimezone(dt):
    timezone = ''
    if dt is not None:
      timezone = dt.strftime('%z')

    return timezone


  # # Check is allowed input string for next procedure of parse
  #
  # @param dataString - string for parse
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return True if allowed or False otherwise
  @staticmethod
  def isAllowedInputString(dataString, logger=None, isExtendLog=False):
    # variable for result
    ret = True
    if dataString is None or not isinstance(dataString, basestring):
      ret = False
    elif dataString != "" and dataString.isupper() and dataString.isalnum() and \
      not dataString.isalpha():
      ret = False
      if logger and isExtendLog:
        logger.debug('input string has not allowed format')

    return ret


  # # Prepare input string (remove all bad simbols)
  #
  # @param inputStr - input string for preparation
  # @return already prepared string
  @staticmethod
  def prepareString(inputStr):
    ret = inputStr

    for tagName in DateTimeType.TAG_NAMES:
      if inputStr.lower().find('%' + tagName + '%') > -1:
        ret = ret.replace('%' + tagName + '%', '')
      else:
        pass

    for bad in DateTimeType.BAD_SIMBOLS:
      ret = ret.replace(bad, ' ')

    ret = ret.replace('  ', ' ')

    return ret


  # # Extract year, month and day from string
  #
  # @param inputStr - input string for extract date
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return year, month, day - trancated input string
  @staticmethod
  def extractDate(inputStr, useCurrentYear=True, logger=None, isExtendLog=False):
    # variables for results
    month = 0
    day = 0
    year = 0

    try:
      for pattern in DateTimeType.patternListDate:
        match = re.search(pattern, inputStr)
        if logger and isExtendLog:
          logger.debug('match: ' + str(match) + ' pattern: ' + str(pattern))

        if match:
          if logger and isExtendLog:
            logger.debug('match.groupdict(): ' + str(match.groupdict()))

          if 'short_year' in match.groupdict():
            year = int(match.groupdict()['short_year']) + int(datetime.date.today().year // 1000 * 1000)

          if 'year' in match.groupdict():
            year = match.groupdict()['year']

          if 'mon' in match.groupdict():
            month = match.groupdict()['mon']
            logger.debug('month: ' + month)
            if month.isdigit() and int(month) > 12:
              if logger and isExtendLog:
                logger.debug('Bad month (' + str(month) + ') scipped!!!')
              continue

          if 'day' in match.groupdict():
            day = match.groupdict()['day']

          if logger and isExtendLog:
            logger.debug('month = ' + month)

          monthNumber = DateTimeType.getMonthNumber(month, logger, isExtendLog)

          if logger and isExtendLog:
            logger.debug('monthNumber = ' + str(monthNumber))

          if monthNumber is not None:
            month = monthNumber
          else:
            month = day = year = 0

          if logger and isExtendLog:
            logger.debug('year: ' + str(year) + ' month: ' + str(month) + ' day: ' + str(day))

          if int(year) > DateTimeType.MIN_ALLOWED_YEAR and int(year) <= datetime.date.today().year and \
            int(month) <= 12 and int(day) <= 31:
            # if int(year) == 0 and int(month) <= 12 and int(day) <= 31:
            break

          if logger is not None and isExtendLog:
            logger.debug('Match is good !!!')
          break

      if useCurrentYear:
        d = datetime.date.today()

        if year == 0 and month and day:
          year = d.year

        if year and month and day == 0:
          day = d.day

    except Exception, err:
      if logger and isExtendLog:
        logger.debug("inputStr: '" + str(inputStr) + "'")
        if logger and ExceptionLog is not None:
          ExceptionLog.handler(logger, err, 'extractDate:', (), \
                             {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
        elif logger:
          logger.debug('extractDate:' + str(err))

    return int(year), int(month), int(day)


  # # Extract hour, minute and second from string
  #
  # @param inputStr - input string for extract time
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return hour, minute, second and tf (time format)
  @staticmethod
  def extractTime(inputStr, logger=None, isExtendLog=False):  # pylint: disable=W0613

    hour = 0
    minute = 0
    second = 0
    tf = ''

    try:
      for pattern in DateTimeType.patternListTime:
        match = re.search(pattern, inputStr)
        # if logger and isExtendLog:
        #  logger.debug('pattern: ' + str(pattern))
        if match:
          # if logger and isExtendLog:
          #  logger.debug('match.groupdict(): ' + str(match.groupdict()))

          if 'hour' in match.groupdict():
            hour = match.groupdict()['hour']

          if 'min' in match.groupdict():
            minute = match.groupdict()['min']

          if 'sec' in match.groupdict():
            second = match.groupdict()['sec']

          if 'tf' in match.groupdict():
            tf = match.groupdict()['tf']

          break

    except Exception, err:
      if logger and isExtendLog:
        logger.debug("inputStr: '" + str(inputStr) + "'")
        if logger and ExceptionLog is not None:
          ExceptionLog.handler(logger, err, 'extractTime:', (), \
                             {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
        elif logger:
          logger.debug('extractTime:' + str(err))

    return int(hour), int(minute), int(second), tf


  # # Exctract common date from string
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractDateCommon(inputStr, useCurrentYear=True, logger=None, isExtendLog=False):
    # variable for results
    ret = None
    try:
      localStr = DateTimeType.prepareString(inputStr)

      if localStr:
        match = re.search(r'\d{10}', localStr)
        if match:
          ret = datetime.datetime.fromtimestamp(int(match.group()))

          locCurrentTime = datetime.datetime.now()
          utcCurrentTime = datetime.datetime.utcnow()
          tmDelta = locCurrentTime - utcCurrentTime

          isNegative = bool(tmDelta.total_seconds() < 0)
          hours = abs(locCurrentTime.hour - utcCurrentTime.hour)
          minutes = abs(locCurrentTime.minute - utcCurrentTime.minute)
          if logger is not None and isExtendLog:
            logger.debug("isNegative: " + str(isNegative) + " hours: " + str(hours) + " minutes: " + str(minutes))

          # Correct datetime value to GMT
          if isNegative:
            ret = ret + datetime.timedelta(hours=hours, minutes=minutes)
          else:
            ret = ret - datetime.timedelta(hours=hours, minutes=minutes)

          # Apply tzInfo
          # tzInfo = OffsetTzInfo(isNegative, hours, minutes)
          tzInfo = OffsetTzInfo(False, 0, 0)
          ret = ret.replace(tzinfo=tzInfo)
          if logger is not None and isExtendLog:
            logger.debug("tzname: " + str(ret.tzname()))
        else:
          year, month, day = DateTimeType.extractDate(localStr, useCurrentYear, logger, isExtendLog)
          if logger and isExtendLog:
            logger.debug('year: ' + str(year) + '\tmonth: ' + str(month) + '\tday: ' + str(day))

          hour, minute, second, tf = DateTimeType.extractTime(localStr, logger, isExtendLog)
          if logger and isExtendLog:
            logger.debug('hour: ' + str(hour) + '\tminute: ' + str(minute) + '\tsecond: ' + str(second) + \
                         '\ttf: ' + str(tf))

          hour, minute = DateTimeType.checkTimeFormat(hour, minute, tf, logger, isExtendLog)

          if logger is not None and isExtendLog:
            logger.debug('hour: ' + str(hour) + '\tminute: ' + str(minute))

          if year and month and day:
            if useCurrentYear:
              now = datetime.datetime.now()
              if month == now.month and day == now.day:
                if hour == 0 and minute == 0:
                  hour = int(now.hour)
                  minute = int(now.minute)
                  second = now.second

            ret = datetime.datetime(year, month, day, hour, minute, second, tzinfo=None)
          elif useCurrentYear and (year + month + day) == 0 and hour > 0 and minute > 0:
            d = datetime.datetime.today()
            year = d.year
            month = d.month
            day = d.day

            if int(d.hour) < int(hour):
              day = (d - datetime.timedelta(days=1)).day

            ret = datetime.datetime(year, month, day, hour, minute, second)

    except Exception, err:
      if logger is not None and isExtendLog:
        logger.debug("inputStr: '" + str(inputStr) + "'")
        if logger and ExceptionLog is not None:
          ExceptionLog.handler(logger, err, 'extractDateCommon:', (inputStr), \
                             {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
        elif logger is not None:
          logger.debug('extractDateCommon:' + str(err))

    return ret


  # # Checking is exist offset from PM time format
  #
  # @param hour - hour value
  # @param minute - minute value
  # @param tf - time format (can be 'AM', 'PM' or other)
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return day, hour - result variables after change if necessary
  @staticmethod
  def checkTimeFormat(hour, minute, tf, logger=None, isExtendLog=False):
    if logger is not None and isExtendLog:
      logger.debug("tf: '%s'", str(tf))
      if tf is not None:
        logger.debug("find = %s", str(tf.lower().find('p')))

    if tf and tf.lower().find('p') > -1:  # found 'PM'
      if int(hour) == 12 and int(minute) == 0:  # # 12:00 PM -> 12:00
        pass
      elif int(hour) >= 0 and int(hour) < 12 and int(minute) >= 0: # # 00:01 PM -> 12:01
        hour += 12

    else:
      if int(hour) == 12 and int(minute) == 0:  # # 12:00 AM -> 00:00
        hour = 0
      elif int(hour) >= 0 and int(hour) < 12 and int(minute) >= 0: # # 00:01 AM -> 00:01
        pass

    return hour, minute


  # # Extract date from string used state of day ('Today', 'Yesterday', 'Day before yesterday')
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current datetime if wasn't selected
  # @param langName - const name of used language
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datatime or None
  @staticmethod
  def extractUseDayState(inputStr, useCurrentYear, langName, logger, isExtendLog):
    # variable for results
    ret = None
    index = 0
    for dayState in DateTimeType.DAY_STATE_DICT[langName]:
      if not inputStr.lower().find(dayState) < 0:
        if logger is not None and isExtendLog:
          logger.debug("!!! dayState: " + str(dayState))

        if useCurrentYear:
          d = datetime.date.today()
          hour, minute, second, tf = DateTimeType.extractTime(inputStr, logger, isExtendLog)  # pylint: disable=W0612
          t = datetime.time(hour, minute, second)
          dt = datetime.datetime.combine(d, t)
          ret = dt - datetime.timedelta(days=index)
          break
      else:
        index = index + 1

    return ret


  # # Extract date from string used time name ('7 hours')
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current datetime if wasn't selected
  # @param langName - const name of used language
  # @return extracted datatime or None
  @staticmethod
  def extractUseTimePeriodName(inputStr, useCurrentYear, langName):
    # variable for results
    ret = None
    match = None
    if useCurrentYear and langName == DateTimeType.LANG_ENG:
      for pattern in [r'(?P<hour>\d{1,2}) hours']:
        match = re.search(pattern, inputStr, re.UNICODE)
        if match:
          d = datetime.datetime.now()
          if 'hour' in match.groupdict():
            hour = match.groupdict()['hour']
            if int(hour) >= 0 and int(hour) <= 24:
              ret = d.replace(hour=int(hour), minute=0, second=0, microsecond=0, tzinfo=None)
              break
    # elif useCurrentYear and langName == DateTimeType.LANG_JAP:
    #  match = re.search(r'(?P<hour>\d{1,2})時間前', inputStr, re.U)
    return ret


  # # Extract date from string used period name left ('4  days left')
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current datetime if wasn't selected
  # @param langName - const name of used language
  # @return extracted datatime or None
  @staticmethod
  def extractUseTimePeriodNameLeft(inputStr, useCurrentYear, langName):
    # variable for results
    ret = None
    if useCurrentYear and langName == DateTimeType.LANG_ENG:
      for period in [u'years', u'months', u'days', u'hours', u'minutes']:
        match = re.search(r'(?P<value>\d{1,2}).? ' + period + '.?left', inputStr)
        if match:
          value = 0
          if 'value' in match.groupdict():
            value = int(match.groupdict()['value'])

          dt = datetime.datetime.now()
          if period == u'years':
            ret = dt + relativedelta(years=+value)
          elif period == u'months':
            ret = dt + relativedelta(months=+value)
          elif period == u'days':
            ret = dt + relativedelta(days=+value)
          elif period == u'hours':
            ret = dt + relativedelta(hours=+value)
          elif period == u'minutes':
            ret = dt + relativedelta(minutes=+value)

          ret = ret.replace(second=0, microsecond=0, tzinfo=None)
          break

    return ret


  # # Extract date from string used period name ago ('1 Hour Ago')
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current datetime if wasn't selected
  # @param langName - const name of used language
  # @param logger - instance of logger for log if necessary
  # @return extracted datatime or None
  @staticmethod
  def extractUseTimePeriodNameAgo(inputStr, useCurrentYear, langName, logger):
    # variable for results
    ret = None
    if useCurrentYear and langName == DateTimeType.LANG_JAP:
      for pattern in [r'(?P<value>\d{1,2})日前', r'(?P<value>\d{1,2})時間前']:
        match = re.search(pattern, inputStr, re.UNICODE)
        if match is not None:
          value = 0
          if 'value' in match.groupdict():
            value = int(match.groupdict()['value'])

            if pattern.find('日前') > 0:
              ret = datetime.datetime.now() + relativedelta(days=-value)
            elif pattern.find('時間前') > 0:
              ret = datetime.datetime.now() + relativedelta(hours=-value)

            ret = ret.replace(second=0, microsecond=0, tzinfo=None)

    if useCurrentYear and langName == DateTimeType.LANG_ENG:
      for period in [u'years', u'months', u'days', u'hours', u'minutes', u'Hour']:
        for pattern in [r'(?P<value>\d{1,2}).? ' + period + '.?Ago',
                        r'(?P<value>\d{1,2}).? ' + period + '.?ago']:
          match = re.search(pattern, inputStr, re.UNICODE)
          if match:
            value = 0
            if 'value' in match.groupdict():
              value = int(match.groupdict()['value'])

            dt = datetime.datetime.now()
            if period == u'years':
              ret = dt + relativedelta(years=-value)
            elif period == u'months':
              ret = dt + relativedelta(months=-value)
            elif period == u'days':
              ret = dt + relativedelta(days=-value)
            elif period == u'hours' or period == u'Hour':
              ret = dt + relativedelta(hours=-value)
            elif period == u'minutes':
              ret = dt + relativedelta(minutes=-value)

            ret = ret.replace(second=0, microsecond=0, tzinfo=None)
            if logger is not None:
              logger.debug("ret: %s", str(ret))
            break

    return ret


  # # Check code page of input string
  #
  # @param inputStr - input string for preparation
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return True if input string id UTF-8 code page or False otherwise
  @staticmethod
  def isUtf8CodePage(inputStr, logger, isExtendLog):
    # variable for result
    isUtf8 = False
    try:
      inputStr.decode('utf-8')
      isUtf8 = True
    except Exception, err:
      if logger is not None and isExtendLog:
        logger.debug('inputStr.decode: ' + str(err))

    return isUtf8


  # # Change code page of input string to ascii
  #
  # @param inputStr - input string for preparation
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return string with ascii code page
  @staticmethod
  def changeCodePageToAscii(inputStr, logger=None, isExtendLog=False):
    # variable for result
    ret = inputStr
    try:
      dataString = inputStr.decode('latin-1')
      ret = dataString.encode('ascii', errors='ignore')
    except Exception, err:
      if logger and isExtendLog:
        logger.debug("inputStr.decode('latin-1') : " + str(err))

    return ret


  # # Extract date from string used intelligent algorithms
  #
  # @param inputStr - input string for preparation
  # @param useCurrentYear - flag of default usage current year if wasn't selected
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @param langName - const name of used language
  # @return extracted datatime or None
  @staticmethod
  def intelligentExtractor(inputStr, useCurrentYear=True, logger=None, isExtendLog=False, langName=None):
    # variable for results
    ret = None
    dataString = copy.copy(inputStr)
    dataString = DateTimeType.prepareString(dataString)
    try:
      if langName is None:
        langName = DateTimeType.getLang(dataString)
      else:
        pass

      if langName is not None:
        ret = DateTimeType.extractUseTimePeriodNameAgo(dataString, useCurrentYear, langName, logger)

      if langName is not None and langName != DateTimeType.LANG_JAP:
        if ret is None:
          ret = DateTimeType.extractUseDayState(dataString, useCurrentYear, langName, logger, isExtendLog)
          if ret is None:
            ret = DateTimeType.extractUseTimePeriodName(dataString, useCurrentYear, langName)
            if ret is None:
              ret = DateTimeType.extractUseTimePeriodNameLeft(dataString, useCurrentYear, langName)

      # #TODO here extended functional in future
    except Exception, err:
      if logger is not None and isExtendLog:
        logger.debug("inputStr: '" + inputStr + "'")
        if logger is not None and ExceptionLog is not None:
          ExceptionLog.handler(logger, err, 'intelligentExtractor:', (inputStr), \
                             {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
        elif logger:
          logger.debug('intelligentExtractor:' + str(err))

    if logger is not None and isExtendLog:
      logger.debug('intelligentExtractor return: ' + str(ret))

    return ret


  # Convertation japanise pubdate to RFC2822
  #
  # @param rawPubdate - candidate for extract data
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return extracted datetime or None
  @staticmethod
  def convertPubDateToRFC2822(rawPubdate, logger=None, isExtendLog=False):
    try:
      # replace all unicode digits to decimal (e.g. u'\uff13' to '3')
      import unicodedata

      if isinstance(rawPubdate, unicode):
        for i in range(0, len(rawPubdate)):
          if rawPubdate[i].isdigit():
            rawPubdate = re.sub(rawPubdate[i], str(unicodedata.digit(rawPubdate[i])), rawPubdate)

      rawPubdate = rawPubdate.encode("utf_8")

      import calendar

      pubdate_parts = rawPubdate.split(",")
      if len(pubdate_parts) > 1:
        rawPubdate = pubdate_parts[0]
      rawPubdate = rawPubdate.replace("posted at", "")
      rawPubdate = rawPubdate.replace("Updated:", "")
      rawPubdate = re.sub(r"\(1/\d{1}ページ\)", "", rawPubdate)

      # Try extract 'Heisei' period
      if "平成" in rawPubdate:
        year = DateTimeType.extractYearFromHeiseiPeriod(rawPubdate)
        if year is not None:
          if logger and isExtendLog:
            logger.debug("'Heisei' period before: " + str(rawPubdate))
          rawPubdate = re.sub(r"平成(\d{1,2})", str(year), rawPubdate)
          if logger and isExtendLog:
            logger.debug("'Heisei' period after: " + str(rawPubdate))

      rawPubdate = re.sub(r"\(木\)", "", rawPubdate)
      rawPubdate = re.sub(r" 年 ", "年", rawPubdate)
      rawPubdate = re.sub(r"@", "", rawPubdate)
      parsed_time_candidate_str = float(calendar.timegm(parse(rawPubdate).timetuple()))

      if logger and isExtendLog:
        logger.debug("pubdate in seconds: %s", str(parsed_time_candidate_str))
    except Exception, err:
      if logger is not None and isExtendLog:
        logger.debug("try replace rawPubdate return: " + str(err))
      rawPubdate = DateTimeType.adjustJapaneseDate(rawPubdate, logger, isExtendLog)
      # #rawPubdate = rawPubdate.decode('latin-1')

      t = u"%Y\xe5\xb9\xb4%m\xe6\x9c\x88%d\xe6\x97\xa5 %H:%M"
      parsed_time_candidate_str = time.mktime(time.strptime(rawPubdate, t))

    # set result value
    ret = datetime.datetime.fromtimestamp(parsed_time_candidate_str)

    return ret


  # Adjust japanise date
  #
  # @param rawPubdate - candidate for extract data
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return rawPubdate - rawPubdate as string
  @staticmethod
  def adjustJapaneseDate(rawPubdate, logger=None, isExtendLog=False):
    # convert rawPubdate in format like
    # 8月20日 20:01
    # 9月3日 11時41分
    # （8月20日 紙面から）
    # 2014年8月7日
    # 2014年8月20日 夕刊
    # 2014年8月21日 朝刊>
    # 2014/8/14付
    # （2014/08/16-14:46）
    # 2014/6/3 18:53 (2014/6/3 20:13更新)
    # 2014.08.20 Wed posted at 17:52 JST
    # 2014.08.01 Fri posted at 12:36 JST
    # 2014年 08月 20日 14:34 JST
    # 2014年08月20日 19時46分
    # 2014年8月29日16時30分
    # 8/20 21:00 更新
    # 11月２３日
    # to
    # 2014年8月7日 20:01
    # check if 日 exist in date
    if logger and isExtendLog:
      logger.debug("pubdate has to be converted: <<%s>>", rawPubdate)
      logger.debug("pubdate type: <<%s>>", str(type(rawPubdate)))
    # self.logger.debug("pubdate charcode: <<%s>>", str(icu.CharsetDetector(rawPubdate).detect().getName()))
    # rawPubdate = rawPubdate.decode("utf_8")
    # self.logger.debug("pubdate has to be converted: <<%s>>", rawPubdate)
    # self.logger.debug("pubdate type: <<%s>>", str(type(rawPubdate)))
    rawPubdate = rawPubdate.strip(" \r\t\n)（）\xe6\x9b\xb4\xe6\x96\xb0\xef" +
                                  "\xbc\x89\xe5\x88\x86\xe4\xbb\x98JST\xe7\xb4\x99\xe9\x9d\xa2\xe3\x81\x8b\xe3\x82" +
                                  "　\xe5\xa4\x95\xe5\x88\x8a\xe6\x9c\x9d\xe5\x88\x8a\xe3\x80\x80\xe5\x88\x86")
    # 2014.08.20 Wed posted at 17:52 JST
    # if "Wed posted at" in rawPubdate:
    #  date_items = rawPubdate.replace(" Wed posted at ", " ").replace(".", " ").split()
    #  rawPubdate = date_items[0] + "\xe5\xb9\xb4" + date_items[1] + "\xe6\x9c\x88" + date_items[2] +\
    # "\xe6\x97\xa5 " + date_items[3]
    if "\xe6\x97\xa5" in rawPubdate:
      rawPubdate = rawPubdate.replace("\xe6\x97\xa5", "\xe6\x97\xa5 ")
      # check if date contain year
      # 2014年08月20日 19時46分
      if "\xe5\xb9\xb4" in rawPubdate and "\xe6\x99\x82" in rawPubdate:
        rawPubdate = rawPubdate.replace("\xe6\x99\x82", ":")
      elif "\xe5\xb9\xb4" in rawPubdate and not "\xe6\x99\x82" in rawPubdate:
        rawPubdate = rawPubdate + " 00:00"
        rawPubdate = rawPubdate.replace('  ', ' ')
      # 2014年08月19日 11:53
      elif "\xe5\xb9\xb4" in rawPubdate and ":" in rawPubdate and rawPubdate.count(" ") == 1:
        pass
      # 2014年 08月 20日 14:34 JST
      elif "\xe5\xb9\xb4" in rawPubdate and ":" in rawPubdate and rawPubdate.count(" ") > 1:
        pos = rawPubdate.find('\xe3\x80\x80')
        if pos > 0:
          rawPubdate = rawPubdate[:pos]

        date_items = rawPubdate.split()
        if isinstance(date_items, list) and len(date_items) == 2:
          rawPubdate = date_items[0] + " " + date_items[1]
        elif isinstance(date_items, list) and len(date_items) == 3:
          rawPubdate = date_items[0] + date_items[1]
        elif isinstance(date_items, list) and len(date_items) == 4:
          rawPubdate = date_items[0] + date_items[1] + date_items[2] + " " + date_items[3]
        else:
          pass
      elif "\xe5\xb9\xb4" in rawPubdate:
        rawPubdate = str(time.gmtime().tm_year) + "\xe5\xb9\xb4" + rawPubdate
    # 2014/8/14付
    if rawPubdate.count("/") == 2:
      # date_items = rawPubdate.split("/")
      # （2014/08/16-14:46）
      date_items = re.split("/|-", rawPubdate)
      if isinstance(date_items, list) and len(date_items) == 4:
        rawPubdate = date_items[0] + "\xe5\xb9\xb4" + date_items[1] + "\xe6\x9c\x88" + date_items[2] + \
        "\xe6\x97\xa5 " + date_items[3]
      else:
        rawPubdate = date_items[0] + "\xe5\xb9\xb4" + date_items[1] + "\xe6\x9c\x88" + date_items[2] + \
        "\xe6\x97\xa5 00:00"
    # 8月20日 紙面から
    if not "\xe5\xb9\xb4" in rawPubdate and not "/" in rawPubdate:
      date_items = rawPubdate.replace("\xe6\x9c\x88", " ").replace("\xe6\x97\xa5", " ").\
      replace("\xe6\x99\x82", " ").split()
      if isinstance(date_items, list) and len(date_items) == 4:
        rawPubdate = str(time.gmtime().tm_year) + "\xe5\xb9\xb4" + date_items[0] + "\xe6\x9c\x88" + date_items[1] + \
        "\xe6\x97\xa5 " + date_items[2] + ":" + date_items[3]
      else:
        rawPubdate = str(time.gmtime().tm_year) + "\xe5\xb9\xb4" + date_items[0] + "\xe6\x9c\x88" + date_items[1] + \
        "\xe6\x97\xa5 00:00"
    # 8/20 21:00 更新
    if not "\xe5\xb9\xb4" in rawPubdate and "/" in rawPubdate:
      date_items = rawPubdate.replace("/", " ").split()
      # 2014/6/3 18:53 (2014/6/3 20:13更新)
      if len(date_items) > 4:
        rawPubdate = date_items[0] + "\xe5\xb9\xb4" + date_items[1] + "\xe6\x9c\x88" + date_items[2] + \
        "\xe6\x97\xa5 " + date_items[3]
      else:
        rawPubdate = str(time.gmtime().tm_year) + "\xe5\xb9\xb4" + date_items[0] + "\xe6\x9c\x88" + date_items[1] + \
        "\xe6\x97\xa5 " + date_items[2]

    if logger is not None and isExtendLog:
      logger.debug("pubdate converted is: <<%s>>", rawPubdate)

    return rawPubdate


  # #Exctract year for japanise date from Heisei period
  #
  # @param rawPubdate - input raw string content pubdate
  # @return year value if success or otherwise None
  @staticmethod
  def extractYearFromHeiseiPeriod(rawPubdate):
    # variable for result
    ret = None
    if "平成" in rawPubdate:
      startPeriodYear = 1988
      match = re.search(r'平成(?P<year>\d{1,2})年', rawPubdate)
      if match:
        if 'year' in match.groupdict():
          year = int(match.groupdict()['year'])
          ret = startPeriodYear + year
    else:
      match = re.search(r'(?P<year>\d{1,4})年', rawPubdate)
      if match:
        if 'year' in match.groupdict():
          ret = int(match.groupdict()['year'])

    return ret


  # #Extract japanise date from Heisei period
  #
  # @param rawPubdate - input raw string content pubdate
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return datetime instance if success or otherwise None
  @staticmethod
  def extractDateFromHeiseiPeriod(rawPubdate, logger=None, isExtendLog=False):
    # variable for result
    ret = None
    try:
      year = DateTimeType.extractYearFromHeiseiPeriod(rawPubdate)
      if year is not None:
        if logger and isExtendLog:
          logger.debug('rawPubdate: ' + str(rawPubdate))
          logger.debug('year: ' + str(year))

        # extract month
        beginPos = rawPubdate.find('年')
        endPos = rawPubdate.find('月')
        month = rawPubdate[beginPos + len('年'):endPos]
        if logger and isExtendLog:
          logger.debug('month: ' + str(month))
        month = int(unicode(month))

        # extract day
        beginPos = rawPubdate.find('月')
        endPos = rawPubdate.find('日')
        day = rawPubdate[beginPos + len('月'):endPos]
        if logger and isExtendLog:
          logger.debug('day: ' + str(day))
        day = int(unicode(day))

        # extract time if passible
        hour, minute, second, tf = DateTimeType.extractTime(rawPubdate, logger, isExtendLog)
        if logger is not None and isExtendLog:
          logger.debug("hour: %s, minute: %s, second: %s, tf: %s", str(hour), str(minute), str(second), str(tf))

        # create result datetime object
        ret = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                                tzinfo=None)
    except Exception, err:
      if logger is not None and isExtendLog:
        logger.debug("Extract 'Heisei' period has error: " + str(err))

    return ret


  # #Replace japan simbols to unicode
  #
  # @param rawPubdate - input raw string content pubdate
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return rawPubdate - already modified string
  @staticmethod
  def replaceJapanSimbols(rawPubdate, logger=None, isExtendLog=False):
    simbolsDict = {'－':'-', '．':'.', '：':':', '／':'/', '，':',', '･':'.', 'ｰ':'-', \
                   '０':'0', '１':'1', '２':'2', '３':'3', '４':'4', '５':'5', '６':'6', '７':'7', '８':'8', '９':'9'}
    # replace simbols
    for key, value in simbolsDict.items():
      try:
        rawPubdate = rawPubdate.replace(key, value)
      except Exception, err:
        if logger is not None and isExtendLog:
          logger.debug(str(err))

    return rawPubdate


  # #Convert timezone name to utc offset
  #
  # @param tzName - name of timezone
  # @param timezonesDict - dictionary with timezones
  # @return utc offset as string
  @staticmethod
  def utcOffset(tzName, timezonesDict=DateTimeTimezones.timezonesDict):  # pylint: disable=W0102
    # variable for result
    ret = None
    if tzName in timezonesDict:
      elem = timezonesDict[tzName]
      if len(elem) > 1:
        if elem[1].find('UTC') > -1:
          ret = elem[1][len('UTC'):]

    return ret


  # # Extract utc offset from string
  #
  # @param inputStr - input string for extract time
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @param timezonesDict - dictionary with timezones
  # @return utc offset numeric as string
  @staticmethod
  def extractUtcOffset(inputStr, logger=None, isExtendLog=False, timezonesDict=DateTimeTimezones.timezonesDict):  # pylint: disable=W0102
    # variable for result
    ret = None
    if inputStr is not None:
      for key in timezonesDict.keys():
        if (inputStr.find(key)) > -1:
          ret = DateTimeType.utcOffset(key, timezonesDict)
          if logger is not None and isExtendLog:
            logger.debug('Timezone: ' + str(key) + ' offset: ' + str(ret))
          break

      if ret is None:
        try:
          for pattern in DateTimeType.patternListTimezoneOffset:
            match = re.match(pattern, inputStr)
            if logger is not None and isExtendLog:
              logger.debug('inputStr: ' + str(inputStr) + ' pattern: ' + str(pattern) + ' match: ' + str(match))
            if match:
              if 'offset' in match.groupdict():
                ret = match.groupdict()['offset']
              break

        except Exception, err:
          if logger is not None and isExtendLog:
            logger.debug('extractUtcOffset error: ' + str(err))

    if logger is not None and isExtendLog:
      logger.debug("!!! ret: %s", str(ret))
    return ret


  # # Extract timezone name from string
  # @param inputStr - input string for extract time
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @param timezonesDict - dictionary with timezones
  # @return utc timezone name as string, in case of fail extraction return empty string
  @staticmethod
  def extractUtcTimezoneName(inputStr, logger=None, isExtendLog=False, timezonesDict=DateTimeTimezones.timezonesDict):  # pylint: disable=W0102
    # variable for result
    ret = ''
    if logger is not None and isExtendLog:
      logger.debug('inputStr: ' + inputStr)
    if inputStr is not None:
      for key in timezonesDict.keys():
        pos = inputStr.find(key)
        if (pos) > -1 and inputStr[pos - 1] == ' ':
          ret = key
          if logger is not None and isExtendLog:
            logger.debug('Timezone name: ' + str(key))
          break

    return ret


  # # Extract timezone name from string
  # @param inputStr - input string for extract time
  # @param logger - instance of logger for log if necessary
  # @param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  # @return normalized string
  @staticmethod
  def normalizeTimezone(inputStr, logger=None, isExtendLog=False):
    # variable for result
    ret = inputStr
    if inputStr is not None:
      pos = inputStr.rfind('+')
      length = len('+')
      if pos == -1:
        pos = inputStr.rfind('-')
        length = len('-')

      if pos > -1:
        oldValue = inputStr[pos + length:].strip()
        newValue = ''
        if logger is not None and isExtendLog:
          logger.debug('oldValue: ' + str(oldValue))
        if oldValue.isdigit() and len(oldValue) > 1:
          newValue = '0' + oldValue[:1] + ':00'
        else:
          match = re.search(r'(?P<tzone>\d{1,4})Z', oldValue)
          if match:
            if 'tzone' in match.groupdict():
              newValue = match.groupdict()['tzone']

        if logger is not None and isExtendLog:
          logger.debug('newValue: ' + str(newValue))
        ret = inputStr.replace(oldValue, newValue)

    return ret


  # # Convert to UTC offset form
  #
  # @param dt - datetime instance
  # @return datetime instance without tzInfo and timezone string
  @staticmethod
  def toUTC(dt):
    # variable for result
    ret = dt
    if dt.utcoffset() is not None:
      ret = dt - dt.utcoffset()
    ret = ret.replace(tzinfo=None)

    return ret
