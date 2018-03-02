# coding: utf-8

"""
HCE project, Python bindings, Distributed Tasks Manager application.
PostProcessingModuleClass is a base class for postprocess modules.

@package: dc_postprocessor
@file PostProcessingModuleClass.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

# This object is a run at once module processing
class PostProcessingModuleClass(object):

  # Default initialization
  def __init__(self, getConfigOption=None, log=None):
    self.getConfigOption = getConfigOption
    self.logger = log

  # # initialization interface method
  #
  # @param - None
  # @return - None
  def init(self):
    pass


  # # process batch interface method
  #
  # @param batchObj - batch instance
  # @return - None
  def processBatch(self, batchObj):
    return batchObj


  # # process batch item interface method
  #
  # @param batchItemObj - batch item instance
  # @return - None
  def processBatchItem(self, batchItemObj):
    return batchItemObj
