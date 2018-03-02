#!/usr/bin/python
# coding: utf-8
"""
HCE project, Python bindings, Crawler application.
Url normalization tests.

@package: dc
@file ftest_UrlNormalization.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import os
import sys
import argparse
import logging

import ppath
from ppath import sys

# from app.Utils import urlNormalization
import app.Utils as Utils


class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def printMessage(msg, color, newLine=True):
  sys.stdout.write(color + str(msg) + bcolors.ENDC + ('\n' if newLine else ''))


def getLogger():
  # create logger
  logger = logging.getLogger('hce')
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


class OutputFile(object):
  def __init__(self, fileName):
    self.fp = None
    try:
      self.fp = open(fileName, 'w')
    except Exception:
      pass


  def __exit__(self):
    print '__exit__()'


  def write(self, msg):
    if self.fp is not None:
      self.fp.write(msg)


def executeTest(base, url, res, log=None):
#   print base, ' ', url, ' ', res
  result = Utils.urlNormalization(base, url, log=log)
  if result != res:
    printMessage("Wrong result: %s\nexpected: %s\n(base: %s, url: %s)" % (result, res, base, url), bcolors.FAIL)
  else:
    printMessage("Success", bcolors.OKGREEN, False)
    printMessage(' : %s' % url, bcolors.HEADER)

  return result == res


def createParser():
  pr = argparse.ArgumentParser()
  pr.add_argument('-i', '--inputFile')
  pr.add_argument('-o', '--outputFile')

  return pr


if __name__ == "__main__":
  try:
    logger = None # getLogger()

    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.inputFile is None:
      raise Exception("Not set input file name")

    ofile = OutputFile(namespace.outputFile)
    
    with open(namespace.inputFile, 'r') as f:
      lines = f.readlines()

      base = None
      url = None
      res = None
      for line in lines:
        parts = line.split()
        if len(parts) == 1:
          base = parts[0]
        elif len(parts) == 2:
          url, res = parts
          if executeTest(base, url, res, logger):
            ofile.write('Success: %s\n' % url)
          else:
            ofile.write('Fail: %s\n' % url)

  except Exception, err:
    sys.stderr.write(str(err) + '\n')
