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
import dc_db.Constants as Constants
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

# # AttrSetTask Class, implements AttributeSet task functionality
#
class AttrSetTask(BaseTask):

  CODE_GOOD_INSERT = 0
  CODE_BAD_INSERT = 1
  CODE_ALREADY_EXIST = 2
  CODE_SITE_NOT_EXIST = 3

  # #Class constructor
  #
  def __init__(self):
    super(AttrSetTask, self).__init__()


  # #make all necessary actions to add new Attributes into mysql db
  #
  # @param attrs list of Attributes objects
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, attrs, queryCallback):
    ret = GeneralResponse()
    for attr in attrs:
      if self.isSiteExist(attr.siteId, queryCallback):
        if self.selectAttribute(attr, queryCallback):
          ret.statuses.append(AttrSetTask.CODE_ALREADY_EXIST)
          self.updateAttribute(attr, queryCallback)
        elif self.addAttribute(attr, queryCallback):
          ret.statuses.append(AttrSetTask.CODE_GOOD_INSERT)
        else:
          ret.statuses.append(AttrSetTask.CODE_BAD_INSERT)
      else:
        ret.statuses.append(AttrSetTask.CODE_SITE_NOT_EXIST)
    return ret


  # #select attribute
  #
  # @param attrObject instance of Attribute object
  # @param queryCallback function for queries execution
  def selectAttribute(self, attrObject, queryCallback):
    ret = False
    LOCAL_URL_CHECK_QUERY = "SELECT COUNT(*) FROM `att_%s` WHERE `Name` = '%s'"

    if attrObject.urlMd5 is None:
      query = LOCAL_URL_CHECK_QUERY % (attrObject.siteId, attrObject.name)
    else:
      LOCAL_URL_CHECK_QUERY += " AND `URLMd5` = '%s'"
      query = LOCAL_URL_CHECK_QUERY % (attrObject.siteId, attrObject.name, attrObject.urlMd5)

    logger.debug("!!! query: %s", str(query))
    res = queryCallback(query, Constants.ATT_DB_ID)
    logger.debug("!!! res: %s", Utils.varDump(res))

    if hasattr(res, '__iter__') and len(res) > 0 and len(res[0]) > 0 and res[0][0] > 0:
      ret = True

    return ret


  # #inserts new attribute
  #
  # @param attrObject instance of Attribute object
  # @param queryCallback function for queries execution
  def addAttribute(self, attrObject, queryCallback):
    ret = False
    fields, values = Constants.getFieldsValuesTuple(attrObject, Constants.AttrTableDict)
    fieldValueString = Constants.createFieldsValuesString(fields, values)
    if fieldValueString is not None and fieldValueString != "":
      query = Constants.INSERT_COMMON_TEMPLATE % ((Constants.DC_ATT_TABLE_NAME_TEMPLATE % attrObject.siteId),
                                                  fieldValueString)
      queryCallback(query, Constants.ATT_DB_ID, Constants.EXEC_NAME, True)
      ret = True

    return ret


  # # Update already exists attributes
  #
  # @param attrObject instance of Attribute object
  # @param queryCallback function for queries execution
  def updateAttribute(self, attrObject, queryCallback):
    UPDATE_TEMPLATE = "UPDATE `att_%s` SET `Value` = '%s' WHERE `Name` = '%s' AND `URLMd5` = '%s'"
    query = UPDATE_TEMPLATE % (attrObject.siteId, Utils.escape(attrObject.value), attrObject.name,
                               attrObject.urlMd5 if attrObject.urlMd5 is not None else "")
    queryCallback(query, Constants.ATT_DB_ID, Constants.EXEC_NAME, True)
