"""@package docstring
 @file goose_extractor.py
 @author Alexey <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""

import signal
from goose import Goose
from dc_processor.base_extractor import BaseExtractor
from dc_processor.base_extractor import signal_handler
# from dc_processor.scraper_result import Result
import dc_processor.Constants as CONSTS
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


class GooseExtractor(BaseExtractor):
  goose = None

  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    try:
      BaseExtractor.__init__(self, config, templ, domain, processorProperties)
      logger.debug("Properties: %s", varDump(self.properties))
      self.name = "Goose extractor"
      # set module rank from module's properties
      self.rankReading(self.__class__.__name__)
      if "EXTRACTOR_USER_AGENT" in processorProperties and processorProperties["EXTRACTOR_USER_AGENT"] is not None:
        self.goose = Goose({'browser_user_agent': processorProperties["EXTRACTOR_USER_AGENT"]})
        logger.debug(">>>  NewspaperExtractor sets userAgent, is" + str(processorProperties["EXTRACTOR_USER_AGENT"]))
      else:
        self.goose = Goose()
      self.data["extractor"] = "Goose extractor"
    except Exception as err:
      ExceptionLog.handler(logger, err, "Goose extractor constructor error: possible /tmp not permitted to write", (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      raise


  def extractTags(self, resource, reslt):
    # support time execution limit
    signal.signal(signal.SIGALRM, signal_handler)
    if 'EXTRACTOR_GOOSE_MAX_EXECUTION' in self.processorProperties:
      t = int(self.processorProperties['EXTRACTOR_GOOSE_MAX_EXECUTION'])
    else:
      t = CONSTS.TIME_EXECUTION_LIMIT
    signal.alarm(t)
    logger.debug("Max execution time signal handler set timeout as: %s", str(t))

    try:
      article = self.goose.extract(raw_html=str(resource.raw_html), url=resource.url)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_TITLE, tag_value=article.title)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_LINK, tag_value=article.canonical_link)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_PUB_DATE, tag_value=article.publish_date)
      # self.addTag(result=reslt, tag_name=CONSTS.TAG_GUID, tag_value=article.link_hash)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_DC_DATE, tag_value=article.additional_data)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_CONTENT_UTF8_ENCODED, tag_value=article.cleaned_text)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_KEYWORDS, tag_value=article.meta_keywords)

      if CONSTS.TAG_MEDIA in reslt.tags.keys() and not self.isTagNotFilled(reslt, CONSTS.TAG_MEDIA):
        logger.debug("!!! Tag 'media' already selected. Skipped... value = %s", str(reslt.tags[CONSTS.TAG_MEDIA]))
      else:
        self.addTag(result=reslt, tag_name=CONSTS.TAG_MEDIA, tag_value=getattr(article, "top_image.src", None))

    except IOError as err:
      # ExceptionLog.handler(logger, err, "Goose open file error. It may be unsupported encoding like jp", (), \
      #                      {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      logger.debug("Goose open file error. It may be unsupported encoding like jp. Error: " + str(err))
    except Exception as err:
      # ExceptionLog.handler(logger, err, "Goose parse error", (), \
      #                      {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
      logger.debug("Goose parse error. Error: " + str(err))

    return reslt
