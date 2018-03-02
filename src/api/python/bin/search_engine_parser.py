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

# Example of using
# ./search_engine_parser.py  < ../data/ftests/test_search_engine/list_of_urls.txt

import ppath
from ppath import sys

import logging
from subprocess import Popen
from subprocess import PIPE
import pickle
import hashlib
import requests
import datetime
from dc_processor.ScraperInData import ScraperInData
import app.Utils

logging.basicConfig(filename="/tmp/search_engine.log", filemode="w")
logger = logging.getLogger("search_engine")
logger.setLevel("DEBUG")


def process(input_data):
  logger.debug("input: %s" % input_data)
  splitted_data = input_data.split(',')
  url = splitted_data[0]
  site_id = "d57f144e7b26c9976769ea94f18b9064" if "google" in url else "1fe592caf03fd50c5f065c30f82b13bb"
  #site_id = hashlib.md5(app.Utils.UrlParser.generateDomainUrl(url)).hexdigest()
  logger.debug("site_id: %s" % str(site_id))
  template = None
  if len(splitted_data)==2:
    template = splitted_data[1]
  content = getContent(url)
  lastModified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  input = ScraperInData(url, None, site_id, content, "", None, lastModified, None)
  input_pickled_object = pickle.dumps(input)
  #logger.debug("scraper input: %s", str(input_pickled_object))
  cmd = "./scraper.py --config=../ini/scraper_search_engine.ini"
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate(input=input_pickled_object)
  logger.debug("scraper response output: %s", str(output))
  logger.debug("scraper response error: %s", str(err))
  exit_code = process.wait()
  return output


def getContent(url):
  # wget -S --no-check-certificate -U "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3" "https://www.google.com/search?q=mac+os"
  cmd = "wget -qO- -S --no-check-certificate -U 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3' '" + url + "'"
  # cmd = "wget -qO- -S --no-check-certificate -U 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3' 'https://www.google.com/search?q=mac+os'"
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate()
  exit_code = process.wait()
  # output = open("google.out", "rb").read()
  # raw_html = output
  # open("/tmp/google.out", "wb").write(output)
  #logger.debug("Raw content output: %s", output)
  # logger.debug("Raw content error: %s", str(err))
  # print raw_html

  # headers = {}
  # headers["User-Agent"] = "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3"
  # content = requests.get(url=url, headers=headers, verify=False)
  # open("del.txt", "wb").write(output)
  # logger.debug("request response: %s", content.text)
  return output


if __name__ == "__main__":
  for input_url in sys.stdin:
    output = process(input_url)
    print output
