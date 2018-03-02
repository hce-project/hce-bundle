#!/usr/bin/python


'''
HCE project, Python bindings, Distributed Crawler application.
Application level constants and enumerations.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import ppath
from ppath import sys

import hashlib
from optparse import OptionParser
import json
import base64

parser = OptionParser()
parser.add_option("-f", "--field", type="string",
                  help="json field pathname semicolon delimited, for example response:error_code", dest="field")
parser.add_option("-b", "--base64", type="string",
                  help="base64 decode value", dest="base64")


if __name__ == "__main__":
  options, arguments = parser.parse_args()

  if options.__dict__["field"]:
    fieldNameStr = options.__dict__["field"]
    if options.__dict__["base64"] is not None:
      base64Decode = int(options.__dict__["base64"])
    else:
      base64Decode = 0

    if fieldNameStr is not None and fieldNameStr != "":
      fieldNamesList = fieldNameStr.split(":")
      jsonString = sys.stdin.read()

      if jsonString is not None and jsonString != "":
        try:
          #jsonDic = json.loads(jsonString.decode('utf-8'))
          jsonDic = json.loads(str(jsonString))

          retVal = jsonDic
          for fieldName in fieldNamesList:
            if isinstance(retVal, dict):
              for jsonName in retVal:
                if fieldName == jsonName:
                  retVal = retVal[fieldName]
                  break
            else:
              if isinstance(retVal, list):
                if fieldName == "__LEN__":
                  retVal = str(len(retVal))
                  break
                else:
                  index = int(fieldName)
                  if len(retVal) > index:
                    retVal = retVal[index]
                  else:
                    retVal = ""
              else:
                if fieldName == "__LEN__":
                  retVal = -1
                  break
          if base64Decode and fieldName != "__LEN__":
            retVal = base64.b64decode(str(retVal))
          else:
            retVal = retVal

          if isinstance(retVal, dict):
            retVal = json.dumps(retVal)

          if isinstance(retVal, unicode):
            sys.stdout.write(retVal)
          else:
            sys.stdout.write(str(retVal))
        except Exception, e:
          sys.stdout.write("Json parsing or item select error : " + str(e) + "\n")
      else:
        sys.stdout.write("Input json is empty.\n")
    else:
      sys.stdout.write("Json field name [" + str(fieldNameStr) + "] error!\n")
  else:
    sys.stdout.write("Mandatory argument(s) not specified, try -h to get detailed descriptions.\n")

  sys.stdout.flush()



