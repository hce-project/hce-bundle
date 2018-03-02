# coding: utf-8

"""
HCE project,  Python bindings, Distributed Tasks Manager application.
DateTimeType Class content main functional extract of datetime.

@package: dc_crawler
@file FetcherType.py
@author Aleksandr Skuridin <skuridin.alexander+hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import re
import json
from dc_crawler.Fetcher import BaseFetcher

class FetcherType(object):

  ## Check the fetcher type by FETCHER_TYPE project property
  #
  #@param urlObj - url request object
  #@param propertyValue - json string with pattern rules
  #@param siteUrl - site URL string with pattern rules. Only for debug purpose
  #@param logger - instance of logger for log if necessary
  #@param isExtendLog - boolean flag for allowed extend logging if True or only error message otherwise
  #@return extracted fetcher type
  @staticmethod
  def getFromProperty(propertyValue, siteUrl, logger=None):
    #isExtendLog = False
    if logger is not None:
      logger.debug(siteUrl + ', FETCHER_TYPE: ' + propertyValue)

    fetchType = None
    try:
      fetcherProperties = json.loads(propertyValue)
      for pattern in fetcherProperties:
        match = re.search(pattern, siteUrl)
        if match:
          fetchType = fetcherProperties[pattern]
          # if fetchType in BaseFetcher.fetchers:
          if fetchType == BaseFetcher.TYP_DYNAMIC or fetchType == BaseFetcher.TYP_NORMAL:
            if logger is not None:
              logger.info(siteUrl + ', Fetch Type value: ' + str(fetchType))
          else:
            logger.debug(siteUrl + ', wrong Fetch Type number: ' + str(fetchType))
            fetchType = None
            continue
          break
    except Exception, ex:
      if logger is not None:
        logger.debug("Fetcher Type Exception: " + str(ex))
    return fetchType
