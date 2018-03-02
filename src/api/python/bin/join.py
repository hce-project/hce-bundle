#!/usr/bin/python

"""
HCE project, Python bindings, Distributed Tasks Manager application.
join.py - cli tool to join data files list delimited with space passed via stdin in 
to one output serialized json stream to stdout.

@package: dc
@file join.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import ppath
from ppath import sys

import os
import sys
import json
import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from app.Utils import varDump

from cement.core import foundation


exitCode = APP_CONSTS.EXIT_SUCCESS
DEFAULT_DELIMITER_VALUE = ' '

# #Parse command line argumets
#
# @param - None
# @return inputFiles - input files list and outputFile - output file name
def parseArguments():
  # variables for result
  inputFiles = outputFile = None

  # create the app
  app = foundation.CementApp('join_tools')
  try:
    # setup the application
    app.setup()
    # add support command line arguments
    app.args.add_argument('-f', '--files', action='store', metavar='input_file_names', help='input file names',
                          required=True)
    app.args.add_argument('-d', '--delimiter', action='store', metavar='delimiter', help='delimiter of input file names string',
                          required=False)
    app.args.add_argument('-o', '--output_file', action='store', metavar='output_file', help='output file name',
                          required=False)
    # run the application
    app.run()

    # get parameters
    delimiter = DEFAULT_DELIMITER_VALUE
    if app.pargs.delimiter is not None:
      delimiter = app.pargs.delimiter

    if app.pargs.files is not None:
      inputFiles = app.pargs.files.split(delimiter)

    if app.pargs.output_file is not None:
      outputFile = app.pargs.output_file

  except Exception, err:
    sys.stderr.write(str(err) + '\n' + Utils.getTracebackInfo() + '\n')
  finally:
    app.close()

  return inputFiles, outputFile


# # Read input file
#
# @param fileName- input file name
# @return loaded json from file
def readFile(fileName):
  # variable for result
  ret = None
  try:
    f = open(fileName, 'r')
    ret = json.load(f)
    f.close()

  except Exception, err:
    sys.stderr.write(str(err) + '\n')

  return ret


# # Output result data
#
# @param outputFile - output file name
# @param result - result data
# @return - None
def outputResultData(outputFile, result):
  if result is not None:
    if outputFile is None:
      sys.stdout.write(json.dumps(result))
    else:
      f = open(outputFile, 'w')
      json.dump(result, f)
      f.close()


# # Merge data
#
# @param inputFiles - input file names list
# @param result - result data
def mergeData(inputFiles):
  # variable for result
  ret = None
  if isinstance(inputFiles, list):
    objs = []
    for fileName in inputFiles:
      obj = readFile(fileName)
      if obj is not None:
        objs.append(obj)

    if len(objs) > 0:
      ret = objs[0]

    for index, obj in enumerate(objs, 1):
      ret['itemsList'][0]['itemObject'].extend(obj['itemsList'][0]['itemObject'])

  return ret


if __name__ == "__main__":
  try:
    inputFiles, outputFile = parseArguments()
    result = mergeData(inputFiles)
    outputResultData(outputFile, result)
  except Exception as err:
    sys.stderr.write(str(err) + '\n' + Utils.getTracebackInfo() + '\n')
    exitCode = APP_CONSTS.EXIT_FAILURE
  except:
    exitCode = APP_CONSTS.EXIT_FAILURE

  sys.stdout.flush()
  os._exit(exitCode)
