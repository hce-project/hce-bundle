"""@package docstring
  @file Constants.py
  @author Alexey <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2013 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
  """

#exit staus code
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SITE_ALL=0

# parameters strings constants
DEFAULT_CFG_FILE="../ini/crawling-optimizer.ini"
APP_NAME = "crawling-optimizer"

# Logging string constatns
# INFO level
MSG_INFO_LOAD_DEFAULT_CONFIG_FILE = "Loading default config file: "
MSG_INFO_LOAD_CONFIG_FILE = "Loading config file: "
MSG_INFO_LOAD_DEFAULT_SITE_ID = "Load default site id: "
MSG_INFO_LOAD_SITE_ID = "Load site id: "

# ERROR level
MSG_ERROR_LOAD_CONFIG = "Can't load config file"
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Can't load logging config file"
MSG_ERROR_PROCESS_GENERAL = "Can't process query"
MSG_ERROR_COLLECT_SITE_DATA = "Can't collect site's data"
MSG_ERROR_STORE_SITE_DATA = "Can't store site's data"
# SQL query's templates
# tables
DB_URLS = "dc_urls"
DB_CO = "dc_co"

# Count new urls for last recrawl period
SQL_QUERY_NEW_URLS = """SELECT count(*), max(`TcDate`), min(`LastModified`), max(`LastModified`) FROM dc_urls.`urls_%s`
  WHERE
  `CDate`
  BETWEEN
  (SELECT DATE_SUB(`RecrawlDate`, INTERVAL `RecrawlPeriod` minute) FROM dc_sites.`sites` WHERE `Id`='%s')
  AND
  (SELECT `RecrawlDate` FROM dc_sites.`sites` WHERE `Id`='%s')
  AND
  `ParentMd5`<>''
  AND
  `Crawled`<>0
  AND
  `Processed`<>0
  AND
  `TagsCount`<>0
  AND
  `Status`=7"""


# Start time of recrawl period
SQL_QUERY_RECRAWL_PERIOD_START = """SELECT
  DATE_SUB(`RecrawlDate`, INTERVAL `RecrawlPeriod` minute)
  FROM dc_sites.`sites` 
  WHERE `Id`='%s'"""


# Get end of crawling time
SQL_QUERY_RECRAWL_END = """SELECT max(`TcDate`) FROM dc_urls.`urls_%s`
  WHERE
  `CDate`
  BETWEEN
  (SELECT DATE_SUB(`RecrawlDate`, INTERVAL `RecrawlPeriod` minute) FROM dc_sites.`sites` WHERE `Id`='%s')
  AND
  (SELECT `RecrawlDate` FROM dc_sites.`sites` WHERE `Id`='%s')"""


# End time of recrawl period
SQL_QUERY_RECRAWL_PERIOD_END = """SELECT `RecrawlDate` FROM dc_sites.`sites` WHERE `Id`='%s'"""


# Create new site's data table
SQL_QUERY_NEW_SITE_TABLE = """CREATE TABLE IF NOT EXISTS `%s` (
  `host` varchar(126) DEFAULT NULL,
  `Contents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `RecrawlStart` datetime DEFAULT NULL COMMENT 'Start date of re-crawl',
  `RecrawlEnd` datetime DEFAULT NULL COMMENT 'End date of re-crawl',
  `minPDate` datetime DEFAULT NULL COMMENT 'When resource was appeared ',
  `maxPDate` datetime DEFAULT NULL,
  `LastAdded` datetime DEFAULT NULL COMMENT 'When content was inserted to the system',
  `CDate` datetime NOT NULL COMMENT 'Date insert row',
  UNIQUE KEY `RecrawlEnd` (`RecrawlEnd`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""


# Put site's data to the table
SQL_QUERY_INSERT_SITE_DATA = """INSERT INTO `%s` VALUES('%s', %s,'%s','%s','%s','%s','%s',NOW()) ON DUPLICATE KEY UPDATE `Contents`=%s, `LastAdded`='%s', `minPDate`='%s', `maxPDate`='%s', `CDate`=NOW()"""
