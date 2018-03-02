#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file prepairer.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import ppath
from ppath import sys

import hashlib
import md5
import time
import json
import logging
from subprocess import Popen
from subprocess import PIPE
import MySQLdb as mdb
import MySQLdb.cursors
from contextlib import closing

import pickle
import urllib
from urlparse import urlparse
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dc.EventObjects import Site
from dc.EventObjects import SiteUpdate
from dc.EventObjects import URL
from dc.EventObjects import URLUpdate
from dc.EventObjects import SiteFilter

logging.basicConfig(filename="prepairer.log", filemode="w")
logger = logging.getLogger("Prepairer")
logger.setLevel("DEBUG")

db_connector = None
dc_sites_db_connect = None
dc_urls_db_connect = None


site_templates_dic = {}
templates_dic = {}


def readTemplatesFromMySQL():
  query = "SELECT sites_urls.URL, sites_properties.`Value` FROM  `sites_properties` INNER JOIN sites_urls ON sites_urls.Site_Id = sites_properties.Site_Id AND sites_properties.Name = 'template'"
  print query
  rows = executeQuery(dc_sites_db_connect, query)
  return rows


def cutURL(url):
  b = url
  arr = None
  a = urlparse(url).netloc.split(":")[0].split(".")
  if len(a) > 2 and a[-3] != "www":
    arr = a[-3:]
    b = str(arr[-3] + "." + arr[-2] + "." + arr[-1])
  else:
    arr = a[-2:]
    b = str(arr[-2] + "." + arr[-1])
  return b


def generateTemplates():
  templates = readTemplatesFromMySQL()
  print templates
  for template in templates:
    # print template
    site_templates_dic[template["URL"]] = template["Value"]
  with open("sites_templates_dic", "w") as f:
    f.write(json.dumps(site_templates_dic))


def fillTemplates():
  global site_templates_dic
  print site_templates_dic
  for (key, value) in site_templates_dic.items():
    url = cutURL(key)
    md5 = hashlib.md5(url).hexdigest()
    templates_dic[md5] = MySQLdb.escape_string(value)


def readTemplatesFromFile():
  global site_templates_dic
  with open("sites_templates_dic", "r") as f:
    site_templates_dic = json.loads(f.read())
  print site_templates_dic


def executeQuery(db_connector, query):
  try:
    with closing(db_connector.cursor(MySQLdb.cursors.DictCursor)) as cursor:
      cursor.execute(query)
      db_connector.commit()
      return cursor.fetchall()
  except mdb.Error as err:  # @todo logging in db_task
    db_connector.rollback()
    raise


def loadDBBackend():
  global db_connector
  global dc_sites_db_connect
  global dc_urls_db_connect

  dbHost = "127.0.0.1"
  dbPort = 3306
  dbUser = "hce"
  dbPWD = "hce12345"

  db_dc_sites = "dc_sites"
  db_dc_urls = "dc_urls"

  dc_sites_db_connect = mdb.connect(dbHost, dbUser, dbPWD, db_dc_sites, dbPort)
  dc_urls_db_connect = mdb.connect(dbHost, dbUser, dbPWD, db_dc_urls, dbPort)


def createSiteObj(input_url):

  # strip input url
  input_url = input_url.strip()

  # root url
  root_url = input_url

  # get url for md5
  norm_url = cutURL(input_url)
  # norm_url = input_url

  # create site
  site = Site(norm_url)
  site.urls = [input_url]
  # create site filters
  # site_filter_pattern = ".*" + norm_url + ".*"
  site_filter_pattern = ".*" + cutURL(input_url) + ".*"
  site_filters = SiteFilter(site.id, site_filter_pattern)


  # create site properties templates
  print templates_dic
  print site.id
  if site.id in templates_dic:
    site.properties["template"] = templates_dic[site.id]

  # fill site
  # site.urls = [root_url]
  # site.urls = []
  site.filters = [site_filters]
  site.maxResources = 100000
  site.maxURLs = 100000
  site.maxErrors = 100000
  site.maxResourceSize = 1000000
  # site.state = Site.STATE_SUSPENDED
  # site.filters = [SiteFilter(site.id, "(.*)")]
  return site


def addSite(site):
  file_name = "site_" + str(site.id) + ".json"
  open(file_name, "w").write(site.toJSON())



if __name__ == "__main__":
  loadDBBackend()
  # generateTemplates()
  readTemplatesFromFile()
  fillTemplates()
  for input_url in sys.stdin:
    site = createSiteObj(input_url)
    addSite(site)
