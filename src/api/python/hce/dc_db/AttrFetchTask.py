'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc.EventObjects
import dc_db.Constants as Constants
from dc_db.BaseTask import BaseTask
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # AttrFetchTask Class, implements AttributeFetch task functionality
#
class AttrFetchTask(BaseTask):

  ATTR_FETCH_TEMPLATE = "SELECT * FROM `%s` "

  # #Class constructor
  #
  def __init__(self):
    super(AttrFetchTask, self).__init__()


  # #make all necessary actions to fetch attributes from db
  #
  # @param attrFetches list of AttrFetche objects
  # @param queryCallback function for queries execution
  # @return list ofAttribute objects
  def process(self, attrFetches, queryCallback):
    ret = []
    for attrFetch in attrFetches:
      if self.isSiteExist(attrFetch.siteId, queryCallback):
        try:
          additionWhere = None
          if attrFetch.name is None:
            additionWhere = self.generateCriterionSQL(attrFetch.criterions)
          else:
            additionWhere = ("WHERE `Name` = '%s'" % attrFetch.name)

          if additionWhere == "":
            additionWhere = "WHERE 1=1"

          if attrFetch.urlMd5 is not None:
            additionWhere += (" AND `URLMd5` = '%s'" % attrFetch.urlMd5)

          logger.debug(">>> additionWhere = " + str(additionWhere))
          if additionWhere is not None and len(additionWhere) > 0:
            query = AttrFetchTask.ATTR_FETCH_TEMPLATE % (Constants.DC_ATT_TABLE_NAME_TEMPLATE % attrFetch.siteId)
            res = queryCallback(query + additionWhere, Constants.ATT_DB_ID, Constants.EXEC_NAME)
            if res is not None and len(res) > 0:
              for elem in res:
                attribute = dc.EventObjects.Attribute(attrFetch.siteId, elem["Name"])
                attribute.urlMd5 = elem["URLMd5"]
                attribute.value = elem["Value"]
                attribute.cDate = elem["CDate"]
                ret.append(attribute)
        except Exception as excp:
          logger.debug(">>> [AttributeFetch] Some Exception = " + str(type(excp)) + " " + str(excp))

    return ret


  # #fetchUrlsAttributes static method, fetches and returns attributes by urlMd5
  #
  # @param siteId - incoming siteId
  # @param urlMd5 - incoming urlMd5
  # @param queryCallback - function for queries execution
  # @return list ofAttribute objects
  @staticmethod
  def fetchUrlsAttributes(siteId, urlMd5, queryCallback):
    attrFetchTask = AttrFetchTask()
    attrFetches = [dc.EventObjects.AttributeFetch(siteId, None, {"WHERE": ("`URLMd5` = '%s'" % urlMd5)})]
    return attrFetchTask.process(attrFetches, queryCallback)


  # #fetchUrlsAttributesByNames static method, fetches and returns attributes by urlMd5 and attribute names
  #
  # @param siteId - incoming siteId
  # @param urlMd5 - incoming urlMd5
  # @param queryCallback - function for queries execution
  # @param attributeNames - attribute names list
  # @return list ofAttribute objects
  @staticmethod
  def fetchUrlsAttributesByNames(siteId, urlMd5, queryCallback, attributeNames):
    # variable for result
    ret = []
    # get full attributes list
    attributes = AttrFetchTask.fetchUrlsAttributes(siteId, urlMd5, queryCallback)
    if isinstance(attributeNames, list):
      # default behavior (return all attributes)
      if '*' in attributeNames:
        ret = attributes
      # search name form list
      else:
        localAttributes = []
        for attribute in attributes:
          if attribute.name in attributeNames:
            localAttributes.append(attribute)
        # save attributes list
        ret = localAttributes

    return ret
