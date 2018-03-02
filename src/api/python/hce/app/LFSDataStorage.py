'''
Created on Mar 17, 2015

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2014-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import json
import os

import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


# # LFSDataStorage Class, implements functional of common crawler data storage
#
class LFSDataStorage(object):

  JSON_EXTENSION = ".json"


  # #Class's constructor
  #
  def __init__(self):
    self.storeDict = {}


  # #Method saveElement saves incoming elements in the storage file that sets in storageDir and domain
  #
  # @param storageDir - root storage dir
  # @param domain - concretes files subputh
  # @param siteId - site's id, that concretes file name
  # @param element - data to save
  def saveElement(self, storageDir, domain, siteId, element):
    jsonStr = json.dumps(element, indent=4)
    if jsonStr is not None and jsonStr != "":
      if os.path.isdir(storageDir):
        localDir = storageDir
        if localDir[-1] != "/":
          localDir += "/"
        localDir += domain
        if not os.path.isdir(localDir):
          try:
            os.makedirs(localDir)
          except Exception:
            pass
        localFileName = localDir
        localFileName += "/"
        localFileName += str(siteId)
        localFileName += self.JSON_EXTENSION
        try:
          fd = open(localFileName, "w")
          fd.write(jsonStr)
          fd.close()
        except IOError:
          logger.debug(">>> LFSDataStorage.saveElement can't open file to write, file=" + localFileName)
      else:
        logger.debug(">>> LFSDataStorage.saveElement can't find root dir, dir=" + storageDir)


  # #Method loadHeaders reads headers data from storage file
  #
  # @param storageDir - root storage dir
  # @param domain - concretes files subputh
  # @param siteId - site's id, that concretes file name
  # @param externalElement - incoming headers that will mix with reading data
  # @param readFromFS - bool value - get element from internal cache or not
  # @return site storage element
  def loadElement(self, storageDir, host, siteId, externalElement=None, readFromFS=False):
    nodeElem = None
    if not readFromFS and host in self.storeDict and siteId in self.storeDict[host]:
      nodeElem = self.storeDict[host][siteId]
    if nodeElem is None:
      if not os.path.isdir(storageDir):
        os.makedirs(storageDir)

      if os.path.isdir(storageDir):
        localDir = storageDir
        if localDir[-1] != "/":
          localDir += "/"
        localDir += host
        if os.path.isdir(localDir):
          localFileName = localDir
          localFileName += "/"
          localFileName += str(siteId)
          localFileName += self.JSON_EXTENSION
          try:
            fd = open(localFileName, "r")
            fileBuf = fd.read()
            if fileBuf is not None and fileBuf != "":
              nodeElem = json.loads(fileBuf)
            fd.close()
          except IOError:
            logger.debug(">>> LFSDataStorage.loadElement can't open file to read, file=" + str(localFileName))
          except Exception as exp:
            logger.debug(">>> LFSDataStorage.loadElement some exception, = " + str(exp))
        else:
          logger.debug(">>> LFSDataStorage.loadElement can't find storage dir, dir=" + str(localDir))
      else:
        logger.debug(">>> LFSDataStorage.loadElement can't find root dir, dir=" + str(storageDir))
    # save nodeElem in class storage hash
    if nodeElem is not None:
      if host not in self.storeDict:
        self.storeDict[host] = {}
      self.storeDict[host][siteId] = nodeElem
    if externalElement is not None:
      if nodeElem is None:
        nodeElem = {}
      for headerKey in externalElement:
        if headerKey not in nodeElem:
          nodeElem[headerKey] = {}
        for valueKey in externalElement[headerKey]:
          if valueKey not in nodeElem[headerKey]:
            nodeElem[headerKey][valueKey] = 0
    return nodeElem


  # #Method returns list of tuples of name from fileStorageHeaders with least freq and
  # which is present in the siteStorageHeaders
  #
  # @param fileStorageElements - incoming items with file storage structure
  # @param siteStorageHeaders - the same for the site storage values
  # @param fileCacheOnly - use only elements from a fileStorageElements as from cache
  # @return optimized low frequency list of name and value tuples
  def fetchLowFreqHeaders(self, fileStorageElements, siteStorageElements=None, fileCacheOnly=False):
    ret = []

    if isinstance(fileStorageElements, dict):
      for headerKey in fileStorageElements:
        minValue = None
        t = None
        for valueKey in fileStorageElements[headerKey]:
          if (minValue is None or minValue > fileStorageElements[headerKey][valueKey]) and \
          (\
           # siteStorageElements is None or \
              siteStorageElements is not None and
              (headerKey in siteStorageElements and isinstance(siteStorageElements[headerKey], list) and \
          valueKey in siteStorageElements[headerKey])):
            minValue = fileStorageElements[headerKey][valueKey]
            t = tuple([headerKey, valueKey])
          elif (minValue is None or minValue > fileStorageElements[headerKey][valueKey]) and fileCacheOnly is True:
            t = tuple([headerKey, valueKey])
        if t is not None:
          ret.append(t)

    return ret


  # #Method converts incoming jsonBuf to the siteStorageElements dict and return them
  #
  # @param jsonBuf - incoming json string with siteStorageElements structure
  # @return siteStorageElements element
  def extractSiteStorageElement(self, jsonBuf):
    ret = None
    try:
      ret = json.loads(jsonBuf)
    except Exception as exp:
      logger.debug(">>> LFSDataStorage.extractSiteStorageElement can't load data from incoming jsonBuf " +
                   "(may be not json format...) exception=" + str(exp))
    return ret

