#coding: utf-8
"""
HCE project,  Python bindings, DC service utility.
ResponseExtractor utility main application class.

@package: DC utility
@file ResponseExtractor.py
@author bgv <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import sys
import json
import base64
import time
import logging.config
import ConfigParser
from cement.core import foundation

import app.Utils as Utils
from app.Utils import ExceptionLog
import app.Consts as APP_CONSTS
import dc_crawler.Constants as DC_CRAWLER_CONSTS


## ResponseExtractor Class main functional,
# class inherits from foundation.CementApp
#
class ResponseExtractor(foundation.CementApp):

  ## Constants error messages used in class
  MSG_ERROR_PARSE_CMD_PARAMS = "Error parse command line parameters."
  MSG_ERROR_EMPTY_CONFIG_FILE_NAME = "Config file name is empty."
  MSG_ERROR_WRONG_CONFIG_FILE_NAME = "Config file name is wrong"
  MSG_ERROR_LOAD_APP_CONFIG = "Error loading application config file."
  MSG_ERROR_READ_LOG_CONFIG = "Error read log config file."
  MSG_ERROR_PROCESSING_REQUEST = "Error processing input data."

  CONFIG_OPTION_ITEM_DELIMITER = "itemDelimiter"

  FROMAT_AUTO = -1
  FROMAT_INTERNAL = 0
  FROMAT_NEWS = 1
  FROMAT_RSS_FEED = 2

  RESULTS_FORMAT_CSV_LINE = 0
  RESULTS_FORMAT_FIELD_LINE = 1
  RESULTS_FORMAT_JSON = 2

  # Options from config file
  CONFIG_OPTION_LOG = 'log'


  # Mandatory
  class Meta(object):
    label = DC_CRAWLER_CONSTS.RTC_PREPROCESSOR_APP_NAME
    def __init__(self):
      pass


  ##constructor
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)

    self.logger = None
    self.batch = None
    self.exitCode = APP_CONSTS.EXIT_SUCCESS
    self.initTagsUniqueHashConfig = ''
    self.initTagsLimitsConfig = ''
    self.extendedLog = False
    self.results = self.RESULTS_FORMAT_JSON
    self.itemDelimiter = "\n"

  ## setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)
    self.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file')
    self.args.add_argument('-i', '--input', action='store', metavar='input_json_file',
                           help='input json file of the URL_CONTENT response, if omitted the stdin read used')
    self.args.add_argument('-o', '--output', action='store', metavar='output_file, if omitted the stdout print used',
                           help='input file, if omitted the stdout write used')
    self.args.add_argument('-f', '--format', action='store', metavar='input_json_file_format',
                           help='input json file buffer format: -1 - auto (default if omitted) 0 - internal,' + \
                            ' 1 - news, 2 - rss-feed')
    self.args.add_argument('-m', '--maxitems', action='store', metavar='max_items',
                           help='max items number to read')
    self.args.add_argument('-s', '--start', action='store', metavar='start_from',
                           help='start from item')
    self.args.add_argument('-e', '--extended', action='store', metavar='extended',
                           help='extended log with additional debug information')
    self.args.add_argument('-t', '--tags', action='store', metavar='tags',
                           help='csv tags fields names list, all fields from response if omitted')
    self.args.add_argument('-r', '--results', action='store', metavar='results',
                           help='results format: 0 - csv fields names list one item per line, ' + \
                           '1 - fields list one field per line, 2 - json (default if omitted)')


  ##load application config file
  #
  #@param configName - name of application config file
  #@return - log config file name
  def __loadAppConfig(self, configName):
    #variable for result
    confLogFileName = ""

    try:
      config = ConfigParser.ConfigParser()
      config.optionxform = str

      readOk = config.read(configName)

      if len(readOk) == 0:
        raise Exception(self.MSG_ERROR_WRONG_CONFIG_FILE_NAME + ": " + configName)

      if config.has_section(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME):
        confLogFileName = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME, self.CONFIG_OPTION_LOG))
        #Init response item delimiter
        self.itemDelimiter = str(config.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                                            self.CONFIG_OPTION_ITEM_DELIMITER))
    except Exception, err:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG + ' ' + str(err))

    return confLogFileName


  ##load log config file
  #
  #@param configName - name of log rtc-finalizer config file
  #@return - None
  def initLogger(self, configName):
    try:
      if isinstance(configName, str) and len(configName) == 0:
        raise Exception(self.MSG_ERROR_EMPTY_CONFIG_FILE_NAME)

      logging.config.fileConfig(configName)

      #call rotation log files and initialization logger
      self.logger = Utils.MPLogger().getLogger()

    except Exception, err:
      raise Exception(self.MSG_ERROR_READ_LOG_CONFIG + ' ' + str(err))


  ##Read file
  #
  #@param inFile - name of file to read
  #@return - the buffer
  def readFile(self, templateFile):
    with open(templateFile, 'r') as f:
      ret = f.read()

    return ret


  ##Write file
  #
  #@param fileName - name of file to write
  #@param outBuffer - buffer to write
  def writeFile(self, fileName, outBuffer):
    with open(fileName, 'w') as f:
      f.write(outBuffer)


  ## run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    startTime = time.time()

    if self.pargs.config:
      self.initLogger(self.__loadAppConfig(self.pargs.config))
    else:
      raise Exception(self.MSG_ERROR_LOAD_APP_CONFIG)

    if self.pargs.input:
      inputBuffer = self.readFile(self.pargs.input)
    else:
      inputBuffer = sys.stdin.read()

    if self.pargs.format:
      inputFormat = int(self.pargs.format)
    else:
      inputFormat = -1

    if self.pargs.maxitems:
      maxItems = int(self.pargs.maxitems)
    else:
      maxItems = -1
    if self.pargs.start:
      startFrom = int(self.pargs.start)
    else:
      startFrom = 0

    if self.pargs.extended:
      self.extendedLog = bool(int(self.pargs.extended))
    else:
      self.extendedLog = True

    if self.pargs.tags:
      tags = self.pargs.tags.split(',')
    else:
      tags = None

    if self.pargs.results:
      self.results = int(self.pargs.results)

    # call processing
    outputBuffer = self.process(inputBuffer, inputFormat, maxItems, startFrom, tags)

    self.logger.info("Total time: %s", str(time.time() - startTime))

    if self.pargs.output:
      self.writeFile(self.pargs.output, outputBuffer)
    else:
      print outputBuffer
      sys.stdout.flush()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)


  ##Make output content by substitution of the template's parts
  #
  #@param contentObj the object from response item in News format
  #@param tags - list of the tags names
  #@return the dict of tags and values
  def getNewsItem(self, contentObj, tags=None):
    ret = {}

    if self.extendedLog:
      self.logger.debug("News format item processing:\n%s", str(contentObj))

    if tags is None:
      ret = contentObj
    else:
      #For each tag in the content object
      for tagName in contentObj:
        if tagName in tags:
          ret[tagName] = self.getTagValueByName(tagName, contentObj, self.FROMAT_NEWS)

    return ret


  ##Make output content by substitution of the template's parts
  #
  #@param contentObj the object from response item in the default internal format
  #@param tags - list of the tags names
  #@return the dict of tags and values
  def getDefaultItem(self, contentObj, tags=None):
    ret = {}

    if 'default' in contentObj and 'data' in contentObj['default'] and 'tagList' in contentObj['default']['data'] and\
     isinstance(contentObj['default']['data']['tagList'], list) and len(contentObj['default']['data']['tagList']) > 0:
      contentObj = contentObj['default']['data']['tagList'][0]
    else:
      raise Exception('Wrong format of the contentObj, structure checks not passed!')

    if self.extendedLog:
      self.logger.debug("Internal format item processing:\n%s", str(contentObj))

    #For each tag in the content object
    for tagItem in contentObj:
      tagName = tagItem['name']
      if tagName in tags:
        tagValue = self.getTagValueByName(tagName, contentObj, self.FROMAT_INTERNAL)
        ret[tagName] = tagValue

    return ret


  ##Check is tag present in response item by the name
  #
  #@param tagName the name of the tag
  #@param item - the one tags set item of the itemObject in the scraper response
  #@param responseFormat - format of the scraper response
  #@return true if tag is present
  def getTagValueByName(self, tagName, item, responseFormat):
    ret = ''

    if responseFormat == self.FROMAT_NEWS:
      if tagName in item:
        ret = item[tagName].decode('string_escape')
      else:
        if self.extendedLog:
          self.logger.debug("Tag `%s` not found as News format, empty value assumed", tagName)
    elif responseFormat == self.FROMAT_INTERNAL:
      found = False
      for tag in item:
        if tag['name'] == tagName:
          found = True
          if len(tag['data']) > 0:
            ret = tag['data'][0].decode('string_escape')
          break
      if not found and self.extendedLog:
        self.logger.debug("Tag `%s` not found as internal format, empty value assumed", tagName)
    else:
      if self.extendedLog:
        self.logger.debug("Format %s not supported", str(responseFormat))

    return ret


  ##Parse the input json and make output collection
  #
  #@param inputObject json
  #@param inputFormat of the inputObject
  #@param maxItems - max items to process
  #@param startFrom - processing start from item
  #@param tags - list of tags names to get
  #@return the output buffer after all macro variables are substituted
  def parse(self, inputObject, inputFormat, maxItems=-1, startFrom=0, tags=None):
    ret = []

    i = 0
    s = 0

    #For all items in URLContent response accumulate doc and toc buffers
    for item in inputObject["itemsList"][0]["itemObject"]:
      if maxItems > -1 and i == maxItems:
        break

      if startFrom > 0 and s < startFrom:
        s += 1
        continue

      if len(item["processedContents"]) > 0:
        try:
          contentObj = json.loads(base64.b64decode(item["processedContents"][0]["buffer"]), encoding='utf-8')
        except Exception, err:
          self.logger.error("Error get contentObj or cDate: %s, possible wrong json in buffer:\n%s", str(err),
                            str(item["processedContents"][0]["buffer"]))
          continue

        if inputFormat < 0:
          inputFormatLocal = self.detectFormat(contentObj)
          if inputFormatLocal is None:
            self.logger.info("Unsupported item object format or empty list:\n%s", str(contentObj))
            continue
        try:
          if inputFormatLocal == self.FROMAT_INTERNAL:
            #Process default internal object format
            item = self.getDefaultItem(contentObj, tags)
          elif inputFormatLocal == self.FROMAT_NEWS:
            #Process NEWS format of response
            item = self.getNewsItem(contentObj[0], tags)
          elif inputFormatLocal == self.FROMAT_RSS_FEED:
            #TODO: process RSS-FEED format of response
            continue
          ret.append(item)
          i += 1
        except (KeyboardInterrupt, SystemExit):
          raise
        except Exception, err:
          self.logger.error("Error process item: %s, contentObj:\n%s", str(err), str(contentObj))
          self.logger.debug("%s", Utils.getTracebackInfo())
          continue

    self.logResultedStatistics(inputObject, i)

    return ret


  ##Detects the format of response object
  #
  #@param inputObject
  #@param items in results set
  def logResultedStatistics(self, inputObject, items):
    self.logger.debug("Items detected %s, output: %s", str(len(inputObject["itemsList"][0]["itemObject"])), str(items))


  ##Detects the format of response object
  #
  #@param contentObj response object
  #@return format code
  def detectFormat(self, contentObj):
    #self.logger.info("Type `%s`, contentObj:\n%s", str(type(contentObj)), str(contentObj))
    #Auto-detect format
    if isinstance(contentObj, dict):
      #Default internal format
      inputFormat = self.FROMAT_INTERNAL
    elif isinstance(contentObj, list) and len(contentObj) > 0:
      #News format
      inputFormat = self.FROMAT_NEWS
    else:
      #Unsupported format
      inputFormat = None

    return inputFormat


  ##Parse json and return dict if okay or None if not
  #
  #@param jsonString json to pars
  #@return resulted dict
  def jsonLoadsSafe(self, jsonString):
    ret = None

    try:
      if jsonString is not None:
        ret = json.loads(jsonString)
    except Exception, err:
      self.logger.error("Error pars json: %s\n%s", str(err), jsonString)

    return ret


  ##process main operations
  #
  #@param inputBuffer - te input buffer, supposes the json from DCC URL_CONTENT response
  #@param inputFormat of the input buffer, including News, Template, RSS-Feed and so on
  #@param maxItems - max items
  #@param startFrom - start from item
  #@param tags list of tags names
  #@return formatted string buffer
  def process(self, inputBuffer, inputFormat=FROMAT_AUTO, maxItems=-1, startFrom=0, tags=None):
    ret = ''

    try:
      self.logger.debug("Processing started, tags: %s", str(tags))

      inputObject = json.loads(inputBuffer, encoding='utf-8')

      items = self.parse(inputObject, inputFormat, maxItems, startFrom, tags)

      #Make output string buffer
      if self.results == self.RESULTS_FORMAT_JSON:
        ret = json.dumps(items, indent=2, ensure_ascii=False, encoding='utf-8')
      elif self.results == self.RESULTS_FORMAT_CSV_LINE:
        for item in items:
          buf = ''
          for tagName in item:
            buf += tagName + '=' + item[tagName] + ','
          if buf[:-1].strip() != '':
            ret += buf[:-1] + self.itemDelimiter.replace("\\n", "\n")
      elif self.results == self.RESULTS_FORMAT_FIELD_LINE:
        for item in items:
          buf = ''
          for tagName in item:
            buf += tagName + '=' + item[tagName] + "\n"
          if buf[:-1].strip() != '':
            ret += buf[:-1] + self.itemDelimiter.replace("\\n", "\n")
      else:
        pass

    except Exception, err:
      ExceptionLog.handler(self.logger, err, "Error:")
      raise Exception(self.MSG_ERROR_PROCESSING_REQUEST + ' ' + str(err))

    return ret

