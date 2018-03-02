"""@package docstring
 @file Scraper.py
 @author Alexey, bgv <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""

import time
import pickle
import sys
import json
import logging.config
import ConfigParser
from cement.core import foundation
import dc_processor.Constants as CONSTS
from dc_processor.scraper_result import Result
from dc_processor.scraper_utils import encode
from dc_processor.ScraperResponse import ScraperResponse
import app.Utils as Utils  # pylint: disable=F0401
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Profiler
import app.Consts as APP_CONSTS

APP_NAME = "ProcessorFeedParser"

#
class ProcessorFeedParser(foundation.CementApp):


  # Mandatory
  class Meta(object):
    label = APP_NAME
    def __init__(self):
      pass


  # #constructor
  # initialize default fields
  def __init__(self, usageModel=APP_CONSTS.APP_USAGE_MODEL_PROCESS, configFile=None, logger=None, inputData=None):
    if usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class __init__ method
      foundation.CementApp.__init__(self)

    self.exit_code = CONSTS.EXIT_SUCCESS
    self.logger = logger
    self.config_db_dir = None
    self.sqliteTimeout = CONSTS.SQLITE_TIMEOUT
    self.entry = None
    self.tagsCount = None
    self.tagsMask = None
    self.pubdate = None
    self.processedContent = None
    self.store_xpath = False
    self.db_engine = CONSTS.MYSQL_ENGINE
    self.article = None
    self.input_data = inputData
    self.articles_tbl = None
    self.PRAGMA_synchronous = None
    self.PRAGMA_journal_mode = None
    self.PRAGMA_temp_store = None
    self.usageModel = usageModel
    self.configFile = configFile
    self.output_data = None



  # #setup
  # setup application
  def setup(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class setup method
      foundation.CementApp.setup(self)


  # #run
  # run application
  def run(self):
    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # call base class run method
      foundation.CementApp.run(self)

    # config section
    self.loadConfig()

    # load logger config file
    self.loadLogConfigFile()

    # load sqlite db backend
    # self.loadSqliteDBBackend()

    # sqlite
    # self.loadDBBackend()

    # options
    self.loadOptions()

    #Do applied algorithm's job
    self.processBatch()

    if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
      # Finish logging
      self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)



  # #main content processing
  # main content processing
  #
  def createArticle(self):
    #self.logger.debug("self.entry: %s" % varDump(self.entry))

    article = Result(self.config, self.entry["urlMd5"])
    extractor = self.__class__.__name__

    for tag in self.entry["entry"]:
      tagValue = self.entry["entry"][tag]
      if isinstance(tagValue, (str, unicode)):
        if tag == 'link':
          tagValue = Utils.UrlNormalizator.entitiesEncode(tagValue)
        else:
          tagValue = tagValue
      elif isinstance(tagValue, int) or isinstance(tagValue, bool) or isinstance(tagValue, float):
        tagValue = str(tagValue)
      elif isinstance(tagValue, dict):
        names = {"url", "name", "value"}
        tagValueNew = None
        for name in names:
          if name in tagValue and isinstance(tagValue[name], (str, unicode)):
            if name == 'url':
              tagValueNew = Utils.UrlNormalizator.entitiesEncode(tagValue[name])
            else:
              tagValueNew = tagValue[name]
            break
        if tagValueNew is None:
          tagValue = ""
        else:
          tagValue = tagValueNew
      elif isinstance(tagValue, list) and len(tagValue) > 0:
        tagValueNew = None
        if isinstance(tagValue[0], dict):
          names = {"href":",", "url":",", "name":",", "term":",", "value":" "}  # pylint: disable=R0204
          for name in names:
            if name in tagValue[0]:
              tv = []
              for item in tagValue:
                if name in item and isinstance(item[name], (str, unicode)):
                  if name == 'href':
                    tv.append(Utils.UrlNormalizator.entitiesEncode(item[name].strip()))
                  else:
                    tv.append(item[name].strip())
              tagValueNew = names[name].join(tv)
              break
        if tagValueNew is None:
          tagValue = ""
        else:
          tagValue = tagValueNew
      else:
        self.logger.debug("Unsupported tag '%s' value type: %s", str(tag), varDump(tagValue))
        tagValue = ""

      article.tags[tag] = {"data":[tagValue], "name":tag, "xpath":"", "extractor":extractor}

    #parent rss feed tag
    if "parent_rss_feed" in self.entry:
      parent_rss_feed = json.dumps(self.entry["parent_rss_feed"])
      if parent_rss_feed[0] == '"':
        parent_rss_feed = parent_rss_feed[1:]
      if parent_rss_feed[-1] == '"':
        parent_rss_feed = parent_rss_feed[:-1]
      article.tags["parent_rss_feed"] = {"data":[parent_rss_feed],
                                         "name":"parent_rss_feed", "xpath":"", "extractor":extractor}

    #parent rss feed urlMd5 tag
    if "parent_rss_feed_urlMd5" in self.entry:
      article.tags["parent_rss_feed_urlMd5"] = {"data":[self.entry["parent_rss_feed_urlMd5"]],
                                                "name":"parent_rss_feed_urlMd5", "xpath":"", "extractor":extractor}

    #tags count
    article.tagsCount = len(article.tags.keys())

    # Finish time
    article.finish = time.time()

    # Set final article
    self.article = article
    #self.logger.debug("article: %s" % varDump(article))



  # #main content processing
  # main content processing
  #
  def parseFeed(self):
    ret = True
    try:
      self.entry = json.loads(self.input_data.raw_content)
      self.createArticle()
      #self.putArticleToDB({"default":self.article})
    except ValueError, err:
      ExceptionLog.handler(self.logger, err, 'Bad raw content:', (self.input_data.raw_content), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      ret = False
    return ret


  # #main content processing
  # main content processing
  #
  def process(self):
    self.logger.debug("URL: %s" % str(self.input_data.url))
    self.logger.debug("URLMd5: %s" % str(self.input_data.urlId))
    self.logger.debug("SiteId: %s" % str(self.input_data.siteId))
    if self.parseFeed():
      self.tagsCount = self.article.tagsCount
      self.tagsMask = self.article.tagsMask
      # TODO: strange level "default", possible need to be removed and new common object need to be used by all scrapers
      self.article.get()
      self.processedContent = {"default":self.article}
      self.processedContent["internal"] = [self.article]
      self.processedContent["custom"] = []
      # correct pubdate
      if CONSTS.PUBLISHED in self.article.tags:
        from dateutil.parser import parse
        self.pubdate = parse(self.article.tags[CONSTS.PUBLISHED]["data"][0]).strftime('%Y-%m-%d %H:%M:%S')
      else:
        self.logger.debug("Resource %s hasn't publish date" % str(self.article.tags[CONSTS.TAG_LINK]["data"]))
      # for ml
      if self.store_xpath:
        self.storeXPath()
    else:
      self.logger.debug("Resource hasn't raw content. Exit.")


  ## For
  #
  def getQueryPrefix(self):
    query_prefix = None
    if self.db_engine == CONSTS.MYSQL_ENGINE:
      query_prefix = "REPLACE INTO `contents_" + str(self.input_data.siteId if len(self.input_data.siteId) else 0)
    else:
      self.logger.info("DB Backend %s not supported" % str(self.db_engine))
    self.logger.info("db_name: " + query_prefix)
    return query_prefix


  ## getDataBuffer
  ## prepare data buffer
  #
  def getDataBuffer(self, data):
    buf = {}
    for key in data.keys():
      data[key].get()
      buf[key] = data[key].data
    ret = encode(json.dumps(buf))
    self.logger.info("Result buffer: %s" % ret)
    return ret


  #TODO: Seems need to remove obsolete functionality
  def putArticleToDB(self, result):
    # Check if Content extracted
    self.logger.info("Result: %s" % varDump(result))
    tags_count = int(result["default"].tagsCount)
    self.logger.info("Tags count: %s" % str(tags_count))
    if int(tags_count) > 0:
      self.logger.info("Tags count OK")

      # Get DB table name
      query_prefix = self.getQueryPrefix()

      # Prepare query
      # Firstly, prepare data buffer
      data = self.getDataBuffer(result)
      # Then, insert data buffer to the query
      #query = query_prefix + "`(`id`,`data`, CDate) VALUES('" \
      #  + result.resId + "', '" + encode(result.get()) + "', strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime'))"
      query = query_prefix + "`(`id`,`data`, CDate) VALUES('" + result["default"].resId + "', '" + data + "', NOW())"

      # Initialize options for DB Backend
      options = {}
      # Genaral options
      options["query"] = query
      self.logger.info("DB Backend %s" % str(self.db_engine))

      if self.db_engine == CONSTS.MYSQL_ENGINE:
        # MYSQL options
        options["dbHost"] = self.dbHost  # pylint: disable=E1101
        options["dbPort"] = self.dbPort  # pylint: disable=E1101
        options["dbUser"] = self.dbUser  # pylint: disable=E1101
        options["dbPWD"] = self.dbPWD  # pylint: disable=E1101
        options["MYSQLDBName"] = self.dc_contents_db  # pylint: disable=E1101
        #TODO: remove obsolete functionality
        #Utils.putContentToMYSQLDB(result, options)
      else:
        self.logger.info("DB Backend %s not supported" % str(self.db_engine))


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    try:
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        # read pickled batch object from stdin and unpickle it
        self.input_data = pickle.loads(sys.stdin.read())

      msgStr = "siteId=" + str(self.input_data.siteId) + ", urlId=" + str(self.input_data.urlId) + \
               ", url=" + str(self.input_data.url)
      self.logger.info("Incoming data:%s", msgStr)
      app.Profiler.messagesList.append(msgStr)
      self.logger.debug("self.input_data:%s\n", varDump(self.input_data))


      self.process()

      self.logger.info("Resulted tagsCount=%s, tagsMask=%s, pubdate=%s", str(self.tagsCount), str(self.tagsMask),
                       str(self.pubdate))

      scraperResponse = ScraperResponse(self.tagsCount, self.tagsMask, self.pubdate, self.processedContent)
      self.logger.debug("scraperResponse:%s\n", varDump(scraperResponse))

      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        print pickle.dumps(scraperResponse)
        sys.stdout.flush()
      else:
        self.output_data = scraperResponse
    except Exception as err:
      ExceptionLog.handler(self.logger, err, CONSTS.MSG_ERROR_PROCESS)
      self.exit_code = CONSTS.EXIT_FAILURE
      raise Exception(err)


  ## storeXpath
  #
  def storeXPath(self):
    ret = False
    '''
    from dc_processor.base_extractor import BaseExtractor
    # check content's presence in response
    if self.scraper_response.tagsMask & BaseExtractor.tagsMask[CONSTS.SUMMARY_DETAIL]:
      content = None
      tags = json.loads(self.scraper_response.processedContent)["data"]["tagList"]
      for tag in tags:
        if tag["name"]==CONSTS.SUMMARY_DETAIL:
          content = tag["data"]["value"]
          self.logger.debug("content: %s" % str(content))
          from scrapy.selector import Selector
          sel = Selector(text=self.raw_content)
          xpath_list = sel.xpath("//*[contains(., '" + content + "')]").extract()
          self.logger.debug("xpath_list: %s" % str(xpath_list))
    '''  # pylint: disable=W0105

    return ret



  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      self.config = ConfigParser.ConfigParser()
      self.config.optionxform = str
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        if self.pargs.config:
          self.config.read(self.pargs.config)
      else:
        self.config.read(self.configFile)
    except Exception as err:
      raise Exception(CONSTS.MSG_ERROR_LOAD_CONFIG + " : " + str(err))



  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      if self.usageModel == APP_CONSTS.APP_USAGE_MODEL_PROCESS:
        log_conf_file = self.config.get("Application", "log")
        logging.config.fileConfig(log_conf_file)
        self.logger = Utils.MPLogger().getLogger()
    except Exception as err:
      raise Exception(CONSTS.MSG_ERROR_LOAD_CONFIG + " : " + str(err))



  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    class_name = self.__class__.__name__
    try:
      self.config_db_dir = self.config.get(class_name, "config_db_dir")
      self.articles_tbl = self.config.get("sqlite", "articles_tbl")
      self.sqliteTimeout = self.config.getint("sqlite", "timeout")

      # support sqlite optimizer options
      if self.config.has_option("sqlite", "PRAGMA_synchronous"):
        self.PRAGMA_synchronous = self.config.get("sqlite", "PRAGMA_synchronous")
      if self.config.has_option("sqlite", "PRAGMA_journal_mode"):
        self.PRAGMA_journal_mode = self.config.get("sqlite", "PRAGMA_journal_mode")
      if self.config.has_option("sqlite", "PRAGMA_temp_store"):
        self.PRAGMA_temp_store = self.config.get("sqlite", "PRAGMA_temp_store")

      # support db backend
      if self.config.has_option(class_name, "db_engine"):
        self.db_engine = self.config.get(class_name, "db_engine")

    except Exception as err:
      print CONSTS.MSG_ERROR_LOAD_OPTIONS + err.message
      raise


  def getExitCode(self):
    return self.exit_code
