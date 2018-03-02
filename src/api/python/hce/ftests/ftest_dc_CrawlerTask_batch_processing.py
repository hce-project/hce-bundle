"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file ftest_dc_CrawlerTask_batch_processing.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import pickle
from collections import namedtuple
from subprocess import Popen
from subprocess import PIPE
from dc.EventObjects import Batch


url_list = [
  "http://www.yomiuri.co.jp/sports/mlb/20140407-OYT1T50015.html?from=ytop_top"
  ]


PYTHON_BINARY="/usr/bin/python"
CRAWLER_BINARY="../../bin/crawler.py"
CFG="--config=../../ini/crawler.ini"


Results = namedtuple("Results", "exit_code output err")


def processFullBatch(input_object):
  input_pickled_object = pickle.dumps(input_object)
  process = Popen([PYTHON_BINARY, CRAWLER_BINARY, CFG], stdout=PIPE, stdin=PIPE)
  (output, err) = process.communicate(input=input_pickled_object)
  exit_code = process.wait()
  return Results(exit_code, output, err)


if __name__ == "__main__":
  #create batch object from list of urls
  input_object = Batch(url_list)
  #TODO main work
  result = processFullBatch(input_object)
  #get response object 
  generalResponse = pickle.loads(result.output)
  #check if all OK
  assert generalResponse.errorCode == GeneralResponse.ERROR_OK