'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import hashlib
import dc.EventObjects
from dc_db.BaseTask import BaseTask
from dc_db.URLFetchTask import URLFetchTask
import dc_db.Constants as Constants
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# #process urlFetch event
class URLVerifyTask(BaseTask):


  # #make all necessary actions to url verifieng
  #
  # @param urlVerifies list of URLVerify objects
  # @param queryCallback function for queries execution
  # @param bdResolveFunc pointer to resolve DB external function
  # @return list of URL objects
  def process(self, urlVerifies, queryCallback, bdResolveFunc):
    urls = []
    for urlVerify in urlVerifies:
      urls.append(self.fetchUrl(urlVerify, queryCallback, bdResolveFunc))
    return urls


  # #Verify current url in DB
  #
  # @param urlVerify instance of URLVerify object
  # @param queryCallback function for queries execution
  # @param bdResolveFunc pointer to resolve DB external function
  # @return list of URL objects
  def fetchUrl(self, urlVerify, queryCallback, bdResolveFunc):
    url = None
    if urlVerify.dbName is not None:
      dbIndex = bdResolveFunc(urlVerify.dbName)
      if dbIndex is not None:
        tableName = Constants.DC_URLS_TABLE_NAME_TEMPLATE % urlVerify.siteId
        query = Constants.SELECT_SQL_TEMPLATE_SIMPLE % ("*", tableName)
        if urlVerify.urlType == dc.EventObjects.URLStatus.URL_TYPE_URL:
          localUrlMd5 = hashlib.md5(urlVerify.url).hexdigest()
        else:
          localUrlMd5 = urlVerify.url
        additionWere = ("`UrlMd5`= '%s'" % localUrlMd5)
        if urlVerify.criterions is not None:
          additionQueryStr = self.generateCriterionSQL(urlVerify.criterions, additionWere)
        else:
          additionQueryStr = self.generateCriterionSQL({}, additionWere)
        if additionQueryStr is not None and len(additionQueryStr) > 0:
          query += " "
          query += additionQueryStr
        res = queryCallback(query, dbIndex, Constants.EXEC_NAME)
        if res is not None and len(res) > 0:
          url = URLFetchTask.fillUrlObj(res[0])
      else:
        logger.error("Error: there isn't %s database connection", str(url.dbName))
    return url
