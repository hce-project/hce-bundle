"""@package docstring
  @file ml_extractor.py
  @author Alexey <developers.hce@gmail.com>
  @link http://hierarchical-cluster-engine.com/
  @copyright Copyright &copy; 2013 IOIX Ukraine
  @license http://hierarchical-cluster-engine.com/license/
  @package HCE project node API
  @since 0.1
  """

import re
from io import BytesIO
from lxml import etree
from dc_processor.base_extractor import BaseExtractor
import dc_processor.Constants as CONSTS
from app.Utils import varDump
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()


class MLExtractor(BaseExtractor):


  def __init__(self, config, templ=None, domain=None, processorProperties=None):
    BaseExtractor.__init__(self, config, templ, domain, processorProperties)
    self.name = CONSTS.EXTRACTOR_NAME_ML
    self.data["extractor"] = CONSTS.EXTRACTOR_NAME_ML
    """
    #stub
    #set properties manually
    #later it will be filled from db
    #prepate algorithm dict
    properties_dict = json.loads(CONSTS.ML_EXTRACTOR_PROPERTIES_JSON)
    logger.debug("properties_dict: %s" % varDump(properties_dict))
    self.properties = properties_dict[CONSTS.PROPERTIES_KEY]
    """
    logger.debug("Properties: %s", varDump(self.properties))

    # set module rank from module's properties
    self.rankReading(self.__class__.__name__)


  def processAttributes(self, elem):
    candidates = []
    attr = elem.items()
    A = elem.getchildren()
    for a in A:
      childs = a.iter(tag="div")
      for child in childs:
        attr = child.items()
        for items in attr:
          words = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', items[1]).lower()
          words = re.sub("_", " ", words)
          words = re.sub("-", " ", words)
          for word in words.split():
            candidates.append(word)
            if "article" in candidates or "content" in candidates:
              return False
    candidates = []
    attr = elem.items()
    for items in attr:
      if items[0] != "style":
        words = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', items[1]).lower()
        words = re.sub("_", " ", words)
        words = re.sub("-", " ", words)
        for word in words.split():
          candidates.append(word)
    return True if "article" in candidates or "content" in candidates or "text" in candidates else False


  def extractTags(self, resource, reslt):
    try:
      xml = resource.raw_html
      context = etree.iterparse(BytesIO(xml.encode("utf-8")), html=True, events=("start", "end"))  # pylint: disable=E1101
      X = {"data":[]}
      try:
        for action, elem in context:
          if (elem.tag == "div" or elem.tag == "article") and action == "start":
            child_tags = [child.tag for child in elem.getchildren()]  # pylint: disable=W0613,W0612
            if elem.tag == "article" or self.processAttributes(elem):
              attr = elem.items()
              full_text = ""
              T = elem.iter()
              for t in T:
                if t.tag == "script":
                  t.clear()
              for text in elem.itertext():
                text = text.strip("\r\n\t ")
                full_text = full_text + text if len(text) > 0 else full_text
              X["data"].append({"value":full_text, "attr":attr})
      except Exception, err:
        logger.debug("Empty DOM. %s", str(err.message))
      if len(X["data"]) > 0:
        I = 0
        L = []
        for x in X["data"]:
          l = 0
          for xx in x["value"]:
            l = l + len(xx)
          L.append(l)
        m = max(L)
        I = [i for i, j in enumerate(L) if j == m]
        self.addTag(result=reslt, tag_name=CONSTS.TAG_CONTENT_UTF8_ENCODED, tag_value=X["data"][I[0]]["value"])
      else:
        logger.debug("Nothing to extarct")
    except Exception as err:
      ExceptionLog.handler(logger, err, 'Parse error:', (err))
    return reslt


  def getXPathFromContent(self, content):  # pylint: disable=W0613
    xpath = None
    # xpath = //*[contains(., content)]
    return xpath
