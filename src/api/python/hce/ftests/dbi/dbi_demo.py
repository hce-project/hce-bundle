#!/usr/bin/python


"""@package docstring
 @file dbi_demo.py
 @author Oleksii <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""


from dbi.dbi import DBI
from dbi.dbi import db
from dbi.dbi import CONSTANTS
from demoTask import DemoBackLogTask
from dtm.TasksDataTable import TasksDataTable
from task import Task
import ConfigParser
import datetime


class DemoTaskManager(object):


  def __init__(self, config_dic):
    # create dbi instance
    self.dbi = DBI(config_dic)


  def process(self, input_tasks):
    t1 = TasksDataTable()
    t2 = TasksDataTable()
    t1.id = 11
    t2.id = 11
    t1.data = "fake data 1"
    t2.data = "fake data 2"
    self.dbi.insert(t1)
    print self.dbi.getErrorCode()
    self.dbi.insert(t2)
    print self.dbi.getErrorCode()
    #print self.dbi.fetch(t1, "id=%s"%(t1.id))
    #print db.session.query(type(t1)).filter(t1.id=t1.id, t1.data=t1.data)
    print db.session.query(type(t1)).filter_by(id=t1.id, data=t1.data).all()
    #print self.dbi.sql(t1, "select * from tasks_data_table where id=%s and data='%s'"%(t1.id,t1.data))
    print self.dbi.getErrorCode()
    return
    """
    # insert one object
    input_back_log_one_task = DemoBackLogTask(input_tasks[0])
    self.dbi.insert(input_back_log_one_task)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle insertion's error 
      print "One insert error!"
      return
    else:
      # do ptocessing after insertion
      pass
    """
    """
    # insert array of objects
    input_back_log_tasks = [DemoBackLogTask(input_task) for input_task in input_tasks]
    self.dbi.insert(input_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle insertion's error 
      print "Bunch insert error!"
      return
    else:
      # do ptocessing after insertion
      pass
    """
    return
    # fetch one object
    fetch_back_log_tasks = DemoBackLogTask(input_tasks[0])
    fetched_back_log_tasks = self.dbi.fetch(fetch_back_log_tasks, "id=%s"%fetch_back_log_tasks.id)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
        print "One fetch error!"
        return
    else:
      # do ptocessing after insertion
      pass
      for task in fetched_back_log_tasks:
        print task

    """
    # fetch bunch of objects
    fetch_back_log_tasks = [DemoBackLogTask(input_task) for input_task in input_tasks]
    fetched_back_log_tasks = self.dbi.fetch(fetch_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
      print "Bunch of fetch error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in fetched_back_log_tasks:
        print task
    """

    """
    # fetch all for one object
    fetch_back_log_tasks = DemoBackLogTask(input_tasks[0])
    fetched_back_log_tasks = self.dbi.fetchAll(fetch_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
      print "fetch all for one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in fetched_back_log_tasks:
        print task
        pass
    """

    """
    # fetch all for bunch of objects
    fetch_back_log_tasks = [DemoBackLogTask(input_task) for input_task in input_tasks]
    fetched_back_log_tasks = self.dbi.fetchAll(fetch_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle fetch's error 
      print "fetch all for bunch of objects error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in fetched_back_log_tasks:
        print task
        pass
    """

    """
    # update one object
    update_back_log_tasks = DemoBackLogTask(Task(id="11111", Tries=22))
    updated_back_log_tasks = self.dbi.update(update_back_log_tasks, "id=%s"%update_back_log_tasks.id)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
        print "update one object error!"
        return
    else:
    # do ptocessing after insertion
      pass
      for task in updated_back_log_tasks:
        #print vars(task)
        pass
    """

    """
    # update bunch of objects
    update_back_log_tasks = [DemoBackLogTask(input_task) for input_task in input_tasks]
    updated_back_log_tasks = self.dbi.update(update_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "update bunch of objects error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in updated_back_log_tasks:
        #print vars(task)
        pass
    """

    """
    # delete one object
    delete_back_log_tasks = DemoBackLogTask(Task(id="11111"))
    deleted_back_log_tasks = self.dbi.delete(delete_back_log_tasks, "id=%s"%delete_back_log_tasks.id)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in deleted_back_log_tasks:
        print vars(task)
    """

    """
    # delete bunch of objects
    delete_back_log_tasks = [DemoBackLogTask(input_task) for input_task in input_tasks]
    deleted_back_log_tasks = self.dbi.delete(delete_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete bunch of objects error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in deleted_back_log_tasks:
        print vars(task)
    """


    # delete all for one object
    delete_back_log_tasks = DemoBackLogTask(input_tasks[0])
    deleted_back_log_tasks = self.dbi.deleteAll(delete_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete all for one object error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in deleted_back_log_tasks:
        print vars(task)


    """
    # delete all for bunch of objects
    delete_back_log_tasks = [DemoBackLogTask(input_task) for input_task in input_tasks]
    deleted_back_log_tasks = self.dbi.deleteAll(delete_back_log_tasks)
    if self.dbi.getErrorCode() != CONSTANTS.DBI_SUCCESS_CODE:
      # handle update's error 
      print "delete all for bunch of objects error!"
      return
    else:
      # do ptocessing after insertion
      pass
      for task in deleted_back_log_tasks:
        print vars(task)
    """

if __name__ == '__main__':
    # config section
    config = ConfigParser.ConfigParser()
    config.read("dbi_demo.ini")
    config_dic = dict(config._sections)
    for k in config_dic:
            config_dic[k] = dict(config._defaults, **config_dic[k])
            config_dic[k].pop('__name__', None)
    
    demo_task_manager = DemoTaskManager(config_dic["TaskManager"])
    cdate = datetime.datetime.now()
    tasks = [Task(id="11111", Tries=11, CDate=cdate), Task(id="22222", Tries=22)]
    demo_task_manager.process(tasks)
