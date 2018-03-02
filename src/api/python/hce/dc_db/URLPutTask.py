'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import base64
import dc.EventObjects
import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
from dc_db.URLCleanupTask import URLCleanUpTask
from app.Utils import ExceptionLog
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #process URLPutTask event
class URLPutTask(BaseTask):


  # #constructor
  #
  # @param dBDataTask instance of DBDataTask module
  def __init__(self, keyValueStorageDir, rawDataDir, dBDataTask):
    super(URLPutTask, self).__init__()
    self.uRLCleanUpTask = URLCleanUpTask(keyValueStorageDir, rawDataDir, dBDataTask)
    self.dBDataTask = dBDataTask


  # #make all necessary actions to get urls content data from storages
  #
  # @param urlPuts list of URLPut objects
  # @param queryCallback function for queries execution
  # @return list of urlPutResponses objects
  def process(self, urlPuts, queryCallback):  # pylint: disable=W0613
    urlPutResponses = []
    for urlPut in urlPuts:
      urlsCount = 0
      localMd5s = []
      if urlPut.urlMd5 is None:
        logger.debug(">>> urlPuts.urlMd5 is None, fetch by criterions")
        localMd5s = self.uRLCleanUpTask.extractUrlByCriterions(urlPuts.siteId, False, urlPuts.criterions,
                                                               queryCallback, Constants.SECONDARY_DB_ID)
      else:
        localMd5s.append(urlPut.urlMd5)
      logger.debug(">>> [URL_PUT] localUrls size = " + str(len(localMd5s)))

      if "data" in urlPut.putDict and urlPut.contentType != dc.EventObjects.Content.CONTENT_PROCESSOR_CONTENT:
        try:
          urlPut.putDict["data"] = base64.b64decode(urlPut.putDict["data"])
        except TypeError:
          pass
      for localMd5 in localMd5s:
        try:
          urlPut.urlMd5 = localMd5
          urlPutResponses.append(self.dBDataTask.process(urlPut, queryCallback))
          urlsCount = urlsCount + 1
        except Exception as err:
          ExceptionLog.handler(logger, err, ">>> [URL_PUT] Exception:")
          logger.debug(">>> [URL_PUT] Some Type Exception [LOOP] = " + str(type(err)))

    return urlPutResponses
