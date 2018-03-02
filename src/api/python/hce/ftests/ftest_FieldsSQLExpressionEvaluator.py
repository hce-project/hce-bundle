'''
Created on Jul 13, 2016

@author: alexander
'''
import unittest
import logging.config
import ConfigParser
import datetime

import dc_crawler.DBTasksWrapper as DBTasksWrapper
import dc.EventObjects
from app.FieldsSQLExpressionEvaluator import FieldsSQLExpressionEvaluator
import app.Consts as APP_CONSTS
from app.Utils import SQLExpression


def getLogger(name='test'):
  # create logger
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(ch)

  return logger

class Test(unittest.TestCase):
  CONFIG_NAME = "../../ini/db-task.ini"

  SITE_ID = '1234567890'
  URL = 'http://127.0.0.1'

  TEST_URL_PROPERTY_CAST_TO_INTEGER = "[{\"URL\":{\"Status\":{\"IF(%ERRORMASK% & 128 > 0, 1, %STATUS%)\":0}}}]"
  TEST_URL_PROPERTY_CAST_TO_STRING = \
  "[{\"URL\":{\"HTTPMethod\":{\"IF(%ERRORMASK% & 128 > 0, 'post', %HTTPMETHOD%)\":1}}}]"
  TEST_URL_PROPERTY_CAST_TO_DATETIME = \
  "[{\"URL\":{\"PDate\":{\"IF(%ERRORMASK% & 128 > 0, '2016-07-01 00:00:00', %PDATE%)\":2}}}]"
  TEST_URL_PROPERTY_CAST_TO_UNSUPPORT = "[{\"URL\":{\"Status\":{\"IF(%ERRORMASK% & 128 > 0, 1, %STATUS%)\":3}}}]"

  TEST_SITE_PROPERTY_CAST_TO_INTEGER = "[{\"Site\":{\"Errors\":{\"IF(%ERRORMASK% & 128 > 0, 1, %ERRORS%)\":0}}}]"

  TEST_PDATE_TIME = "[{\"pattern\": \".*bbc.com\/dir1\/.*\", \"value\":\"IF(TIME(%PDATE%)='00:00:01', TIME(NOW()), TIME(%PDATE%))\"}]"

  def setUp(self):
    cfgParser = ConfigParser.ConfigParser()
    cfgParser.read(self.CONFIG_NAME)
    self.wrapper = DBTasksWrapper.DBTasksWrapper(cfgParser)
    self.logger = getLogger('hce')


  def tearDown(self):
    pass


  # # Get object ('Site' or 'URL')
  #
  # @param objectName - name of object
  # @param fields - dict of names and values for filling of object
  # @return object instance
  def getObject(self, objectName, fields):
    # variable for result
    obj = None

    if objectName == FieldsSQLExpressionEvaluator.OBJECT_NAME_SITE:
      # Create instance of 'Site'
      obj = dc.EventObjects.Site(self.URL)
    elif objectName == FieldsSQLExpressionEvaluator.OBJECT_NAME_URL:
      obj = dc.EventObjects.URL(self.SITE_ID, self.URL)  # pylint: disable=R0204

    if obj is not None:
      for fieldName, fieldValue in fields.items():
        if hasattr(obj, fieldName):
          setattr(obj, fieldName, fieldValue)

    return obj


  # # Get site properties
  #
  # @param propertyName
  # @param propertyValue
  # @return site properties dict
  def getSiteProperties(self, propertyName, propertyValue):
    # variable for result
    ret = {}
    if isinstance(propertyName, basestring) and propertyValue is not None:
      ret[propertyName] = propertyValue

    return ret


  def testURLCastToInteger(self):

    errorMessage = "Return wrong 'status' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER, \
                                            self.TEST_URL_PROPERTY_CAST_TO_INTEGER)

    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'status':7, 'errorMask':128})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["status"] == 1, errorMessage)


    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'status':7, 'errorMask':127})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["status"] == 7, errorMessage)


  def testURLCastToString(self):

    errorMessage = "Return wrong 'httpMethod' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER, \
                                            self.TEST_URL_PROPERTY_CAST_TO_STRING)

    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'httpMethod':'post', 'errorMask':128})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["httpMethod"] == 'post', errorMessage)


    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'httpMethod':'get', 'errorMask':127})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["httpMethod"] == 'get', errorMessage)


  def testURLCastToDatetime(self):

    errorMessage = "Return wrong 'pDate' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER, \
                                            self.TEST_URL_PROPERTY_CAST_TO_DATETIME)

    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL,
                            {'pDate':'2016-01-01 00:00:00', 'errorMask':128})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["pDate"] == '2016-07-01 00:00:00', errorMessage + \
                    ' pDate: ' + str(urlObj.pDate))


    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL,
                            {'pDate':'2016-01-01 00:00:00', 'errorMask':127})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["pDate"] == '2016-01-01 00:00:00', errorMessage + \
                    ' pDate: ' + str(urlObj.pDate))


  def testURLCastToUnsupportType(self):

    errorMessage = "Return wrong 'status' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER, \
                                            self.TEST_URL_PROPERTY_CAST_TO_UNSUPPORT)

    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'status':4, 'errorMask':128})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["status"] == 4, errorMessage)


    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'status':4, 'errorMask':127})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["status"] == 4, errorMessage)


  def testURLWrongStageForUpdate(self):

    errorMessage = "Return wrong 'status' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_PROCESSOR, \
                                            self.TEST_URL_PROPERTY_CAST_TO_UNSUPPORT)

    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'status':4, 'errorMask':128})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["status"] == 4, errorMessage)


    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL, {'status':4, 'errorMask':127})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, None, urlObj, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["status"] == 4, errorMessage)


  def testSiteCastToInteger(self):

    errorMessage = "Return wrong 'errors' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER, \
                                            self.TEST_SITE_PROPERTY_CAST_TO_INTEGER)

    siteObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_SITE, {'errors':2, 'errorMask':128})

    self.logger.debug('siteObj.errors = ' + str(siteObj.errors))
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, siteObj, None, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["errors"] == 1, errorMessage)

    siteObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_SITE, {'errors':2, 'errorMask':127})
    changedFieldsDict = FieldsSQLExpressionEvaluator.execute(siteProperties, self.wrapper, siteObj, None, self.logger, \
                                         APP_CONSTS.SQL_EXPRESSION_FIELDS_UPDATE_CRAWLER)
    self.assertTrue(changedFieldsDict["errors"] == 2, errorMessage)


  def testPDateTime(self):
    errorMessage = "Return wrong 'pDate' value"
    siteProperties = self.getSiteProperties(APP_CONSTS.SQL_EXPRESSION_FIELDS_PDATE_TIME, \
                                            self.TEST_PDATE_TIME)
    urlObj = self.getObject(FieldsSQLExpressionEvaluator.OBJECT_NAME_URL,
                            {'status':4, 'errorMask':0, \
                             'pDate':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                             'url':'http://bbc.com/dir1/index.html'})
    pubdate = FieldsSQLExpressionEvaluator.evaluatePDateTime(siteProperties, self.wrapper, urlObj, self.logger, None)

    self.logger.debug("pubdate = " + str(pubdate))
    self.assertTrue(pubdate == str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), errorMessage)

if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
