#!/usr/bin/python


'''
HCE project, Python bindings, Distributed Crawler application.
Applied utility to check sets of URLs from nodes in URLContent request results.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2014 IOIX Ukraine
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
parser.add_option("-s", "--stat", type="string",
                  help="include stat data", dest="resStat")


if __name__ == "__main__":
  options, arguments = parser.parse_args()

  if options.__dict__["resStat"] is not None:
    statFlag = int(options.__dict__["resStat"])
  else:
    statFlag = 0

  jsonString = sys.stdin.read()

  if jsonString is not None and jsonString != "":
    try:
      #jsonDic = json.loads(jsonString).decode('utf-8')
      jsonDic = json.loads(str(jsonString))

      retVal = {"nodesCount":0, "totalItems":0, "uniqueItems":0, "totalDuplicated":0, "uniqueDuplicated":0,
                "duplicatedFreqsList":{}, "totalItemsList":{}, "statusesFreqList":{}, "resStat":None, "urlStat":None}

      retVal["nodesCount"] = len(jsonDic["itemsList"])

      for i in xrange(1, retVal["nodesCount"] + 1):
        retVal["duplicatedFreqsList"][str(i)] = {}

      idsDict = {}
      urlsDict = {}
      for itemsList in jsonDic["itemsList"]:
        retVal["totalItemsList"][itemsList["host"]] = len(itemsList["itemObject"])
        retVal["totalItems"] = retVal["totalItems"] + len(itemsList["itemObject"])
        idsDict[itemsList["host"]] = {}
        for itemObject in itemsList["itemObject"]:
          idsDict[itemsList["host"]][itemObject["urlMd5"]] = {"freq":0, "url":itemObject["url"],
                                                              "status":itemObject["status"]}
          if itemObject["url"] in urlsDict:
            urlsDict[itemObject["url"]].append([itemsList["host"], itemObject["status"]])
          else:
            urlsDict[itemObject["url"]] = [[itemsList["host"], itemObject["status"]]]
          if str(itemObject["status"]) in retVal["statusesFreqList"]:
            retVal["statusesFreqList"][str(itemObject["status"])] = retVal["statusesFreqList"][str(itemObject["status"])] + 1
          else:
            retVal["statusesFreqList"][str(itemObject["status"])] = 1

      idsDict2 = dict(idsDict)
      for host, idDict in idsDict.iteritems():
        for id, freqDict in idDict.iteritems():
          for host1, idDict1 in idsDict.iteritems():
            if id in idDict1:
              idsDict2[host][id]["freq"] = idsDict2[host][id]["freq"] + 1

      for host, idDict in idsDict2.iteritems():
        for id, freqDict in idDict.iteritems():
          if freqDict["freq"] > 1:
            retVal["totalDuplicated"] = retVal["totalDuplicated"] + 1
          if id not in retVal["duplicatedFreqsList"][str(freqDict["freq"])]:
            retVal["duplicatedFreqsList"][str(freqDict["freq"])][id] = [freqDict]
          else:
            retVal["duplicatedFreqsList"][str(freqDict["freq"])][id].append(freqDict)
          #retVal["duplicatedFreqsList"][str(freqDict["freq"])][id] = host

      for freq, idsDict in retVal["duplicatedFreqsList"].iteritems():
        if int(freq) == 1:
          name = "uniqueItems"
        else:
          name = "uniqueDuplicated"
        retVal[name] = retVal[name] + len(idsDict)
        if statFlag == 0:
          retVal["duplicatedFreqsList"][freq] = len(idsDict)

      if statFlag:
        retVal["resStat"] = idsDict2
        retVal["urlStat"] = urlsDict

      sys.stdout.write(json.dumps(retVal, indent=4, separators=(',', ': ')))

    except Exception, e:
      sys.stdout.write("Json parsing or structure access error : " + e.message + "\n")
  else:
    sys.stdout.write("Input json is empty.\n")

  sys.stdout.flush()



