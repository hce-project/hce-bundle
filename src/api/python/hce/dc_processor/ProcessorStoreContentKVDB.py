"""@package docstring
 @file Scraper.py
 @author Alexey <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""



import pickle
import sys
import sqlite3  # as sqlite3
import logging.config
import ConfigParser
from cement.core import foundation
# import app.Utils as Utils  # pylint: disable=F0401
import dc_processor.Constants as CONSTS
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

APP_NAME = "ProcessorStoreContentKVDB"

MSG_ERROR_LOAD_CONFIG = "Error loading config file. Exciting."
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Error loading logging config file. Exiting."
MSG_ERROR_LOAD_EXTRACTORS = "Error load extractors "
MSG_ERROR_TEMPLATE_EXTRACTION = "Error template extraction "
MSG_ERROR_DYNAMIC_EXTRACTION = "Error dynamic extraction "
MSG_ERROR_LOAD_DB_BACKEND = "Error load db backend"
MSG_ERROR_LOAD_OPTIONS = "Error load options"
MSG_INFO_PREPARE_CONTENT = "Prepare content: "
MSG_ERROR_ADJUST_PR = "Error adjust partial references. "
MSG_ERROR_PROCESS = "Processor Storing Contents process batch error: "

SQLITE_TIMEOUT = 30

# #Scraper
#
#
class ProcessorStoreContentKVDB(foundation.CementApp):


  # Mandatory
  class Meta(object):
    label = APP_NAME
    def __init__(self):
      pass


  # #constructor
  # initialize default fields
  def __init__(self):
    # call base class __init__ method
    foundation.CementApp.__init__(self)
    self.exit_code = CONSTS.EXIT_SUCCESS
    self.logger = None
    self.config_db_dir = None
    self.sqliteTimeout = SQLITE_TIMEOUT
    self.input_data = None
    self.raw_contents_tbl = None


  # #setup
  # setup application
  def setup(self):
    # call base class setup method
    foundation.CementApp.setup(self)
    self.args.add_argument('-c', '--config', action='store', metavar='config_file', help='config ini-file')


  # #run
  # run application
  def run(self):
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


  # #main content processing
  # main content processing
  #
  def process(self):
    self.putContentToDB()
    # return response.get()


  def putContentToDB(self):
    # get appropriate db name, depending on siteId
    if len(self.input_data.siteId):
      db_name = self.config_db_dir + "/" + self.input_data.siteId + ".db"
    else:
      db_name = self.config_db_dir + "/0.db"
    self.logger.info("db_name: " + db_name)
    connector = None
    try:
      # put parsed resource to the db
      connector = sqlite3.connect(db_name, timeout=self.sqliteTimeout)  # @UndefinedVariable
      connector.text_factory = str
      with connector:
        cur = connector.cursor()
        query = "CREATE TABLE IF NOT EXISTS \
                %s(id VARCHAR(32) PRIMARY KEY UNIQUE, data TEXT, CDate DATETIME DEFAULT CURRENT_TIMESTAMP)" \
                % (self.raw_contents_tbl)
        cur.execute(query)
        cur.execute("INSERT OR REPLACE INTO raw_contents VALUES(?,?,datetime('now','localtime'))",
                    (self.input_data.urlId, self.input_data.raw_content))

    except Exception as err:
      # Connection objects can be used as context managers that automatically commit or rollback transactions.
      # In the event of an exception, the transaction is rolled back; otherwise, the transaction is committed:
      # connector.rollback()
      ExceptionLog.handler(self.logger, err, 'putContentToDB')
      raise


  # #process batch
  # the main processing of the batch object
  def processBatch(self):
    try:
      # read pickled batch object from stdin and unpickle it
      input_pickled_object = sys.stdin.read()
      stored_in_data = pickle.loads(input_pickled_object)
      self.input_data = stored_in_data
      # self.logger.info("input scraper object: " + str(vars(stored_in_data)))
      # TODO main processing over every url from list of urls in the batch object
      self.process()
      # self.logger.info("output : " + str(output))
      # send response to the stdout
      # print input_pickled_object
    except Exception as err:
      ExceptionLog.handler(self.logger, err, MSG_ERROR_PROCESS, (err))
      self.exit_code = CONSTS.EXIT_FAILURE


  # #load config from file
  # load from cli argument or default config file
  def loadConfig(self):
    try:
      self.config = ConfigParser.ConfigParser()
      self.config.optionxform = str
      if self.pargs.config:
        self.config.read(self.pargs.config)
    except Exception as err:
      print MSG_ERROR_LOAD_CONFIG + err.message
      raise


  # #load logging
  # load logging configuration (log file, log level, filters)
  #
  def loadLogConfigFile(self):
    try:
      log_conf_file = self.config.get("Application", "log")
      logging.config.fileConfig(log_conf_file)
      self.logger = Utils.MPLogger().getLogger()
    except Exception as err:
      print MSG_ERROR_LOAD_LOG_CONFIG_FILE + err.message
      raise


  # #load mandatory options
  # load mandatory options
  #
  def loadOptions(self):
    try:
      self.config_db_dir = self.config.get(self.__class__.__name__, "config_db_dir")
      self.raw_contents_tbl = self.config.get("sqlite", "raw_contents_tbl")
      self.sqliteTimeout = self.config.getint("sqlite", "timeout")
    except Exception as err:
      print MSG_ERROR_LOAD_OPTIONS + err.message
      raise


  # #
  #
  #
  def getExitCode(self):
    return self.exit_code
