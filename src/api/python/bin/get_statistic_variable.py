#!/usr/bin/python

"""
HCE project, Tools for get statistic variable main functional.

@package: bin
@file get_statistic_variable.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

# Sample of usage: ./get_statistic_variable.py -d=/var/www/archives/grasp/demo/2017/10/09 -p=.*statlog.json -n=itemsDetected

import re
import os
import sys
import json
from cement.core import foundation


# # get arguments
#
# @param - None
# @return tuple of extracted parameters from cmd
def getArgs():
  # variables for result
  dirName = pattern = paramName = None
    
  app = foundation.CementApp('get_statistic_variable')
  app.setup()
  app.add_arg('-d', '--dir', action='store', metavar='input_directory_name', help='input directory name', required=True)
  app.add_arg('-p', '--pattern', action='store', metavar='pattern_file_name', help='pattern file name for search in dirrectory', required=True)
  app.add_arg('-n', '--name', action='store', metavar='parameter_name', help='parameter name in found files', required=True)
  app.add_arg('-o', '--output', action='store', metavar='output_file_name', help='output file name. If not set output in stdout')
  app.run()

  dirName = app.pargs.dir
  pattern = app.pargs.pattern
  paramName = app.pargs.name
  outputFile = app.pargs.output if app.pargs.output else None
  app.close()  
  
  return dirName, pattern, paramName, outputFile


# # get files list
#
# @param dirName - dirrectory name for search files
# @param pattern - re pattern for search files
# @return files list
def getFilesList(dirName, pattern):
  # variable for result
  filesList = []
  if dirName is not None and pattern is not None:
    try:
      files = os.listdir(dirName)
      for fileName in files:
        fullName = dirName + os.sep + fileName
        if os.path.isdir(fullName):
          internalFilesList = getFilesList(fullName, pattern)
          filesList += internalFilesList
        else:
          if re.search(pattern, fullName, re.U + re.I) is not None:
            filesList.append(fullName)
    except Exception:
      pass

  return filesList


# # get value from dict
#
# @param path - path to parameter
# @param itemObject - item object
# @param delimiter - delimiter used for split
# @return extracted value
def getValueFromDict(path, itemObject, delimiter=':'):
  # variable for result
  ret = 0 # itemObject
  fieldNamesList = path.split(delimiter)
  for fieldName in fieldNamesList:
    if isinstance(ret, dict) and fieldName in ret:
      ret = ret[fieldName]
    elif isinstance(ret, list) and fieldName.isdigit():
      ret = ret[int(fieldName)]

  return ret


# # extract data from file
#
# @param fileName - file name
# @param paramName - parameter name
# @return integer value extracted from file
def extractData(fileName, paramName):
  # variable for result
  ret = 0
  try:
    with open(fileName) as f:
      dataDict = json.load(f)
      ret = int(getValueFromDict(paramName, dataDict))

  except Exception, err:
    sys.stderr.write("Extract data from % failed. Error: %s\n" % (fileName, str(err)))

  return ret


# # output data
#
# @param jsonDict - output dictionary
# @param outputFile - output file name
# @return - None
def outputData(jsonDict, outputFile):
  try:
    if isinstance(jsonDict, dict):
      jsonData = json.dumps(jsonDict)

      if outputFile is None:
        sys.stdout.write(jsonData)
      else:
        with open(outputFile, 'w') as f:
          f.write(jsonData)

  except Exception, err:
    sys.stderr.write("Ouput data failed. Error: %s\n" % str(err))


# # Main processing
if __name__ == '__main__':
  # Contants used in json
  FILES_FIELD_NAME = 'files'

  try:
    dirName, pattern, paramName, outputFile = getArgs()

    totalCount = 0
    filesDict = {}
    filesList = getFilesList(dirName, pattern)
    for fileName in filesList:
      value = int(extractData(fileName, paramName))
      filesDict[fileName] = value
      totalCount += value

    # make output dictionary
    jsonDict = {}
    jsonDict[paramName] = totalCount
    jsonDict[FILES_FIELD_NAME] = filesDict

    outputData(jsonDict, outputFile)

  except Exception, err:
    sys.stderr.write("Error: %s\n" % str(err))
  
