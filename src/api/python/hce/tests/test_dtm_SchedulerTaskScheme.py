'''
Created on Mar 13, 2014

@author: igor
'''

import unittest
from dtm.SchedulerTask import SchedulerTask
from dtm.SchedulerTaskScheme import SchedulerTaskScheme
from dbi.dbi import DBI
import dbi.Constants as dbi_consts
import tempfile
import os


class TestSchedulerTaskScheme(unittest.TestCase):


    def setUp(self):
        tf = tempfile.NamedTemporaryFile()
        print os.path.basename(tf.name)          
        sql_name = "sqlite:///" +  os.path.basename(tf.name) + "TestSchedulerTaskScheme.db"               
        config_dbi = dict({"db_name": sql_name})        
        #config_dbi = dict({"db_name": "sqlite:///:memory:"})
        self.dbi = DBI(config_dbi)
        self.schedulerTask = self.getNewSchedulerTask(1)
        self.schedulerTaskScheme = SchedulerTaskScheme(self.schedulerTask)                
                
                
    def getNewSchedulerTask(self, startValue):
        schedulerTask = SchedulerTask()
        schedulerTask.id = startValue
        schedulerTask.rTime = startValue + 1
        schedulerTask.rTimeMax = startValue + 2
        schedulerTask.state = startValue + 3
        schedulerTask.priority = startValue + 4        
        return schedulerTask
        

    def checkError(self):
        print self.dbi.getErrorCode()
        if self.dbi.getErrorCode() != dbi_consts.DBI_SUCCESS_CODE:
            assert(False)


    def test_create_empty_db(self):
        results = self.dbi.fetchAll(self.schedulerTaskScheme)
        self.checkError()
        
        ##inserted list in list
        self.assertEqual(len(results[0]), 0, "")
            
    
    def test_insert_data(self):
        lookSchedulerTask = SchedulerTask()
        lookSchedulerTask.id = 1
        lookSchedulerTaskScheme = SchedulerTaskScheme(lookSchedulerTask)
                                                        
        self.dbi.insert(self.schedulerTaskScheme)
        self.checkError()      
                                                        
        fetchSchedulerTaskScheme = self.dbi.fetch(lookSchedulerTaskScheme, "id=%s" % lookSchedulerTask.id)[0]
        self.checkError()
        fetchSchedulerTask = fetchSchedulerTaskScheme._getSchedulerTask()
        
        self.assertEqual(self.schedulerTask.__dict__, fetchSchedulerTask.__dict__, "")
        
        self.dbi.delete(self.schedulerTaskScheme, "id=%s" % self.schedulerTask.id)
        
        
    def test_del_data(self):
        self.dbi.insert(self.schedulerTaskScheme)
        self.checkError()      

        self.dbi.delete(self.schedulerTaskScheme, "id=%s" % self.schedulerTask.id)        
        self.checkError()
        
        results = self.dbi.fetchAll(self.schedulerTaskScheme)
        self.checkError()
        
        self.assertEqual(len(results[0]), 0, "")
        
                
    def test_update_data(self):
        self.dbi.insert(self.schedulerTaskScheme)
        self.checkError()      
        
        self.schedulerTask.state = 101
        updateSchedulerTaskScheme = SchedulerTaskScheme(self.schedulerTask)
        
        self.dbi.update(updateSchedulerTaskScheme, "id=%s" % self.schedulerTask.id)
        self.checkError()

        fetchSchedulerTaskScheme = self.dbi.fetch(updateSchedulerTaskScheme, "id=%s" % self.schedulerTask.id)[0]
        self.checkError()
        
        fetchSchedulerTask = fetchSchedulerTaskScheme._getSchedulerTask()
        
        self.assertEqual(fetchSchedulerTask.__dict__, self.schedulerTask.__dict__, "")
        
        self.dbi.delete(self.schedulerTaskScheme, "id=%s" % self.schedulerTask.id)