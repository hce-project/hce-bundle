'''
@package: dc
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import dc_db.Constants as DB_CONST


CRITERION_WHERE = "WHERE"
CRITERION_ORDER = "ORDER BY"
CRITERION_LIMIT = "LIMIT"

def generateCriterionSQL(criterions, additionWhere=None, siteId=None):
  additionString = ""
  if siteId is not None:
    localCriterions = {}
    for key in criterions:
      if isinstance(criterions[key], basestring):
        localCriterions[key] = criterions[key].replace("%" + DB_CONST.SITE_ID_NAME + "%", siteId)
      else:
        localCriterions[key] = criterions[key]
    criterions = localCriterions

  # Criterions "WHERE" block
  if CRITERION_WHERE in criterions and criterions[CRITERION_WHERE] is not None and criterions[CRITERION_WHERE] != "":
    additionString += (" " + CRITERION_WHERE + " ")
    if additionWhere is not None:
      additionString += (additionWhere + " AND ")
    additionString += str(criterions[CRITERION_WHERE])
  elif additionWhere is not None:
    additionString += (" " + CRITERION_WHERE + " ")
    additionString += additionWhere
  # Criterions "ORDER" block
  if CRITERION_ORDER in criterions and criterions[CRITERION_ORDER] is not None and criterions[CRITERION_ORDER] != "":
    additionString += (" " + CRITERION_ORDER + " ")
    additionString += str(criterions[CRITERION_ORDER])
  # Criterions "LIMIT" block
  if CRITERION_LIMIT in criterions and criterions[CRITERION_LIMIT] is not None and criterions[CRITERION_LIMIT] != "":
    localLimit = criterions[CRITERION_LIMIT]
    if isinstance(localLimit, list):
      localString = ("%s , %s" % (str(localLimit[0]), str(localLimit[1])))
    else:
      localString = str(localLimit)
    additionString += (" " + CRITERION_LIMIT + " " + localString)
  return additionString
