'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import hashlib
from dtm.EventObjects import GeneralResponse
from dc_db.BaseTask import BaseTask
from dc_db.URLUpdateTask import URLUpdateTask
from dc_db.AttrSetTask import AttrSetTask
from dc_db.FieldRecalculator import FieldRecalculator
import dc_db.Constants as Constants
import dc.EventObjects
import app.Exceptions
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process list of URLs
class URLNewTask(BaseTask):

  CODE_GOOD_INSERT = 0
  CODE_BAD_INSERT = 1
  CODE_ALREADY_EXIST = 2

  # #constructor
  #
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask, siteTask=None):
    super(URLNewTask, self).__init__()
    self.siteTask = siteTask
    self.recalculator = FieldRecalculator()
    self.urlMd5 = None
    self.urlUpdateTask = URLUpdateTask(keyValueStorageDir, rawDataDir, dBDataTask)


  # Memethod creates new site, using SiteTask class
  #
  # @param initUrl base site url
  # @param queryCallback function for queries execution
  def newSiteCreate(self, initUrl, queryCallback):
    if self.siteTask is None:
      raise Exception(">>> URLNew.siteTask object is None!")
    localSiteObj = dc.EventObjects.Site(initUrl)
    self.siteTask.process(localSiteObj, queryCallback)


  # Memethod makes operation with "site" database table
  #
  # @param urlObject instance of URL object
  # @param queryCallback function for queries execution
  def fillSiteRelatedFields(self, urlObj, queryCallback):
    ret = False
    SITE_EXTRACT_SQL_QUERY = "SELECT `RequestDelay`, `HTTPTimeout`, `URLType` FROM `sites` WHERE id = '%s'"
    res = queryCallback(SITE_EXTRACT_SQL_QUERY % urlObj.siteId, Constants.PRIMARY_DB_ID)
    if hasattr(res, '__iter__') and len(res) > 0:
      ret = True
      if urlObj.requestDelay is None:
        urlObj.requestDelay = res[0][0]
      if urlObj.httpTimeout is None:
        urlObj.httpTimeout = res[0][1]
      if urlObj.type is None:
        urlObj.type = res[0][2]
    return ret


  # Try to extract siteId from MySQL database, based on incoming url field
  #
  # @param url - URL.URL field of incoming object
  # @param queryCallback function for queries execution
  def resolveSiteIdByURL(self, url, queryCallback):
    ret = None
    query = Constants.SELECT_SITE_ID_BY_URL % url
    res = queryCallback(query, Constants.PRIMARY_DB_ID)
    if hasattr(res, '__iter__') and len(res) > 0:
      ret = res[0][0]
      logger.debug(">>> Site_Id By URL = %s", str(ret))
    return ret


  def calcSiteIdByUrl(self, url):
    canonicUrl = Utils.UrlParser.generateDomainUrl(url)
    if canonicUrl is not None and len(canonicUrl) > 0 and canonicUrl[-1] != '/':
      canonicUrl += '/'
    localSiteId = hashlib.md5(canonicUrl).hexdigest()
    return localSiteId


  # Memethod makes operation with "site" database table
  #
  # @param urlObject instance of URL object
  # @param queryCallback function for queries execution
  def siteTableOperation(self, urlObj, queryCallback):
    if urlObj.siteSelect == dc.EventObjects.URL.SITE_SELECT_TYPE_EXPLICIT:
      if urlObj.siteId == "" or not self.isSiteExist(urlObj.siteId, queryCallback):
        urlObj.siteId = "0"
    elif urlObj.siteSelect == dc.EventObjects.URL.SITE_SELECT_TYPE_AUTO:
      try:
        canonicUrl = Utils.UrlParser.generateDomainUrl(urlObj.url)
        if canonicUrl is not None and len(canonicUrl) > 0 and canonicUrl[-1] != '/':
          canonicUrl += '/'
        localSiteId = self.calcSiteIdByUrl(urlObj.url)
        logger.debug(">>> S_NEW_ID=" + str(localSiteId))
        if self.isSiteExist(localSiteId, queryCallback):
          urlObj.siteId = localSiteId
          self.fillSiteRelatedFields(urlObj, queryCallback)
        elif canonicUrl is not None:
          self.newSiteCreate(canonicUrl, queryCallback)
          urlObj.siteId = localSiteId
        else:
          raise Exception(">>> canonicUrl is None !!!")
      except app.Exceptions.UrlParseException:
        logger.debug(">>> UrlParseException")
    elif urlObj.siteSelect == dc.EventObjects.URL.SITE_SELECT_TYPE_QUALIFY_URL:
      localSiteId = self.calcSiteIdByUrl(urlObj.url)
      if not self.isSiteExist(localSiteId, queryCallback):
        urlObj.siteId = "0"
    elif urlObj.siteSelect == dc.EventObjects.URL.SITE_SELECT_TYPE_NONE:
      localSiteId = self.calcSiteIdByUrl(urlObj.url)
      if not self.isSiteExist(localSiteId, queryCallback):
        Exception(">>> urlObj operation can't find siteId")
    else:
      raise Exception(">>> urlObj.siteSelect field has wrong value - %s" % str(urlObj.siteSelect))


  # #make all necessary actions to add new URLs into mysql db
  #
  # @param urls list of URL objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, urls, queryCallback):
    ret = GeneralResponse()
    status = URLNewTask.CODE_BAD_INSERT
    isRelatedSite = False
    for url in urls:
      isRelatedSite = False
      if url.siteId is None and url.siteSelect != dc.EventObjects.URL.SITE_SELECT_TYPE_EXPLICIT:
        url.siteId = self.resolveSiteIdByURL(url.url, queryCallback)
      if self.isSiteExist(url.siteId, queryCallback):
        isRelatedSite = self.fillSiteRelatedFields(url, queryCallback)
      logger.debug(">>> Url New main = " + url.url)
      try:
        if not isRelatedSite:
          logger.debug(">>> Url New before = " + url.url)
          self.siteTableOperation(url, queryCallback)
          logger.debug(">>> Site_Id By URL = %s", str(url.url))
          logger.debug(">>> Url New after = " + url.url)
        if url.siteId is not None and url.siteId != "":
          status = self.urlInsertWithGoodSietId(url, status, queryCallback)
      except Exception as excp:
        logger.debug(">>> Url New operation exception = " + str(excp))
      ret.statuses.append(status)
    return ret


  # #decomposition block code in urlInsertWithGoodSietId method
  #
  # @param urlObj - incoming URL object
  # @param statusInit incoming init value for return status code
  # @param queryCallback function for queries execution
  # @return new status code value
  def urlInsertWithGoodSietId(self, urlObj, statusInit, queryCallback):
    ret = statusInit
    if not self.selectURL(urlObj, queryCallback):
      if self.addURL(urlObj, queryCallback):
        ret = URLNewTask.CODE_GOOD_INSERT
        if urlObj.attributes is not None and len(urlObj.attributes) > 0:
          self.attributesSet(urlObj.attributes, queryCallback)
    else:
      ret = URLNewTask.CODE_ALREADY_EXIST
      if urlObj.urlUpdate is not None:
        logger.debug(">>> Url New Start Internal urlUpdate")
        self.urlUpdateTask.process([urlObj.urlUpdate], queryCallback)

      if urlObj.attributes is not None and len(urlObj.attributes) > 0:
        self.attributesSet(urlObj.attributes, queryCallback)

    self.recalculator.commonRecalc(urlObj.siteId, queryCallback)
    if "urlPut" in urlObj.__dict__ and urlObj.urlPut is not None:
      self.urlUpdateTask.urlPutOperation(urlObj, urlObj.urlPut, queryCallback)
    return ret


  # #update urls
  #
  # @param urlObject instance of URL object
  # @param queryCallback function for queries execution
  def selectURL(self, urlObject, queryCallback):
    ret = False
    self.urlMd5 = None
    LOCAL_URL_CHECK_QUERY = "SELECT COUNT(*) FROM `urls_%s` WHERE `URLMd5` = '%s'"
    if urlObject.urlMd5 is not None:
      self.urlMd5 = urlObject.urlMd5
    else:
      self.urlMd5 = hashlib.md5(urlObject.url).hexdigest()
    query = LOCAL_URL_CHECK_QUERY % (urlObject.siteId, self.urlMd5)
    res = queryCallback(query, Constants.SECONDARY_DB_ID)
    if hasattr(res, '__iter__') and len(res) > 0 and len(res[0]) > 0 and res[0][0] > 0:
      ret = True
    return ret


  # #inserts new url
  #
  # @param urlObject instance of URL object
  # @param queryCallback function for queries execution
  def addURL(self, urlObject, queryCallback):
    self.statisticLogUpdate(urlObject, self.urlMd5, urlObject.siteId, urlObject.status, queryCallback, True)
    ret = False
    fields, values = Constants.getFieldsValuesTuple(urlObject, Constants.URLTableDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values)
    if fieldValueString is not None and fieldValueString != "":
      query = Constants.INSERT_COMMON_TEMPLATE % ((Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlObject.siteId),
                                                  fieldValueString)
      logger.debug(str(query))
      queryCallback(query, Constants.SECONDARY_DB_ID, Constants.EXEC_NAME, True)
      ret = True

    return ret


  # #inserts new Attributes
  #
  # @param attributes list of Attributes objects
  # @param queryCallback function for queries execution
  def attributesSet(self, attributes, queryCallback):
    logger.debug(">>> Add Attributes (len) == " + str(len(attributes)))
    attrSetTask = AttrSetTask()
    res = attrSetTask.process(attributes, queryCallback)
    logger.debug(">>> Add Attributes (res) == " + varDump(res))
