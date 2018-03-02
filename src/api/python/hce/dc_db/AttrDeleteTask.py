'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc.EventObjects
from dtm.EventObjects import GeneralResponse
from dc_db.BaseTask import BaseTask
import dc_db.Constants as Constants
from app.Utils import varDump
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


# # AttrDeleteTask Class, implements AttributeDelete task functionality
#
class AttrDeleteTask(BaseTask):


  ATTR_DELETE_TEMPLATE = "DELETE FROM `%s` "


  # #Class constructor
  #
  def __init__(self):
    super(AttrDeleteTask, self).__init__()


  # #make all necessary actions to delete attributes data from db
  #
  # @param urlDeletes list of AttrDelete objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, attrDeletes, queryCallback):
    ret = GeneralResponse()
    for attrDelete in attrDeletes:
      if self.isSiteExist(attrDelete.siteId, queryCallback):
        try:
          additionWhere = None
          if attrDelete.name is None:
            additionWhere = self.generateCriterionSQL(attrDelete.criterions)
          else:
            additionWhere = ("WHERE `Name` = '%s'" % attrDelete.name)
            
          if additionWhere == "":
            additionWhere = "WHERE 1=1"

          if attrDelete.urlMd5 is not None:
            additionWhere += (" AND `URLMd5` = '%s'" % attrDelete.urlMd5)
            
          logger.debug(">>> additionWhere = " + str(additionWhere))
          if additionWhere is not None and len(additionWhere) > 0:
            query = AttrDeleteTask.ATTR_DELETE_TEMPLATE % ((Constants.DC_ATT_TABLE_NAME_TEMPLATE % attrDelete.siteId))
            queryCallback(query + additionWhere, Constants.ATT_DB_ID)
            ret.statuses.append(True)
          else:
            ret.statuses.append(False)
        except Exception as excp:
          logger.debug(">>> [AttributeDelete] Some Exception = " + str(type(excp)) + " " + str(excp))
          ret.statuses.append(False)
      else:
        ret.statuses.append(False)
    return ret


  # #fetchUrlsAttributes static method, fetches and returns attributes by urlMd5
  #
  # @param siteId incoming siteId
  # @param urlMd5 incoming urlMd5
  # @param queryCallback function for queries execution
  @staticmethod
  def deleteUrlsAttributes(siteId, urlMd5, queryCallback):
    attrDeleteTask = AttrDeleteTask()
    attrDeletes = [dc.EventObjects.AttributeDelete(siteId, None, {"WHERE": ("`URLMd5` = '%s'" % urlMd5)})]
    res = attrDeleteTask.process(attrDeletes, queryCallback)
    logger.debug(">>> AttrDeleteTask.deleteUrlsAttributes operation result = " + varDump(res))
