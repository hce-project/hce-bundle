#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file ftest_dc_full_batch_processing.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import md5
#import pickle
try:
  import cPickle as pickle
except ImportError:
  import pickle
from collections import namedtuple
from subprocess import Popen
from subprocess import PIPE
from dc.EventObjects import Batch
from dc.EventObjects import BatchItem
from dtm.EventObjects import GeneralResponse


siteId1 = str(md5.new("http://www.yomiuri.co.jp").hexdigest())
urlId1 = str(md5.new("http://www.yomiuri.co.jp/sports/mlb/20140407-OYT1T50015.html?from=ytop_top").hexdigest())
bItem1 = BatchItem(siteId1, urlId1)

siteId2 = str(md5.new("http://localhost/www.yomiuri.co.jp").hexdigest())
urlId2 = str(md5.new("http://localhost/www.yomiuri.co.jp/template1.html").hexdigest())
bItem2 = BatchItem(siteId2, urlId2)

siteId3 = ""
urlId3 = str(md5.new("http://localhost/www.yomiuri.co.jp/template1.html").hexdigest())
bItem3 = BatchItem(siteId3, urlId3)


url_list = [
  #bItem1,
  bItem2,
  bItem3
  #"http://192.168.1.61/article1.html"
  #"http://www.yomiuri.co.jp/sports/mlb/20140407-OYT1T50015.html?from=ytop_top"
  ]


PWD="cd ../../bin"
PYTHON_BINARY="/usr/bin/python"
CRAWLER_TASK_BINARY="./crawler-task.py"
CRAWLER_TASK_CFG="--config=../ini/crawler-task.ini"
PROCESSOR_TASK_BINARY="./processor-task.py"
PROCESSOR_TASK_CFG="--config=../ini/processor-task.ini"


Results = namedtuple("Results", "exit_code, output, err")


def processFullBatch(input_object):
  input_pickled_object = pickle.dumps(input_object)
  #process = Popen([PYTHON_BINARY, CRAWLER_TASK_BINARY, CRAWLER_TASK_CFG, " | ", PYTHON_BINARY, PROCESSOR_TASK_BINARY, PROCESSOR_TASK_CFG], stdout=PIPE, stdin=PIPE, shell=True)
  process = Popen(PWD+" && "+PYTHON_BINARY+" "+CRAWLER_TASK_BINARY+" "+CRAWLER_TASK_CFG+" | "+PYTHON_BINARY+" "+PROCESSOR_TASK_BINARY+" "+PROCESSOR_TASK_CFG, stdout=PIPE, stdin=PIPE, shell=True)
  (output, err) = process.communicate(input=input_pickled_object)
  #print output
  exit_code = process.wait()
  return Results(exit_code, output, err)


if __name__ == "__main__":
  #create batch object from list of urls
  #url_list = [str(md5.new(url).hexdigest()) for url in url_list]
  input_object = Batch(1,url_list)
  #TODO main work
  result = processFullBatch(input_object)
  #get response object 
  response = pickle.loads(result.output)
  #check if all OK
  #assert generalResponse.errorCode == GeneralResponse.ERROR_OK