#!/usr/bin/python

import sys
import json

from dc_crawler.UserProxyJsonWrapper import UserProxyJsonWrapper
from dc.EventObjects import Proxy
from app.Utils import varDump


siteProperty = {"USER_PROXY": "{\"source\": 0,\"file_path\":\"\/home\/hce\/proxy.json\",\"proxies\":{\"84.23.107.195:8080\":{\"host\":\"84.23.107.195:8080\",\"domains\": [\"*\"],\"priority\":11,\"limits\":null}}}" }


jsonData = json.loads(siteProperty["USER_PROXY"])

print jsonData, type(jsonData)

userProxyJsonWrapper = UserProxyJsonWrapper(jsonData)

print 'userProxyJsonWrapper.getProxies() = ', userProxyJsonWrapper.getProxies()

# userProxyJsonWrapper.setProxyData({'host':'dev.intel.com:83', 'domains':['*'], 'priority':1, 'limits':11})
userProxyJsonWrapper.setProxyData({'host':'dev.intel.com:85', 'domains':'[\'.*intel.*\']', 'priority':2, 'limits':22})
userProxyJsonWrapper.setProxyData({'host':'dev.intel.com:85'})

print 'userProxyJsonWrapper.getProxies() = ', userProxyJsonWrapper.getProxies()

print 'userProxyJsonWrapper.getSource() = ', userProxyJsonWrapper.getSource()
print 'userProxyJsonWrapper.getFilePath() = ', userProxyJsonWrapper.getFilePath()
print 'userProxyJsonWrapper.getTriesCount() = ', userProxyJsonWrapper.getTriesCount()

proxy = Proxy('12345', 'localhost')
proxy.priority = 1
userProxyJsonWrapper.addProxyList([proxy])
print 'userProxyJsonWrapper.getProxies() = ', userProxyJsonWrapper.getProxies()
print 'userProxyJsonWrapper.getSource() = ', userProxyJsonWrapper.getSource()
userProxyJsonWrapper.setSource(1)
print 'userProxyJsonWrapper.getSource() = ', userProxyJsonWrapper.getSource()

userProxyJsonWrapper.setSource(0)
print 'userProxyJsonWrapper.getSource() = ', userProxyJsonWrapper.getSource()
print 'userProxyJsonWrapper.getProxyList() = ', userProxyJsonWrapper.getProxyList()

for proxy in userProxyJsonWrapper.getProxyList():
  print 'Proxy: ', varDump(proxy)
