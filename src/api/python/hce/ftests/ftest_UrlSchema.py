'''
Created on Nov 23, 2015

@author: scorp
'''
import os
import unittest
import logging
from dc_crawler.UrlSchema import UrlSchema
import app.Consts as APP_CONSTS


class Test(unittest.TestCase):

  def __init__(self, methodName='runTest'):
    unittest.TestCase.__init__(self, methodName)
    self.testUrls = {}
    self.testSchemas = {}
    self.testUrls["url1"] = "http://domen1.com/file?%param1%&from%param2%and%param3%_end"
    self.testUrls["schema1"] = ("{\"type\": 1,  \"mode\": 0, \"parameters\" : {\"param1\" : [\"z1\", \"z2\"], " +
                               "\"param2\" : [\"ffA1\", \"ffA2\", \"ffA\"]}, \"max_items\": 33}")
    self.testUrls["result1"] = ["http://domen1.com/file?z1&fromffA1and%param3%_end"]
    self.testUrls["url2"] = "http://domen1.com/file?%param1%&from%param2%and%param3%_end"
    self.testUrls["schema2"] = ("{\"type\": 2,  \"mode\": 0, \"parameters\" : {\"param1\" : {\"min\": 10, " +
                                "\"max\": 22, \"step\": 3}, \"param2\" : {\"min\": -22, " +
                                "\"max\": 0, \"step\": 1}}, \"max_items\": 33}")
    self.testUrls["result2"] = ["http://domen1.com/file?10&from-22and%param3%_end"]
    self.testUrls["url3"] = "http://domen1.com/file?%param1%&from%param2%and%param3%_end"
    self.testUrls["schema3"] = ("{\"type\": 3,  \"mode\": 0, \"parameters\" : {\"param1\" : {\"min\": 10, " +
                                "\"max\": 22, \"step\": 3}, \"param2\" : {\"min\": -22, " +
                                "\"max\": 0, \"step\": 1}}, \"max_items\": 33}")
    self.testUrls["url4"] = "http://domen1.com/file?%param1%&from%param2%and%param3%_end"
    self.testUrls["schema4"] = ("{\"type\": 3,  \"mode\": 0, \"parameters\" : {\"param1\" : {\"min\": 10, " +
                                "\"max\": 22, \"chars\": 0, \"case\": 0}, \"param2\" : {\"min\": -22, " +
                                "\"max\": 0, \"chars\": 1, \"case\": 1}}, \"max_items\": 33}")

    self.testUrls["url5"] = "http://domen1.com/file?%param1%&from%param2%and%param3%_end"
    self.testUrls["schema5"] = ("{\"type\": 1,  \"mode\": 1, \"parameters\" : {\"param1\" : [\"z1\", \"z2\"], " +
                               "\"param2\" : [\"ffA1\", \"ffA2\", \"ffA\"]}, \"max_items\": 3}")
    self.testUrls["result5"] = ["http://domen1.com/file?z1&fromffA1and%param3%_end"]


  def test_1_Predefined_One(self):
    schema = UrlSchema(self.testUrls["schema1"])
    self.assertTrue(schema.generateUrlSchema(self.testUrls["url1"]) == self.testUrls["result1"])


  def test_2_IncrementInt_One(self):
    schema = UrlSchema(self.testUrls["schema2"])
    self.assertTrue(schema.generateUrlSchema(self.testUrls["url2"]) == self.testUrls["result2"])


  def test_3_RandomInt_One(self):
    schema = UrlSchema(self.testUrls["schema3"])
    retList = schema.generateUrlSchema(self.testUrls["url3"])
    self.assertTrue(len(retList) == 1)
    self.assertTrue(retList[0].find("param1") == -1)
    self.assertTrue(retList[0].find("param2") == -1)


  def test_4_RandomChar_One(self):
    schema = UrlSchema(self.testUrls["schema4"])
    retList = schema.generateUrlSchema(self.testUrls["url4"])
    self.assertTrue(len(retList) == 1)
    self.assertTrue(retList[0].find("param1") == -1)
    self.assertTrue(retList[0].find("param2") == -1)


  def test_5_Predefined_List(self):
    schema = UrlSchema(self.testUrls["schema5"])
    retList = schema.generateUrlSchema(self.testUrls["url5"])
    self.assertTrue(len(retList) == 3)
    self.assertTrue(retList[0] == self.testUrls["result5"][0])


def getLogger():
  # create logger
  logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
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


def test():
  logger = getLogger()
  testDataList = ['111', '222', '333', '1 2 3', '4 5']

  testUrl = 'http://127.0.0.1/some_test_url_%%'
  testFilePath = '/tmp/urlSchemaTestFile.json'
  urlSchemaData = "{\"type\":1, \"parameters\":{}, \"file_path\": \"%s\", \"mode\":1, \"max_items\":200, \"delimiter\":\"%s\",\"format\":\"plain-text\", \"url_encode\":1, \"batch_insert\":2}"
  urlSchemaDelimiter = ''
  urlSchemaParameter = urlSchemaData % (testFilePath, urlSchemaDelimiter)

  print urlSchemaParameter

  # fill data file
  f = open(testFilePath, 'w')
  if urlSchemaDelimiter == "":
    for word in testDataList:
      f.write(word + '\n')
  else:
    for word in testDataList:
      f.write(word + urlSchemaDelimiter)
  f.close()

#   f = open(testFilePath, 'r')
#   data = f.read()
#   f.close()
#   print data

  schema = UrlSchema(schema=urlSchemaParameter)
  resUrls = schema.generateUrlSchema(testUrl)

  print "Result:"
  for url in resUrls:
    print url

#   if os.path.isfile(testFilePath):
#     os.remove(testFilePath)


if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  # unittest.main()

  test()
