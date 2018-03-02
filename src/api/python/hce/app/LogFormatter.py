'''
HCE project, Python bindings.
Logging messages formatters classes.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

##Log formatter event, defines the object to format message string
#
#The LogFormatterEvent object used to create log message string representation according with special format.
class LogFormatterEvent(object):

  OBJECT_DUMP_DELIMITER = "\n"
  MESSAGE_PREFIX = ""

  ##constructor
  #initialize fields
  #
  #@param event Event object instance to dump itself and eventObj inside
  #@param objectsList List of objects to dump
  #
  def __init__(self, event, objectsList, descriptionText):
    self.event = event
    self.objects = objectsList
    self.description = descriptionText


  def __str__(self):
    ret = self.MESSAGE_PREFIX + str(vars(self.event))

    if self.event.eventObj and hasattr(self.event.eventObj, "__dict__"):
      ret = ret + self.OBJECT_DUMP_DELIMITER + str(vars(self.event.eventObj)) + self.OBJECT_DUMP_DELIMITER
      for obj in self.objects:
        ret = ret + self.OBJECT_DUMP_DELIMITER + str(vars(obj)) + self.OBJECT_DUMP_DELIMITER

    ret = ret + self.description + self.OBJECT_DUMP_DELIMITER

    return ret


