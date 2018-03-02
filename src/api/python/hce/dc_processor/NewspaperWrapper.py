"""@package docstring
 @file NewspaperWrapper.py
 @author Scorp <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""

import inspect
from newspaper import Article
from newspaper import images
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


# # Class NewspaperWrapper is owner wrapper for Articla class - main class of newspaper library
#
class NewspaperWrapper(Article):


  # #Class Constructor
  #
  # @param url - resource's url
  # @param title - param that internally used in newspaper library
  # @param source_url - param that internally used in newspaper library
  # @param config - param that internally used in newspaper library
  # @param isLoadUrls - bool value, that indicates - load resources images or not
  # @param kwargs - params that internally used in newspaper library
  def __init__(self, url, title=u'', source_url=u'', config=None, isLoadUrls=True, **kwargs):
    super(NewspaperWrapper, self).__init__(url, title, source_url, config, **kwargs)
    self.isLoadUrls = isLoadUrls


  # # sort_images method, sorts resources images
  #
  # @param imgs - incoming list of resources images
  # @return just sorted resources images
  def sort_images(self, imgs):
    img_dimensions = []
    for image in imgs:
      try:
        img_dimension = images.fetch_image_dimension(image, self.config.browser_user_agent)
      except Exception, err:
        logger.error("fetch_image_dimension: %s", str(err))
        img_dimension = None

      if img_dimension is None:
        img_dimensions.append({"dim": None, "img_url": image})
      else:
        img_dimensions.append({"dim": img_dimension[0] * img_dimension[1], "img_url": image})
    ret = [img["img_url"] for img in sorted(img_dimensions, key=lambda img: img["dim"], reverse=True)]
    return ret


  # # versionnedWrapper wrap method, that allows call of class methods with various params list in various
  # library versions
  #
  # @param methodName - name of wrapped method
  # @return wrapped method return value
  def versionnedWrapper(self, methodName):
    argsResult = inspect.getargspec(getattr(self.extractor, methodName))
    if argsResult is not None and argsResult.args is not None and \
    len(argsResult.args) - (0 if argsResult.defaults is None else len(argsResult.defaults)) == 2 and \
    "article" in argsResult.args:
      ret = getattr(self.extractor, methodName)(self)  # pylint: disable=E1101
    else:
      ret = getattr(self.extractor, methodName)(self.url, self.clean_doc)  # pylint: disable=E1101
    return ret


  # # fetch_images overloaded version on Article.fetch_images method
  def fetch_images(self):
    if self.clean_doc is not None:  # pylint: disable=E1101
      meta_img_url = self.versionnedWrapper("get_meta_img_url")
      self.set_meta_img(meta_img_url)  # pylint: disable=E1101

    if self.clean_top_node is not None and not self.has_top_image():  # pylint: disable=E1101
      first_img = self.versionnedWrapper("get_first_img_url")
      self.set_top_img(first_img)

    if not self.has_top_image() and self.isLoadUrls:  # pylint: disable=E1101
      self.set_reddit_top_img()
    else:
      logger.debug(">>> not load urls")

    if self.isLoadUrls and self.clean_doc is not None:
      imgs = self.versionnedWrapper("get_img_urls")
      imgs = self.sort_images(imgs)
      self.set_imgs(imgs)


  # # fetch_images overloaded version on Article.set_top_img method
  #
  # @param src_url - url of source image
  def set_top_img(self, src_url):
    if self.isLoadUrls:
      super(NewspaperWrapper, self).set_top_img(src_url)
    else:
      logger.debug(">>> not load urls")
