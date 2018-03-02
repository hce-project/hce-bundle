#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file scraper_json_viewer.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import ppath
from ppath import sys

import pickle
import sqlite3 as lite
from dc_processor.scraper_utils import decode


config_db_dir = "../data/dc_dbdata"

def processBatch():
  json = None
  # read pickled batch object from stdin and unpickle it
  input_pickled_object = sys.stdin.read()
  # print input_pickled_object
  input_data = (pickle.loads(input_pickled_object)).items[0]
  # print("Batch item: siteId: %s, urlId: %s" %(input_data.siteId, input_data.urlId))
  if len(input_data.siteId):
    db_name = config_db_dir + "/" + input_data.siteId + ".db"
  else:
    db_name = config_db_dir + "/0.db"
  con = lite.connect(db_name)
  with con:
    cur = con.cursor()
    query = "SELECT `data` FROM `articles` WHERE `id`='%s' order by `CDate` DESC LIMIT 1" % (input_data.urlId)
    cur.execute(query)
    json = cur.fetchone()
  print decode(json[0])


if __name__ == "__main__":
  processBatch()
