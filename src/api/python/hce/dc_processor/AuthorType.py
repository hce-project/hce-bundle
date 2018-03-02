# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
AuthorType Class content main functional extract of author data.

@package: dc_processor
@file AuthorType.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import json


# # Class AuthorType for extract author data.
#
class AuthorType(object):
  # #Constans used in class
  # Author tag name value
  MAIN_TAG_NAME = 'author'
  # Support options names
  MIN_WORDS_NAME = 'min_words'
  MAX_WORDS_NAME = 'max_words'
  MIN_BYTES_NAME = 'min_bytes'
  MAX_BYTES_NAME = 'max_bytes'
  MAX_CHARS_WORD_NAME = 'max_chars_word'
  CLEAN_NONE_ALPHA_NAME = 'clean_none_alpha'
  VALUE_NAME = 'value'
  MISMATCH_NAME = 'mismatch'
  UNDETECTED_NAME = 'undetected'
  # 'Mismatch' options values
  MISMATCH_VALUE_EMPTY = 'empty'
  MISMATCH_VALUE_IGNORE = 'ignore'
  MISMATCH_VALUE_VALUE = 'value'
  MISMATCH_VALUE_PARSE = 'parse'
  # 'Undetected' options values
  UNDETECTED_VALUE_EMPTY = 'empty'
  UNDETECTED_VALUE_IGNORE = 'ignore'
  UNDETECTED_VALUE_VALUE = 'value'
  # Default options values
  MIN_WORDS_DEFAULT_VALUE = 1
  MAX_WORDS_DEFAULT_VALUE = 8
  MIN_BYTES_DEFAULT_VALUE = 3
  MAX_BYTES_DEFAULT_VALUE = 32
  MAX_CHARS_WORD_DEFAULT_VALUE = MAX_BYTES_DEFAULT_VALUE
  CLEAN_NONE_ALPHA_DEFAULT_VALUE = 1
  MISMATCH_DEFAULT_VALUE = MISMATCH_VALUE_EMPTY
  UNDETECTED_DEFAULT_VALUE = UNDETECTED_VALUE_EMPTY

  # #Constant of error messages
  # ERROR_INPUT_PARAMS = 'Error initialization by input parameters.'
  ERROR_DATA_STRING_TYPE = 'Data string is not string.'
  ERROR_CONFIG_PROPERTY_TYPE = 'Config property type is wrong'
  ERROR_PROCESSOR_PROPERTY_TYPE = 'Processor property type is wrong'
  ERROR_MAIN_TAG_NAME = "Main tag name '" + str(MAIN_TAG_NAME) + "' not found"

  # #Constructor
  #
  # @param confProp - properties as JSON already read from config file
  # @param procProp - properties as JSON from PROCESSOR_PROPERTIES
  # @param dataString - string for extract
  # @param logger - instance of logger for log if necessary
  def __init__(self, confProp=None, procProp=None, dataString=None, logger=None):
    self.author = AuthorType.parse(confProp, procProp, dataString, logger)


  # #Get default properties
  #
  # @param - None
  # @return prop - dictionary with default properties
  @staticmethod
  def getDefaultProperties():
    # variable for result
    propDict = {}
    # initialization use default values
    propDict[AuthorType.MIN_WORDS_NAME] = AuthorType.MIN_WORDS_DEFAULT_VALUE
    propDict[AuthorType.MAX_WORDS_NAME] = AuthorType.MAX_WORDS_DEFAULT_VALUE
    propDict[AuthorType.MIN_BYTES_NAME] = AuthorType.MIN_BYTES_DEFAULT_VALUE
    propDict[AuthorType.MAX_BYTES_NAME] = AuthorType.MAX_BYTES_DEFAULT_VALUE
    propDict[AuthorType.MAX_CHARS_WORD_NAME] = AuthorType.MAX_CHARS_WORD_DEFAULT_VALUE
    propDict[AuthorType.CLEAN_NONE_ALPHA_NAME] = AuthorType.CLEAN_NONE_ALPHA_DEFAULT_VALUE
    propDict[AuthorType.MISMATCH_NAME] = AuthorType.MISMATCH_DEFAULT_VALUE
    propDict[AuthorType.UNDETECTED_NAME] = AuthorType.UNDETECTED_DEFAULT_VALUE

    return propDict


  # #Merge properties
  #
  # @param confProp - properties as JSON string already read from config file
  # @param procProp - properties as JSON string from PROCESSOR_PROPERTIES
  @staticmethod
  def mergeProperties(confProp, procProp):

    if confProp is not None and not (isinstance(confProp, str) or isinstance(confProp, unicode) or\
                                     isinstance(confProp, dict)):
      raise Exception(AuthorType.ERROR_CONFIG_PROPERTY_TYPE + ': ' + str(type(confProp)))

    if procProp is not None and not (isinstance(procProp, str) or isinstance(procProp, unicode) or\
                                     isinstance(procProp, dict)):
      raise Exception(AuthorType.ERROR_PROCESSOR_PROPERTY_TYPE + ': ' + str(type(procProp)))

    # variable for result
    propDict = AuthorType.getDefaultProperties()

    # update variables from config file
    confPropDict = {}
    if confProp is not None:
      if not isinstance(confProp, dict):
        confPropDict = json.loads(confProp)
      else:
        confPropDict = confProp

      if not confPropDict.has_key(AuthorType.MAIN_TAG_NAME):
        raise Exception(AuthorType.ERROR_MAIN_TAG_NAME)

      propDict.update(confPropDict[AuthorType.MAIN_TAG_NAME])

    # update variables from PROCESSOR_PROPERTIES
    procPropDict = {}
    if procProp is not None:
      if not isinstance(procProp, dict):
        procPropDict = json.loads(procProp)
      else:
        procPropDict = procProp

      if not procPropDict.has_key(AuthorType.MAIN_TAG_NAME):
        raise Exception(AuthorType.ERROR_MAIN_TAG_NAME)

      propDict.update(procPropDict[AuthorType.MAIN_TAG_NAME])

    return propDict


  # #Check data string limits
  #
  # @param propDict - dictionary of properties
  # @param dataString -  data string for extract
  # @param logger - instance of logger for log if necessary
  # @return True - if allowed limits interval, otherwise False
  @staticmethod
  def checkDataStringLimits(propDict, dataString, logger=None):
    # variable for result
    ret = False

    bytesCount = len(dataString)
    wordsCount = 0
    for word in dataString.split():
      if len(word) >= int(propDict[AuthorType.MIN_BYTES_NAME]):
        wordsCount += 1

    if logger is not None:
      logger.debug('bytesCount = ' + str(bytesCount))
      logger.debug('wordsCount = ' + str(wordsCount))

    # check limits
    if bytesCount >= int(propDict[AuthorType.MIN_BYTES_NAME]) and \
    bytesCount <= int(propDict[AuthorType.MAX_BYTES_NAME]) and \
    wordsCount >= int(propDict[AuthorType.MIN_WORDS_NAME]) and \
    wordsCount <= int(propDict[AuthorType.MAX_WORDS_NAME]):
      ret = True

    return ret


  # #Check word is good ot not
  #
  # @param word - same word
  # @param minAllowedWordLength - min allowed length of word
  # @param logger - instance of logger for log if necessary
  # @return True - if success, otherwise False
  @staticmethod
  def isGoodWord(word, minAllowedWordLength, logger=None):

    if logger is not None:
      logger.debug('word: ' + str(word) + ' minAllowedWordLength = ' + str(minAllowedWordLength))
      logger.debug('word.istitle(): ' + str(bool(unicode(word, 'utf-8').istitle())))

    # variable for result
    ret = False
    if len(word) >= minAllowedWordLength:
      if unicode(word, 'utf-8').istitle():
        ret = True

    if logger is not None:
      logger.debug('ret = ' + str(ret))

    return ret


  # #Remove none alpha from word
  #
  # @param word - input word
  # @return word without not alpha simbols
  @staticmethod
  def removeNoneAlpha(word):
    wd = []
    for s in word:
      if s.isalpha():
        wd.append(s)
      else:
        wd.append(' ')

    return ''.join(wd)


  # #Get pair names
  #
  # @param wordsList - words list for extract
  # @param minAllowedWordLength - min allowed length of word
  # @param cleanNoneAlpha - flag of clean none alpha simbols before analyze
  # @param logger - instance of logger for log if necessary
  # @return string of pair names  if success, otherwise None
  @staticmethod
  def getPairNames(wordsList, minAllowedWordLength, cleanNoneAlpha=False, logger=None):
    # variable for result
    ret = None
    first = second = ''
    for index in range(0, len(wordsList)):
      if index < len(wordsList) - 1:
        if logger is not None:
          logger.debug('cleanNoneAlpha: ' + str(cleanNoneAlpha))

        if cleanNoneAlpha:
          first = AuthorType.removeNoneAlpha(wordsList[index])
          second = AuthorType.removeNoneAlpha(wordsList[index + 1])

          firstList = first.split()
          if len(firstList) > 0:
            first = firstList[-1]

          secondList = second.split()
          if len(secondList) > 0:
            second = secondList[0]

        else:
          first = wordsList[index]
          second = wordsList[index + 1]

        if logger is not None:
          logger.debug('first: ' + str(first) + ' second: ' + str(second))

        if (AuthorType.isGoodWord(first, minAllowedWordLength, logger) and \
            AuthorType.isGoodWord(second, minAllowedWordLength, logger)) or \
            (AuthorType.isGoodWord(first, minAllowedWordLength, logger) and second.isupper()) or \
            (first.isupper() and AuthorType.isGoodWord(second, minAllowedWordLength, logger)):
          ret = first + ' ' + second
          break

    return ret


  # #Extract author name
  #
  # @param wordsList - words list for extract
  # @param minAllowedWordLength - min allowed length of word
  # @param maxAllowedWordLength - max allowed length of word
  # @param logger - instance of logger for log if necessary
  # @return author name as string if success, otherwise None
  @staticmethod
  def extractAuthorName(wordsList, minAllowedWordLength, maxAllowedWordLength, logger=None):
    # variable for result
    ret = None

    for word in wordsList:
      # first word with upper title
      if AuthorType.isGoodWord(word, int(minAllowedWordLength)) and word != wordsList[0]:
        ret = (AuthorType.removeNoneAlpha(word).strip())
        if logger is not None:
          logger.debug('Found first word with upper title: ' + str(ret))
        break

      # extract from email
      pos = word.find('@')
      if pos > -1:
        AuthorName = word[:pos]
        if len(AuthorName) >= minAllowedWordLength and len(AuthorName) <= maxAllowedWordLength:
          ret = AuthorName
          if logger is not None:
            logger.debug('Found author name in email: ' + str(ret))
          break
        else:
          if logger is not None:
            logger.debug("Candidate '" + str(AuthorName) + "' for extract from email didn't pass limits")

      # search two words was concatenated
      if len(word) > minAllowedWordLength:
        found = False
        for index in range(0, len(word)):
          if index > 0 and word[index - 1].isalpha() and word[index].isupper():
            first = word[:index]
            second = word[index:]
            if AuthorType.isGoodWord(first, int(minAllowedWordLength)) and \
            AuthorType.isGoodWord(second, int(minAllowedWordLength)):
              ret = first + ' ' + second
              if logger is not None:
                logger.debug('Found author name from two concatinated words: ' + str(ret))
              found = True
            else:
              if logger is not None:
                logger.debug("Candidate '" + str(word) + \
                              "' for extract from two concatinated words didn't pass validate")
            break
        if found:
          break

      # search nickname
      if word.find('_') > -1:
        wd = word.split('_')
        if len(wd) > 0:
          ret = wd[0]
          if len(wd) > 1:
            ret += (' ' + AuthorType.removeNoneAlpha(wd[1]).split()[0])
            if logger is not None:
              logger.debug('Found author name from nickname: ' + str(ret))
            break

    return ret


  # #Make parsing data string
  #
  # @param propDict - dictionary of properties
  # @param dataString - string for extract
  # @param logger - instance of logger for log if necessary
  # @return string value - if success, otherwise None
  @staticmethod
  def makeParsing(propDict, dataString, logger=None):
    wordsList = dataString.split()

    # Search pair: name, surname
    ret = AuthorType.getPairNames(wordsList, int(propDict[AuthorType.MIN_BYTES_NAME]), False, None)
    if logger is not None:
      logger.debug('Search author as pair words: ' + str(ret))

    if ret is None and bool(propDict[AuthorType.CLEAN_NONE_ALPHA_NAME]):
      ret = AuthorType.getPairNames(wordsList, int(propDict[AuthorType.MIN_BYTES_NAME]), True)
      if logger is not None:
        logger.debug('Search author as pair words after clean not alpha: ' + str(ret))

    if ret is None:
      ret = AuthorType.extractAuthorName(wordsList, int(propDict[AuthorType.MIN_BYTES_NAME]),
                                         int(propDict[AuthorType.MAX_CHARS_WORD_NAME]), logger)
      if logger is not None:
        logger.debug('makeParsing return: ' + str(ret))

    return ret


  # # static method for parse
  #
  # @param confProp - properties as JSON already read from config file
  # @param procProp - properties as JSON from PROCESSOR_PROPERTIES
  # @param dataString - string for extract
  # @param logger - instance of logger for log if necessary
  # @return extracted author as string or None
  @staticmethod
  def parse(confProp, procProp, dataString, logger=None):
    # variable for result
    ret = None
    try:
      if logger is not None:
        logger.debug('input raw data to parse: ' + str(dataString))

      if not isinstance(dataString, str) and not isinstance(dataString, unicode):
        raise Exception(AuthorType.ERROR_DATA_STRING_TYPE + ' type: ' + str(type(dataString)))

      propDict = AuthorType.mergeProperties(confProp, procProp)
      if logger is not None:
        logger.debug('merged properties: ' + str(propDict))

      isGood = AuthorType.checkDataStringLimits(propDict, dataString, logger)
      if logger is not None:
        logger.debug('isGood: ' + str(bool(isGood)))

      # check mismatch
      if isGood:
        ret = AuthorType.makeParsing(propDict, str(dataString), logger)
      else:
        if propDict[AuthorType.MISMATCH_NAME] == AuthorType.MISMATCH_VALUE_EMPTY:
          ret = ''
        elif propDict[AuthorType.MISMATCH_NAME] == AuthorType.MISMATCH_VALUE_IGNORE:
          ret = dataString
        elif propDict[AuthorType.MISMATCH_NAME] == AuthorType.MISMATCH_VALUE_VALUE:
          ret = propDict[AuthorType.VALUE_NAME]
        elif propDict[AuthorType.MISMATCH_NAME] == AuthorType.MISMATCH_VALUE_PARSE:
          ret = AuthorType.makeParsing(propDict, dataString, logger)
        else:
          ret = ''

      # check undetected
      if ret is None:
        if propDict[AuthorType.UNDETECTED_NAME] == AuthorType.UNDETECTED_VALUE_EMPTY:
          ret = ''
        elif propDict[AuthorType.UNDETECTED_NAME] == AuthorType.UNDETECTED_VALUE_IGNORE:
          ret = dataString
        elif propDict[AuthorType.UNDETECTED_NAME] == AuthorType.UNDETECTED_VALUE_VALUE:
          ret = propDict[AuthorType.VALUE_NAME]
        else:
          ret = ''

    except Exception, err:
      if logger is not None:
        logger.debug('Error: ' + str(err))

    return ret
