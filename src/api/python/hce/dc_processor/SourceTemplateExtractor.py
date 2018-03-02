'''
@package: dc
@author scorp
@file SourceTemplateExtractor.py
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import json
import types
import hashlib
import datetime
import requests
import app.Utils as Utils  # pylint: disable=F0401

# Logger initialization
logger = Utils.MPLogger().getLogger()

# #SourceTemplateExtractor class implements templates exctracting from specified template sources
#
class SourceTemplateExtractor(object):


  SOURCE_NAME_FILE = "file"
  SOURCE_NAME_HTTP = "http"
  POST_BUFF_MACROS = ["RAW_CONTENT", "URL"]


  # #Class Constructor
  #
  def __init__(self):
    self.TemplHash = {}
    self.macroDict = {}


  # # scheduleCalc method calculates schedule conditions
  #
  # @param scheduler - incoming scheduler json structure
  # @param additionData - addition data, used in templates source conditions
  # @return bool value, that means use surrent template source or not use
  def scheduleCalc(self, schedule, additionData):
    ret = False
    scheduleStorageData = None
    curdatetime = datetime.datetime.now()
    if "file" in schedule:
      with open(schedule["file"], "r") as fd:
        scheduleStorageData = json.loads(fd.read())
    if schedule["type"] == 0:
      if additionData["parentMD5"] == "":
        ret = True
    elif schedule["type"] == 1:
      ret = True
    elif schedule["type"] == 2:
      if scheduleStorageData is not None:
        atTime = datetime.datetime.strptime(schedule["at"], "%Y-%m-%d %H:%M")
        saveAtTime = None
        if "saveAtTime" in scheduleStorageData and scheduleStorageData["saveAtTime"] is not None:
          saveAtTime = datetime.datetime.strptime(scheduleStorageData["saveAtTime"], "%Y-%m-%d %H:%M")
        if saveAtTime != atTime:
          scheduleStorageData["tCount"] = 0
          scheduleStorageData["saveAtTime"] = atTime.strftime("%Y-%m-%d %H:%M")
        if curdatetime > atTime:
          if scheduleStorageData["tCount"] == 0:
            ret = True
          scheduleStorageData["tCount"] += 1
    elif schedule["type"] == 3:
      if scheduleStorageData is not None:
        if "saveNowTime" in scheduleStorageData and scheduleStorageData["saveNowTime"] is not None:
          atTime = datetime.datetime.strptime(scheduleStorageData["saveNowTime"], "%Y-%m-%d %H:%M")
        else:
          atTime = datetime.datetime.strptime(schedule["at"], "%Y-%m-%d %H:%M")

        if curdatetime > (atTime + datetime.timedelta(minutes=int(schedule["step"]))):
          scheduleStorageData["saveNowTime"] = curdatetime.strftime("%Y-%m-%d %H:%M")
          ret = True
    if scheduleStorageData is not None:
      scheduleStorageData["datetime"] = curdatetime.strftime("%Y-%m-%d %H:%M")
      with open(schedule["file"], "w") as fd:
        fd.write(json.dumps(scheduleStorageData))
    return ret


  # # loadTemplateFromSource main public/process class method
  #
  # @param templateSource - incoming templateSource data
  # @param additionData - addition data, used in templates source conditions
  # @param rawContent - incoming resource's rawContent
  # @return new fetched templates
  def loadTemplateFromSource(self, templateSource, additionData=None, rawContent=None, url=None):
    ret = []
    self.macroDict = {}
    if rawContent is not None:
      self.macroDict["RAW_CONTENT"] = rawContent
    if url is not None:
      self.macroDict["URL"] = url
    templateSourceStruct = None
    try:
      templateSourceStruct = json.loads(templateSource)
    except Exception as excp:
      logger.debug(">>> Wrong while json loads from templateSource; err=" + str(excp))
    # if templateSourceStruct is not None and type(templateSourceStruct) is types.ListType:
    if templateSourceStruct is not None and isinstance(templateSourceStruct, types.ListType):
      for templateSourceElement in templateSourceStruct:
        addedElement = None
        try:
          if "schedule" in templateSourceElement and templateSourceElement["schedule"] is not None and \
          self.scheduleCalc(templateSourceElement["schedule"], additionData):
            if templateSourceElement["source"] == SourceTemplateExtractor.SOURCE_NAME_FILE:
              with open(templateSourceElement["request"], "rb") as fd:
                addedElement = json.loads(fd.read())
            elif templateSourceElement["source"] == SourceTemplateExtractor.SOURCE_NAME_HTTP:
              addedElement = self.resolveTemplateByHTTP(templateSourceElement)

          if addedElement is not None:
            if isinstance(addedElement, types.ListType) and len(addedElement) > 0:
              ret.append(addedElement[0])
            elif isinstance(addedElement, types.DictType):
              ret.append(addedElement)
        except Exception as excp:
          logger.debug(">>> Something wrong with templateSourceElement procession; err=" + str(excp))
    return ret


  # # resolveTemplateByHTTP method fetches by HTTP request and returns one or list template elements
  #
  # @param templateSourceElement - incoming template source element
  # @param rawContent - incoming resource's rawContent
  # @return one or list template elements
  def resolveTemplateByHTTP(self, templateSourceElement):
    ret = None
    requestString = None
    contentTypeHeader = None
    if "headers" in templateSourceElement:
      contentTypeHeader = json.loads(templateSourceElement["headers"])  # {"Content-Type": "application/json"}
    if templateSourceElement["request"].startswith("http://") or \
    templateSourceElement["request"].startswith("https://"):
      requestString = templateSourceElement["request"]
    else:
      pass
    if requestString is not None:
      if templateSourceElement["post"] is None or templateSourceElement["post"] == "":
        templateHash = hashlib.md5(requestString).hexdigest()
        if templateHash in self.TemplHash:
          ret = self.TemplHash[templateHash]
        else:
          ret = requests.get(requestString, headers=contentTypeHeader)
          self.TemplHash[templateHash] = ret
      else:
        templateHash = hashlib.md5(requestString + templateSourceElement["post"]).hexdigest()
        replacedPost = self.replacePostRawContent(templateSourceElement["post"])
        if templateHash in self.TemplHash:
          ret = self.TemplHash[templateHash]
        else:
          replacedPost = replacedPost.encode("utf-8")
          logger.debug(">>> POST Data: requestString:\n" + str(requestString) + \
                       "\ntemplateSourceElement:\n" + str(templateSourceElement["post"]) + \
                       "\nreplacedPost:\n" + str(replacedPost) + "\nheaders:\n" + str(contentTypeHeader))
          ret = requests.post(requestString, replacedPost, headers=contentTypeHeader)
          self.TemplHash[templateHash] = ret
      if ret is not None and ret.status_code == 200 and ret.text is not None:
        ret = json.loads(ret.text)
      else:
        logger.debug(">>> Something wrong with HTTP request, Response code == " + str(ret.status_code) +
                     "content == " + str(ret.text))
    return ret


  # # replacePostRawContent method finds and replaces RAW_CONTENT_MACRO in POST data
  #
  # @param post incoming POST data
  # @param rawContent - incoming resource's rawContent
  # @return replaced POST data
  def replacePostRawContent(self, post):
    ret = post
    for elem in self.POST_BUFF_MACROS:
      if post.find("%" + elem + "%") >= 0:
        if elem in self.macroDict:
          ret = post.replace("%" + elem + "%", self.macroDict[elem])
        else:
          ret = post.replace("%" + elem + "%", "")
    return ret
