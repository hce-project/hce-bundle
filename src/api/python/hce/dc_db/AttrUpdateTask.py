'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

from dtm.EventObjects import GeneralResponse
from dc_db.BaseTask import BaseTask
from dc_db.AttrSetTask import AttrSetTask
import dc_db.Constants as Constants
import dc.EventObjects
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# # AttrSetTask Class, implements AttributeSet task functionality
#
class AttrUpdateTask(BaseTask):


  # #Class constructor
  #
  def __init__(self):
    super(AttrUpdateTask, self).__init__()
    self.arrtSet = AttrSetTask()


  # #make all necessary actions to get update attributes data in db
  #
  # @param attrUpdates list of AttributeUpdate objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, attrUpdates, queryCallback):
    ret = GeneralResponse()
    for attrUpdate in attrUpdates:
      statusValue = False
      if self.isSiteExist(attrUpdate.siteId, queryCallback):
        if self.arrtSet.selectAttribute(attrUpdate, queryCallback):
          self.updateAttribute(attrUpdate, queryCallback)
          statusValue = True
        else:
          localAttribute = dc.EventObjects.Attribute(attrUpdate.siteId, attrUpdate.name)
          localAttribute.urlMd5 = attrUpdate.urlMd5 if attrUpdate.urlMd5 is not None else ""
          localAttribute.value = attrUpdate.value if attrUpdate.value is not None else ""
          localRet = self.arrtSet.process([localAttribute], queryCallback)
          if len(localRet.statuses) > 0 and localRet.statuses[0] == AttrSetTask.CODE_GOOD_INSERT:
            statusValue = True
      ret.statuses.append(statusValue)
    return ret


 # # Update already exists attributes
  #
  # @param attrObject instance of Attribute object
  # @param queryCallback function for queries execution
  def updateAttribute(self, attrObject, queryCallback):
    
    UPDATE_TEMPLATE = "UPDATE `att_%s` SET `Value` = '%s' WHERE `Name` = '%s'"
    
    if attrObject.urlMd5 is None:
      query = UPDATE_TEMPLATE % (attrObject.siteId, Utils.escape(attrObject.value), attrObject.name)
    else:
      UPDATE_TEMPLATE +=  "AND `URLMd5` = '%s'"
      query = UPDATE_TEMPLATE % (attrObject.siteId, Utils.escape(attrObject.value), attrObject.name, attrObject.urlMd5)

    logger.debug("!!! query: %s", str(query))
    queryCallback(query, Constants.ATT_DB_ID, Constants.EXEC_NAME, True)




