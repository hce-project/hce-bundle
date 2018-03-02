# coding: utf-8

"""
@package: dc
@file UrlSchema.py
@author Scorp <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import copy
import os
import json
import random
import string
from datetime import datetime
import urllib
import requests
import app.Consts as APP_CONSTS
from app.Utils import ExceptionLog
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


# # UrlSchema Class, implements functional UrlSchema custom generators
#
class UrlSchema(object):

  SCHEMA_DISABLE = 0
  SCHEMA_PREDEFINED = 1
  SCHEMA_INCREMENTAL_INT = 2
  SCHEMA_RANDOM_INT = 3
  SCHEMA_RANDOM_STR = 4

  CHAR_ASCII_LATIN = 0
  CHAR_HEXADECIMAL = 1
  CHAR_LOWER = 0
  CHAR_UPPER = 1

  MODE_ONE_URL = 0
  MODE_LIST_URLS = 1

  BATCH_INSERT_NO_ONE_ITEMS = 0
  BATCH_INSERT_ALL_NEW_ITEMS = 1
  BATCH_INSERT_ONLY_FIRST_ITEM = 2
  BATCH_INSERT_DEFAULT = BATCH_INSERT_NO_ONE_ITEMS
  BATCH_INSERT_MIN_ALLOWED_VALUE = BATCH_INSERT_NO_ONE_ITEMS
  BATCH_INSERT_MAX_ALLOWED_VALUE = BATCH_INSERT_ONLY_FIRST_ITEM

  JSON_SUFF = ".json"
  URL_SCHEMA_DATA_FILE_NAME_PREFIX = "url_schema_data_"


  # #Class constructor
  #
  # @param schema - incoming schema in json format
  def __init__(self, schema=None, siteId=None, urlSchemaDataDir=None):
    self.batchInsert = self.BATCH_INSERT_DEFAULT
    self.externalError = APP_CONSTS.ERROR_OK
    self.indexFileName = None
    self.indexStruct = None
    try:
      # self.globalindex = None
      self.schema = json.loads(schema)

      if isinstance(urlSchemaDataDir, basestring):
        if not os.path.isdir(urlSchemaDataDir):
          logger.debug("Create urlSchemaDataDir: %s", str(urlSchemaDataDir))
          try:
            os.makedirs(urlSchemaDataDir)
          except OSError, err:
            logger.debug("Creation of %s return error: %s", str(urlSchemaDataDir), str(err))

        if urlSchemaDataDir[-1] != '/':
          urlSchemaDataDir += '/'
        self.indexFileName = urlSchemaDataDir + self.URL_SCHEMA_DATA_FILE_NAME_PREFIX + str(siteId) + self.JSON_SUFF
        if os.path.isfile(self.indexFileName):
          self.indexStruct = self.readJsonFile(self.indexFileName)
          logger.debug(">>> readJsonFile '" + str(self.indexFileName) + "' - SUCCESS")
        else:
          self.indexStruct = None

    except Exception as excp:
      ExceptionLog.handler(logger, excp, ">>> UrlSchema wrong json loads")
      self.schema = None


  # #Method readJsonFile reads from file and return param index structure
  #
  # @param fileName - incoming file name
  # @return json structure, just readed from file
  def readJsonFile(self, fileName):
    ret = {}
    fd = None
    try:
      fd = open(fileName, "r")
      if fd is not None:
        ret = json.loads(fd.read())  # #.decode('utf-8').encode('latin-1', errors='ignore'))
        fd.close()
    except Exception, err:
      logger.debug(">>> readJsonFile error, file name = " + str(fileName) + " | " + str(err))
      if fd is not None:
        fd.close()
    return ret


  # #Method schemaPredefined implements predefined schema algorithm
  #
  # @param inUrl - incoming url
  # @param parametrs - incoming schema params
  # @return processed url
  def schemaPredefined(self, inUrl, parametrs):
    # logger.debug('schemaPredefined enter  parametrs: ' + str(parametrs))
    for paramKey in parametrs:
      macroName = '%' + paramKey + '%'
      if inUrl.find(macroName) >= 0:

        paramList = []
        frequencyList = []
        timeList = []
        elements = {}

        if self.indexStruct is not None and paramKey in self.indexStruct:
          elements.update(self.indexStruct[paramKey])
          # logger.debug('elements1: ' + str(elements))
          for val in parametrs[paramKey]:
            if val not in self.indexStruct[paramKey]:
              elements.update({val:{"frequency":0, "time":0}})
              self.indexStruct[paramKey].update(elements)
          # logger.debug('elements3: ' + str(elements))
        else:
          for val in parametrs[paramKey]:
            elements.update({val:{"frequency":0, "time":0}})
          # logger.debug('elements2: ' + str(elements))
          self.indexStruct = {paramKey:elements}

        for key, element in elements.items():
          if "frequency" in element and "time" in element:
            paramList.append(key)
            frequencyList.append(int(element["frequency"]))
            timeList.append(int(element["time"]))

          # logger.debug('key: ' + str(key))
          # logger.debug('element: ' + str(element))

        mixIndex = frequencyList.index(min(frequencyList))
        logger.debug('mixIndex: ' + str(mixIndex))
        logger.debug('paramList[mixIndex]: ' + str(paramList[mixIndex]))

        logger.debug('>>> inUrl 1: ' + str(inUrl))
        inUrl = unicode(inUrl.replace(macroName, paramList[mixIndex]))
        logger.debug('>>> inUrl 2: ' + str(inUrl))
        frequencyList[mixIndex] += 1
        timeList[mixIndex] = int((datetime.now() - datetime.fromtimestamp(0)).total_seconds())

        # logger.debug('>>> self.indexStruct: ' + str(self.indexStruct))
        # logger.debug('self.indexStruct[paramKey] 1: ' + str(self.indexStruct[paramKey]))
        self.indexStruct[paramKey].update({paramList[mixIndex]:{"frequency":frequencyList[mixIndex], \
                                                              "time":timeList[mixIndex]}})
        # logger.debug('self.indexStruct[paramKey] 2: ' + str(self.indexStruct[paramKey]))

    return inUrl


  # #Method schemaIncrementalInt implements incremental int schema algorithm
  #
  # @param inUrl - incoming url
  # @param parametrs - incoming schema params
  # @param maxItems - count max items
  # @return processed url
  def schemaIncrementalInt(self, inUrl, parameters, maxItems):
    logger.debug("schemaIncrementalInt() enter ... parameters: " + str(parameters) + "\ninUrl: " + str(inUrl) + \
                 "\nmaxItems: " + str(maxItems))
    # variable for result
    ret = []
    # localRet = inUrl
    for paramKey in parameters:
      macroName = '%' + paramKey + '%'
      if inUrl.find(macroName) >= 0:
#        index = parameters[paramKey]["min"]
#        logger.debug("index = " + str(index))
#        if self.indexStruct is not None and paramKey in self.indexStruct:
#          index = self.indexStruct[paramKey]
#          logger.debug("index = " + str(index))
#
#        if index >= parameters[paramKey]["min"] and index <= parameters[paramKey]["max"]:
#          logger.debug("Before replace inUrl = " + str(inUrl))
#          inUrl = inUrl.replace(macroName, str(index))
#          logger.debug("After replace inUrl = " + str(inUrl))
#        else:
#          logger.debug("!!! continue !!!")
#          continue
#
#        logger.debug("self.indexStruct: " + varDump(self.indexStruct))
#        if self.indexStruct is not None:
#          logger.debug("Old index = " + str(index))
#          index += parameters[paramKey]["step"]
#          if index > parameters[paramKey]["max"]:
#            index = parameters[paramKey]["min"]
#          self.indexStruct[paramKey] = index
#          logger.debug("New index = " + str(index))

        if maxItems > int(parameters[paramKey]["max"]):
          ret = self.replaceSchemaIncrementalInt(inUrl,
                                                 macroName,
                                                 int(parameters[paramKey]["min"]),
                                                 int(parameters[paramKey]["max"]),
                                                 int(parameters[paramKey]["step"]))
        else:
          logger.debug("Start self.indexStruct: %s", varDump(self.indexStruct))
          minPos = 0
          if self.indexStruct is not None and paramKey in self.indexStruct:
            minPos = int(self.indexStruct[paramKey])
            logger.debug("minPos from structure = " + str(minPos))
          else:
            minPos = int(parameters[paramKey]["min"])

          nextPos = maxItems * int(parameters[paramKey]["step"]) + minPos
          if nextPos >= int(parameters[paramKey]["max"]):
            nextPos = int(parameters[paramKey]["max"])

          ret = self.replaceSchemaIncrementalInt(inUrl,
                                                 macroName,
                                                 minPos,
                                                 nextPos,
                                                 int(parameters[paramKey]["step"]))

          if self.indexStruct is None:
            self.indexStruct = {}

          logger.debug("nextPos = " + str(nextPos))
          if nextPos >= int(parameters[paramKey]["max"]):
            nextPos = 0

          logger.debug("nextIndex after truncate = " + str(nextPos))
          self.indexStruct[paramKey] = nextPos

        logger.debug("Finish self.indexStruct: %s", varDump(self.indexStruct))

    return ret


  # # Method replaceSchemaIncrementalInt using for incremental int schema algorithm
  #
  # @param inUrl - incoming url
  # @param macroName - macro name
  # @param minPos - min pos
  # @param minPos - max pos
  # @param step - step
  # @return processed url and last pos
  def replaceSchemaIncrementalInt(self, inUrl, macroName, minPos, maxPos, step):
    # variable for result
    ret = []
    localRet = inUrl
    for x in range(minPos, maxPos, step):
      localUrl = copy.copy(inUrl)
      logger.debug("Before replace inUrl = " + str(localUrl))
      localUrl = localUrl.replace(macroName, str(x))
      logger.debug("After replace inUrl = " + str(localUrl))

      if localRet != localUrl and localUrl not in ret:
        ret.append(localUrl)

    return ret


  # #Method schemaRandomInt implements random int schema algorithm
  #
  # @param inUrl - incoming url
  # @param parametrs - incoming schema params
  # @return processed url
  def schemaRandomInt(self, inUrl, parametrs):
    for paramKey in parametrs:
      macroName = '%' + paramKey + '%'
      if inUrl.find(macroName) >= 0:
        inUrl = inUrl.replace(macroName, str(random.randint(parametrs[paramKey]["min"], parametrs[paramKey]["max"])))
    return inUrl


  # #Method schemaRandomStr implements random string schema algorithm
  #
  # @param inUrl - incoming url
  # @param parametrs - incoming schema params
  # @return processed url
  def schemaRandomStr(self, inUrl, parametrs):
    lowAsciiSet = string.ascii_lowercase
    hexdigitsSet = ''.join([ch for ch in string.hexdigits if not ch.isupper()])
    for paramKey in parametrs:
      macroName = '%' + paramKey + '%'
      if inUrl.find(macroName) >= 0:
        valueLen = random.randint(parametrs[paramKey]["min"], parametrs[paramKey]["max"])
        valueStr = ''
        for _ in xrange(0, valueLen):
          if parametrs[paramKey]["chars"] == self.CHAR_ASCII_LATIN:
            valueStr += lowAsciiSet[random.randint(0, len(lowAsciiSet) - 1)]
          elif parametrs[paramKey]["chars"] == self.CHAR_HEXADECIMAL:
            valueStr += hexdigitsSet[random.randint(0, len(hexdigitsSet) - 1)]
        if parametrs[paramKey]["case"] == self.CHAR_LOWER:
          valueStr = valueStr.lower()
        elif parametrs[paramKey]["case"] == self.CHAR_UPPER:
          valueStr = valueStr.upper()
        inUrl = inUrl.replace(macroName, valueStr)
    return inUrl


  # #Method saveJsonInFile saves indexes structute into the file
  #
  # @param fileName - incoming file name
  def saveJsonInFile(self, fileName):
    if self.indexStruct is not None and len(self.indexStruct) > 0 and fileName is not None:
      fd = None
      try:
        fd = open(fileName, "w")
        if fd is not None:
          fd.write(json.dumps(self.indexStruct, ensure_ascii=False))
          fd.close()
      except Exception, err:
        ExceptionLog.handler(logger, err, ">>> saveJsonInFile error, file name = " + str(fileName))
        if fd is not None:
          fd.close()


  # #Method resolveParametersByHTTP
  #
  # @param urls - list of external sources urls
  # @param defaultValue - default for return value
  # @return new parameters value, fetched by http
  def resolveParametersByHTTP(self, urls, defaultValue=None):
    if defaultValue is None:
      ret = {}
    else:
      ret = defaultValue
    newParams = None
    for url in urls:
      result = None
      try:
        result = requests.get(url)
      except Exception as excp:
        self.externalError = APP_CONSTS.ERROR_URLS_SCHEMA_EXTERNAL
        logger.debug(">>> bad url request; url=" + url + ";err= " + str(excp))
      if result is not None and result.status_code == 200 and result.text is not None:
        try:
          newParams = json.loads(result.text)
        except Exception as excp:
          self.externalError = APP_CONSTS.ERROR_URLS_SCHEMA_EXTERNAL
          logger.debug(">>> bad external parameters json" + str(excp))
      if newParams is not None:
        ret = newParams
        self.externalError = APP_CONSTS.ERROR_OK
        break
    return ret


  # #Method resolveParametersByFormat
  #
  # @param parameters - input parameters for resolve
  # @param delimiter - delimiter value using for split text
  # @param formatValue - format field value
  # @param defaultValue - default for return value
  # @return new parameters value, fetched by 'format' url schema property
  def resolveParametersByFormat(self, parameters, delimiter=' ', formatValue='json', defaultValue=None):
    # variable for result
    ret = defaultValue
    logger.debug('!!! parameters: ' + str(parameters))

    if formatValue == 'plain-text':
      for paramName in parameters:
        logger.debug("paramName: '" + str(paramName) + "' type: " + str(type(paramName)))
        logger.debug("paramValue: '" + str(parameters[paramName]) + "' type: " + str(type(parameters[paramName])))

        if isinstance(parameters[paramName], basestring):
          if delimiter == "":
            # split don't use delimiter
            parameters[paramName] = unicode(parameters[paramName]).splitlines()
          else:
            # split use delimiter
            parameters[paramName] = unicode(parameters[paramName]).split(delimiter)

          # remove empty strings from list
          parameters[paramName] = [elem for elem in parameters[paramName] if elem]

      ret = parameters
      logger.debug('!!! ret: ' + str(ret))

    elif formatValue == 'json':
      ret = parameters
    else:
      logger.error("Unsupported format value: '" + str(formatValue) + "'")

    return ret


  # #Method urlEncodeToParameters
  #
  # @param parameters - input parameters for resolve
  # @param urlEncode - urlEncode flag value
  # @return new parameters value, url encoded if neccesary
  def urlEncodeToParameters(self, parameters, urlEncode):
    # variable for result
    ret = parameters
    # logger.debug('>>>>> parameters: ' + str(parameters))

    if urlEncode is not None and int(urlEncode) > 0:
      for paramName in parameters:
        if isinstance(parameters[paramName], list) or isinstance(parameters[paramName], unicode):
          paramsList = []
          for elem in parameters[paramName]:
            if isinstance(elem, str) or isinstance(elem, unicode):
              try:
                encodedStr = urllib.urlencode({'':elem})
                if len(encodedStr) > 0 and encodedStr[0] == '=':
                  encodedStr = encodedStr[1:]
                paramsList.append(encodedStr)
              except Exception, err:
                logger.debug("urlencode '" + str(elem) + "' has error: " + str(err))
                paramsList.append(unicode(elem))

          parameters[paramName] = paramsList

      ret = parameters
      # logger.debug('>>>>> ret: ' + str(ret))

    return ret


  # #Method getMaxCountParameters
  #
  # @param parameters - input parameters
  # @return max count of parameters list
  def getMaxCountParameters(self, parameters):
    countsList = [0]
    for values in parameters.values():
      # logger.debug('>>> values: ' + str(values))
      if isinstance(values, list):
        countsList.append(len(values))

    return max(countsList)


  # #Method resolveParametersFromFile
  #
  # @param fileName - input file name
  # @param  default for return value
  # @return new parameters value, fetched from file
  def resolveParametersFromFile(self, fileName, defaultValue=None):
    logger.debug(">>> resolveParametersFromFile enter  fileName: " + str(fileName))
    # variable for result
    ret = defaultValue
    parameters = {}

    if fileName.find(self.JSON_SUFF) == len(fileName) - len(self.JSON_SUFF):

      fd = None
      try:
        fd = open(fileName, "r")
        if fd is not None:
          buff = fd.read()
          if len(buff) > 0 and buff[0] == '{':  # maybe 'json'
            parameters = json.loads(buff)
          else:
            parameters = {"":buff}  # maybe 'plain-text'

      except Exception, err:
        logger.debug(">>> resolveParametersFromFile error, file name = " + str(fileName) + " | " + str(err))
      finally:
        if fd is not None:
          fd.close()

      if len(parameters) > 0:
        ret = parameters
    else:
      logger.debug("Wrong file name: '" + str(fileName) + "', expected  '<file_name>.json'")

    return ret


  # #Method generateUrlSchema main class public point, whcih
  #
  # @param inUrl - incoming url
  # @return processed url
  def generateUrlSchema(self, inUrl):
    ret = []
    itemsLen = 1
    if self.schema is not None:
      try:
        if "urls" in self.schema:
          self.schema["parameters"] = self.resolveParametersByHTTP(self.schema["urls"])

        if "file_path" in self.schema:
          self.schema["parameters"] = self.resolveParametersFromFile(self.schema["file_path"], \
                                                                     self.schema["parameters"])

        # logger.debug('self.schema["parameters"]: ' + str(self.schema["parameters"]))

        if "format" in self.schema:
          delimiter = ' '
          if "delimiter" in self.schema:
            delimiter = self.schema["delimiter"]
          self.schema["parameters"] = self.resolveParametersByFormat(self.schema["parameters"], delimiter, \
                                                                         self.schema["format"], \
                                                                         self.schema["parameters"])

        if "url_encode" in self.schema:
          self.schema["parameters"] = self.urlEncodeToParameters(self.schema["parameters"], self.schema["url_encode"])

        if "batch_insert" in self.schema and \
        int(self.schema["batch_insert"]) >= self.BATCH_INSERT_MIN_ALLOWED_VALUE and \
        int(self.schema["batch_insert"]) <= self.BATCH_INSERT_MAX_ALLOWED_VALUE:
          self.batchInsert = int(self.schema["batch_insert"])

        # get max count parameters
        maxCountParameters = self.getMaxCountParameters(self.schema["parameters"])
        logger.debug('maxCountParameters: ' + str(maxCountParameters))

        if self.schema["mode"] == self.MODE_LIST_URLS:
          itemsLen = int(self.schema["max_items"])
        for _ in xrange(0, itemsLen):
          localRet = inUrl
          if self.schema["type"] == self.SCHEMA_PREDEFINED:
            localRet = self.schemaPredefined(inUrl, self.schema["parameters"])

          elif self.schema["type"] == self.SCHEMA_INCREMENTAL_INT:
            # localRet = self.schemaIncrementalInt(inUrl, self.schema["parameters"])
            # get full urls list
            ret = self.schemaIncrementalInt(inUrl, self.schema["parameters"], itemsLen)

          elif self.schema["type"] == self.SCHEMA_RANDOM_INT:
            localRet = self.schemaRandomInt(inUrl, self.schema["parameters"])

          elif self.schema["type"] == self.SCHEMA_RANDOM_STR:
            localRet = self.schemaRandomStr(inUrl, self.schema["parameters"])

          if localRet != inUrl and localRet not in ret:
            ret.append(localRet)
            if len(ret) >= int(maxCountParameters):
              logger.debug('>>> break   len(ret) = ' + str(len(ret)))
              break
          else:
            break
      except Exception as excp:
        ExceptionLog.handler(logger, excp, ">>> generateUrlSchema has some error")
      self.saveJsonInFile(self.indexFileName)
    logger.debug(">>> urlSchema len = " + str(len(ret)))
    return ret
