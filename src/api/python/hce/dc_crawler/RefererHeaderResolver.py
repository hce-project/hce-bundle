"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file RefererHeaderResolver.py
@author scorp <developers.hce@gmail.com>
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import app.Utils as Utils  # pylint: disable=F0401
import dc.EventObjects
import dc.Constants as DC_CONSTS

logger = Utils.MPLogger().getLogger()


# #RefererHeaderResolver class calculate "Referer" fields value and add it to the headers
#
class RefererHeaderResolver(object):

  MODE_NONE = 0
  MODE_SIMPLE = 1
  MODE_DOMAIN = 2
  MODE_PARENT = 3
  HEADER_NAME = "Referer"


  def __init__(self, dbWrapper=None):
    self.dbWrapper = dbWrapper


  # #fetchParentUrl fetchs parent url from db
  #
  # @param siteId current resource's siteId
  # @param parentMd5 current resource's parentMd5
  # @param dbWrapper db-task wrapper
  def fetchParentUrl(self, siteId, parentMd5, dbWrapper):
    ret = None
    if siteId is not None and parentMd5 is not None and dbWrapper is not None:
      urlStatus = dc.EventObjects.URLStatus(siteId, parentMd5)
      urlStatus.urlType = dc.EventObjects.URLStatus.URL_TYPE_MD5
      drceSyncTasksCoverObj = DC_CONSTS.DRCESyncTasksCover(DC_CONSTS.EVENT_TYPES.URL_STATUS, [urlStatus])
      responseDRCESyncTasksCover = dbWrapper.process(drceSyncTasksCoverObj)
      row = responseDRCESyncTasksCover.eventObject
      if row is not None and len(row) > 0 and row[0] is not None:
        ret = row[0].url
    return ret


  # #resolveRefererHeader public method, adds "Referer" header in the headers dics with correspond values
  #
  # @param headers incoming http headers dict
  # @param mode mode of "Referer" header value calculating
  # @param url current resource's url
  # @param siteId current resource's siteId
  # @param parentMd5 current resource's parentMd5
  # @param dbWrapper db-task wrapper
  def resolveRefererHeader(self, headers, mode, url, siteId=None, parentMd5=None, dbWrapper=None):
    mode = int(mode)

    for headerName in headers:
      if headerName.lower() == self.HEADER_NAME.lower():
        logger.info(">>> Referer field already in dict headers")
        return

    if mode == self.MODE_NONE:
      pass
    elif mode == self.MODE_SIMPLE:
      headers[self.HEADER_NAME] = url
    elif mode == self.MODE_DOMAIN:
      headers[self.HEADER_NAME] = Utils.UrlParser.generateDomainUrl(url)
    elif mode == self.MODE_PARENT:
      parentUrl = self.fetchParentUrl(siteId, parentMd5, dbWrapper if dbWrapper is not None else self.dbWrapper)
      headers[self.HEADER_NAME] = parentUrl if parentUrl is not None else url

