'''
Created on Feb 12, 2014

@author: igor
'''
import json
import unittest
from drce.Commands import Session
from drce.Commands import TaskExecuteStruct
from drce.Commands import TaskExecuteRequest
from drce.Commands import TaskCheckRequest
from drce.Commands import TaskTerminateRequest
from drce.Commands import TaskGetDataRequest

import drce.Consts as consts

class TestSession(unittest.TestCase):
    
    def test_set_env_variable(self):
        session = Session(0, 0, 0)
        expect_evn = dict({"LINES": "80",
                                        "HOSTNAME": "node22"})
        
        session.add_evn_pair("LINES", "80")
        session.add_evn_pair("HOSTNAME", "node22")
                        
        self.assertEqual(expect_evn, session.environment, "failed set of evn variable ")



class TestTaskExecuteStruct(unittest.TestCase):
    
    def test_add_file_variable(self):
        task_exec_struct = TaskExecuteStruct()
        
        file1 = {"name" : "go.py", "data" : "-f", "action":22}
        file2 = {"name" : "none.cpp", "data" : "-fu", "action":2}
        expect_files = list()
        expect_files.append(file1)
        expect_files.append(file2)
                        
        task_exec_struct.add_files("go.py", "-f", 22)
        task_exec_struct.add_files("none.cpp", "-fu", 2)                        
                        
        self.assertEqual(expect_files, task_exec_struct.files, "failed set of files")
                
        

class TestTaskExecuteRequest(unittest.TestCase):
    
    
    def test_correct_init_request(self):
        id = "121"
        execute_request = TaskExecuteRequest(id)
        
        self.assertEqual(id, execute_request.id, "class construction error")
        self.assertEqual(consts.EXECUTE_TASK, execute_request.type, "class construction error")
    
        

class TestTaskCheckRequest(unittest.TestCase):
    
    def test_correct_create_request(self):
        uid = "11"
        check_request = TaskCheckRequest(uid, consts.SIMPLE_STATUS_INFO)
        
        self.assertEqual(uid, check_request.id, "check request creation error")
        self.assertEqual(consts.CHECK_TASK_STATE, check_request.type, "type error")
        self.assertEqual(consts.SIMPLE_STATUS_INFO, check_request.data["type"], "data type error")
        
            

class TestTaskTerminateRequest(unittest.TestCase):
    
    def test_correct_create_request(self):
        uid = "12"
        default_data = ({"alg":0, "delay":0, "repeat":0, "signal":0})
        terminate_request = TaskTerminateRequest(uid)
        
        self.assertEqual(uid, terminate_request.id, "id set error")
        self.assertEqual(consts.TERMINATE_TASK, terminate_request.type, "type set error")
        self.assertEqual(default_data, terminate_request.data, "data set error")
        


class TestTaskGetDataRequest(unittest.TestCase):    
    
    def test_correct_init_request(self):
        uid = "121"
        execute_request = TaskGetDataRequest(uid, consts.FETCH_DATA_SAVE)
        
        self.assertEqual(uid, execute_request.id, "class construction error")
        self.assertEqual(consts.GET_TASK_DATA, execute_request.type, "data error")
        self.assertEqual(consts.FETCH_DATA_SAVE, execute_request.data["type"], "data type error")
