# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
LinkResolver is a module class and has a main functional for link resolve.

@package: dc_postprocessor
@file LinkResolver.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import re
import json
import base64
import requests
import requests.exceptions

from dc_postprocessor.PostProcessingModuleClass import PostProcessingModuleClass

# This object is a run at once module for link resolve
class LinkResolver(PostProcessingModuleClass):

  # # Constants for property 'LINK_RESOLVE'
  LINK_RESOLVE_PROPERTY_NAME = 'LINK_RESOLVE'

  # Constants used in class
  CONFIG_OPTION_METHOD = 'method'
  CONFIG_OPTION_DELIMITER = 'delimiter'
  CONFIG_OPTION_HEADER_FILE = 'headers_file'

  PROPERTY_NAME_METHOD = 'method'

  LINK_FIELD_NAME = 'link'
  SEARCH_PATTERN = 'redirect_url\".*href=\"(.*)\">'

  # Constants default values
  DEFAULT_VALUE_METHOD = 'HEAD'
  DEFAULT_VALUE_DELIMITER = ','

  # Constants of error messages
  ERROR_MSG_INITIALIZATION_CALLBACK = "Error initialization of callback function for get config options."
  ERROR_MSG_INITIALIZATION_LOGGER = "Error initialization of self.logger."
  ERROR_MSG_RESOLVE__REDIRECT_URL = "Resolve redirect url failed. Error: %s"
  ERROR_MSG_READ_HEADER = "Error read header file. File: '%s', error: '%s', line: '%s'"

  # Default initialization
  def __init__(self, getConfigOption=None, log=None):
    PostProcessingModuleClass.__init__(self, getConfigOption, log)

    self.method = self.DEFAULT_VALUE_METHOD
    self.delimiter = self.DEFAULT_VALUE_DELIMITER
    self.headers = None
    self.siteProperty = None


  # # initialization
  #
  # @param - None
  # @return - None
  def init(self):
    if self.getConfigOption is None:
      raise Exception(self.ERROR_MSG_INITIALIZATION_CALLBACK)

    if self.logger is None:
      raise Exception(self.ERROR_MSG_INITIALIZATION_LOGGER)

    self.method = self.getConfigOption(sectionName=self.__class__.__name__,
                                       optionName=self.CONFIG_OPTION_METHOD,
                                       defaultValue=self.DEFAULT_VALUE_METHOD)

    self.delimiter = self.getConfigOption(sectionName=self.__class__.__name__,
                                          optionName=self.CONFIG_OPTION_DELIMITER,
                                          defaultValue=self.DEFAULT_VALUE_DELIMITER)

    if self.delimiter == "":
      self.delimiter = self.DEFAULT_VALUE_DELIMITER

    self.headers = self.__readHeaderFile(self.getConfigOption(sectionName=self.__class__.__name__,
                                                              optionName=self.CONFIG_OPTION_HEADER_FILE))

#     self.logger.debug("Module parameters: method = '%s', delimiter = '%s', headers:\n%s",
#                       str(self.method), str(self.delimiter), varDump(self.headers))


  # # read headers file
  #
  # @param fileName - the file name to read
  # @return -None
  def __readHeaderFile(self, fileName):
    # variable for result
    ret = {}
    with open(fileName, 'r') as f:
      for header in ''.join(f.readlines()).splitlines():
        if not header:
          continue
        try:
          key, value = header[:header.index(':')].strip(), header[header.index(':') + len(':'):].strip()
        except Exception, err:
          self.logger.error(self.ERROR_MSG_READ_HEADER, str(fileName), str(err), header)

        if key[0] != '#':
          ret[key] = value

    return ret


  # # resolve redirect link
  #
  # @param url - url for resolve redirect
  # @return resolved link
  def resolve(self, url):
    # variable for result
    ret = url
    method = self.method

    try:
      if self.PROPERTY_NAME_METHOD in self.siteProperty:
        methods = self.siteProperty[self.PROPERTY_NAME_METHOD]
        for pattern, value in methods.items():
          if re.search(pattern, url, re.I + re.U) is not None:
            method = value
            break

      self.logger.debug("Apply method: '%s' for %s", str(method), str(url))

      req = requests.Request(method=method, url=url, headers=self.headers)
      r = req.prepare()
      s = requests.Session()
      res = s.send(r, allow_redirects=True)
      ret = res.request.url

      if res.content != "":
        match = re.search(self.SEARCH_PATTERN, res.content, re.I + re.U)
        if match is not None:
          ret = match.group(1)

    except requests.exceptions.RequestException, err:
      self.logger.error(self.ERROR_MSG_RESOLVE__REDIRECT_URL, str(err))
    except Exception, err:
      self.logger.error(self.ERROR_MSG_RESOLVE__REDIRECT_URL, str(err))

    return ret


  # # process batch item interface method
  #
  # @param batchItemObj - batch item instance
  # @return - None
  def processBatchItem(self, batchItem):

    if self.LINK_RESOLVE_PROPERTY_NAME in batchItem.properties:
      self.siteProperty = batchItem.properties[self.LINK_RESOLVE_PROPERTY_NAME]
      self.logger.debug("!!! self.siteProperty: %s, type: %s", str(self.siteProperty), str(type(self.siteProperty)))

      if batchItem.urlContentResponse is not None and isinstance(batchItem.urlContentResponse.processedContents, list):
        for index in xrange(len(batchItem.urlContentResponse.processedContents)):
          if isinstance(batchItem.urlContentResponse.processedContents[index], basestring) and \
            batchItem.urlContentResponse.processedContents[index] != "":
            # unpack processed content
            processedContent = json.loads(base64.b64decode(batchItem.urlContentResponse.processedContents[index]))

            # search and call resolve link method
            if self.LINK_FIELD_NAME in processedContent:
              links = processedContent[self.LINK_FIELD_NAME].split(self.delimiter)
              rlinks = []
              for link in links:
                rlinks.append(self.resolve(link))

              processedContent[self.LINK_FIELD_NAME] = self.delimiter.join(rlinks)
              # pack updated processed content
              batchItem.urlContentResponse.processedContents[index] = base64.b64encode(json.dumps(processedContent))

    return batchItem
