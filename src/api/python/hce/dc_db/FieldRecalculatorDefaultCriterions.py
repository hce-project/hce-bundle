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
import app.SQLCriterions
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


CRIT_RESOURCES = "COUNTER_CRIT_RESOURCES"
CRIT_CONTENTS = "COUNTER_CRIT_CONTENTS"
CRIT_CLURLS = "COUNTER_CRIT_CLURLS"
CRIT_NURLS = "COUNTER_CRIT_NURLS"
CRIT_DURLS = "COUNTER_CRIT_DURLS"
CRIT_CRURLS = "COUNTER_CRIT_CRURLS"
CRIT_PURLS = "COUNTER_CRIT_PURLS"
CRIT_ERRORS = "COUNTER_CRIT_ERRORS"

CRIT_CRAWLED_THIS_NODE = '( NOT (`Status`=' + str(dc.EventObjects.URL.STATUS_CRAWLED) + ' AND `Crawled`=0 ))'

DefaultRecalculatorCriterions = {CRIT_RESOURCES: {"WHERE": "`Status`=" + \
                                 str(dc.EventObjects.URL.STATUS_CRAWLED) + " AND `Crawled`>0 AND `Size`>0 " + \
                                 "AND ((`ErrorMask` & 4198399) = 0) AND `ContentType`='text/html'"},
                                 CRIT_CONTENTS: {"WHERE": " `Status`=7 AND `TagsCount`>0 AND `Processed`>0"},
                                 CRIT_CLURLS: {'WHERE': "`ParentMd5`<>'' AND " + CRIT_CRAWLED_THIS_NODE},
                                 CRIT_NURLS: {"WHERE": "`Status`=" + str(dc.EventObjects.URL.STATUS_NEW)},
                                 CRIT_DURLS: {},
                                 CRIT_CRURLS: {},
                                 CRIT_PURLS: {},
                                 CRIT_ERRORS: {'WHERE': "`ErrorMask`>0 AND " + CRIT_CRAWLED_THIS_NODE}}


def getDefaultCriterions(criterionName, siteId, queryCallback):
  ret = ""
  SQL_SELECT_TEMPLATE = "SELECT `Value` FROM `sites_properties` WHERE `Name`='%s' AND `Site_Id`='%s'"
  criterionDict = {}
  query = SQL_SELECT_TEMPLATE % (criterionName, siteId)
  res = queryCallback(query, Constants.PRIMARY_DB_ID)
  if res is not None and len(res) > 0 and res[0] is not None:
    criterionDict[app.SQLCriterions.CRITERION_WHERE] = res[0][0]
  elif criterionName in DefaultRecalculatorCriterions:
    criterionDict = DefaultRecalculatorCriterions[criterionName]
  ret = app.SQLCriterions.generateCriterionSQL(criterionDict, None, siteId)
  logger.debug(">>> Recalculate Def Ret = " + ret)
  return ret
