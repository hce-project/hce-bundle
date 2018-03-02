"""
HCE project,  Python bindings, Distributed Tasks Manager application.
SystemCommandHandler Class content main functional support different system command.

@package: app
@file SystemCommandHandler.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import resource
import gc


## Class SystemCommandHandler for support different system command
#
class SystemCommandHandler(object):
  ##Constans of error messages
  ERROR_NOT_SUPPORTED_TYPE = 'Not supported type of SystemCommandHandler'
  ##Constans error codes
  ERROR_OK = 0
  ERROR_FAIL = 1
  ##Constructor
  #
  #@param logger - logger instance
  def __init__(self, logger=None):
    self.logger = logger
    self.errorMsg = ''
    self.handlers = [self.onGarbageCollectorCleanupHandler]


  ##Execute system command
  #
  #@param typeNumber - type number of system command as integer
  #@param inputData - input data
  #@return error code ERROR_OK if success, ERROR_FAIL othewise
  def execute(self, typeNumber, inputData=None):
    #variable for result
    ret = self.ERROR_FAIL
    if self.logger is not None:
      self.logger.debug('type: ' + str(typeNumber))

    try:
      if int(typeNumber) >= len(self.handlers) or int(typeNumber) < 0:
        raise Exception(self.ERROR_NOT_SUPPORTED_TYPE + ' (' + str(typeNumber) + ')')

      (self.handlers[int(typeNumber)])(inputData)
      ret = self.ERROR_OK
    except Exception, err:
      self.errorMsg = str(err)

    return ret


  ##Handler of garbage collector cleanup
  #
  #@param inputData - input data
  def onGarbageCollectorCleanupHandler(self, inputData=None):  # pylint: disable=W0613
    gc.collect()
    if self.logger is not None:
      self.logger.debug('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
      self.logger.debug('GC generations count: ' + str(gc.get_count()))
