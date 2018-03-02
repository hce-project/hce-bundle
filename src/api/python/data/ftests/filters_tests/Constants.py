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

TASK_DUBLICATE_ERR = 2020
TASK_DUBLICATE_ERR_MSG = "Dublicate site"

EXEC_INDEX = 0
EXEC_NAME = 1

PRIMARY_DB_ID = "primaryDB"
SECONDARY_DB_ID = "secondaryDB"

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


# SQL tempaltes
USE_SQL_TEMPLATE = "USE `%s`"

INSERT_COMMON_TEMPLATE = "INSERT INTO `%s` SET %s"
SITE_SQL_TEMPLATE = "INSERT INTO `sites` %s VALUES %s"
SITE_FILTER_SQL_TEMPLATE = "INSERT INTO `sites_filters` SET `Site_Id`='%s', `Pattern`='%s', `Type`='%s', \
`Mode`='%s', `State`='%s', `Stage`='%s', `Subject`='%s', `Action`='%s'"
SITE_FILTER_SQL_UPDATE = "UPDATE `sites_filters` SET `Pattern`='%s' WHERE `Site_Id`='%s' AND `Type`='%s' \
AND `Mode`='%s' AND `State`='%s'"
SITE_PROP_SQL_TEMPLATE = "INSERT INTO `sites_properties` SET `Site_Id`='%s', `Name`='%s', `Value`='%s'"
SITE_PROP_SQL_ADDITIONS = ", `URLMD5`='%s'"
SITE_PROP_SQL_SHOT = "INSERT INTO `sites_properties` SET %s"
SITE_PROP_SQL_UPDATE = "UPDATE `sites_properties` SET %s WHERE `Site_Id`='%s' AND `Name`='%s'"
SITE_URL_SQL_TEMPLATE = "INSERT INTO `sites_urls` SET `Site_Id`='%s', `URL`='%s', `User_Id`='%s'"
SITE_URL_SQL_UPDATE = "UPDATE`sites_urls` SET `User_Id`='%s' WHERE `Site_Id`='%s' AND `URL`='%s'"

DEL_BY_ID_QUERY_TEMPLATE = "DELETE FROM `%s` WHERE `Site_Id` = '%s'"

SQL_CHECK_TABLE_EXIST_TEMPLATE = """ SELECT IF( EXISTS(SELECT * FROM information_schema.TABLES WHERE Table_Name="%s" \
and TABLE_SCHEMA="%s"), 1, 0) """
DC_SITE_URL_SQL_TEMPLATE = "INSERT INTO `%s` (`Site_Id`, `URL`) VALUES('%s', '%s')"

SELECT_SQL_TEMPLATE = """ SELECT * FROM `%s` WHERE %s"""
SELECT_SQL_TEMPLATE_SIMPLE = """ SELECT %s FROM `%s`"""
SELECT_SITE_ID_BY_URL = "SELECT `Site_Id` FROM `sites_urls` \
WHERE SUBSTRING(\"%s\", 1, LENGTH(URL))=`URL` ORDER BY LENGTH(URL) DESC LIMIT 1"
CHECK_TABLE_SQL_ADDITION = "`User_Id` = %s"

# #sql query which checks existence of a table
CHECK_TABLE_SQL_TEMPLATE = " SELECT COUNT(*) FROM sites WHERE `Id` = '%s'"
CHECK_TABLE_SQL_ADDITION = " AND `User_Id` = %s"

# template for key value file name
KEY_VALUE_FILE_NAME_TEMPLATE = "%s.db"


siteDict = dict({"id": "Id",
             "uDate": "UDate",
             "tcDate": "TcDate",
             "cDate": "CDate",
             "resources": "Resources",
             "contents": "Contents",
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
             "collectedURLs": "CollectedURLs",
             "fetchType": "FetchType"}
        )


propDict = dict({"siteId": "Site_Id",
             "urlMd5": "URLMd5",
             "name": "Name",
             "value": "Value",
             "uDate": "UDate",
             "cDate": "CDate"}
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
             "maxURLsFromPage": "MaxURLsFromPage"}
         )


# #Function strips last symbol in incoming string
#
# incomeStr - incoming string
# symbol - symbol for comparing with last char in string
def stripSymbol(incomeStr, symbol=None):
  ret = incomeStr
  if len(incomeStr) > 0:
    if symbol == None or incomeStr[-1] == symbol:
      ret = incomeStr[:-1]
  return ret


# #Function parse incoming object and dict and converts them to the 2 lists
#
# obj - incoming converting object
# inputDict - incoming converting dict
# return tuple with fields,values lists
def getFieldsValuesTuple(obj, inputDict):
  fields = []
  values = []
  for key in inputDict:
    attr = None
    if isinstance(obj, dict):
      if key in obj.keys() and obj[key] != None:
        fields.append(inputDict[key])
        attr = obj[key]
    else:
      if hasattr(obj, key) and getattr(obj, key) != None:
        fields.append(inputDict[key])
        attr = getattr(obj, key)
    if attr != None:
      if isinstance(attr, str) or isinstance(attr, unicode):
        escapingStr = MySQLdb.escape_string(str(attr))
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


def createFieldsValuesString(fields, values):
  ret = ""
  if len(fields) == len(values):
    for fieldIndex in xrange(0, len(fields)):
      ret = ret + FIELD_QUOTE_SEPARATOR + fields[fieldIndex] + FIELD_QUOTE_SEPARATOR + "=" + \
            values[fieldIndex] + COMA_SEPARATOR
  ret = stripSymbol(ret, COMA_SEPARATOR)
  return ret
