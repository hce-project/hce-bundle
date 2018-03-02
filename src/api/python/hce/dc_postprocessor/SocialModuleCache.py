# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Social module cache main functional.

@package: dc_postprocessor
@file SocialModuleCache.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2018 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import json
import ConfigParser

import app.Utils as Utils
from app.CacheDataStorage import CacheDataStorage


class SocialModuleCache(CacheDataStorage):

  CONFIG_OPTION_VALIDATION_MAP = "validationMap"

  # Initialization
  #
  # @param configOptionsExtractor - it can be config parser instance or callback function for getting config options
  # @param log - logger instance
  # @param delayInit - boolean flag in mean delay initialization
  def __init__(self, configOptionsExtractor, log, delayInit=False):
    CacheDataStorage.__init__(self, configOptionsExtractor, log, delayInit=False)
    self.loadConfigOptions(configOptionsExtractor)

    self.itemsDataDict = CacheDataStorage.ItemsDataDict(uniqueKeyName=self.configOptions.uniqueKeyName,
                                                        cachedFieldName=self.configOptions.cachedFieldName)

    if not delayInit:
      self.init()


  # # load config options
  #
  # @param configOptionsExtractor - it can be config parser instance or callback function for getting config options
  # @return confgi options instance
  def loadConfigOptions(self, configOptionsExtractor):
    try:
      getConfigOption = None

      if isinstance(configOptionsExtractor, ConfigParser.RawConfigParser):
        getConfigOption = configOptionsExtractor.get
      elif callable(configOptionsExtractor):
        getConfigOption = configOptionsExtractor
      else:
        raise Exception(CacheDataStorage.MSG_ERROR_INPUT_PARAMETER)

      self.configOptions.validationMap = Utils.jsonLoadsSafe(jsonString=getConfigOption(self.__class__.__name__, \
                                                                                        self.CONFIG_OPTION_VALIDATION_MAP), default={}, log=self.logger)
    except Exception, err:
        self.logger.error(CacheDataStorage.MSG_ERROR_GET_CONFIG_OPTIONS, str(err))
        self.logger.info(Utils.getTracebackInfo())


  # # Check is valid social data
  #
  # @param socialData - socialData dictionary
  # @return True if valid or False otherwise
  def isValid(self, socialData):
    # variable for result
    ret = True
    
    if isinstance(self.configOptions.validationMap, dict) and len(self.configOptions.validationMap) > 0:
      for key, value in self.configOptions.validationMap.items():
        for fieldName in value:
          if not isinstance(socialData, dict) or fieldName not in socialData or (socialData[fieldName] is None or socialData[fieldName] == ""):
            ret = False
            break

    return ret


  # # update dictionary
  #
  # @param lhs - social data dict
  # @param rhs - social data dict
  # @return merged dict
  def updateDict(self, lhs, rhs):
    # variable for result
    ret = {}

    if isinstance(lhs, dict) and isinstance(rhs, dict):
      for key, value in rhs.items():
        if key in lhs.keys():
          if (lhs[key] is None or lhs[key] == "") and rhs[key] is not None and rhs[key] != "":
            ret[key] = rhs[key]
          elif (rhs[key] is None or rhs[key] == "") and lhs[key] is not None or lhs[key] != "":
            ret[key] = lhs[key]
          else:
            ret.update({key:value})
        else:
          ret.update({key:value})

    return ret


  # # Merge social data
  #
  # @param lhs - social data dict
  # @param rhs - social data dict
  # @return merged social data dict
  def mergeSocialData(self, lhs, rhs):
    # variable for result
    ret = {}
    
    if not isinstance(lhs, dict) and isinstance(rhs, dict):
      ret = rhs

    elif isinstance(lhs, dict) and not isinstance(rhs, dict):
      ret = lhs

    elif isinstance(lhs, dict) and isinstance(rhs, dict):
      ret.update(self.updateDict(lhs, rhs))
      ret.update(self.updateDict(rhs, lhs))

    return ret


  # # Save social data to DB (cache social data table)
  #
  # @param itemsDataDict - items data dict with processed data
  # @return - None
  def saveSocialDataToDB(self, itemsDataDict):
    if isinstance(itemsDataDict, CacheDataStorage.ItemsDataDict):
      for key, value in itemsDataDict.items():
        # kwarg = {self.configOptions.uniqueKeyName:key}
        socialData = itemsDataDict.getCachedData(**{self.configOptions.uniqueKeyName:key})
        self.logger.debug("socialData: %s", str(socialData))

        if socialData is not None:
          if self.isValid(socialData):
            self.setCachedDataToDB(**value)
          else:
            self.logger.debug("Not valid social data!")
            cachedData = self.getCachedlDataFromDB(**{self.configOptions.uniqueKeyName:key})
            self.logger.debug("cachedData: %s" , str(cachedData))

            if cachedData is None:
              self.logger.debug("Cached data not found. Save to DB partially filled data.")
              self.setCachedDataToDB(**value)
            else:
              mergedData = self.mergeSocialData(lhs=cachedData, rhs=socialData)
              self.logger.debug("mergedData: %s" , json.dumps(mergedData, encoding='utf-8'))
              self.setCachedDataToDB(**{self.configOptions.uniqueKeyName:key, self.configOptions.cachedFieldName:mergedData})
