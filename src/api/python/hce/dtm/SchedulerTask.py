'''
@package: dtm
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

##Class describes structures of  task item used in Scheduler
#
class SchedulerTask(object):

  ##constructor
  #initialise all class variable of None
  #more information in DTM_application_architecture
  def __init__(self):
    self.id = None
    self.rTime = 0
    self.rTimeMax = 0
    self.state = None
    self.priority = 0
    self.strategy = ""
    self.tries = 0
