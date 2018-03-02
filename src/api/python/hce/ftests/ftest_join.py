#!/usr/bin/python
'''
HCE project, Python bindings, DC dependencies
The join tools research tests.

@package: drce
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ppath
from ppath import sys

import os
from subprocess import Popen, PIPE
from tempfile import SpooledTemporaryFile as tempfile
from subprocess import Popen
from subprocess import PIPE

from app.Utils import varDump

testDataDir = './join-convertor-data'
testOutputFile = '/tmp/join_output_file.json'
testDelimiter = ';'

delimiterTemplate = "--delimiter='%s'"
firstCmdTemplate = "cd ~/hce-node-bundle/api/python/bin && ./join.py --files='%s' --output_file='%s'"
secondCmdTemplate = "cd ~/hce-node-bundle/api/python/bin && ./join.py --files='%s'"


def execute(cmd):
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True)
  output, err = process.communicate()
  exitCode = process.wait()
  return output, err, exitCode


def makeInputFileList(dataDir, delimiter=None):
  # variable for result
  ret = ''

  if os.path.isdir(dataDir):
    filesList = [os.path.abspath(os.path.join(dataDir, f)) for f in os.listdir(dataDir) if os.path.isfile(os.path.join(dataDir, f))]

    if delimiter is None:
      delimiter = ' '

    ret = delimiter.join(filesList)

  return ret


def testExecute(cmd, files):
  print ("cmd: " + str(cmd))

  output, err, exitCode = execute(cmd)
  print ("exitCode: " + str(exitCode))
  print ("error: " + str(err))
  print ("output: " + str(output))


if __name__ == "__main__":
  files = makeInputFileList(testDataDir, testDelimiter)
  print ("files: " + str(files))

  cmd = (firstCmdTemplate % (files, testOutputFile)) + ' ' + (delimiterTemplate % testDelimiter)
  testExecute(cmd, files)

  files = files.split(testDelimiter)[0]
  print ("files: " + str(files))
  cmd = (firstCmdTemplate % (files, testOutputFile)) + ' ' + (delimiterTemplate % testDelimiter)
  testExecute(cmd, files)

  cmd = (firstCmdTemplate % (files, testOutputFile)) + ' ' + (delimiterTemplate % testDelimiter)
  testExecute(cmd, files)

  cmd = secondCmdTemplate % files
  testExecute(cmd, files)
