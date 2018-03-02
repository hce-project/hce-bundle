# coding: utf-8
"""
HCE project,  Python bindings, Distributed Tasks Manager application.
FetcherPost Class content main functional of post process after fetching procedure.

@package: dc_crawler
@file FetcherPost.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2018 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import os
import re

from dc_crawler.Fetcher import Response


class FetcherPost(object):
  # # Constants error messages used in class
  MSG_ERROR_FETCHER_POST_PROCESSING_SKIPPED = "FetcherPost processing skipped. Reason: %s"
  MSG_ERROR_PROCESSING_ID_COLLECT_SKIPPED = "Processing ID collect skipped. Reason: %s"

  MSG_ERROR_WRONG_PROPERTY = "Wrong type of the input property: %s"
  MSG_ERROR_WRONG_PARAMETERS = "Wrong type of the input parameter: %s"
  MSG_ERROR_NOT_FOUND_FILE_NAME = "Not found file name option for the result pages file."
  MSG_ERROR_GET_DOMAIN = "Get domain failed. Possible you used wrong protocol."

  # # Constants used in class
  PROPERTY_OPTION_ID_COLLECT_NAME = 'fb_pages_id_collect'
  PROPERTY_OPTION_DATA_SCRAPING_NAME = 'fb_pages_data_scraping'
  PROPERTY_OPTION_PAGES_FILE = 'pages_file'

  PATTERNS_FOR_ID_COLLECT = ['fb://page/(\d+)', 'fb://page/\?id=(\d+)']


  # # Initialization
  #
  # @param properties - properties dictionary
  # @param log - logger instance
  def __init__(self, properties, log):
    self.properties = properties
    self.logger = log
    self.data = None


  # # Process execution method
  #
  # @param response - Response class instance
  # @return - None
  def process(self, response):
    try:
      if not isinstance(self.properties, dict):
        raise Exception(self.MSG_ERROR_WRONG_PROPERTY % str(type(self.properties)))

      if not isinstance(response, Response):
        raise Exception(self.MSG_ERROR_WRONG_PARAMETERS % str(type(self.properties)))

      # execution some post procedures if necessary
      if self.PROPERTY_OPTION_ID_COLLECT_NAME in self.properties and int(self.properties[self.PROPERTY_OPTION_ID_COLLECT_NAME])>0:
        self.logger.debug("Found active option '%s'.", str(self.PROPERTY_OPTION_ID_COLLECT_NAME))
        self.processIdCollect(response)

      if self.PROPERTY_OPTION_DATA_SCRAPING_NAME in self.properties and int(self.properties[self.PROPERTY_OPTION_DATA_SCRAPING_NAME]) > 0:
        self.logger.debug("Found active option '%s'.", str(self.PROPERTY_OPTION_DATA_SCRAPING_NAME))
        self.processDataScraping(response)

    except Exception, err:
      self.logger.error(self.MSG_ERROR_FETCHER_POST_PROCESSING_SKIPPED, str(err))


  # # Process ID collect
  #
  # @param response - Response class instance
  # @return - None
  def processIdCollect(self, response):
    try:
      if self.PROPERTY_OPTION_PAGES_FILE not in self.properties or self.properties[self.PROPERTY_OPTION_PAGES_FILE] == "":
        raise Exception(self.MSG_ERROR_NOT_FOUND_FILE_NAME)

      if isinstance(response.page_source, basestring):
        for pattern in self.PATTERNS_FOR_ID_COLLECT:
          matches = re.findall(pattern=pattern, string=response.page_source, flags=re.U + re.I + re.M)
          if len(matches) > 0:
            self.logger.debug("Found Id '%s' by pattern '%s'", str(matches[0]), str(pattern))
            self.saveToFile(matches[0], response.url, self.properties[self.PROPERTY_OPTION_PAGES_FILE])
            break
          
    except Exception, err:
      self.logger.error(self.MSG_ERROR_PROCESSING_ID_COLLECT_SKIPPED, str(err))


  def getDomain(self):
    # variable for result
    ret = None

    if isinstance(self.data, dict) and 'options' in self.data and isinstance(self.data['options'], dict) and 'currentDataMd5' in self.data['options']:
      currentDataMd5 = self.data['options']['currentDataMd5']
      self.logger.debug("currentDataMd5: %s", str(currentDataMd5))
      if 'data' in self.data and currentDataMd5 in self.data['data'] and isinstance(self.data['data'][currentDataMd5], dict) and \
        'domain' in self.data['data'][currentDataMd5]:
        ret = self.data['data'][currentDataMd5]['domain']
        self.logger.debug("domain: %s", str(ret))

    return ret


  ## save ID to file
  #
  # @param id - ID for saving
  # @param url - url of media page
  # @param fileName - file name
  def saveToFile(self, id, url, fileName):
    domain = self.getDomain()
    if domain is None:
      raise Exception(self.MSG_ERROR_GET_DOMAIN)
    else:
      msg = "%s, %s, %s\n" % (str(domain), str(url), str(id))
      mode = 'a' if os.path.isfile(fileName) else 'w'
      with open(fileName, mode) as f:
        f.write(msg)


  # # Process data scraping
  #
  # @param response - Response class instance
  # @return - None
  def processDataScraping(self, response):
    pass

