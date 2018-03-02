"""@package docstring
  @file alchemy_extractor.py
  @author Alexey <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2013 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
  """

from dc_processor.base_extractor import BaseExtractor
import dc_processor.Constants as CONSTS
from dc_processor.alchemyapi import AlchemyAPI
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


class AlchemyExtractor(BaseExtractor):


  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    BaseExtractor.__init__(self, config, templ, domain, processorProperties)
    self.name = CONSTS.EXTRACTOR_NAME_ALCHEMY
    self.data["extractor"] = CONSTS.EXTRACTOR_NAME_ALCHEMY
    logger.debug("Properties: %s", varDump(self.properties))

    # set module rank from module's properties
    self.rankReading(self.__class__.__name__)


  def extractTags(self, resource, reslt):
    try:
      logger.info("AAAAAAA")
      parser = AlchemyAPI()
      logger.info("BBBBBBB")
      text = parser.text("html", resource.raw_html)
      logger.info("CCCCCCC")
      logger.info("Article's corpus: %s", text)
      self.addTag(result=reslt, \
                    tag_name=CONSTS.TAG_CONTENT_UTF8_ENCODED, \
                    tag_value=text)
      logger.info("DDDDDDD")
    except Exception, err:
      logger.info(varDump(err))
    return reslt


