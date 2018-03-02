"""@package docstring
  @file boilerpipe_extractor.py
  @author Alexey <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2013 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
  """

from dc_processor.base_extractor import BaseExtractor
import dc_processor.Constants as CONSTS
from boilerpipe.extract import Extractor  # pylint: disable=F0401
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


class BoilerpipeExtractor(BaseExtractor):


  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    BaseExtractor.__init__(self, config, templ, domain, processorProperties)
    self.name = CONSTS.EXTRACTOR_NAME_BOILERPIPE
    self.data["extractor"] = CONSTS.EXTRACTOR_NAME_BOILERPIPE
    logger.debug("Properties: %s", varDump(self.properties))

    self.rankReading(self.__class__.__name__)


  def extractTags(self, resource, reslt):
    try:
      extractor = Extractor(extractor='ArticleExtractor', html=resource.raw_html)
      text = extractor.getText()
      logger.info("Article's corpus: %s", text)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_CONTENT_UTF8_ENCODED, tag_value=text)
    except Exception, err:
      ExceptionLog.handler(logger, err, 'extractTags:', (err), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    return reslt
