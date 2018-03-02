# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
Collect urls limits main functional.

@package: dc_crawler
@file CollectUrlsLimits.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re


# Collect urls limits class
class CollectUrlsLimits(object):
  # # Constants used in class
  MAX_URLS_FROM_PAGE="MaxURLSFromPage"
  OPTION_RULE_PAIR_LEN =   2

  # # Constants of error messages used in class
  EXCUTION_ERROR = "Execution error: %s"
  WRONG_PROPERTY_FORMAT = "Wrong property format: %s"
  WRONG_RULES_FORMAT = "Wrong rules format: %s"

  # # Initialization
  def __init__(self):
    pass


  ## execute apply limits
  #
  # @param properties - property from siteProperty
  # @param url - url string
  # @param optionsName - option name
  # @param default - default value
  # @param log - logger instance
  # @return max urls from page value after apply limits
  @staticmethod
  def execute(properties, url, optionsName, default, log=None):
    # variable for result
    ret = default
    try:
      if not isinstance(properties, dict):
        raise Exception(CollectUrlsLimits.WRONG_PROPERTY_FORMAT % str(properties))

      for pattern, rules in properties.items():
        if re.search(pattern=pattern, string=url, flags=re.U + re.I) is not None:
          if log is not None:
            log.debug("Pattern '%s' passed for url: %s", str(pattern), str(url))

          if not isinstance(rules, list):
            raise Exception(CollectUrlsLimits.WRONG_RULES_FORMAT % str(rules))

          for rule in rules:
            if isinstance(rule, list) and len(rule) == CollectUrlsLimits.OPTION_RULE_PAIR_LEN:
              if re.search(pattern=rule[0], string=optionsName, flags=re.U+re.I) is not None:
                if log is not None:
                  log.debug("Pattern '%s' passed for option name: %s", str(rule[0]), str(optionsName))

                ret = type(default)(rule[1])

    except Exception, err:
      if log is not None:
        log.error(CollectUrlsLimits.EXCUTION_ERROR, str(err))

    return ret
