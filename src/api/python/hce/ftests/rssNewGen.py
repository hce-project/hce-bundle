#!/usr/bin/python

'''
Created on Nov 4, 2014
@author: scorp
'''

import ppath# pylint: disable=W0611
import hashlib
import json

pPath = "../ftests/rss/rss_list.txt"
pTmp = "../ftests/rss/rss_tmp.json"
sPathTmp = "../ftests/rss/snew/site_new_%s.json"

ffile = open(pPath, "r")
obj = json.load(ffile)
ffile.close()

tfile = open(pTmp, "r")
tObj = json.load(tfile)
tfile.close()

for url in obj["rss_list"]:
  md5 = hashlib.md5(url).hexdigest()
  tObj["id"] = md5
  if "filters" in tObj and hasattr(tObj["filters"], '__iter__'):
    for lFilter in tObj["filters"]:
      if "siteId" in lFilter:
        lFilter["siteId"] = md5
  urls = []
  urls.append(url)
  tObj["urls"] = urls
  
  sPath = sPathTmp % md5
  
  sfile = open(sPath, "w")
  json.dump(tObj, sfile, indent=4)
  sfile.close()

if __name__ == '__main__':
    pass