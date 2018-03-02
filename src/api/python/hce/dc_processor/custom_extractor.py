# coding: utf-8
'''
Created on Mar 02, 2016

@package: dc_processor
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import signal
import types
import dc_processor.Constants as CONSTS
from dc_processor.base_extractor import BaseExtractor
from dc_processor.base_extractor import signal_handler
from app.Utils import ExceptionLog
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


# CustomExtractor exctractor class, extracts data from custom structure
class CustomExtractor(BaseExtractor):


  # #constructor
  # initialize default fields
  # @param config - Scraper's config
  # @param templ - default template
  # @param domain - processing url's domain
  # @param processorProperties - Scraper's processorProperties
  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    try:
      BaseExtractor.__init__(self, config, templ, domain, processorProperties)
      logger.debug("Properties: %s", varDump(self.properties))
      self.name = "Custom extractor"
      # set module rank from module's properties
      self.rankReading(self.__class__.__name__)
      self.data["extractor"] = self.name
    except Exception as err:
      ExceptionLog.handler(logger, err, "Custom extractor constructor error: possible /tmp not permitted to write", (),
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      raise


  # #extractTags method, common data extraction method
  # @param resource - incoming resource element
  # @param reslut - incoming reslut element, which filled inside method
  # @return reslut element
  def extractTags(self, resource, reslut):
    # support time execution limit
    signal.signal(signal.SIGALRM, signal_handler)
    if 'EXTRACTOR_CUSTOM_MAX_EXECUTION' in self.processorProperties:
      t = int(self.processorProperties['EXTRACTOR_CUSTOM_MAX_EXECUTION'])
    else:
      t = CONSTS.TIME_EXECUTION_LIMIT
    signal.alarm(t)
    logger.debug("Max execution time signal handler set timeout as: %s", str(t))

    try:
      if resource.raw_html is not None and isinstance(resource.raw_html, types.DictType):
        for key in resource.raw_html:
          localTagValue = resource.raw_html[key] if isinstance(resource.raw_html[key], types.ListType) else \
                          [str(resource.raw_html[key])]
          self.addTag(result=reslut, tag_name=key, tag_value=localTagValue)
    except IOError as err:
      ExceptionLog.handler(logger, err, "Custom extractor file error. It may be unsupported encoding like jp", (), \
                            {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    except Exception as err:
      ExceptionLog.handler(logger, err, "Custom extractor error", (), \
                            {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    return reslut
