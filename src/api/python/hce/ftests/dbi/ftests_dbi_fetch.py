"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file dbi.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


"""
used in:
./hce/dtm/Scheduler.py
./hce/dtm/TasksManager.py
./hce/dtm/TasksDataManager.py
"""

from dbi.dbi import DBI
from dtm.TaskLogScheme import TaskLogScheme
from dtm.TaskLog import TaskLog


def run_test():
  config_dic = {"db_name":"sqlite:///:memory:"}
  dbi = DBI(config_dic)
  tl = TaskLog()
  tls1 = TaskLogScheme(tl)
  tls1.id = 11
  tls2 = TaskLogScheme(tl)
  tls2.id = 11
  dbi.insert(tls1)
  dbi.insert(tls2)
  obj = dbi.fetch(tls1, "id=11")
  print obj
  if len(obj)!=2:
    print "BAD"
  else:
    print"OK"
  return



if __name__ == "__main__":
  
  run_test()