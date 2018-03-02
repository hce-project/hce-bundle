'''
Created on Mar 26, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

##DTMAExceptions module keepts DTMA module native exceptions
class DTMAEmptyClasses(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class DTMAEmptyFields(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class DTMANameValueException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)
