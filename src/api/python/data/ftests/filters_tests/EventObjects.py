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
import logging

from app.Utils import JsonSerializable
from app.Utils import SQLExpression
from app.Utils import UrlNormalizator
import app.Consts as APP_CONSTS


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)

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

  # #constructor
  # initialize fields
  # @param url One of possible url used as root entry point of the site
  #
  def __init__(self, url, _userId=0):
    super(Site, self).__init__()

    url = URL(0, url).getURL()
    # #@var id
    # The site Id, calculated as md5 hash from first root url
    try:
      self.id = hashlib.md5(url).hexdigest()
    except Exception:
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
    self.priority = 0
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
    if len(url):
      self.urls.append(url)
    # #@var filters
    # The list of url filters object SiteFilter
    self.filters = [SiteFilter(self.id, "(.*)")]
    # #@var properties
    # The dic of site properties fields
    self.properties = {"PROCESS_CTYPES":"text/html", "STORE_HTTP_REQUEST":"1", "STORE_HTTP_HEADERS":"1",
                       "HTTP_HEADERS":"", "HTTP_COOKIE":""}
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
    self.fetchType = 1



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



# #SiteFind event object
#
# Get list of Site objects and find them by URL pattern
#
class SiteFind(JsonSerializable):

  MAX_NUMBER_DEFAULT = 10

  CRITERION_LIMIT = "LIMIT"
  CRITERION_WHERE = "WHERE"
  CRITERION_ORDER = "ORDER BY"
  DEFAULT_ORDER_BY_CDATE = "CDate DESC"

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
  def __init__(self, siteId, taskType=TASK_TYPE_SYNC):
    super(SiteDelete, self).__init__()
    self.id = siteId
    self.taskType = taskType



# #SiteCleanup event object
#
# The cleanup site operation object.
#
class SiteCleanup(JsonSerializable):

  TASK_TYPE_SYNC = 1
  TASK_TYPE_ASYNC = 2

  # #constructor
  # initialize fields
  # @param siteId site identifier
  # @param taskType delete task type - sync or async in specification of DRCE API protocol
  #
  def __init__(self, siteId, taskType=TASK_TYPE_SYNC):
    super(SiteCleanup, self).__init__()
    self.id = siteId
    self.taskType = taskType



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
  def __init__(self, siteId, pattern, ptype=TYPE_INCLUDE, pmode=TYPE_URL, pstate=TYPE_ENABLED, pstage=0, psubject = "", paction=0):
    super(SiteFilter, self).__init__()
    self.siteId = siteId
    self.pattern = pattern
    self.type = ptype
    self.mode = pmode
    self.state = pstate
    self.stage = pstage
    self.subject = psubject
    self.action = paction



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

  # Type of collect operation "Regular" - collects URLs and insert only for this site according filters
  TYPE_REGULAR = 0
  # Type of collect operation "Single", do not collect URLs
  TYPE_SINGLE = 1
  # Type of collect operation "Regular ext." - collects URLs and insert for all sites according filters
  TYPE_REGULAR_EXT = 2
  # Type of collect operation "New site" - collect URLs, create sites and insert URLs for all sites according filters
  TYPE_NEW_SITE = 3

  # Explicit type means that if site not resolved by Id or Id is empty or None, put URL to general DB table
  SITE_SELECT_TYPE_EXPLICIT = 0
  # Auto type means that if site not resolved by ID or Id is empty or None, generate Id by qualified URL domain and
  # try to identify site and if site not resolved - create new site table using qualified domain name
  SITE_SELECT_TYPE_AUTO = 1
  # Qualify URL type means that if site not resolved by Id or empty or None, try to qualify domain name and generate Id
  # If site not resolved, put URL to general DB table
  SITE_SELECT_TYPE_QUALIFY_URL = 2

  CONTENT_TYPE_TEXT_HTML = "text/html"
  CONTENT_TYPE_UNDEFINED = ""

  # #constructor
  # initialize fields
  # @param siteId site identifier
  #
  def __init__(self, siteId, url, state=STATE_ENABLED):
    super(URL, self).__init__()

    # normalize url according to RFC 3986
    # logger.debug("init url: <<%s>>", url)
    # init_url_md5 = hashlib.md5(url).hexdigest()
    # logger.debug("init url md5: <<%s>>", init_url_md5)
    # logger.debug("norm url: <<%s>>", url)
    # norm_url_md5 = hashlib.md5(url).hexdigest()
    # logger.debug("norm url md5: <<%s>>", norm_url_md5)

    self.siteId = siteId
    self.url = url
    # normalize url according to RFC 3986
    self.url = self.getURL()
    self.type = self.TYPE_REGULAR
    self.state = state
    self.status = self.STATUS_NEW
    self.siteSelect = self.SITE_SELECT_TYPE_EXPLICIT
    self.crawled = 0
    self.processed = 0
    try:
      self.urlMd5 = hashlib.md5(url).hexdigest()
    except Exception:
      self.urlMd5 = hashlib.md5(url).hexdigest()
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
    self.httpMethod = ""
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
    self.maxURLsFromPage = 0


  # #constructor
  # initialize fields
  # @param siteId site identifier
  #
  def getURL(self, _type="normalized"):
    url = self.url
    if _type == "normalized":
      url = UrlNormalizator.normalize(self.url)
    return url



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

  # #constructor
  # initialize fields
  # @param sitesList list of site's identifiers (MD5). If omitted or empty - all sites will take a part
  # @param urlsCriterions dic of limit name and value. If omitted or empty - the "LIMIT" is set to DEFAULT_LIMIT
  # @param sitesCriterions dic of limit name and value. If omitted or empty - the "LIMIT" is set to DEFAULT_LIMIT
  # @param urlUpdate URLUpdate object, if is not None then used to update each URL record after select
  #
  def __init__(self, sitesList=None, urlsCriterions=None, sitesCriterions=None, urlUpdate=None):
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



# #URLUpdate event object
#
# The URLUpdate event object for update operation. Updates only not None value fields
#
class URLUpdate(URL):

  # #constructor
  # initialize fields
  # @param urlString the identifier for URL, depends on urlType - HTTP URL or MD5(HTTP URL)
  # @param urlType the type of url field value, see the URLStatus.URL_TYPE_URL definition
  # @param stateField - the state field
  # @param statusField - the status field
  # @param siteIdField - the siteId field
  # @param typeField - the type field
  #
  def __init__(self, siteId, urlString, urlType=URLStatus.URL_TYPE_URL, stateField=None, statusField=None):
    super(URLUpdate, self).__init__(siteId, urlString, stateField)
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
    # Init criterions
    self.criterions = {}
    self.criterions[URLFetch.CRITERION_LIMIT] = 1


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

  # #constructor
  # initialize fields
  # @param siteId md5 string of site Id
  # @param urlId md5 string of URL Id
  # @param urlObj the URL object from source SQL db
  #
  def __init__(self, siteId, urlId, urlObj):
    super(BatchItem, self).__init__()
    self.siteId = siteId
    self.urlId = urlId
    self.urlObj = urlObj



# #Batch event object
#
# The Batch event object for crawling tasks.
#
class Batch(JsonSerializable):

  OPERATION_TYPE_NAME = "type"
  TYPE_NORMAL_CRAWLER = 1
  TYPE_INCR_CRAWLER = 2
  TYPE_URLS_RETURN = 3

  # #constructor
  # initialize fields
  # @param batchId - the batch Id the same as DRCE task Id
  # @param batchItems list of BatchItem objects to process
  #
  def __init__(self, batchId, batchItems=None, crawlerType=None):
    super(Batch, self).__init__()
    self.id = batchId
    if crawlerType is None:
      crawlerType = Batch.TYPE_NORMAL_CRAWLER

    self.crawlerType = crawlerType
    if batchItems == None:
      self.items = []
    else:
      self.items = batchItems



# #URLDelete event object
#
# The URLDelete event object for delete operation. Delete URL and all related data including content files,
# processed contents and URL registration
#
class URLDelete(JsonSerializable):

  # #constructor
  # initialize fields
  # @param urlString the identifier for URL, depends on urlType - HTTP URL or MD5(HTTP URL)
  # @param urlType the type of url field value, see the URLStatus.URL_TYPE_URL definition
  # @param criterions the sql query parts dict, see URLFetch for detailed description
  def __init__(self, siteId, urlString, urlType=URLStatus.URL_TYPE_URL, criterions=None):
    super(URLDelete, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.urlType = urlType
    self.criterions = criterions



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



# #URLContentRequest event object
#
# The URLContentRequest event object get URL's content operation.
#
class URLContentRequest(JsonSerializable):

  CONTENT_TYPE_PROCESSED = 1
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

  # #constructor
  # initialize fields
  # @param urlString the HTTP URL
  # @param urlType the type of url field value, always URLStatus.URL_TYPE_URL
  # @param contentTypeMask - the content types mask defines types of content that will be collected and returned
  #
  def __init__(self, siteId, urlString, contentTypeMask=CONTENT_TYPE_PROCESSED + CONTENT_TYPE_RAW_LAST):
    super(URLContentRequest, self).__init__()
    self.siteId = siteId
    self.url = urlString
    self.urlMd5 = self.fillMD5(urlString)
    self.contentTypeMask = contentTypeMask
    self.urlFetch = None


  # #Method fills self.url and self.urlMd5 class fields
  #
  # urlString - url
  def fillMD5(self, urlString):
    try:
      return hashlib.md5(urlString).hexdigest()
    except Exception:
      return hashlib.md5(urlString).hexdigest()


# #Content object
#
# The Content object represents content data for URLContentResponse event object.
#
class Content(JsonSerializable):

  CONTENT_RAW_CONTENT = 0
  CONTENT_TIDY_CONTENT = 1
  CONTENT_DYNAMIC_CONTENT = 9
  CONTENT_PROCESSOR_CONTENT = 10

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
  # @param processedContents the list of Content objects for processed contents from key-value DB
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
    # Init urlMd5
    self.urlMd5 = None



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
