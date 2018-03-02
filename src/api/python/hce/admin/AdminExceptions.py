'''
Created on Feb 17, 2014

@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

##AdminExceptions module keepts admin module native exceptions
class AdminTimeoutException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class AdminWrongConnectionKey(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)
