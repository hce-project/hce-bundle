# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
AuthorType Class content main functional extract of author data.

@package: dc_crawler
@file UrlLimits.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import copy
import json
import requests
import dc_crawler.Constants as CONTANTS
import dc.EventObjects as dc_event


class UrlLimits(object):
  # # Constans used in class
  OPTION_ROOT_URL_MASK = "root_url_mask"
  OPTION_CONTENT_TYPE_MASK = "content_type_mask"
  OPTION_MAX_ITEMS = "max_items"
  OPTION_OFFSET = "offset"

  HEADER_CONTENT_TYPE_NAME = "content-type"

  # # Initialization
  def __init__(self):
    pass
  
  
  ## apply aone limits filter
  #
  # @param propertyElement - property of limits for one element
  # @param urlsList - list of urls
  # @param log - logger instance
  # @return truncated list of urls if necessary
  @staticmethod
  def applyOneLimitsFilter(propertyElement, urlsList, log=None):
    # variable for result
    ret = copy.copy(urlsList)
    
    if isinstance(propertyElement, dict) and isinstance(urlsList, list):

      if UrlLimits.OPTION_ROOT_URL_MASK in propertyElement or UrlLimits.OPTION_CONTENT_TYPE_MASK in propertyElement:
        for urlObj in urlsList:
          url = urlObj.url if isinstance(urlObj, dc_event.URL) else urlObj

          try:
            res = requests.head(url, allow_redirects=True)
            # check http code
            if res.status_code == CONTANTS.HTTP_CODE_200:
              rootUrlMaskPassed = True
              if UrlLimits.OPTION_ROOT_URL_MASK in propertyElement and isinstance(propertyElement[UrlLimits.OPTION_ROOT_URL_MASK], list):
                rootUrlMaskPassed = False
                for rootUrlMask in propertyElement[UrlLimits.OPTION_ROOT_URL_MASK]:
                  if log is not None:
                    log.debug("Pattern '%s' searching in '%s'.", str(rootUrlMask), str(res.url))
                  if re.search(pattern=rootUrlMask, string=res.url, flags=re.U + re.I):
                    if log is not None:
                      log.debug("Pattern '%s' matched for '%s'.", str(rootUrlMask), str(res.url))
                    rootUrlMaskPassed = True
                    break

              if not rootUrlMaskPassed:
                ret.remove(url)
                continue
                
              contentTypeMaskPassed = True
              if UrlLimits.OPTION_CONTENT_TYPE_MASK in propertyElement and isinstance(propertyElement[UrlLimits.OPTION_CONTENT_TYPE_MASK], list):
                contentTypeMaskPassed = False
                for contentTypeMask in propertyElement[UrlLimits.OPTION_CONTENT_TYPE_MASK]:
                  if UrlLimits.HEADER_CONTENT_TYPE_NAME in res.headers:
                    contentType = res.headers[UrlLimits.HEADER_CONTENT_TYPE_NAME].split(';')[0]
                    if re.search(pattern=contentTypeMask, string=contentType, flags=re.U + re.I):
                      if log is not None:
                        log.debug("Pattern '%s' matched for '%s'.", str(contentTypeMask), str(contentType))
                      contentTypeMaskPassed = True
                      break
                
              if not contentTypeMaskPassed:
                ret.remove(url)

            else:
              if log is not None:
                log.debug("Resolving url return status code = %s", str(res.status_code))
              ret.remove(url)

          except Exception, err:
            if log is not None:
              log.error("Resolving url failed. Error: %s", str(err))
      
      if UrlLimits.OPTION_OFFSET in propertyElement and propertyElement[UrlLimits.OPTION_OFFSET] is not None:
        offset = int(propertyElement[UrlLimits.OPTION_OFFSET])
        if log is not None:
          log.debug("Apply offset = %s", str(offset))
        if offset > 0 and offset < len(ret):
          ret = ret[offset:]

      if UrlLimits.OPTION_MAX_ITEMS in propertyElement and propertyElement[UrlLimits.OPTION_MAX_ITEMS] is not None:
        maxItems = int(propertyElement[UrlLimits.OPTION_MAX_ITEMS])
        if log is not None:
          log.debug("Apply maxItems = %s", str(maxItems))
        if maxItems > 0 and maxItems < len(ret):
          ret = ret[:maxItems]
    
    return ret


  ## load properties
  #
  # @param properties - properties string
  # @param log - logger instance
  # @return properties object
  @staticmethod
  def loadProperties(properties, log=None):
    # variable for result
    ret = properties
    try:
      if isinstance(properties, basestring):
        ret = json.loads(properties, encoding='utf-8')
    except Exception, err:
      if log is not None:
        log.error("Load properties failed. Error: %s", str(err))
    
    return ret
    

  # # Apply limits
  #
  # @param properties - properties of limits
  # @param urlsList - list of urls
  # @param log - logger instance
  # @return truncated list of urls if necessary
  @staticmethod
  def applyLimits(properties, urlsList, log=None):
    # variable for result
    ret = urlsList

    if log is not None:
      log.debug("properties: %s, type: %s", str(properties), str(type(properties)))

    propObj = UrlLimits.loadProperties(properties, log)

    if isinstance(propObj, list):
      for propertyElement in propObj:
        ret = UrlLimits.applyOneLimitsFilter(propertyElement, ret, log)
    elif isinstance(propObj, dict):
      ret = UrlLimits.applyOneLimitsFilter(propObj, ret, log)

    return ret
