#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file resources_manager_dbi_demo.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from dbi import DBI
from dbi import CONSTANTS
from Resources import Resources as dbResources
from EventObjects import Resource as eventResource

class DemoResourcesManager(object):
    
    
  def __init__(self, config_dic):
    # create dbi instance
    self.dbi = DBI(config_dic)
        
    
  def updateResourcesData(self, updated_resources):
    # insert one object
    input_back_log_one_task = dbResources(updated_resources)
    self.dbi.insert(input_back_log_one_task)
    if self.dbi.getError() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle insertion's error 
      print "One insert error!"
      return
    else:
      # do ptocessing after insertion
      pass


    # fetch one object
    fetch_back_log_tasks = dbResources(updated_resources)
    fetched_back_log_tasks = self.dbi.fetch(fetch_back_log_tasks, "nodeId=%s"%fetch_back_log_tasks.nodeId)
    if self.dbi.getError() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
      print "One fetch error!"
      return
    else:
      # do ptocessing after insertion
      pass
      print fetched_back_log_tasks



    # fetch all for one object
    fetch_back_log_tasks = dbResources(updated_resources)
    fetched_back_log_tasks = self.dbi.fetchAll(fetch_back_log_tasks)
    if self.dbi.getError() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
      print "fetch all for one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in fetched_back_log_tasks:
        #print task
        pass



    # update one object
    update_back_log_tasks = dbResources(updated_resources)
    updated_back_log_tasks = self.dbi.update(update_back_log_tasks, "nodeId=%s"%update_back_log_tasks.nodeId)
    if self.dbi.getError() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "update one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in updated_back_log_tasks:
        #print vars(task)
        pass
        
        

    # delete one object
    delete_back_log_tasks = dbResources(updated_resources)
    deleted_back_log_tasks = self.dbi.delete(delete_back_log_tasks, "nodeId=%s"%delete_back_log_tasks.nodeId)
    if self.dbi.getError() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in deleted_back_log_tasks:
        print vars(task)



    # delete all for one object
    delete_back_log_tasks = dbResources(updated_resources)
    deleted_back_log_tasks = self.dbi.deleteAll(delete_back_log_tasks)
    if self.dbi.getError() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete all for one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in deleted_back_log_tasks:
        print vars(task)



if __name__ == '__main__':
    # config section
    config_dic = dict()
    config_dic["db_name"] = ""
    # create ResourcesManager instance
    demoResourceManager = DemoResourcesManager(config_dic)
    event_Resource = eventResource("1")
    demoResourceManager.updateResourcesData(event_Resource)
