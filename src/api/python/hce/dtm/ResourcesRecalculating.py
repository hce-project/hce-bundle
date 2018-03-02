'''
Created on Mar 13, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import EventObjects
import sys

##Class ResourcesRecalculating, that contains recalcularing algorithm of resource data
#
class ResourcesRecalculating(object):


  ##constructor
  #initialise all class variable and recieve config as param
  def __init__(self):
    self.resources = {}
    self.resourcesAVG = EventObjects.ResourcesAVG()


  def addUpdateResources(self, resources):
    self.resources[resources.nodeId] = resources


  ##recalculate method
  #recalculate method calls outside and performs recalculate processing, now it's empty
  def recalculate(self):
    rCount = 0
    self.resourcesAVG.cpu = 0
    self.resourcesAVG.io = 0
    self.resourcesAVG.ramRU = 0
    self.resourcesAVG.ramVU = 0
    self.resourcesAVG.ramR = 0
    self.resourcesAVG.ramV = 0
    self.resourcesAVG.swap = 0
    self.resourcesAVG.disk = 0
    self.resourcesAVG.uDate = 0
    self.resourcesAVG.cpuCores = 0
    self.resourcesAVG.threads = 0
    self.resourcesAVG.processes = 0
    for resourceItem in self.resources.values():
      if resourceItem.state == EventObjects.Resource.STATE_ACTIVE:
        self.resourcesAVG.cpu += resourceItem.cpu
        self.resourcesAVG.io += resourceItem.io
        self.resourcesAVG.ramRU += resourceItem.ramRU
        self.resourcesAVG.ramVU += resourceItem.ramVU
        self.resourcesAVG.ramR += resourceItem.ramR
        self.resourcesAVG.ramV += resourceItem.ramV
        self.resourcesAVG.swap += resourceItem.swap
        self.resourcesAVG.disk += resourceItem.disk
        if rCount == 0 or resourceItem.uDate < self.resourcesAVG.uDate:
          self.resourcesAVG.uDate = resourceItem.uDate
        self.resourcesAVG.cpuCores += resourceItem.cpuCores
        self.resourcesAVG.threads += resourceItem.threads
        self.resourcesAVG.processes += resourceItem.processes
        rCount += 1
    if rCount > 0:
      self.resourcesAVG.cpu = self.resourcesAVG.cpu / rCount
      self.resourcesAVG.io = self.resourcesAVG.io / rCount
      self.resourcesAVG.ramRU = self.resourcesAVG.ramRU / rCount
      self.resourcesAVG.ramVU = self.resourcesAVG.ramVU / rCount
      self.resourcesAVG.ramR = self.resourcesAVG.ramR / rCount
      self.resourcesAVG.ramV = self.resourcesAVG.ramV / rCount
      self.resourcesAVG.swap = self.resourcesAVG.swap / rCount
      self.resourcesAVG.disk = self.resourcesAVG.disk / rCount
      self.resourcesAVG.cpuCores = self.resourcesAVG.cpuCores / rCount
      self.resourcesAVG.threads = self.resourcesAVG.threads / rCount
      self.resourcesAVG.processes = self.resourcesAVG.processes / rCount
    else:
      self.resourcesAVG.cpu = sys.maxint
      self.resourcesAVG.io = sys.maxint


  def getResourcesAVG(self):
    return self.resourcesAVG
