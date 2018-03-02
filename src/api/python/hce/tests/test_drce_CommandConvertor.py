'''
Created on Feb 13, 2014

@author: igor
'''
import json
import unittest
from drce.CommandConvertor import TaskExecuteStructEncoder 
from drce.CommandConvertor import TaskExecuteRequestEncoder
from drce.CommandConvertor import CommandConvertor
from drce.CommandConvertor import CommandConvertorError
from drce.Commands import TaskExecuteStruct
from drce.Commands import TaskExecuteRequest
from drce.Commands import TaskCheckRequest, TaskTerminateRequest
import drce.Consts as consts


class TestTaskExecuteStruct(unittest.TestCase):
    
    
    def teEst_json_encode(self): 
        expect_json = """{"files": [{"action": 22, "data": "-f", "name": "go.py"}], "input": "", "session": {"tmode": 0, "shell": "", "environment": {}, "user": "", "timeout": 0, "password": "", "type": 0, "port": 0}, "command": ""}""" 
                
        task_exec_struct = TaskExecuteStruct()
        task_exec_struct.add_files("go.py", "-f", 22)
        res_json = json.dumps(task_exec_struct, cls= TaskExecuteStructEncoder)
        
        self.assertEqual(expect_json, res_json, "json edcoder is broken")



class TestTaskExecuteRequest(unittest.TestCase):
    
        
    def test_json_convertor(self):
        execute_request = TaskExecuteRequest("id")        
        #last 2 params for pretty print
        json.dumps(execute_request, cls = TaskExecuteRequestEncoder, sort_keys = False, indent = 4)
        commandConvertor =  CommandConvertor()
        commandConvertor.to_json(execute_request)
        

        
class TestTaskCheckRequest(unittest.TestCase):
    
    
    def test_json_convert(self):
        uid = "11"
        check_request = TaskCheckRequest(uid, consts.SIMPLE_STATUS_INFO)        
        json.dumps(check_request.__dict__, indent=2)
        


class TestTaskTerminateRequest(unittest.TestCase):
    
    
    def test_json_convert(self):
        uid = "11"
        terminate_request = TaskTerminateRequest(uid)
        json.dumps(terminate_request.__dict__, indent=2)
        
        
class TestCommandConvertor(unittest.TestCase):
    
    
    def teEst_from_json_convertor(self):
        json_s = """
        {
          "error_code":0,
          "error_message" :"msg",
          "time":10,
          "state":1,
          "pid":101,
          "data":[
          {"files":[{"name":"f1", "data":"data1", "action":12}],
             "stdout":"out",
             "stderror":"error",
             "exit_status":5,
             "node":"n1",
             "time":100
          }
          ]
        }        
        """        
        test_err_str = "json parsing is failed"
        cmd_convertor = CommandConvertor()
        task_response = cmd_convertor.from_json(json_s)
        
        self.assertEqual(task_response.error_code, 0, test_err_str)
        self.assertEqual(task_response.error_msg, "msg", test_err_str )
        self.assertEqual(task_response.state, 1, test_err_str)
        self.assertEqual(task_response.pid, 101, test_err_str)
        self.assertEqual(len(task_response.data), 1, test_err_str)
        response_item = task_response.data[0]        
        self.assertEqual(len(response_item.files), 1, test_err_str)        
        self.assertEqual(response_item.files[0]["name"], "f1", test_err_str)
        self.assertEqual(response_item.files[0]["data"], "data1", test_err_str)
        self.assertEqual(response_item.files[0]["action"], 12, test_err_str)
        self.assertEqual(response_item.stdout, "out", test_err_str)
        self.assertEqual(response_item.stderror, "error", test_err_str)
        self.assertEqual(response_item.exit_status, 5, test_err_str)
        self.assertEqual(response_item.node, "n1", test_err_str)
        self.assertEqual(response_item.time, 100, test_err_str)
                        
    
    
    def test_parse_wrong_json(self):
        json_s = """{"some":1, "data":["1", "2"]} """
        
        cmd_convertor = CommandConvertor()
        with self.assertRaises(CommandConvertorError):
            list(cmd_convertor.from_json(json_s))
            
            
    def test_parse_wrong_json_no_list_field(self):
        json_s = """
        {
          "error_code":0,
          "error_message" :"msg",
          "time":10,
          "state":1,
          "data":[
          {"files":["f1", "f2"],
             "stdout":"out",
             "stderror":"error",
             "time":100
          }
          ]
        }        
        """
        cmd_convertor = CommandConvertor()
        with self.assertRaises(CommandConvertorError):
            list(cmd_convertor.from_json(json_s))                
    