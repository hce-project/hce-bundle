"""@package docstring
 @file newspaper_extractor.py
 @author Alexey <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""

import signal
import dc_processor.Constants as CONSTS
from dc_processor.base_extractor import BaseExtractor
from dc_processor.base_extractor import signal_handler
# from dc_processor.scraper_result import Result
from dc_processor.NewspaperWrapper import NewspaperWrapper
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


class NewspaperExtractor(BaseExtractor):


  # local class constants general purpose
  EXTRACTOR_NAME = "Newspaper extractor"
  SECTION_NAME = "extractor"


  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    BaseExtractor.__init__(self, config, templ, domain, processorProperties)

    # self.processorProperties = processorProperties
    logger.debug("Properties: %s", varDump(self.properties))

    # set module rank from module's properties
    self.rankReading(self.__class__.__name__)

    self.name = "Newspaper extractor"
    self.data["extractor"] = "Newspaper extractor"
    self.userAgent = processorProperties["EXTRACTOR_USER_AGENT"] if "EXTRACTOR_USER_AGENT" in\
     processorProperties else None


  def imagesProcessing(self, article):
    ret = None
    if article.top_img is not None:
      ret = []
      ret.append(article.top_img)
      ret.extend([x for x in article.imgs if x != article.top_img])
    else:
      ret = article.imgs

    if ret is not None:
      ret = self.tagValueValidate(CONSTS.TAG_MEDIA, ret)
      if ret is not None:
        localValue = self.imgDelimiter.join(ret)
        ret = []
        ret.append(localValue)

    return ret


  def extractTags(self, resource, reslt):
    # support time execution limit
    signal.signal(signal.SIGALRM, signal_handler)
    if 'EXTRACTOR_NEWSPAPER_MAX_EXECUTION' in self.processorProperties:
      t = int(self.processorProperties['EXTRACTOR_NEWSPAPER_MAX_EXECUTION'])
    else:
      t = CONSTS.TIME_EXECUTION_LIMIT
    signal.alarm(t)
    logger.debug("Max execution time signal handler set timeout as: %s", str(t))

    isLoadUrlsParam = False
    imageRation = None
    if self.processorProperties is not None and "SCRAPER_DOWNLOAD_IMAGES" in self.processorProperties:
      isLoadUrlsParam = bool(int(self.processorProperties["SCRAPER_DOWNLOAD_IMAGES"]))
    if self.processorProperties is not None and "IMAGE_RATION" in self.processorProperties:
      imageRation = float(self.processorProperties["IMAGE_RATION"])

    kArgs = {}
    if imageRation is not None:
      kArgs = {"title": u'', "source_url": u'', "config": None, "image_dimension_ration": imageRation}
    if self.userAgent is not None:
      kArgs["browser_user_agent"] = self.userAgent
      logger.debug(">>> NewspaperExtractor sets userAgent, is = " + str(self.userAgent))


    kArgs["isLoadUrls"] = isLoadUrlsParam
    if CONSTS.TAG_MEDIA in reslt.tags.keys() and not self.isTagNotFilled(reslt, CONSTS.TAG_MEDIA):
      logger.debug("!!! Tag 'media' already selected. Skipped")
      kArgs["isLoadUrls"] = False

    article = NewspaperWrapper(" ", **kArgs)

    article.html = resource.raw_html
    article.is_downloaded = True

    try:
      article.parse()
      self.addTag(result=reslt, tag_name=CONSTS.TAG_TITLE, tag_value=article.title)
      # self.addTag(result=reslt, tag_name=CONSTS.TAG_LINK, tag_value=article.canonical_link)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_LINK, tag_value=resource.url)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_DESCRIPTION, tag_value=article.summary)
      if hasattr(article, "published_date"):
        self.addTag(result=reslt, tag_name=CONSTS.TAG_PUB_DATE, tag_value=str(article.published_date))  # pylint: disable=E1101
      elif hasattr(article, "publish_date"):
        self.addTag(result=reslt, tag_name=CONSTS.TAG_PUB_DATE, tag_value=str(article.publish_date))
      self.addTag(result=reslt, tag_name=CONSTS.TAG_AUTHOR, tag_value=article.authors)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_DC_DATE, tag_value=article.additional_data)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_CONTENT_UTF8_ENCODED, tag_value=article.text)
      self.addTag(result=reslt, tag_name=CONSTS.TAG_KEYWORDS, tag_value=article.meta_keywords)
      imgList = self.imagesProcessing(article)
      logger.debug("!!! Tag 'media' imgList: %s", str(imgList))
      if imgList is not None:
        self.addTag(result=reslt, tag_name=CONSTS.TAG_MEDIA, tag_value=imgList)

    except Exception as err:
      ExceptionLog.handler(logger, err, 'Newspaper parse error:', (), \
                           {ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_DEBUG})
    return reslt
