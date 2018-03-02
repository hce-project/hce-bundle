'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import base64
import json
import copy
import types
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# class ProcessedContentInternalStruct contents static methods for processing internal structure of processedContent
class ProcessedContentInternalStruct(object):

  DATA_FIELD = "data"
  CDATE_FIELD = "CDate"


  # # parseProcessedBuf fills processed content list, depend of contentMask value,
  #
  # @param cDateValue - incoming CDate value
  # @param contentMask - incoming contentMask
  # @param processedContent - incoming processedContent as dict value
  # @return list of Content or tuple(Content, Content) objects
  @staticmethod
  def processDictProcessedContent(cDateValue, contentMask, processedContent):
    ret = []

    logger.debug("contentMask: %s, len(processedContent): %s", str(contentMask), str(len(processedContent)))
    if contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED:
      if len(processedContent["custom"]) > 0:
        logger.debug("return item processedContent['custom'][0]")
        resultElem = base64.b64encode(processedContent["custom"][0])
      else:
        logger.debug("return deep copy of processedContent, `internal` and `custom` removed")
        localProcessedContent = copy.deepcopy(processedContent)
        del localProcessedContent["internal"]
        del localProcessedContent["custom"]
        resultElem = json.dumps(localProcessedContent, ensure_ascii=False, encoding='utf-8')
        resultElem = base64.b64encode(resultElem)
      content = dc.EventObjects.Content(resultElem, cDateValue, dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
      ret.append(content)
    if contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_INTERNAL and \
      contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_CUSTOM:
      i = 0
      for elem in processedContent["internal"]:
        resultElem = json.dumps(elem, ensure_ascii=False, encoding='utf-8')
        resultElem = base64.b64encode(resultElem)
        contentInternal = dc.EventObjects.Content(resultElem, cDateValue,
                                                  dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
        if i < len(processedContent["custom"]):
          elemCustom = processedContent["custom"][i]
          resultElem = base64.b64encode(elemCustom)
          contentCustom = dc.EventObjects.Content(resultElem, cDateValue,
                                                  dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
        else:
          contentCustom = None
        insertTuple = (contentInternal, contentCustom)
        ret.append(insertTuple)
        i += 1
    elif contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_INTERNAL:
      for elem in processedContent["internal"]:
        resultElem = json.dumps(elem, ensure_ascii=False, encoding='utf-8')
        resultElem = base64.b64encode(resultElem)
        content = dc.EventObjects.Content(resultElem, cDateValue, dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
        ret.append(content)
        if (contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_ALL) == 0:
          break
    elif contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_CUSTOM:
      for elem in processedContent["custom"]:
        resultElem = base64.b64encode(elem)
        content = dc.EventObjects.Content(resultElem, cDateValue, dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
        ret.append(content)
        if (contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED_ALL) == 0:
          break

    logger.debug("Return Content instance list: %s", str(len(ret)))

    return ret


  # # parseProcessedBuf method decodes incoming processedContent buff, and fills, depend of contentMask value,
  # outgoing Contents list
  #
  # @param buf - incoming processedContent buff
  # @param cDateValue - incoming CDate value
  # @param contentMask - incoming contentMask
  # @return list of Content or tuple(Content, Content) objects
  @staticmethod
  def parseProcessedBuf(buf, cDateValue, contentMask):
    ret = []
    try:
      processedContent = json.loads(base64.b64decode(buf))
    except Exception as excp:
      processedContent = None
      logger.debug(">>> Wrong something bad with processedContent decode, =" + str(excp))
    if processedContent is not None:
      if isinstance(processedContent, types.DictType):
        if "custom" in processedContent and "internal" in processedContent:
          ret = ProcessedContentInternalStruct.processDictProcessedContent(cDateValue, contentMask, processedContent)
        else:
          logger.debug(">>> Wrong custom or internal not present in processedContent DICT")
      elif isinstance(processedContent, types.ListType):
        if contentMask & dc.EventObjects.URLContentRequest.CONTENT_TYPE_PROCESSED:
          resultElem = json.dumps(processedContent, ensure_ascii=False, encoding='utf-8')
          resultElem = base64.b64encode(resultElem)
          content = dc.EventObjects.Content(resultElem, cDateValue, dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT)
          ret.append(content)
    return ret
