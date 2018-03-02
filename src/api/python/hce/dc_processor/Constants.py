"""@package docstring
 @file Constants.py
 @author Alexey, bgv <developers.hce@gmail.com>, Alexander Vybornyh <alexander.hce.cluster@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013-2015 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""
import app.Consts as APP_CONSTS
LOGGER_NAME = APP_CONSTS.LOGGER_NAME

# constants for general purpose
TAG_MEDIA = "media"
TAG_TITLE = "title"
TAG_LINK = "link"
TAG_DESCRIPTION = "description"
TAG_PUB_DATE = "pubdate"
TAG_DC_DATE = "dc_date"
TAG_AUTHOR = "author"
TAG_GUID = "guid"
TAG_CONTENT_UTF8_ENCODED = "content_encoded"
TAG_KEYWORDS = "keywords"
TAG_MEDIA_THUMBNAIL = "media_thumbnail"
TAG_MEDIA_CONTENT = "media_content"
TAG_ENCLOSURE = "enclosure"
TAG_GOOGLE = "google_search"
TAG_GOOGLE_TOTAL = "google_search_total"
TAG_SUMMARY_LANG = "summary_lang"
HTML_LANG = "html_lang"
PARENT_RSS_FEED = "parent_rss_feed"
PARENT_RSS_FEED_URLMD5 = "parent_rss_feed_urlMd5"
SUMMARY = "summary"
SUMMARY_DETAIL = "summary_detail"
COMMENTNS = "comments"
TAGS = "tags"
PUBLISHED = "published"
CONTENT = "content"
UPDATED = "updated"
UPDATED_PARSED = "updated_parsed"
TAG_ORDER_NUMBER = "order_number"
TAG_SOURCE_URL = "source_url"
TAG_FEED_URL = "feed_url"
# TAG_LINKS = "links"
TAG_TYPE_DATETIME = 'datetime'
TAG_PUBDATE_TZ = 'pubdate_tz'
# content hash for duplicate detection
CONTENT_HASH_ALGORITHM_EMPTY = 0
CONTENT_HASH_ALGORITHM_MD5 = 1
CONTENT_HASH_ALGORITHM_CRC32 = 2
CONTENT_HASH_ALGORITHM_SOUNDEX = 3
CONTENT_HASH_ALGORITHM_SHA1 = 4
CONTENT_HASH_ALGORITHM_SDHASH = 5
CONTENT_HASH_ALGORITHM_BBHASH = 6
CONTENT_HASH_ALGORITHM_MRSH_V2 = 7
CONTENT_HASH_ALGORITHM_MVHASH_B = 8
CONTENT_HASH_ALGORITHM_MD5_WITHOUT_HTML = 9
CONTENT_HASH_ACTION_DELETE = 1
PARENT_URL_MD5 = ""

TAGS_RULES_MASK_DEFAULT_VALUE = 4
TAGS_RULES_MASK_RULE_PRIORITY = 2
TAGS_RULES_MASK_MANDATORY_FIELD = 1

# MODES
PROCESS_ALGORITHM_REGULAR = "regular"
PROCESS_ALGORITHM_TRAINING = "training"
PROCESS_ALGORITHM_PREDICTION = "prediction"
PROCESS_ALGORITHM_CONCURRENCY = "concurrency"
PROCESS_ALGORITHM_METRIC = "metric_based"
PROCESS_ALGORITHM_FEED_PARSER = "feed_parser"
PROCESS_ALGORITHM_ALCHEMY = "ALCHEMY"
PROCESS_ALGORITHM_BOILERPIPE = "BOILERPIPE"
PROCESS_ALGORITHM_NEWSPAPER = "NEWSPAPER"
PROCESS_ALGORITHM_GOOSE = "GOOSE"
PROCESS_ALGORITHM_SCRAPY = "SCRAPY"
PROCESS_ALGORITHM_ML = "ML"

TRAINING_QUEUE = "TRAINING_QUEUE"
TRAINED_QUEUE = "TRAINED_QUEUE"
CONCURRENCY_QUEUE = "CONCURRENCY_QUEUE"

DB_SECTION = "mysql"
DB_HOST = "db_host"
DB_PORT = "db_port"
DB_USER = "db_user"
DB_PWD = "db_pwd"
DB_SITES = "db_dc_sites"
DB_URLS = "db_dc_urls"
DB_SCRAPERS = "db_dc_scrapers"
DC_CONTENTS_DB_NAME = "db_dc_contents"
SQL_TMP_TABLE = "metrics"

MYSQL_ENGINE = "mysql_engine"

# log messages
MSG_ERROR_OK = ""
MSG_ERROR_LOAD_DB_BACKEND = "Error loading DB backend. "
MSG_ERROR_LOAD_CONFIG = "Error loading config file."
MSG_ERROR_LOAD_LOG_CONFIG_FILE = "Error loading logging config file."
MSG_ERROR_LOAD_EXTRACTORS = "Error load extractors "
MSG_ERROR_TEMPLATE_EXTRACTION = "Error template extraction "
MSG_ERROR_DYNAMIC_EXTRACTION = "Error dynamic extraction "
MSG_ERROR_LOAD_OPTIONS = "Error load options"
MSG_INFO_PREPARE_CONTENT = "Prepare content: "
MSG_ERROR_ADJUST_PR = "Error adjust partial references. "
MSG_ERROR_PROCESS = "Processor Storing Contents process batch error: "
MSG_ERROR_CALC_METRICS = "Smth goes wrong. See traceback: "


# staus code
ERROR_OK = 0

# exit staus code
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# sqlite operation timeout, sec.
SQLITE_TIMEOUT = 30

# scrapping extract tags operation time limit, sec.
TIME_EXECUTION_LIMIT = 20

PYTHON_BINARY = "/usr/bin/python"

# DEFAULT PROCESSOR_NAME
PROCESSOR_EMPTY = ""
SCRAPER_BINARY = "./scraper.py"
SCRAPER_CFG = "--config=../ini/scraper.ini"

# STORE PROCESSOR_NAME
PROCESSOR_STORE = "STORE"
STORE_PROCESSOR_BINARY = "./processor_store_content_kvdb.py"
STORE_PROCESSOR_CFG = "--config=../ini/processor-store-content-in-kvdb.ini"

# FEED_PARSER PROCESSOR_NAME
PROCESSOR_FEED_PARSER = "FEED_PARSER"
PROCESSOR_RSS = "RSS"

# REAL TIME CRAWLING
REPROCESS_KEY = "reprocess"
REPROCESS_VALUE_NO = 0
RECRAWL_KEY = "recrawl"
RECRAWL_VALUE_NO = 0

PROCESSOR_FEED_PARSER_BINARY = "./processor_feed_parser.py"
PROCESSOR_FEED_PARSER_CFG = "--config=../ini/processor_feed_parser.ini"

# SCRAPER MULTI ITEMS PROCESSOR_NAME
PROCESSOR_SCRAPER_MULTI_ITEMS = "SCRAPER_MULTI_ITEMS"
SCRAPER_MULTI_ITEMS_BINARY = "./scraper_multi_items_task.py"
SCRAPER_MULTI_ITEMS_CFG = "--config=../ini/scraper_multi_items_task.ini"

# SCRAPER CUSTOM PROCESSOR_NAME
PROCESSOR_SCRAPER_CUSTOM = "SCRAPER_CUSTOM"
SCRAPER_CUSTOM_BINARY = "./scraper_custom_task.py"
SCRAPER_CUSTOM_CFG = "--config=../ini/scraper_custom_task.ini"

# extractor's names
EXTRACTOR_NAME_ML = "ML extractor"
EXTRACTOR_NAME_ALCHEMY = "Alchemy extractor"
EXTRACTOR_NAME_BOILERPIPE = "Boilerpipe extractor"

MODULES_KEY = "modules"
ALGORITHM_KEY = "algorithm"
ALGORITHM_NAME_KEY = "algorithm_name"
PROPERTIES_KEY = "properties"
TEMPLATE_KEY = "template"
RANK_KEY = "rank"
USE_HTML5_KEY = "html5"

SCRAPER_RANK_INIT = 10
USE_HTML5_YES = 1
USE_HTML5_NO = 0

TIMEZONE_LIST = ["JST"]
COMMON_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# # METRIC SECTION

# DEFAULT (base empty) METRIC
DEFAULT_TRESHOLD_VALUE = 0
DEFAULT_METRIC_VALUE = 0
DEFAULT_COMPARATOR = ""

# WORDS METRIC
# Words count in corpus of article
WORDS_TRESHOLD_VALUE = 100
# Words comparator type
WORDS_COMPARATOR = "round"


# SENTENCES METRIC
SENTENCES_TRESHOLD_VALUE = 5
# Sentences comparator type
SENTENCES_COMPARATOR = "round"

# AUTOMATED READABILITY INDEX METRIC
ARI_TRESHOLD_VALUE = 1
# ARI comparator type
ARI_COMPARATOR = "round"

ARTICLE_CORPUS = "content_encoded"

# # METRIC SECTION END

GOOGLE_SEARCH_SITE_ID = "google_search"
CABINET_SEARCH_SITE_ID = "cabinet_search"
# obsolete. Will be removed in next release
OLD_GOOGLE_SEARCH_SITE_ID = "d57f144e7b26c9976769ea94f18b9064"
OLD_CABINET_SEARCH_SITE_ID = "1fe592caf03fd50c5f065c30f82b13bb"


# For the module import algorithms usage mode
SCRAPER_APP_CLASS_NAME = "Scraper"
SCRAPER_APP_CLASS_CFG = "../ini/scraper.ini"
STORE_APP_CLASS_NAME = "???"
STORE_APP_CLASS_CFG = "../ini/processor-store-content-in-kvdb.ini"
PROCESSOR_FEED_PARSER_CLASS_NAME = "ProcessorFeedParser"
PROCESSOR_FEED_PARSER_CLASS_CFG = "../ini/processor_feed_parser.ini"

SCRAPER_MULTI_ITEMS_APP_CLASS_NAME = "ScraperMultiItemsTask"
SCRAPER_MULTI_ITEMS_APP_CLASS_CFG = "../ini/scraper_multi_items_task.ini"

SCRAPER_CUSTOM_JSON_APP_CLASS_NAME = "ScraperCustomJson"
SCRAPER_CUSTOM_JSON_APP_CLASS_CFG = "../ini/scraper_custom_task.ini"

TAG_REDUCE_MASK_PROP_NAME = "SCRAPER_TEXT_REDUCER_MASK"
TAG_REDUCE_PROP_NAME = "SCRAPER_TEXT_REDUCER"
TAG_MARKUP_PROP_NAME = "SCRAPER_TEXT_MARKUP"
TAG_KEEP_ATTRIBUTES_PROP_NAME = "SCRAPER_KEEP_ATTRIBUTES"
TAG_CLOSE_VOID_PROP_NAME = "CLOSE_VOID"

TAGS_TYPES_NAME = "TAGS_TYPES"

PDATE_TIMEZONES_NAME = "PDATE_TIMEZONES"
PDATE_DAY_MONTH_ORDER_NAME = "PDATE_DAY_MONTH_ORDER"

LANG_PROP_NAME = "SCRAPER_LANG_DETECT"

MEDIA_LIMITS_NAME = "MEDIA_LIMITS"

# Constants for property 'HTTP_REDIRECT_LINK'
HTTP_REDIRECT_LINK_NAME = "HTTP_REDIRECT_LINK"
LOCATION_NAME = "Location"
HTTP_REDIRECT_LINK_VALUE_URL = 1
HTTP_REDIRECT_LINK_VALUE_LOCATION = 2
HTTP_REDIRECT_LINK_VALUE_REDIRECT_URL = 3
HTTP_REDIRECT_LINK_VALUE_SOURCE_URL = 4
HTTP_REDIRECT_LINK_LINK_TAG_NAME = 'link'
REDIRECT_URL_NAME = 'redirect_url'

# ML section
TEMPLATE_CONDITION_TYPE_URL = 0

# HTML5 SEMANTIC TASG
class HTML5_SEMANTIC_TAGS(object):

  HEADER = "header"
  FOOTER = "footer"
  ARTICLE = "article"
  SECTION = "section"


  def __init__(self):
    pass
