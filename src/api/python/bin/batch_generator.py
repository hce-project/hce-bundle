#!/usr/bin/python


"""
  HCE project,  Python bindings, Distributed Tasks Manager application.
  Event objects definitions.
  
  @package: dc
  @file batch_generator.py
  @author Oleksii <developers.hce@gmail.com>
  @link: http://hierarchical-cluster-engine.com/
  @copyright: Copyright &copy; 2013-2014 IOIX Ukraine
  @license: http://hierarchical-cluster-engine.com/license/
  @since: 0.1
  """


import ppath
import os
import sys
import json
import pickle
import hashlib
import logging

from app.Utils import varDump
import dc.EventObjects as dc_event


EXIT_SUCCESS = 0
EXIT_FAILURE = 1

LOGGER_NAME = "batch_generator"

MSG_ERROR_READ_BATCH = "ERROR READ BATCH FROM STDIN"


logging.basicConfig(filename="../log/batch_generator.log", filemode="w")
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel("DEBUG")


if __name__ == "__main__":
  error = EXIT_SUCCESS
  input_json = sys.stdin.read()
  batch_data = json.loads(input_json)
  site_id = batch_data["site_id"]
  urls = batch_data["urls"]
  tags = batch_data["tags"]
  id = batch_data["id"]
  logger.debug("id: <<%s>>, site_id: <<%s>>, urls: <<%s>>, tags: <<%s>>" % (id, site_id, urls, tags))
  item_no = 1
  batch_items = []
  for item in urls:
    item_url = item["url"]
    item_site_id = None
    if "site_id" in item:
      item_site_id = item["site_id"]
    logger.debug("URL #%s: url: <<%s>>, site_id: <<%s>>" % (item_no, item_url, item_site_id ))
    item_no = item_no + 1
    sid = item_site_id or site_id
    uid = hashlib.md5(item_url).hexdigest()
    url_obj = dc_event.URL(sid, item_url)
    batch_item = dc_event.BatchItem(sid, uid, url_obj)
    batch_items.append(batch_item)
  batch_obj = dc_event.Batch(id, batch_items, dc_event.Batch.TYPE_REAL_TIME_CRAWLER)
  logger.debug("BATCH: %s" % varDump(batch_obj))
  print pickle.dumps(batch_obj)
  sys.stdout.flush()
  os._exit(error)
