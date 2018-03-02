'''
HCE project, Python bindings, Distributed Crawler application.
Application level constants and enumerations.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


from collections import namedtuple
import app.Consts as APP_CONSTS


# #Event types definition, used to unique identification events by inproc messaging transport
#
#
class EVENT_TYPES(object):
  # ClientInterfaceService
  SITE_NEW = 1
  SITE_UPDATE = 2
  SITE_STATUS = 3
  SITE_DELETE = 4
  SITE_CLEANUP = 5

  URL_NEW = 6
  URL_UPDATE = 7
  URL_STATUS = 8
  URL_DELETE = 9
  URL_FETCH = 10
  URL_CLEANUP = 11
  URL_CONTENT = 12

  RESOURCE_FETCH = 13
  RESOURCE_DELETE = 14

  SITE_FIND = 15
  SQL_CUSTOM = 16

  BATCH = 17
  URL_PURGE = 18
  FIELD_RECALCULATE = 19
  URL_VERIFY = 20
  URL_AGE = 21
  URL_PUT = 22
  URL_HISTORY = 23
  URL_STATS = 24

  PROXY_NEW = 25
  PROXY_UPDATE = 26
  PROXY_DELETE = 27
  PROXY_STATUS = 28
  PROXY_FIND = 29

  ATTR_SET = 30
  ATTR_UPDATE = 31
  ATTR_DELETE = 32
  ATTR_FETCH = 33
  # ClientInterfaceService
  SITE_NEW_RESPONSE = 101
  SITE_UPDATE_RESPONSE = 102
  SITE_STATUS_RESPONSE = 103
  SITE_DELETE_RESPONSE = 104
  SITE_CLEANUP_RESPONSE = 105

  URL_NEW_RESPONSE = 106
  URL_UPDATE_RESPONSE = 107
  URL_STATUS_RESPONSE = 108
  URL_DELETE_RESPONSE = 109
  URL_FETCH_RESPONSE = 110
  URL_CLEANUP_RESPONSE = 111
  URL_CONTENT_RESPONSE = 112

  RESOURCE_FETCH_RESPONSE = 113
  RESOURCE_DELETE_RESPONSE = 114

  SITE_FIND_RESPONSE = 115

  SQL_CUSTOM_RESPONSE = 116

  BATCH_RESPONSE = 117
  URL_PURGE_RESPONSE = 118
  FIELD_RECALCULATE_RESPONSE = 119
  URL_VERIFY_RESPONSE = 120
  URL_AGE_RESPONSE = 121

  URL_PUT_RESPONSE = 122
  URL_HISTORY_RESPONSE = 123
  URL_STATS_RESPONSE = 124

  PROXY_NEW_RESPONSE = 125
  PROXY_UPDATE_RESPONSE = 126
  PROXY_DELETE_RESPONSE = 127
  PROXY_STATUS_RESPONSE = 128
  PROXY_FIND_RESPONSE = 129

  ATTR_SET_RESPONSE = 130
  ATTR_UPDATE_RESPONSE = 131
  ATTR_DELETE_RESPONSE = 132
  ATTR_FETCH_RESPONSE = 133
  # #constructor
  # initialize fields
  #
  def __init__(self):
    pass


# Name tuple for request and response DRCE Sync tasks cover
DRCESyncTasksCover = namedtuple('DRCESyncTasksCover', 'eventType eventObject')


# Logger name
# LOGGER_NAME = "dc"
LOGGER_NAME = APP_CONSTS.LOGGER_NAME
# Total crawling batches counter name for stat variables
BATCHES_CRAWL_COUNTER_TOTAL_NAME = "batches_crawl_total"
# Crawling batches queue size counter name for stat variables
BATCHES_CRAWL_COUNTER_QUEUE_NAME = "batches_crawl_queue"
# Crawling fault batches fault counter name for stat variables
BATCHES_CRAWL_COUNTER_FAULT_NAME = "batches_crawl_fault"
# Crawling not empty batches counter name for stat variables
BATCHES_CRAWL_COUNTER_FILLED_NAME = "batches_crawl_filled"
# Crawling total urls in all batches counter name for stat variables
BATCHES_CRAWL_COUNTER_URLS_NAME = "batches_crawl_urls"
# Crawling urls in fault batches counter name for stat variables
BATCHES_CRAWL_COUNTER_URLS_FAULT_NAME = "batches_crawl_urls_fault"
# Crawling URL_FETCH requests counter name for stat variables
BATCHES_CRAWL_COUNTER_URL_FETCH_NAME = "batches_crawl_url_fetch"
# Crawling cancelled URL_FETCH requests counter name for stat variables
BATCHES_CRAWL_COUNTER_URL_FETCH_CANCELLED_NAME = "batches_crawl_url_fetch_cancelled"
# Crawling delete task requests fault counter name for stat variables
BATCHES_CRAWL_COUNTER_DELETE_FAULT_NAME = "batches_crawl_delete_fault"
# Crawling batches fault counter name for stat variables
BATCHES_CRAWL_COUNTER_FAULT_TTL_NAME = "batches_crawl_fault_ttl"
# Crawling batches check state fault counter name for stat variables
BATCHES_CRAWL_COUNTER_CHECK_FAULT_NAME = "batches_crawl_check_fault"
# Crawling batches urls returned counter name for stat variables
BATCHES_CRAWL_COUNTER_URLS_RET_NAME = "batches_crawl_urls_ret"
# Crawling incremental URL_FETCH requests counter name for stat variables
BATCHES_CRAWL_COUNTER_URL_FETCH_INCR_NAME = "batches_crawl_url_fetch_incr"
# Sites re-crawl counter name for stat variables
SITES_RECRAWL_COUNTER_NAME = "sites_recrawl_cnt"
# Sites re-crawl sites updated counter name for stat variables
SITES_RECRAWL_UPDATED_COUNTER_NAME = "sites_recrawl_updated_cnt"
# Sites re-crawl sites deleted counter name for stat variables
SITES_RECRAWL_DELETED_COUNTER_NAME = "sites_recrawl_deleted_cnt"
# Sites DRCE requests counter name for stat variables
SITES_DRCE_COUNTER_NAME = "sites_recrawl_drce_cnt"
# Avg processing time init in stat vars
BATCHES_CRAWL_COUNTER_TIME_AVG_NAME = "batches_crawl_time_avg"
# Crawling batches real-time threads number init in stat vars
BATCHES_REALTIME_THREADS_NAME = "batches_realtime_threads"
# Crawling batches real-time threads created number init in stat vars
BATCHES_REALTIME_THREADS_CREATED_COUNTER_NAME = "batches_realtime_threads_created"
# Crawling average urls/items in batches counter name for stat variables
BATCHES_CRAWL_COUNTER_ITEMS_AVG_NAME = "batches_crawl_items_avg"
# Crawling dynamic fetcher batches counter name for stat variables
BATCHES_CRAWL_COUNTER_FETCHER_DYNAMIC = "batches_crawl_fetcher_dynamic"
# Crawling static fetcher batches counter name for stat variables
BATCHES_CRAWL_COUNTER_FETCHER_STATIC = "batches_crawl_fetcher_static"
# Crawling mixed static fetcher batches counter name for stat variables
BATCHES_CRAWL_COUNTER_FETCHER_MIXED = "batches_crawl_fetcher_mixed"


# Crawling batches sendURLFetchRequest counter name for stat variables
BATCHES_CRAWL_COUNTER_URL_FETCH_REQUESTS_NAME = "batches_crawl_url_fetch_requests"

# Recrawling threads counter name for stat variables
RECRAWL_THREADS_COUNTER_QUEUE_NAME = "recrawl_threads"
# Recrawling sites queue size counter name for stat variables
RECRAWL_SITES_QUEUE_NAME = "recrawl_sites_queue"
# Recrawling total threads created counter name for stat variables
RECRAWL_THREADS_CREATED_COUNTER_NAME = "recrawl_threads_created"

# Common threads counter name for stat variables
COMMON_THREADS_COUNTER_QUEUE_NAME = "common_threads"
# Common operations counter name for stat variables
COMMON_OPERATIONS_COUNTER_NAME = "common_operations_cnt"
# Common total threads created counter name for stat variables
COMMON_THREADS_CREATED_COUNTER_NAME = "common_threads_created"

# Purge current batches counter name for stat variables
BATCHES_PURGE_COUNTER_NAME = "purge_batches"
# Purge batches canceled counter name for stat variables
BATCHES_PURGE_COUNTER_CANCELLED_NAME = "purge_batches_canceled"
# Purge total batches counter name for stat variables
BATCHES_PURGE_COUNTER_TOTAL_NAME = "purge_batches_total"
# Purge batches create errors counter name for stat variables
BATCHES_PURGE_COUNTER_ERROR_NAME = "purge_batches_error"
# Purge batches execution faults counter name for stat variables
BATCHES_PURGE_COUNTER_FAULT_NAME = "purge_batches_fault"
# Purge batches task delete fault counter name for stat variables
BATCHES_PURGE_COUNTER_DELETE_FAULT_NAME = "purge_batches_delete_fault"
# Purge batches task check state fault counter name for stat variables
BATCHES_PURGE_COUNTER_CHECK_FAULT_NAME = "purge_batches_check_fault"

# Process Batches counter init in stat vars
BATCHES_PROCESS_COUNTER_TOTAL_NAME = "batches_process_total"
# Process Batches in queue counter init in stat vars
BATCHES_PROCESS_COUNTER_QUEUE_NAME = "batches_process_queue"
# Process Batches that fault processing counter init in stat vars
BATCHES_PROCESS_COUNTER_FAULT_NAME = "batches_process_fault"
# Process Batches that not empty counter init in stat vars
BATCHES_PROCESS_COUNTER_FILLED_NAME = "batches_process_filled"
# Process Batches urls total counter init in stat vars
BATCHES_PROCESS_COUNTER_URLS_NAME = "batches_process_urls"
# Process batches urls fault total counter init in stat vars
BATCHES_PROCESS_COUNTER_URLS_FAULT_NAME = "batches_process_urls_fault"
# Process batches delete task requests fault counter name for stat variables
BATCHES_PROCESS_COUNTER_DELETE_FAULT_NAME = "batches_process_delete_fault"
# Process batches check task requests fault counter name for stat variables
BATCHES_PROCESS_COUNTER_CHECK_FAULT_NAME = "batches_process_check_fault"
# Process batches fault TTL counter name for stat variables
BATCHES_PROCESS_COUNTER_FAULT_TTL_NAME = "batches_process_fault_ttl"
# Process batches cancelled counter name for stat variables
BATCHES_PROCESS_COUNTER_CANCELLED_NAME = "batches_process_cancelled"

# Age current batches counter name for stat variables
BATCHES_AGE_COUNTER_NAME = "age_batches"
# Age batches canceled counter name for stat variables
BATCHES_AGE_COUNTER_CANCELLED_NAME = "age_batches_canceled"
# Age total batches counter name for stat variables
BATCHES_AGE_COUNTER_TOTAL_NAME = "age_batches_total"
# Age error batches counter name for stat variables
BATCHES_AGE_COUNTER_ERROR_NAME = "age_batches_error"
# Age batches execution faults counter name for stat variables
BATCHES_AGE_COUNTER_FAULT_NAME = "age_batches_fault"
# Age batches task delete fault counter name for stat variables
BATCHES_AGE_COUNTER_DELETE_FAULT_NAME = "age_batches_delete_fault"
# Age batches task check state fault counter name for stat variables
BATCHES_AGE_COUNTER_CHECK_FAULT_NAME = "age_batches_check_fault"

# incremenal crawling vars
INCR_MIN_FREQ_CONFIG_VAR_NAME = "INCR_MIN_FREQ"
INCR_MAX_DEPTH_CONFIG_VAR_NAME = "INCR_MAX_DEPTH"
INCR_MAX_URLS_CONFIG_VAR_NAME = "INCR_MAX_URLS"

# Merge parameter name in event.cookie
MERGE_PARAM_NAME = "MERGE_RESULTS"

# Set of RAW data file suffixes
RAW_DATA_SUFF = ".bin"
RAW_DATA_HEADERS_SUFF = ".headers.txt"
RAW_DATA_REQESTS_SUFF = ".requests.txt"
RAW_DATA_META_SUFF = ".meta.txt"
RAW_DATA_COOKIES_SUFF = ".cookies.txt"
RAW_DATA_TIDY_SUFF = ".tidy"
RAW_DATA_DYNAMIC_SUFF = ".dyn"
RAW_DATA_CHAIN_SUFF = ".chain"

# sites_properties keys names
SITE_PROP_AUTO_REMOVE_RESOURCES = "AUTO_REMOVE_RESOURCES"
SITE_PROP_AUTO_REMOVE_ORDER = "AUTO_REMOVE_ORDER"
SITE_PROP_AUTO_REMOVE_WHERE = "AUTO_REMOVE_WHERE"
SITE_PROP_AUTO_REMOVE_WHERE_ACTIVE = "AUTO_REMOVE_WHERE_ACTIVE"
SITE_PROP_RECRAWL_DELETE_WHERE = "RECRAWL_DELETE_WHERE"

SITE_PROP_SAVE_COOKIES = "STORE_COOKIES"

DRCE_REQUEST_ROUTING_ROUND_ROBIN = '{"role":1}'
DRCE_REQUEST_ROUTING_RESOURCE_USAGE = '{"role":5}'
DRCE_REQUEST_ROUTING_MULTICAST = '{"role":0}'
DRCE_REQUEST_ROUTING_RND = '{"role":4}'

