'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import MySQLdb
import app.Consts as APP_CONSTS

APP_NAME = "db-task"
DEFAULT_LOCK_TTL = 600

DB_DATA_KVDB = 0
DB_DATA_MYSQL = 1

TASK_DUPLICATE_ERR = 2020
TASK_DUPLICATE_ERR_MSG = "Duplicate site"
TASK_SQL_ERR = 2021
TASK_SQL_ERR_MSG = "Some SQL error, look log file for details"

EXEC_INDEX = 0
EXEC_NAME = 1

PRIMARY_DB_ID = "primaryDB"
SECONDARY_DB_ID = "secondaryDB"
THIRD_DB_ID = "thirdDB"
FOURTH_DB_ID = "fourthDB"
FIFTH_DB_ID = "fifthDB"
STAT_DB_ID = "statDB"
LOG_DB_ID = "logDB"
ATT_DB_ID = "attDB"
STAT_DOMAINS_DB_ID = "statDomainsDB"

DB_STORAGE_TABLE_NAME = "articles"

DB_LOCK_APPLICATION_ID = 0
FETCH_LOCK_NAME = "SELECT_LOCK"

COMA_SEPARATOR = ","
FIELD_QUOTE_SEPARATOR = "`"

EXIT_CODE_OK = 0
EXIT_CODE_CONFIG_ERROR = 1
EXIT_CODE_GLOBAL_ERROR = 2
EXIT_CODE_MYSQL_ERROR = 3

# LOGGER_NAME = "dc_db"
LOGGER_NAME = APP_CONSTS.LOGGER_NAME

# work db names
DC_SITES = "dc_sites"
DC_URLS = "dc_urls"

# template for table names in dc_urls db
DC_URLS_TABLE_NAME_TEMPLATE = "urls_%s"
URL_URL_SQL_UPDATE = 'UPDATE ' + DC_URLS_TABLE_NAME_TEMPLATE + ' SET %s WHERE'
URL_URL_SQL_SELECT_COUNT = 'SELECT COUNT(*) FROM ' + DC_URLS_TABLE_NAME_TEMPLATE + ' WHERE '
DC_CONTENTS_TABLE_NAME_TEMPLATE = "contents_%s"
DC_FREQ_TABLE_NAME_TEMPLATE = "freq_%s"
DC_LOG_TABLE_NAME_TEMPLATE = "log_%s"
DC_ATT_TABLE_NAME_TEMPLATE = "att_%s"

# SQL tempaltes
USE_SQL_TEMPLATE = "USE `%s`"
SELECT_DB_STORAGE = "SELECT * FROM `%s` WHERE Id = '%s'"

INSERT_COMMON_TEMPLATE = "INSERT INTO `%s` SET %s"
SITE_SQL_TEMPLATE = "INSERT INTO `sites` %s VALUES %s"
#------------------------------- Site Filters SQL templates -------------------------
SITE_FILTER_SQL_TEMPLATE = "INSERT INTO `sites_filters` SET `Site_Id`='%s', `Pattern`='%s', `Subject`='%s', \
`OperationCode`=%s, `Stage`=%s, `Action`=%s, `UDate`=%s, `Type`='%s', `Mode`='%s', `State`='%s', `Group_Id`=%s"
SITE_FILTER_SQL_UPDATE = "UPDATE `sites_filters` SET `Pattern`='%s', `Subject`='%s', `OperationCode`=%s, `Stage`=%s, \
`Action`=%s, `UDate`=%s,`Group_Id`=%s WHERE `Site_Id`='%s' AND `Type`='%s' AND `Mode`='%s' AND `State`='%s'"
SITE_PROP_SQL_TEMPLATE = "INSERT INTO `sites_properties` SET `Site_Id`='%s', `Name`='%s', `Value`='%s'"
SITE_PROP_SQL_ADDITIONS = ", `URLMD5`='%s'"
SITE_PROP_SQL_SHOT = "INSERT INTO `sites_properties` SET %s"
SITE_PROP_SQL_UPDATE = "UPDATE `sites_properties` SET %s WHERE `Site_Id`='%s' AND `Name`='%s'"
SITE_URL_SQL_TEMPLATE = "INSERT INTO `sites_urls` SET %s"
SITE_URL_SQL_UPDATE = "UPDATE `sites_urls` SET %s WHERE `Site_Id`='%s'"
SITE_URL_SQL_SELECT_COUNT = 'SELECT COUNT(*) FROM `sites_urls` WHERE '

DEL_BY_ID_QUERY_TEMPLATE = "DELETE FROM `%s` WHERE `Site_Id` = '%s'"

SQL_CHECK_TABLE_EXIST_TEMPLATE = """ SELECT IF( EXISTS(SELECT * FROM information_schema.TABLES WHERE Table_Name="%s" \
and TABLE_SCHEMA="%s"), 1, 0) """
DC_SITE_URL_SQL_TEMPLATE = "INSERT INTO `%s` (`Site_Id`, `URL`) VALUES('%s', '%s')"

SELECT_SQL_TEMPLATE = """ SELECT * FROM `%s` WHERE %s"""
SELECT_SQL_TEMPLATE_SIMPLE = """ SELECT %s FROM `%s`"""
SELECT_SITE_ID_BY_URL = "SELECT `Site_Id` FROM `sites_urls` \
WHERE SUBSTRING(\"%s\", 1, LENGTH(URL))=`URL` ORDER BY LENGTH(URL) DESC LIMIT 1"
CHECK_TABLE_SQL_ADDITION = "`User_Id` = %s"
SQL_CREATE_QUERY_TEMPLATE = "CREATE TABLE IF NOT EXISTS `%s` LIKE dc_urls.%s"

# #sql query which checks existence of a table
CHECK_TABLE_SQL_TEMPLATE = " SELECT COUNT(*) FROM sites WHERE `Id` = '%s'"
CHECK_TABLE_SQL_ADDITION = " AND `User_Id` = %s"

# template for key value file name
KEY_VALUE_FILE_NAME_TEMPLATE = "%s.db"

class StatFreqConstants(object):

  FREQ_INSERT = "FIns"
  FREQ_DELETE = "FDel"
  FREQ_UPDATE = "FUpd"
  FREQ_NEW_STATUS = "FNew"
  FREQ_CRAWLED_STATUS = "FCrawled"
  FREQ_PROCESSED_STATS = "FProcessed"
  FREQ_AGED_STATE = "FAged"
  FREQ_DELETED_STATE = "FDeleted"
  FREQ_PURGED_STATE = "FPurged"

logOperationsDict = dict({"LOG_INSERT": 20,
                          "LOG_DELETE": 21,
                          "LOG_UPDATE": 22,
                          "LOG_URL_CLEANUP": 23,
                          "LOG_URL_AGING": 24,
                          "LOG_URL_CONTENT": 25,
                          "LOG_NEW": 1,
                          "LOG_SELECTED_CRAWLING": 2,
                          "LOG_CRAWLING": 3,
                          "LOG_CRAWLED": 4,
                          "LOG_SELECTED_PROCESSING": 5,
                          "LOG_PROCESSING": 6,
                          "LOG_PROCESSED": 7})

siteDict = dict({"id": "Id",
                 "uDate": "UDate",
                 "tcDate": "TcDate",
                 "tcDateProcess": "TcDateProcess",
                 "cDate": "CDate",
                 "resources": "Resources",
                 "contents": "Contents",
                 "collectedURLs": "CollectedURLs",
                 "newURLs": "NewURLs",
                 "deletedURLs": "DeletedURLs",
                 "iterations": "Iterations",
                 "state": "State",
                 "priority": "Priority",
                 "maxURLs": "MaxURLs",
                 "maxURLsFromPage": "MaxURLsFromPage",
                 "maxResources": "MaxResources",
                 "maxErrors": "MaxErrors",
                 "maxResourceSize": "MaxResourceSize",
                 "requestDelay": "RequestDelay",
                 "processingDelay": "ProcessingDelay",
                 "httpTimeout": "HTTPTimeout",
                 "errorMask": "ErrorMask",
                 "errors": "Errors",
                 "size": "Size",
                 "avgSpeed": "AVGSpeed",
                 "avgSpeedCounter": "AVGSpeedCounter",
                 "urlType": "URLType",
                 "userId": "User_Id",
                 "recrawlPeriod": "RecrawlPeriod",
                 "recrawlDate": "RecrawlDate",
                 "fetchType": "FetchType",
                 "description": "Description",
                 "categoryId": "Category_Id"}
               )

siteExcludeList = ["Id"]

propDict = dict({"siteId": "Site_Id",
                 "urlMd5": "URLMd5",
                 "name": "Name",
                 "value": "Value",
                 "uDate": "UDate",
                 "cDate": "CDate"}
               )


filterDict = dict({"siteId": "Site_Id",
                   "pattern": "Pattern",
                   "subject": "Subject",
                   "opCode": "OperationCode",
                   "stage": "Stage",
                   "action": "Action",
                   "type": "Type",
                   "mode": "Mode",
                   "state": "State",
                   "uDate": "UDate",
                   "cDate": "CDate",
                   "groupId": "Group_Id"}
                 )


URLTableDict = dict({"siteId": "Site_Id",
                     "url": "URL",
                     "type": "Type",
                     "state": "State",
                     "status": "Status",
                     "crawled": "Crawled",
                     "processed": "Processed",
                     "urlMd5": "URLMd5",
                     "contentType": "ContentType",
                     "requestDelay": "RequestDelay",
                     "processingDelay": "ProcessingDelay",
                     "httpTimeout": "HTTPTimeout",
                     "charset": "Charset",
                     "batchId": "Batch_Id",
                     "errorMask": "ErrorMask",
                     "crawlingTime": "CrawlingTime",
                     "processingTime": "ProcessingTime",
                     "totalTime": "TotalTime",
                     "httpCode": "HTTPCode",
                     "UDate": "UDate",
                     "CDate": "CDate",
                     "httpMethod": "HTTPMethod",
                     "size": "Size",
                     "linksI": "LinksI",
                     "linksE": "LinksE",
                     "freq": "Freq",
                     "depth": "Depth",
                     "rawContentMd5": "RawContentMd5",
                     "parentMd5": "ParentMd5",
                     "lastModified": "LastModified",
                     "eTag": "ETag",
                     "mRate": "MRate",
                     "mRateCounter": "MRateCounter",
                     "tcDate": "TcDate",
                     "maxURLsFromPage": "MaxURLsFromPage",
                     "tagsMask": "TagsMask",
                     "tagsCount": "TagsCount",
                     "pDate": "PDate",
                     "contentURLMd5": "ContentURLMd5",
                     "priority": "Priority",
                     "classifierMask": "ClassifierMask"}
                   )

ProxyTableDict = dict({"id": "Id",
                       "siteId": "Site_Id",
                       "host": "Host",
                       "domains": "Domains",
                       "priority": "Priority",
                       "state": "State",
                       "countryCode":"CountryCode",
                       "countryName":"CountryName",
                       "regionCode":"RegionCode",
                       "regionName":"RegionName",
                       "cityName":"CityName",
                       "zipCode":"ZipCode",
                       "timeZone":"TimeZone",
                       "latitude":"Latitude",
                       "longitude":"Longitude",
                       "metroCode":"MetroCode",
                       "faults":"Faults",
                       "faultsMax":"FaultsMax",
                       "categoryId":"Category_Id",
                       "limits": "Limits",
                       "description": "Description",
                       "cDate":"CDate",
                       "uDate":"UDate"}
                     )

AttrTableDict = dict({"name": "Name",
                      "urlMd5": "URLMD5",
                      "value": "Value"}
                    )


urlExcludeList = ["URL", "URLMd5"]
proxyExcludeList = ["Id", "Site_Id", "Host", "CDate"]

SiteURLTableDitct = dict(URLTableDict.items() + {"userId": "User_Id"}.items())

DbContentFields = {"KVDB": ["id", "data", "CDate"],
                   "MYSQL":["id", "data", "CDate"]}

SITE_ID_NAME = "SITE_ID"


# #Function reads datatime field as str
#
# fName - field name
# row - db row
# returns converted value
def readDataTimeField(fName, row):
  ret = None
  if fName in row and row[fName] is not None:
    ret = str(row[fName])
  return ret


# #Function strips last symbol in incoming string
#
# incomeStr - incoming string
# symbol - symbol for comparing with last char in string
def stripSymbol(incomeStr, symbol=None):
  ret = incomeStr
  if len(incomeStr) > 0:
    if symbol is None or incomeStr[-1] == symbol:
      ret = incomeStr[:-1]
  return ret


# #Function parse incoming object and dict and converts them to the 2 lists
#
# @param obj - incoming converting object
# @param inputDict - incoming converting dict
# @param excludeList - exclude list
# @return tuple with fields,values lists
def getFieldsValuesTuple(obj, inputDict, excludeList=None):
  fields = []
  values = []
  for key in inputDict:
    attr = None
    if isinstance(obj, dict):
      if key in obj.keys() and obj[key] is not None:
        if excludeList is None or key not in excludeList:
          fields.append(inputDict[key])
          attr = obj[key]
    else:
      if hasattr(obj, key) and getattr(obj, key) is not None:
        if excludeList is None or key not in excludeList:
          fields.append(inputDict[key])
          attr = getattr(obj, key)

    if attr is not None:
      if isinstance(attr, basestring):
        escapingStr = MySQLdb.escape_string(str(attr))  # pylint: disable=E1101
        values.append(("'" + escapingStr + "'"))
      else:
        values.append(str(attr))
  return (fields, values)


# #Function converts incoming fields and values lists to the string representation
#
# fields - fields list
# values - values list
# return tupe with string representation
def cleateFieldsValuesLists(fields, values):
  retFields = ""
  retValues = ""
  if len(fields) == len(values):
    for field in fields:
      retFields += (FIELD_QUOTE_SEPARATOR + field + FIELD_QUOTE_SEPARATOR + COMA_SEPARATOR)
    for value in values:
      retValues += value + COMA_SEPARATOR
  else:
    pass
  retFields = stripSymbol(retFields, COMA_SEPARATOR)
  retValues = stripSymbol(retValues, COMA_SEPARATOR)
  return (retFields, retValues)


# #Function string representation of incoming lists (fields and values)
#
# fields - fields list
# values - values list
# return string of fields=values pairs
def createFieldsValuesString(fields, values, excludeList=None):
  ret = ""
  if len(fields) == len(values):
    for fieldIndex in xrange(0, len(fields)):
      if excludeList is None or fields[fieldIndex] not in excludeList:
        ret = ret + FIELD_QUOTE_SEPARATOR + fields[fieldIndex] + FIELD_QUOTE_SEPARATOR + "=" + \
        values[fieldIndex] + COMA_SEPARATOR
  ret = stripSymbol(ret, COMA_SEPARATOR)
  return ret
