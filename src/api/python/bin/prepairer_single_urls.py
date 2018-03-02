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
  a = urlparse(url).netloc.split(":")[0].split(".")
  arr = None
  b = None
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
    print template
    site_templates_dic[template["URL"]] = template["Value"]
  with open("sites_templates_dic", "w") as f:
    f.write(json.dumps(site_templates_dic))
  for (key, value) in site_templates_dic.items():
    url = cutURL(key)
    md5 = hashlib.md5(url).hexdigest()
    templates_dic[md5] = MySQLdb.escape_string(value)
  pass


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

  # create site
  site = Site(norm_url)

  # create site filters
  site_filter_pattern = ".*" + norm_url + ".*"
  site_filters = SiteFilter(site.id, site_filter_pattern)


  # create site properties templates
  if site.id in templates_dic:
    site.properties["template"] = templates_dic[site.id]

  # fill site
  # site.urls = [root_url]
  site.urls = []
  site.filters = [site_filters]
  # site.maxResources = 5
  # site.maxURLs = 5
  # site.state = Site.STATE_SUSPENDED
  # site.filters = [SiteFilter(site.id, "(.*)")]
  return site


def createURLObj(site, input_url):
  url = URL(site.id, input_url)
  url.status = URL.STATUS_SELECTED_CRAWLING
  url.type = URL.TYPE_SINGLE
  return url


def addSite(site):
  file_name = "site_" + str(site.id) + ".json"
  open(file_name, "w").write(site.toJSON())
  cmd = "./dc-client.py --config=../ini/dc-client.ini --command=SITE_NEW --file=./%s" % file_name
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate()
  exit_code = process.wait()
  open("dc-client_new_site_output.txt", "w").write(output)
  return exit_code


def addURL(url, site):
  file_name = "url_" + str(site.id) + ".json"
  open(file_name, "w").write("[" + url.toJSON() + "]")
  cmd = "./dc-client.py --config=../ini/dc-client.ini --command=URL_NEW --file=./%s" % file_name
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate()
  exit_code = process.wait()
  open("dc-client_new_url_output.txt", "w").write(output)
  return exit_code


def updateURL(input_url, site):
  url_updated = URLUpdate(site.id, input_url)
  url_updated.status = URL.STATUS_SELECTED_CRAWLING
  # url_updated.type = URL.TYPE_SINGLE
  file_name = "url_" + str(url_updated.urlMd5) + ".json"
  open(file_name, "w").write("[" + url_updated.toJSON() + "]")
  cmd = "./dc-client.py --config=../ini/dc-client.ini --command=URL_UPDATE --file=./%s" % file_name
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate()
  exit_code = process.wait()
  open("dc-client_update_url_output.txt", "w").write(output)
  return url_updated


def updateSite(site):
  site_updated = SiteUpdate(site.id)
  site_updated.state = Site.STATE_ACTIVE
  file_name = "updated_site_" + str(site_updated.id) + ".json"
  open(file_name, "w").write(site_updated.toJSON())
  cmd = "./dc-client.py --config=../ini/dc-client.ini --command=SITE_UPDATE --file=./%s" % file_name
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate()
  exit_code = process.wait()
  open("dc-client_update_site_output.txt", "w").write(output)


def processBatch():
  # input_url = sys.stdin.read()[0:-1]
  for input_url in sys.stdin:
    input_url = input_url.strip()
    logger.debug(input_url)
    # site_url = "http://" + urlparse(urllib.unquote(input_url).decode('utf8')).hostname
    # site = createSiteObj(site_url)
    site = createSiteObj(input_url)
    open(site.id, "w").write(input_url)
    url = createURLObj(site, input_url)
    addSite(site)
    addURL(url, site)
    # updateURL(input_url, site)
    # updateSite(site)
    time.sleep(1)
    # bItem = BatchItem(site.id, url_updated.urlMd5)
    bItem = BatchItem(site.id, url.urlMd5, url)
    url_list = [bItem]
    input_object = Batch(11, url_list)
    input_pickled_object = pickle.dumps(input_object)
    print input_pickled_object


if __name__ == "__main__":
  # loadDBBackend()
  # generateTemplates()
  processBatch()
