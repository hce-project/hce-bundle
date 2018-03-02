#!/usr/bin/python
# coding: utf-8

import sys
import logging
import MySQLdb as mdb
import MySQLdb.cursors
import ConfigParser

import app.Consts as APP_CONSTS
from app.Utils import varDump
from app.CacheDataStorage import CacheDataStorage
 

def getLogger():
  # create logger
  logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  logger.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(ch)

  return logger


def getConfigParser():

  config = ConfigParser.RawConfigParser()
  CONFIG_SECTION = "CacheDataStorage"

  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_UNIQUE_KEY_NAME, 'urlmd5')
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHED_FIELD_NAME, 'socialData')
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_SELECT_QUERY, "SELECT * FROM `social_data_cache` WHERE `URLMd5`='%URLMD5%' AND `CDate` BETWEEN DATE_SUB(NOW(), INTERVAL 1440 MINUTE) AND NOW()")
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_INSERT_QUERY, "INSERT INTO `social_data_cache`(`URLMd5`, `URL`, `SocialData`) VALUES ('%URLMD5%', '%URL%', '%SOCIAL_DATA%') ON DUPLICATE KEY UPDATE `SocialData`='%SOCIAL_DATA%'")
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_DELETE_QUERY, "DELETE FROM `social_data_cache` WHERE `CDate` < DATE_SUB(NOW(), INTERVAL 1440 MINUTE)")
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME, 'social_data_cache')
  config.set(CONFIG_SECTION, CacheDataStorage.ConfigOptions.CONFIG_OPTION_MACRO_NAMES_MAP, '{"socialData":["social_data", "social__data"]}')

  config.add_section(CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME)
  config.set(CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_HOST, '127.0.0.1')
  config.set(CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_PORT, '3306')
  config.set(CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_USER, 'hce')
  config.set(CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_PWD, 'hce12345')
  config.set(CacheDataStorage.ConfigOptions.CONFIG_OPTION_CACHE_DB_NAME, CacheDataStorage.DBConnectionOptions.CONFIG_OPTION_DB_CHARSET, 'utf8')

  return config


if __name__ == '__main__':

  logger = getLogger()
  config = getConfigParser()

  cacheDataStorage = CacheDataStorage(config, logger)

  cachedData = cacheDataStorage.getCachedlDataFromDB(urlmd5='123')
  logger.info("cachedData: %s, type: %s", str(cachedData), str(type(cachedData)))

  cacheDataStorage.setCachedDataToDB(urlmd5='123', socialData={'social':[1, 2, 3]})

  itemsDataDict = CacheDataStorage.ItemsDataDict(cacheDataStorage.configOptions.uniqueKeyName, cacheDataStorage.configOptions.cachedFieldName)
  itemsDataDict.add(urlmd5='123', socialData={'social':[1, 2, 5]})
  cacheDataStorage.saveCachedDataToDB(itemsDataDict)

  cacheDataStorage.removeObsoleteCachedData()

  logger.info("getCachedData: %s", str(itemsDataDict.getCachedData(urlmd5='123')))
  itemsDataDict.setCachedData(urlmd5='123', socialData={'social':[1, 2, 3]})
  logger.info("getCachedData: %s", str(itemsDataDict.getCachedData(urlmd5='123')))

  itemsDataDict2 = CacheDataStorage.ItemsDataDict(cacheDataStorage.configOptions.uniqueKeyName, cacheDataStorage.configOptions.cachedFieldName)
  itemsDataDict2.add(urlmd5='1234', socialData={'social':[1, 2, 4]})
  itemsDataDict.addCachedData(itemsDataDict2)
  logger.info("getCachedData: %s", str(itemsDataDict.getCachedData(urlmd5='1234')))

