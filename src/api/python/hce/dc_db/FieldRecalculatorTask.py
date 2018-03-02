'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import copy
from dc_db.BaseTask import BaseTask
from dc_db.FieldRecalculator import FieldRecalculator
from dtm.EventObjects import GeneralResponse  # pylint: disable=unused-import
import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()


# #class implemented all logic necessary to process SiteCleanUp request
#
class FieldRecalculatorTask(BaseTask):

  # #constructor
  #
  def __init__(self):
    super(FieldRecalculatorTask, self).__init__()
    self.recalculator = FieldRecalculator()


  # #make all necessary actions to update site into in mysql db
  #
  # @param siteRecalculatorObj instance of SiteRecalculatorObj object
  # @param queryCallback function for queries execution
  # @return generalResponse instance of GeneralResponse object
  def process(self, siteRecalculatorObjs, queryCallback):
    response = GeneralResponse()
    for siteRecalculatorObj in siteRecalculatorObjs:
      if hasattr(siteRecalculatorObj, "criterions") and siteRecalculatorObj.criterions is not None:
        siteIds = self.fetchByCriterions(siteRecalculatorObj.criterions, queryCallback)
        if siteIds is not None and hasattr(siteIds, '__iter__'):
          for siteId in siteIds:
            localSiteRecalculatorObj = copy.deepcopy(siteRecalculatorObj)
            localSiteRecalculatorObj.criterions = None
            localSiteRecalculatorObj.siteId = siteId
            siteRecalculatorObjs.append(localSiteRecalculatorObj)
    for siteRecalculatorObj in siteRecalculatorObjs:
      response.statuses.append(siteRecalculatorObj.siteId)
      self.recalculator.commonRecalc(siteRecalculatorObj.siteId, queryCallback, siteRecalculatorObj.recalcType)
    return response
