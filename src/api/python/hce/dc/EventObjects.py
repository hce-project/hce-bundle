'''
HCE project, Python bindings, Distributed Crawler application.
Event objects definitions.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import hashlib
import time

from app.Utils import JsonSerializable
from app.Utils import SQLExpression
from app.Utils import UrlNormalizator
import app.Consts as APP_CONSTS
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()

DELAYED_OPERATION = 0
NOT_DELAYED_OPERATION = 1

# #Site event object, defines the Site abstraction
#
# The site object used to create site representation inside DC application.
# This is a main data unit that is used by DC inside to operate.
class Site(JsonSerializable):

  STATE_ACTIVE = 1
  STATE_DISABLED = 2
  STATE_SUSPENDED = 3
  STATE_DELETED = 4
  STATE_DELETE_TASK = 5
  STATE_RESTART = 6
  STATE_CLEANED = 7
  STATE_CLEANUP_TASK = 8
  STATE_NOT_FOUND = 9

  FETCH_TYPE_STATIC = 1
  FETCH_TYPE_DYNAMIC = 2
  FETCH_TYPE_AUTO = 7
  FETCH_TYPE_EXTERNAL = 3

  # Default piority for Site
  DEFAULT_PRIORITY = 100

  # Default categoryId
  DEFAULT_CATEGORY_ID = 0

  # #constructor
  # initialize fields
  # @param url One of possible url used as root entry point of the site
  #
  def __init__(self, url, _userId=0):
    super(Site, self).__init__()

    url = URL(siteId=0, url=url,
              normalizeMask=UrlNormalizator.NORM_NONE).getURL(normalizeMask=UrlNormalizator.NORM_NONE)
    # #@var id
    # The site Id, calculated as md5 hash from first root url
    self.id = hashlib.md5(url).hexdigest()
    self.uDate = None
    self.tcDate = None
    self.cDate = SQLExpression("NOW()")
    self.resources = 0
    self.contents = 0
    self.iterations = 0
    # #@var state
    # The site state
    self.state = self.STATE_ACTIVE
    # #@var priority
    # The site priority, low value means low priority
    self.priority = self.DEFAULT_PRIORITY
    # The max URLs number that can be collected for site, 0 - means unlimited
    self.maxURLs = 0
    # The max resources number that can be collected for site, 0 - means unlimited
    self.maxResources = 0
    # The max crawling error number, 0 - means unlimited
    self.maxErrors = 0
    # The max resource size, byte
    self.maxResourceSize = 0
    # HTTP request delay, msec
    self.requestDelay = 500
    # Content processing delay, msec
    self.processingDelay = 500
    # HTTP response timeout, msec
    self.httpTimeout = 30000
    # Error mask bit set, see detailed specification
    self.errorMask = 0
    # Errors counter
    self.errors = 0
    # the sum of all raw content files sizes of resources crawled
    self.size = 0
    # AVG bytes per second (BPS) rate
    self.avgSpeed = 0
    # total times of claculating avg speed
    self.avgSpeedCounter = 0
    # URL type
    # 0 - Regular, collect URLs and insert only for this site according filters;
    # 1 - Single, do not collect URLs,
    # 3 - collect URLs, create sites and insert for all
    self.urlType = 0
    # #@var description
    # The site description.
    self.description = ""
    # #@var urls
    # The list of urls strings used as root entry points
    self.urls = []
    if url is not None and len(url) > 0:
      localUrl = SiteURL(siteId=self.id, url=url, normalizeMask=UrlNormalizator.NORM_NONE)
      self.urls.append(localUrl)
    # #@var filters
    # The list of url filters object SiteFilter
    self.filters = [SiteFilter(self.id, "(.*)")]
    # #@var properties
    # The dic of site properties fields
    self.properties = [{"name": "PROCESS_CTYPES", "value": "text/html"},
                       {"name": "STORE_HTTP_REQUEST", "value": "1"},
                       {"name": "STORE_HTTP_HEADERS", "value": "1"},
                       {"name": "HTTP_HEADERS", "value": ""},
                       {"name": "HTTP_COOKIE", "value": ""}]
    self.userId = _userId
    # #@var recrawlPeriod
    self.recrawlPeriod = 0
    # #@var recrawlDate
    self.recrawlDate = None
    # #@var maxURLsFromPage
    self.maxURLsFromPage = 0
    # #@var collectedURLs
    self.collectedURLs = 0
    # #@var fetchType
    self.fetchType = self.FETCH_TYPE_STATIC
    # #@var newURLs
    self.newURLs = 0
    # #@var deletedURLs
    self.deletedURLs = 0
    # #@var moveURLs
    self.moveURLs = True
    self.tcDateProcess = None
    self.categoryId = self.DEFAULT_CATEGORY_ID


  # #Rewrite internal site's fields by another siteObj
  #
  # @param siteObj another Site object
  # @param addListFields bool value that means - extend or overwrite list type fields
  def rewriteFields(self, siteObj, addListFields=True):
    excludeFields = ["urls", "filters", "properties"]
    for field in siteObj.__dict__:
      if field not in excludeFields and siteObj.__dict__[field] is not None:
        self.__dict__[field] = siteObj.__dict__[field]
    for field in excludeFields:
      if addListFields:
        if self.__dict__[field] is not None and siteObj.__dict__[field] is not None:
          self.__dict__[field] += siteObj.__dict__[field]
        elif siteObj.__dict__[field] is not None:
          self.__dict__[field] = []
          self.__dict__[field] += siteObj.__dict__[field]
      elif siteObj.__dict__[field] is not None:
        self.__dict__[field] = siteObj.__dict__[field]


  # #Check item by name in properties container
  #
  # @param keyName name
  # @param properties container
  @staticmethod
  def isInProperties(prop, keyName):
    ret = False

    if isinstance(prop, dict) and keyName in prop:
      ret = True
    else:
      if isinstance(prop, list):
        for item in prop:
          if isinstance(item, dict) and keyName == item["name"]:
            ret = True
            break

    return ret


  # #Check item by name in properties container
  #
  # @param keyName name key of property object item to find
  # @param fieldName name of property object item field to return, if omitted the keyName used
  # @param prop container
  @staticmethod
  def getFromProperties(prop, keyName, fieldName="value"):
    ret = None

    if isinstance(prop, dict) and keyName in prop:
      ret = prop[keyName]
    else:
      if isinstance(prop, list):
        for item in prop:
          if isinstance(item, dict) and keyName == item["name"] and fieldName in item:
            ret = item[fieldName]
            break

    return ret



# #SiteUpdate event object
#
# The update site operation object
#
class SiteUpdate(Site):

  UPDATE_TYPE_APPEND = 0
  UPDATE_TYPE_OVERWRITE = 1
  UPDATE_TYPE_UPDATE = 2

  # #constructor
  # initialize fields
  # @param siteId site identifier
  #
  def __init__(self, siteId, updateType=UPDATE_TYPE_APPEND):
    super(SiteUpdate, self).__init__("")
    self.updateType = updateType
    self.id = siteId
    self.uDate = None
    self.tcDate = None
    self.cDate = None
    self.resources = None
    self.iterations = None
    self.description = None
    self.urls = None
    self.filters = None
    self.properties = None
    self.state = None
    self.priority = None
    self.maxURLs = None
    self.maxResources = None
    self.maxErrors = None
    self.maxResourceSize = None
    self.requestDelay = None
    self.httpTimeout = None
    self.errorMask = None
    self.errors = None
    self.size = None
    self.avgSpeed = None
    self.avgSpeedCounter = None
    self.urlType = None
    self.contents = None
    self.processingDelay = None
    self.userId = None
    self.recrawlPeriod = None
    self.recrawlDate = None
    self.maxURLsFromPage = None
    self.criterions = None
    self.collectedURLs = None
    self.newURLs = None
    self.deletedURLs = None
    self.fetchType = None
    self.tcDateProcess = None
    self.categoryId = None



# #SiteFind event object
#
# Get list of Site objects and find them by URL pattern
#
class SiteFind(JsonSerializable):

  MAX_NUMBER_DEFAULT = 10

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"
  CRITERION_TABLES = "TABLES"
  DEFAULT_ORDER_BY_CDATE = "CDate DESC"
  DEFAULT_TABLES = ""

  # #constructor
  # initialize fields
  # @param url pattern of site's root URL that will be find in root url from left string position
  # @param group bool property defines does results will be grouped from several hosts for one site in one or will be
  #        listed as is
  # @param maxNumber maximum items for SQL query returned unique sites Ids
  # @param offset for SQL query returned unique sites Ids
  #
  def __init__(self, url, criterions=None):
    super(SiteFind, self).__init__()
    self.url = url

    # Init criterions for Sites
    if criterions is None:
      criterions = {}
    self.criterions = criterions

    if self.CRITERION_ORDER not in criterions:
      self.criterions[self.CRITERION_ORDER] = self.DEFAULT_ORDER_BY_CDATE

    if self.CRITERION_WHERE not in criterions:
      self.criterions[self.CRITERION_WHERE] = "1=1"

    if self.CRITERION_LIMIT not in criterions:
      self.criterions[self.CRITERION_LIMIT] = str(self.MAX_NUMBER_DEFAULT)

    if self.CRITERION_TABLES not in criterions:
      self.criterions[self.CRITERION_TABLES] = str(self.DEFAULT_TABLES)

    self.excludeList = []



# #SiteStatus event object
#
# The get site status operation object.
#
class SiteStatus(JsonSerializable):

  # #constructor
  # initialize fields
  # @param siteId site identifier, used to get site data from correspondent tables
  # @param deleteTaskId delete task identifier to check task state, if state if finished get task data request Type=1
  # to delete task's data from EE before return response. If delete task finished, Site.state=STATE_DELETED returned,
  # if not - Site.state=STATE_DELETE_TASK returned
  #
  def __init__(self, siteId, deleteTaskId=None):
    super(SiteStatus, self).__init__()
    self.id = siteId
    self.deleteTaskId = deleteTaskId
    self.excludeList = []



# #SiteDelete event object
#
# The delete site operation object.
#
class SiteDelete(JsonSerializable):

  TASK_TYPE_SYNC = 1
  TASK_TYPE_ASYNC = 2

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param taskType delete task type - sync or async in specification of DRCE API protocol
  #
  def __init__(self, siteId=None, taskType=TASK_TYPE_SYNC, criterions=None):
    super(SiteDelete, self).__init__()
    self.id = siteId
    self.taskType = taskType
    self.delayedType = NOT_DELAYED_OPERATION
    if criterions is not None:
      self.criterions = criterions
    else:
      self.criterions = {}
    if self.id is not None and URLFetch.CRITERION_WHERE not in self.criterions:
      self.criterions[URLFetch.CRITERION_WHERE] = "`Site_Id=`" + str(self.id)



# #SiteCleanup event object
#
# The cleanup site operation object.
#
class SiteCleanup(JsonSerializable):

  TASK_TYPE_SYNC = 1
  TASK_TYPE_ASYNC = 2

  HISTORY_CLEANUP_NOT = 0
  HISTORY_CLEANUP_LOG = 1
  HISTORY_CLEANUP_FULL = 2

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param taskType delete task type - sync or async in specification of DRCE API protocol
  #
  def __init__(self, siteId, taskType=TASK_TYPE_SYNC):
    super(SiteCleanup, self).__init__()
    self.id = siteId
    self.taskType = taskType
    self.delayedType = NOT_DELAYED_OPERATION
    self.moveURLs = True
    self.saveRootUrls = True
    self.state = Site.STATE_ACTIVE
    self.historyCleanUp = self.HISTORY_CLEANUP_NOT



# #SiteFilter object
#
# The SiteFilter object.
#
class SiteFilter(JsonSerializable):

  TYPE_EXCLUDE = 0
  TYPE_INCLUDE = 1

  TYPE_DISABLED = 0
  TYPE_ENABLED = 1

  TYPE_URL = 0
  TYPE_MEDIA = 1
  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param pattern string
  # @param ptype type of pattern to enable or to disable if satisfy
  #
  def __init__(self, siteId, pattern, ptype=TYPE_INCLUDE, pmode=TYPE_URL, pstate=TYPE_ENABLED):
    super(SiteFilter, self).__init__()
    self.siteId = siteId
    self.pattern = pattern
    self.subject = ""
    self.opCode = 0
    self.stage = 5
    self.action = 1
    self.type = ptype
    self.mode = pmode
    self.state = pstate
    self.uDate = None
    self.cDate = None
    self.groupId = 0



# #URL event object
#
# The URL event object for operations uses URLs.
#
class URL(JsonSerializable):

  # URL states, used by selection condition to crawl and process
  STATE_ENABLED = 0
  STATE_DISABLED = 1
  STATE_ERROR = 2

  # URL statuses, used by selection condition to crawl and process and to indicate state of operations
  STATUS_UNDEFINED = 0
  STATUS_NEW = 1
  STATUS_SELECTED_CRAWLING = 2
  STATUS_CRAWLING = 3
  STATUS_CRAWLED = 4
  STATUS_SELECTED_PROCESSING = 5
  STATUS_PROCESSING = 6
  STATUS_PROCESSED = 7
  STATUS_SELECTED_CRAWLING_INCREMENTAL = 8

  # content statuses mask
  CONTENT_EMPTY = 0
  CONTENT_STORED_ON_DISK = 1 << 0

  # Type of collect operation "Regular" - collects URLs and insert only for this site according filters
  TYPE_REGULAR = 0
  # Type of collect operation "Single", do not collect URLs
  TYPE_SINGLE = 1
  # Type of collect operation "Regular ext." - collects URLs and insert for all sites according filters
  TYPE_REGULAR_EXT = 2
  # Type of collect operation "New site" - collect URLs, create sites and insert URLs for all sites according filters
  TYPE_NEW_SITE = 3
  # Type of is url fetched already
  TYPE_FETCHED = 4
  # Type of is url from real time crawling task
  TYPE_REAL_TIME_CRAWLER = 5
  # Type of is url from real time crawling task
  TYPE_CHAIN = 6

  # Explicit type means that if site not resolved by Id or Id is empty or None, put URL to general DB table
  SITE_SELECT_TYPE_EXPLICIT = 0
  # Auto type means that if site not resolved by ID or Id is empty or None, generate Id by qualified URL domain and
  # try to identify site and if site not resolved - create new site table using qualified domain name
  SITE_SELECT_TYPE_AUTO = 1
  # Qualify URL type means that if site not resolved by Id or empty or None, try to qualify domain name and generate Id
  # If site not resolved, put URL to general DB table
  SITE_SELECT_TYPE_QUALIFY_URL = 2
  SITE_SELECT_TYPE_NONE = 3

  CONTENT_TYPE_TEXT_HTML = "text/html"
  CONTENT_TYPE_UNDEFINED = ""

  URL_NORMALIZE_MASK = UrlNormalizator.NORM_DEFAULT

  # #constructor
  # initialize fields
  # @param siteId site identifier
  #
  def __init__(self, siteId, url, state=STATE_ENABLED, urlUpdate=None, normalizeMask=URL_NORMALIZE_MASK):
    super(URL, self).__init__()

    self.siteId = siteId
    self.url = url
    if url is not None:
      # normalize url according to RFC 3986
      self.url = self.getURL(normalizeMask)
    self.type = self.TYPE_REGULAR
    self.state = state
    self.status = self.STATUS_NEW
    self.siteSelect = self.SITE_SELECT_TYPE_NONE
    self.crawled = 0
    self.processed = 0
    if url is not None:
      self.urlMd5 = hashlib.md5(self.url).hexdigest()
    else:
      self.urlMd5 = None
    self.contentType = self.CONTENT_TYPE_UNDEFINED
    self.requestDelay = 500
    self.processingDelay = 500
    self.httpTimeout = 30000
    self.charset = ""
    self.batchId = 0
    self.errorMask = 0
    self.crawlingTime = 0
    self.processingTime = 0
    self.totalTime = 0
    self.httpCode = 0
    self.UDate = None
    self.CDate = None
    self.httpMethod = "get"
    self.size = 0
    self.linksI = 0
    self.linksE = 0
    self.freq = 0
    self.depth = 0
    self.rawContentMd5 = ""
    self.parentMd5 = ""
    self.lastModified = None
    self.eTag = ""
    self.mRate = 0.0
    self.mRateCounter = 0
    self.tcDate = None
    self.maxURLsFromPage = 100
    self.contentMask = self.CONTENT_EMPTY
    self.tagsMask = 0
    self.tagsCount = 0
    self.pDate = None
    self.contentURLMd5 = ""
    self.priority = 0
    self.urlUpdate = urlUpdate
    self.urlPut = None
    self.chainId = None
    self.classifierMask = 0
    self.attributes = []


  # #constructor
  # initialize fields
  # @param normalizeMask
  #
  def getURL(self, normalizeMask=URL_NORMALIZE_MASK):
    url = self.url
    if normalizeMask != UrlNormalizator.NORM_NONE:
      url = UrlNormalizator.normalize(self.url, None, normalizeMask)

    return url



# #SiteURL event object
#
# The SiteURL event object for operations uses sites_urls table.
#
class SiteURL(URL):

  def __init__(self, siteId, url, stateField=None, normalizeMask=URL.URL_NORMALIZE_MASK):
    super(SiteURL, self).__init__(siteId, url, stateField, normalizeMask=normalizeMask)

    self.userId = None



# #URLStatus event object
#
# The URLStatus event object for URL_STATUS operation.
#
class URLStatus(JsonSerializable):

  URL_TYPE_URL = 0
  URL_TYPE_MD5 = 1

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param urlString the URL string according with HTTP spec.
  #
  def __init__(self, siteId, urlString):
    super(URLStatus, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.urlType = self.URL_TYPE_URL



# #URLFetch event object
#
# The URLFetch event object for fetch URLs operation.
#
class URLFetch(JsonSerializable):

  DEFAULT_ALGORITHM = 0
  PROPORTIONAL_ALGORITHM = 1
  DEFAULT_LIMIT = 20

  DEFAULT_ORDER_BY_SITES = "Priority DESC, TcDate ASC"
  DEFAULT_ORDER_BY_URLS = "CDate ASC"

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"
  CRITERION_SQL = "SQL"


  # #constructor
  # initialize fields
  # @param sitesList list of site's identifiers (MD5). If omitted or empty - all sites will take a part
  # @param urlsCriterions dic of limit name and value. If omitted or empty - the "LIMIT" is set to DEFAULT_LIMIT
  # @param sitesCriterions dic of limit name and value. If omitted or empty - the "LIMIT" is set to DEFAULT_LIMIT
  # @param urlUpdate URLUpdate object, if is not None then used to update each URL record after select
  # @param siteUpdate SiteUpdate object, if is not None then used to update site after select
  #
  def __init__(self, sitesList=None, urlsCriterions=None, sitesCriterions=None, urlUpdate=None, siteUpdate=None):
    super(URLFetch, self).__init__()
    # Init sites list
    if sitesList is None:
      sitesList = []
    self.sitesList = sitesList
    # Init criterions for Sites
    if sitesCriterions is None:
      sitesCriterions = {}
    self.sitesCriterions = sitesCriterions
    if self.CRITERION_ORDER not in sitesCriterions:
      self.sitesCriterions[self.CRITERION_ORDER] = self.DEFAULT_ORDER_BY_SITES
    # Init criterions for URLs
    if urlsCriterions is None:
      urlsCriterions = {}
    self.urlsCriterions = urlsCriterions
    if self.CRITERION_LIMIT not in urlsCriterions:
      self.urlsCriterions[self.CRITERION_LIMIT] = self.DEFAULT_LIMIT
    if self.CRITERION_ORDER not in urlsCriterions:
      self.urlsCriterions[self.CRITERION_ORDER] = self.DEFAULT_ORDER_BY_URLS
    self.urlUpdate = urlUpdate
    self.maxURLs = self.DEFAULT_LIMIT
    self.algorithm = self.DEFAULT_ALGORITHM
    self.isLocking = True
    self.lockIterationTimeout = 1
    self.siteUpdate = siteUpdate
    self.attributeNames = ['*']


# #URLUpdate event object
#
# The URLUpdate event object for update operation. Updates only not None value fields
#
class URLUpdate(URL):

  # #constructor
  # initialize fields
  # @param urlString - a identifier for URL, depends on urlType - HTTP URL or MD5(HTTP URL)
  # @param urlType - a type of url field value, see the URLStatus.URL_TYPE_URL definition
  # @param stateField - a state field
  # @param statusField - a status field
  # @param normalizeMask - a normalize mask
  # @param urlObject - a url object
  #
  def __init__(self, siteId, urlString, urlType=URLStatus.URL_TYPE_URL, stateField=None, statusField=None,
               normalizeMask=URL.URL_NORMALIZE_MASK, urlObject=None):
    if urlObject is None or not isinstance(urlObject, URL):
      # Init with default
      if urlType == URLStatus.URL_TYPE_URL:
        url = urlString
      else:
        url = None
      # super(URLUpdate, self).__init__(siteId, urlString, stateField)
      super(URLUpdate, self).__init__(siteId=siteId, url=url, state=stateField, normalizeMask=normalizeMask)
      self.siteId = siteId
      self.type = None
      self.state = stateField
      self.status = statusField
      self.siteSelect = None
      self.crawled = None
      self.processed = None
      self.fillMD5(urlString, urlType)
      self.contentType = None
      self.requestDelay = None
      self.processingDelay = None
      self.httpTimeout = None
      self.charset = None
      self.batchId = None
      self.errorMask = None
      self.crawlingTime = None
      self.processingTime = None
      self.totalTime = None
      self.httpCode = None
      self.UDate = SQLExpression("NOW()")
      self.CDate = None
      self.httpMethod = None
      self.size = None
      self.linksI = None
      self.linksE = None
      self.freq = None
      self.depth = None
      self.rawContentMd5 = None
      self.parentMd5 = None
      self.lastModified = None
      self.eTag = None
      self.mRate = None
      self.mRateCounter = None
      self.tcDate = None
      self.maxURLsFromPage = None
      self.priority = None
      self.tagsCount = None
      self.contentURLMd5 = None
      self.tagsMask = None
      self.chainId = None
      self.classifierMask = None
      self.attributes = None
      # Init criterions
      self.criterions = {}
      self.criterions[URLFetch.CRITERION_LIMIT] = 1
    else:
      # Init from URL object
      for name, value in urlObject.__dict__.items():
        if not name.startswith("__"):
          if hasattr(self, name) and value is not None:
            setattr(self, name, value)


  # #Method fills self.url and self.urlMd5 class fields
  #
  # urlString - url
  # urlType - url's type
  def fillMD5(self, urlString, urlType):
    if urlType == URLStatus.URL_TYPE_URL:
      # Commented out because parent class doing the same
      # self.url = urlString
      # self.urlMd5 = hashlib.md5(urlString).hexdigest()
      pass
    else:
      self.url = None
      self.urlMd5 = urlString



# #BatchItem object
#
# The BatchItem object for batch crawling tasks.
#
class BatchItem(JsonSerializable):

  PROP_FEED = "feed"

  # #constructor
  # initialize fields
  # @param siteId md5 string of site Id
  # @param urlId md5 string of URL Id
  # @param urlObj the URL object from source SQL db
  #
  def __init__(self, siteId, urlId, urlObj, urlPutObj=None, urlContentResponse=None, siteObj=None, depth=0):
    super(BatchItem, self).__init__()
    self.siteId = siteId
    self.urlId = urlId
    self.urlObj = urlObj
    self.properties = {}

    # For demo real time mode
    self.urlPutObj = urlPutObj

    # For supporting demo real-time mode algorithms
    # Algorithms can be:
    # Only crawling
    # Only processing
    # Crawling and processing
    self.urlContentResponse = urlContentResponse

    self.siteObj = siteObj
    self.depth = depth



# #Batch event object
#
# The Batch event object for crawling tasks.
#
class Batch(JsonSerializable):

  OPERATION_TYPE_NAME = "type"
  TYPE_NORMAL_CRAWLER = 1
  TYPE_INCR_CRAWLER = 2
  TYPE_URLS_RETURN = 3
  TYPE_REAL_TIME_CRAWLER = 4
  TYPE_PURGE = 5
  TYPE_PROCESS = 6
  TYPE_AGE = 7

  DB_MODE_RW = 3
  DB_MODE_R = 1
  DB_MODE_W = 2
  DB_MODE_NO = 0

  # #constructor
  # initialize fields
  # @param batchId - the batch Id the same as DRCE task Id
  # @param batchItems list of BatchItem objects to process
  #
  def __init__(self, batchId, batchItems=None, crawlerType=None, dbMode=DB_MODE_RW, maxIterations=1, maxItems=None):
    super(Batch, self).__init__()
    self.id = batchId
    if crawlerType is None:
      crawlerType = Batch.TYPE_NORMAL_CRAWLER
    self.crawlerType = crawlerType
    if batchItems is None:
      self.items = []
    else:
      self.items = batchItems
    self.errorMask = APP_CONSTS.ERROR_OK
    self.dbMode = dbMode
    self.maxIterations = maxIterations
    self.maxItems = maxItems
    self.maxExecutionTime = 0
    self.removeUnprocessedItems = False


# #URLDelete event object
#
# The URLDelete event object for delete operation. Delete URL and all related data including content files,
# processed contents and URL registration
#
class URLDelete(JsonSerializable):

  REASON_USER_REQUEST = 0
  REASON_AGING = 1
  REASON_SITE_LIMITS = 2
  REASON_SELECT_TO_CRAWL_TTL = 3
  REASON_SELECT_TO_PROCESS_TTL = 4
  REASON_RECRAWL = 5
  REASON_CRAWLER_AUTOREMOVE = 6
  REASON_SITE_UPDATE_ROOT_URLS = 7
  REASON_RT_FINALIZER = 10
  REASON_PROCESSOR_DUPLICATE = 11


  # #constructor
  # initialize fields
  # @param urlString the identifier for URL, depends on urlType - HTTP URL or MD5(HTTP URL)
  # @param urlType the type of url field value, see the URLStatus.URL_TYPE_URL definition
  # @param criterions the sql query parts dict, see URLFetch for detailed description
  def __init__(self, siteId, urlString, urlType=URLStatus.URL_TYPE_URL, criterions=None, reason=REASON_USER_REQUEST):
    super(URLDelete, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.urlType = urlType
    self.criterions = criterions
    self.delayedType = NOT_DELAYED_OPERATION
    self.reason = reason



# #URLCleanup event object
#
# The URLCleanup event object for cleanup operation. Also can updates only not None value fields
#
class URLCleanup(JsonSerializable):

  # #constructor
  # initialize fields
  # @param urlString the identifier for URL, depends on urlType - HTTP URL or MD5(HTTP URL)
  # @param urlType the type of url field value, see the URLStatus.URL_TYPE_URL definition
  # @param stateField - the state field
  # @param statusField - the status field
  #
  def __init__(self, siteId, urlString, urlType=URLStatus.URL_TYPE_URL, stateField=None, statusField=None,
               criterions=None):
    super(URLCleanup, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.urlType = urlType
    self.state = stateField
    self.status = statusField
    self.criterions = criterions
    self.delayedType = NOT_DELAYED_OPERATION



# #URLContentRequest event object
#
# The URLContentRequest event object get URL's content operation.
#
class URLContentRequest(JsonSerializable):

  CONTENT_TYPE_PROCESSED = 1  # Return one best value in custom format if exists or default internal if not
  CONTENT_TYPE_RAW_LAST = 2
  CONTENT_TYPE_RAW_FIRST = 4
  CONTENT_TYPE_RAW_ALL = 8
  CONTENT_TYPE_HEADERS = 16
  CONTENT_TYPE_REQUESTS = 32
  CONTENT_TYPE_META = 64
  CONTENT_TYPE_COOKIES = 128
  CONTENT_TYPE_TIDY = 256
  CONTENT_TYPE_DYNAMIC = 512
  CONTENT_TYPE_RAW = 1024
  CONTENT_TYPE_CHAIN = 2048
  CONTENT_TYPE_PROCESSED_INTERNAL = 4096  # Return internal format value(s) one or several
  CONTENT_TYPE_PROCESSED_CUSTOM = 8192  # Return custom format value(s) one or several
  CONTENT_TYPE_PROCESSED_ALL = 16384  # Return all values in addition to the CONTENT_TYPE_PROCESSED
  CONTENT_TYPE_ATTRIBUTES = 32768  # Return attributes

  URL_TYPE_STRING = 0
  URL_TYPE_MD5 = 1

  # #constructor
  # initialize fields
  # @param urlString the HTTP URL
  # @param urlType the type of url field value, always URLStatus.URL_TYPE_URL
  # @param contentTypeMask - the content types mask defines types of content that will be collected and returned
  #
  def __init__(self, siteId, urlString, contentTypeMask=CONTENT_TYPE_PROCESSED + CONTENT_TYPE_RAW_LAST,
               urlType=URL_TYPE_STRING):
    super(URLContentRequest, self).__init__()
    self.siteId = siteId
    self.url = urlString
    if urlType == self.URL_TYPE_STRING:
      self.urlMd5 = self.fillMD5(urlString)
    else:
      self.urlMd5 = urlString
    self.contentTypeMask = contentTypeMask
    self.urlFetch = None
    self.attributeNames = ['*']
    self.dbFieldsList = ["Status", "Crawled", "Processed", "ContentType", "Charset", "ErrorMask", "CrawlingTime",
                         "ProcessingTime", "HTTPCode", "Size", "LinksI", "LinksE", "RawContentMd5", "LastModified",
                         "CDate", "UDate", "TagsMask", "TagsCount", "PDate", "ContentURLMd5", "Batch_Id"]

    self.dbFieldsListDefaultValues = {"Status":1,
                                      "Crawled":0,
                                      "Processed":0,
                                      "ContentType":"",
                                      "Charset":"",
                                      "ErrorMask":0,
                                      "CrawlingTime":0,
                                      "ProcessingTime":0,
                                      "HTTPCode":0,
                                      "Size":0,
                                      "LinksI":0,
                                      "LinksE":0,
                                      "RawContentMd5":"",
                                      "LastModified":None,
                                      "CDate":int(time.time()),
                                      "UDate":None,
                                      "TagsMask":0,
                                      "TagsCount":0,
                                      "PDate":None,
                                      "ContentURLMd5":"",
                                      "Batch_Id":0}


  # #Method fills self.url and self.urlMd5 class fields
  #
  # urlString - url
  def fillMD5(self, urlString):
    return hashlib.md5(urlString).hexdigest()



# #Content object
#
# The Content object represents content data for URLContentResponse event object.
#
class Content(JsonSerializable):

  CONTENT_RAW_CONTENT = 0
  CONTENT_TIDY_CONTENT = 1
  CONTENT_HEADERS_CONTENT = 2
  CONTENT_REQUESTS_CONTENT = 3
  CONTENT_META_CONTENT = 4
  CONTENT_COOKIES_CONTENT = 5
  CONTENT_DYNAMIC_CONTENT = 9
  CONTENT_PROCESSOR_CONTENT = 10
  CONTENT_CHAIN_PARTS = 11

  # #constructor
  # initialize fields
  # @param contentBuffer the data buffer
  # @param cDate the content creation timestamp or zero if not defined
  #
  def __init__(self, contentBuffer, cDate=0, typeId=CONTENT_RAW_CONTENT):
    super(Content, self).__init__()
    # Init buffer
    self.buffer = contentBuffer
    # Init creation date
    self.cDate = cDate
    # Contents type
    self.typeId = typeId



# #URLContentResponse event object
#
# The URLContentResponse event object response on get URL's content operation.
#
class URLContentResponse(JsonSerializable):

  STATUS_OK = 0
  STATUS_URL_NOT_FOUND = 1
  STATUS_RAW_CONTENT_NOT_FOUND = 2
  STATUS_PROCESSED_CONTENT_NOT_FOUND = 3

  # #constructor
  # initialize fields
  # @param url the HTTP URL of crawled resource
  # @param rawContents the list of Content objects for raw crawled files
  # @param processedContents the list of Content objects for processed contents, depends on the CONTENT_TYPE_PROCESSED
  #                          CONTENT_TYPE_PROCESSED_INTERNAL, CONTENT_TYPE_PROCESSED_CUSTOM and
  #                          CONTENT_TYPE_PROCESSED_ALL bits. If both the CONTENT_TYPE_PROCESSED_INTERNAL and
  #                          CONTENT_TYPE_PROCESSED_CUSTOM is set - list item is a tuple with Content objects in
  #                          internal and custom formats: [(ContentObjInternal, ContentObjCustom), ...].
  #                          If only CONTENT_TYPE_PROCESSED is set, the custom format returned if exists and internal
  #                          if not.
  # @param status the sql db field from `dc_urls`.`urls_SITE_ID_MD5`.`status`
  #
  def __init__(self, url, rawContents=None, processedContents=None, status=STATUS_OK):
    super(URLContentResponse, self).__init__()
    # Init url
    self.url = url
    # Init status
    self.status = status
    # Init raw contents list
    self.rawContents = []
    if rawContents is not None:
      self.rawContents = rawContents
    # Init processed contents list
    self.processedContents = []
    if processedContents is not None:
      self.processedContents = processedContents
    # Addition content elements (lists)
    self.headers = []
    self.requests = []
    self.meta = []
    self.cookies = []
    self.urlMd5 = None
    self.rawContentMd5 = None
    self.dbFields = {}
    self.siteId = 0
    self.contentURLMd5 = ""
    self.rawContentMd5 = ""
    self.itemProperties = None
    self.attributes = []



# #ClientResponse event object
#
# The ClientResponse event object to response on any client request.
#
class ClientResponse(JsonSerializable):

  STATUS_OK = 0
  STATUS_ERROR_NONE = 1
  STATUS_ERROR_EMPTY_LIST = 2

  # #constructor
  # initialize fields
  # @param itemsList the list of ClientResponseItem objects
  # @param errorCode the general error code, if all item objects are okay it is okay
  # @param errorMessage the united error message
  #
  def __init__(self, itemsList=None, errorCode=STATUS_OK, errorMessage=""):
    super(ClientResponse, self).__init__()
    # Error code
    if itemsList is None:
      self.itemsList = []
    else:
      self.itemsList = itemsList
    self.errorCode = errorCode
    self.errorMessage = errorMessage



class ClientResponseItem(JsonSerializable):

  STATUS_OK = 0
  STATUS_ERROR_RESTORE_OBJECT = 1
  STATUS_ERROR_DRCE = 2
  MSG_ERROR_RESTORE_OBJECT = "Object restore error!"
  MSG_ERROR_RESTORE_OBJECT = "DRCE error!"

  # #constructor
  # initialize fields
  # @param itemObject the item object from the DRCE response
  #
  def __init__(self, itemObject):
    super(ClientResponseItem, self).__init__()
    self.itemObject = itemObject
    self.errorCode = self.STATUS_OK
    self.errorMessage = ""
    self.id = 0
    self.host = ""
    self.port = 0
    self.node = ""
    self.time = 0



class URLPurge(JsonSerializable):

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"

  MAX_URLS_TO_DELETE_FROM_SITE = 100
  ALL_SITES = -1

  # #constructor
  # If the siteId is None the siteLimits must be a tuple: zero item is offset and first item is a number of items to
  # purge, for example (0, 100) - means from zero offset of sites list process 100 sites
  # @param urlString the identifier for URL, depends on urlType - HTTP URL or MD5(HTTP URL)
  # @param urlType the type of url field value, see the URLStatus.URL_TYPE_URL definition
  # @param criterions the sql query parts dict, see URLFetch for detailed description, for URLs
  def __init__(self, siteId, urlString, urlType=URLStatus.URL_TYPE_URL, criterions=None):
    super(URLPurge, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.urlType = urlType
    if criterions is None:
      criterions = {self.CRITERION_LIMIT:self.MAX_URLS_TO_DELETE_FROM_SITE}
    self.criterions = criterions
    self.siteLimits = None



class FieldRecalculatorObj(JsonSerializable):

  FULL_RECALC = 0
  PARTITION_RECALC = 1

  # #constructor
  def __init__(self, siteId, recalcType=FULL_RECALC, criterions=None):
    super(FieldRecalculatorObj, self).__init__()
    self.siteId = siteId
    self.recalcType = recalcType
    self.criterions = criterions



class URLVerify(JsonSerializable):

  # #constructor
  def __init__(self, siteId, urlString, dbName, urlType=URLStatus.URL_TYPE_URL, criterions=None):
    super(URLVerify, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.dbName = dbName
    self.urlType = urlType
    self.criterions = criterions



# #URLAge event object used to make request of URLAge operation
#
# The URLAge operation object performs delete URLs by aging condition
#
class URLAge(JsonSerializable):

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"

  MAX_URLS_TO_DELETE_FROM_SITE = 100
  MAX_SITES_TO_SELECT = 10
  DEFAULT_LIMIT = 100

  # #constructor
  # @param urlsCriterions - criterions for fetching urls from MySQL db (dc_urls db)
  # @param sitesCriterions - criterions for fetching sites from MySQL db (db_sites db)
  def __init__(self, urlsCriterions=None, sitesCriterions=None):
    super(URLAge, self).__init__()
    if urlsCriterions is None:
      urlsCriterions = {self.CRITERION_LIMIT:self.MAX_URLS_TO_DELETE_FROM_SITE}
    self.urlsCriterions = urlsCriterions
    if sitesCriterions is None:
      sitesCriterions = {self.CRITERION_LIMIT:self.MAX_SITES_TO_SELECT}
    self.sitesCriterions = sitesCriterions
    self.maxURLs = self.DEFAULT_LIMIT
    self.delayedType = NOT_DELAYED_OPERATION



# #DataFetchRequest incoming (request) class for db storage request
#
#
class DataFetchRequest(JsonSerializable):

  # #constructor
  # @param siteId - siteId
  # @param urlMd5 - url's md5
  # @param criterions - addition SQL criterions
  def __init__(self, siteId, urlMd5, criterions=None):
    super(DataFetchRequest, self).__init__()
    self.siteId = siteId
    self.urlMd5 = urlMd5
    self.criterions = criterions



# #DataFetchResponse outgoing (response) class for db storage request
#
#
class DataFetchResponse(JsonSerializable):

  # #constructor
  # @param resultDict - db storage result fields
  # @param errCode - operation error code
  # @param errMessage - operation error message
  def __init__(self, resultDict, errCode=0, errMessage=""):
    super(DataFetchResponse, self).__init__()
    self.resultDict = resultDict
    self.errCode = errCode
    self.errMessage = errMessage



# #DataDeleteRequest incoming (request) class for db storage [Data delte operations]
#
#
class DataDeleteRequest(JsonSerializable):

  # #constructor
  # @param siteId - siteId
  # @param filesSuffix - suffix of storage file
  # @param urlMd5 - url's md5
  def __init__(self, siteId, urlMd5, filesSuffix):
    super(DataDeleteRequest, self).__init__()
    self.siteId = siteId
    self.filesSuffix = filesSuffix
    self.urlMd5 = urlMd5



# #DataDeleteResponse outgoing (response) class for db storage [Data delte operations]
#
#
class DataDeleteResponse(JsonSerializable):

  # #constructor
  # @param errCode - operation error code
  # @param errMessage - operation error message
  def __init__(self, errCode=0, errMessage=""):
    super(DataDeleteResponse, self).__init__()
    self.errCode = errCode
    self.errMessage = errMessage



# #DataDeleteRequest incoming (request) class for db storage [Data delte operations]
#
#
class DataCreateRequest(JsonSerializable):

  # #constructor
  # @param siteId - siteId
  # @param filesSuffix - suffix of storage file
  # @param urlMd5 - url's md5
  def __init__(self, siteId, urlMd5, filesSuffix):
    super(DataCreateRequest, self).__init__()
    self.siteId = siteId
    self.filesSuffix = filesSuffix
    self.urlMd5 = urlMd5



# #DataDeleteResponse outgoing (response) class for db storage [Data delte operations]
#
#
class DataCreateResponse(JsonSerializable):

  # #constructor
  # @param errCode - operation error code
  # @param errMessage - operation error message
  def __init__(self, errCode=0, errMessage=""):
    super(DataCreateResponse, self).__init__()
    self.errCode = errCode
    self.errMessage = errMessage



# #URLPutRequest incoming (request) class for db storage [Data delte operations]
#
#
class URLPut(JsonSerializable):

  # #constructor
  # @param siteId - siteId
  # @param urlMd5 - url's md5
  # @param CDate - url's CDate
  # @param criterions - criterions for urlMd5's fetching (if urlMd5 is None)
  def __init__(self, siteId, urlMd5, contentType, putDict=None, criterions=None, fileStorageSuffix=None):
    super(URLPut, self).__init__()
    if putDict is None:
      putDict = {}
    self.siteId = siteId
    self.urlMd5 = urlMd5
    self.putDict = putDict
    self.criterions = criterions
    self.contentType = contentType
    self.fileStorageSuffix = fileStorageSuffix



# #DataDeleteResponse outgoing (response) class for db storage [Data delte operations]
#
#
class URLPutResponse(JsonSerializable):

  # #constructor
  # @param errCode - operation error code
  # @param errMessage - operation error message
  def __init__(self, contentType, errCode=0, errMessage=""):
    super(URLPutResponse, self).__init__()
    self.contentType = contentType
    self.errCode = errCode
    self.errMessage = errMessage



# #URLHistoryRequest event object
#
# The URLHistoryRequest event object get URL's history operation.
#
class URLHistoryRequest(JsonSerializable):

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"
  DEFAULT_ORDER = "ODate ASC"
  DEFAULT_WHERE = "URLMD5='%URL%'"
  DEFAULT_LIMIT = 100

  # #constructor
  # initialize fields
  # @param siteId the Site Id
  # @param urlMd5 the md5(url) or None to avoid seletcion for one URL only
  # @param criterions the criterions for the SQL request
  #
  def __init__(self, siteId, urlMd5=None, urlCriterions=None, logCriterions=None):
    super(URLHistoryRequest, self).__init__()
    self.siteId = siteId
    self.urlMd5 = urlMd5
    if urlCriterions is None:
      self.urlCriterions = {}
    else:
      self.urlCriterions = urlCriterions
    if self.CRITERION_LIMIT not in self.urlCriterions and urlCriterions is not None:
      self.urlCriterions[self.CRITERION_LIMIT] = str(self.DEFAULT_LIMIT)
    if logCriterions is None:
      self.logCriterions = {}
    else:
      self.logCriterions = logCriterions
    if self.CRITERION_ORDER not in self.logCriterions and logCriterions is not None:
      self.logCriterions[self.CRITERION_ORDER] = self.DEFAULT_ORDER



# #URLHistoryResponse event object
#
# The URLHistoryResponse event object represents the response of the URL's history operation.

class URLHistoryResponse(JsonSerializable):

  # #constructor
  # initialize fields
  # @param logRows the list of items of selected rows from the `dc_stat_logs`.`log_SITE_ID` table as is
  #
  def __init__(self, logRows=None, siteId=None):
    super(URLHistoryResponse, self).__init__()
    self.siteId = siteId
    if logRows is None:
      self.logRows = []
    else:
      self.logRows = logRows



# #URLHistoryRequest event object
#
# The URLHistoryRequest event object get URL's history operation.
#
class URLStatsRequest(JsonSerializable):

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"
  DEFAULT_ORDER = "ODate ASC"
  DEFAULT_WHERE = "URLMD5='%URL%'"
  DEFAULT_LIMIT = 100

  # #constructor
  # initialize fields
  # @param siteId the Site Id
  # @param urlMd5 the md5(url) or None to avoid seletcion for one URL only
  # @param criterions the criterions for the SQL request
  #
  def __init__(self, siteId, urlMd5=None, urlCriterions=None, statsCriterions=None):
    super(URLStatsRequest, self).__init__()
    self.siteId = siteId
    self.urlMd5 = urlMd5
    if urlCriterions is None:
      self.urlCriterions = {}
    else:
      self.urlCriterions = urlCriterions
    if self.CRITERION_LIMIT not in self.urlCriterions and urlCriterions is not None:
      self.urlCriterions[self.CRITERION_LIMIT] = str(self.DEFAULT_LIMIT)
    if statsCriterions is None:
      self.statsCriterions = {}
    else:
      self.statsCriterions = statsCriterions



# #URLStatsResponse event object
#
# The URLStatsResponse event object represents the response of the URL's stats operation.
class URLStatsResponse(JsonSerializable):

  # #constructor
  # initialize fields
  # @param freqRows the list of items of selected rows from the `dc_stat_freq`.`freq_SITE_ID` table as is
  #
  def __init__(self, freqRows=None, siteId=None):
    super(URLStatsResponse, self).__init__()
    self.siteId = siteId
    if freqRows is None:
      self.freqRows = []
    else:
      self.freqRows = freqRows


# #Proxy event object
#
# The Proxy event object represents sites_proxy table element
class Proxy(JsonSerializable):

  # #constructor
  def __init__(self, siteId, host):
    super(Proxy, self).__init__()
    self.id = 0
    self.siteId = siteId
    self.host = host
    self.domains = None
    self.priority = 0
    self.state = 0
    self.countryCode = ""
    self.countryName = ""
    self.regionCode = 0
    self.regionName = ""
    self.cityName = ""
    self.zipCode = ""
    self.timeZone = ""
    self.latitude = 0.0
    self.longitude = 0.0
    self.metroCode = 0
    self.faults = 0
    self.faultsMax = 0
    self.categoryId = 0
    self.limits = None
    self.description = ""
    self.cDate = int(time.time())
    self.uDate = SQLExpression("NOW()")


# #ProxyUpdate event object
#
# The ProxyUpdate event object which updates fields in Proxy table
class ProxyUpdate(Proxy):

  # #constructor
  def __init__(self, siteId, host):
    super(ProxyUpdate, self).__init__(siteId, host)
    self.id = 0
    self.siteId = siteId
    self.host = host
    self.domains = None
    self.priority = 0
    self.state = 0
    self.countryCode = ""
    self.countryName = ""
    self.regionCode = 0
    self.regionName = ""
    self.cityName = ""
    self.zipCode = ""
    self.timeZone = ""
    self.latitude = 0.0
    self.longitude = 0.0
    self.metroCode = 0
    self.faults = 0
    self.faultsMax = 0
    self.categoryId = 0
    self.limits = None
    self.description = ""
    self.cDate = int(time.time())
    self.uDate = SQLExpression("NOW()")


# #ProxyDelete event object
#
# The ProxyDelete event object which deletes fields in Proxy table
class ProxyDelete(JsonSerializable):

  # #constructor
  def __init__(self, siteId=None, host=None, criterions=None):
    super(ProxyDelete, self).__init__()
    self.siteId = siteId
    self.host = host
    if criterions is not None:
      self.criterions = criterions
    else:
      self.criterions = {}
    if self.siteId is not None and URLFetch.CRITERION_WHERE not in self.criterions:
      self.criterions[URLFetch.CRITERION_WHERE] = "`Site_Id=`" + str(self.siteId)


# #ProxyStatus event object
#
# The ProxyStatus event object which deletes fields in Proxy table
class ProxyStatus(JsonSerializable):

  # #constructor
  def __init__(self, siteId=None, host=None, criterions=None):
    super(ProxyStatus, self).__init__()
    self.siteId = siteId
    self.host = host
    if criterions is not None:
      self.criterions = criterions
    else:
      self.criterions = {}
    if self.siteId is not None and URLFetch.CRITERION_WHERE not in self.criterions:
      self.criterions[URLFetch.CRITERION_WHERE] = "`Site_Id=`" + str(self.siteId)



# #ProxyFind event object
#
# The ProxyFind event object which finds and returns proxies by criterions
class ProxyFind(JsonSerializable):

  # #constructor
  def __init__(self, siteId=None, criterions=None, siteCriterions=None):
    super(ProxyFind, self).__init__()
    self.siteId = siteId
    if criterions is not None:
      self.criterions = criterions
    else:
      self.criterions = {}
    if siteCriterions is not None:
      self.siteCriterions = siteCriterions
    else:
      self.siteCriterions = {}
    if self.siteId is not None and URLFetch.CRITERION_WHERE not in self.criterions:
      self.criterions[URLFetch.CRITERION_WHERE] = "`Site_Id=`" + str(self.siteId)



# #Attribute event object
#
# The Attribute event object for operations uses Attributes.
#
class Attribute(JsonSerializable):

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param Name attribute's name
  #
  def __init__(self, siteId, name, urlMd5='', value='', cDate=None):
    super(Attribute, self).__init__()
    self.siteId = siteId
    self.name = name
    self.urlMd5 = urlMd5
    self.value = value
    self.cDate = cDate


# #AttributeUpdate event object
#
# The AttributeUpdate event object for update operation. Updates only not None value fields
#
class AttributeUpdate(Attribute):

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param Name attribute's name
  #
  def __init__(self, siteId, name):
    super(AttributeUpdate, self).__init__(siteId, name)
    self.siteId = siteId
    self.name = name
    self.urlMd5 = None
    self.value = None
    self.cDate = None


# #AttributeDelete event object
#
# The AttributeDelete event object for delete operation. Deletes attributes by name or by criterions
#
class AttributeDelete(Attribute):

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param Name attribute's name
  #
  def __init__(self, siteId, name=None, criterions=None):
    super(AttributeDelete, self).__init__(siteId, name)
    self.siteId = siteId
    self.name = name
    self.urlMd5 = None
    if criterions is not None:
      self.criterions = criterions
    else:
      self.criterions = {}



# #AttributeFetch event object
#
# The AttributeFetch event object for fetch operation. Fetches attributes by name or by criterions
#
class AttributeFetch(Attribute):

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param Name attribute's name
  #
  def __init__(self, siteId, name=None, criterions=None):
    super(AttributeFetch, self).__init__(siteId, name)
    self.siteId = siteId
    self.name = name
    self.urlMd5 = None
    if criterions is not None:
      self.criterions = criterions
    else:
      self.criterions = {}
