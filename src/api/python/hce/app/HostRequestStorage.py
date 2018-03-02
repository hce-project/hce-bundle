'''
Created on Mar 17, 2015

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import json
import re
import time
import os
import random

import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # HostRequestStorage Class, implements functional http delay by hosts frequence
#
class HostRequestStorage(object):

  ITEM_PROCESS = 0
  ITEM_BREAK = 1
  JSON_SUFF = ".json"
  PATH_CONFIG_KEY = "PATH_CONFIG"
  TAIL_SLASH_LAMBDA = lambda self, path: '' if (path is None or len(path) == 0 or path[-1] == '/') else '/'
  FREQ_AVERAGE_LIST_SIZE = 5
  HTTP_FREQ_LIMITS_FILE_NAME_PREFIX = "http_freq_limits_"

  # #Class's constructor
  #
  # @param httpFreqLimits - incoming HTTP_FREQ_LIMITS property
  def __init__(self, httpFreqLimits):
    self.httpFreqLimits = None
    try:
      self.httpFreqLimits = json.loads(httpFreqLimits)
    except Exception as excp:
      logger.debug(">>> wrong with httpFreqLimits json.loads; " + str(excp))


  # #Method checkHost checks current url in the HTTP_FREQ_LIMITS structure
  #
  # @param path - path to the file storage data
  # @param url - element's url
  # @param siteId - site's id
  # @return delay operation state
  def checkHost(self, path, url, siteId):
    ret = self.ITEM_PROCESS
    domain = Utils.UrlParser.getDomain(url)
    if path is None and self.httpFreqLimits is not None and self.PATH_CONFIG_KEY in self.httpFreqLimits:
      path = self.httpFreqLimits[self.PATH_CONFIG_KEY]

    if self.httpFreqLimits is not None and path is not None and domain is not None and siteId is not None:
      httpFreqLimit = None
      for elem in self.httpFreqLimits:
        if elem != self.PATH_CONFIG_KEY:
          if re.compile(elem).match(domain) is not None:
            httpFreqLimit = self.httpFreqLimits[elem]
            break
      if httpFreqLimit is not None:
        fpath = path + self.TAIL_SLASH_LAMBDA(path) + domain + '/' + \
        self.HTTP_FREQ_LIMITS_FILE_NAME_PREFIX + str(siteId) + self.JSON_SUFF
        freqJson = None
        try:
          with open(fpath, 'r') as fd:
            freqBuf = fd.read()
            freqJson = json.loads(freqBuf)
        except Exception as excp:
          logger.debug(">>> wrong in HostRequestStorage.checkHost method; " + str(excp))
#        if freqJson is not None and "requestData" in freqJson:
#          nowTime = int(time.time())
#          if (freqJson["requestData"] + httpFreqLimit["max_freq"]) > nowTime:
#            delayTime = (freqJson["requestData"] + httpFreqLimit["max_freq"]) - nowTime
#            if delayTime > httpFreqLimit["max_delay"]:
#              ret = self.ITEM_BREAK
#            else:
#              if "randomized" in httpFreqLimit and int(httpFreqLimit["randomized"]) > 0:
#                delayTime += random.randint(1, int(httpFreqLimit["max_delay"]))
#                logger.debug(">>> Use 'randomized' for delay")
#
#              logger.debug(">>> start delay = " + str(delayTime))
#              time.sleep(delayTime)
#              logger.debug(">>> finish delay = " + str(delayTime))
#          freqJson["requestData"] = nowTime
#        else:
#          freqJson = {"requestData": int(time.time())}
        if freqJson is not None and "start" in freqJson and "count" in freqJson:
          nowTime = int(time.time())
          start = int(freqJson["start"])
          count = int(freqJson["count"])

          freqAverage = 0.0
          delayTime = 0
          delta = int(nowTime - start)
          if delta > 0:
            freqAverage = float(count) / delta
          if count > 0:
            delayTime = delta / count

          logger.debug('freqAverage = ' + str(freqAverage) + ' compare ' + str(float(httpFreqLimit["max_freq"])))
          logger.debug('delayTime = ' + str(delayTime) + ' compare ' + str(int(httpFreqLimit["max_delay"])))
          logger.debug('count = ' + str(count))

          if float(freqAverage) > float(httpFreqLimit["max_freq"]):
            logger.debug("Checking 'max_freq' passed: " + str(freqAverage) + " > " + \
                         str(float(httpFreqLimit["max_freq"])))
            ret = self.ITEM_BREAK
          # elif delayTime > 2 * int(httpFreqLimit["max_delay"]):
          #  logger.debug("Checking 'max_delay' passed: " + str(delayTime) + " > " + \
          #                 str(float(httpFreqLimit["max_delay"])))
          #  ret = self.ITEM_BREAK
          else:
            if delayTime <= int(httpFreqLimit["max_delay"]):
              delayTime = int(httpFreqLimit["max_delay"]) - delayTime

            if "randomized" in httpFreqLimit and int(httpFreqLimit["randomized"]) > 0:
              delayTime += random.randint(1, int(httpFreqLimit["max_delay"]))
              logger.debug(">>> Use 'randomized' for delay")

            if delayTime > 0 and delayTime <= int(httpFreqLimit["max_delay"]):
              logger.debug(">>> start max_delay = " + str(delayTime))
              time.sleep(delayTime)
              logger.debug(">>> finish max_delay = " + str(delayTime))

          freqJson["count"] = count + 1
        else:
          freqJson = {"start": int(time.time()), "count":0}


        if os.path.exists(path):
          if not os.path.exists(path + self.TAIL_SLASH_LAMBDA(path) + domain):
            try:
              os.mkdir(path + self.TAIL_SLASH_LAMBDA(path) + domain)
            except Exception as excp:
              logger.debug(">>> makedir exception " + str(excp))
          with open(fpath, 'w') as fd:
            freqBuf = json.dumps(freqJson)
            fd.write(freqBuf)
        else:
          logger.debug(">>> path not exists !!! path: " + path)
    return ret
