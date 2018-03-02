"""
@package: dc
@file CollectProperties.py
@author Scorp <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""
import hashlib
import json
import os
import sqlite3
import lxml

from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


class CollectProperties(object):

  KV_TABLE_TEMPLATES = {
      "titles": ''' CREATE TABLE titles (
      url_id VARCHAR(32) NOT NULL PRIMARY KEY,
      data VARCHAR(100) NOT NULL DEFAULT '')''',

      "redirects": ''' CREATE TABLE redirects (
      url_id VARCHAR(32) NOT NULL PRIMARY KEY,
      data VARCHAR(1000000) NOT NULL DEFAULT '') ''',

      "internal_links": ''' CREATE TABLE internal_links (
      url_id VARCHAR(32) NOT NULL PRIMARY KEY,
      data VARCHAR(1000000) NOT NULL DEFAULT '') ''',

      "external_links": ''' CREATE TABLE external_links (
      url_id VARCHAR(32) NOT NULL PRIMARY KEY,
      data VARCHAR(1000000) NOT NULL DEFAULT '') '''
  }
  KV_DB_TABLE_NAMES = ("titles", "redirects", "internal_links", "external_links")

  def __init__(self):
    self.siteId = None
    self.kvDbDir = None
    self.res = None
    self.batchItem = None
    self.realUrl = None
    self.urlProcess = None


  # #checkFieldsIsNone method checks all class's mandatory fields
  #
  def checkFieldsIsNone(self, checkList):
    # for field in self.__dict__:
    #  if field in checkList and (not hasattr(self, field) or getattr(self, field) is None):
    #    raise Exception(">>> [CollectProperties] Mandatory field must be initialized, field Name = " + field)
    for name in checkList:
      if not hasattr(self, name) or getattr(self, name) is None:
        raise Exception("Some mandatory field `%s` must be initialized!", name)


  # #process - main collectProperties processing point
  #
  # @param dom the - dom tree of the page
  # @param wrapper - db-task wrapper
  # @param internalLinks internal link list
  # @param externalLinks external link list
  def process(self, dom, internalLinks, externalLinks):
    if dom is None:
      raise Exception(">>> [CollectProperties.process] dom param must be not None")
    if internalLinks is None:
      raise Exception(">>> [CollectProperties.process] internalLinks param must be not None")
    if externalLinks is None:
      raise Exception(">>> [CollectProperties.process] externalLinks param must be not None")
    self.checkFieldsIsNone(["siteId", "kvDbDir", "res", "batchItem", "realUrl"])
    kvCursor = None
    try:
      kvConnector, kvCursor = self.collectProperties(dom, internalLinks, externalLinks, self.siteId, self.kvDbDir,
                                                     self.res, self.batchItem.urlId)
    except Exception, err:
      ExceptionLog.handler(logger, err, "collect base properties to key-value db failed", \
                      (self.siteId, self.kvDbDir, self.res, self.batchItem.urlId))
    if kvCursor is not None and kvConnector is not None:
      try:
        self.collectAddtionalProp(kvCursor, len(internalLinks), len(externalLinks), self.batchItem, self.realUrl)
      except Exception, err:
        ExceptionLog.handler(logger, err, "collect addtional propeties to main db failed", \
                             (self.realUrl))
      kvConnector.close()


  # #collectProperties collect page properties to Key-Value DB
  #
  # @param dom - the dom tree of the page
  # @param internalLinks internal link list
  # @param externalLinks external link list
  # @param siteId - site's id
  # @param kvDbDir - kvdb storage directory
  # @param res - resource object
  # @param urlId - url's id
  def collectProperties(self, dom, internalLinks, externalLinks, siteId, kvDbDir, res, urlId):
    kvConnector, kvCursor = self.prepareKvDbConnector(siteId, kvDbDir)
    self.checkKVTable(kvConnector, kvCursor)
    title = None
    domTitle = None
    tmp = dom.find(".//title")
    if tmp is not None:
      domTitle = tmp.text
    if isinstance(domTitle, lxml.etree._Element):  # pylint: disable=E1101,W0212
      title = domTitle.text
    if isinstance(title, str):
      title = title.decode('utf-8')

    histories = []
    for history in res.redirects:
      textHeaders = '\r\n'.join(['%s: %s' % (k, v) for k, v in history.headers.iteritems()])
      historyItem = {"status_code": history.status_code, "headers": textHeaders}
      histories.append(historyItem)
    historiesData = json.dumps(histories)
    internalLinksData = json.dumps(internalLinks)
    externalLinksData = json.dumps(externalLinks)
    # save title
    kvCursor.execute('''INSERT OR REPLACE INTO titles(url_id, data) VALUES(?, ?)''', (urlId, title))

    # save redirects
    kvCursor.execute('''INSERT OR REPLACE INTO redirects(url_id, data) VALUES(?, ?)''', (urlId, historiesData))

    # save internal links
    kvCursor.execute('''INSERT OR REPLACE INTO internal_links(url_id, data) VALUES(?, ?)''', \
      (urlId, internalLinksData))

    # save external links
    kvCursor.execute('''INSERT OR REPLACE INTO external_links(url_id, data) VALUES(?, ?)''', \
      (urlId, externalLinksData))

    kvConnector.commit()
    return kvConnector, kvCursor


  # #collectProperties collect page properties to Key-Value DB
  #
  # @param kvCursor - incoming kvdb Cursor
  # @param wrapper - db-task wrapper
  # @param internalLinks internal link list
  # @param externalLinks external link list
  # @param res -resource object
  # @param batchItem - bathItem object
  # @param realUrl - primary resource's url
  def collectAddtionalProp(self, kvCursor, internalLinksCount, externalLinksCount, batchItem, realUrl):
    self.checkFieldsIsNone(["res", "urlProcess"])
    # logger.debug("Response: %s", str(self.res))
    size = len(self.res.str_content)
    contentMd5 = hashlib.md5(self.res.str_content).hexdigest()
    kvSql = "SELECT data FROM internal_links WHERE url_id <> '%s'" % (batchItem.urlId,)
    kvCursor.execute(kvSql)
    freq = 0
    for row in kvCursor.fetchall():
      urlInternalLists = row["data"]
      if realUrl in urlInternalLists:
        freq += 1

    self.urlProcess.siteId = batchItem.siteId
    self.urlProcess.updateAdditionProps(internalLinksCount, externalLinksCount, batchItem, size, freq, contentMd5)


  # prepare sqlite DB connector and cursor object
  #
  # @param siteId - incoming site's Id
  # @param kvDbDir - incoming kvDb storage directory
  # return kvConnector and kvCursor objects
  def prepareKvDbConnector(self, siteId, kvDbDir):
    dbFile = os.path.join(kvDbDir, "%s_fields.db" % (siteId,))
    kvConnector = sqlite3.connect(dbFile)
    kvConnector.row_factory = sqlite3.Row
    kvConnector.text_factory = unicode
    kvCursor = kvConnector.cursor()
    return kvConnector, kvCursor


  # # checkKVTable check weather the sqlite table exists
  # if not, then create it
  #
  # @param kvConnector - incoming kvdb Connector
  # @param kvCursor - incoming kvdb Cursor
  def checkKVTable(self, kvConnector, kvCursor):
    for table in self.KV_DB_TABLE_NAMES:
      sql = "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table' AND name='%s'" % table
      kvCursor.execute(sql)
      if kvCursor.fetchone()["cnt"] == 0:
        logger.info("kv table %s dose not exist, createing...", table)
        kvCursor.execute(self.KV_TABLE_TEMPLATES[table])
        kvConnector.commit()
