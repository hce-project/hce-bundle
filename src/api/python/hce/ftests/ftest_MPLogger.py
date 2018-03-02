#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging.config
import threading
import time

from app.Utils import MPLogger

import ppath


class TestApp(object):
  # Initialization
  def __init__(self, number, logFileName):
    self.number = number
    self.logger = self.__getLogger(logFileName)
    self.logger.debug("Initialized... %s", str(self.number))


  def __getLogger(self, logFileName):

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=logFileName,
                    filemode='w')

    return  MPLogger().getLogger()


  def run(self):
    self.logger.debug("Runned...%s", str(self.number))


  def close(self):
    self.logger.debug("Finished...%s", str(self.number))


def worker(number, logFileName, start):
  """thread worker function"""
  print 'Worker: %s' % number
  try:
    app = TestApp(number, logFileName)
    app.run()
    app.close()
  except Exception, err:
    sys.stderr.write(str(err) + '\n')
  
  return



count = 3
logFileName = '../../log/logger.test.log'
start = False

threads = []
for i in range(count):
  t = threading.Thread(target=worker, args=(i, logFileName, start))
  threads.append(t)
  t.start()

start = True

for t in threads:
  t.join()

