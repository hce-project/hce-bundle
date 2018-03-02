"""
  HCE project, Python bindings, Processor Manager application.
  Event objects definitions.

  @package: dc
  @file CrawlingOptimiser.py.py
  @author Oleksii <developers.hce@gmail.com>
  @author madk <developers.hce@gmail.com>
  @link: http://hierarchical-cluster-engine.com/
  @copyright: Copyright &copy; 2013-2014 IOIX Ukraine
  @license: http://hierarchical-cluster-engine.com/license/
  @since: 0.1
  """


import logging.config
import ConfigParser
from cement.core import foundation

import dc_co.Constants as CONSTS
import app.Consts as APP_CONSTS
import app.Utils as Utils  # pylint: disable=F0401
from dc_crawler.DBTasksWrapper import DBTasksWrapper



# #The CrawlerTask class, is a interface for fetching content from the web
#
# This object is a run at once application
class CrawlingOptimiser(foundation.CementApp):

  # Mandatory
  class Meta(object):
    label = CONSTS.APP_NAME
    def __init__(self):
      pass


  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.exit_code = CONSTS.EXIT_SUCCESS
    self.logger = None
    self.message_queue = []
    # self.url_table = None
    self.site_id = None
    self.recrawl_dict = {}
    self.site_features = {}
    self.local_wrapper = None
    self.remote_wrapper = None
    self.remote_host = None

  # #setup
  # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)
    self.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file')
    self.args.add_argument('-s', '--site', action='store', metavar='site alias', help='site alias')


  # #run
  # run application
  def run(self):
    # call base class run method
    foundation.CementApp.run(self)

    # config section
    self.loadConfig()

    # load logger config file
    self.loadLogConfigFile()

    # load mandatory options
    self.loadOptions()

    # make processing
    self.process()

    # Finish logging
    self.logger.info(APP_CONSTS.LOGGER_DELIMITER_LINE)



  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      self.config = ConfigParser.ConfigParser()
      self.config.optionxform = str

      # config argument
      if self.pargs.config:
        self.config.read(self.pargs.config)
        self.message_queue.append(CONSTS.MSG_INFO_LOAD_CONFIG_FILE + str(self.pargs.config))
      else:
        self.config.read(CONSTS.DEFAULT_CFG_FILE)
        self.message_queue.append(CONSTS.MSG_INFO_LOAD_DEFAULT_CONFIG_FILE + CONSTS.DEFAULT_CFG_FILE)

      # site argument
      if self.pargs.site:
        self.site_id = self.pargs.site
        self.message_queue.append(CONSTS.MSG_INFO_LOAD_SITE_ID + str(self.pargs.site))
      else:
        self.site_id = CONSTS.SITE_ALL
        self.message_queue.append(CONSTS.MSG_INFO_LOAD_DEFAULT_SITE_ID + str(CONSTS.SITE_ALL))

    except Exception, err:
      print CONSTS.MSG_ERROR_LOAD_CONFIG, err.message
      raise


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      # print str(vars(self.config))
      log_conf_file = self.config.get("Application", "log")
      logging.config.fileConfig(log_conf_file)
      self.logger = Utils.MPLogger().getLogger()
    except Exception, err:
      print CONSTS.MSG_ERROR_LOAD_LOG_CONFIG_FILE, err.message
      raise


  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    try:
      # remote host
      remote_db_task_ini = self.config.get(self.__class__.__name__, "db-task_ini_remote")
      remote_cfgParser = ConfigParser.ConfigParser()
      remote_cfgParser.read(remote_db_task_ini)
      self.remote_wrapper = DBTasksWrapper(remote_cfgParser)
      self.remote_host = remote_cfgParser.get("TasksManager", "db_host")
      # local host
      local_db_task_ini = self.config.get(self.__class__.__name__, "db-task_ini_local")
      local_cfgParser = ConfigParser.ConfigParser()
      local_cfgParser.read(local_db_task_ini)
      self.local_wrapper = DBTasksWrapper(local_cfgParser)
    except Exception, err:
      self.logger.error(CONSTS.MSG_ERROR_LOAD_LOG_CONFIG_FILE)
      self.logger.error(str(err.message))
      raise



  # # process
  #
  def process(self):
    # log message buffer
    for msg in self.message_queue:
      self.logger.info(msg)

    if self.site_id is not None:
      try:
        # collect site's data
        self.recrawl_dict[self.site_id] = self.collectSiteData()
        self.logger.info("self.recrawl_dict: %s" % str(self.recrawl_dict))
        # store site's data
        self.storeSiteData()
      except Exception, err:
        self.logger.error(CONSTS.MSG_ERROR_PROCESS_GENERAL + ' ' + str(err))


  # # collectSiteData
  #
  def collectSiteData(self):
    site_data_dict = {}
    if self.site_id is not None:
      try:
        # New Contents
        query = CONSTS.SQL_QUERY_NEW_URLS % (self.site_id, self.site_id, self.site_id)
        response = self.remote_wrapper.customRequest(query, CONSTS.DB_URLS)
        if response is not None:
          self.logger.info("response: %s" % str(response))
          site_data_dict["Contents"] = response[0][0]
          site_data_dict["LastAdded"] = response[0][1]
          site_data_dict["minPDate"] = response[0][2]
          site_data_dict["maxPDate"] = response[0][3]

        # Recrawl start
        query = CONSTS.SQL_QUERY_RECRAWL_PERIOD_START % (self.site_id)
        response = self.remote_wrapper.customRequest(query, CONSTS.DB_URLS)
        if response is not None:
          self.logger.info("response: %s" % str(response))
          site_data_dict["RecrawlStart"] = response[0][0]

        # Recrawl end
        query = CONSTS.SQL_QUERY_RECRAWL_PERIOD_END % (self.site_id)
        response = self.remote_wrapper.customRequest(query, CONSTS.DB_URLS)
        if response is not None:
          self.logger.info("response: %s" % str(response))
          site_data_dict["RecrawlEnd"] = response[0][0]

      except Exception, err:
        self.logger.error(CONSTS.MSG_ERROR_COLLECT_SITE_DATA + ' ' + str(err))
    self.logger.info("site_data_dict: %s" % str(site_data_dict))
    return site_data_dict


  # # storeSiteData
  #
  def storeSiteData(self):
    try:
      if True:  # self.recrawl_dict[self.site_id]["Contents"]>0:
        # Create New table if not exists
        query = CONSTS.SQL_QUERY_NEW_SITE_TABLE % (self.site_id)
        response = self.local_wrapper.customRequest(query, CONSTS.DB_CO)
        if response is not None:
          self.logger.info("response: %s" % str(response))

        # Put site's data to the site's table
        query = CONSTS.SQL_QUERY_INSERT_SITE_DATA % \
          (self.site_id, \
          self.remote_host, \
          self.recrawl_dict[self.site_id]["Contents"], \
          self.recrawl_dict[self.site_id]["RecrawlStart"], \
          self.recrawl_dict[self.site_id]["RecrawlEnd"], \
          self.recrawl_dict[self.site_id]["minPDate"], \
          self.recrawl_dict[self.site_id]["maxPDate"], \
          self.recrawl_dict[self.site_id]["LastAdded"], \
          self.recrawl_dict[self.site_id]["Contents"], \
          self.recrawl_dict[self.site_id]["LastAdded"], \
          self.recrawl_dict[self.site_id]["minPDate"], \
          self.recrawl_dict[self.site_id]["maxPDate"])
        response = self.local_wrapper.customRequest(query, CONSTS.DB_CO)
        if response is not None:
          self.logger.info("response: %s" % str(response))
      else:
        self.logger.info("Zero contents.")
    except Exception, err:
      self.logger.error(CONSTS.MSG_ERROR_STORE_SITE_DATA + ' ' + str(err))
