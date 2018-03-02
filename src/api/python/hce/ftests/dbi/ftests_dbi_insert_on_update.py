#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file ftests_dbi_insert_on_update.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from dbi.dbi import DBI
from dbi.dbi import CONSTANTS
from Resources import Resources as dbResources
from dtm.EventObjects import Resource as eventResource

class DemoResourcesManager(object):
    
    
  def __init__(self, config_dic):
    # create dbi instance
    self.dbi = DBI(config_dic)
        
    
  def updateResourcesData(self, resource):
    # insert object
    original_resource = dbResources(resource)
    self.dbi.insert(original_resource)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle insertion's error 
      print "insert original resource error!"
      return
    else:
      # do ptocessing after insertion
      print "original resource: %s" % original_resource 
      pass


    # fetch object
    fetched_resource = dbResources(resource)
    fetched_original_resource = self.dbi.fetch(fetched_resource, "nodeId=%s"%fetched_resource.nodeId)
    if self.dbi.getErrorCode()!=CONSTANTS.DBI_SUCCESS_CODE and fetched_original_resource!=original_resource:
      # handle fetch's error 
      print "fetch original resource error!"
      return
    else:
      # do ptocessing after insertion
      pass
      print "fetched original resource: %s" % fetched_original_resource



    # update otiginal resource
    updated_resource = dbResources(resource)
    updated_resource.name = "updated"
    print "updated resource: %s" % fetched_original_resource
    returned_updated_resource = self.dbi.insertOnUpdate(updated_resource, "nodeId=%s"%updated_resource.nodeId)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
      print "insert on update error!"
      return
    else:
      # do ptocessing after insertion
      pass
      print "returned updated resource: %s" % returned_updated_resource 



    # fetch updated object
    fetched_resource = dbResources(resource)
    fetched_updated_resource = self.dbi.fetch(fetched_resource, "nodeId=%s"%fetched_resource.nodeId)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      print "fetched updated resource: %s" % fetched_updated_resource






if __name__ == '__main__':
    # config section
    config_dic = dict()
    config_dic["db_name"] = "/del.db"
    # create ResourcesManager instance
    demoResourceManager = DemoResourcesManager(config_dic)
    event_Resource = eventResource("100")
    demoResourceManager.updateResourcesData(event_Resource)
