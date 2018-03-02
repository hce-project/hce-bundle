'''
Created on Mar 6, 2014

@author: igor
'''
import unittest
from dtm.TaskLogScheme import TaskLogScheme
from dtm.TaskBackLogScheme import TaskBackLogScheme
from dtm.TaskLog import TaskLog
from dbi.dbi import DBI
import dbi.Constants as dbi_consts
import datetime


class TestTaskLogScheme(unittest.TestCase):


    def setUp(self):
        config_dbi = dict({"db_name": "sqlite:///:memory:"})
        self.dbi = DBI(config_dbi)
                

    def tearDown(self):
        del self.dbi 
        self.dbi = None
                

    def getNewTaskLog(self, startValue):
        taskLog = TaskLog()
        taskLog.id = startValue
        taskLog.pId = startValue + 1        
        taskLog.nodeName =str(startValue + 2)
        taskLog.cDate = datetime.datetime.now()
        taskLog.sDate = datetime.datetime.now()
        taskLog.rDate = datetime.datetime.now()
        taskLog.fDate = datetime.datetime.now()
        taskLog.pTime = startValue + 7
        taskLog.pTimeMax = startValue + 8
        taskLog.state = startValue + 9
        taskLog.uRRAM = startValue + 10
        taskLog.uVRAM = startValue + 11
        taskLog.uCPU = startValue + 12
        taskLog.uThreads = startValue + 13
        taskLog.tries = startValue + 14                
        return taskLog


    def checkError(self):
        print self.dbi.getErrorCode()
        if self.dbi.getErrorCode() != dbi_consts.DBI_SUCCESS_CODE:
            assert(False)


    def test_create_empty_db(self):
        taskLog = self.getNewTaskLog(1)
        taskLogScheme = TaskLogScheme(taskLog)                
        results = self.dbi.fetchAll(taskLogScheme)
        self.checkError()
        
        ##inserted list in list
        self.assertEqual(len(results[0]), 0, "")
            

    def test_insert_data(self):
        taskLog = self.getNewTaskLog(1)
        taskLogScheme = TaskLogScheme(taskLog)        
                    
        lookTaskLog = TaskLog()
        lookTaskLog.id = 1
        lookTaskLogScheme = TaskLogScheme(lookTaskLog)
                                                        
        self.dbi.insert(taskLogScheme)
        self.checkError()      
                                                        
        fetchTaskLogScheme = self.dbi.fetch(lookTaskLogScheme, "id=%s" % taskLog.id)[0]
        self.checkError()
        fetchTaskLog = fetchTaskLogScheme._getTaskLog()
        
        self.assertEqual(taskLog.__dict__, fetchTaskLog.__dict__, "")
        
        self.dbi.delete(taskLogScheme, "id=%s" % taskLog.id)
        
        
    def test_del_data(self):
        taskLog = self.getNewTaskLog(1)
        taskLogScheme = TaskLogScheme(taskLog)        
                    
        self.dbi.insert(taskLogScheme)
        self.checkError()
        self.dbi.delete(taskLogScheme,  "id=%s" % taskLog.id)
        self.checkError()
        results = self.dbi.fetchAll(taskLogScheme)
        self.checkError()
        
        self.assertEqual(len(results[0]), 0, "")
        
                
    def test_update_data(self):
        taskLog = self.getNewTaskLog(1)
        taskLogScheme = TaskLogScheme(taskLog)

        self.dbi.insert(taskLogScheme)
        self.checkError()
        
        taskLog.pId = 101
        taskLogScheme = TaskLogScheme(taskLog)
        self.dbi.update(taskLogScheme, "id=%s" % taskLog.id)
        self.checkError()
        
        fetchTaskLogScheme = self.dbi.fetch(taskLogScheme, "id=%s" % taskLog.id)[0]
        fetchTaskLog = fetchTaskLogScheme._getTaskLog()
        
        self.assertEqual(fetchTaskLog.pId, taskLog.pId, "")
        
        self.dbi.delete(taskLogScheme, "id=%s" % taskLog.id)
        
                        
    def test_insert_in_two_bases(self):      
        taskLog = self.getNewTaskLog(1)        
        taskLogScheme =  TaskLogScheme(taskLog)
        taskBackLogScheme = TaskBackLogScheme(taskLog)
                
        self.dbi.insert(taskLogScheme)
        self.checkError()      

        self.dbi.insert(taskBackLogScheme)
        self.checkError()
        
        fetchTaskLogScheme = self.dbi.fetch(taskLogScheme,  "id=%s" % taskLog.id)[0]
        self.checkError()      
        fetchTaskLog = fetchTaskLogScheme._getTaskLog()
        
        self.assertEqual(taskLog.__dict__, fetchTaskLog.__dict__, "")

        fetchTaskBackLogScheme = self.dbi.fetch(taskBackLogScheme, "id=%s" % taskLog.id)[0]
        self.checkError()      
        fetchTaskBackLog = fetchTaskBackLogScheme._getTaskLog()
        
        self.assertEqual(taskLog.__dict__, fetchTaskBackLog.__dict__, "")
        
        #clean up
        self.dbi.delete(taskLogScheme, "id=%s" % taskLog.id)
        self.dbi.delete(taskBackLogScheme, "id=%s" % taskLog.id)
        
