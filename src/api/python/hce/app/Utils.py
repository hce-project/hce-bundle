'''
Created on Mar 28, 2014

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


try:
  import cPickle as pickle  # pylint: disable=W0611
except ImportError:
  import pickle  # pylint: disable=W0611

import json
import re
import sys
import os
import traceback
import types
import time
import hashlib
import ctypes
import zlib
import urllib
import urlparse
import collections
from subprocess import Popen
from subprocess import PIPE
from datetime import datetime
from decimal import Decimal
import logging
import threading
from stat import ST_MTIME
from HTMLParser import HTMLParser
import validators

import app.Consts as APP_CONSTS
from app.Url import Url
from app.url_normalize import url_normalize
from app.ExtendInnerText import ExtendInnerText
from app.Exceptions import UrlParseException


# Logger initialization
logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)

lock = threading.Lock()

# META_RE_0 = "<meta http-equiv=\"refresh\".*?>"
# META_RE_1 = "<!--(.*<meta http-equiv=\"refresh\".*|\n)*?-->"
# META_RE_2 = "url=(.*?)\""
# META_RE_3 = ";(http.*)\""

META_REDIRECT = r"http-equiv\W*refresh.+?url\W+?(.+?)\""

SEARCH_COMMENT_SIMPLE_PATTERN = r"<!--(.|\n)*?-->"
SEARCH_COMMENT_PATTERN = r"\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>"
SEARCH_NOSCRIPT_PATTERN = r"<noscript>(.|\n)*?</noscript>"

# #PropertiesValidator contains only 1 method - isValueIn, that find value in class(classType param)
# attributes that began with "prefix"
#
class PropertiesValidator(object):


  def __init__(self):
    pass


  @staticmethod
  def isValueIn(classType, prefix, value):
    retVal = False
    for localValue in classType.__dict__:
      if str(localValue).find(prefix) == 0:
        if value == getattr(classType, localValue, None):
          retVal = True
          break
    return retVal


# #getPath global function, finds and return value by path in json string or dict document
# dictionary - incoming dictionary (optional)
# jsonString - incoming json string (optional)
# path - incoming path to find
# method return valid value or raises exceptions -
# [ValueError] - bad jsodnString format
# [TypeError, KeyError, IndexError] - excpetions raised if path not found
# Warning!!! path don't checks by syntaxis
def getPath(dictionary, jsonString, path):
  if jsonString != None:
    dictionary = json.loads(jsonString)
  for i, p in re.findall(r'(\d+)|(\w+)', path):
    dictionary = dictionary[p or int(i)]
  return dictionary



# #Json serialization
#
class JsonSerializable(object):

  # #constructor
  # initialize task's fields
  #
  def __init__(self):
    pass

  @staticmethod
  def json_serial(obj):
    if isinstance(obj, datetime):
      return obj.isoformat()
    else:
      if isinstance(obj, Decimal):
        return str(obj)
      else:
        # if isinstance(obj, type.DictProxy):
        if isinstance(obj, types.DictProxyType):
          return dict(obj)
        else:
          return obj.__dict__


  def toJSON(self):
    # return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    # Support custom serialization of datetime
    return json.dumps(self.__dict__, default=JsonSerializable.json_serial, sort_keys=True, indent=4)


class SQLExpression(object):
  def __init__(self, stringExpression=""):
    super(SQLExpression, self).__init__()
    if stringExpression is None:
      self.str = ""
    else:
      self.str = str(stringExpression)

  def __str__(self):
    return self.str



# #The PathMaker class
#
# This class purpose to use as static method container to split FS directory pattern on two parts
# @param string is a directory pattern
# @param subdirLen is a number of characters in sub-directory item
#
class PathMaker(object):

  SUBDIR_LEVEL1_LEN = 2
  SUBDIR_CHAR = "/"

  def __init__(self, string, subdirLen=SUBDIR_LEVEL1_LEN):
    super(PathMaker, self).__init__()

    self.string = string
    self.subdirLen = subdirLen

    if "CONTENT_STORE_PATH" in os.environ and os.environ["CONTENT_STORE_PATH"] != "":
      logger.debug("os.environ[CONTENT_STORE_PATH]: set to %s", os.environ["CONTENT_STORE_PATH"])
      self.string += "/"
      self.string += os.environ["CONTENT_STORE_PATH"]
    else:
      logger.debug("os.environ[CONTENT_STORE_PATH]: not set.")

  def getDir(self):
    if len(self.string) > self.subdirLen:
      return self.string[:self.subdirLen] + self.SUBDIR_CHAR + self.string[self.subdirLen:]
    else:
      return self.string


# #The ConfigParamsList class
#
# This class purpose to use as object few options read from config
# @param initial_data - input dictionaries
# @param kwargs - keyword arguments
#
class ConfigParamsList(object):
  def __init__(self, *initial_data, **kwargs):
    for dictionary in initial_data:
      for key in dictionary:
        setattr(self, key, dictionary[key])
    for key in kwargs:
      setattr(self, key, kwargs[key])


# #The function to safe getting config parameters and  return default value if cannot get value
#
# @param parser - instance of ConfigParser class
# @param section  - section name of parameter
# @param option - option name of parameter
# @param defValue - default value
# @return - if success extracted value, otherwise return default value
#
def getConfigParameter(parser, section, option, defValue):
  ret = defValue

  if parser and parser.has_option(section, option):
    try:
      ret = parser.get(section, option, defValue)
    except Exception:
      ret = defValue

  return ret


# #The function to get traceback information string prepared for logging
#
# This function collects traceback information and creates sreing representation ready to log it
# @param linesNumberMax max number of traceback lines to include in to the collection, None - signs all
# @ret return string
#
def getTracebackInfo(linesNumberMax=None):
  ret = ""
  n = 0

  type_, value_, traceback_ = sys.exc_info()
  stack = traceback.format_tb(traceback_)
  del type_
  del value_
  for item in stack:
    ret = ret + "\n" + (str(item))
    n = n + 1
    if linesNumberMax != None and n == linesNumberMax:
      break

  return ret



# #The function to get accumulate the traceback information in global variable __tracebackList
tracebackList = []
tracebackTimeQueue = []
tracebackIdent = False
tracebackIdentFiller = "-"
tracebackMessageCall = "call"
tracebackMessageExit = "exit"
tracebackmessageDelimiter = ":"
tracebackTimeMark = True
tracebackTimeMarkFormat = "%Y-%m-%d %H:%M:%S.%f"
tracebackTimeMarkDelimiter = " "
tracebackIncludeInternalCalls = False
tracebackIncludeLineNumber = True
tracebackIncludeLineNumberDelimiter = ":"
tracebackIncludeFileNumber = True
tracebackIncludeFileNumberDelimiter = ":"
tracebackFunctionNameDelimiter = ":"
tracebackExcludeModulePath = ["/usr/lib/", "/usr/local/lib/"]
tracebackExcludeFunctionName = ["varDump"]
tracebackExcludeFunctionNameStarts = ["<"]
tracebackIncludeExitCalls = True
tracebackRecursionlimit = 0
tracebackRecursionlimitErrorMsg = "RECURSION STACK LIMIT REACHED "
tracebackIncludeLocals = False
tracebackIncludeArg = False
tracebackIncludeLocalsPrefix = "\nLOCALS:\n"
tracebackIncludeArgPrefix = "\nARG:\n"
tracebackLogger = None
tracebackElapsedTimeDelimiter = ""
tracebackElapsedTimeFormat = "{:.6f}"
tracebackUnknownExceptionMsg = "Unknown exception!"

#
# This function collects traceback information and creates sreing representation ready to log it
# @param linesNumberMax max number of traceback lines to include in to the collection, None - signs all
# @ret return string
#
def tracefunc(frame, event, arg, indent=None):  # pylint: disable=W0613
  if indent is None:
    indent = [0]

  if event == "call" or event == "return":
    lock.acquire()

    try:
      if event == "call":
        indent[0] += 2
        if tracebackIdent:
          idents = tracebackIdentFiller * indent[0]
        else:
          idents = ""
        message = tracebackMessageCall
        tracebackTimeQueue.append(time.time())
        te = ""
      elif event == "return":
        if tracebackIdent:
          idents = tracebackIdentFiller * indent[0]
        else:
          idents = ""
        indent[0] -= 2
        message = tracebackMessageExit
        te = "{:.6f}".format(time.time() - tracebackTimeQueue.pop())

      if tracebackTimeMark:
        # t = time.strftime(tracebackTimeMarkFormat)
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
      else:
        t = ""

      if tracebackIncludeLineNumber:
        ln = str(frame.f_lineno)
      else:
        ln = ""

      if tracebackIncludeFileNumber:
        fn = str(frame.f_code.co_filename)
      else:
        fn = ""

      excludedP = False
      for item in tracebackExcludeModulePath:
        if item in frame.f_code.co_filename:
          excludedP = True
          break

      excludedF = False
      for item in tracebackExcludeFunctionName:
        if frame.f_code.co_name == item:
          excludedF = True
          break

      excludedF2 = False
      for item in tracebackExcludeFunctionNameStarts:
        if frame.f_code.co_name.startswith(item):
          excludedF2 = True
          break

      if tracebackIncludeLocals or tracebackIncludeArg:
        oldRL = sys.getrecursionlimit()
        if oldRL < tracebackRecursionlimit:
          sys.setrecursionlimit(tracebackRecursionlimit)
        else:
          oldRL = None

        if tracebackIncludeLocals:
          localsDump = ""
          try:
            # localsDump = varDump(frame.f_locals)
            localsDump = str(frame.f_locals)
            localsDump = tracebackIncludeLocalsPrefix + localsDump
          except:  # pylint:disable=W0702
            localsDump = tracebackRecursionlimitErrorMsg + str(tracebackRecursionlimit)
            # pass
        else:
          localsDump = ""

        if tracebackIncludeArg:
          argDump = ""
          try:
            # argDump = varDump(arg)
            argDump = str(arg)
            argDump = tracebackIncludeArgPrefix + argDump
          except:  # pylint:disable=W0702
            argDump = tracebackRecursionlimitErrorMsg + str(tracebackRecursionlimit)
            # pass
        else:
          argDump = ""

        if oldRL is not None:
          sys.setrecursionlimit(oldRL)
      else:
        localsDump = ""
        argDump = ""

      if (not (tracebackIncludeInternalCalls is False and frame.f_code.co_name.startswith("__"))) and\
        (not (tracebackIncludeExitCalls is False and event == "return")) and\
        (not excludedP) and (not excludedF) and (not excludedF2):
        tmsg = idents + message + tracebackmessageDelimiter + \
                             fn + tracebackIncludeFileNumberDelimiter + \
                             ln + tracebackIncludeLineNumberDelimiter + \
                             frame.f_code.co_name + "()" + tracebackFunctionNameDelimiter + \
                             tracebackElapsedTimeDelimiter + te + localsDump + argDump
        if tracebackLogger is None:
          tracebackList.append(t + tracebackTimeMarkDelimiter + tmsg)
        else:
          tracebackLogger.debug("%s", tmsg)
          if len(tracebackTimeQueue) == 0:
            tracebackLogger.debug("%s", APP_CONSTS.LOGGER_DELIMITER_LINE)

    except Exception as e:
      if tracebackLogger is None:
        tracebackList.append("Exception: " + str(e))
      else:
        tracebackLogger.error("%s", str(e))
    except:  # pylint: disable=W0702
      if tracebackLogger is None:
        tracebackList.append(tracebackUnknownExceptionMsg)
      else:
        tracebackLogger.error("%s", tracebackUnknownExceptionMsg)

    lock.release()

  return tracefunc



# #The function to get a printable representation of an object for debugging
#
#
# @param obj The object to print
# @param stringifyType - 0 - json, 1 - str
# @ret return string dump
#
def varDump(obj, stringify=True, strTypeMaxLen=256, strTypeCutSuffix='...', stringifyType=1, ignoreErrors=False,
            objectsHash=None, depth=0, indent=2, ensure_ascii=False, maxDepth=10):
  if objectsHash is None:
    objectsHash = []
  # print 'depth: ' + str(depth)
  depth += 1
  if depth < maxDepth:
    newobj = obj
    try:
      if isinstance(obj, list):
        newobj = []
        for item in obj:
          newobj.append(varDump(item, False, strTypeMaxLen, strTypeCutSuffix, stringifyType, ignoreErrors,
                                objectsHash, depth, indent, ensure_ascii, maxDepth))
      elif isinstance(obj, tuple):
        temp = []
        for item in obj:
          temp.append(varDump(item, False, strTypeMaxLen, strTypeCutSuffix, stringifyType, ignoreErrors,
                              objectsHash, depth, indent, ensure_ascii, maxDepth))
        newobj = tuple(temp)  # pylint: disable=R0204
      elif isinstance(obj, set):
        temp = []
        for item in obj:
          temp.append(str(varDump(item, False, strTypeMaxLen, strTypeCutSuffix, stringifyType, ignoreErrors,
                                  objectsHash, depth, indent, ensure_ascii, maxDepth)))
        newobj = set(temp)
      elif isinstance(obj, dict):
        newobj = {}
        for key, value in obj.items():
          newobj[str(varDump(key, False, strTypeMaxLen, strTypeCutSuffix))] = \
           varDump(value, False, strTypeMaxLen, strTypeCutSuffix, stringifyType, ignoreErrors,
                   objectsHash, depth, indent, ensure_ascii, maxDepth)
      # elif isinstance(obj, types.FunctionType):
      #  newobj = repr(obj)
      elif '__dict__' in dir(obj):
        newobj = {}
        for k in obj.__dict__.keys():
          # print 'k:' + str(k)
          # print 'v:' + str(obj.__dict__[k])
          if isinstance(obj.__dict__[k], basestring):
            newobj[k] = obj.__dict__[k]
            if strTypeMaxLen > 0 and len(newobj[k]) > strTypeMaxLen:
              newobj[k] = newobj[k][:strTypeMaxLen] + strTypeCutSuffix
          else:
            if '__dict__' in dir(obj.__dict__[k]):
              sobj = str(obj.__dict__[k])
              if sobj in objectsHash:
                newobj[k] = 'OBJECT RECURSION: ' + sobj
              else:
                objectsHash.append(sobj)
                newobj[k] = varDump(obj.__dict__[k], False, strTypeMaxLen, strTypeCutSuffix, stringifyType,
                                    ignoreErrors, objectsHash, depth, indent, ensure_ascii, maxDepth)
            else:
              newobj[k] = varDump(obj.__dict__[k], False, strTypeMaxLen, strTypeCutSuffix, stringifyType,
                                  ignoreErrors, objectsHash, depth, indent, ensure_ascii, maxDepth)
        sobj = str(obj)
        if ' object at ' in sobj and '__type__' not in newobj:
          newobj['__type__'] = sobj.replace(" object at ", " #").replace("__main__.", "")
      else:
        if stringifyType == 0:
          try:
            s = json.dumps(newobj, indent=indent, ensure_ascii=ensure_ascii)
            del s
          except Exception as err:
            newobj = str(newobj)
    except Exception as err:
      if ignoreErrors:
        newobj = ''
      else:
        newobj = 'General error: ' + str(err) + "\n" + getTracebackInfo()
  else:
    newobj = 'MAX OBJECTS EMBED DEPTH ' + str(maxDepth) + ' REACHED!'

  if stringify:
    if stringifyType == 0:
      try:
        newobj = json.dumps(newobj, indent=indent, ensure_ascii=ensure_ascii)
      except Exception as err:
        if ignoreErrors:
          newobj = ''
        else:
          newobj = 'To json error: ' + str(err)
    else:
      newobj = str(newobj)

  return newobj


# pylint: disable=W0702
def memUsage(point=""):
  import resource
  # usage = resource.getrusage(resource.RUSAGE_SELF)
  return '''%s: mem=%s mb
      ''' % (point, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000)



# #class UrlParser makes URL operation
#
class UrlParser(object):


  def __init__(self):
    pass


  # #The function check protocol and dimain name in the incoming url
  #
  # url - param, incoming url
  # @ret boolean
  @staticmethod
  def isValidURL(url):
    ret = False
    parseUrl = urlparse.urlparse(url)
    if parseUrl.scheme != None and parseUrl.netloc != None:
      ret = True
    return ret


  # #The function generates base url
  #
  # url - param, incoming url
  # @ret boolean
  @staticmethod
  def generateDomainUrl(url):
    ret = ""
    parseUrl = urlparse.urlparse(url)
    if UrlParser.isValidURL(url):
      ret = parseUrl.scheme + "://" + parseUrl.netloc
    else:
      raise UrlParseException("Empty protocol or domain name")
    return ret


  # #The function extracts domain name
  #
  # url - param, incoming url
  # @ret boolean
  @staticmethod
  def getDomain(url):
    auth = urlparse.urlsplit(url.strip())[1]
    ret = (re.search('([^@]*@)?([^:]*):?(.*)', auth).groups())[1]
    return ret


# # normalization url string use base url
#
# @param base - base url string
# @param url - url string
# @param supportProtocols - support protocol list
# @param log - logger instance
# @return already normalized url string or None - in case of bad result normalization
def urlNormalization(base, url, supportProtocols=None, log=None):
  # variable for result
  res = None

  # Internal function for prepare before normalization
  def prepareNormalization(path):
    out = []
    pathStr = path
    replaceSimbolDict = {'\a':'/a',
                         '\b':'/b',
                         '\f':'/f',
                         '\n':'/n',
                         '\r':'/r',
                         '\t':'/t',
                         '\v':'/v',
                         '\\':'\\\\'}

    replaceStartSimbolDict = {'://': ''}

    for src, dest in replaceStartSimbolDict.items():
      if pathStr.startswith(src):
        pathStr = pathStr.replace(src, dest)

    for src, dest in replaceSimbolDict.items():
      pathStr = pathStr.replace(src, dest)      

    for i in range(0, 32):
      pathStr = pathStr.replace(str(chr(i)), str('/%o' % i))

    for s in pathStr.split("\\"):
      out.append(s)

    out = [elem for elem in out if elem != '']

    return '/'.join(out)


  if isinstance(url, basestring):
    # validate
#     if Url(url).isValid():
#       if log is not None:
#         log.debug("return as valid url: %s", str(url))
#       res = url
#     else:
    # set default result
    resUrl = prepareNormalization(url)
    if isinstance(base, basestring):
      # normalization url
      baseUrl = prepareNormalization(base)

      if baseUrl != resUrl:
        resUrl = urlparse.urljoin(baseUrl, resUrl)

      if url != resUrl and log is not None:
        log.debug('==== Urls different ====')
        log.debug("base: %s", str(baseUrl))
        log.debug("url: %s", str(url))
        log.debug("res: %s", str(resUrl))

      res = resUrl

  # check support protocols
  if isinstance(supportProtocols, list):
    if log is not None:
      log.debug("supportProtocols: %s, res: %s", str(supportProtocols), str(res))
    # extract protocol schema from url
    if isinstance(res, basestring):
      v = urlparse.urlsplit(res)
      if v.scheme not in supportProtocols:
        if log is not None:
          log.debug("Not support protocol: %s", str(v.scheme))
        res = None

  if log is not None:
    log.debug("before normalization res: %s", str(res))

  # normalization
  if res is not None:
    localUrls = res.split()
    resUrls = []
    if log is not None:
      log.debug("localUrls: %s", str(localUrls))

    for localUrl in localUrls:
      if localUrl != "":
        resUrls.append(url_normalize(localUrl))

    if log is not None:
      log.debug("resUrls: %s", varDump(resUrls))
    res = ','.join(resUrls)
    if log is not None:
      log.debug("res: %s", str(res))

  return res


# #class UrlNormalizator makes URL normalization
#
class UrlNormalizator(object):

  NORM_NONE = 0
  NORM_SKIP_WWW = 1
  NORM_USE_VALIDATOR = 2
  NORM_MAIN = 4
  NORM_DEFAULT = NORM_MAIN
  BAD_URL_PREFIX = "normalization-error://?"


  def __init__(self):
    pass


  # #The function normalize the incoming url according  RFC 3986
  #
  # url - param, incoming url
  # @ret normalized url
  @staticmethod
  def normalize(url, supportProtocols=None, normMask=NORM_DEFAULT):
    norm_url = url.strip()
    if normMask != 0:
      logger.debug("None zero normMask: %s", str(normMask))
    # TODO: need to be replaced with default filter for collect URLs protocols check stage
    if supportProtocols is not None and isinstance(supportProtocols, list):
      colonPos = norm_url.find(':')
      slashPos = norm_url.find('/')
      if colonPos != -1 and (slashPos == -1 or slashPos > colonPos):
        if len(norm_url.split(':')) > 1:
          protocol = norm_url.split(':')[0]
          if protocol not in supportProtocols:
            try:
              norm_url = UrlNormalizator.BAD_URL_PREFIX + urllib.quote(norm_url)
            except Exception as err:
              logger.debug(">>> urllib.quote error = " + str(err))
              norm_url = UrlNormalizator.BAD_URL_PREFIX + norm_url

    if norm_url == url:
      try:
        stripWWW = True if normMask & UrlNormalizator.NORM_SKIP_WWW else False
        useValidator = True if normMask & UrlNormalizator.NORM_USE_VALIDATOR else False
        enableAdditionNormalize = True if normMask & UrlNormalizator.NORM_MAIN else False
        norm_url = str(urinormpath(url.strip(), stripWWW, useValidator, enableAdditionNormalize))
        # norm_url = str(canonicalize_url(url.strip()))
        # logger.debug("norm_url: <%s>", norm_url)
        # except urlnorm.InvalidUrl:
        #  logger.error("Normalization InvalidUrl")
        #  norm_url = ""
      except Exception as e:
        logger.error("Normalization error: " + str(e) + "\nURL: [" + url + "]\n" + str(getTracebackInfo()))

    return norm_url


  # #The check url by bad url prefix
  #
  # url - param, incoming url
  # @ret bool value is url valid or not
  @staticmethod
  def isNormalUrl(url):
    return False if url.find(UrlNormalizator.BAD_URL_PREFIX) == 0 else True


  # #The function encode entities "&" to "&amp;" if needed
  #
  # @param url to encode
  # @param entities dict, keys are not encode and values are encoded forms
  # @return encoded url
  @staticmethod
  def entitiesEncode(url, entities=None):
    ret = url
    if entities is None:
      entities = {"&": "&amp;"}

    for k in entities:
      le = len(entities[k])
      p = -1
      while True:
        l = len(ret)
        p = ret.find(k, p + 1)
        if p == -1:
          break
        else:
          if (p + le - 1 > l) or ((p + le - 1 <= l) and (ret[p:p + le] != entities[k])):
            ret = ret[:p] + entities[k] + ret[p + 1:]
          else:
            continue

    return ret



# ENV_SCRAPER_STORE_PATH = "ENV_SCRAPER_STORE_PATH"
# # storePickleOnDisk
#
def storePickleOnDisk(input_pickled_object, env_path, file_name):
  if env_path in os.environ and os.environ[env_path] != "":
    logger.debug("os.environ[%s]: set to %s", env_path, os.environ[env_path])
    open(os.environ[env_path] + file_name, "wb").write(input_pickled_object)
  else:
    logger.debug("os.environ[%s]: not set.", env_path)



# This function taken from uritools module as it was removed from module
def urinormpath(path, stripWWW=False, useValidator=False, enableAdditionNormalize=True):  # pylint: disable=W0613
  # Remove '.' and '..' path segments from a URI path.
  # RFC 3986 5.2.4. Remove Dot Segments
  ret = None
  ret1 = None

  try:
    if path is None or path == "":
      ret1 = path
    else:
      out = []
      for s in path.split('/'):
        if s == '.':
          continue
        elif s != '..':
          out.append(s)
        elif out:
          out.pop()
      # Fix leading/trailing slashes
      if path.startswith('/') and (not out or out[0]):
        out.insert(0, '')
      if path.endswith('/.') or path.endswith('/..'):
        out.append('')
      ret = '/'.join(out)

      if stripWWW:
        splitPath = path.split("?")
        if len(splitPath) > 0:
          splitPath[0] = splitPath[0].replace("://www.", "://")
          localPath = splitPath[0]
          for elem in splitPath[1:]:
            localPath += "?"
            localPath += elem
      else:
        localPath = path

      if enableAdditionNormalize:
        resultUrlDict = Url(localPath)
        if useValidator and not Url.GetStats([resultUrlDict])[0]["valid"]:
          raise Exception(path + " NOT VALIDATE!")
        ret1 = Url.GetStats([resultUrlDict])[0]["canonicalized"]
      else:
        ret1 = localPath

      if ret is not None and ret1 is not None and ret != ret1:
        logger.debug("--->>>> URLS DIFFERTNT <<<<---")
        logger.debug(ret)
        logger.debug(ret1)
  except Exception as e:
    logger.error("Normalization error: " + str(e) + "\npath: [" + path + "]\n" + str(getTracebackInfo()))

  return ret1



# #Logger file name generator
#
#
class LoggerFileName(object):


  def __init__(self, loggerInst=None):
    self.loggerInst = loggerInst


  def getFreeProcInstanceNumber(self, sock_prefix="module", min_number=0, max_number=32):
    ret = ""

    for i in range(min_number, max_number):
      try:
        import socket

        global lock_socket  # pylint: disable=W0601
        lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        # Create an abstract socket
        lock_socket.bind('\0' + "dc_process_lock_" + sock_prefix + str(i))
        ret = str(i)
        break
      except socket.error:
        # Socket already exists
        continue

    return ret


  def findReplace(self, newFile=None, rollover=True):
    log_file = None

    if self.loggerInst is None:
      lg = logging.getLogger('')
    else:
      lg = self.loggerInst
    for h in lg.__dict__['handlers']:
      if h.__class__.__name__ == 'FileHandler':
        log_file = h.baseFilename
        if newFile is not None:
          h.baseFilename = newFile
          if h.stream:
            h.stream.close()
            h.stream = None
          h.stream = h._open()  # pylint: disable=W0212
          if os.path.exists(newFile):
            t = os.stat(newFile)[ST_MTIME]
          else:
            t = int(time.time())
          h.rolloverAt = h.computeRollover(t)
          if rollover and h.shouldRollover(''):
            h.doRollover()
        break
      elif h.__class__.__name__ == 'TimedRotatingFileHandler':
        log_file = h.baseFilename
        if newFile is not None:
          h.baseFilename = newFile
          if h.stream:
            h.stream.close()
            h.stream = None
          h.stream = h._open()  # pylint: disable=W0212
          if rollover and h.shouldRollover(''):
            h.doRollover()
        break

    return log_file



# #Flush logger's file type handlers
#
# @param loggerObj
def loggerFlush(loggerObj):
  for h in loggerObj.handlers:
    if h.__class__.__name__ == 'FileHandler' or h.__class__.__name__ == 'TimedRotatingFileHandler':
      h.flush()



# #accumulateSubstrings accumulates substr list in one string and returns it, also adds prefixies between
#  substrings in resulting string. substrList and prefixes must be List[str] type with equal length
# @param substrList - substrings list
# @param prefixes - prefixies list
# @returns - accumulate string
def accumulateSubstrings(substrList, prefixes):
  ret = ""
  if substrList is None or not isinstance(substrList, list):  # # type(substrList) is not types.ListType:
    raise Exception(">>> error substrList is None or not List type")
  if prefixes is None or not isinstance(prefixes, list):  # #  type(prefixes) is not types.ListType:
    raise Exception(">>> error prefixes is None or not List type")
  if len(substrList) != len(prefixes):
    raise Exception(">>> error substrList and prefixes lists have different lengths")
  i = 0
  for substr in substrList:
    if isinstance(substr, str) or isinstance(substr, unicode):
      if isinstance(prefixes[i], str) or isinstance(prefixes[i], unicode):
        ret += str(prefixes[i])
      ret += str(substr)
    i += 1
  return ret



class DataReplacementConstants(object):

  CUR_YEAR_FULL = "@CUR_YEAR_FULL"
  CUR_YEAR_SHORT = "@CUR_YEAR_SHORT"
  CUR_MONTH = "@CUR_MONTH"
  CUR_DAY = "@CUR_DAY"


# #generateReplacementDict method generates and returns replacement dict with current datatime
# @returns - replacement dict with current datatime
def generateReplacementDict():
  ret = {}
  ret[DataReplacementConstants.CUR_YEAR_FULL] = datetime.now().strftime("%Y")
  ret[DataReplacementConstants.CUR_YEAR_SHORT] = datetime.now().strftime("%y")
  ret[DataReplacementConstants.CUR_MONTH] = datetime.now().strftime("%m")
  ret[DataReplacementConstants.CUR_DAY] = datetime.now().strftime("%d")
  return ret


# #parseHost parse the root host name from url
# for example: the result of http://s1.y1.example.com/path/to is example.com
# @param url the full url
# @return host of the url, eg: example.com
def parseHost(url):
  host = None
  if urlparse.urlparse(url).hostname:
    host = '.'.join(urlparse.urlparse(url).hostname.split('.')[-2:])
  return host


# # convert date str to HTTP header format
# 2014-07-29 20:31:50 (GMT+8) to Tue, 29 Jul 2014 12:31:50 GMT
# @param date_str date str, 2014-07-29 20:31:50
# @return HTTP header formated date str : Tue, 29 Jul 2014 12:31:50 GMT
def convertToHttpDateFmt(date_str):
  stamp = time.mktime(date_str.timetuple())
  # stamp = time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S'))
  return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(stamp))


# # method returns siteId, substitutes to "0" value if incoming siteId is None
# @param siteId - ID of site
# @param log - logger instanse for log usage
def autoFillSiteId(siteId, log):
  ret = siteId
  if siteId is None:
    ret = "0"
    if log is not None:
      log.debug("set siteId = '0' from 'autoFillSiteId'")

  return ret


# # method strips incoming html from html comments
# @param htmlBuf incoming content in string format
# @param soup incoming content as bs object
# @param hType -hType of handler
# @return clean html buff
def stripHTMLComments(htmlBuf=None, soup=None, hType=3):
  from bs4 import Comment

  ret = htmlBuf
  if soup is not None and hType == 0:
    for elem in soup.findAll(text=lambda text: isinstance(text, Comment)):
      elem.extract()
  elif htmlBuf is not None and hType == 1:
    ret = re.sub(SEARCH_COMMENT_PATTERN, "", htmlBuf)
    logger.debug("!!! use pattern: %s", str(SEARCH_COMMENT_PATTERN))
  elif htmlBuf is not None and hType == 2:
    ret = re.sub(SEARCH_COMMENT_SIMPLE_PATTERN, "", htmlBuf)
    logger.debug("!!! use pattern: %s", str(SEARCH_COMMENT_SIMPLE_PATTERN))
  elif htmlBuf is not None and hType == 3:
    ret = cutSubstringEntrances(htmlBuf, behaveMask=2)

  return ret


# Cuts substring entrances in source buffer started and finished with strings
#
# @param buf - source buffer
# @param startStr - start string
# @param finishStr - finish string
# @param behaveMask - bit set mask defines a behavior in case of finishStr not found, 0 - do nothing,
#                    1 - cut up to finishDefault or end of buffer if no end of line found, 2 - cut up to end of buffer
# @param greediness - max cutting number, 0 - means unlimited
# @param finishDefault - default finish string used if behaveMask == 1 and finishStr is not found
# @return resulted string
def cutSubstringEntrances(buf, startStr='<!--', finishStr='-->', behaveMask=0, greediness=0, finishDefault='\n'):
  ret = buf
  i = 0
  while True:
    i += 1
    replaced = False
    if ret.find(startStr) != -1:
      p = ret.index(startStr)
      if p is not None:
        p1 = None
        if ret.find(finishStr, p) != -1:
          p1 = ret.index(finishStr, p) + len(finishStr)
        else:
          if behaveMask == 1:
            if ret.find(finishDefault, p) != -1:
              p1 = ret.index(finishDefault, p) + len(finishDefault)
            else:
              p1 = len(ret)
          if behaveMask == 2:
            p1 = len(ret)
        if p1 is not None:
          ret = ret[0:p] + ret[p1:]
          # print ret
          replaced = True
    if greediness > 0 and i == greediness:
      break
    if not replaced:
      break

  return ret


# # method erase incoming html from noscript blocks
# @param htmlBuf - incoming content in string format
# @return clean html buff
def eraseNoScript(htmlBuf=None):
  ret = htmlBuf
  if htmlBuf is not None:
#     ret = re.sub(SEARCH_NOSCRIPT_PATTERN, "", htmlBuf)
#     logger.debug("!!! use pattern: %s", str(SEARCH_NOSCRIPT_PATTERN))
    ret = cutSubstringEntrances(htmlBuf, startStr='<noscript>', finishStr='</noscript>', behaveMask=2)
#     logger.debug("!!! htmlBuf: %s", varDump(htmlBuf, strTypeMaxLen=10))
#     logger.debug("!!! ret: %s", varDump(ret, strTypeMaxLen=10))

  return ret


# Strips from all HTML tags with set of different methods
# @param htmlTxt input content
# @param method 0 - by BeautifulSoup, 1 - with RE 1, 2 - RE 2, 3 - HTML parser, 4 - clear Python w/o lib, 5 - xml lib
# @param joinGlue - the glue string to joing parts
# @param regExp - the custom re for the method 1 or 2
# @return cleared content
def stripHTMLTags(htmlTxt, method=2, joinGlue=' ', regExp=None):
  ret = ''

  if htmlTxt is not None and htmlTxt.strip() != '':
    if method == 0:
      from bs4 import BeautifulSoup
      ret = joinGlue.join(BeautifulSoup(htmlTxt, 'lxml').findAll(text=True))
    elif method == 1 or method == 2:
      if regExp is not None:
        r = regExp
      else:
        if method == 1:
          #r = ur'<[^<]+?>'
          r = ur'<[^>]*>'
        else:
          r = ur'(<!--.*?-->|<[^>]*>)'
      ret = re.sub(r, joinGlue, htmlTxt, flags=re.UNICODE)
    elif method == 3:
      ret = MLStripper()
      ret.feed(htmlTxt)
      ret = ret.get_data()
    elif method == 4:
      tag = False
      quote = False
      for c in htmlTxt:
        if c == '<' and not quote:
          tag = True
        elif c == '>' and not quote:
          tag = False
        elif (c == '"' or c == "'") and tag:
          quote = not quote
        elif not tag:
          ret = ret + joinGlue + c
    elif method == 5:
      import xml
      ret = joinGlue.join(xml.etree.ElementTree.fromstring(htmlTxt).itertext())

  if method == 1 or method == 2:
    import cgi
    ret = cgi.escape(ret)
    ret = re.sub('[<>]', '', ret)

  return ret.strip()



class MLStripper(object, HTMLParser):
  def __init__(self, joinGlue=' '):
    super(MLStripper, self).__init__()
    self.reset()
    self.fed = []
    self.joinGlue = joinGlue


  def handle_data(self, d):
    self.fed.append(d)


  def get_data(self):
    return self.joinGlue.join(self.fed)


# # function extracts text from html content, strips all tags
# @param htmlText incoming raw html
# @param stripComment is strip comment or not
# @param stripScript is strip script or not
# @return inner html text
def innerHTMLText(htmlBuf, stripComment=True, stripScript=True):
  from bs4 import BeautifulSoup

  soup = BeautifulSoup(htmlBuf, 'lxml')

  if stripScript:
    for elem in soup.findAll(name='script'):
      elem.extract()
  if stripComment:
    stripHTMLComments(htmlBuf=None, soup=soup)

  return ''.join(soup.findAll(text=True))


# # function concatinates all HTMLTags from extractor also strips elements
# @param selectorList incoming Selector
# @return inner text from incoming selector
def innerText(selectorList, delimiter=' ', innerDelimiter=' ', tagReplacers=None, REconditions=None,
              attrConditions=None, keepAttributes=None, baseUrl=None, closeVoid=None, excludeNodes=None):
  extendInnerText = ExtendInnerText(tagReplacers, delimiter, innerDelimiter, REconditions, attrConditions,
                                    keepAttributes, baseUrl, closeVoid, excludeNodes)
  extendInnerText.innerText(None, selectorList, None)
  ret = extendInnerText.stripHtml
  return ret


# # function concatinates all HTMLTags from extractor also strips elements
# @param selectorList incoming Selector
# @return list of inner text from incoming selector
def innerTextToList(selectorList, delimiter=' ', innerDelimiter=' ', tagReplacers=None, REconditions=None,
                    attrConditions=None, keepAttributes=None, baseUrl=None, closeVoid=None, excludeNodes=None):
  extendInnerText = ExtendInnerText(tagReplacers, delimiter, innerDelimiter, REconditions, attrConditions,
                                    keepAttributes, baseUrl, closeVoid, excludeNodes)
  extendInnerText.innerTextToList(None, selectorList, None)
  ret = extendInnerText.stripHtmlList
  return ret


# # function looks fiers not empty extracted XPath from subXPathes, using subXPathPattern for real xpath creating
# @param xpath - incoming root xpath
# @param sel - incoming selector
# @param subXPathPattern - subXPath creation pattern
# @param subXPathes - list of subXPathes
# @return retXPath and retXPathValue values
def getFirstNotEmptySubXPath(xpath, sel, subXPathPattern, subXPathes):
  retXPath = None
  retXPathValue = None
  for subXPath in subXPathes:
    retXPath = xpath + (subXPathPattern % subXPath)
    try:
      retXPathValue = sel.xpath(retXPath).extract()
    except Exception as excp:
      logger.info(">>> Common xPath extractor exception, = " + retXPath + " excp=" + str(excp))
      retXPathValue = None
      continue
    if len(retXPathValue) > 0 and ''.join(retXPathValue).strip() != '':
      break
  return retXPath, retXPathValue


# # function call splitPairs for each element in incomeDict and fills return dict
# @param incomeDict incoming dict
# @param splitters incoming splitters
# @return result dict
def getPairsDicts(incomeDict, splitters=','):
  ret = {}
  if isinstance(incomeDict, dict):
    for key in incomeDict:
      if isinstance(incomeDict[key], str) or isinstance(incomeDict[key], unicode):
        ret[key] = splitPairs(incomeDict[key], splitters)
  return ret


# # function extracts splits incoming string by splitters into dict of name=value pairs
# @param buf incoming text buf
# @param splitters incoming splitters
# @return result dict
def splitPairs(buf, splitters=','):
  ret = {}
  splitStr = buf.split(splitters)
  for elem in splitStr:
    localStr = elem.split('=')
    if isinstance(localStr, list) and len(localStr) >= 2:
      ret[localStr[0]] = localStr[1]
  return ret


# # function looks is str2 an a tail of str1
# @param str1 main string
# @param str2 searching tail substring
# @return False or True
def isTailSubstr(str1, str2):
  ret = False
  if str1.find(str2) > 0 and ((len(str1) - str1.find(str2)) == len(str2)):
    ret = True
  return ret


# # function make string raplacement while
# @param buf incoming text buf
# @param replaceFrom substring for replacement from
# @param replaceTo substring for replacement to
# @return replacement string
def replaceLoopValue(buf, replaceFrom, replaceTo):
  localValue = buf
  replaceValue = localValue.replace(replaceFrom, replaceTo)
  while len(replaceValue) != len(localValue):
    localValue = replaceValue
    replaceValue = localValue.replace(replaceFrom, replaceTo)
  return localValue


# # # function extract html redirect link from meta
# # @param utf8Buff incoming buff of html page
# # @param log - logger instance
# # @return html redirect link
# def extractHTMLRedirectFromMeta(utf8Buff, log):
#   # variable for result
#   ret = None
#
#   localREList = re.findall(META_RE_0, utf8Buff, re.I)
#   if len(localREList) > 0:
#     log.debug("!!! Found pattern: '%s' - HTML redirect is exist...", str(META_RE_0))
#     match = re.search(META_RE_1, utf8Buff, re.I | re.U)
#     if match is not None:
#       log.debug("!!! Found pattern: '%s' - HTML redirect blocked by comment...", str(META_RE_1))
#     else:
#       for bodyStr in localREList:
#         match = re.search(META_RE_2, bodyStr, re.I | re.U)
#         log.debug("!!! bodyStr: %s, pattern: '%s', match: %s", str(bodyStr), str(META_RE_2), varDump(match))
#         if match is not None:
#           ret = match.group(1)
#         else:
#           match = re.search(META_RE_3, bodyStr, re.I | re.U)
#           log.debug("!!! bodyStr: %s, pattern: '%s', match: %s", str(bodyStr), str(META_RE_3), varDump(match))
#           if match is not None:
#             ret = match.group(1)
#
#         if ret is not None:
#           break
#
#   return ret


# # extract html redirect link from meta
# @param buff - raw contant of html page
# @param log - logger instance
# @return - html redirect link
def getHTMLRedirectUrl(buff, log):
  # variable for result
  ret = None
  resUrl = ''

  match = re.search(META_REDIRECT, stripHTMLComments(buff), re.I | re.U)
  if match is not None:
    resUrl = match.groups()[0].strip()

  log.debug('resUrl: ' + str(resUrl))
  urlObj = Url(resUrl)
  if urlObj.isValid():
    ret = resUrl

  log.debug('ret: ' + str(ret))

  return ret


# # function parse incoming email adress
# @param href - incoming email href
# @param onlyName - extract email names instead full email names
# @param defaultSeparator - default separator between email elements
# @return parsed email
def emailParse(href, onlyName=False, defaultSeparator=' '):  # pylint: disable=W0613
  ret = href
  splitHref = href.split('?')
  if splitHref is not None and len(splitHref) > 0:
    adresses = splitHref[0]
    adresses = adresses.split(',')
    if onlyName:
      names = []
      for adress in adresses:
        adress = adress.split('@')
        if adress is not None and len(adress) > 0:
          names.append(adress[0])
      adresses = names
    ret = ''
    for adress in adresses:
      ret += adress
      ret += ' '
    ret = ret.strip()
  return ret



# #Multi process logger
#
class MPLogger(object):

  ROTATED_ATTRIBUTE_NAME = '__rotated'

  # #initialization
  #
  def __init__(self):
    super(MPLogger, self).__init__()
    self.fnameOld = ''


# #rotation log files of logger
  #
  # @param loggerName - name of logger
  # @return - None
  def getLogger(self, loggerName=None, fileNameSuffix='', restore=False):
    if loggerName is None:
      ln = APP_CONSTS.LOGGER_NAME
    else:
      ln = loggerName

    if fileNameSuffix != '' or restore is True:
      rollover = False
    else:
      rollover = True

    try:
      # Get regular logger
      lg = logging.getLogger(ln)
      # Replace logger name for processes instances
      lfn = LoggerFileName(lg)
      fname = lfn.findReplace()
      if fname is not None and fname != '':
        if restore is False:
          if not hasattr(lg, self.ROTATED_ATTRIBUTE_NAME) or not getattr(lg, self.ROTATED_ATTRIBUTE_NAME):
            self.fnameOld = fname
            fname += fileNameSuffix
            pin = lfn.getFreeProcInstanceNumber(os.path.basename(fname))
            if pin != '' and ((pin != '0' and fileNameSuffix == '') or (pin == '0' and fileNameSuffix != '')):
              pin = '.' + pin + '.log'
              fname = lfn.findReplace(fname + pin, rollover=rollover)
              setattr(lg, self.ROTATED_ATTRIBUTE_NAME, True)
              lg = logging.getLogger(ln)
              setattr(lg, self.ROTATED_ATTRIBUTE_NAME, True)
        else:
          if self.fnameOld != '':
            fname = lfn.findReplace(self.fnameOld, rollover=rollover)
            lg = logging.getLogger(ln)
      return lg
    except Exception, err:
      raise Exception('Logger initialization error:' + str(err) + "\n" + getTracebackInfo())


def strToUnicode(inputStr):
  ret = inputStr

  if isinstance(inputStr, str):
    ret = inputStr.decode('utf-8')

  return ret


# Split string removes duplicated peaces and joing back
# @param inStr - input string
# @param delimiter - splitter delimiter
# @param joingGlue - optional glue string to joing with, if None or omitted - the delimiter used
# @param trimMode - peaces trim mode: 0 - not trimmed, 1 - trimmed left, 2 - trimmed right, 3 - trimmed both
# @return string with duplicated peaces removed
def removeDuplicated(inStr, delimiter="\n", joingGlue=None, trimMode=1, skipEmpty=False):
  ret = inStr.split(delimiter)

  if joingGlue is None:
    glue = delimiter
  else:
    glue = joingGlue

  prev = None
  new = []
  for item in ret:
    if trimMode > 0:
      if trimMode == 1:
        item = item.lstrip()
      elif trimMode == 2:
        item = item.rstrip()
      else:
        item = item.strip()
    if skipEmpty and item == '':
      continue
    if item != prev:
      new.append(item)
    prev = item
  ret = new

  return glue.join(ret).strip()


# Checks is the input content possible contains an CSS markup, possible is an in-line STYLE tag innerHTML
#
# @param content - to analyse
# @return zero if presence of the CSS markup is not detected or number of the detected fragments
def getContentCSSMarkupEntrancesNumber(content):
  return len(re.findall(r'\{.+?\}', content))


# Class ExceptionLog for logging of the exception common way
class ExceptionLog(object):

  # #Constans used in class
  LEVEL_NAME_ERROR = 'error'
  LEVEL_NAME_INFO = 'info'
  LEVEL_NAME_DEBUG = 'debug'

  LEVEL_VALUE_ERROR = logging.ERROR
  LEVEL_VALUE_INFO = logging.INFO
  LEVEL_VALUE_DEBUG = logging.DEBUG

  # #Constructor
  #
  # @param log - logger instance
  # @param error - Exception inherited object instance
  # @param message - error message string
  # @param objects - objects tuple to dump
  def __init__(self, log, error, message, objects):
    super(ExceptionLog, self).__init__()
    self.logger = log
    self.error = error
    self.message = message
    self.objects = objects


  # # Static handler for logging of the exception
  #
  # @param log - logger instance
  # @param error - Exception inherited object instance
  # @param message - error message string
  # @param objects - objects tuple to dump
  @staticmethod
  def handler(log, error, message, objects=(), levels={}):  # pylint: disable=W0102
    # dictionary with default values
    levelsDict = { \
                  ExceptionLog.LEVEL_NAME_ERROR:ExceptionLog.LEVEL_VALUE_ERROR, \
                  ExceptionLog.LEVEL_NAME_INFO:ExceptionLog.LEVEL_VALUE_INFO, \
                  ExceptionLog.LEVEL_NAME_DEBUG:ExceptionLog.LEVEL_VALUE_DEBUG \
                 }

    # filling levelDict necessary log level values
    for name, level in levels.items():
      if levelsDict.has_key(name):
        levelsDict[name] = level

    errorMsg = ''
    try:
      if isinstance(str(error), str) or isinstance(str(error), unicode):
        errorMsg = str(error)
    except Exception, err:
      log.log(levelsDict[ExceptionLog.LEVEL_NAME_DEBUG], 'Try make str(err) return error: ' + str(err))

    # Log the error message and Exception object with the ERROR level
    log.log(levelsDict[ExceptionLog.LEVEL_NAME_ERROR], message + ' ' + errorMsg)

    # Log the traceback with INFO level.
    log.log(levelsDict[ExceptionLog.LEVEL_NAME_INFO], getTracebackInfo())

    # Log the objects dumps with DEBUG level.
    if isinstance(objects, tuple):
      for obj in objects:
        log.log(levelsDict[ExceptionLog.LEVEL_NAME_DEBUG], varDump(obj))


  # # Dump log of the exception
  #
  # @param - None
  # @return - None
  def dump(self):
    ExceptionLog.handler(self.logger, self.error, self.message, self.objects)


class InterruptableThread(threading.Thread):
  ERROR_CODE_OK = 0
  ERROR_CODE_GENERAL_EXCEPTION = 1
  ERROR_CODE_APPLIED_EXCEPTION = 2

  def __init__(self, func, args, kwargs, default, log):
    threading.Thread.__init__(self)
    self.function = func
    self.args = args
    self.kwargs = kwargs
    self.result = default
    self.logger = log
    self.errorCode = self.ERROR_CODE_OK
    self.errorMessage = ''
    self.errorException = Exception('Dummy exception')
  def run(self):
    try:
      self.result = self.function(*self.args, **self.kwargs)
    except Exception, err:
      if self.logger is not None:
        self.logger.error("Error of execution of thread class InterruptableThread(): %s\nargs: %s",
                          str(err), str(self.args))
      self.errorCode = self.ERROR_CODE_APPLIED_EXCEPTION
      self.errorMessage = str(err)
      self.errorException = err
      raise err
    except:
      self.errorCode = self.ERROR_CODE_GENERAL_EXCEPTION
      self.errorMessage = 'Undefined error of execution of thread class InterruptableThread(), args: ' + str(self.args)
      if self.logger is not None:
        self.logger.error(self.errorMessage)


# #The function to execute another function in a thread with limited time to run
#
# @param func to execute
# @param args
# @param kwargs
# @param timeout - limit of execution time floating point, sec
# @param default - value to return if execution time limit reached
# @ret return value or default value
def executeWithTimeout(func, args=None, kwargs=None, timeout=1, default=None, log=None):
  if args is None:
    args = ()
  # import threading
  if kwargs is None:
    kwargs = {}

  it = InterruptableThread(func, args, kwargs, default, log)
  it.start()
  it.join(timeout)
  if it.isAlive():
    try:
      it._Thread__stop()  # pylint: disable=W0212
      time.sleep(1)
    except:
      if log is not None:
        log.error("an not stop thread with _Thread__stop()!")
    if it.isAlive():
      try:
        it.__stop()  # pylint: disable=W0212
        time.sleep(1)
      except:
        if log is not None:
          log.error("Can not stop thread with __stop()!")
      if it.isAlive():
        try:
          it._Thread__delete()  # pylint: disable=W0212
          time.sleep(1)
        except:
          if log is not None:
            log.error("Can not stop thread with _Thread__delete()!")

    if it.errorCode == it.ERROR_CODE_APPLIED_EXCEPTION:
      if log is not None:
        log.error("Error1 code %s, exception: %s", str(it.errorCode), str(it.errorException))
      raise it.errorException
    return default
  else:
    if it.errorCode == it.ERROR_CODE_APPLIED_EXCEPTION:
      if log is not None:
        log.error("Error2 code %s, exception: %s", str(it.errorCode), str(it.errorException))
      raise it.errorException
    return it.result


# #Load file data by protocoled reference
#
# @param initString string in json format or @file:// reference
# @param protocolPrefix
# @param loggerObj
# @return initString unchanged, value from file loaded by link or empty string if load error
def loadFromFileByReference(fileReference, initString=None, protocolPrefix='file://', loggerObj=None):
  ret = initString

  if fileReference.startswith(protocolPrefix):
    try:
      f = fileReference[len(protocolPrefix):]
      ret = readFile(f)
    except Exception, err:
      if loggerObj is not None:
        loggerObj.error("Error load from file `%s` by reference: %s", f, str(err))

  return ret


# #Read file
#
# @param inFile - name of file to read
# @param decodeUTF8 - decode utf8 or not after read from file
# @return - the buffer
def readFile(inFile, decodeUTF8=True):
  with open(inFile, 'r') as f:
    ret = f.read()

  if decodeUTF8:
    ret = ret.decode('utf8')

  return ret


# #Escape string value
#
# @param string
# @return escaped string
def escape(string):
  return string.replace("\\", "\\\\").replace('"', '\\\"').replace("'", "\\\'").replace("\n", "\\n").\
    replace("\r", "\\r").replace("\0", "\\0")


# #Validate URL string
#
# @param url - url string
# @return True if valid or otherwise False
def isValidURL(url):
  return False if isinstance(validators.url(url), validators.ValidationFailure) else True


# #Get some hash of a string limited bit size
#
# @param strBuf - string buffer
# @param binSize - binary value size bits, supported values 32, 64 and 128
# @param digestType - 0 - md5, 1 - sha1
# @param fixedMode - 0 digests play, 1 - crc32 to uint32, 2 - crc32 to ulong
# @param valLimit - limit of a value useful to fix a DB type size (MySQL 8 bytes BIGINT(20))
# @return True if valid or otherwise False
def getHash(strBuf, binSize=32, digestType=0, fixedMode=0, valLimit=18446744073709552000L):

  if fixedMode == 0:
    if digestType == 0:
      d = hashlib.md5(strBuf)
    else:
      d = hashlib.sha1(strBuf)  # pylint: disable=R0204
    if binSize == 32:
      s = 8
    elif binSize == 64:
      s = 16
    else:
      s = 32
    h = d.hexdigest()
    v = int(h[:s], 16)
    if v > valLimit:
      for i in xrange(1, s - 1):
        v = int(h[:s - i], 16)
        if v < valLimit:
          break
  elif fixedMode == 1:
    v = ctypes.c_uint32(zlib.crc32(strBuf, int(time.time()))).value
  else:
    v = ctypes.c_ulong(zlib.crc32(strBuf, int(time.time()))).value

  return v


# # Convert string to float
# @param val - input value as string
# @param defaultValue - default value for result
# @param log - logger instance
# @param positivePrefixes - positive prefixes dictionary
# @return result float value
def strToFloat(val, defaultValue=0.0, log=None, positivePrefixes=None):
  # variable for result
  ret = defaultValue
  if positivePrefixes is None:
    posPrefixes = {'K':'1E3', 'M':'1E6', 'G':'1E9', 'T':'1E12', 'P':'1E15', 'E':'1E18', 'Z':'1E21', 'Y':'1E24'}
  else:
    posPrefixes = positivePrefixes

  try:
    val = val.upper()
    if val[-1] in posPrefixes.keys():
      v = Decimal(val[:-1])
      ret = float(v * Decimal(posPrefixes[val[-1]]))
    else:
      ret = float(val)
  except Exception, err:
    if log is not None:
      log.debug(str(err))

  return ret


# #Convert string to proxy tuple (proxy_type, proxy_host, proxy_port, proxy_user, proxy_passwd)
#
# @param proxyString - proxy string
# @param log - logger instance
# @return proxy tuple if success or None otherwise
def strToProxy(proxyString, log=None, defaultProxyType='http'):
  # variables for result
  ret = None
  proxy_type = proxy_host = proxy_port = proxy_user = proxy_passwd = None
  if isinstance(proxyString, basestring) and proxyString != "":
    try:
      pattern = '(.*)://(.*):(.*)@(.*):(.*)'
      match = re.search(pattern, proxyString, re.I + re.U)
      if match is not None:
        proxy_type, proxy_user, proxy_passwd, proxy_host, proxy_port = match.groups()

      else:
        pattern = '(.*)://(.*):(.*)'
        match = re.search(pattern, proxyString, re.I + re.U)
        if match is not None:
          proxy_type, proxy_host, proxy_port = match.groups()
        else:
          pattern = '(.*):(.*)'
          match = re.search(pattern, proxyString, re.I + re.U)
          if match is not None:
            proxy_host, proxy_port = match.groups()
            proxy_type = defaultProxyType

      ret = (proxy_type, proxy_host, proxy_port, proxy_user, proxy_passwd)
    except Exception, err:
      if log is not None:
        log.error("Error: %s", str(err))

  return ret


# # execute command line command
#
# @param cmd - command line string
# @param inputStream - input stream to popen
# @param log - logger instance
# @return result named tuple with support names: 'stdout', 'stderr', 'exitCode'
def executeCommand(cmd, inputStream='', log=None):
  # variables for result tuple
  output = ''
  errMsg = ''
  exitCode = APP_CONSTS.EXIT_FAILURE
  try:
    if log is not None:
      log.debug("Popen: %s", str(cmd))

    process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True, executable='/bin/bash')
    if log is not None:
      log.debug("len(inputStream)= %s", str(len(inputStream)))

    (output, errMsg) = process.communicate(input=inputStream)
    exitCode = process.wait()

    if log is not None:
      log.debug("Process response has exitCode = %s, stdout len = %s, stderr: %s",
                str(exitCode), str(len(output)), str(errMsg))

  except Exception, err:
    if log is not None:
      log.error("Popen execution error: %s", str(err))

  # make result tuple
  PopenResult = collections.namedtuple('PopenResult', ['stdout', 'stderr', 'exitCode'])
  popenResult = PopenResult(stdout=output, stderr=errMsg, exitCode=exitCode)

  return popenResult


# # Parse json and return dict if okay or None if not
#
# @param jsonString json to pars
# @param log - logger instance
# @return resulted dict
def jsonLoadsSafe(jsonString, default=None, log=None):
  # variable for result
  ret = default
  try:
    if jsonString is not None and jsonString != '':
      if isinstance(jsonString, basestring):
        ret = json.loads(jsonString)
      else:
        ret = jsonString
        if log is not None:
          log.debug("Input object type is: %s", type(jsonString))
  except Exception, err:
    if log is not None:
      log.error("Error pars json: %s; source string:\n%s", str(err), jsonString)

  return ret


# simple re match check for search word definition
#
# @param word - word for search
# @param buff - buffer where is search
# @param log - logger instance
# @return True if match exist or False otherwise
def reMatch(word, buff, log=None):
  # variable for result
  ret = False
  if isinstance(word, basestring) and isinstance(buff, basestring):
    try:
      if word.startswith(u'/'):
        word = word[1:]
        if re.search(pattern=word, string=buff, flags=re.U + re.I + re.M) is not None:
          ret = True
      else:
        ret = (word.upper() == buff.upper())
  
    except Exception, err:
      if log is not None:
        log.error("Expression: %s, Error: %s", str(word), str(err))

  return ret
