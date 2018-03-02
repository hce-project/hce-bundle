# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
UrlNormalize Class content main functional of support the URL_NORMALIZE properties.

@package: app
@file UrlNormalize.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re

import app.Consts as APP_CONSTS
import app.Utils as Utils


class UrlNormalize(object):

  # Constants used in class
  PROPERTY_OPTIONS_MASK = 'mask'
  PROPERTY_OPTIONS_REPLACE = 'replace'

  # Constants of error messages
  ERROR_MSG_FAILED_REPLACE = "Operation replace failed. Error: %s"

  # Initialization
  def __init__(self):
    pass


  ## get normalize mask
  #
  # @param siteProperties - site properties 
  # @param defaultValue - default value
  # @return normalize mask
  @staticmethod
  def getNormalizeMask(siteProperties, defaultValue=Utils.UrlNormalizator.NORM_DEFAULT):
    # variable for result
    ret = defaultValue
    
    if siteProperties is not None and isinstance(siteProperties, dict) and APP_CONSTS.URL_NORMALIZE in siteProperties and \
      isinstance(siteProperties[APP_CONSTS.URL_NORMALIZE], dict) and UrlNormalize.PROPERTY_OPTIONS_MASK in siteProperties[APP_CONSTS.URL_NORMALIZE]:
      ret = int(siteProperties[APP_CONSTS.URL_NORMALIZE][UrlNormalize.PROPERTY_OPTIONS_MASK])
    
    return ret
    

  # # execute normalization url string use base url
  #
  # @param siteProperties - site properties 
  # @param base - base url string
  # @param url - url string
  # @param supportProtocols - support protocol list
  # @param log - logger instance
  # @return already normalized url string or None - in case of bad result normalization
  @staticmethod
  def execute(siteProperties, base, url, supportProtocols=None, log=None):

    # check site property for exist replace rule
    if siteProperties is not None and isinstance(siteProperties, dict) and APP_CONSTS.URL_NORMALIZE in siteProperties:
      if log is not None:
        log.info("!!! siteProperties['%s']: '%s', type: %s", str(APP_CONSTS.URL_NORMALIZE), str(siteProperties[APP_CONSTS.URL_NORMALIZE]), 
                 str(type(siteProperties[APP_CONSTS.URL_NORMALIZE])))
      
      replaceList = []
      propertyDict = {}
      if isinstance(siteProperties[APP_CONSTS.URL_NORMALIZE], basestring):
        propertyDict = Utils.jsonLoadsSafe(jsonString=siteProperties[APP_CONSTS.URL_NORMALIZE], default=propertyDict, log=log)
      
      if isinstance(propertyDict, dict) and UrlNormalize.PROPERTY_OPTIONS_REPLACE in propertyDict:
        replaceList = propertyDict[UrlNormalize.PROPERTY_OPTIONS_REPLACE]

      if log is not None:
        log.debug("!!! replaceList: %s", str(replaceList))

      if isinstance(replaceList, list):
        for replaceElem in replaceList:
          if isinstance(replaceElem, dict):
            for pattern, repl in replaceElem.items():
              try:
                if log is not None:
                  log.debug("!!! pattern: %s, url: %s", str(pattern), str(url))
                url = re.sub(pattern=pattern, repl=repl, string=url, flags=re.U + re.I)
                if log is not None:
                  log.debug("!!! res url: %s", str(url))
              except Exception, err:
                if log is not None:
                  log.error(UrlNormalize.ERROR_MSG_FAILED_REPLACE, str(err))
    
    return Utils.urlNormalization(base=base, url=url, supportProtocols=supportProtocols, log=log)
